import math
from datetime import datetime
import dash_mantine_components as dmc
import plotly.graph_objects as go
from design_system import DesignSystem, SemanticColors
from utils.helpers import format_value, safe_get
from .base_strategy import KPIStrategy
from .chart_engine import ChartEngine

class WorkshopKPIStrategy(KPIStrategy):
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

        config = {
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

        if node.get("percentage_of_total"):
            config["percentage_of_total"] = node.get("percentage_of_total")

        return config

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica de mantenimiento.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


class WorkshopGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, color="indigo", icon="tabler:gauge", has_detail=True, layout_config=None, use_needle=False, variant=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.kpi_key = kpi_key
        self.use_needle = use_needle
        self.gauge_params = {
            "range_max_mult": 1.15,
            "threshold_width": 5,
            "threshold_color": DesignSystem.WARNING[5],
            "exceed_color": DesignSystem.INFO[5],
            "bg_color": "rgba(148, 163, 184, 0.05)",
            "font_size": 18,
        }

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        return {
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

    def get_figure(self, data_context, theme="light"):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)

        if self.use_needle:
            if isinstance(raw_node, (int, float)):
                node = {"value": raw_node}
            elif raw_node is None:
                node = {}
            else:
                node = raw_node

            current_val = node.get("value", 0)
            target_val = node.get("target", 0)

            if isinstance(current_val, float) and current_val <= 1.0:
                current_val *= 100
            if isinstance(target_val, float) and target_val <= 1.0:
                target_val *= 100

            return self._create_needle_gauge(current_val, target_val)

        fig = ChartEngine.render_gauge(raw_node, theme, self.layout, self.hex_color)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _create_needle_gauge(self, current_val, target_val):
        fig = go.Figure(go.Indicator(
            mode="gauge",
            value=current_val,
            gauge={
                "axis": {"range": [0, 100], "visible": True, "tickwidth": 1, "tickcolor": "gray"},
                "bar": {"color": "rgba(0,0,0,0)"},
                "bgcolor": "white",
                "steps": [
                    {"range": [0, 85], "color": "#fa5252"},
                    {"range": [85, 95], "color": "#fcc419"},
                    {"range": [95, 100], "color": "#228be6"},
                ],
            },
        ))

        theta = 180 - (current_val * 1.8)
        r = 0.45
        x_pivot, y_pivot = 0.5, 0.25
        x_tip = x_pivot + r * math.cos(math.radians(theta))
        y_tip = y_pivot + r * math.sin(math.radians(theta))

        fig.add_shape(type="line", x0=x_pivot, y0=y_pivot, x1=x_tip, y1=y_tip, line=dict(color="black", width=4), xref="paper", yref="paper")
        fig.add_shape(type="circle", x0=x_pivot - 0.02, y0=y_pivot - 0.02, x1=x_pivot + 0.02, y1=y_pivot + 0.02, fillcolor="black", line_color="black", xref="paper", yref="paper")

        fig.update_layout(
            template="zam_light",
            height=160,
            margin=dict(l=25, r=25, t=40, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(x=0.5, y=0.45, text=f"{current_val:.0f}%", showarrow=False, font=dict(size=18, weight="bold"))],
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Análisis de eficiencia de mantenimiento.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


class WorkshopTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", layout_config=None, variant=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context, theme="light"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = data_source.get("categories") or data_source.get("months") or []
        series_list = data_source.get("series", [])
        if not categories or not series_list:
            return self._create_empty_figure("Sin datos", theme=theme)

        fig = go.Figure()

        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", f"Serie {idx}")
            s_data = serie.get("data", [])
            s_color = serie.get("color", DesignSystem.BRAND[5])
            s_type = serie.get("type", "bar")
            is_dashed = serie.get("dashed", False) or "Meta" in s_name

            if s_type == "line" or is_dashed:
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    mode="lines+markers",
                    line=dict(color=s_color, width=3, dash="dot" if is_dashed else "solid"),
                    marker=dict(size=6),
                ))
            else:
                fig.add_trace(go.Bar(x=categories, y=s_data, name=s_name, marker_color=s_color))

        fig.update_layout(
            template="zam_light" if theme == "light" else "zam_dark",
            barmode="group",
            height=350,
            margin=dict(t=40, b=50, l=40, r=20),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            hovermode="x unified",
        )
        return fig

    def render_detail(self, data_context):
        return None


class WorkshopDonutChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-pie", color="indigo", layout_config=None, variant=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context, theme="light"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        fig = ChartEngine.render_donut(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def render_detail(self, data_context):
        return None


class WorkshopHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", layout_config=None, variant=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context, theme="light"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        fig = ChartEngine.render_horizontal_bar(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def render_detail(self, data_context):
        return None


class WorkshopBarChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", layout_config=None, variant=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context, theme="light"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])
        if not categories:
            return self._create_empty_figure("Sin categorías", theme=theme)

        fig = go.Figure()

        for serie in series_list:
            s_name = serie.get("name", "Valor")
            s_data = serie.get("data", [])
            s_color = serie.get("color", self.hex_color)
            fig.add_trace(go.Bar(x=categories, y=s_data, name=s_name, marker_color=s_color))

        fig.update_layout(
            template="zam_light" if theme == "light" else "zam_dark",
            height=350,
            margin=dict(t=30, b=40, l=40, r=20),
            showlegend=len(series_list) > 1,
        )
        return fig

    def render_detail(self, data_context):
        return None


class WorkshopComboChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", layout_config=None, variant=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context, theme="light"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])
        if not categories or not series_list:
            return self._create_empty_figure("Sin datos", theme=theme)

        fig = go.Figure()

        for serie in series_list:
            s_name = serie.get("name", "")
            s_data = serie.get("data", [])
            s_color = serie.get("color", self.hex_color)
            s_type = serie.get("type", "bar")

            if s_type == "line":
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    mode="lines+markers",
                    line=dict(color=s_color, width=3),
                    marker=dict(size=6),
                    yaxis="y2",
                ))
            else:
                fig.add_trace(go.Bar(x=categories, y=s_data, name=s_name, marker_color=s_color))

        fig.update_layout(
            template="zam_light" if theme == "light" else "zam_dark",
            height=350,
            margin=dict(t=30, b=40, l=40, r=40),
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
            hovermode="x unified",
            yaxis=dict(title=""),
            yaxis2=dict(title="", overlaying="y", side="right"),
        )
        return fig

    def render_detail(self, data_context):
        return None


class WorkshopTableStrategy:
    def __init__(self, screen_id, table_key, variant=None):
        self.screen_id = screen_id
        self.table_key = table_key
        self.variant = variant

    def _resolve_table_data(self, data_context):
        from services.data_manager import data_manager

        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {}) # type: ignore
        inject_paths = screen_config.get("inject_paths", {})

        if self.variant:
            lookup_key = f"{self.table_key}_{self.variant}"
            path = inject_paths.get(lookup_key) or inject_paths.get(self.table_key)
        else:
            path = inject_paths.get(self.table_key)

        if not path:
            return None
        return safe_get(data_context, path)

    def render(self, data_context, **kwargs):
        node = self._resolve_table_data(data_context)
        if not node:
            return dmc.Text("Sin datos de tabla", c="dimmed", ta="center", py="xl") # type: ignore

        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])
        summary = node.get("summary", {})
        total_row = data_source.get("total_row")

        if not headers or not rows:
            return dmc.Text("Sin datos", c="dimmed", ta="center", py="xl") # type: ignore

        table_body = []
        for row in rows[:50]:
            table_body.append(dmc.TableTr([dmc.TableTd(str(cell), style={"fontSize": "11px"}) for cell in row]))

        if summary:
            table_body.append(dmc.TableTr([
                dmc.TableTd(
                    str(summary.get(h.lower().replace(" ", "_"), "---")),
                    style={"fontSize": "11px", "fontWeight": "bold", "backgroundColor": DesignSystem.SLATE[0]},
                )
                for h in headers
            ]))
        elif total_row:
            table_body.append(dmc.TableTr([
                dmc.TableTd(
                    str(cell),
                    style={"fontSize": "11px", "fontWeight": "bold", "backgroundColor": "#f8f9fa"},
                )
                for cell in total_row
            ]))

        return dmc.Table(
            [
                dmc.TableThead(dmc.TableTr([
                    dmc.TableTh(
                        h,
                        style={"fontSize": "11px", "fontWeight": "bold", "backgroundColor": DesignSystem.SLATE[0]},
                    )
                    for h in headers
                ])),
                dmc.TableTbody(table_body),
            ],
            striped=True, # type: ignore
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
        )
