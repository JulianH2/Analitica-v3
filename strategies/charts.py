from datetime import datetime
import plotly.graph_objects as go
from design_system import ChartColors, Colors, Typography
from .base_strategy import KPIStrategy

def get_current_month():
    return datetime.now().month

class MainTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-area-line", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context, theme="light"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        all_categories = data_source.get("categories") or data_source.get("months") or []
        series_list = data_source.get("series", [])
        if not all_categories:
            return self._create_empty_figure("Sin eje temporal", theme=theme)

        current_month = get_current_month()
        categories = all_categories[:current_month]
        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_type = s.get("type", "bar")
            s_name = s.get("name", f"Serie {idx}")
            s_data = s.get("data", [])[:current_month]
            s_color = s.get("color", ChartColors.DEFAULT[idx % len(ChartColors.DEFAULT)])

            if s_type == "line" or "Meta" in s_name:
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    mode="lines+markers",
                    line=dict(color=s_color, width=3, dash="dot" if "Meta" in s_name else "solid"),
                    marker=dict(size=6),
                ))
            else:
                fig.add_trace(go.Bar(x=categories, y=s_data, name=s_name, marker_color=s_color))

        height_val = self.layout.get("height", 350)
        plotly_height = height_val if isinstance(height_val, int) else None
        template = "zam_dark" if theme == "dark" else "zam_light"

        fig.update_layout(
            template=template,
            margin=dict(t=30, b=40, l=50, r=30),
            height=plotly_height,
            autosize=True,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            barmode="group",
            hovermode="x unified",
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10)),
        )
        return fig


class TableChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:table", has_detail=True, layout_config=None, variant=None):
        super().__init__(title=title, icon=icon, has_detail=has_detail, layout_config=layout_config, variant=variant)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context, theme="light"):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure(theme=theme)

        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])
        if not headers:
            return self._create_empty_figure("Sin estructura de tabla", theme=theme)

        cols = list(map(list, zip(*rows))) if rows else [[] for _ in headers]

        is_dark = theme == "dark"
        header_bg = Colors.BG_DARK_CARD if is_dark else Colors.SLATE[1]
        header_color = Colors.TEXT_DARK if is_dark else Colors.SLATE[7]
        cell_bg = Colors.BG_DARK if is_dark else "white"
        cell_color = Colors.TEXT_DARK if is_dark else Colors.SLATE[6]
        line_color = Colors.SLATE[5] if is_dark else Colors.SLATE[2]

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f"<b>{h}</b>" for h in headers],
                fill_color=header_bg,
                align="left",
                font=dict(color=header_color, size=Typography.TABLE_HEADER),
                height=30,
            ),
            cells=dict(
                values=cols,
                fill_color=cell_bg,
                align="left",
                font=dict(color=cell_color, size=Typography.TABLE),
                height=25,
                line_color=line_color,
            ),
        )])

        template = "zam_dark" if theme == "dark" else "zam_light"
        fig.update_layout(
            template=template,
            margin=dict(t=10, b=10, l=10, r=10),
            height=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig
