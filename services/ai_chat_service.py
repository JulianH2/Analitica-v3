"""
Servicio de chat del copilot impulsado por Pydantic AI y Ollama local.
Cero SQL: el LLM solo invoca herramientas (funciones Python).
El frontend debe enviar el contexto del dashboard (pantalla, widget, filtros) vía dashboard_context.
"""
import asyncio
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Ejecutor para correr el agente async en un hilo con su propio event loop (evita "event loop is already running").
_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ai_chat")


def _run_async_in_new_loop(coro):
    """Ejecuta una coroutine en un event loop nuevo con limpieza correcta.
    asyncio.run() cancela tasks pendientes (incluyendo cleanup de httpx/openai)
    antes de cerrar el loop, evitando 'Task exception was never retrieved'."""
    return asyncio.run(coro)

from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

logger = logging.getLogger(__name__)

# ─── Configuración Ollama (override via env vars OLLAMA_BASE_URL / OLLAMA_MODEL) ─
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:latest")


# ─── Contexto del dashboard (inyección desde el frontend) ─────────────────────
class DashboardContext(BaseModel):
    """Contexto actual del dashboard que ve el usuario. El agente no adivina: usa esto."""
    screen_id: Optional[str] = None
    widget_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, Any]] = None  # ej. {"year": "2024", "month": "enero"}
    timezone: Optional[str] = None  # ej. "America/Mexico_City"
    user_id: Optional[Any] = None  # id_licencia o similar desde sesión
    role_id: Optional[int] = None
    current_db: Optional[str] = None  # base de datos para ejecutar queries (ej. session current_db)

    def to_display_string(self) -> str:
        parts = []
        if self.screen_id:
            parts.append(f"Pantalla: {self.screen_id}")
        if self.widget_id:
            parts.append(f"Widget seleccionado: {self.widget_id}")
        if self.filters:
            parts.append(f"Filtros: {json.dumps(self.filters, ensure_ascii=False)}")
        if self.date_range:
            parts.append(f"Rango: {json.dumps(self.date_range, ensure_ascii=False)}")
        if self.timezone:
            parts.append(f"Zona horaria: {self.timezone}")
        return "; ".join(parts) if parts else "Sin contexto de pantalla"


# ─── Dependencias del agente (contexto + acceso a datos, sin SQL libre) ────────
@dataclass
class DashboardDeps:
    """Dependencias inyectadas en cada ejecución del agente."""
    context: DashboardContext
    data_manager: Any  # DataManager, evita import circular


# ─── Herramientas (Tool Calling): solo funciones Python, cero SQL ────────────
def _summarize_screen_data(data: Dict[str, Any], max_depth: int = 7) -> str:
    """Convierte datos de get_screen en un resumen legible para el LLM.
    max_depth=7 cubre la estructura anidada real (hasta 5-6 niveles en algunos screens)."""
    lines: List[str] = []
    _VALUE_KEYS = {"value_formatted", "current_value", "value", "title", "label", "name",
                   "target", "vs_last_year_value", "vs_last_year_delta", "ytd_value"}

    def _walk(obj: Any, path: str, depth: int) -> None:
        if depth <= 0:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                key_path = f"{path}.{k}" if path else k
                if isinstance(v, (dict, list)):
                    _walk(v, key_path, depth - 1)
                elif v is not None and v != "" and (k in _VALUE_KEYS or "formatted" in k):
                    lines.append(f"  {key_path}: {v}")
    _walk(data, "", max_depth)
    return "\n".join(lines[:120]) if lines else "(sin datos o estructura no reconocida)"


