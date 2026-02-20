from decimal import Decimal
import hashlib
import json
import re
import time
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

from dash import no_update
from flask import session

from dashboard_core.query_builder import SmartQueryBuilder
from dashboard_core.db_helper import execute_dynamic_query
from services.real_data_service import RealDataService
from utils.helpers import format_value
from dash import no_update, html
from components.skeleton import get_skeleton
import asyncio

Json = Union[Dict[str, Any], List[Any]]
PathList = List[Union[str, int]]

@dataclass
class CacheEntry:
    data: Json
    ts: float

class DataManager:
    _instance: Optional["DataManager"] = None
    SCREEN_MAP: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls) -> "DataManager":
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self.base_service = RealDataService()
        self.qb = SmartQueryBuilder()
        self.cache = {}
        self.query_cache = {}
        self.DEFAULT_TTL_SECONDS = 60
        self._load_screen_configs()
    
    def _load_screen_configs(self) -> None:
        try:
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent

            possible_paths = [
                project_root / "configs" / "screens.json",
                project_root / "screens.json",
                Path("configs/screens.json").resolve()
            ]

            config_path = None
            for p in possible_paths:
                if p.exists():
                    config_path = p
                    break
            
            if config_path:
                print(f"✅ Configuración cargada desde: {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.SCREEN_MAP = json.load(f)
                self._validate_and_normalize_configs()
            else:
                print(f"⚠️ NO SE ENCONTRÓ screens.json.")
                self.SCREEN_MAP = self._get_minimal_config()
                
        except Exception as e:
            print(f"❌ Error cargando configuración: {str(e)}")
            self.SCREEN_MAP = self._get_minimal_config()
    
    def _validate_and_normalize_configs(self) -> None:
        for screen_id, config in self.SCREEN_MAP.items(): # type: ignore
            defaults = {
                "section_key": None,
                "section_keys": None,
                "ttl_seconds": self.DEFAULT_TTL_SECONDS,
                "kpi_roadmap": {},
                "chart_roadmap": {},
                "categorical_roadmap": {},
                "table_roadmap": {},
                "inject_paths": {}
            }
            self.SCREEN_MAP[screen_id] = {**defaults, **config} # type: ignore
    
    def _get_minimal_config(self) -> Dict[str, Dict[str, Any]]:
        return {
            "home": {
                "section_keys": ["main", "operational", "workshop", "administration"],
                "ttl_seconds": 30,
                "kpi_roadmap": {},
                "chart_roadmap": {},
                "categorical_roadmap": {},
                "table_roadmap": {},
                "inject_paths": {}
            }
        }
    
    def reload_configs(self) -> None:
        self._load_screen_configs()
        self.cache.clear()
    
    def _db_fingerprint(self) -> str:
        db_config = session.get("current_db")
        if not db_config: 
            return "no-db"
        try:
            raw = json.dumps(db_config, sort_keys=True, default=str).encode("utf-8")
        except:
            raw = str(db_config).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]
    
    def _normalize_filters(self, filters: Optional[Dict]) -> Dict:
        if not filters:
            return {}
        ignore_values = ["Todas", "Todos", "All", "Todo", None, ""]
        return {k: v for k, v in filters.items() if v not in ignore_values}
    
    def _cache_key(self, screen_id: str, filters: Optional[Dict] = None) -> str:
        normalized = self._normalize_filters(filters)
        f_str = json.dumps(normalized, sort_keys=True, default=str) if normalized else "no_filters"
        return f"{self._db_fingerprint()}::{screen_id}::{f_str}"
    
    def _is_fresh(self, entry: CacheEntry, ttl: int) -> bool:
        return (time.time() - entry.ts) <= ttl
    
    def _clean_val(self, v: Any) -> float:
        if v is None:
            return 0.0
        if isinstance(v, Decimal):
            v = float(v)
        if isinstance(v, str):
            clean = v.replace('%', '').replace('+', '').replace(',', '').replace('$', '').strip()
            try:
                v = float(clean)
            except ValueError:
                return 0.0
        if isinstance(v, (float, int)):
            if math.isnan(v) or math.isinf(v):
                return 0.0
            return float(v)
        return 0.0
    
    def _safe_divide(self, numerator: float, denominator: float) -> float:
        num = self._clean_val(numerator)
        den = self._clean_val(denominator)
        if den == 0:
            return 0.0
        result = num / den
        if math.isnan(result) or math.isinf(result):
            return 0.0
        return result
    
    def _format_val(self, v: Any, fmt: str) -> str:
        try:
            val = self._clean_val(v)
            if val == 0 and v is None:
                return "---"
            if fmt == "currency":
                return format_value(val, "$")
            if fmt == "percent":
                return f"{val * 100:.1f}%"
            if fmt == "integer":
                return f"{int(val):,}"
            if fmt == "decimal":
                return f"{val:,.2f}"
            return f"{val:,.2f}"
        except Exception:
            return "---"
    
    def _format_delta(self, delta: float, has_base: bool = True) -> str:
        try:
            val = self._clean_val(delta)
            if not has_base:
                return "N/A"
            return f"{val * 100:+.1f}%"
        except Exception:
            return "N/A"

    def _sql_cache_key(self, sql: str) -> str:
        # Incluye fingerprint de la BD para evitar mezclar resultados entre conexiones
        digest = hashlib.sha256(sql.encode("utf-8")).hexdigest()
        return f"{self._db_fingerprint()}::sql::{digest}"

    def _prune_query_cache(self) -> None:
        # Limpieza simple para evitar crecimiento infinito
        if len(self.query_cache) <= 500:
            return
        now = time.time()
        stale_keys = [k for k, e in self.query_cache.items() if (now - e.ts) > (self.DEFAULT_TTL_SECONDS * 4)]
        for k in stale_keys[:300]:
            self.query_cache.pop(k, None)

    async def _execute_query_cached(self, db_config: Any, sql: str, ttl: int) -> Any:
        key = self._sql_cache_key(sql)

        entry = self.query_cache.get(key)
        if entry and self._is_fresh(entry, ttl):
            return entry.data  # rows cacheados

        rows = await execute_dynamic_query(db_config, sql)
        # Guarda incluso [] para evitar repetir hits en queries que “no traen nada”
        self.query_cache[key] = CacheEntry(data=rows, ts=time.time())

        self._prune_query_cache()
        return rows

    def get_screen(
        self,
        screen_id: str,
        *,
        use_cache: bool = True,
        allow_stale: bool = True,
        force_base: bool = False,
        filters: Optional[Dict] = None
    ) -> Json:
        cfg = self.SCREEN_MAP.get(screen_id) if self.SCREEN_MAP else None
        if not cfg: 
            return {}
        
        ttl = int(cfg.get("ttl_seconds") or self.DEFAULT_TTL_SECONDS)
        key = self._cache_key(screen_id, filters)
        
        if not force_base and use_cache and key in self.cache:
            entry = self.cache[key]
            if allow_stale or self._is_fresh(entry, ttl):
                return entry.data
        
        base = self.base_service.get_full_dashboard_data()
        keys = cfg.get("section_keys") or [cfg.get("section_key")]
        sliced = {k: base.get(k, {}) for k in keys if k}
        
        if use_cache:
            self.cache[key] = CacheEntry(data=sliced, ts=time.time())
        
        return sliced

    def _safe_eval_formula(self, formula: str, row_dict: Dict[str, Any]) -> float:
        try:
            safe_dict = {k: self._clean_val(v) for k, v in row_dict.items()}
            result = eval(formula, {"__builtins__": {}}, safe_dict)
            return self._clean_val(result)
        except Exception:
            return 0.0

    async def refresh_screen(self, screen_id: str, filters: Optional[Dict] = None, *, use_cache: bool = True, db_config: Any = None) -> Json:
        cfg = self.SCREEN_MAP.get(screen_id) if self.SCREEN_MAP else {}
        if not cfg:
            return {}
        
        cache_key = self._cache_key(screen_id, filters)
        
        if use_cache and cache_key in self.cache:
            entry = self.cache[cache_key]
            if self._is_fresh(entry, int(cfg.get("ttl_seconds") or 30)):
                return entry.data
        

        base = self.base_service.get_full_dashboard_data()
        keys = cfg.get("section_keys") or [cfg.get("section_key")]
        data = {k: base.get(k, {}) for k in keys if k}
        
        if not db_config:
            db_config = session.get("current_db")
            
        if not db_config:
            if use_cache:
                self.cache[cache_key] = CacheEntry(data=data, ts=time.time())
            return data
        
        inject_paths = cfg.get("inject_paths", {})
        
        kpi_roadmap = cfg.get("kpi_roadmap", {})
        
        for group_key, spec in kpi_roadmap.items():

            if not isinstance(spec, dict):
                print(f"⚠️ DataManager: spec para '{group_key}' no es dict (tipo: {type(spec).__name__}), skipping...")
                continue
            
            dims = spec.get("dimensions", [])
            raw_metrics = spec.get("metrics", [])
            

            metric_batches = []
            if raw_metrics and isinstance(raw_metrics[0], list):
                metric_batches = raw_metrics
            else:
                metric_batches = [raw_metrics] if raw_metrics else []
            
            fixed_filters_raw = spec.get("fixed_filters", {})
            fixed_filters_per_batch = isinstance(fixed_filters_raw, list)

            row_context = {}


            for batch_idx, batch in enumerate(metric_batches):
                if not batch: continue
                combined_filters = (filters or {}).copy()
                if fixed_filters_per_batch:
                    if batch_idx < len(fixed_filters_raw):
                        ff = fixed_filters_raw[batch_idx]
                        if isinstance(ff, dict):
                            combined_filters.update(ff)
                        elif isinstance(ff, list):
                            for f in ff:
                                if isinstance(f, dict):
                                    combined_filters.update(f)
                elif isinstance(fixed_filters_raw, dict):
                    combined_filters.update(fixed_filters_raw)
                try:
                    build = self.qb.get_dataframe_query(batch, dims, filters=combined_filters)
                    if build and "query" in build:
                        #print(f"🔍 Query de KPI {group_key}->{batch}: {build['query']}")
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: return data
                        if rows is None or (not rows and db_config):
                            print(f"🛑 Abortando carga de {screen_id}: BD no disponible o error crítico.")
                            break
                        if rows:

                            for k, v in rows[0].items():
                                row_context[k] = self._clean_val(v)
                except Exception:
                    pass


            for col_def in spec.get("columns", []):
                target_key = col_def.get("target")

                path = inject_paths.get(f"{group_key}.{target_key}") or inject_paths.get(target_key)

                if not path: continue

                val = 0.0
                

                if "formula" in col_def:
                    f_str = col_def["formula"]
                    try:
                        if "lambda" in f_str:

                            calc_func = eval(f_str, {"__builtins__": {}})
                            val = calc_func(row_context)
                        else:
                            val = eval(f_str, {"__builtins__": {}}, row_context)
                    except Exception:
                        val = 0.0

                else:
                    data_key = col_def.get("key")
                    val = row_context.get(data_key, 0.0)


                clean_val = self._clean_val(val)
                self._set_path(data, path, clean_val)

                if path and len(path) > 1:
                    leaf = path[-1]
                    parent_path = path[:-1]
                    kpi_key = path[-2] if len(path) >= 2 else ""

                    is_count_kpi = kpi_key in ("total_trips", "total_kilometers", "units_used", "customers_served", "real_kilometers")

                    is_decimal_kpi = kpi_key in ("real_yield", "liters_consumed", "avg_collection_days", "average_payment_days")
                    is_percent_kpi = kpi_key == "availability_percent"
                    fmt = "integer" if is_count_kpi else ("percent" if is_percent_kpi else ("decimal" if is_decimal_kpi else "currency"))
                    if leaf == "value" or leaf == "current_value":
                        self._set_path(data, parent_path + ["value_formatted"], self._format_val(clean_val, fmt))
                    elif leaf == "target":
                        self._set_path(data, parent_path + ["target_formatted"], self._format_val(clean_val, fmt))

                    if kpi_key in ("avg_collection_days", "average_payment_days"):
                        self._set_path(data, parent_path + ["vs_last_year_formatted"], "none")
                        self._set_path(data, parent_path + ["label_prev_year"], "Vs 2025")
                    elif kpi_key == "availability_percent":
                        self._set_path(data, parent_path + ["vs_last_year_formatted"], None)
                        self._set_path(data, parent_path + ["vs_last_year_delta"], None)
                        self._set_path(data, parent_path + ["vs_last_year_delta_formatted"], None)
                    elif leaf == "vs_last_year_value":
                        self._set_path(data, parent_path + ["vs_last_year_formatted"], self._format_val(clean_val, fmt))
                    elif leaf == "ytd_value":
                        self._set_path(data, parent_path + ["ytd_formatted"], self._format_val(clean_val, fmt))
                    elif leaf in ("trips_meta", "trips_previous", "trips_ytd", "kms_meta", "kms_anterior", "kms_ytd", "kms_valor"):
                        fmt_leaf = "integer" if "trips" in leaf or "kms" in leaf else "currency"
                        self._set_path(data, parent_path + [leaf + "_formatted"], self._format_val(clean_val, fmt_leaf))
                    elif "delta" in leaf or "variance" in leaf:
                        self._set_path(data, parent_path + [leaf + "_formatted"], self._format_delta(clean_val))




        chart_roadmap = cfg.get("chart_roadmap", {})
        for chart_key, spec in chart_roadmap.items():
            path = inject_paths.get(chart_key)
            if not path: continue


            if not isinstance(spec, dict):
                print(f"⚠️ DataManager: spec para chart '{chart_key}' no es dict (tipo: {type(spec).__name__}), skipping...")
                continue

            fixed_filters_raw = spec.get("fixed_filters", {})
            fixed_filters_per_batch = isinstance(fixed_filters_raw, list)

            chart_batches = []
            if "metrics" in spec: 
                raw_c = spec["metrics"]
                chart_batches = raw_c if (raw_c and isinstance(raw_c[0], list)) else [raw_c]
                series_defs = spec.get("columns", [])
            else:
                chart_batches = [list(spec.values())]
                series_defs = [{"key": v, "series": k} for k, v in spec.items()]

            temp_results = {i: {} for i in range(1, 13)}
            for batch_idx, batch in enumerate(chart_batches):
                try:
                    combined_filters = (filters or {}).copy()
                    if fixed_filters_per_batch:
                        if batch_idx < len(fixed_filters_raw):
                            ff = fixed_filters_raw[batch_idx]
                            if isinstance(ff, dict):
                                combined_filters.update(ff)
                    elif isinstance(fixed_filters_raw, dict):
                        combined_filters.update(fixed_filters_raw)
                    
                    build = self.qb.get_dataframe_query(batch, ["__month__"], filters=combined_filters)
                    if build and "query" in build:
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: return data
                        if rows:
                            for r in rows:

                                p_val = r.get('__month__') or r.get('month') or r.get('period')
                                try:
                                    if p_val is None:
                                        p_int = 0
                                    else:
                                        p_int = int(p_val)
                                except Exception:
                                    p_int = 0
                                
                                if 1 <= p_int <= 12:
                                    for k, v in r.items():
                                        if k not in ["period", "month", "__month__"]:
                                            temp_results[p_int][k] = self._clean_val(v)
                except Exception: pass

            chart_data = {"months": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"], "series": []}
            has_valid = False
            for s_def in series_defs:
                key = s_def.get("key")
                s_name = s_def.get("series", "Serie")
                formula_str = s_def.get("formula")
                if formula_str:
                    try:
                        calc_func = eval(formula_str, {"__builtins__": {}}) if "lambda" in formula_str else None
                        vals = []
                        for m in range(1, 13):
                            row = temp_results.get(m, {})
                            try:
                                v = calc_func(row) if calc_func else 0.0
                            except Exception:
                                v = 0.0
                            vals.append(self._clean_val(v))
                    except Exception:
                        vals = [0.0] * 12
                else:
                    vals = [temp_results[m].get(key, 0.0) for m in range(1, 13)]
                if any(v != 0 for v in vals): has_valid = True
                serie_entry = {"name": s_name.capitalize(), "data": vals}
                if "type" in s_def:
                    serie_entry["type"] = s_def["type"]
                chart_data["series"].append(serie_entry)
            
            if has_valid: 

                target_path = path + ["data"]
                self._set_path(data, target_path, chart_data)

        for chart_key, spec in cfg.get("categorical_roadmap", {}).items():
            path = inject_paths.get(chart_key)
            if not path: continue
            

            if not isinstance(spec, dict):
                print(f"⚠️ DataManager: spec para categorical '{chart_key}' no es dict (tipo: {type(spec).__name__}), skipping...")
                continue

            try:
                combined_filters = (filters or {}).copy()
                ff = spec.get("fixed_filters", {})
                if isinstance(ff, dict):
                    combined_filters.update(ff)
                
                dims = [spec.get("dimension")] if isinstance(spec.get("dimension"), str) else spec.get("dimensions", [])
                raw_mets = spec.get("metrics", [])

                mets = raw_mets[0] if raw_mets and isinstance(raw_mets[0], list) else (raw_mets if isinstance(raw_mets, list) else [spec.get("kpi")] if spec.get("kpi") else [])

                chart_data = {"labels": [], "values": [], "categories": [], "series": [{"name": "Valor", "data": []}]}
                has_data = False

                if spec.get("columns"):

                    label_col = next((c for c in spec["columns"] if c.get("role") == "label"), None)
                    value_col = next((c for c in spec["columns"] if c.get("role") == "value"), None)
                    label_key = label_col.get("key") if label_col else None
                    series_name = (value_col.get("series") or "Valor") if value_col else "Valor"
                    formula_str = value_col.get("formula") if value_col else None
                    value_key = value_col.get("key") if value_col else None
                    calc_func = eval(formula_str, {"__builtins__": {}}) if formula_str and "lambda" in formula_str else None

                    if not mets or not dims:
                        pass
                    else:
                        build = self.qb.get_dataframe_query(mets, dims, filters=combined_filters)
                        if build and "query" in build:
                            rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                            if not rows and db_config: return data
                            if rows:
                                has_data = True
                                for r in rows[:15]:
                                    lbl = str(r.get(label_key, "N/A")) if label_key else "N/A"
                                    if calc_func:
                                        try:
                                            val = self._clean_val(calc_func(r))
                                        except Exception:
                                            val = 0.0
                                    else:
                                        val = self._clean_val(r.get(value_key, 0))
                                    chart_data["labels"].append(lbl)
                                    chart_data["values"].append(val)
                                    chart_data["categories"].append(lbl)
                                    chart_data["series"][0]["name"] = series_name
                                    chart_data["series"][0]["data"].append(val)

                                sorted_tuples = sorted(
                                    zip(chart_data["values"], chart_data["labels"], chart_data["categories"]),
                                    key=lambda t: -(t[0] if isinstance(t[0], (int, float)) else 0)
                                )
                                chart_data["values"] = [t[0] for t in sorted_tuples]
                                chart_data["labels"] = [t[1] for t in sorted_tuples]
                                chart_data["categories"] = [t[2] for t in sorted_tuples]
                                chart_data["series"][0]["data"] = chart_data["values"]
                else:

                    mets = [spec.get("kpi")] if isinstance(spec.get("kpi"), str) else mets
                    build = self.qb.get_dataframe_query(mets, dims, filters=combined_filters)
                    if build and "query" in build:
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: return data
                        if rows:
                            has_data = True
                            val_key = mets[0] if mets else "value"
                            rows.sort(key=lambda x: self._clean_val(x.get(val_key, 0)), reverse=True)
                            for r in rows[:15]:
                                lbl = "N/A"
                                for k in r.keys():
                                    if k not in (mets if isinstance(mets[0], str) else []):
                                        lbl = str(r[k])
                                        break
                                val = self._clean_val(r.get(val_key, 0))
                                chart_data["labels"].append(lbl)
                                chart_data["values"].append(val)
                                chart_data["categories"].append(lbl)
                                chart_data["series"][0]["data"].append(val)

                if has_data:
                    self._set_path(data, path, {"data": chart_data})
            except Exception:
                pass


        for table_key, spec in cfg.get("table_roadmap", {}).items():
            path = inject_paths.get(table_key)
            if not path: continue


            if not isinstance(spec, dict):
                print(f"⚠️ DataManager: spec para table '{table_key}' no es dict (tipo: {type(spec).__name__}), skipping...")
                continue

            dims = spec.get("dimensions", [])
            raw_mets = spec.get("metrics", [])

            mets = raw_mets[0] if raw_mets and isinstance(raw_mets[0], list) else (raw_mets if isinstance(raw_mets, list) else [])
            combined_filters = (filters or {}).copy()
            combined_filters.update(spec.get("fixed_filters", {}))


            metrics_by_fact = {}
            for m_key in mets:
                m_def = self.qb.metrics.get(m_key)
                if not m_def or m_def.get("type") == "derived": continue
                tbl = m_def.get("recipe", {}).get("table")
                if tbl: metrics_by_fact.setdefault(tbl, []).append(m_key)

            results_map = {}
            has_data = False
            
            for fact_tbl, grp_mets in metrics_by_fact.items():
                try:
                    build = self.qb.get_dataframe_query(grp_mets, dims, filters=combined_filters)
                    if build and "query" in build:
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: return data
                        if rows:
                            has_data = True
                            for r in rows:

                                rk = tuple(r.get(d) for d in dims) if len(dims) > 1 else list(r.values())[0]
                                results_map.setdefault(rk, {}).update(r)
                except Exception:
                    pass

            if not has_data: continue


            col_totals = {}
            temp_rows = []
            
            for row in results_map.values():

                for m in mets:
                    val = self._clean_val(row.get(m))
                    row[m] = val
                    if isinstance(val, (int, float)):
                        col_totals[m] = col_totals.get(m, 0) + val
                

                for col in spec.get("columns", []):
                    if "formula" in col:
                        f_str = col["formula"]
                        col_key = col.get("key") or (col.get("label") or "").strip().replace(" ", "_").replace(".", "_").lower() or ""
                        if not col_key:
                            continue
                        try:

                            raw_val = None
                            if "lambda" in f_str:
                                calc_func = eval(f_str, {"__builtins__": {}})
                                raw_val = calc_func(row)
                            else:
                                raw_val = eval(f_str, {"__builtins__": {}}, row)


                            

                            if col.get("format") == "text":
                                row[col_key] = str(raw_val) if raw_val is not None else ""
                            

                            elif isinstance(raw_val, str):
                                try:
                                    clean_test = raw_val.replace('%', '').replace('+', '').replace(',', '').replace('$', '').strip()
                                    if not clean_test: raise ValueError()
                                    float(clean_test)

                                    row[col_key] = self._clean_val(raw_val)
                                except ValueError:

                                    row[col_key] = raw_val
                            

                            else:
                                row[col_key] = self._clean_val(raw_val)

                        except Exception:
                            row[col_key] = "" if col.get("format") == "text" else 0.0

                temp_rows.append(row)


            for row in temp_rows:
                for col in spec.get("columns", []):
                    if "formula" in col:
                        col_key = col.get("key") or (col.get("label") or "").strip().replace(" ", "_").replace(".", "_").lower() or ""
                        if col_key:
                            v = row.get(col_key)
                            if isinstance(v, (int, float)):
                                col_totals[col_key] = col_totals.get(col_key, 0) + v


            headers = [c.get("label", "") for c in spec.get("columns", [])]
            final_rows = []

            for idx, row in enumerate(temp_rows):
                disp = []
                for col in spec.get("columns", []):
                    if col.get("role") == "row_number":
                        disp.append(str(idx + 1))
                        continue
                    ck = col.get("key") or (col.get("label") or "").strip().replace(" ", "_").replace(".", "_").lower() or ""
                    val = row.get(ck)
                    

                    if col.get("is_total_ratio"):
                        nk = col.get("numerator_key", ck)
                        val = self._safe_divide(row.get(nk, 0), col_totals.get(nk, 0))
                    

                    f = col.get("format")
                    if f == "currency": disp.append(self._format_val(val, "currency"))
                    elif f == "percent": disp.append(f"{self._clean_val(val):.2%}")
                    elif f == "integer": disp.append(f"{int(self._clean_val(val)):,}")
                    else: disp.append(str(val) if val is not None else "")
                
                final_rows.append(disp)
                
            self._set_path(data, path, {"headers": headers, "rows": final_rows})

        if use_cache:
            self.cache[cache_key] = CacheEntry(data=data, ts=time.time())
        
        return data

    def _set_path(self, data: Dict, path: PathList, value: Any) -> None:
        try:
            cur = data
            for k in path[:-1]:
                if isinstance(cur, dict):
                    cur = cur.setdefault(k, {})
                elif isinstance(cur, list) and isinstance(k, int):
                    while len(cur) <= k:
                        cur.append({})
                    cur = cur[k]
                else:
                    return
            if path:
                cur[path[-1]] = value
        except Exception:
            pass

    def dash_ids(self, screen_id, prefix=None):
        base = f"{prefix}__{screen_id}" if prefix else screen_id
        return {
            "token_store": f"{base}__tok",
            "auto_interval": f"{base}__int",
            "kpi_store": f"{base}__kpi_st",
            "chart_store": f"{base}__cha_st",
            "table_store": f"{base}__tab_st",
            "body": f"{base}__body"
        }
    

    def dash_refresh_components(self, screen_id, interval_ms=800, max_intervals=1, prefix=None):
        from dash import dcc
        ids = self.dash_ids(screen_id, prefix)
        return [
            dcc.Store(id=ids["kpi_store"], data=0),
            dcc.Store(id=ids["chart_store"], data=0),
            dcc.Store(id=ids["table_store"], data=0),
            dcc.Store(id=ids["token_store"], data=0),
            dcc.Interval(id=ids["auto_interval"], interval=interval_ms, max_intervals=max_intervals)
        ], ids

    def register_dash_refresh_callbacks(self, *, screen_id: str, body_output_id: str, render_body: Callable[[Json], Any], prefix: Optional[str] = None, filter_ids: Optional[List[str]] = None) -> Dict[str, str]:
        from dash import callback, Input, Output
        ids = self.dash_ids(screen_id, prefix=prefix)
        inputs = [
            Input(ids["auto_interval"], "n_intervals"),
            Input("selected-db-store", "data")
        ]
    
        if filter_ids:
            inputs.extend([Input(fid, "value") for fid in filter_ids])

        _MONTH_NAMES = (
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        )

        @callback(Output(ids["token_store"], "data"), inputs, prevent_initial_call=False)
        async def _auto_refresh(n_intervals, selected_db, *filter_values):
            filters = {}
            if filter_ids:
                for i, fid in enumerate(filter_ids):
                    if i >= len(filter_values):
                        break
                    val = filter_values[i]
                    key = fid.split("-")[-1] if "-" in fid else fid
                    key = key.replace("__", ".")
                    if key == "year":
                        filters["year"] = val if val else str(datetime.now().year)
                    elif key == "month":
                        filters["month"] = val if val else _MONTH_NAMES[datetime.now().month - 1]
                    elif val:
                        filters[key] = val
                # Garantizar año y mes cuando la pantalla los usa (por si los componentes no devolvieron valor)
                if any(f == "year" or f.endswith("-year") for f in filter_ids) and "year" not in filters:
                    filters["year"] = str(datetime.now().year)
                if any(f == "month" or f.endswith("-month") for f in filter_ids) and "month" not in filters:
                    filters["month"] = _MONTH_NAMES[datetime.now().month - 1]
            await self.refresh_screen(screen_id, filters=filters, use_cache=True, db_config=selected_db)
            return json.dumps(filters)

        @callback(Output(body_output_id, "children"), Input(ids["token_store"], "data"))
        def _rerender(token_data):
        
            if token_data is None or token_data == 0:
                return get_skeleton(screen_id)
            current_filters = {}
            try:
                if isinstance(token_data, str):
                    current_filters = json.loads(token_data)
                elif isinstance(token_data, dict):
                    current_filters = token_data
            except:
                return get_skeleton(screen_id)

            screen_data = self.get_screen(
                screen_id,
                use_cache=True,
                allow_stale=True,
                filters=current_filters
            )

            content = render_body(screen_data)
        
            return html.Div(content, className="page-content-loaded")


        return ids

data_manager = DataManager()