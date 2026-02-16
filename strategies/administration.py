import dash_ag_grid as dag
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html
from dash_iconify import DashIconify
from datetime import datetime
from design_system import BadgeConfig, ChartColors, Colors, ComponentSizes, GaugeConfig, SemanticColors, Shadows, Space, Typography
from design_system import DesignSystem as DS
from utils.helpers import format_value, safe_get

from .base_strategy import KPIStrategy
from .chart_engine import ChartEngine


def get_current_month():
    return datetime.now().month


def safe_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            clean = val.replace("%", "").replace("$", "").replace(",", "").strip()
            return float(clean) if clean else default
        except:
            return default
    return default


def safe_max(*args):
    valid = [safe_float(v) for v in args if v is not None]
    return max(valid) if valid else 0.0


class AdminKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, icon, color, has_detail=True, layout_config=None, inverse=False, variant=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.kpi_key = kpi_key
        self.inverse = inverse

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        return {
            "title": self.title,
            "icon": self.icon,
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
        }

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c="dimmed") # type: ignore


class AdminGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, color="indigo", icon="tabler:gauge", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.kpi_key = kpi_key

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        cfg = {
            "title": self.title,
            "icon": self.icon,
            "value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year"),
            "target_formatted": node.get("target_formatted"),
            "meta_text": f"Meta: {node.get('target_formatted')}" if node.get("target_formatted") else "",
        }

        if self.kpi_key == "average_collection_days":
            cfg["vs_last_year_formatted"] = "none"
            cfg["label_prev_year"] = "Vs 2025"

        return cfg

    def get_figure(self, data_context, theme="dark"):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        fig = ChartEngine.render_gauge(raw_node, theme, self.layout, self.hex_color)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c="dimmed") # type: ignore


class AdminDonutChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-pie", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        fig = ChartEngine.render_donut(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c="dimmed") # type: ignore


class AdminTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "color": self.color, "is_chart": True}

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        fig = ChartEngine.render_trend(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c="dimmed") # type: ignore

class AdminHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        fig = ChartEngine.render_horizontal_bar(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class AdminHistoricalForecastLineStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "color": self.color, "is_chart": True}

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_name = s.get("name", "")
            s_data = s.get("data", [])
            is_forecast = "Forecast" in s_name or "Proyección" in s_name
            base_color = ChartColors.LINE_TRENDS[idx % len(ChartColors.LINE_TRENDS)]

            fig.add_trace(go.Scatter(
                x=categories,
                y=s_data,
                name=s_name,
                mode="lines+markers",
                line=dict(color=base_color, width=2, dash="dash" if is_forecast else "solid"),
                marker=dict(size=5 if is_forecast else 6),
            ))

        h_val = self.layout.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c="dimmed") # type: ignore


class AdminStackedBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_name = s.get("name", "")
            s_data = s.get("data", [])
            base_color = ChartColors.CHART_COLORS[idx % len(ChartColors.CHART_COLORS)]

            fig.add_trace(go.Bar(
                x=categories,
                y=s_data,
                name=s_name,
                marker=dict(color=base_color, cornerradius=6),
            ))

        h_val = self.layout.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            barmode="stack",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c="dimmed") # type: ignore


class AdminCashFlowChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:arrows-up-down", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        ingresos = data_source.get("ingresos", [])
        egresos = data_source.get("egresos", [])

        fig = go.Figure()
        fig.add_trace(go.Bar(x=categories, y=ingresos, name="Ingresos", marker=dict(color=Colors.POSITIVE, cornerradius=6)))
        fig.add_trace(go.Bar(x=categories, y=[-e for e in egresos], name="Egresos", marker=dict(color=Colors.NEGATIVE, cornerradius=6)))

        h_val = self.layout.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            barmode="relative",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig


class AdminMultiLineChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_name = s.get("name", "")
            s_data = s.get("data", [])
            base_color = ChartColors.LINE_TRENDS[idx % len(ChartColors.LINE_TRENDS)]

            fig.add_trace(go.Scatter(
                x=categories,
                y=s_data,
                name=s_name,
                mode="lines+markers",
                line=dict(color=base_color, width=2),
                marker=dict(size=6),
            ))

        h_val = self.layout.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig

# En strategies/administration.py

import dash_mantine_components as dmc
import dash_ag_grid as dag
from dash import html
from dash_iconify import DashIconify
from design_system import DesignSystem, Colors, Typography, Space, ComponentSizes
from utils.helpers import safe_get 

class AdminTableStrategy:
    def __init__(self, screen_id, table_key, title="", icon="tabler:table", color="gray", variant=None):
        self.screen_id = screen_id
        self.table_key = table_key
        self.title = title
        self.icon = icon
        self.color = color
        self.variant = variant
        self.has_detail = True  # <--- CRÍTICO: Habilita el botón del drawer

    def _get_data(self, data_context):
        from services.data_manager import data_manager
        
        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {})
        inject_paths = screen_config.get("inject_paths", {})
        
        path = None
        if self.variant:
            lookup_key = f"{self.table_key}_{self.variant}"
            path = inject_paths.get(lookup_key) or inject_paths.get(self.table_key)
        else:
            path = inject_paths.get(self.table_key)

        if not path:
            return None, None

        node = safe_get(data_context, path)
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

    def get_card_config(self, data_context):
        columns_config, row_data = self._get_data(data_context)
        # Preparar datos crudos para el drawer (similar a OpsTableStrategy)
        export_data = []
        if columns_config and row_data:
             for row in row_data:
                new_row = {col["headerName"]: row.get(col["field"]) for col in columns_config}
                export_data.append(new_row)

        return {
            "title": self.title or self.table_key,
            "icon": self.icon,
            "is_table": True,
            "main_value": f"{len(row_data)} registros" if row_data else "0",
            "raw_data": export_data 
        }

    def render(self, data_context, mode="dashboard", theme="dark"):
        columns_config, row_data = self._get_data(data_context)

        if columns_config is None or not row_data:
            return dmc.Center(
                style={"height": 200},
                children=[
                    dmc.Stack(
                        align="center",
                        gap=Space.XS,
                        children=[
                            DashIconify(icon="tabler:table-off", width=40, color=Colors.NEXA_GRAY),
                            dmc.Text("Sin datos disponibles", size="xs", c="dimmed", style={"fontFamily": Typography.FAMILY}),
                        ],
                    )
                ],
            )

        # CORRECCIÓN CLAVE: El drawer manda "analysis", tu código usa "analyst".
        # Aceptamos ambos y llamamos a _render_analyst para tener una ID ÚNICA.
        if mode in ["analyst", "analysis"]:
            return self._render_analyst(columns_config, row_data, theme)

        return self._render_dashboard(columns_config, row_data, theme)

    def _render_dashboard(self, columns_config, row_data, theme="dark"):
        is_dark = theme == "dark"
        unique_key = f"{self.screen_id}-{self.table_key}"

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
            # ID ÚNICA PARA DASHBOARD: ag-grid-dashboard
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
        # ID ÚNICA PARA DRAWER: ag-grid-analyst
        # Esto evita el conflicto de IDs duplicadas que impedía abrir el drawer
        table_id = {"type": "ag-grid-analyst", "index": f"{self.screen_id}-{self.table_key}"}

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