def _extract_widget_data_text(screen_data: Dict[str, Any], widget: Any) -> str:
    if not screen_data or not widget:
        return "(Sin datos disponibles en el contexto actual)"

    widget_id = getattr(widget, "widget_id", "")
    screen_id = getattr(widget, "screen_id", "")
    metric_keys = getattr(widget, "metric_keys", []) or []
    meta = getattr(widget, "meta", {}) or {}
    title = meta.get("title") or widget_id.replace("_", " ").title()
    lines = [f"**Indicador:** {title}"]
    kpi_data = None

    try:
        from services.data_manager import data_manager as _dm
        screen_cfg = (getattr(_dm, "SCREEN_MAP", {}) or {}).get(screen_id, {})
        inject_paths = screen_cfg.get("inject_paths") or {}
        path = None

        # Strategy 1: direct widget_id match (works for most KPIs whose key == widget_id)
        path = inject_paths.get(widget_id)

        # Strategy 2: dot-notation prefix match — e.g. "rp_kms_tot.current_value" → path[:-1]
        # Handles widgets where inject_paths keys use "{widget_id}.{field}" pattern.
        if path is None:
            prefix = widget_id + "."
            for key, p in inject_paths.items():
                if key.startswith(prefix) and isinstance(p, list) and len(p) > 1:
                    path = p[:-1]  # parent container path (drop leaf field)
                    break

        # Strategy 2b: column target scan — mirrors data_manager's own inject_paths lookup:
        #   inject_paths.get(f"{group_key}.{target}") or inject_paths.get(target)
        # Handles rp_kms_lt where only generic target keys exist (e.g. "current_value").
        if path is None:
            columns = meta.get("columns") or []
            for col_def in columns:
                if not isinstance(col_def, dict):
                    continue
                target_key = col_def.get("target")
                if not target_key:
                    continue
                for k in (f"{widget_id}.{target_key}", target_key):
                    candidate = inject_paths.get(k)
                    if candidate and isinstance(candidate, list) and len(candidate) > 1:
                        path = candidate[:-1]  # parent container (drop leaf field)
                        break
                if path is not None:
                    break

        # Strategy 3: metric_keys as inject_paths keys — e.g. widget rp_kms_lt has
        # metric_keys=["real_yield"] and inject_paths["real_yield"] exists.
        if path is None and metric_keys:
            for mk in metric_keys:
                candidate = inject_paths.get(str(mk))
                if candidate and isinstance(candidate, list):
                    path = candidate
                    break

        if path and isinstance(path, list):
            cur = screen_data
            for key in path:
                if isinstance(cur, dict):
                    cur = cur.get(key)
                else:
                    cur = None
                    break
            if isinstance(cur, dict):
                kpi_data = cur
    except Exception:
        pass

    # Strategy 4: shallow kpis dict fallback (screens that store kpis at root level)
    if kpi_data is None:
        kpis = screen_data.get("kpis") or {}
        kpi_data = kpis.get(widget_id)

    if kpi_data and isinstance(kpi_data, dict):
        _SKIP = {"icon", "color", "title", "description", "label", "format", "prefix", "suffix"}
        for k, v in kpi_data.items():
            # Skip nested dicts/lists — they are sibling KPI containers, not this widget's values.
            if v is not None and k not in _SKIP and not isinstance(v, (dict, list)):
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    # Last resort: full screen summary (may include unrelated KPIs)
    lines.append(_summarize_screen_data(screen_data))
    return "\n".join(lines)


# ─── Extracción de menciones @{Widget Name} ──────────────────────────────────
_AT_MENTION_RE = re.compile(r"@\{([^}]+)\}")
_INTERNAL_ARTIFACT_RE = re.compile(
    r'```[\w]*\s*\{[\s\S]*?\}\s*```'
    r'|\{\s*"name"\s*:\s*"[a-z_]+"\s*,[\s\S]{0,800}?\}',
    re.DOTALL,
)


def _extract_at_mention(text: str) -> Optional[str]:
    """Extrae el primer @{Nombre Widget} del mensaje, devuelve solo el nombre interior."""
    m = _AT_MENTION_RE.search(text or "")
    return m.group(1).strip() if m else None


def _widget_display_name(w: Any) -> str:
    """Devuelve el nombre amigable de un widget: label > title > widget_id titlecased."""
    meta = getattr(w, "meta", {}) or {}
    return (
        meta.get("label")
        or meta.get("title")
        or getattr(w, "widget_id", "").replace("_", " ").title()
    )


