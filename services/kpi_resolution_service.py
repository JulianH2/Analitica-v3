"""
Motor de resolución de KPI: dado question + screen_id (y opcional widget_id),
devuelve RESUELTO (un widget), AMBIGUO (hasta 3 candidatos) o NO_ENCONTRADO.
Ranking por coincidencia de entidades (métrica, dimensiones, términos).
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional

from dashboard_core.metadata_engine import MetadataEngine
from services.widget_catalog_service import WidgetDefinition, list_widgets_by_screen, list_all_widgets_global, get_widget_definition


@dataclass
class ResolutionResult:
    status: str  # RESUELTO | AMBIGUO | NO_ENCONTRADO
    resolved_widget: Optional[WidgetDefinition] = None
    candidates: List[WidgetDefinition] = field(default_factory=list)

_ALIAS_EXPANSIONS: dict = {
    "viaje":          ["trip", "viaje"],
    "viajes":         ["trips", "trip", "viaje"],
    "ingreso":        ["revenue", "ingreso"],
    "ingresos":       ["revenue", "revenues", "ingreso"],
    "costo":          ["cost", "costo"],
    "costos":         ["costs", "cost", "costo"],
    "gasto":          ["expense", "cost", "gasto"],
    "gastos":         ["expenses", "costs", "gasto"],
    "cobranza":       ["receivable", "cobranza", "collection"],
    "cobrar":         ["receivable", "cobranza"],
    "disponibilidad": ["availability", "disponibilidad"],
    "disponible":     ["availability", "disponibilidad"],
    "flota":          ["fleet", "flota"],
    "unidad":         ["unit", "unidad"],
    "unidades":       ["units", "unit", "unidad"],
    "taller":         ["workshop", "taller", "maintenance"],
    "mantenimiento":  ["maintenance", "workshop", "mantenimiento"],
    "facturacion":    ["invoice", "billing", "facturacion"],
    "factura":        ["invoice", "factura"],
    "km":             ["km", "kms", "kilometros", "mileage"],
    "kilometros":     ["km", "kms", "kilometros"],
    "utilizar":       ["utilization", "utilizacion"],
    "utilizacion":    ["utilization", "utilizacion"],
    "utilizada":      ["utilized", "utilization", "unit"],
    "utilizadas":     ["utilized", "units", "utilizacion"],
    "total":          ["total"],
    # Clientes
    "cliente":        ["customer", "client", "served", "cliente"],
    "clientes":       ["customers", "customer", "client", "served", "clientes"],
    "servido":        ["served", "customer", "client", "servido"],
    "servidos":       ["served", "customers", "clients", "servido"],
    "atendido":       ["served", "attended", "customer"],
    "atendidos":      ["served", "customers", "attended"],
    # Rutas / conductores
    "ruta":           ["route", "ruta"],
    "rutas":          ["routes", "route", "ruta"],
    "conductor":      ["driver", "conductor"],
    "conductores":    ["drivers", "driver", "conductor"],
    "operador":       ["operator", "driver", "operador"],
    "operadores":     ["operators", "drivers", "operador"],
    # Rentabilidad / márgenes
    "margen":         ["margin", "profit", "margen"],
    "ganancia":       ["profit", "gain", "revenue", "ganancia"],
    "ganancias":      ["profit", "gains", "revenue", "ganancia"],
    "utilidad":       ["profit", "utility", "utilidad"],
    "utilidades":     ["profits", "utility", "utilidad"],
    "neto":           ["net", "neto"],
    "bruto":          ["gross", "bruto"],
    # Rendimiento / eficiencia
    "eficiencia":     ["efficiency", "yield", "eficiencia"],
    "rendimiento":    ["performance", "yield", "rendimiento"],
    "promedio":       ["average", "avg", "promedio"],
    "variacion":      ["variation", "change", "delta", "variacion"],
    # Operativa
    "operativo":      ["operational", "operation", "operativo"],
    "operativos":     ["operational", "operations", "operativo"],
    "orden":          ["order", "orden"],
    "ordenes":        ["orders", "order", "orden"],
    "servicio":       ["service", "servicio"],
    "servicios":      ["services", "service", "servicio"],
    "entrada":        ["entry", "input", "entrada"],
    "entradas":       ["entries", "inputs", "entry", "entrada"],
    # Tiempo / periodos
    "mes":            ["month", "mes"],
    "mensual":        ["monthly", "month", "mensual"],
    "anual":          ["annual", "year", "anual"],
    "año":            ["year", "annual", "año"],
    "trimestre":      ["quarter", "quarterly", "trimestre"],
    # Combustible / consumo
    "litro":          ["liter", "litre", "fuel", "consumption", "litro"],
    "litros":         ["liters", "litres", "fuel", "consumption", "litros"],
    "combustible":    ["fuel", "gasoline", "diesel", "combustible"],
    "gasolina":       ["gasoline", "fuel", "gasolina"],
    "diesel":         ["diesel", "fuel", "diesel"],
    "consumo":        ["consumption", "consumed", "usage", "consumo"],
    "consumidos":     ["consumed", "usage", "fuel", "consumidos"],
    # Cargo / peso / distancia
    "carga":          ["cargo", "load", "weight", "carga"],
    "peso":           ["weight", "cargo", "peso"],
    "distancia":      ["distance", "km", "mileage", "distancia"],
    # Financiero extra
    "deuda":          ["debt", "receivable", "deuda"],
    "cobro":          ["collection", "receivable", "cobro"],
    "cobros":         ["collections", "receivable", "cobro"],
    "pago":           ["payment", "pago"],
    "pagos":          ["payments", "pago"],
}


def _normalize_tokens(text: str) -> List[str]:
    if not text or not isinstance(text, str):
        return []
    low = text.lower().strip()
    tokens = re.findall(r"[a-záéíóúñ0-9]+", low)
    return [t for t in tokens if len(t) > 1]


def _expand_tokens(tokens: List[str]) -> List[str]:
    """Expand Spanish colloquial tokens to include English/technical equivalents."""
    expanded = list(tokens)
    for t in tokens:
        for alias in _ALIAS_EXPANSIONS.get(t, []):
            if alias not in expanded:
                expanded.append(alias)
    return expanded


def _widget_search_text(w: WidgetDefinition, metrics_map: dict) -> str:
    parts = [w.widget_id.replace("_", " "), w.screen_id.replace("-", " ")]
    for mk in w.metric_keys:
        m = metrics_map.get(mk)
        if isinstance(m, dict) and m.get("name"):
            parts.append(m["name"])
    for d in w.dimensions:
        parts.append(d.replace(".", " ").replace("_", " "))
    for col in (w.meta.get("columns") or []):
        if isinstance(col, dict) and col.get("label"):
            parts.append(col["label"])
    if w.meta.get("title"):
        parts.append(w.meta["title"])
    if w.meta.get("label"):
        parts.append(w.meta["label"])
    return " ".join(parts)


def _entity_score(question_tokens: List[str], widget_text: str, base_count: Optional[int] = None) -> float:
    """Calcula qué fracción de los tokens de la pregunta aparecen en el texto del widget.
    base_count permite usar el conteo de tokens originales (sin expandir) como denominador,
    evitando que la expansión de aliases diluya el score."""
    if not question_tokens:
        return 0.0
    widget_tokens = set(_normalize_tokens(widget_text))
    if not widget_tokens:
        return 0.0
    matches = sum(1 for t in question_tokens if t in widget_tokens)
    denominator = base_count if base_count and base_count > 0 else len(question_tokens)
    return matches / denominator


# Umbrales: arriba de HIGH -> RESUELTO; entre LOW y HIGH -> AMBIGUO; abajo -> NO_ENCONTRADO
SCORE_HIGH = 0.25
SCORE_LOW = 0.08
MAX_CANDIDATES = 3


def resolve(
    question: str,
    screen_id: str,
    widget_id_from_context: Optional[str] = None,
    tenant_db: Optional[str] = None,
) -> ResolutionResult:
    """
    Resuelve la pregunta a un widget (o candidatos).
    Si widget_id_from_context viene y es válido para la pantalla, devuelve RESUELTO con ese widget.
    """
    q_clean = (question or "").strip()
    question_tokens = _normalize_tokens(q_clean)
    expanded_tokens = _expand_tokens(question_tokens)
    metrics_map = (MetadataEngine().get_context(tenant_db) or {}).get("metrics") or {}

    widgets = list_widgets_by_screen(screen_id, tenant_db=tenant_db)
    used_global = False
    if not widgets:
        widgets = list_all_widgets_global(tenant_db=tenant_db)
        used_global = True

    # Exact widget_id match always wins
    q_id = q_clean.lower().replace(" ", "_")
    for w in widgets:
        if w.widget_id.lower() == q_id or w.widget_id.lower() == q_clean.lower():
            return ResolutionResult(status="RESUELTO", resolved_widget=w, candidates=[])

    # NLP/semantic resolution takes priority over conversation memory.
    # Explicit questions ("¿cuánto fue el ingreso?") override the last resolved widget.
    # base_count = original token count antes de expandir (evita dilución del score).
    base_count = len(question_tokens)
    result = _rank_and_resolve(expanded_tokens, widgets, metrics_map, base_count=base_count)
    if result.status == "RESUELTO":
        return result

    # NLP didn't find a confident match — fall back to context/memory so
    # follow-up messages ("¿y el mes pasado?") continue on the same KPI.
    if widget_id_from_context and screen_id:
        w = get_widget_definition(screen_id, widget_id_from_context, tenant_db=tenant_db)
        if w is not None:
            return ResolutionResult(status="RESUELTO", resolved_widget=w, candidates=[])

    if result.status == "NO_ENCONTRADO" and not used_global:
        global_widgets = list_all_widgets_global(tenant_db=tenant_db)
        global_result = _rank_and_resolve(expanded_tokens, global_widgets, metrics_map, base_count=base_count)
        if global_result.candidates:
            return ResolutionResult(
                status="AMBIGUO",
                resolved_widget=None,
                candidates=global_result.candidates[:MAX_CANDIDATES],
            )
    return result


def _rank_and_resolve(
    question_tokens: List[str],
    widgets: List[WidgetDefinition],
    metrics_map: dict,
    base_count: Optional[int] = None,
) -> ResolutionResult:
    if not question_tokens:
        return ResolutionResult(status="NO_ENCONTRADO", resolved_widget=None, candidates=widgets[:MAX_CANDIDATES])

    scored: List[tuple] = []
    for w in widgets:
        text = _widget_search_text(w, metrics_map)
        score = _entity_score(question_tokens, text, base_count=base_count)
        scored.append((score, w))

    scored.sort(key=lambda x: -x[0])
    best_score = scored[0][0] if scored else 0.0
    best_widget = scored[0][1] if scored else None
    second_score = scored[1][0] if len(scored) > 1 else 0.0

    if best_score >= SCORE_HIGH:
        if best_score >= second_score * 2 or second_score == 0:
            return ResolutionResult(status="RESUELTO", resolved_widget=best_widget, candidates=[])
        return ResolutionResult(status="RESUELTO", resolved_widget=best_widget, candidates=[])
    if best_score >= SCORE_LOW:
        candidates = [w for _s, w in scored[:MAX_CANDIDATES]]
        return ResolutionResult(status="AMBIGUO", resolved_widget=None, candidates=candidates)
    return ResolutionResult(status="NO_ENCONTRADO", resolved_widget=None, candidates=[])
