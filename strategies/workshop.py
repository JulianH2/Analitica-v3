import math
import dash_mantine_components as dmc
import plotly.graph_objects as go
from design_system import DesignSystem, SemanticColors, dmc as _dmc
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
        return dmc.Text("Detalle de métrica de mantenimiento.", size="sm", c=_dmc(SemanticColors.TEXT_MUTED))
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
            "hide_meta": self.use_needle,
            "raw_data": node,
        }
        if self.key == "availability_percent":
            cfg["vs_last_year_formatted"] = None
            cfg["vs_last_year_delta"] = None
            cfg["vs_last_year_delta_formatted"] = None
        return cfg

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

            return self._create_needle_gauge(current_val, target_val, theme)

        fig = ChartEngine.render_gauge(raw_node, theme, self.layout, self.hex_color)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _create_needle_gauge(self, current_val, target_val, theme="light"):
        is_dark = theme == "dark"
        # Colores sólidos por zona (como imagen de referencia)
        if current_val >= 92:
            zone_color = "#2f9e44"
            status_label = "Óptimo"
        elif current_val >= 85:
            zone_color = "#f08c00"
            status_label = "Aceptable"
        else:
            zone_color = "#c92a2a"
            status_label = "Crítico"

        fig = go.Figure(go.Indicator(
            mode="gauge",
            value=current_val,
            gauge={
                "axis": {
                    "range": [0, 100],
                    "visible": True,
                    "tickwidth": 1,
                    "tickcolor": "rgba(120,120,120,0.6)",
                    "tickfont": {"size": 9, "color": "#9ca3af" if is_dark else "#888"},
                    "nticks": 6,
                },
                "bar": {"color": "rgba(0,0,0,0)", "thickness": 0},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 60],  "color": "#c92a2a"},
                    {"range": [60, 75], "color": "#e67700"},
                    {"range": [75, 85], "color": "#f08c00"},
                    {"range": [85, 92], "color": "#94d82d"},
                    {"range": [92, 100],"color": "#2f9e44"},
                ],
                "threshold": {
                    "line": {"color": "#1971c2", "width": 3},
                    "thickness": 0.85,
                    "value": target_val if target_val else 90,
                },
            },
        ))

        # ── Aguja como SVG path shape (layer="above" → encima del arco) ──
        # Pivote en la base del arco (centro-abajo del gauge)
        theta = 180 - (current_val * 1.8)
        r_needle = 0.32          # largo de la aguja
        r_base = 0.025           # ancho de la base
        x_pivot, y_pivot = 0.5, 0.22   # base del arco del gauge

        x_tip = x_pivot + r_needle * math.cos(math.radians(theta))
        y_tip = y_pivot + r_needle * math.sin(math.radians(theta))

        x_bl = x_pivot + r_base * math.cos(math.radians(theta + 90))
        y_bl = y_pivot + r_base * math.sin(math.radians(theta + 90))
        x_br = x_pivot + r_base * math.cos(math.radians(theta - 90))
        y_br = y_pivot + r_base * math.sin(math.radians(theta - 90))

        needle_color = "#e8eaed" if is_dark else "#1a1a2e"
        hub_color = "#1a1a2e" if not is_dark else "#e8eaed"

        # Triángulo de la aguja como shape path (se renderiza ENCIMA del gauge)
        path_str = f"M {x_bl} {y_bl} L {x_tip} {y_tip} L {x_br} {y_br} Z"
        fig.add_shape(
            type="path", path=path_str,
            fillcolor=needle_color, line=dict(color=needle_color, width=0),
            xref="paper", yref="paper", layer="above",
        )

        # Hub central
        fig.add_shape(type="circle",
            x0=x_pivot - 0.028, y0=y_pivot - 0.028,
            x1=x_pivot + 0.028, y1=y_pivot + 0.028,
            fillcolor=needle_color, line=dict(color=hub_color, width=2),
            xref="paper", yref="paper", layer="above")
        fig.add_shape(type="circle",
            x0=x_pivot - 0.010, y0=y_pivot - 0.010,
            x1=x_pivot + 0.010, y1=y_pivot + 0.010,
            fillcolor=hub_color, line=dict(color=hub_color, width=0),
            xref="paper", yref="paper", layer="above")

        height = self.layout.get("height", 280)

        fig.update_layout(
            template="zam_dark" if is_dark else "zam_light",
            height=height,
            margin=dict(l=20, r=20, t=30, b=15),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(x=0.5, y=0.38, text=f"<b>{current_val:.0f}%</b>",
                    showarrow=False,
                    font=dict(size=20, color=zone_color, family="Nexa, Montserrat, sans-serif"),
                    xref="paper", yref="paper"),
                dict(x=0.5, y=0.20, text=status_label,
                    showarrow=False,
                    font=dict(size=10, color="#9ca3af" if is_dark else "#888888"),
                    xref="paper", yref="paper"),
            ],
        )
        return fig

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Análisis de eficiencia de mantenimiento.", size="sm", c=_dmc(SemanticColors.TEXT_MUTED))
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
            return dmc.Text("Sin datos de tabla", c=_dmc("dimmed"), ta="center", py="xl")
        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])
        summary = node.get("summary", {})
        total_row = data_source.get("total_row")

        if not headers or not rows:
            return dmc.Text("Sin datos", c=_dmc("dimmed"), ta="center", py="xl")
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