def _clean_response_text(text: str) -> str:
    """Elimina artefactos internos (JSON tool calls, notas de uso interno) de la respuesta del LLM."""
    if not text:
        return text
    cleaned = _INTERNAL_ARTIFACT_RE.sub("", text)
    cleaned = re.sub(
        r'^(Recuerda que|Esta llamada|La respuesta al user|El output de|Una forma práctica).*$',
        "",
        cleaned,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    return cleaned if cleaned.strip() else text


# ─── Detección de mensajes casuales/saludos ───────────────────────────────────
_CASUAL_PATTERNS = [
    r"\bhola\b", r"\bbuenos\s+(d[ií]as|tardes|noches)\b", r"\bbuenas\b",
    r"\bhey\b", r"\bhi\b", r"\bqu[eé]\s+tal\b", r"\bc[oó]mo\s+est[aá]s\b",
    r"\bqu[eé]\s+puedes\b", r"\bqu[eé]\s+haces\b", r"\ben\s+qu[eé]\s+(me\s+)?ayud",
    r"\bpu[eé]des\s+ayudarme\b", r"\bc[oó]mo\s+te\s+llamas\b", r"\bqui[eé]n\s+eres\b",
    r"\bpara\s+qu[eé]\s+sirves\b", r"\bqu[eé]\s+sabes\b",
]


def _is_casual_message(text: str) -> bool:
    """Devuelve True si el mensaje parece un saludo o pregunta general, no una consulta de datos."""
    low = (text or "").lower().strip()
    if len(low.split()) <= 2:
        return True
    return any(re.search(pat, low) for pat in _CASUAL_PATTERNS)


async def _disambiguate_with_llm(user_message: str, candidates: list) -> str:
    """
    Genera una respuesta amigable cuando hay ambigüedad KPI o el mensaje es un saludo.
    Para saludos → se presenta y explica capacidades.
    Para consultas ambiguas → pide clarificación mencionando los KPIs candidatos con nombres amigables.
    """
    names_friendly = [_widget_display_name(c) for c in candidates[:3]]
    is_casual = _is_casual_message(user_message)
    if is_casual:
        context = (
            "El usuario escribió un saludo o pregunta general. "
            "Preséntate brevemente como Zamy, menciona 2-3 cosas que puedes hacer "
            "(analizar KPIs, revisar tendencias, comparar vs meta, detectar anomalías) "
            "y sugiere que hagan una pregunta concreta sobre los datos del dashboard."
        )
    else:
        context = (
            f"El usuario preguntó algo que podría referirse a varios indicadores: "
            f"{', '.join(names_friendly)}. "
            "Pide amablemente que precise cuál le interesa, listando las opciones con nombres amigables. "
            "Sé breve y profesional."
        )
    try:
        async with AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama") as client:
            resp = await client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres Zamy, asistente de analítica de negocio integrado en un dashboard. "
                            "Responde siempre en español, de forma breve (máximo 3 oraciones), "
                            "cálida y profesional. No repitas el contexto técnico, solo responde naturalmente."
                        ),
                    },
                    {"role": "user", "content": f"Instrucción: {context}\n\nMensaje del usuario: {user_message}"},
                ],
                max_tokens=180,
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text
    except Exception as e:
        logger.warning("_disambiguate_with_llm failed: %s", e)

    if is_casual:
        return (
            "¡Hola! Soy Zamy, tu asistente de analítica. "
            "Puedo analizar KPIs, revisar tendencias, comparar contra metas y detectar anomalías. "
            "¿Sobre qué indicador o pantalla te gustaría comenzar?"
        )
    options = " | ".join(names_friendly)
    return f"Parece que tu pregunta puede referirse a: {options}. ¿Podrías indicar cuál te interesa para darte el análisis exacto?"


