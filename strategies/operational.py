import datetime
import dash_ag_grid as dag
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html
from dash_iconify import DashIconify
from design_system import BadgeConfig, ChartColors, Colors, ComponentSizes, GaugeConfig, PlotlyConfig, SemanticColors, Shadows, Space, Typography
from design_system import DesignSystem as DS
from services.time_service import TimeService
from utils.helpers import format_value, safe_get
from .base_strategy import KPIStrategy

time_service = TimeService()
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

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

def clean_series(x_data, y_data):
    import math
    x_clean, y_clean = [], []
    for x, y in zip(x_data or [], y_data or []):
        y_val = safe_float(y)
        if not math.isnan(y_val):
            x_clean.append(x)
            y_clean.append(y_val)
        else:
            x_clean.append(x)
            y_clean.append(0)
    return x_clean, y_clean


class OpsKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, icon, color, has_detail=True, layout_config=None, inverse=False, variant=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.kpi_key = kpi_key
        self.inverse = inverse

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node, "value_formatted": str(raw_node)}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node if isinstance(raw_node, dict) else {}

        if not node:
            return {"title": self.title, "main_value": "---", "icon": self.icon, "color": self.color, "raw_data": []}

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
        }

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica operacional.", size="sm", c="dimmed") # type: ignore


class OpsGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, color="indigo", icon="tabler:gauge", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.kpi_key = kpi_key

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node, "value_formatted": str(raw_node)}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node if isinstance(raw_node, dict) else {}

        if not node:
            return {"title": self.title, "main_value": "---", "icon": self.icon, "color": self.color, "raw_data": []}

        return {
            "title": self.title,
            "icon": self.icon,
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
        }

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context, theme="dark"):
        ts = TimeService()
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        if not raw_node or not isinstance(raw_node, dict):
            return self._create_empty_figure(theme=theme)

        prev_year = str(ts.previous_year)
        current = safe_float(raw_node.get("value", 0))
        target = safe_float(raw_node.get("target")) if raw_node.get("target") else None
        vs_last_year = safe_float(raw_node.get("vs_last_year")) if raw_node.get("vs_last_year") else None

        percentage = (current / target * 100) if target and target > 0 else 0
        gauge_color = GaugeConfig.get_gauge_color(percentage) if target else self.hex_color
        max_val = safe_max(current, target or 0, vs_last_year or 0, 100)

        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=current,
            number={"font": {"size": Typography.KPI_MEDIUM, "family": Typography.FAMILY}, "valueformat": ",.0f"},
            gauge={
                "axis": {"range": [0, max_val * 1.1], "tickwidth": 1},
                "bar": {"color": gauge_color},
                "bgcolor": Colors.TRANSPARENT,
                "borderwidth": 0,
                "threshold": {"line": {"color": Colors.CHART_TARGET, "width": 4}, "thickness": 0.8, "value": target if target else max_val},
            },
        ))

        if target:
            fig.add_annotation(x=0.5, y=-0.15, text=f"<b>META:</b> {target:,.0f}", showarrow=False, font=dict(size=Typography.BADGE, color=Colors.CHART_TARGET, family=Typography.FAMILY), xref="paper", yref="paper")
        if vs_last_year:
            fig.add_annotation(x=0.5, y=-0.30, text=f"Año {prev_year}: {vs_last_year:,.0f}", showarrow=False, font=dict(size=Typography.XS, color=Colors.CHART_PREVIOUS, family=Typography.FAMILY), xref="paper", yref="paper")

        fig.update_layout(template="plotly_dark" if theme == "dark" else "plotly", height=self.layout.get("height", ComponentSizes.KPI_HEIGHT_NORMAL), margin=dict(l=25, r=25, t=30, b=50), hovermode=False)
        return fig

class OpsTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "color": self.color, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context, theme="dark"):
        ts = TimeService()
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        curr_year = str(ts.current_year)
        prev_year = str(ts.previous_year)
        curr_month = datetime.date.today().month

        data_source = node.get("data", node)
        categories = data_source.get("categories") or data_source.get("months") or []
        series_list = data_source.get("series", [])

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_name = s.get("name", "")
            s_data = s.get("data", [])

            if "Meta" in s_name or "Objetivo" in s_name:
                base_color = Colors.CHART_TARGET
            elif curr_year in s_name or "Actual" in s_name:
                base_color = Colors.CHART_CURRENT
            elif prev_year in s_name or "Anterior" in s_name:
                base_color = Colors.CHART_PREVIOUS
            else:
                base_color = ChartColors.CHART_COLORS[idx % len(ChartColors.CHART_COLORS)]

            past_y = [safe_float(y) if i < curr_month else None for i, y in enumerate(s_data)]
            future_y = [safe_float(y) if i >= curr_month - 1 else None for i, y in enumerate(s_data)]

            if "Meta" in s_name:
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name="Meta",
                    mode="lines+markers",
                    line=dict(color=base_color, width=2, dash="dot"),
                    marker=dict(size=6),
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories,
                    y=past_y,
                    name=s_name.replace(curr_year, "Actual").replace(prev_year, "Anterior"),
                    marker=dict(color=base_color, cornerradius=6),
                    width=0.38,
                    offsetgroup=str(idx),
                ))
                fig.add_trace(go.Bar(
                    x=categories,
                    y=future_y,
                    name=f"{s_name} (proy.)",
                    marker=dict(color=base_color, opacity=0.45, cornerradius=6),
                    width=0.38,
                    offsetgroup=str(idx),
                    showlegend=False,
                ))

        h_val = self.layout.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            barmode="group",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig


class OpsDonutChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-pie", color="indigo", color_map=None, has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key
        self.color_map = color_map or {}

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context, theme="dark"):
        is_dark = theme == "dark"
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key) or {}
        data_source = node.get("data", node)

        labels = data_source.get("labels", [])
        values = data_source.get("values", [])
        colors = data_source.get("colors", [])
        total = data_source.get("total_formatted", "")

        if not labels or not values:
            return self._create_empty_figure(theme=theme)

        if not colors:
            colors = [ChartColors.DONUT[i % len(ChartColors.DONUT)] for i in range(len(labels))]

        fig_height = self.layout.get("height", 260)
        max_index = max(range(len(values)), key=lambda i: values[i])

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.65,
            marker=dict(colors=colors, line=dict(color=Colors.BG_DARK_CARD if is_dark else Colors.BG_LIGHT, width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
            pull=[0.05 if i == max_index else 0 for i in range(len(values))],
        )])

        if total:
            fig.add_annotation(
                text=f"<b>Total</b><br>{total}",
                x=0.30,
                y=0.5,
                showarrow=False,
                font=dict(size=Typography.MD, color=Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT, family=Typography.FAMILY),
                xref="paper",
                yref="paper",
            )

        fig.update_traces(domain=dict(x=[0.0, 0.60], y=[0.0, 1.0]))
        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=fig_height,
            margin=dict(t=30, b=20, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.65, itemsizing="constant"),
        )
        return fig


class OpsHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context, theme="dark"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = [str(c) for c in (data_source.get("categories") or data_source.get("labels") or [])]
        values = [safe_float(v) for v in data_source.get("values", [])]
        target_val = safe_float(data_source.get("target") or data_source.get("goal"))

        if not categories:
            return self._create_empty_figure("Sin datos", theme=theme)

        num_bars = len(categories)
        calculated_height = max(self.layout.get("height", 340), num_bars * 50 + 100)
        avg_value = sum(values) / len(values) if values else 0

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker=dict(color=Colors.CHART_GOLD, cornerradius=6),
            width=0.80,
            text=[f"${v/1e6:.1f}M" if v >= 1e6 else f"${v/1e3:.1f}k" if v >= 1000 else f"${v:.0f}" for v in values],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Valor: $%{x:,.2f}<extra></extra>",
        ))

        if target_val > 0 or avg_value > 0:
            ref_val = target_val if target_val > 0 else avg_value
            fig.add_vline(
                x=ref_val,
                line_width=2,
                line_dash="dot",
                line_color=Colors.CHART_TARGET,
                annotation_text=f"META: ${ref_val:,.0f}",
                annotation_position="top",
                annotation_font=dict(size=Typography.XS, color=Colors.CHART_TARGET, family=Typography.FAMILY),
            )

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=calculated_height,
            margin=dict(t=50, b=40, l=120, r=80),
            showlegend=False,
            xaxis=dict(showgrid=True, zeroline=False, tickformat="$,.0f", side="top"),
            yaxis=dict(type="category", autorange="reversed", automargin=True),
            bargap=0.8,
        )
        return fig

class OpsTableStrategy:
    def __init__(self, screen_id, table_key, title="", icon="tabler:table", color="gray", variant=None):
        self.screen_id = screen_id
        self.table_key = table_key
        self.title = title
        self.icon = icon
        self.color = color
        self.has_detail = True
        self.variant = variant

    def _get_data(self, data_context):
        from services.data_manager import data_manager

        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {}) # type: ignore
        inject_paths = screen_config.get("inject_paths", {})

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

    def render(self, data_context, mode="dashboard", theme="dark"):
        columns_config, row_data = self._get_data(data_context)
        if columns_config is None:
            return dmc.Center(style={"height": 200}, children=[
                dmc.Stack(align="center", gap=Space.XS, children=[
                    DashIconify(icon="tabler:table-off", width=40, color=Colors.NEXA_GRAY),
                    dmc.Text("Sin datos disponibles", size="xs", c="dimmed", style={"fontFamily": Typography.FAMILY}), # type: ignore
                ])
            ])

        if mode == "analyst":
            return self._render_analyst(columns_config, row_data, theme)
        return self._render_dashboard(columns_config, row_data, theme)

    def get_card_config(self, data_context):
        columns_config, row_data = self._get_data(data_context)
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
            "raw_data": export_data,
        }

    def get_figure(self, data_context):
        return None

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
            className="ag-theme-alpine",
        )

        return html.Div(style={"height": "500px", "display": "flex", "flexDirection": "column"}, children=[
            dmc.Badge("Modo Analista", variant="light", color="violet", mb=Space.XS),
            html.Div(style={"flex": 1}, children=grid),
        ])


class OpsMapStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:map", color="indigo", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context, theme="dark"):
        is_dark = theme == "dark"
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure("Sin datos de mapa", theme=theme)

        data_source = node.get("data", node)
        routes = data_source.get("routes", [])
        if not routes:
            return self._create_empty_figure("Sin rutas disponibles", theme=theme)

        fig = go.Figure()

        for route in routes:
            lats = route.get("lat", [])
            lons = route.get("lon", [])
            name = route.get("name", "Ruta")
            color = route.get("color", Colors.CHART_BLUE)

            if lats and lons:
                fig.add_trace(go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode="lines+markers",
                    name=name,
                    line=dict(width=3, color=color),
                    marker=dict(size=8, color=color),
                ))

        center_lat, center_lon = 20.5937, -100.3897
        all_lats = [lat for r in routes for lat in (r.get("lat", []) or [])]
        all_lons = [lon for r in routes for lon in (r.get("lon", []) or [])]

        if all_lats and all_lons:
            center_lat = sum(all_lats) / len(all_lats)
            center_lon = sum(all_lons) / len(all_lons)

        legend_bg = "rgba(98,104,110,0.9)" if is_dark else "rgba(255,255,255,0.9)"

        fig.update_layout(
            mapbox=dict(style="open-street-map", center=dict(lat=center_lat, lon=center_lon), zoom=10),
            margin=dict(l=0, r=0, t=0, b=0),
            height=self.layout.get("height", ComponentSizes.CHART_HEIGHT_LG),
            showlegend=True,
            font=dict(family=Typography.FAMILY, size=Typography.SM, color=Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor=legend_bg, font=dict(size=Typography.XS, family=Typography.FAMILY)),
        )
        return fig
