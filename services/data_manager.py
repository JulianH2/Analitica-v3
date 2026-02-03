from decimal import Decimal
import hashlib
import json
import re
import time
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

from dash import no_update
from flask import session

from dashboard_core.query_builder import SmartQueryBuilder
from dashboard_core.db_helper import execute_dynamic_query
from services.real_data_service import RealDataService
from utils.helpers import format_value

Json = Union[Dict[str, Any], List[Any]]
PathList = List[Union[str, int]]

@dataclass
class CacheEntry:
    data: Json
    ts: float

class DataManager:
    _instance: Optional["DataManager"] = None
    SCREEN_MAP: Optional[Dict[str, Dict[str, Any]]] = None
    
    def __new__(cls) -> "DataManager":
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self.base_service = RealDataService()
        self.qb = SmartQueryBuilder()
        self.cache = {}
        self.DEFAULT_TTL_SECONDS = 30
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

    async def _resolve_any_kpi(self, db_config, kpi_id: str, filters: Dict, session_results: Dict) -> float:
        if kpi_id in session_results:
            return self._clean_val(session_results[kpi_id])
        
        try:
            build = self.qb.build_kpi_query(kpi_id, filters=filters)
        except Exception:
            session_results[kpi_id] = 0.0
            return 0.0
        
        if not build or build.get("error"):
            session_results[kpi_id] = 0.0
            return 0.0
        
        result = 0.0
        
        if build.get("type") == "placeholder":
            result = self._clean_val(build.get("default_value", 0))
            session_results[kpi_id] = result
            return result
        
        if build.get("type") == "sql":
            try:
                rows = await execute_dynamic_query(db_config, build["query"])
                if rows:
                    v = list(rows[0].values())[0]
                    result = self._clean_val(v)
            except Exception:
                result = 0.0
        
        elif build.get("type") == "derived":
            formula = build.get("formula", "")
            if formula:
                try:
                    tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula)
                    tokens = sorted(list(set(tokens)), key=len, reverse=True)
                    
                    for token in tokens:
                        if token in ["if", "else", "or", "and"]:
                            continue
                        sub_val = await self._resolve_any_kpi(db_config, token, filters, session_results)
                        formula = re.sub(rf'\b{token}\b', str(sub_val), formula)
                    
                    result = self._clean_val(eval(formula))
                except Exception:
                    result = 0.0
        
        session_results[kpi_id] = result
        return result

    def _safe_eval_formula(self, formula: str, row_dict: Dict[str, Any]) -> float:
        try:
            safe_dict = {k: self._clean_val(v) for k, v in row_dict.items()}
            result = eval(formula, {"__builtins__": {}}, safe_dict)
            return self._clean_val(result)
        except Exception:
            return 0.0

    async def refresh_screen(self, screen_id: str, filters: Optional[Dict] = None, *, use_cache: bool = True) -> Json:
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
        
        db_config = session.get("current_db")
        if not db_config:
            if use_cache:
                self.cache[cache_key] = CacheEntry(data=data, ts=time.time())
            return data
        
        kpi_roadmap = cfg.get("kpi_roadmap", {})
        inject_paths = cfg.get("inject_paths", {})
        session_results = {}
        connection_failed = False

        for ui_key, kpi_id in kpi_roadmap.items():
            if connection_failed:
                break
            try:
                await self._resolve_any_kpi(db_config, kpi_id, filters, session_results) # type: ignore
                base_kpi = kpi_id.replace("_previous_year", "").replace("_ytd", "").replace("_target", "")
                for suffix in ["_previous_year", "_target", "_ytd", "_target_ytd"]:
                    dep_kpi = f"{base_kpi}{suffix}"
                    if dep_kpi in self.qb.metrics and dep_kpi not in session_results:
                        await self._resolve_any_kpi(db_config, dep_kpi, filters, session_results) # type: ignore
            except Exception as e:
                if "Login failed" in str(e) or "28000" in str(e):
                    connection_failed = True
                    break

        for ui_key, kpi_id in kpi_roadmap.items():
            path = inject_paths.get(ui_key)
            if not path:
                continue
            
            val = self._clean_val(session_results.get(kpi_id, 0))
            if val == 0:
                continue
            
            metric_def = self.qb.metrics.get(kpi_id, {})
            fmt = metric_def.get("format") or metric_def.get("recipe", {}).get("format", "number")
            
            base_kpi = kpi_id.replace("_previous_year", "").replace("_ytd", "").replace("_target", "")
            prev_val = self._clean_val(session_results.get(f"{base_kpi}_previous_year", 0))
            target_val = self._clean_val(session_results.get(f"{base_kpi}_target", 0))
            ytd_val = self._clean_val(session_results.get(f"{base_kpi}_ytd", 0))
            target_ytd = self._clean_val(session_results.get(f"{base_kpi}_target_ytd", 0))
            
            vs_prev_delta = self._safe_divide(val - prev_val, prev_val)
            target_delta = self._safe_divide(val - target_val, target_val)
            ytd_delta = self._safe_divide(ytd_val - target_ytd, target_ytd) if ytd_val else 0
            
            kpi_object = {
                "title": metric_def.get("name", ui_key),
                "value": val,
                "value_formatted": self._format_val(val, fmt),
                "format": fmt,
                "vs_last_year_value": prev_val,
                "vs_last_year_formatted": self._format_val(prev_val, fmt) if prev_val else "---",
                "vs_last_year_delta": vs_prev_delta,
                "vs_last_year_delta_formatted": self._format_delta(vs_prev_delta, prev_val > 0),
                "label_prev_year": "Año Ant.",
                "target": target_val,
                "target_formatted": self._format_val(target_val, fmt) if target_val else "---",
                "target_delta": target_delta,
                "target_delta_formatted": self._format_delta(target_delta, target_val > 0),
                "ytd_value": ytd_val,
                "ytd_formatted": self._format_val(ytd_val, fmt) if ytd_val else "---",
                "ytd_delta": ytd_delta,
                "ytd_delta_formatted": self._format_delta(ytd_delta, target_ytd > 0),
                "trend": vs_prev_delta * 100,
                "trend_direction": "up" if vs_prev_delta > 0 else "down" if vs_prev_delta < 0 else "neutral",
                "status": "success" if target_delta >= 0 else "warning"
            }
            self._set_path(data, path, kpi_object)

        for chart_key, series_map in cfg.get("chart_roadmap", {}).items():
            path = inject_paths.get(chart_key)
            if not path or connection_failed:
                continue
            
            chart_data = {"months": ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"], "series": []}
            has_valid_data = False
            
            for series_name, kpi_id in series_map.items():
                try:
                    build = self.qb.build_series_query(kpi_id, filters=filters)
                    values = [None] * 12
                    if build and "query" in build:
                        rows = await execute_dynamic_query(db_config, build["query"])
                        if rows:
                            has_valid_data = True
                            for r in rows:
                                p = r.get('period')
                                if isinstance(p, int) and 1 <= p <= 12:
                                    values[p-1] = self._clean_val(r.get('value')) # type: ignore
                except Exception:
                    pass
                chart_data["series"].append({"name": series_name.capitalize(), "data": values}) # type: ignore
            
            if has_valid_data:
                self._set_path(data, path, {"data": chart_data})

        for chart_key, spec in cfg.get("categorical_roadmap", {}).items():
            path = inject_paths.get(chart_key)
            if not path or connection_failed:
                continue
            try:
                build = self.qb.build_categorical_query(spec.get("kpi"), spec.get("dimension"), filters=filters)
                chart_data = {"labels": [], "values": [], "categories": [], "series": [{"name": "Valor", "data": []}]}
                has_valid_data = False
                if build and "query" in build:
                    rows = await execute_dynamic_query(db_config, build["query"])
                    if rows:
                        has_valid_data = True
                        for r in rows:
                            lbl = r.get("label", "N/A")
                            val = self._clean_val(r.get("value"))
                            chart_data["labels"].append(lbl)
                            chart_data["values"].append(val)
                            chart_data["categories"].append(lbl)
                            chart_data["series"][0]["data"].append(val)
                if has_valid_data:
                    self._set_path(data, path, {"data": chart_data})
            except Exception:
                pass
            
        for table_key, spec in cfg.get("table_roadmap", {}).items():
            path = inject_paths.get(table_key)
            if not path or connection_failed:
                continue
            dims = spec.get("dimensions", [])
            mets = spec.get("metrics", [])
            combined_filters = (filters or {}).copy()
            combined_filters.update(spec.get("fixed_filters", {}))

            metrics_by_fact = {}
            for m_key in mets:
                m_def = self.qb.metrics.get(m_key)
                if not m_def or m_def.get("type") == "derived":
                    continue
                tbl = m_def.get("recipe", {}).get("table")
                if tbl:
                    metrics_by_fact.setdefault(tbl, []).append(m_key)

            results_map = {}
            has_data = False
            for fact_tbl, grp_mets in metrics_by_fact.items():
                try:
                    build = self.qb.get_dataframe_query(grp_mets, dims, filters=combined_filters)
                    if build and "query" in build:
                        rows = await execute_dynamic_query(db_config, build["query"])
                        if rows:
                            has_data = True
                            for r in rows:
                                rk = tuple(r.get(d) for d in dims) if len(dims) > 1 else list(r.values())[0]
                                results_map.setdefault(rk, {}).update(r)
                except Exception:
                    pass

            if not has_data:
                continue

            col_totals = {}
            temp_rows = []
            for row in results_map.values():
                for m in mets:
                    row[m] = self._clean_val(row.get(m))
                for col in spec.get("columns", []):
                    if col.get("formula"):
                        row[col["key"]] = self._safe_eval_formula(col["formula"], row)
                for k, v in row.items():
                    if isinstance(v, (int, float)):
                        col_totals[k] = col_totals.get(k, 0) + v
                temp_rows.append(row)

            headers = [c["label"] for c in spec.get("columns", [])]
            final_rows = []
            for row in temp_rows:
                disp = []
                for col in spec.get("columns", []):
                    ck = col["key"]
                    val = row.get(ck)
                    if col.get("is_total_ratio"):
                        nk = col.get("numerator_key", ck)
                        val = self._safe_divide(row.get(nk, 0), col_totals.get(nk, 0))
                    f = col.get("format")
                    if f == "currency":
                        disp.append(self._format_val(val, "currency"))
                    elif f == "percent":
                        disp.append(f"{self._clean_val(val):.2%}")
                    elif f == "integer":
                        disp.append(f"{int(self._clean_val(val)):,}")
                    else:
                        disp.append(str(val) if val else "")
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
        return {"token_store": f"{base}__tok", "auto_interval": f"{base}__int"}

    def dash_refresh_components(self, screen_id, interval_ms=800, max_intervals=1, prefix=None):
        from dash import dcc
        ids = self.dash_ids(screen_id, prefix)
        return [
            dcc.Store(id=ids["token_store"], data=0),
            dcc.Interval(id=ids["auto_interval"], interval=interval_ms, max_intervals=max_intervals)
        ], ids

    def register_dash_refresh_callbacks(self, *, screen_id: str, body_output_id: str, render_body: Callable[[Json], Any], prefix: Optional[str] = None, filter_ids: Optional[List[str]] = None) -> Dict[str, str]:
        from dash import callback, Input, Output
        ids = self.dash_ids(screen_id, prefix=prefix)

        @callback(Output(ids["token_store"], "data"), [Input(ids["auto_interval"], "n_intervals")] + ([Input(fid, "value") for fid in filter_ids] if filter_ids else []), prevent_initial_call=False)
        async def _auto_refresh(n_intervals, *filter_values):
            filters = {}
            if filter_ids:
                for i, fid in enumerate(filter_ids):
                    val = filter_values[i]
                    key = fid.split("-")[-1] if "-" in fid else fid
                    if val:
                        filters[key] = val
            await self.refresh_screen(screen_id, filters=filters, use_cache=True)
            return json.dumps(filters)

        @callback(Output(body_output_id, "children"), Input(ids["token_store"], "data"))
        def _rerender(token_data):
            if token_data is None:
                return no_update
            current_filters = {}
            try:
                if isinstance(token_data, str):
                    current_filters = json.loads(token_data)
                elif isinstance(token_data, dict):
                    current_filters = token_data
            except:
                pass
            return render_body(self.get_screen(screen_id, use_cache=True, allow_stale=True, filters=current_filters))

        return ids

data_manager = DataManager()