# El agente se crea después de definir las herramientas que lo usan
def _create_agent() -> Agent[DashboardDeps, str]:
    ollama_client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    model = OpenAIChatModel(
        OLLAMA_MODEL,
        provider=OpenAIProvider(openai_client=ollama_client),
    )

    agent = Agent[DashboardDeps, str](
        model,
        deps_type=DashboardDeps,
        output_type=str,
        system_prompt="Eres Zamy, asistente inteligente de negocio. Responde siempre en español.",
    )

    @agent.system_prompt
    def system_prompt_with_context(ctx: RunContext[DashboardDeps]) -> str:
        """Prompt base más inyección del contexto actual del dashboard."""
        base = (
            "Eres Zamy, el asistente inteligente de negocio integrado en el dashboard de analítica. "
            "Tu personalidad es proactiva, clara y conversacional. Siempre respondes en español o Ingles.\n\n"

            "## Capacidades\n"
            "- **Analítica de datos**: interpretas KPIs, tendencias, comparativos vs meta, variaciones, "
            "desglose por dimensiones y anomalías detectadas en los datos del dashboard.\n"
            "- **Insights de cartas**: cada tarjeta (widget) del dashboard tiene un cajón de análisis. "
            "Puedes explicar en detalle qué significa un valor, por qué subió o bajó, y qué acción tomar.\n"
            "- **Operaciones y salud organizacional**: puedes analizar datos de taller, flota, disponibilidad, "
            "costos operativos, cuentas por cobrar, o cualquier indicador operativo que aparezca en el dashboard.\n"
            "- **Conversación general**: si el usuario hace preguntas abiertas sobre negocio, gestión, "
            "metodologías o temas relacionados con su industria, responde con criterio profesional.\n"
            "- **Accesibilidad**: si el usuario escribe con errores ortográficos o de forma informal, "
            "entiende la intención y responde igual de bien.\n\n"

            "## Reglas estrictas\n"
            "1. NUNCA inventes números, métricas ni valores: usa solo los datos que obtienes de las herramientas "
            "(list_available_screens, get_screen_summary).\n"
            "2. Si necesitas datos de una pantalla o KPI, invoca la herramienta antes de responder.\n"
            "3. Si no encuentras datos, dilo con claridad y sugiere qué hacer (abrir la pantalla correcta, "
            "aplicar filtros, verificar conexión).\n"
            "4. No generes SQL directamente; las herramientas se encargan del acceso a datos.\n"
            "5. Respuestas concisas: ve al punto. Si la respuesta es larga, usa bullets o secciones cortas.\n"
            "6. Si detectas anomalías en los datos (caídas bruscas, valores en cero, desviaciones de meta), "
            "señálalas proactivamente aunque el usuario no las haya preguntado.\n"
            "7. COMPARACIONES — regla obligatoria: cuando compares dos períodos, SIEMPRE muestra ambos valores "
            "absolutos antes del porcentaje. Formato: 'Período A: $X → Período B: $Y (±Z%)'. "
            "Nunca respondas solo con el porcentaje.\n"
            "8. LENGUAJE NATURAL: el usuario puede preguntar con términos coloquiales ('ingreso por viaje', "
            "'cuánto gasté', 'cómo me fue en cobranza'). Identifica la métrica correspondiente en los datos "
            "y responde sin pedirle que use términos técnicos.\n"
        )
        ctx_str = ctx.deps.context.to_display_string()
        if ctx_str and ctx_str != "Sin contexto de pantalla":
            base += f"\n## Contexto actual del usuario\n{ctx_str}\n"
            base += (
                "Usa este contexto para personalizar tu respuesta: "
                "habla de los datos de esta pantalla específica y con los filtros activos.\n"
            )
        return base

    @agent.tool
    def list_available_screens(ctx: RunContext[DashboardDeps]) -> str:
        """Lista los IDs de pantallas/dashboards disponibles en el sistema."""
        dm = ctx.deps.data_manager
        tenant_db = getattr(ctx.deps.context, "current_db", None) if ctx.deps.context else None
        screen_map = dm.get_screen_map(tenant_db)
        if not screen_map:
            return "No hay pantallas configuradas."
        screens = list(screen_map.keys())
        return "Pantallas disponibles: " + ", ".join(screens)

    @agent.tool
    def get_screen_summary(
        ctx: RunContext[DashboardDeps],
        screen_id: str,
        use_context_filters: bool = True,
    ) -> str:
        """
        Obtiene un resumen de los datos actuales de una pantalla del dashboard.
        screen_id: ID de la pantalla (ej. home, operational-dashboard).
        use_context_filters: si True, usa los filtros del contexto actual del usuario cuando estén disponibles.
        """
        dm = ctx.deps.data_manager
        filters = None
        if use_context_filters and ctx.deps.context.filters:
            filters = ctx.deps.context.filters
        try:
            data = dm.get_screen(screen_id, use_cache=True, allow_stale=True, filters=filters)
        except Exception as e:
            logger.warning("get_screen_summary error: %s", e)
            return f"Error al cargar la pantalla {screen_id}: {str(e)}"
        summary = _summarize_screen_data(data)
        return f"Resumen de '{screen_id}':\n{summary}"

    return agent


# ─── Singleton del agente (lazy) ─────────────────────────────────────────────
_agent: Optional[Agent[DashboardDeps, str]] = None


