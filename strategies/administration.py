import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import Colors, ComponentSizes, Space, Typography, dmc as _dmc
from utils.helpers import safe_get
from .base_strategy import KPIStrategy
from .chart_engine import ChartEngine


class AdminKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="", has_detail=True, variant=None, inverse=False, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)
        self.inverse = inverse

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": False,
            "color": self.color,
            "inverse": self.inverse,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year", "Año Ant."),
            "target_formatted": node.get("target_formatted"),
            "target_delta": node.get("target_delta"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "trend": node.get("trend"),
            "trend_direction": node.get("trend_direction"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status"),
            "status_color": node.get("status_color") or self.color,
            "raw_data": node,
        }

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=_dmc("dimmed"))
class AdminGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:gauge", has_detail=True, variant=None, inverse=False, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)
        self.inverse = inverse

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node, "value_formatted": str(raw_node)}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node if isinstance(raw_node, dict) else {}

        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": False,
            "color": self.color,
            "inverse": self.inverse,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year", "Año Ant."),
            "target_formatted": node.get("target_formatted"),
            "target_delta": node.get("target_delta"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "trend": node.get("trend"),
            "trend_direction": node.get("trend_direction"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status"),
            "status_color": node.get("status_color") or self.color,
            "raw_data": node,
        }

    def get_figure(self, ctx, theme="dark"):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_gauge(raw_node, theme, self.layout, self.hex_color)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig
    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=_dmc("dimmed"))
    
class AdminDonutChartStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-pie", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_donut(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=_dmc("dimmed"))
class AdminTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-line", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "color": self.color,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_trend(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=_dmc("dimmed"))
class AdminHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-bar", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_horizontal_bar(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class AdminHistoricalForecastLineStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-line", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "color": self.color,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_multi_line(node, theme, self.layout, forecast_mode=True)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=_dmc("dimmed"))
class AdminStackedBarStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-bar", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "color": self.color,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_stacked_bar(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=_dmc("dimmed"))

class AdminBarChartStrategy(KPIStrategy):
    """Vertical bar chart strategy (non-stacked)."""
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-bar", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "color": self.color,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_bar_chart(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=_dmc("dimmed"))

class AdminMultiLineStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-line", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_multi_line(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


def _parse_admin_cell(v):
    if isinstance(v, (int, float)):
        return float(v) if v == v else None
    if not isinstance(v, str):
        return None
    s = v.strip()
    if s in ("", "---", "-"):
        return None
    neg = s.startswith("-")
    s = s.lstrip("+-$").strip()
    mult = 1.0
    if s.endswith("B"):
        mult = 1e9; s = s[:-1]
    elif s.endswith("M"):
        mult = 1e6; s = s[:-1]
    elif s.endswith("m"):
        mult = 1e3; s = s[:-1]
    elif s.upper().endswith("K"):
        mult = 1e3; s = s[:-1]
    elif s.endswith("%"):
        return None
    try:
        n = float(s.replace(",", "")) * mult
        return -n if neg else n
    except ValueError:
        return None


def _fmt_admin_currency(v):
    if v == 0:
        return "$0"
    a = abs(v)
    if a >= 1e9:
        return f"${v/1e9:.1f}B"
    if a >= 1e6:
        return f"${v/1e6:.1f}M"
    if a >= 1e3:
        return f"${v/1e3:.1f}m"
    return f"${v:,.0f}"


