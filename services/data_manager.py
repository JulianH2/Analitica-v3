from decimal import Decimal
import hashlib
import json
import re
import time
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
                print(f"⚠️ NO SE ENCONTRÓ screens.json. Buscando en: {[str(p) for p in possible_paths]}")
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
                "section_keys": ["operaciones", "mantenimiento", "administracion"],
                "ttl_seconds": 30,
                "kpi_roadmap": {},
                "chart_roadmap": {},
                "categorical_roadmap": {},
                "table_roadmap": {},
                "inject_paths": {}
            }
        }
    
    def _save_configs(self, path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.SCREEN_MAP, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
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
            print(f"⚠️ get_screen: No config para '{screen_id}'")
            return {}
        
        ttl = int(cfg.get("ttl_seconds") or self.DEFAULT_TTL_SECONDS)
        key = self._cache_key(screen_id, filters)
        
        print(f"🔑 get_screen buscando cache key: {key}")
        
        if not force_base and use_cache and key in self.cache:
            entry = self.cache[key]
            is_fresh = self._is_fresh(entry, ttl)
            print(f"✅ Cache HIT para '{screen_id}' | fresh={is_fresh} | keys={list(entry.data.keys()) if entry.data else 'empty'}")
            if is_fresh or allow_stale:
                return entry.data
        else:
            print(f"❌ Cache MISS para '{screen_id}'")
        
        base = self.base_service.get_full_dashboard_data()
        keys = cfg.get("section_keys") or [cfg.get("section_key")]
        sliced = {k: base.get(k, {}) for k in keys if k}
        
        print(f"📦 Retornando datos BASE (mock) para '{screen_id}'")
        
        if use_cache:
            self.cache[key] = CacheEntry(data=sliced, ts=time.time())
        
        return sliced
    
    async def _resolve_any_kpi(self, db_config, kpi_id, filters, session_results):
        if kpi_id in session_results:
            return session_results[kpi_id]
        
        build = self.qb.build_kpi_query(kpi_id, filters=filters)
        
        print(f"🔍 KPI: {kpi_id} | Build type: {build.get('type') if build else 'None'}")
        
        if not build: 
            print(f"⚠️ KPI '{kpi_id}' no tiene build, retornando 0")
            return 0.0
        
        if build.get("error"):
            print(f"❌ Error en build para '{kpi_id}': {build.get('error')}")
            return 0.0
        
        result = 0.0
        
        if build.get("type") == "placeholder":
            result = float(build.get("default_value", 0))
            print(f"📦 Placeholder '{kpi_id}' = {result}")
            session_results[kpi_id] = result
            return result
        
        if build.get("type") == "sql":
            try:
                query = build["query"]
                print(f"🗄️ SQL para '{kpi_id}':\n{query[:200]}...") 
                
                rows = await execute_dynamic_query(db_config, query)
                
                if rows:
                    v = list(rows[0].values())[0]
                    print(f"📊 Resultado raw para '{kpi_id}': {v} (tipo: {type(v).__name__})")
                    result = float(v) if v is not None else 0.0
                else:
                    print(f"⚠️ Sin filas para '{kpi_id}', usando 0")
                    result = 0.0
                    
            except Exception as e:
                print(f"❌ Error ejecutando SQL para '{kpi_id}': {e}")
                result = 0.0
        
        elif build.get("type") == "derived":
            formula = build.get("formula")
            if formula:
                print(f"📐 Fórmula derivada para '{kpi_id}': {formula}")
                
                tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula)
                tokens = sorted(list(set(tokens)), key=len, reverse=True)
                
                resolved_values = {}
                
                for token in tokens:
                    if token in ["if", "else", "or", "and"]: 
                        continue
                    sub_val = await self._resolve_any_kpi(db_config, token, filters, session_results)
                    sub_val = sub_val if sub_val is not None else 0.0
                    resolved_values[token] = sub_val
                    formula = re.sub(rf'\b{token}\b', str(sub_val), formula)
                
                print(f"📐 Fórmula resuelta: {formula}")
                print(f"📐 Valores usados: {resolved_values}")
                
                try: 
                    result = float(eval(formula))
                    print(f"✅ Resultado derivado '{kpi_id}' = {result}")
                except Exception as e:
                    print(f"❌ Error evaluando fórmula '{kpi_id}': {e}")
                    result = 0.0
        
        session_results[kpi_id] = result
        return result
    
    def _safe_eval_formula(self, formula: str, row_dict: Dict[str, Any]) -> float:
        try:
            safe_dict = {k: (float(v) if v is not None else 0.0) 
                        for k, v in row_dict.items() 
                        if isinstance(v, (int, float, type(None)))}
            
            for k, v in row_dict.items():
                if k not in safe_dict:
                    safe_dict[k] = v
            result = eval(formula, {"__builtins__": {}}, safe_dict)
            return float(result) if result is not None else 0.0
        except (ZeroDivisionError, TypeError, ValueError, NameError) as e:
            print(f"⚠️ Error evaluando fórmula '{formula}': {e}")
            print(f"   Valores disponibles: {row_dict}")
            return 0.0
        except Exception as e:
            print(f"❌ Error inesperado en fórmula '{formula}': {e}")
            return 0.0
    
    async def refresh_screen(self, screen_id: str, filters: Optional[Dict] = None, *, use_cache: bool = True) -> Json:
        cfg = self.SCREEN_MAP.get(screen_id) if self.SCREEN_MAP else {}
        if not cfg: 
            return {}
        
        normalized_filters = self._normalize_filters(filters)
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
        
        for ui_key, kpi_id in kpi_roadmap.items():
            await self._resolve_any_kpi(db_config, kpi_id, filters, session_results)

            base_kpi = kpi_id.replace("_previous_year", "").replace("_ytd", "").replace("_target", "")
            dependencies = [
                f"{base_kpi}_target", f"{base_kpi}_ytd",
                f"{base_kpi}_target_ytd", f"{base_kpi}_previous_year"
            ]
            for dep_kpi in dependencies:
                if dep_kpi in self.qb.metrics and dep_kpi not in session_results:
                    await self._resolve_any_kpi(db_config, dep_kpi, filters, session_results)
        
        for ui_key, kpi_id in kpi_roadmap.items():
            path = inject_paths.get(ui_key)
            if not path: continue
            
            val = session_results.get(kpi_id, 0.0)
            if val == 0: continue 

            metric_def = self.qb.metrics.get(kpi_id, {})
            fmt = metric_def.get("format") or metric_def.get("recipe", {}).get("format", "number")
            
            def fmt_val(v, f):
                if v is None: return "---"
                if f == "currency": return format_value(v, "$")
                if f == "percent": return f"{v * 100:.1f}%"
                if f == "integer": return f"{int(v):,}"
                return f"{v:,.2f}"

            formatted = fmt_val(val, fmt)
            
            base_kpi = kpi_id.replace("_previous_year", "").replace("_ytd", "").replace("_target", "")
            prev_year_val = session_results.get(f"{base_kpi}_previous_year", 0)
            target_val = session_results.get(f"{base_kpi}_target", 0)
            ytd_val = session_results.get(f"{base_kpi}_ytd", 0)
            target_ytd_val = session_results.get(f"{base_kpi}_target_ytd", 0)

            vs_prev_delta = (val - prev_year_val) / prev_year_val if prev_year_val else 0
            target_delta = (val - target_val) / target_val if target_val else 0
            ytd_delta = (ytd_val - target_ytd_val) / target_ytd_val if (target_ytd_val and ytd_val) else 0

            kpi_object = {
                "title": metric_def.get("name", ui_key),
                "value": val,
                "value_formatted": formatted,
                "format": fmt,
                
                "vs_last_year_value": prev_year_val,
                "vs_last_year_formatted": fmt_val(prev_year_val, fmt),
                "vs_last_year_delta": vs_prev_delta,
                "vs_last_year_delta_formatted": f"{vs_prev_delta * 100:+.1f}%" if prev_year_val else "N/A",
                "label_prev_year": "Año Ant.",
                
                "target": target_val,
                "target_formatted": fmt_val(target_val, fmt),
                "target_delta": target_delta,
                "target_delta_formatted": f"{target_delta * 100:+.1f}%" if target_val else "N/A",
                
                "ytd_value": ytd_val,
                "ytd_formatted": fmt_val(ytd_val, fmt),
                "ytd_delta": ytd_delta,
                "ytd_delta_formatted": f"{ytd_delta * 100:+.1f}%" if target_ytd_val else "---",
                
                "trend_direction": "up" if vs_prev_delta > 0 else "down" if vs_prev_delta < 0 else "neutral",
                "status": "success" if target_delta >= 0 else "warning"
            }
            self._set_path(data, path, kpi_object)

        chart_roadmap = cfg.get("chart_roadmap", {})
        for chart_key, series_map in chart_roadmap.items():
            path = inject_paths.get(chart_key)
            if not path: continue
            
            chart_data = {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": []
            }
            has_valid_data = False
            
            for series_name, kpi_id in series_map.items():
                build = self.qb.build_series_query(kpi_id, filters=filters)
                values = [0.0] * 12
                
                if build and "query" in build:
                    rows = await execute_dynamic_query(db_config, build["query"])
                    if rows:
                        has_valid_data = True
                        for r in rows:
                            p = r.get('period')
                            v = r.get('value', 0.0)
                            if isinstance(p, int) and 1 <= p <= 12:
                                values[p-1] = v
                
                chart_data["series"].append({
                    "name": series_name.capitalize(),
                    "data": values
                })
            
            if has_valid_data:
                self._set_path(data, path, {"data": chart_data}) 

        cat_roadmap = cfg.get("categorical_roadmap", {})
        for chart_key, spec in cat_roadmap.items():
            path = inject_paths.get(chart_key)
            if not path: continue
            
            kpi = spec.get("kpi")
            dim = spec.get("dimension")
            build = self.qb.build_categorical_query(kpi, dim, filters=filters)
            
            chart_data = {"labels": [], "values": [], "categories": [], "series": [{"name": "Valor", "data": []}]}
            has_valid_data = False

            if build and "query" in build:
                rows = await execute_dynamic_query(db_config, build["query"])
                if rows:
                    has_valid_data = True
                    for r in rows:
                        lbl = r.get("label", "N/A")
                        val = r.get("value") or 0.0
                        
                        chart_data["labels"].append(lbl)
                        chart_data["values"].append(val)
                        chart_data["categories"].append(lbl)
                        chart_data["series"][0]["data"].append(val)
            
            if has_valid_data:
                self._set_path(data, path, {"data": chart_data})

        for table_key, spec in cfg.get("table_roadmap", {}).items():
            path = inject_paths.get(table_key)
            if not path: continue

            dims = spec.get("dimensions", [])     
            mets = spec.get("metrics", [])        
            combined_filters = (filters or {}).copy()
            combined_filters.update(spec.get("fixed_filters", {}))

            metrics_by_fact_table = {} 
            for m_key in mets:
                metric_def = self.qb.metrics.get(m_key)
                if not metric_def or metric_def.get("type") == "derived": continue
                origin_table = metric_def.get("recipe", {}).get("table")
                if not origin_table: continue
                if origin_table not in metrics_by_fact_table: metrics_by_fact_table[origin_table] = []
                metrics_by_fact_table[origin_table].append(m_key)

            results_map = {}
            has_valid_data = False

            for fact_table, group_metrics in metrics_by_fact_table.items():
                build = self.qb.get_dataframe_query(group_metrics, dims, filters=combined_filters)
                if build and "query" in build:
                    rows = await execute_dynamic_query(db_config, build["query"])
                    if rows:
                        has_valid_data = True
                        for r in rows:
                            row_key = tuple(r.get(d) for d in dims) if len(dims) > 1 else list(r.values())[0]
                            if row_key not in results_map: results_map[row_key] = r.copy()
                            else: results_map[row_key].update(r)

            if not has_valid_data: continue

            final_rows = []
            column_totals = {}
            temp_rows = []

            for row_dict in results_map.values():
                for m in mets:
                    val = row_dict.get(m)
                    if val is None: val = 0.0
                    elif isinstance(val, Decimal): val = float(val)
                    row_dict[m] = val
                
                for col_def in spec.get("columns", []):
                    col_key = col_def.get("key")
                    formula = col_def.get("formula")
                    if formula:
                        row_dict[col_key] = self._safe_eval_formula(formula, row_dict)
                
                for k, v in row_dict.items():
                    if isinstance(v, (int, float)):
                        column_totals[k] = column_totals.get(k, 0.0) + v
                temp_rows.append(row_dict)

            headers = [c["label"] for c in spec.get("columns", [])]
            for row_dict in temp_rows:
                display_row = []
                for col_def in spec.get("columns", []):
                    col_key = col_def.get("key")
                    fmt = col_def.get("format")
                    val = row_dict.get(col_key)

                    if col_def.get("is_total_ratio"):
                        numerator_key = col_def.get("numerator_key", col_key)
                        val_num = row_dict.get(numerator_key, 0)
                        total_denom = column_totals.get(numerator_key, 0)
                        val = val_num / total_denom if total_denom else 0
                    
                    if fmt == "currency": display_val = format_value(val, "$")
                    elif fmt == "percent": display_val = f"{val:.2%}"
                    elif fmt == "integer": display_val = f"{int(val):,}" if val is not None else "0"
                    else: display_val = str(val) if val is not None else ""
                    
                    display_row.append(display_val)
                final_rows.append(display_row)

            self._set_path(data, path, {"headers": headers, "rows": final_rows})
        
        if use_cache:
            self.cache[cache_key] = CacheEntry(data=data, ts=time.time())

        return data
    
    def _set_path(self, data: Dict[str, Any], path: PathList, value: Any) -> None:
        cur = data
        for key in path[:-1]:
            if isinstance(cur, dict):
                if key not in cur:
                    cur[key] = {}
                cur = cur[key] # type: ignore
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
        ], ids
    
    def register_dash_refresh_callbacks(
        self,
        *,
        screen_id: str,
        body_output_id: str,
        render_body: Callable[[Json], Any],
        prefix: Optional[str] = None,
        filter_ids: Optional[List[str]] = None
    ) -> Dict[str, str]:
        
        import dash
        from dash import callback, Input, Output
        
        ids = self.dash_ids(screen_id, prefix=prefix)
        
        @callback(
            Output(ids["token_store"], "data"),
            [Input(ids["auto_interval"], "n_intervals")] + 
            ([Input(fid, "value") for fid in filter_ids] if filter_ids else []),
            prevent_initial_call=False,
        )
        async def _auto_refresh(n_intervals, *filter_values):
            filters = {}
            if filter_ids:
                for i, fid in enumerate(filter_ids):
                    val = filter_values[i]
                    key = fid.split("-")[-1] if "-" in fid else fid
                    if val:
                        filters[key] = val
            
            print(f"🔄 Auto-refresh para '{screen_id}' con filtros: {filters}")
            await self.refresh_screen(screen_id, filters=filters, use_cache=True)
            
            return json.dumps(filters)
        
        @callback(
            Output(body_output_id, "children"),
            Input(ids["token_store"], "data"),
        )
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
            
            print(f"🎨 Re-render para '{screen_id}' buscando cache con filtros: {current_filters}")
            
            ctx = self.get_screen(
                screen_id, 
                use_cache=True, 
                allow_stale=True, 
                filters=current_filters
            )
            
            print(f"📦 Datos obtenidos del cache: {list(ctx.keys()) if ctx else 'vacío'}")
            
            return render_body(ctx)
        
        return ids

data_manager = DataManager()