async def _explain_diagnostic_with_llm(user_message: str, raw_diagnostic: str) -> str:
    """
    Pasa el diagnóstico técnico por el LLM para obtener una explicación en lenguaje natural:
    qué significa, qué revisar y por qué. Si falla, devuelve el texto crudo.
    """
    try:
        async with AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama") as client:
            system = (
                "Eres Zamy, analista de negocio integrado en un dashboard de analítica.\n\n"
                "## Regla #1 — Respuesta inmediata\n"
                "Cuando tengas datos, responde DIRECTAMENTE con los valores. "
                "NUNCA preguntes al usuario qué quiere ver ni pidas aclaraciones. "
                "Si los datos están presentes, preséntelos de una vez.\n\n"
                "## Regla #2 — Estructura de respuesta\n"
                "Usa este orden:\n"
                "1. **Valor actual**: el número principal del KPI (con unidad o signo).\n"
                "2. **Comparación**: si hay valor anterior, muestra AMBOS valores y la variación. "
                "Formato obligatorio: 'Año anterior: $X → Actual: $Y (±Z%)'. "
                "NUNCA omitas uno de los dos valores.\n"
                "3. **Evaluación**: ¿es positivo, negativo o neutral para el negocio? "
                "Una oración corta.\n"
                "4. **Acción** (solo si es relevante): qué revisar o hacer a continuación.\n\n"
                "## Regla #3 — Concisión\n"
                "Máximo 3-4 bullets o 2 párrafos cortos. Sin texto de relleno.\n\n"
                "## Regla #4 — Lenguaje coloquial\n"
                "El usuario puede usar términos como 'ingreso por viaje', 'clientes que atendimos', "
                "'cuánto gasté'. Identifica la métrica en los datos y responde directamente, "
                "sin pedirle que use términos técnicos.\n\n"
                "Responde siempre en español."
            )
            user_prompt = (
                f"Pregunta: {user_message}\n\n"
                f"Datos del indicador:\n{raw_diagnostic}\n\n"
                "Responde directamente con los valores y tu análisis."
            )
            resp = await client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=520,
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text
    except Exception as e:
        logger.warning("_explain_diagnostic_with_llm failed, using raw diagnostic: %s", e)
    return raw_diagnostic


def generate_insight_sync(widget_title: str, stats_summary: str) -> str:
    async def _call() -> str:
        system = (
            "Eres Zamy, analista de negocio integrado en un dashboard.\n"
            "Recibes estadísticas calculadas sobre un indicador o gráfica del dashboard.\n\n"
            "Tu tarea: escribe exactamente 3 bullets cortos en español. "
            "Cada bullet comienza con un emoji de estado:\n"
            "• 📊 **Estado**: evaluación directa del indicador (positivo / regular / crítico) "
            "con el valor o rango más relevante.\n"
            "• 🔍 **Hallazgo**: lo más importante que revelan los datos "
            "(tendencia, dispersión, valores extremos, comparación con promedio).\n"
            "• 💡 **Recomendación**: acción concreta que el negocio puede tomar. "
            "Si los datos son normales, di qué monitorear.\n\n"
            "Reglas:\n"
            "- NO repitas números literalmente: interprétalos ('alta variabilidad', 'por encima del promedio', etc.).\n"
            "- Sé específico al indicador recibido, no genérico.\n"
            "- Máximo 1-2 líneas por bullet.\n"
            "- NUNCA hagas preguntas al usuario."
        )
        prompt = f"Indicador: {widget_title}\n\nEstadísticas:\n{stats_summary}\n\nInsights:"
        async with AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama") as client:
            resp = await client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=280,
            )
            return (resp.choices[0].message.content or "").strip()

    try:
        future = _executor.submit(_run_async_in_new_loop, _call())
        return future.result(timeout=35)
    except Exception as e:
        logger.warning("generate_insight_sync failed: %s", e)
        return ""


def _format_diagnostic_response(
    diag: Any,
    lineage_data: Optional[Dict[str, Any]],
    widget: Any,
) -> str:
    """Formatea DiagnosticResult y opcionalmente lineage a texto para el usuario."""
    lines = [f"**Widget:** {getattr(widget, 'widget_id', 'N/A')}"]
    if diag.aggregate_value:
        lines.append("**Valor actual:** " + json.dumps(diag.aggregate_value, ensure_ascii=False, default=str))
    if diag.meta_compare and diag.meta_compare.get("rows"):
        lines.append("**Comparación con meta:** " + json.dumps(diag.meta_compare["rows"], ensure_ascii=False, default=str))
    if diag.findings:
        lines.append("**Hallazgos:**")
        for f in diag.findings:
            lines.append(f"  - {f.get('descripcion', f)}")
    if diag.breakdown_rows:
        lines.append(f"**Desglose:** {len(diag.breakdown_rows)} filas.")
    if lineage_data:
        lines.append("**Cálculo (lineage):**")
        for m in (lineage_data.get("metric_formulas") or [])[:5]:
            lines.append(f"  - {m.get('name', m.get('metric_key'))}: {m.get('formula', 'N/A')}")
        if lineage_data.get("global_filters"):
            lines.append("  Filtros activos: " + ", ".join(lineage_data["global_filters"]))
    return "\n".join(lines)


