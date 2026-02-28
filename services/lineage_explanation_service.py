"""
Explicación con lineage: cómo se calcula el KPI (fórmula, tablas, joins, filtros, modificadores).
100% basado en metadata; no ejecuta SQL.
"""
from typing import Any, Dict, List, Optional

from dashboard_core.metadata_engine import MetadataEngine
from services.widget_catalog_service import WidgetDefinition


def explain(
    widget_definition: WidgetDefinition,
    filters: Optional[Dict[str, Any]] = None,
    tenant_db: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Genera explicación de lineage para el widget.
    Salida: metric_formulas, tables_involved, joins_chain, global_filters, time_modifiers.
    """
    meta = MetadataEngine().get_context(tenant_db) or {}
    metrics_map = meta.get("metrics") or {}
    tables_map = meta.get("tables") or {}
    modifiers_map = meta.get("modifiers") or {}

    metric_formulas: List[Dict[str, Any]] = []
    tables_involved = set()
    for mk in (widget_definition.metric_keys or []) or ([widget_definition.primary_metric] if widget_definition.primary_metric else []):
        if not mk:
            continue
        m = metrics_map.get(mk)
        if not m:
            metric_formulas.append({"metric_key": mk, "name": mk, "formula": "Sin definición en metadata"})
            continue
        name = m.get("name") or mk
        if m.get("type") == "derived":
            metric_formulas.append({
                "metric_key": mk,
                "name": name,
                "type": "derived",
                "formula": m.get("formula") or "N/A",
            })
            continue
        recipe = m.get("recipe") or {}
        table_alias = recipe.get("table")
        column = recipe.get("column")
        agg = recipe.get("aggregation") or "SUM"
        time_mod = recipe.get("time_modifier")
        formula_desc = f"{agg}({table_alias}.{column})" if table_alias and column else "N/A"
        if time_mod:
            mod_desc = (modifiers_map.get(time_mod) or {}).get("description") or time_mod
            formula_desc += f" con modificador: {mod_desc}"
        metric_formulas.append({
            "metric_key": mk,
            "name": name,
            "table": table_alias,
            "column": column,
            "aggregation": agg,
            "time_modifier": time_mod,
            "formula": formula_desc,
        })
        if table_alias:
            tables_involved.add(table_alias)
    for dim in (widget_definition.dimensions or []):
        if "." in dim:
            tbl = dim.split(".")[0]
            tables_involved.add(tbl)

    joins_chain: List[Dict[str, Any]] = []
    for tbl in sorted(tables_involved):
        t_def = tables_map.get(tbl)
        if not t_def:
            continue
        joins = t_def.get("joins") or {}
        for j_key, j_def in joins.items():
            target = j_def.get("target_table")
            on = j_def.get("on")
            j_type = j_def.get("type", "INNER")
            if target and on:
                joins_chain.append({"from": tbl, "to": target, "type": j_type, "on": on})

    global_filters_desc: List[str] = []
    if filters:
        if filters.get("year"):
            global_filters_desc.append(f"Año: {filters['year']}")
        if filters.get("month"):
            global_filters_desc.append(f"Mes: {filters['month']}")
        for k, v in filters.items():
            if k in ("year", "month"):
                continue
            if v:
                global_filters_desc.append(f"{k}: {v}")

    time_modifiers_desc: List[Dict[str, Any]] = []
    for m in metric_formulas:
        tm = m.get("time_modifier")
        if tm and tm not in [x.get("key") for x in time_modifiers_desc]:
            desc = (modifiers_map.get(tm) or {}).get("description") or tm
            time_modifiers_desc.append({"key": tm, "description": desc})

    return {
        "widget_id": widget_definition.widget_id,
        "screen_id": widget_definition.screen_id,
        "metric_formulas": metric_formulas,
        "tables_involved": sorted(tables_involved),
        "joins": joins_chain,
        "global_filters": global_filters_desc,
        "time_modifiers": time_modifiers_desc,
    }
