import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from flask import session

from dashboard_core.query_builder import SmartQueryBuilder
from dashboard_core.db_helper import execute_dynamic_query
from services.real_data_service import RealDataService
from services.pbi_mapper import PBI_MAPPING

Json = Union[Dict[str, Any], List[Any]]
Path = List[Union[str, int]]

@dataclass
class CacheEntry:
    data: Json
    ts: float

class DataManager:
    _instance: Optional["DataManager"] = None
    base_service: RealDataService
    qb: SmartQueryBuilder
    cache: Dict[str, CacheEntry]
    DEFAULT_TTL_SECONDS: int
    SCREEN_MAP: Dict[str, Dict[str, Any]]
    USE_MOCK_DATA = False

    def __new__(cls) -> "DataManager":
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.base_service = RealDataService()
            cls._instance.qb = SmartQueryBuilder()
            cls._instance.cache = {}
            cls._instance.DEFAULT_TTL_SECONDS = 30

            cls._instance.SCREEN_MAP = {
                "admin-banks": {
                    "section_key": "financial",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "admin-collection": {
                    "section_key": "financial",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "admin-payables": {
                    "section_key": "financial",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "home": {
                    "section_keys": ["operational", "maintenance", "financial"],
                    "ttl_seconds": 30,
                    "kpi_roadmap": {
                        "viajes_val": "viajes"
                    },
                    "inject_paths": {
                        "viajes_val": [
                            "operational", "dashboard", "kpis", "total_trips", "value"
                        ]
                    }
                },
                "ops-costs": {
                    "section_key": "operational",
                    "ttl_seconds": 60,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-dashboard": {
                    "section_keys": ["operational", "maintenance", "financial"],
                    "ttl_seconds": 60,
                    "kpi_roadmap": {
                        "ingreso_valor": "ingreso_viaje",
                        "ingreso_meta": "meta_ingreso_viaje",
                        "ingreso_delta": "pct_desviacion_ingreso_vs_anterior",
                        "ingreso_ytd": "ingreso_viaje_acumulado",
                        "ingreso_ytd_delta": "pct_desviacion_ingreso_acumulado",
                        "viajes_val": "viajes",
                        "viajes_valor": "viajes",
                        "viajes_meta": "meta_viajes",
                        "viajes_delta": "pct_desviacion_viajes_vs_anterior",
                        "viajes_ytd": "viajes_acumulado",
                        "viajes_ytd_delta": "pct_desviacion_viajes_acumulado",
                        "kms_valor": "kilometros",
                        "kms_meta": "meta_kilometros",
                        "kms_delta": "pct_desviacion_kilometros_vs_anterior",
                        "kms_ytd": "kilometros_acumulado",
                        "kms_ytd_delta": "pct_desviacion_kilometros_acumulado"
                    },
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
                    "inject_paths": {
                        "ingreso_valor": ["operational", "dashboard", "kpis", "trip_revenue", "value"],
                        "ingreso_meta": ["operational", "dashboard", "kpis", "trip_revenue", "target"],
                        "ingreso_delta": ["operational", "dashboard", "kpis", "trip_revenue", "delta"],
                        "ingreso_ytd": ["operational", "dashboard", "kpis", "trip_revenue", "ytd"],
                        "ingreso_ytd_delta": ["operational", "dashboard", "kpis", "trip_revenue", "ytd_delta"],
                        "viajes_val": ["operational", "dashboard", "kpis", "total_trips", "value"],
                        "viajes_valor": ["operational", "dashboard", "kpis", "total_trips", "value"],
                        "viajes_meta": ["operational", "dashboard", "kpis", "total_trips", "target"],
                        "viajes_delta": ["operational", "dashboard", "kpis", "total_trips", "delta"],
                        "viajes_ytd": ["operational", "dashboard", "kpis", "total_trips", "ytd"],
                        "viajes_ytd_delta": ["operational", "dashboard", "kpis", "total_trips", "ytd_delta"],
                        "kms_valor": ["operational", "dashboard", "kpis", "kilometers", "value"],
                        "kms_meta": ["operational", "dashboard", "kpis", "kilometers", "target"],
                        "kms_delta": ["operational", "dashboard", "kpis", "kilometers", "delta"],
                        "kms_ytd": ["operational", "dashboard", "kpis", "kilometers", "ytd"],
                        "kms_ytd_delta": ["operational", "dashboard", "kpis", "kilometers", "ytd_delta"],
                        "ingresos_anual": ["operational", "dashboard", "charts", "ingresos_anual"],
                        "viajes_anual": ["operational", "dashboard", "charts", "viajes_anual"],
                        "mix_operacion": ["operational", "dashboard", "charts", "mix_operacion"],
                        "top_rutas": ["operational", "dashboard", "tables", "rutas_cargado"],
                        "top_areas": ["operational", "dashboard", "charts", "por_area"],
                        "balanceo_unidades": ["operational", "dashboard", "charts", "balanceo_unidades"]
                    },
                },
                "ops-performance": {
                    "section_key": "operational",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "ops-routes": {
                    "section_key": "operational",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-availability": {
                    "section_key": "maintenance",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-dashboard": {
                    "section_key": "maintenance",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-inventory": {
                    "section_key": "maintenance",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
                "taller-purchases": {
                    "section_key": "maintenance",
                    "ttl_seconds": 30,
                    "kpi_roadmap": {},
                    "inject_paths": {},
                },
            }
        return cls._instance

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

        base = self.base_service.get_full_dashboard_data()
        keys = cfg.get("section_keys") or [cfg.get("section_key")]
        sliced = {k: base.get(k, {}) for k in keys if k}
        
        if use_cache:
            self.cache[key] = CacheEntry(data=sliced, ts=time.time())
        return sliced

    def get_pbi_measure_name(self, section: str, key: str) -> Optional[str]:
        try:
            return PBI_MAPPING.get(section, {}).get('kpis', {}).get(key)
        except Exception:
            return None

    async def _resolve_any_kpi(self, db_config, kpi_id, session_results):
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
            if formula:
                for token in re.findall(r'[a-z_]+', formula):
                    if token in ["if", "else"]: continue
                    sub_val = await self._resolve_any_kpi(db_config, token, session_results)
                    formula = formula.replace(token, str(sub_val))
                try: result = float(eval(formula))
                except: result = 0.0

        session_results[kpi_id] = result
        return result

    def _inject_mock(self, screen_id: str, data: dict) -> dict:
        if screen_id == "home":
            data["operational"]["dashboard"]["kpis"]["total_trips"] = {
                "value": 1280,
                "target": 1500,
                "delta": 0.12,
                "ytd": 8920
            }
    
            data["operational"]["dashboard"]["charts"]["ingresos_anual"] = {
                "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
                "actual": [120, 130, 125, 140, 150, 160],
                "anterior": [110, 120, 118, 130, 135, 145],
                "meta": [140, 140, 140, 140, 140, 140]
            }
    
        if screen_id == "ops-dashboard":
            data["operational"]["dashboard"]["kpis"]["trip_revenue"] = {
                "value": 18_500_000,
                "target": 20_000_000,
                "delta": -0.08,
                "ytd": 92_000_000
            }
    
        if screen_id.startswith("taller"):
            data["maintenance"]["dashboard"]["kpis"]["maintenance_cost"] = {
                "value": 1_250_000,
                "target": 1_100_000,
                "delta": 0.14,
                "ytd": 6_800_000
            }
    
        return data

    async def refresh_screen(self, screen_id: str, *, use_cache=True) -> Json:
        cfg = self.SCREEN_MAP.get(screen_id)
        if not cfg: return {}

        base = self.base_service.get_full_dashboard_data()
        keys = cfg.get("section_keys") or [cfg.get("section_key")]
        data = {k: base.get(k, {}) for k in keys if k}

        db_config = session.get("current_db")
        
        if not db_config:
            if self.USE_MOCK_DATA:
                return self._inject_mock(screen_id, data)
            return data
        
        inject_paths = cfg.get("inject_paths", {})
        session_results = {}

        kpi_roadmap = cfg.get("kpi_roadmap", {})
        for ui_key, kpi_id in kpi_roadmap.items():
            path = inject_paths.get(ui_key)
            if not path: continue

            val = await self._resolve_any_kpi(db_config, kpi_id, session_results)
            self._set_path(data, path, val)

        chart_roadmap = cfg.get("chart_roadmap", {})
        for chart_key, series_map in chart_roadmap.items():
            path = inject_paths.get(chart_key)
            if not path: continue

            chart_data: Dict[str, List[Any]] = {
                "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            }

            for series_name, kpi_id in series_map.items():
                build = self.qb.build_series_query(kpi_id)
                values = [0.0] * 12 
                
                if build and "query" in build:
                    rows = await execute_dynamic_query(db_config, build["query"])
                    if rows:
                        for r in rows:
                            p = r.get('period')
                            v = r.get('value', 0.0)
                            if isinstance(p, int) and 1 <= p <= 12:
                                values[p-1] = v
                
                chart_data[series_name] = values
            
            self._set_path(data, path, chart_data)

        cat_roadmap = cfg.get("categorical_roadmap", {})
        for chart_key, spec in cat_roadmap.items():
            path = inject_paths.get(chart_key)
            if not path: continue
            
            kpi = spec.get("kpi")
            dim = spec.get("dimension")
            
            build = self.qb.build_categorical_query(kpi, dim)
            chart_data = {"labels": [], "values": []}
            
            is_table = "tables" in path 
            table_rows = []

            if build and "query" in build:
                 rows = await execute_dynamic_query(db_config, build["query"])
                 if rows:
                     for r in rows:
                         lbl = r.get("label", "N/A")
                         val = r.get("value")
                         if val is None: val = 0.0
                         
                         if is_table:
                             table_rows.append([lbl, f"${val:,.0f}"]) 
                         else:
                             chart_data["labels"].append(lbl)
                             chart_data["values"].append(val)
            
            if is_table:
                self._set_path(data, path, {
                    "h": ["Concepto", "Valor"], 
                    "r": table_rows
                })
            else:
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
                while len(cur) <= key:
                    cur.append({}) 
                cur = cur[key]
            else:
                return

        if isinstance(cur, dict) and isinstance(path[-1], str):
            cur[path[-1]] = value
        elif isinstance(cur, list) and isinstance(path[-1], int):
            if len(cur) == path[-1]:
                cur.append(value)
            elif len(cur) > path[-1]:
                cur[path[-1]] = value

    def dash_ids(self, screen_id, prefix=None):
        base = f"{prefix}__{screen_id}" if prefix else screen_id
        return {"token_store": f"{base}__tok", "auto_interval": f"{base}__int"}

    def dash_refresh_components(self, screen_id, interval_ms=800, max_intervals=1, prefix=None):
        from dash import dcc
        ids = self.dash_ids(screen_id, prefix)
        return [
            dcc.Store(id=ids["token_store"], data=0),
            dcc.Interval(id=ids["auto_interval"], interval=interval_ms, max_intervals=max_intervals)
        ]

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