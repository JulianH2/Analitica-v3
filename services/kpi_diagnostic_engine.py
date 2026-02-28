"""
Motor SQL determinístico para diagnóstico de KPIs.
Solo ejecuta SQL generado por SmartQueryBuilder (nunca SQL libre del LLM).
Modos: aggregate, timeseries, breakdown, detail (breakdown con limit), meta_compare.
Incluye run_diagnostic para flujo estructurado de diagnóstico automático.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dashboard_core.query_builder import SmartQueryBuilder
from dashboard_core.db_helper import _execute_dynamic_query_sync

from services.widget_catalog_service import WidgetDefinition

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticResult:
    """Resultado del diagnóstico: evidencia, queries y hallazgos."""
    aggregate_value: Optional[Dict[str, Any]] = None
    meta_compare: Optional[Dict[str, Any]] = None
    timeseries_rows: List[Dict] = field(default_factory=list)
    breakdown_rows: List[Dict] = field(default_factory=list)
    detail_rows: List[Dict] = field(default_factory=list)
    queries_executed: List[str] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)  # tipo, descripción, datos

DETAIL_ROW_LIMIT = 100
MAX_QUERIES_PER_REQUEST = 10


def _sanitize_filters(filters: Optional[Dict]) -> Dict:
    """Allowlist de claves conocidas para evitar inyección."""
    if not filters or not isinstance(filters, dict):
        return {}
    allowed = {"year", "month"}
    out = {}
    for k, v in filters.items():
        if k in allowed:
            if k == "year" and v is not None:
                try:
                    out["year"] = int(v)
                except (TypeError, ValueError):
                    out["year"] = str(v).strip()[:20]
            elif k == "month" and v is not None:
                out["month"] = str(v).strip()[:30]
            else:
                out[k] = v
    return out


def run_mode(
    widget_definition: WidgetDefinition,
    filters: Optional[Dict[str, Any]],
    db_name: str,
    mode: str,
    tenant_db: Optional[str] = None,
    limit: int = DETAIL_ROW_LIMIT,
) -> Dict[str, Any]:
    """
    Ejecuta un modo del motor y devuelve { "mode", "rows", "query_executed", "error" (opcional) }.
    mode: aggregate | timeseries | breakdown | detail | meta_compare
    """
    filters = _sanitize_filters(filters)
    qb = SmartQueryBuilder(tenant_db=tenant_db)
    metrics = list(widget_definition.metric_keys) or []
    if not metrics and widget_definition.primary_metric:
        metrics = [widget_definition.primary_metric]
    if not metrics:
        return {"mode": mode, "rows": [], "query_executed": None, "error": "Widget sin métricas"}

    combined_filters = {**filters, **(widget_definition.fixed_filters or {})}

    if mode == "aggregate":
        build = qb.get_dataframe_query(metrics, [], filters=combined_filters)
    elif mode == "timeseries":
        build = qb.get_dataframe_query(metrics, ["__month__"], filters=combined_filters)
    elif mode == "breakdown":
        dims = list(widget_definition.dimensions) or []
        build = qb.get_dataframe_query(metrics, dims, filters=combined_filters)
    elif mode == "detail":
        dims = list(widget_definition.dimensions) or []
        build = qb.get_dataframe_query(metrics, dims, filters=combined_filters)
        if build and build.get("query"):
            build["query"] = build["query"].rstrip() + f" ORDER BY 1 OFFSET 0 ROWS FETCH NEXT {max(1, min(limit, 500))} ROWS ONLY"
    elif mode == "meta_compare":
        primary = widget_definition.primary_metric
        meta_key = widget_definition.meta_metric_key
        if not primary:
            return {"mode": mode, "rows": [], "query_executed": None, "error": "Sin métrica principal"}
        agg_actual = qb.get_dataframe_query([primary], [], filters=combined_filters)
        rows_actual = []
        query_actual = None
        if agg_actual and agg_actual.get("query"):
            query_actual = agg_actual["query"]
            rows_actual = _execute_dynamic_query_sync(db_name, query_actual)
        rows_meta = []
        query_meta = None
        if meta_key:
            agg_meta = qb.get_dataframe_query([meta_key], [], filters=combined_filters)
            if agg_meta and agg_meta.get("query"):
                query_meta = agg_meta["query"]
                rows_meta = _execute_dynamic_query_sync(db_name, query_meta)
        out_rows = []
        if rows_actual:
            row = dict(rows_actual[0])
            row["_metric"] = primary
            row["_type"] = "actual"
            out_rows.append(row)
        if rows_meta:
            row = dict(rows_meta[0])
            row["_metric"] = meta_key
            row["_type"] = "meta"
            out_rows.append(row)
        return {
            "mode": mode,
            "rows": out_rows,
            "query_executed": query_actual or query_meta,
            "queries": [q for q in [query_actual, query_meta] if q],
        }
    else:
        return {"mode": mode, "rows": [], "query_executed": None, "error": f"Modo no soportado: {mode}"}

    if not build or build.get("error"):
        err = (build or {}).get("error", "Error al construir query")
        return {"mode": mode, "rows": [], "query_executed": None, "error": err}
    if (build or {}).get("type") == "placeholder":
        return {"mode": mode, "rows": build.get("default_value") or [], "query_executed": None}

    query = build.get("query")
    if not query:
        return {"mode": mode, "rows": [], "query_executed": None, "error": "Query vacía"}
    try:
        rows = _execute_dynamic_query_sync(db_name, query)
        row_count = len(rows) if rows else 0
        logger.info(
            "KPIDiagnosticEngine query executed: mode=%s db=%s widget=%s row_count=%s",
            mode, db_name, getattr(widget_definition, "widget_id", ""), row_count,
        )
    except Exception as e:
        logger.exception("KPIDiagnosticEngine run_mode failed: %s", e)
        return {"mode": mode, "rows": [], "query_executed": query, "error": str(e)}
    return {"mode": mode, "rows": rows or [], "query_executed": query}


def run_diagnostic(
    widget_definition: WidgetDefinition,
    filters: Optional[Dict[str, Any]],
    db_name: str,
    tenant_db: Optional[str] = None,
    max_queries: int = MAX_QUERIES_PER_REQUEST,
) -> DiagnosticResult:
    """
    Ejecuta el flujo de diagnóstico estructurado: aggregate, meta_compare (si aplica),
    timeseries, detección de anomalías, breakdown, y opcionalmente detail en periodo afectado.
    """
    result = DiagnosticResult()
    filters = _sanitize_filters(filters)
    query_count = 0

    def run(mode: str, **kwargs):
        nonlocal query_count
        if query_count >= max_queries:
            return None
        out = run_mode(widget_definition, filters, db_name, mode, tenant_db=tenant_db, **kwargs)
        if out.get("query_executed"):
            query_count += 1
            result.queries_executed.append(out["query_executed"])
        for q in out.get("queries") or []:
            if q and q not in result.queries_executed:
                query_count += 1
                result.queries_executed.append(q)
        return out

    agg = run("aggregate")
    if agg and agg.get("rows"):
        result.aggregate_value = agg["rows"][0] if agg["rows"] else None
    if widget_definition.meta_metric_key:
        meta_out = run("meta_compare")
        if meta_out and meta_out.get("rows"):
            result.meta_compare = {"rows": meta_out["rows"]}

    ts_out = run("timeseries")
    if ts_out and ts_out.get("rows"):
        result.timeseries_rows = ts_out["rows"]
        for i, row in enumerate(result.timeseries_rows):
            period = row.get("period")
            val = None
            for k, v in row.items():
                if k != "period" and v is not None and isinstance(v, (int, float)):
                    val = v
                    break
            if val is not None and val == 0:
                result.findings.append({
                    "tipo": "periodo_sin_valor",
                    "descripcion": f"Periodo {period} con valor 0",
                    "datos": {"period": period, "value": val},
                })
            if i > 0 and val is not None and isinstance(val, (int, float)):
                prev = None
                for k, v in result.timeseries_rows[i - 1].items():
                    if k != "period" and v is not None and isinstance(v, (int, float)):
                        prev = v
                        break
                if prev is not None and prev != 0 and val is not None:
                    pct = ((val - prev) / prev) * 100
                    if pct < -20:
                        result.findings.append({
                            "tipo": "caida_abrupta",
                            "descripcion": f"Caída de {pct:.1f}% respecto al periodo anterior",
                            "datos": {"period": period, "value": val, "previous": prev, "pct_change": pct},
                        })

    if widget_definition.dimensions:
        br_out = run("breakdown")
        if br_out and br_out.get("rows"):
            result.breakdown_rows = br_out["rows"][:20]
            if result.findings and result.breakdown_rows:
                result.findings.append({
                    "tipo": "breakdown_disponible",
                    "descripcion": "Desglose por dimensiones para identificar contribuyentes",
                    "datos": {"row_count": len(result.breakdown_rows)},
                })

    if result.findings and widget_definition.dimensions and query_count < max_queries:
        detail_out = run("detail", limit=50)
        if detail_out and detail_out.get("rows"):
            result.detail_rows = detail_out["rows"]

    return result
