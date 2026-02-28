"""
Catálogo global de widgets: listar por pantalla, listar todos, obtener definición completa.
Consume data_manager.SCREEN_MAP y MetadataEngine (tables, metrics, modifiers).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dashboard_core.metadata_engine import MetadataEngine
from services.data_manager import data_manager


@dataclass
class WidgetDefinition:
    """Definición de un widget para el agente y el motor SQL."""
    widget_id: str
    screen_id: str
    viz_type: str  # kpi | chart | categorical | table
    metric_keys: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    fixed_filters: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)  # labels, title, columns
    primary_metric: Optional[str] = None  # métrica principal para aggregate
    meta_metric_key: Optional[str] = None  # clave de métrica "meta" si existe (chart_roadmap)


def _metric_keys_from_spec(spec: Any) -> List[str]:
    if spec is None:
        return []
    if isinstance(spec, str):
        return [spec]
    if isinstance(spec, list):
        out = []
        for item in spec:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, list):
                out.extend(_metric_keys_from_spec(item))
        return list(dict.fromkeys(out))
    if isinstance(spec, dict):
        if "metrics" in spec:
            return _metric_keys_from_spec(spec["metrics"])
        if "actual" in spec:
            out = [spec["actual"]]
            if spec.get("anterior"):
                out.append(spec["anterior"])
            if spec.get("meta"):
                out.append(spec["meta"])
            return out
        if "kpi" in spec:
            return [spec["kpi"]]
    return []


def _dimensions_from_spec(spec: Any) -> List[str]:
    if not isinstance(spec, dict):
        return []
    dims = spec.get("dimensions") or spec.get("dimension")
    if isinstance(dims, str):
        return [dims]
    if isinstance(dims, list):
        return [d for d in dims if isinstance(d, str)]
    return []


def _fixed_filters_from_spec(spec: Any) -> Dict[str, Any]:
    if not isinstance(spec, dict):
        return {}
    return spec.get("fixed_filters") or {}


def _meta_from_spec(spec: Any, viz_type: str) -> Dict[str, Any]:
    if not isinstance(spec, dict):
        return {}
    meta = {}
    if "columns" in spec:
        meta["columns"] = spec["columns"]
    if "label" in spec:
        meta["label"] = spec["label"]
    if "title" in spec:
        meta["title"] = spec["title"]
    return meta


def list_widgets_by_screen(screen_id: str, tenant_db: Optional[str] = None) -> List[WidgetDefinition]:
    """Lista todos los widgets de una pantalla."""
    screen_map = data_manager.get_screen_map(tenant_db) or {}
    cfg = screen_map.get(screen_id)
    if not cfg:
        return []

    out: List[WidgetDefinition] = []
    meta_ctx = MetadataEngine().get_context(tenant_db)
    metrics_map = meta_ctx.get("metrics") or {}

    # kpi_roadmap: key -> string (metric) | dict
    for widget_id, spec in (cfg.get("kpi_roadmap") or {}).items():
        if isinstance(spec, str):
            metric_keys = [spec]
            dims = []
            fixed = {}
            meta = {}
            primary = spec
        else:
            metric_keys = _metric_keys_from_spec(spec)
            dims = _dimensions_from_spec(spec)
            fixed = _fixed_filters_from_spec(spec)
            meta = _meta_from_spec(spec, "kpi")
            primary = metric_keys[0] if metric_keys else None
        modifiers = []
        if primary and primary in metrics_map:
            rec = (metrics_map.get(primary) or {}).get("recipe") or {}
            if rec.get("time_modifier"):
                modifiers.append(rec["time_modifier"])
        out.append(WidgetDefinition(
            widget_id=widget_id,
            screen_id=screen_id,
            viz_type="kpi",
            metric_keys=metric_keys,
            dimensions=dims,
            fixed_filters=fixed,
            meta=meta,
            primary_metric=primary,
            meta_metric_key=None,
        ))

    # chart_roadmap
    for widget_id, spec in (cfg.get("chart_roadmap") or {}).items():
        if not isinstance(spec, dict):
            continue
        metric_keys = _metric_keys_from_spec(spec)
        dims = _dimensions_from_spec(spec)
        primary = spec.get("actual") or (metric_keys[0] if metric_keys else None)
        meta_key = spec.get("meta")
        out.append(WidgetDefinition(
            widget_id=widget_id,
            screen_id=screen_id,
            viz_type="chart",
            metric_keys=metric_keys,
            dimensions=dims,
            fixed_filters=_fixed_filters_from_spec(spec),
            meta=_meta_from_spec(spec, "chart"),
            primary_metric=primary,
            meta_metric_key=meta_key,
        ))

    # categorical_roadmap
    for widget_id, spec in (cfg.get("categorical_roadmap") or {}).items():
        if not isinstance(spec, dict):
            continue
        kpi = spec.get("kpi")
        dim = spec.get("dimension")
        metric_keys = [kpi] if kpi else []
        dims = [dim] if dim else []
        out.append(WidgetDefinition(
            widget_id=widget_id,
            screen_id=screen_id,
            viz_type="categorical",
            metric_keys=metric_keys,
            dimensions=dims,
            fixed_filters=_fixed_filters_from_spec(spec),
            meta=_meta_from_spec(spec, "categorical"),
            primary_metric=kpi,
            meta_metric_key=None,
        ))

    # table_roadmap
    for widget_id, spec in (cfg.get("table_roadmap") or {}).items():
        if not isinstance(spec, dict):
            continue
        metric_keys = _metric_keys_from_spec(spec)
        dims = _dimensions_from_spec(spec)
        out.append(WidgetDefinition(
            widget_id=widget_id,
            screen_id=screen_id,
            viz_type="table",
            metric_keys=metric_keys,
            dimensions=dims,
            fixed_filters=_fixed_filters_from_spec(spec),
            meta=_meta_from_spec(spec, "table"),
            primary_metric=metric_keys[0] if metric_keys else None,
            meta_metric_key=None,
        ))

    return out


def list_all_widgets_global(tenant_db: Optional[str] = None) -> List[WidgetDefinition]:
    """Lista todos los widgets de todas las pantallas."""
    screen_map = data_manager.get_screen_map(tenant_db) or {}
    out: List[WidgetDefinition] = []
    for screen_id in screen_map:
        out.extend(list_widgets_by_screen(screen_id, tenant_db=tenant_db))
    return out


def get_widget_definition(
    screen_id: str,
    widget_id: str,
    tenant_db: Optional[str] = None,
) -> Optional[WidgetDefinition]:
    """Obtiene la definición completa de un widget por pantalla e id."""
    widgets = list_widgets_by_screen(screen_id, tenant_db=tenant_db)
    for w in widgets:
        if w.widget_id == widget_id:
            return w
    return None
