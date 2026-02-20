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
            "label_prev_year": node.get("label_prev_year", "Año Ant"),
            "target_formatted": node.get("target_formatted"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "trend": node.get("trend_direction"),
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
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:gauge", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        cfg = {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": False,
            "value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year"),
            "target_formatted": node.get("target_formatted"),
            "meta_text": f"Meta: {node.get('target_formatted')}" if node.get("target_formatted") else "",
            "raw_data": node,
        }

        if self.key == "average_collection_days":
            cfg["vs_last_year_formatted"] = "none"
            cfg["label_prev_year"] = "Vs 2025"

        return cfg

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


class AdminTableStrategy:
    def __init__(self, screen_id, key, title="", color="gray", icon="tabler:table", has_detail=True, variant=None):
        self.screen_id = screen_id
        self.key = key
        self.title = title
        self.icon = icon
        self.color = color
        self.has_detail = has_detail
        self.variant = variant

    def _get_data(self, ctx):
        from services.data_manager import data_manager
        
        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {})
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

    def _render_dashboard(self, columns_config, row_data, theme="dark"):
        is_dark = theme == "dark"
        unique_key = f"{self.screen_id}-{self.key}"

        column_defs = []
        for i, col in enumerate(columns_config):
            col_def = {
                "field": col["field"],
                "headerName": col["headerName"],
                "sortable": True,
                "resizable": True,
                "suppressMenu": True,
                "tooltipField": col["field"],
                "cellStyle": {"fontSize": "12px", "display": "flex", "alignItems": "center"}
            }
            if i == 0:
                col_def.update({"pinned": "left", "width": 140, "suppressSizeToFit": True})
            else:
                col_def.update({"flex": 1, "minWidth": 100})
            column_defs.append(col_def)

        grid = dag.AgGrid(
            id={"type": "ag-grid-dashboard", "index": unique_key},
            rowData=row_data,
            columnDefs=column_defs,
            defaultColDef={"sortable": True, "resizable": True, "filter": False},
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 10,
                "rowHeight": 35,
                "headerHeight": 35,
                "suppressFieldDotNotation": True,
                "domLayout": "autoHeight"
            },
            className="ag-theme-alpine-dark" if is_dark else "ag-theme-alpine",
        )

        return html.Div(
            style={"display": "flex", "flexDirection": "column"},
            children=[
                html.Div(style={"width": "100%"}, children=grid),
            ],
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