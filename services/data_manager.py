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
        self.qb = SmartQueryBuilder()
        self.cache = {}
        self.query_cache = {}
        self._tenant_screen_cache: Dict[str, Dict[str, Any]] = {}
        self.DEFAULT_TTL_SECONDS = 60
        self._screens_base_dir: Optional[Path] = None
        self._load_screen_configs()

    def _get_tenant_key(self, db_config: Any) -> Optional[str]:
        """Obtiene el identificador de tenant (nombre de carpeta) desde session current_db o db_config."""
        if db_config is None:
            return None
        if isinstance(db_config, str):
            return db_config.strip() or None
        if isinstance(db_config, dict):
            return (db_config.get("base_de_datos") or db_config.get("name") or db_config.get("id")) or None
        return str(db_config) or None

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Fusiona override sobre base recursivamente. Listas se reemplazan."""
        out = dict(base)
        for k, v in override.items():
            if k in out and isinstance(out[k], dict) and isinstance(v, dict):
                out[k] = DataManager._deep_merge(out[k], v)
            else:
                out[k] = v
        return out

    def _load_screen_configs(self) -> None:
        try:
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent
            self._screens_base_dir = project_root / "configs" / "screens"

            possible_paths = [
                self._screens_base_dir / "defaults" / "screens.json",
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
                print(f"✅ Configuración de pantallas cargada desde: {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.SCREEN_MAP = json.load(f)
                self._validate_and_normalize_configs()
            else:
                print(f"⚠️ NO SE ENCONTRÓ screens.json.")
                self.SCREEN_MAP = self._get_minimal_config()

        except Exception as e:
            print(f"❌ Error cargando configuración: {str(e)}")
            self.SCREEN_MAP = self._get_minimal_config()

    def get_screen_map(self, tenant_db: Any = None) -> Dict[str, Dict[str, Any]]:
        """
        Devuelve el mapa de pantallas (default o fusionado con tenant).
        Si tenant_db coincide con el nombre de una carpeta bajo configs/screens/, carga
        screens.json de esa carpeta y lo fusiona sobre el default.
        """
        tenant_key = self._get_tenant_key(tenant_db)
        if not tenant_key:
            return self.SCREEN_MAP

        if tenant_key in self._tenant_screen_cache:
            return self._tenant_screen_cache[tenant_key]

        if not self._screens_base_dir:
            return self.SCREEN_MAP

        tenant_path = self._screens_base_dir / tenant_key / "screens.json"
        if not tenant_path.exists():
            self._tenant_screen_cache[tenant_key] = self.SCREEN_MAP
            return self.SCREEN_MAP

        try:
            with open(tenant_path, 'r', encoding='utf-8') as f:
                overlay = json.load(f)
            merged = dict(self.SCREEN_MAP)
            for screen_id, tenant_config in overlay.items():
                if isinstance(tenant_config, dict) and screen_id in merged:
                    merged[screen_id] = self._deep_merge(merged[screen_id], tenant_config)
                else:
                    merged[screen_id] = tenant_config
            for screen_id, config in merged.items():
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
                merged[screen_id] = {**defaults, **config}
            self._tenant_screen_cache[tenant_key] = merged
            return merged
        except Exception as e:
            print(f"⚠️ Error cargando screens tenant '{tenant_key}': {e}")
            self._tenant_screen_cache[tenant_key] = self.SCREEN_MAP
            return self.SCREEN_MAP

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
        self._tenant_screen_cache.clear()
    
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

        #print(f"🔍 SQL:\n{sql.strip()}\n")
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
        filters: Optional[Dict] = None,
        db_name: Optional[str] = None,
    ) -> Json:
        tenant_key = self._get_tenant_key(session.get("current_db"))
        screen_map = self.get_screen_map(tenant_key)
        cfg = screen_map.get(screen_id) if screen_map else None
        if not cfg:
            return {}

        if filters:
            filters = self._translate_filters(screen_id, filters, tenant_db=tenant_key)

        ttl = int(cfg.get("ttl_seconds") or self.DEFAULT_TTL_SECONDS)
        if db_name is not None:
            try:
                raw = json.dumps(db_name, sort_keys=True, default=str).encode("utf-8")
            except Exception:
                raw = str(db_name).encode("utf-8")
            fingerprint = hashlib.sha256(raw).hexdigest()[:16]
            normalized = self._normalize_filters(filters)
            f_str = json.dumps(normalized, sort_keys=True, default=str) if normalized else "no_filters"
            key = f"{fingerprint}::{screen_id}::{f_str}"
        else:
            key = self._cache_key(screen_id, filters)
        
        if not force_base and use_cache and key in self.cache:
            entry = self.cache[key]
            if allow_stale or self._is_fresh(entry, ttl):
                return entry.data

        if allow_stale and use_cache and not force_base:
            normalized = self._normalize_filters(filters)
            f_str = json.dumps(normalized, sort_keys=True, default=str) if normalized else "no_filters"
            suffix = f"::{screen_id}::{f_str}"
            for k, entry in self.cache.items():
                if k.endswith(suffix) and entry.data:
                    return entry.data

        return {}

    def _safe_eval_formula(self, formula: str, row_dict: Dict[str, Any]) -> float:
        try:
            safe_dict = {k: self._clean_val(v) for k, v in row_dict.items()}
            result = eval(formula, {"__builtins__": {}}, safe_dict)
            return self._clean_val(result)
        except Exception:
            return 0.0

    async def refresh_screen(self, screen_id: str, filters: Optional[Dict] = None, *, use_cache: bool = True, db_config: Any = None) -> Json:
        tenant_key = self._get_tenant_key(db_config or session.get("current_db"))
        screen_map = self.get_screen_map(tenant_key)
        cfg = screen_map.get(screen_id) if screen_map else {}
        if not cfg:
            return {}
        if filters:
            filters = self._translate_filters(screen_id, filters, tenant_db=tenant_key)

        cache_key = self._cache_key(screen_id, filters)

        if use_cache and cache_key in self.cache:
            entry = self.cache[cache_key]
            if self._is_fresh(entry, int(cfg.get("ttl_seconds") or 30)):
                return entry.data


        data: Json = {}

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
                    build = self.qb.get_dataframe_query(batch, dims, filters=combined_filters, page_filters=cfg.get("page_filter", []))
                    if build and "query" in build:
                        print(f"🔍 Query de KPI {group_key}->{batch}: {build['query']}")
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: continue
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

                    is_count_kpi = kpi_key in ("total_trips", "total_kilometers", "units_used", "customers_served", "real_kilometers", "workshop_entries", "items_registered", "items_with_stock", "items_without_stock")

                    is_decimal_kpi = kpi_key in ("real_yield", "liters_consumed", "avg_collection_days", "average_payment_days")
                    is_percent_kpi = kpi_key in ("availability_percent", "compliance_level")
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
                chart_batches = [[v for v in spec.values() if isinstance(v, str)]]
                series_defs = [{"key": v, "series": k} for k, v in spec.items() if isinstance(v, str)]

            spec_dims = spec.get("dimensions", ["__month__"])
            is_ym_mode = "__year_month__" in spec_dims
            dim_arg = ["__year_month__"] if is_ym_mode else ["__month__"]
            temp_results: Dict[Any, Any] = {} if is_ym_mode else {i: {} for i in range(1, 13)}

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

                    build = self.qb.get_dataframe_query(batch, dim_arg, filters=combined_filters, page_filters=cfg.get("page_filter", []))
                    if build and "query" in build:
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: continue
                        if rows:
                            for r in rows:
                                if is_ym_mode:
                                    yr = r.get('anio') or r.get('year')
                                    mo = r.get('mes') or r.get('month')
                                    try:
                                        yr_int = int(yr) if yr is not None else 0
                                        mo_int = int(mo) if mo is not None else 0
                                    except Exception:
                                        yr_int, mo_int = 0, 0
                                    if yr_int > 0 and 1 <= mo_int <= 12:
                                        yk = (yr_int, mo_int)
                                        if yk not in temp_results:
                                            temp_results[yk] = {}
                                        for k, v in r.items():
                                            if k not in ("anio", "year", "mes", "month"):
                                                temp_results[yk][k] = self._clean_val(v)
                                else:
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

            _MO_ABBR = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
            if is_ym_mode:
                sorted_yk = sorted(k for k in temp_results.keys() if isinstance(k, tuple))
                categories = [f"{_MO_ABBR[mo-1]} {yr}" for yr, mo in sorted_yk]
                n_periods = len(sorted_yk)
                chart_data = {"months": categories, "series": [], "tooltip_data": [{} for _ in range(n_periods)]}
                has_valid = False
                for s_def in series_defs:
                    if s_def.get("role") == "label":
                        continue
                    key = s_def.get("key")
                    s_name = s_def.get("series", "Serie")
                    formula_str = s_def.get("formula")
                    is_tooltip = s_def.get("role") == "tooltip"
                    if formula_str:
                        try:
                            calc_func = eval(formula_str, {"__builtins__": {}}) if "lambda" in formula_str else None
                            vals = []
                            for yk in sorted_yk:
                                row = temp_results.get(yk, {})
                                try:
                                    v = calc_func(row) if calc_func else 0.0
                                except Exception:
                                    v = 0.0
                                vals.append(self._clean_val(v))
                        except Exception:
                            vals = [0.0] * n_periods
                    else:
                        vals = [temp_results[yk].get(key, 0.0) for yk in sorted_yk]
                    if is_tooltip:
                        for i, v in enumerate(vals):
                            chart_data["tooltip_data"][i][s_name] = v
                    else:
                        if any(v != 0 for v in vals): has_valid = True
                        serie_entry = {"name": s_name.capitalize(), "data": vals}
                        if "type" in s_def:
                            serie_entry["type"] = s_def["type"]
                        chart_data["series"].append(serie_entry)
            else:
                chart_data = {"months": _MO_ABBR, "series": [], "tooltip_data": [{} for _ in range(12)]}
                has_valid = False
                for s_def in series_defs:
                    if s_def.get("role") == "label":
                        continue  # dimension labels are not chart series
                    key = s_def.get("key")
                    s_name = s_def.get("series", "Serie")
                    formula_str = s_def.get("formula")
                    is_tooltip = s_def.get("role") == "tooltip"
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
                    if is_tooltip:
                        for month_idx, v in enumerate(vals):
                            chart_data["tooltip_data"][month_idx][s_name] = v
                    else:
                        if any(v != 0 for v in vals): has_valid = True
                        serie_entry = {"name": s_name.capitalize(), "data": vals}
                        if "type" in s_def:
                            serie_entry["type"] = s_def["type"]
                        chart_data["series"].append(serie_entry)

            if has_valid:
                self._set_path(data, path + ["data"], chart_data)

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

                    label_cols = [c for c in spec["columns"] if c.get("role") == "label"]
                    value_col = next((c for c in spec["columns"] if c.get("role") == "value"), None)
                    if not value_col:
                        value_col = next((c for c in spec["columns"] if c.get("formula") and c.get("role") != "label"), None)
                    label_keys = [c.get("key") for c in label_cols]
                    series_name = (value_col.get("series") or "Valor") if value_col else "Valor"
                    formula_str = value_col.get("formula") if value_col else None
                    value_key = value_col.get("key") if value_col else None
                    calc_func = eval(formula_str, {"__builtins__": {}}) if formula_str and "lambda" in formula_str else None

                    if not dims:
                        pass
                    else:
                        # Multi-batch: when metrics are list-of-lists, group by fact table and
                        # run one query per group, then merge rows by dimension key.
                        # This avoids INNER JOIN blowup when metrics live in different tables.
                        if raw_mets and isinstance(raw_mets[0], list):
                            all_mets = [m for sublist in raw_mets for m in sublist]
                            _mfact = {}
                            for mk in all_mets:
                                m_def = self.qb.metrics.get(mk)
                                if not m_def or m_def.get("type") in ("derived", "placeholder"): continue
                                tbl = m_def.get("recipe", {}).get("table")
                                if tbl: _mfact.setdefault(tbl, []).append(mk)
                            _rmap = {}
                            for _grp in _mfact.values():
                                _gb = self.qb.get_dataframe_query(_grp, dims, filters=combined_filters, page_filters=cfg.get("page_filter", []))
                                if _gb and "query" in _gb:
                                    _gr = await self._execute_query_cached(db_config, _gb["query"], self.DEFAULT_TTL_SECONDS)
                                    if _gr:
                                        for r in _gr:
                                            _rk = tuple(str(r.get(d, "")) for d in dims)
                                            _rmap.setdefault(_rk, {}).update(r)
                            rows = list(_rmap.values()) if _rmap else []
                        else:
                            if not mets: rows = []
                            else:
                                build = self.qb.get_dataframe_query(mets, dims, filters=combined_filters, page_filters=cfg.get("page_filter", []))
                                rows = []
                                if build and "query" in build:
                                    rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS) or []

                        if not rows and db_config: continue
                        if rows:
                            has_data = True
                            computed_rows = []
                            for r in rows:
                                if calc_func:
                                    try:
                                        val = self._clean_val(calc_func(r))
                                    except Exception:
                                        val = 0.0
                                else:
                                    val = self._clean_val(r.get(value_key, 0))
                                computed_rows.append((r, val))

                            if len(label_keys) > 1:
                                levels = []
                                for level_idx, lk in enumerate(label_keys):
                                    dim_name = lk.split(".")[-1].replace("_", " ").capitalize() if "." in lk else lk.capitalize()
                                    agg = {}
                                    for r, val in computed_rows:
                                        key_parts = tuple(str(r.get(k, "")) for k in label_keys[:level_idx + 1])
                                        agg[key_parts] = agg.get(key_parts, 0.0) + val
                                    sorted_items = sorted(agg.items(), key=lambda x: -x[1])[:15]
                                    level_cats = [parts[-1] for parts, _ in sorted_items]
                                    level_vals = [v for _, v in sorted_items]
                                    levels.append({"name": dim_name, "categories": level_cats, "values": level_vals, "series": [{"name": series_name, "data": level_vals}]})
                                first = levels[0] if levels else {"categories": [], "values": [], "series": [{"name": series_name, "data": []}]}
                                chart_data = {
                                    "levels": levels,
                                    "labels": first["categories"],
                                    "values": first["values"],
                                    "categories": first["categories"],
                                    "series": first["series"],
                                }
                            else:
                                label_key = label_keys[0] if label_keys else None
                                for r, val in computed_rows:
                                    lbl = str(r.get(label_key, "N/A")) if label_key else "N/A"
                                    chart_data["labels"].append(lbl)
                                    chart_data["values"].append(val)
                                    chart_data["categories"].append(lbl)
                                    chart_data["series"][0]["name"] = series_name
                                    chart_data["series"][0]["data"].append(val)
                                sorted_tuples = sorted(
                                    zip(chart_data["values"], chart_data["labels"], chart_data["categories"]),
                                    key=lambda t: -(t[0] if isinstance(t[0], (int, float)) else 0)
                                )[:15]
                                chart_data["values"] = [t[0] for t in sorted_tuples]
                                chart_data["labels"] = [t[1] for t in sorted_tuples]
                                chart_data["categories"] = [t[2] for t in sorted_tuples]
                                chart_data["series"][0]["data"] = chart_data["values"]
                                # Extra series for combo charts (bar + line, etc.)
                                extra_cols = [c for c in spec.get("columns", [])
                                              if c.get("role") != "label" and c is not value_col
                                              and (c.get("formula") or c.get("key"))
                                              and c.get("key") not in label_keys]
                                if extra_cols:
                                    for ec in extra_cols:
                                        ec_formula = ec.get("formula")
                                        ec_key = ec.get("key")
                                        ec_name = ec.get("series") or ec.get("key", "Serie")
                                        ec_type = ec.get("type", "bar")
                                        ec_calc = eval(ec_formula, {"__builtins__": {}}) if ec_formula and "lambda" in ec_formula else None
                                        ec_by_lbl = {}
                                        for r, _ in computed_rows:
                                            lbl = str(r.get(label_key, "N/A")) if label_key else "N/A"
                                            if ec_calc:
                                                try:
                                                    v = self._clean_val(ec_calc(r))
                                                except Exception:
                                                    v = 0.0
                                            else:
                                                v = self._clean_val(r.get(ec_key, 0))
                                            ec_by_lbl[lbl] = ec_by_lbl.get(lbl, 0.0) + v
                                        ec_data = [ec_by_lbl.get(lbl, 0.0) for lbl in chart_data["categories"]]
                                        if any(v != 0 for v in ec_data):
                                            chart_data["series"].append({"name": ec_name, "data": ec_data, "type": ec_type})
                else:

                    mets = [spec.get("kpi")] if isinstance(spec.get("kpi"), str) else mets
                    build = self.qb.get_dataframe_query(mets, dims, filters=combined_filters, page_filters=cfg.get("page_filter", []))
                    if build and "query" in build:
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: continue
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

            if raw_mets and isinstance(raw_mets[0], list):
                mets = [m for batch in raw_mets for m in batch]
            else:
                mets = raw_mets if isinstance(raw_mets, list) else []
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
                    build = self.qb.get_dataframe_query(grp_mets, dims, filters=combined_filters, page_filters=cfg.get("page_filter", []))
                    if build and "query" in build:
                        rows = await self._execute_query_cached(db_config, build["query"], self.DEFAULT_TTL_SECONDS)
                        if not rows and db_config: continue
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

    def _translate_filters(self, screen_id: str, filters: Dict, tenant_db: Any = None) -> Dict:
        screen_map = self.get_screen_map(tenant_db or session.get("current_db"))
        screen = screen_map.get(screen_id, {})
        filter_specs: Dict = screen.get("filters", {})
        if not filter_specs:
            return filters

        translated: Dict = {}
        for k, v in filters.items():
            if k in ("year", "month") or "." in k:
                translated[k] = v
                continue
            spec = filter_specs.get(k)
            if not spec:
                # Unknown key — pass as-is so QB qualifies it with fact table
                translated[k] = v
                continue
            # Determine the actual WHERE column
            where_col: Optional[str] = spec.get("where_column")
            if not where_col:
                cols = spec.get("columns", [])
                # For concat filters use the last column (most specific);
                # for single-column filters use the only column.
                where_col = cols[-1] if cols else None
            if where_col:
                translated[where_col] = v
            else:
                translated[k] = v
        return translated

    def register_filter_options_callback(
        self,
        screen_id: str,
        year_id: str,
        month_id: str,
        filter_ids: List[str],
        skip_ids: Optional[List[str]] = None,
    ) -> None:
        from dash import callback, Input, Output, State

        _skip = set(skip_ids or [])
        populatable = [fid for fid in filter_ids if fid not in _skip]
        if not populatable:
            return

        _MONTH_NAMES_LOCAL = (
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        )

        @callback(
            [Output(fid, "data") for fid in populatable],
            Input(year_id, "value"),
            Input(month_id, "value"),
            State("selected-db-store", "data"),
        )
        async def _populate_filter_dropdowns(year_val, month_val, selected_db):
            base_filters = {
                "year": year_val or str(datetime.now().year),
                "month": month_val or _MONTH_NAMES_LOCAL[datetime.now().month - 1],
            }
            try:
                all_opts = await self.get_all_filter_options(
                    screen_id=screen_id,
                    base_filters=base_filters,
                    db_config=selected_db,
                )
            except Exception as exc:
                print(f"⚠️ register_filter_options_callback [{screen_id}]: {exc}")
                all_opts = {}

            results = []
            for fid in populatable:
                parts = fid.split("-")
                key = "-".join(parts[1:]) if len(parts) > 1 else fid

                options: List[Dict] = all_opts.get(key, [])
                blank_label = "Todos" if key in ("cliente", "operador") else "Todas"
                data = [{"label": blank_label, "value": blank_label}] + options

                results.append(data)

            return results

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

    def register_dash_refresh_callbacks(
        self,
        *,
        screen_id: str,
        body_output_id: str,
        render_body: Callable[[Json], Any],
        prefix: Optional[str] = None,
        filter_ids: Optional[List[str]] = None,
        global_token_output_id: Optional[str] = None,
        manual_filter_ids: Optional[List[str]] = None,
        apply_trigger_id: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        filter_ids        → Inputs: cualquier cambio dispara el refresh (ej. año/mes).
        manual_filter_ids → States: se leen al refrescar pero NO disparan el refresh.
        apply_trigger_id  → Input adicional: clic en botón "Aplicar" dispara el refresh
                            (necesario cuando se usan manual_filter_ids).
        """
        from dash import callback, Input, Output, State
        ids = self.dash_ids(screen_id, prefix=prefix)
        inputs = [Input(ids["auto_interval"], "n_intervals")]
        if filter_ids:
            inputs.extend([Input(fid, "value") for fid in filter_ids])
        if apply_trigger_id:
            inputs.append(Input(apply_trigger_id, "n_clicks"))
        state = [State("selected-db-store", "data")]
        if manual_filter_ids:
            state.extend([State(fid, "value") for fid in manual_filter_ids])

        _MONTH_NAMES = (
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        )

        def _parse_filter_list(fids, vals):
            out = {}
            for i, fid in enumerate(fids or []):
                if i >= len(vals):
                    break
                val = vals[i]
                # Strip the first dash-segment (page prefix, e.g. "ops", "bank")
                # so "ops-tipo-unidad" → "tipo-unidad" and "ops-empresa" → "empresa".
                # This avoids single-segment collisions like "ops-unidad" == "ops-tipo-unidad"
                # which the old last-segment extraction produced.
                parts = fid.split("-")
                key = "-".join(parts[1:]) if len(parts) > 1 else fid
                key = key.replace("__", ".")
                if key == "year":
                    out["year"] = val if val else str(datetime.now().year)
                elif key == "month":
                    out["month"] = val if val else _MONTH_NAMES[datetime.now().month - 1]
                elif val:
                    out[key] = val
            return out

        outputs = [Output(ids["token_store"], "data")]
        if global_token_output_id:
            outputs.append(Output(global_token_output_id, "data", allow_duplicate=True))

        n_filter  = len(filter_ids)        if filter_ids        else 0
        n_apply   = 1                      if apply_trigger_id  else 0
        n_manual  = len(manual_filter_ids) if manual_filter_ids else 0

        prevent_initial = "initial_duplicate" if global_token_output_id else False
        @callback(outputs, inputs, state, prevent_initial_call=prevent_initial)
        async def _auto_refresh(n_intervals, *args):
            filter_values  = list(args[:n_filter])
            # apply_click sits between filter_ids and state args
            manual_values  = list(args[n_filter + n_apply + 1 : n_filter + n_apply + 1 + n_manual])
            selected_db    = args[n_filter + n_apply] if len(args) > n_filter + n_apply else None

            filters = _parse_filter_list(filter_ids, filter_values)
            # manual filters: merge but do NOT override auto filter values
            manual_filters = _parse_filter_list(manual_filter_ids, manual_values)
            for k, v in manual_filters.items():
                if k not in filters:
                    filters[k] = v

            all_fids = (filter_ids or []) + (manual_filter_ids or [])
            if any(f == "year" or f.endswith("-year") for f in all_fids) and "year" not in filters:
                filters["year"] = str(datetime.now().year)
            if any(f == "month" or f.endswith("-month") for f in all_fids) and "month" not in filters:
                filters["month"] = _MONTH_NAMES[datetime.now().month - 1]
            try:
                await self.refresh_screen(screen_id, filters=filters, use_cache=True, db_config=selected_db)
            except Exception as e:
                print(f"⚠️ DataManager [{screen_id}]: error en refresh, usando caché si existe — {e}")
            token_data = json.dumps(filters)
            if global_token_output_id:
                return [token_data, token_data]
            return token_data

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

        # Skeleton feedback: fires immediately when filters change (before async data fetch)
        loading_inputs = []
        if filter_ids:
            loading_inputs.extend([Input(fid, "value") for fid in filter_ids])
        if apply_trigger_id:
            loading_inputs.append(Input(apply_trigger_id, "n_clicks"))

        if loading_inputs:
            @callback(
                Output(body_output_id, "children", allow_duplicate=True),
                loading_inputs,
                prevent_initial_call=True,
            )
            def _show_loading(*args):
                return get_skeleton(screen_id)

        return ids

    async def get_filter_options(
        self,
        screen_id: str,
        filter_key: str,
        base_filters: Optional[Dict] = None,
        db_config: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        tenant_key = self._get_tenant_key(db_config or session.get("current_db"))
        screen_map = self.get_screen_map(tenant_key)
        screen = screen_map.get(screen_id, {})
        filter_spec = screen.get("filters", {}).get(filter_key)
        if not filter_spec:
            return []

        columns: List[str] = filter_spec.get("columns", [])
        if not columns:
            return []

        # Build a direct SELECT DISTINCT on dimension tables — no date constraints,
        # so all possible values appear regardless of the selected period.
        col_parts = [(c.split(".")[0], c.split(".")[1]) for c in columns if "." in c]
        if not col_parts:
            return []

        tables_meta = self.qb.tables
        seen_tbls: List[str] = []
        for tbl, _ in col_parts:
            if tbl not in seen_tbls:
                seen_tbls.append(tbl)

        # Use the last table as FROM anchor (it typically holds the FK to parent tables)
        from_tbl = seen_tbls[-1]
        from_tbl_def = tables_meta.get(from_tbl)
        if not from_tbl_def:
            return []

        select_parts = [f"{tbl}.{col}" for tbl, col in col_parts]
        joins_sql = ""
        processed: set = {from_tbl}
        for tbl in seen_tbls[:-1]:
            if tbl in processed:
                continue
            path = self.qb._find_join_path(from_tbl, tbl)
            if path:
                for next_alias, join_def in path:
                    if next_alias in processed:
                        continue
                    next_def = tables_meta.get(next_alias)
                    if not next_def:
                        continue
                    j_type = join_def.get("type", "INNER")
                    j_on = join_def.get("on")
                    joins_sql += f" {j_type} JOIN {next_def['table_name']} as {next_alias} ON {j_on}"
                    processed.add(next_alias)

        order_sql = ", ".join(select_parts)
        sql = (
            f"SELECT DISTINCT {', '.join(select_parts)}"
            f" FROM {from_tbl_def['table_name']} as {from_tbl}"
            f"{joins_sql}"
            f" ORDER BY {order_sql}"
        )

        db_name = db_config
        if not db_name:
            try:
                db_name = session.get("current_db")
            except RuntimeError:
                db_name = None

        if not db_name:
            return []

        #print(f"🔍 Filter SQL [{filter_key}]:\n{sql}\n")
        rows = await execute_dynamic_query(db_name, sql)
        if not rows:
            return []

        is_concat = filter_spec.get("display") == "concat"
        concat_sep = filter_spec.get("concat_sep", " / ")
        label_column = columns[0]

        def _row_val(row: Dict, col: str) -> Optional[str]:
            # SQL returns short column names; try full "tbl.col" first, then "col"
            v = row.get(col) or row.get(col.split(".")[-1])
            return str(v).strip() if v is not None else None

        options: List[Dict[str, str]] = []
        seen: set = set()

        for row in rows:
            if is_concat:
                parts = [_row_val(row, c) for c in columns]
                if any(p is None for p in parts):
                    continue
                label_str = concat_sep.join(p for p in parts if p)
                value_str = parts[-1] or ""
            else:
                label_str = _row_val(row, label_column)
                if label_str is None:
                    continue
                value_str = label_str

            if label_str and label_str not in seen:
                seen.add(label_str)
                options.append({"label": label_str, "value": value_str})

        return sorted(options, key=lambda x: x["label"])

    async def get_all_filter_options(
        self,
        screen_id: str,
        base_filters: Optional[Dict] = None,
        db_config: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, str]]]:
        """Fetch dropdown options for every filter declared on a screen.

        Returns a dict keyed by filter_key with the list of options for
        each filter, e.g.::

            {
              "d_area.area":      [{"label": "Norte", "value": "Norte"}, ...],
              "d_tipo_orden.tipo_orden": [...],
            }
        """
        tenant_key = self._get_tenant_key(db_config or session.get("current_db"))
        screen_map = self.get_screen_map(tenant_key)
        screen = screen_map.get(screen_id, {})
        filter_specs = screen.get("filters", {})
        if not filter_specs:
            return {}

        results: Dict[str, List[Dict[str, str]]] = {}
        for filter_key in filter_specs:
            try:
                results[filter_key] = await self.get_filter_options(
                    screen_id=screen_id,
                    filter_key=filter_key,
                    base_filters=base_filters,
                    db_config=db_config,
                )
            except Exception as exc:
                print(f"⚠️ get_all_filter_options [{screen_id}][{filter_key}]: {exc}")
                results[filter_key] = []

        return results


data_manager = DataManager()