class AdminTableStrategy:
    def __init__(self, screen_id, key, title="", color="gray", icon="tabler:table", has_detail=True, variant=None, pivot_col=None):
        self.screen_id = screen_id
        self.key = key
        self.title = title
        self.icon = icon
        self.color = color
        self.has_detail = has_detail
        self.variant = variant
        self.pivot_col = pivot_col      # if set, pivot on this column index (id=0, pivot_dim=1, value=2)
        self.pivot_order: "list[str] | None" = None  # override after init to enforce column order
        self.hex_color = Colors.COLOR_MAP.get(color, Colors.NEXA_GRAY)

    def _get_data(self, ctx):
        from flask import session
        from services.data_manager import data_manager

        screen_map = data_manager.get_screen_map(session.get("current_db")) or {}
        screen_config = screen_map.get(self.screen_id, {})
        inject_paths = screen_config.get("inject_paths", {})
        
        path = None
        if self.variant:
            lookup_key = f"{self.key}_{self.variant}"
            path = inject_paths.get(lookup_key) or inject_paths.get(self.key)
        else:
            path = inject_paths.get(self.key)

        if not path:
            return None, None

        node = safe_get(ctx, path)
        if not node:
            return None, None

        data_source = node.get("data", node) if isinstance(node, dict) else node
        headers_list = []
        raw_rows = []

        if isinstance(data_source, dict):
            headers_list = data_source.get("headers", [])
            raw_rows = data_source.get("rows", [])
        elif isinstance(data_source, list) and data_source:
            if isinstance(data_source[0], dict):
                headers_list = list(data_source[0].keys())
                raw_rows = [[item.get(h) for h in headers_list] for item in data_source]
            elif isinstance(data_source[0], list):
                headers_list = [f"Col {i+1}" for i in range(len(data_source[0]))]
                raw_rows = data_source

        if not headers_list:
            return None, None

        columns_config = [{"field": f"col_{i}", "headerName": h} for i, h in enumerate(headers_list)]

        safe_row_data = []
        for row in raw_rows:
            row_dict = {}
            if isinstance(row, (list, tuple)):
                for i, col in enumerate(columns_config):
                    val = row[i] if i < len(row) else ""
                    row_dict[col["field"]] = val if val is not None else ""
            elif isinstance(row, dict):
                for i, h in enumerate(headers_list):
                    val = row.get(h, "")
                    row_dict[f"col_{i}"] = val if val is not None else ""
            safe_row_data.append(row_dict)

        return columns_config, safe_row_data

    def get_card_config(self, ctx):
        columns_config, row_data = self._get_data(ctx)
        export_data = []
        if columns_config and row_data:
             for row in row_data:
                new_row = {col["headerName"]: row.get(col["field"]) for col in columns_config}
                export_data.append(new_row)

        return {
            "title": self.title or self.key,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": True,
            "is_chart": False,
            "main_value": f"{len(row_data)} registros" if row_data else "0",
            "raw_data": export_data 
        }

    def render(self, ctx, mode="dashboard", theme="dark"):
        columns_config, row_data = self._get_data(ctx)

        if columns_config is None or not row_data:
            return dmc.Center(
                style={"height": 200},
                children=[
                    dmc.Stack(
                        align="center",
                        gap=Space.XS,
                        children=[
                            DashIconify(icon="tabler:table-off", width=40, color=Colors.NEXA_GRAY),
                            dmc.Text("Sin datos disponibles", size="xs", c=_dmc("dimmed"), style={"fontFamily": Typography.FAMILY}),
                        ],
                    )
                ],
            )

        if mode in ["analyst", "analysis"]:
            return self._render_analyst(columns_config, row_data, theme)

        return self._render_dashboard(columns_config, row_data, theme)

    def _pivot_data(self, columns_config, row_data):
        """Pivot flat (id, pivot_dim, value) rows → id-row × pivot_dim-columns."""
        if len(columns_config) < 3 or not row_data:
            return columns_config, row_data, []

        id_field   = columns_config[0]["field"]
        id_header  = columns_config[0]["headerName"]
        piv_field  = columns_config[1]["field"]
        val_field  = columns_config[2]["field"]

        # Ordered unique pivot values — respect pivot_order if provided
        data_vals = list(dict.fromkeys(
            str(r.get(piv_field, "") or "") for r in row_data if r.get(piv_field)
        ))
        if self.pivot_order:
            # Keep prescribed order; append any extra values found in data but not in order list
            piv_vals = [p for p in self.pivot_order] + [v for v in data_vals if v not in self.pivot_order]
        else:
            piv_vals = data_vals
        pv_to_sf = {pv: f"pv_{i}" for i, pv in enumerate(piv_vals)}

        # Group by id
        groups: dict = {}
        group_order: list = []
        for r in row_data:
            id_val = str(r.get(id_field, "") or "")
            pv = str(r.get(piv_field, "") or "")
            val = r.get(val_field, "")
            if id_val not in groups:
                groups[id_val] = {id_field: id_val}
                group_order.append(id_val)
            if pv in pv_to_sf:
                groups[id_val][pv_to_sf[pv]] = val

        # Build rows + row totals + column sums
        col_sums = {sf: 0.0 for sf in pv_to_sf.values()}
        new_rows = []
        for id_val in group_order:
            row = {id_field: groups[id_val][id_field]}
            row_total = 0.0
            for pv in piv_vals:
                sf = pv_to_sf[pv]
                raw = groups[id_val].get(sf, "---")
                row[sf] = raw if raw else "---"
                n = _parse_admin_cell(raw)
                if n is not None:
                    row_total += n
                    col_sums[sf] += n
            row["__total__"] = _fmt_admin_currency(row_total)
            new_rows.append(row)

        # TOTAL pinned bottom row
        total_row = {id_field: "TOTAL"}
        grand = 0.0
        for pv in piv_vals:
            sf = pv_to_sf[pv]
            total_row[sf] = _fmt_admin_currency(col_sums[sf])
            grand += col_sums[sf]
        total_row["__total__"] = _fmt_admin_currency(grand)

        # Column definitions
        new_cols = [{"field": id_field, "headerName": id_header}]
        for pv in piv_vals:
            new_cols.append({"field": pv_to_sf[pv], "headerName": pv})
        new_cols.append({"field": "__total__", "headerName": "Total"})

        return new_cols, new_rows, [total_row]

    def _render_dashboard(self, columns_config, row_data, theme="dark"):
        is_dark = theme == "dark"
        unique_key = f"{self.screen_id}-{self.key}"

        pinned_bottom = []
        if self.pivot_col is not None:
            columns_config, row_data, pinned_bottom = self._pivot_data(columns_config, row_data)

        column_defs = []
        for i, col in enumerate(columns_config):
            is_total_col = col.get("field") == "__total__"
            col_def = {
                "field": col["field"],
                "headerName": col["headerName"],
                "sortable": True,
                "resizable": True,
                "suppressMenu": True,
                "tooltipField": col["field"],
                "cellStyle": {
                    "fontSize": "11px",
                    "fontWeight": "bold" if is_total_col else "normal",
                    "display": "flex",
                    "alignItems": "center",
                },
            }
            if i == 0:
                col_def.update({"pinned": "left", "width": 120, "suppressSizeToFit": True})
            elif is_total_col:
                col_def.update({"pinned": "right", "width": 100, "flex": 0})
            else:
                col_def.update({"flex": 1, "minWidth": 90})
            column_defs.append(col_def)

        grid = dag.AgGrid(
            id={"type": "ag-grid-dashboard", "index": unique_key},
            rowData=row_data,
            columnDefs=column_defs,
            defaultColDef={"sortable": True, "resizable": True, "filter": False},
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 15,
                "rowHeight": 28,
                "headerHeight": 28,
                "suppressFieldDotNotation": True,
                "domLayout": "autoHeight",
                "pinnedBottomRowData": pinned_bottom,
            },
            className="ag-theme-alpine-dark" if is_dark else "ag-theme-alpine",
        )

        return html.Div(
            style={"display": "flex", "flexDirection": "column"},
            children=[html.Div(style={"width": "100%", "overflowX": "auto"}, children=grid)],
        )

    def _render_analyst(self, columns_config, row_data, theme="dark"):
        table_id = {"type": "ag-grid-analyst", "index": f"{self.screen_id}-{self.key}"}

        def _get_filter_type(field):
            if row_data:
                val = row_data[0].get(field)
                if isinstance(val, (int, float)):
                    return "agNumberColumnFilter"
            return "agTextColumnFilter"

        column_defs = []
        for i, col in enumerate(columns_config):
            col_def = {
                "field": col["field"],
                "headerName": col["headerName"],
                "sortable": True,
                "filter": _get_filter_type(col["field"]),
                "resizable": True,
                "floatingFilter": True,
                "minWidth": 110,
                "flex": 1,
                "tooltipField": col["field"],
            }
            if i == 0:
                col_def["pinned"] = "left"
            column_defs.append(col_def)

        grid = dag.AgGrid(
            id=table_id,
            rowData=row_data,
            columnDefs=column_defs,
            dashGridOptions={"pagination": True, "paginationPageSize": 50, "suppressFieldDotNotation": True},
            style={"height": "100%", "width": "100%"},
            className="ag-theme-alpine-dark" if theme == "dark" else "ag-theme-alpine",
        )

        return html.Div(
            style={"height": "500px", "display": "flex", "flexDirection": "column"},
            children=[
                dmc.Badge("Modo Analista", variant="light", color="violet", mb=Space.XS),
                html.Div(style={"flex": 1}, children=grid),
            ]
        )