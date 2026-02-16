import datetime
import dash_ag_grid as dag
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import Colors, ComponentSizes, Space, Typography
from utils.helpers import safe_get
from .base_strategy import KPIStrategy
from .chart_engine import ChartEngine


class OpsKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="", has_detail=True, variant=None, inverse=False, layout_config=None):
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
            "status_color": node.get("status_color"),
            "raw_data": node,
        }

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica operacional.", size="sm", c="dimmed") # type: ignore


class OpsGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:gauge", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

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
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "target_formatted": node.get("target_formatted"),
            "target_delta": node.get("target_delta"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status"),
            "raw_data": node,
        }

    def get_figure(self, ctx, theme="dark"):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_gauge(raw_node, theme, self.layout, self.hex_color)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class OpsTrendChartStrategy(KPIStrategy):
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


class OpsDonutChartStrategy(KPIStrategy):
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


class OpsHorizontalBarStrategy(KPIStrategy):
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


class OpsMapStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:map", has_detail=True, variant=None, layout_config=None):
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
        fig = ChartEngine.render_map(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure("Sin datos de mapa", theme=theme)
        return fig


class OpsTableStrategy:
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
        headers_list, raw_rows = [], []

        if isinstance(data_source, dict):
            headers_list = data_source.get("headers", [])
            raw_rows = data_source.get("rows", [])
        elif isinstance(data_source, list) and data_source and isinstance(data_source[0], dict):
            headers_list = list(data_source[0].keys())
            for item in data_source:
                raw_rows.append([item.get(h) for h in headers_list])

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
                    field_key = f"col_{i}"
                    val = row.get(h, "")
                    row_dict[field_key] = val if val is not None else ""
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
            "raw_data": export_data,
        }

    def render(self, ctx, mode="dashboard", theme="dark"):
        columns_config, row_data = self._get_data(ctx)
        if columns_config is None:
            return dmc.Center(style={"height": 200}, children=[
                dmc.Stack(align="center", gap=Space.XS, children=[
                    DashIconify(icon="tabler:table-off", width=40, color=Colors.NEXA_GRAY),
                    dmc.Text("Sin datos disponibles", size="xs", c="dimmed", style={"fontFamily": Typography.FAMILY}), # type: ignore
                ])
            ])

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
            }
            if i == 0:
                col_def.update({"pinned": "left", "width": 90, "flex": 0})
            else:
                col_def.update({"minWidth": 130, "flex": 1})
            column_defs.append(col_def)

        grid = dag.AgGrid(
            id={"type": "ag-grid-dashboard", "index": unique_key},
            rowData=row_data,
            columnDefs=column_defs,
            defaultColDef={"sortable": True, "resizable": True, "filter": False},
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 20,
                "rowHeight": ComponentSizes.TABLE_ROW_HEIGHT,
                "headerHeight": ComponentSizes.TABLE_HEADER_HEIGHT,
                "suppressFieldDotNotation": True,
                "quickFilterText": "",
            },
            style={"height": "100%", "width": "100%"},
            className="ag-theme-alpine compact",
        )

        search_bar = dmc.Group(justify="space-between", mt=Space.SM, children=[
            dmc.TextInput(
                id={"type": "ag-quick-search", "index": unique_key},
                placeholder="Buscar...",
                leftSection=DashIconify(icon="tabler:search", width=ComponentSizes.ICON_SM),
                size="xs",
                radius="xl",
                style={"width": "220px"},
                styles={"input": {
                    "fontSize": f"{Typography.SM}px",
                    "height": f"{ComponentSizes.BUTTON_HEIGHT_SM}px",
                    "fontFamily": Typography.FAMILY,
                    "backgroundColor": "rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.03)",
                    "color": Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT,
                }},
            ),
            dmc.Text(f"{len(row_data)} registros", size="xs", c="dimmed", style={"fontSize": f"{Typography.XS}px", "fontFamily": Typography.FAMILY}), # type: ignore
        ])

        return html.Div(style={"height": "100%", "display": "flex", "flexDirection": "column"}, children=[
            html.Div(style={"flex": 1, "minHeight": "250px", "overflow": "hidden"}, children=grid),
            search_bar,
        ])

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
            className="ag-theme-alpine",
        )

        return html.Div(style={"height": "500px", "display": "flex", "flexDirection": "column"}, children=[
            dmc.Badge("Modo Analista", variant="light", color="violet", mb=Space.XS),
            html.Div(style={"flex": 1}, children=grid),
        ])