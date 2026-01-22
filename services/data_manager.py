import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

from flask import session

from dashboard_core.query_builder import SmartQueryBuilder
from dashboard_core.db_helper import execute_dynamic_query
from services.real_data_service import RealDataService

Json = Union[Dict[str, Any], List[Any]]
Path = List[Union[str, int]]


@dataclass
class CacheEntry:
    data: Json
    ts: float  # epoch seconds


class DataManager:
    _instance: Optional["DataManager"] = None
    base_service: RealDataService
    qb: SmartQueryBuilder
    cache: Dict[str, CacheEntry]
    DEFAULT_TTL_SECONDS: int
    SCREEN_MAP: Dict[str, Dict[str, Any]]

    def __new__(cls) -> "DataManager":
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.base_service = RealDataService()
            cls._instance.qb = SmartQueryBuilder()
            cls._instance.cache = {}
            cls._instance.DEFAULT_TTL_SECONDS = 30

            # --- CONFIGURACIÓN DE PANTALLAS ---
            cls._instance.SCREEN_MAP = {
                "admin-banks": {
                    "section_key": "administracion",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "admin-collection": {
                    "section_key": "administracion",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},     # luego lo llenas
                    "inject_paths": {},    # luego lo llenas
                },
                "admin-payables": {
                    "section_key": "administracion",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},     # luego lo llenas
                    "inject_paths": {},    # luego lo llenas
                },
                "home": {
                    "section_keys": ["operaciones", "mantenimiento", "administracion"],
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-costs": {
                    "section_key": "operaciones",
                    "ttl_seconds": 60,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-dashboard": {
                    "section_keys": ["operaciones", "mantenimiento", "administracion"],
                    "ttl_seconds": 60,
                    
                    # 1. KPIs Escalares (Tarjetas Superiores)
                    "kpi_roadmap": {
                        # Ingreso
                        "ingreso_valor": "ingreso_viaje",
                        "ingreso_meta": "meta_ingreso_viaje",
                        "ingreso_delta": "pct_desviacion_ingreso_vs_anterior",
                        "ingreso_ytd": "ingreso_viaje_acumulado",
                        "ingreso_ytd_delta": "pct_desviacion_ingreso_acumulado",

                        # Viajes
                        "viajes_valor": "viajes",
                        "viajes_meta": "meta_viajes",
                        "viajes_delta": "pct_desviacion_viajes_vs_anterior",
                        "viajes_ytd": "viajes_acumulado",
                        "viajes_ytd_delta": "pct_desviacion_viajes_acumulado",

                        # Kilómetros
                        "kms_valor": "kilometros",
                        "kms_meta": "meta_kilometros",
                        "kms_delta": "pct_desviacion_kilometros_vs_anterior",
                        "kms_ytd": "kilometros_acumulado",
                        "kms_ytd_delta": "pct_desviacion_kilometros_acumulado"
                    },
                    
                    # 2. Gráficas (Series de Tiempo) -> ¡GENÉRICO!
                    # Define aquí tus gráficas sin tocar código Python
                    "chart_roadmap": {
                        "ingresos_anual": {
                            "actual": "ingreso_viaje",
                            "anterior": "ingreso_viaje_anterior",
                            "meta": "meta_ingreso_viaje"
                        },
                         "viajes_anual": {
                            "actual": "viajes",
                            "anterior": "viajes_anterior",
                            "meta": "meta_viajes"
                        }
                    },

                    "categorical_roadmap": {
                        "mix_operacion": {
                            "kpi": "ingreso_viaje",
                            "dimension": "tipo_operacion"
                        },
                        "top_rutas": {
                            "kpi": "ingreso_viaje",
                            "dimension": "ruta"
                        },
                        "top_areas": {
                            "kpi": "ingreso_viaje",
                            "dimension": "area"
                        },
                        "balanceo_unidades": {
                            "kpi": "ingreso_viaje",
                            "dimension": "unidad"
                        }
                    },

                    # 3. Rutas de Inyección (Dónde poner los datos)
                    "inject_paths": {
                        # Apuntamos al nodo del indicador para llenar valor, meta, delta, display, etc.
                        "ingreso_valor": ["operaciones", "dashboard", "indicadores", "ingreso_viaje", "valor"],
                        "ingreso_meta": ["operaciones", "dashboard", "indicadores", "ingreso_viaje", "meta"],
                        "ingreso_delta": ["operaciones", "dashboard", "indicadores", "ingreso_viaje", "monthly_delta"],
                        "ingreso_ytd": ["operaciones", "dashboard", "indicadores", "ingreso_viaje", "ytd_display"],
                        "ingreso_ytd_delta": ["operaciones", "dashboard", "indicadores", "ingreso_viaje", "ytd_delta"],

                        "viajes_valor": ["operaciones", "dashboard", "indicadores", "viajes", "valor"],
                        "viajes_meta": ["operaciones", "dashboard", "indicadores", "viajes", "meta"],
                        "viajes_delta": ["operaciones", "dashboard", "indicadores", "viajes", "monthly_delta"],
                        "viajes_ytd": ["operaciones", "dashboard", "indicadores", "viajes", "ytd_display"],
                        "viajes_ytd_delta": ["operaciones", "dashboard", "indicadores", "viajes", "ytd_delta"],

                        "kms_valor": ["operaciones", "dashboard", "indicadores", "kilometros", "valor"],
                        "kms_meta": ["operaciones", "dashboard", "indicadores", "kilometros", "meta"],
                        "kms_delta": ["operaciones", "dashboard", "indicadores", "kilometros", "monthly_delta"],
                        "kms_ytd": ["operaciones", "dashboard", "indicadores", "kilometros", "ytd_display"],
                        "kms_ytd_delta": ["operaciones", "dashboard", "indicadores", "kilometros", "ytd_delta"],
                        
                        # Gráficas de Línea/Barras
                        "ingresos_anual": ["operaciones", "dashboard", "graficas", "ingresos_anual"],
                        "viajes_anual": ["operaciones", "dashboard", "graficas", "viajes_anual"],

                        # Gráficas Categóricas
                        "mix_operacion": ["operaciones", "dashboard", "graficas", "mix_operacion"],
                        "top_rutas": ["operaciones", "dashboard", "tablas", "rutas_cargado"],
                        "top_areas": ["operaciones", "dashboard", "graficas", "por_area"],
                        "balanceo_unidades": ["operaciones", "dashboard", "graficas", "balanceo_unidades"]
                    },
                },
                "ops-performance": {
                    "section_key": "operaciones",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-routes": {
                    "section_key": "operaciones",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-availability": {
                    "section_key": "mantenimiento",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-dashboard": {
                    "section_key": "mantenimiento",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-inventory": {
                "section_key": "mantenimiento",
                "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-purchases": {
                    "section_key": "mantenimiento",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
            }
        return cls._instance

    # --- Métodos de Cache (Sin cambios) ---
    def _db_fingerprint(self) -> str:
        db_config = session.get("current_db")
        if not db_config: return "no-db"
        try:
            raw = json.dumps(db_config, sort_keys=True, default=str).encode("utf-8")
        except:
            raw = str(db_config).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    def _cache_key(self, screen_id: str) -> str:
        return f"{self._db_fingerprint()}::{screen_id}"

    def _is_fresh(self, entry: CacheEntry, ttl: int) -> bool:
        return (time.time() - entry.ts) <= ttl

    def get_screen(self, screen_id: str, *, use_cache=True, allow_stale=True) -> Json:
        cfg = self.SCREEN_MAP.get(screen_id)
        if not cfg: return {}
        
        ttl = int(cfg.get("ttl_seconds") or self.DEFAULT_TTL_SECONDS)
        key = self._cache_key(screen_id)

        if use_cache and key in self.cache:
            entry = self.cache[key]
            if self._is_fresh(entry, ttl) or allow_stale:
                return entry.data

        # Fallback a estructura base (con ceros)
        base = self.base_service.get_full_dashboard_data()
        keys = cfg.get("section_keys") or [cfg.get("section_key")]
        sliced = {k: base.get(k, {}) for k in keys if k}
        
        if use_cache:
            self.cache[key] = CacheEntry(data=sliced, ts=time.time())
        return sliced

    async def _resolve_any_kpi(self, db_config, kpi_id, session_results):
        """Resuelve KPI con cache local. Soporta SQL y fórmulas derivadas."""
        if kpi_id in session_results:
            return session_results[kpi_id]

        build = self.qb.build_kpi_query(kpi_id)
        if not build: return 0.0

        result = 0.0
        if build.get("type") == "sql":
            try:
                rows = await execute_dynamic_query(db_config, build["query"])
                v = list(rows[0].values())[0] if rows else 0
                result = float(v or 0)
            except Exception as e:
                print(f"ERROR SQL en KPI {kpi_id}: {e}")
                result = 0.0

        elif build.get("type") == "derived":
            formula = build.get("formula")
            import re
            # Resolvemos recursivamente cada variable de la fórmula
            if formula:
                for token in re.findall(r'[a-z_]+', formula):
                    if token in ["if", "else"]: continue
                    sub_val = await self._resolve_any_kpi(db_config, token, session_results)
                    formula = formula.replace(token, str(sub_val))
                try: result = float(eval(formula))
                except: result = 0.0

        session_results[kpi_id] = result
        return result

    # --- REFRESH INTELIGENTE (Async) ---
    async def refresh_screen(self, screen_id: str, *, use_cache=True) -> Json:
        cfg = self.SCREEN_MAP.get(screen_id)
        if not cfg: return {}

        base = self.base_service.get_full_dashboard_data()
        keys = cfg.get("section_keys") or [cfg.get("section_key")]
        data = {k: base.get(k, {}) for k in keys if k}

        db_config = session.get("current_db")
        if not db_config: return data
        
        inject_paths = cfg.get("inject_paths", {})

        session_results = {}
        # 1. Resolver KPIs Escalares (Tarjetas Principales)
        kpi_roadmap = cfg.get("kpi_roadmap", {})
        for ui_key, kpi_id in kpi_roadmap.items():
            path = inject_paths.get(ui_key)
            if not path: continue

            # CORRECCIÓN: Resolvemos SOLO el valor solicitado y lo asignamos.
            # No construimos un diccionario complejo aquí porque el 'path'
            # ya apunta al nodo hoja específico (ej. 'valor', 'meta', 'ytd_display').
            
            val = await self._resolve_any_kpi(db_config, kpi_id, session_results)
            
            # Formateo básico opcional para campos de texto (_display)
            # Si el path termina en 'display' y es dinero, podrías formatear aquí,
            # pero es más seguro enviar el dato crudo y que la Strategy lo formatee.
            #if isinstance(path[-1], str) and "display" in path[-1] and isinstance(val, (int, float)):
                 # Si prefieres enviar texto pre-formateado al display:
                 #is_money = "ingreso" in kpi_id or "costo" in kpi_id
                 #val = f"${val:,.0f}" if is_money else f"{val:,.0f}"

            self._set_path(data, path, val)

        # 2. Resolver Gráficas (Lógica GENÉRICA Nueva)
        chart_roadmap = cfg.get("chart_roadmap", {})
        for chart_key, series_map in chart_roadmap.items():
            path = inject_paths.get(chart_key)
            if not path: continue

            chart_data: Dict[str, List[Any]] = {
                "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            }

            # Itera sobre las series definidas en el mapa (actual, anterior, meta, etc.)
            for series_name, kpi_id in series_map.items():
                build = self.qb.build_series_query(kpi_id)
                values = [0.0] * 12 # Inicializa array vacío
                
                if build and "query" in build:
                    rows = await execute_dynamic_query(db_config, build["query"])
                    if rows:
                        for r in rows:
                            # Asume que el query retorna 'period' (1-12) y 'value'
                            p = r.get('period')
                            v = r.get('value', 0.0)
                            if isinstance(p, int) and 1 <= p <= 12:
                                values[p-1] = v # Asigna al mes correspondiente
                
                chart_data[series_name] = values
            
            self._set_path(data, path, chart_data)

        # 3. --- NUEVO: Resolver Gráficas Categóricas (Drill-Down) ---
        cat_roadmap = cfg.get("categorical_roadmap", {})
        for chart_key, spec in cat_roadmap.items():
            path = inject_paths.get(chart_key)
            if not path: continue
            
            kpi = spec.get("kpi")
            dim = spec.get("dimension")
            
            # Llamamos al nuevo método que creamos en QueryBuilder
            build = self.qb.build_categorical_query(kpi, dim)
            #print(f"DEBUG: Generando query para {chart_key}: {build.get('query')}")
            # Estructura estándar para Charts: { labels: [], values: [] }
            chart_data = {"labels": [], "values": []}
            
            # Estructura alternativa si es tabla (h=header, r=rows)
            # Detectamos si el path apunta a una 'tabla' para formatear diferente si es necesario
            is_table = "tablas" in path
            table_rows = []

            if build and "query" in build:
                 rows = await execute_dynamic_query(db_config, build["query"])
                 if rows:
                     for r in rows:
                         lbl = r.get("label", "N/A")
                         val = r.get("value")
                         if val is None:
                             val = 0.0
                         
                         if is_table:
                             # Formato simple para tablas: [Label, Valor]
                             # Puedes mejorar esto si quieres formatear moneda aquí
                             table_rows.append([lbl, f"${val:,.0f}"]) 
                         else:
                             # Formato para Gráficas (Pie/Barra)
                             chart_data["labels"].append(lbl)
                             chart_data["values"].append(val)
            
            if is_table:
                # Si es tabla, inyectamos estructura de tabla
                # Asumimos headers simples. Puedes parametrizarlos si prefieres.
                self._set_path(data, path, {
                    "h": ["Concepto", "Valor"], 
                    "r": table_rows
                })
            else:
                # Si es gráfica, inyectamos labels/values
                self._set_path(data, path, chart_data)

        if use_cache:
            self.cache[self._cache_key(screen_id)] = CacheEntry(data=data, ts=time.time())

        return data

    def _set_path(self, data: Dict[str, Any], path: Path, value: Any) -> None:
        cur: Any = data
        for key in path[:-1]:
            if isinstance(cur, dict):
                if key not in cur:
                    cur[key] = {}
                cur = cur[key]
            elif isinstance(cur, list) and isinstance(key, int):
                # This part is for completeness if you ever need to modify lists by index.
                # For now, the logic assumes dicts.
                while len(cur) <= key:
                    cur.append({}) # Or some other default
                cur = cur[key]
            else:
                # Path is invalid for the current structure
                return

        if isinstance(cur, dict) and isinstance(path[-1], str):
            cur[path[-1]] = value
        elif isinstance(cur, list) and isinstance(path[-1], int):
            if len(cur) == path[-1]:
                cur.append(value)
            elif len(cur) > path[-1]:
                cur[path[-1]] = value

    # --- Dash Helpers (Sin cambios) ---
    def dash_ids(self, screen_id, prefix=None):
        base = f"{prefix}__{screen_id}" if prefix else screen_id
        return {"token_store": f"{base}__tok", "auto_interval": f"{base}__int"}

    def dash_refresh_components(self, screen_id, interval_ms=800, max_intervals=1, prefix=None):
        from dash import dcc
        ids = self.dash_ids(screen_id, prefix)
        return [
            dcc.Store(id=ids["token_store"], data=0),
            dcc.Interval(id=ids["auto_interval"], interval=interval_ms, max_intervals=max_intervals)
        ], ids

    def register_dash_refresh_callbacks(self, screen_id, body_output_id, render_body, prefix=None):
        from dash import callback, Input, Output
        ids = self.dash_ids(screen_id, prefix)

        @callback(Output(ids["token_store"], "data"), Input(ids["auto_interval"], "n_intervals"))
        async def _auto(n):
            await self.refresh_screen(screen_id)
            return (n or 0)

        @callback(Output(body_output_id, "children"), Input(ids["token_store"], "data"))
        def _render(_):
            return render_body(self.get_screen(screen_id))
        return ids

data_manager = DataManager()