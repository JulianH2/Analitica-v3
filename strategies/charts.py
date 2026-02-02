import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem

class MainTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-area-line", layout_config=None):
        super().__init__(title=title, icon=icon, has_detail=True, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure()

        data_source = node.get("data", node)

        categories = data_source.get("categories") or data_source.get("months") or []
        series_list = data_source.get("series", [])

        if not categories:
            return self._create_empty_figure("Sin eje temporal")

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_type = s.get("type", "bar")
            s_name = s.get("name", f"Serie {idx}")
            s_data = s.get("data", [])
            s_color = s.get("color", DesignSystem.BRAND[5])

            if s_type == "line" or "Meta" in s_name:
                fig.add_trace(go.Scatter(
                    x=categories, y=s_data, name=s_name,
                    mode='lines+markers',
                    line=dict(color=s_color, width=3, dash='dot' if "Meta" in s_name else 'solid')
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories, y=s_data, name=s_name,
                    marker_color=s_color
                ))

        fig.update_layout(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(t=20, b=20, l=40, r=20),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group'
        )
        return fig

class TableChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:table", layout_config=None):
        super().__init__(title=title, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node: return self._create_empty_figure()

        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])

        if not headers:
            return self._create_empty_figure("Sin estructura de tabla")

        cols = list(map(list, zip(*rows))) if rows else []

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f"<b>{h}</b>" for h in headers],
                fill_color=DesignSystem.SLATE[1],
                align='left',
                font=dict(color=DesignSystem.SLATE[7], size=12),
                height=30
            ),
            cells=dict(
                values=cols,
                fill_color='white',
                align='left',
                font=dict(color=DesignSystem.SLATE[6], size=12),
                height=25,
                line_color=DesignSystem.SLATE[2]
            )
        )])

        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=None,
            paper_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig