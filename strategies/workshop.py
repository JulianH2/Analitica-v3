import math
import dash_mantine_components as dmc
import plotly.graph_objects as go
from design_system import DesignSystem, SemanticColors
from utils.helpers import safe_get
from .base_strategy import KPIStrategy
from .chart_engine import ChartEngine


class WorkshopKPIStrategy(KPIStrategy):
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

        config = {
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

        if node.get("percentage_of_total"):
            config["percentage_of_total"] = node.get("percentage_of_total")

        return config

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica de mantenimiento.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


class WorkshopGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:gauge", has_detail=True, variant=None, use_needle=False, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)
        self.use_needle = use_needle
        self.gauge_params = {
            "range_max_mult": 1.15,
            "threshold_width": 5,
            "threshold_color": DesignSystem.WARNING[5],
            "exceed_color": DesignSystem.INFO[5],
            "bg_color": "rgba(148, 163, 184, 0.05)",
            "font_size": 18,
        }

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        if isinstance(raw_node, (int, float)):
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
            "value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year"),
            "target_formatted": node.get("target_formatted"),
            "meta_text": f"Meta: {node.get('target_formatted')}" if node.get("target_formatted") else "",
            "raw_data": node,
        }

    def get_figure(self, ctx, theme="light"):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)

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

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Análisis de eficiencia de mantenimiento.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


class WorkshopTrendChartStrategy(KPIStrategy):
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

    def get_figure(self, ctx, theme="light"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_trend(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopDonutChartStrategy(KPIStrategy):
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

    def get_figure(self, ctx, theme="light"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_donut(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopHorizontalBarStrategy(KPIStrategy):
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

    def get_figure(self, ctx, theme="light"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_horizontal_bar(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopBarChartStrategy(KPIStrategy):
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

    def get_figure(self, ctx, theme="light"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_bar_chart(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopComboChartStrategy(KPIStrategy):
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

    def get_figure(self, ctx, theme="light"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_combo_chart(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopTableStrategy:
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

        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])
        
        return headers, rows

    def get_card_config(self, ctx):
        headers, rows = self._get_data(ctx)
        
        export_data = []
        if headers and rows:
            for row in rows:
                if isinstance(row, (list, tuple)):
                    row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
                else:
                    row_dict = row
                export_data.append(row_dict)
        
        return {
            "title": self.title or self.key,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": True,
            "is_chart": False,
            "main_value": f"{len(rows)} registros" if rows else "0",
            "raw_data": export_data,
        }

    def render(self, ctx, mode="dashboard", theme="light"):
        node = self._resolve_table_data(ctx)
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
            striped="odd",
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
        )

    def _resolve_table_data(self, ctx):
        from services.data_manager import data_manager

        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {})
        inject_paths = screen_config.get("inject_paths", {})

        if self.variant:
            lookup_key = f"{self.key}_{self.variant}"
            path = inject_paths.get(lookup_key) or inject_paths.get(self.key)
        else:
            path = inject_paths.get(self.key)

        if not path:
            return None
        return safe_get(ctx, path)