def _get_agent() -> Agent[DashboardDeps, str]:
    global _agent
    if _agent is None:
        _agent = _create_agent()
    return _agent


# ─── Servicio público (compatible con el callback actual de Dash) ───────────────
class AIChatService:
    def __init__(self) -> None:
        self.conversation_history: List[Dict[str, str]] = []
        self._last_run_result: Any = None
        self._last_resolved_widget_id: Optional[str] = None

    def get_response(
        self,
        user_message: str,
        dashboard_context: Optional[DashboardContext] = None,
    ) -> Tuple[str, str]:
        """
        Responde al mensaje del usuario usando el agente (Ollama + tool calling).
        Flujo asíncrono ejecutado de forma síncrona para el callback de Dash.
        Sin contexto de pantalla (screen_id), devuelve mensaje pidiendo abrir una pantalla.
        """
        if not dashboard_context or not (getattr(dashboard_context, "screen_id", None) or "").strip():
            ts = time.strftime("%H:%M")
            msg = "Abre una pantalla del dashboard para que pueda analizar los datos en contexto."
            self.conversation_history.append({"role": "user", "content": user_message, "timestamp": ts})
            self.conversation_history.append({"role": "assistant", "content": msg, "timestamp": ts})
            return msg, ts
        try:
            # Ejecutar el agente en un hilo con su propio event loop para evitar
            # "This event loop is already running" cuando Dash ya tiene un loop activo.
            coro = self.get_response_async(user_message, dashboard_context)
            future = _executor.submit(_run_async_in_new_loop, coro)
            return future.result(timeout=120)
        except Exception as e:
            logger.exception("Agent run failed: %s", e)
            response_text = f"Error interno: {type(e).__name__}: {e}"
            timestamp = time.strftime("%H:%M")
            self._last_run_result = None
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": timestamp,
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": timestamp,
            })
            return response_text, timestamp

    async def get_response_async(
        self,
        user_message: str,
        dashboard_context: Optional[DashboardContext] = None,
    ) -> Tuple[str, str]:
        """Versión asíncrona: orquestación intent → resolución KPI → diagnóstico → formato."""
        from services.data_manager import data_manager
        from services.intent_service import classify as classify_intent
        from services.kpi_resolution_service import resolve as resolve_kpi

        dashboard_context = dashboard_context or DashboardContext()
        screen_id = (dashboard_context.screen_id or "").strip()
        widget_id_ctx = getattr(dashboard_context, "widget_id", None) or None
        current_db = getattr(dashboard_context, "current_db", None) or ""
        filters = dashboard_context.filters or {}

        logger.info(
            "get_response_async context: screen_id=%s filters=%s date_range=%s current_db=%s",
            screen_id, filters, getattr(dashboard_context, "date_range", None), current_db or "(vacío)",
        )

        intent_result = classify_intent(user_message)

        if _is_casual_message(user_message):
            deps = DashboardDeps(context=dashboard_context, data_manager=data_manager)
            agent = _get_agent()
            try:
                message_history = None
                if self._last_run_result is not None:
                    try:
                        message_history = self._last_run_result.all_messages()
                    except Exception:
                        message_history = None
                result = await agent.run(user_message, deps=deps, message_history=message_history)
                self._last_run_result = result
                response_text = result.output if isinstance(result.output, str) else str(result.output)
            except Exception as e:
                logger.warning("Agent run (casual) failed: %s", e)
                response_text = (
                    "¡Hola! Soy Zamy, tu asistente de analítica. "
                    "Puedo analizar KPIs, revisar tendencias, comparar contra metas y detectar anomalías. "
                    "¿Sobre qué indicador te gustaría comenzar?"
                )
            timestamp = time.strftime("%H:%M")
            self.conversation_history.append({"role": "user", "content": user_message, "timestamp": timestamp})
            self.conversation_history.append({"role": "assistant", "content": response_text, "timestamp": timestamp})
            return response_text, timestamp

        effective_widget_id = widget_id_ctx or self._last_resolved_widget_id
        at_mention = _extract_at_mention(user_message)
        query_for_resolution = at_mention if at_mention else user_message

        resolution = resolve_kpi(query_for_resolution, screen_id, widget_id_from_context=effective_widget_id, tenant_db=current_db)

        if resolution.status == "RESUELTO" and resolution.resolved_widget:
            self._last_resolved_widget_id = resolution.resolved_widget.widget_id
            try:
                # Use widget's own screen_id (resolver may have matched globally on a different screen)
                widget_screen_id = getattr(resolution.resolved_widget, "screen_id", None) or screen_id
                logger.info("Extracting context data for widget=%s on screen=%s",
                            getattr(resolution.resolved_widget, "widget_id", None), widget_screen_id)
                screen_data = data_manager.get_screen(widget_screen_id, use_cache=True, allow_stale=True, filters=filters, db_name=current_db or None)
                if not isinstance(screen_data, dict) or not screen_data:
                    screen_data = data_manager.get_screen(screen_id, use_cache=True, allow_stale=True, filters=filters, db_name=current_db or None)
                if not isinstance(screen_data, dict):
                    screen_data = {}
                raw_diagnostic = _extract_widget_data_text(screen_data, resolution.resolved_widget)
                response_text = await _explain_diagnostic_with_llm(user_message, raw_diagnostic)
            except Exception as e:
                logger.exception("Data extraction failed: %s", e)
                response_text = f"Error al obtener los datos: {type(e).__name__}: {e}"
            timestamp = time.strftime("%H:%M")
            self.conversation_history.append({"role": "user", "content": user_message, "timestamp": timestamp})
            self.conversation_history.append({"role": "assistant", "content": response_text, "timestamp": timestamp})
            return response_text, timestamp

        if resolution.status == "AMBIGUO" and resolution.candidates:
            response_text = await _disambiguate_with_llm(user_message, resolution.candidates)
            timestamp = time.strftime("%H:%M")
            self.conversation_history.append({"role": "user", "content": user_message, "timestamp": timestamp})
            self.conversation_history.append({"role": "assistant", "content": response_text, "timestamp": timestamp})
            return response_text, timestamp

        deps = DashboardDeps(context=dashboard_context, data_manager=data_manager)
        agent = _get_agent()
        try:
            message_history = None
            if self._last_run_result is not None:
                try:
                    message_history = self._last_run_result.all_messages()
                except Exception:
                    message_history = None
            result = await agent.run(user_message, deps=deps, message_history=message_history)
            self._last_run_result = result
            response_text = result.output if isinstance(result.output, str) else str(result.output)
            response_text = _clean_response_text(response_text)
        except Exception as e:
            logger.exception("Agent run failed: %s", e)
            response_text = (
                "No pude procesar tu mensaje. Comprueba que Ollama esté en marcha "
                "(localhost:11434) y que el modelo esté disponible."
            )
            self._last_run_result = None

        timestamp = time.strftime("%H:%M")
        self.conversation_history.append({"role": "user", "content": user_message, "timestamp": timestamp})
        self.conversation_history.append({"role": "assistant", "content": response_text, "timestamp": timestamp})
        return response_text, timestamp

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_history

    def clear_history(self) -> None:
        self.conversation_history.clear()
        self._last_run_result = None
        self._last_resolved_widget_id = None

    def get_quick_actions(self) -> List[Dict[str, str]]:
        return [
            {
                "icon": "tabler:chart-line",
                "label": "Ver tendencias de ventas",
                "action": "¿Cuáles son las tendencias de ventas actuales?",
            },
            {
                "icon": "tabler:report-money",
                "label": "Análisis financiero",
                "action": "Dame un resumen del análisis financiero",
            },
            {
                "icon": "tabler:users",
                "label": "Información de clientes",
                "action": "¿Qué me puedes decir sobre la cartera de clientes?",
            },
            {
                "icon": "tabler:help",
                "label": "¿Qué puedes hacer?",
                "action": "¿En qué puedes ayudarme?",
            },
        ]


ai_chat_service = AIChatService()
