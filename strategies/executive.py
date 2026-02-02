import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem
from utils.helpers import format_value

class ExecutiveKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, icon, color, is_pct=False, has_detail=True, layout_config=None, inverse=False):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.kpi_key = kpi_key
        self.is_pct = is_pct
        self.inverse = inverse

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)

        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        config = node.copy()

        val = config.get("value")
        if val is None: val = config.get("current_value")
        if val is None: val = config.get("valor", 0)

        if "value_formatted" not in config:
            fmt = self.layout.get("value_format", "abbreviated")
            config["value_formatted"] = f"{val:,.2f}%" if self.is_pct else format_value(val, "$", format_type=fmt) # type: ignore

        meta = config.get("target") or config.get("target_value") or config.get("meta", 0)
        trend = config.get("trend_percent")
        if trend is None and meta and meta > 0: # type: ignore
             trend = ((val - meta) / meta) * 100 # type: ignore
             config["trend"] = trend # type: ignore

        config.update({
            "title": self.title,
            "icon": self.icon,
            "color": self.color,
            "inverse": self.inverse,
            "value": config["value_formatted"],
            "main_value": config["value_formatted"]
        }) # type: ignore

        return config

    def render_detail(self, data_context):
        return dmc.Text("Detalle no disponible", c="dimmed") # type: ignore

class ExecutiveMiniKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, color, icon, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=False, layout_config=layout_config)
        self.screen_id = screen_id
        self.kpi_key = kpi_key

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)

        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        val = node.get("value") or node.get("current_value") or node.get("valor", 0)
        formatted = node.get("value_formatted")

        if not formatted:
             formatted = format_value(val, "$", format_type="abbreviated") # type: ignore

        return {
            "title": self.title,
            "value": formatted,
            "icon": self.icon,
            "color": self.color
        }

    def render_detail(self, data_context):
        return None

class ExecutiveDonutStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-pie", color_map=None, has_detail=True, layout_config=None):
        super().__init__(title=title, has_detail=has_detail, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key
        self.color_map = color_map or {}

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key) or {}
        data_source = node.get("data", node)
        labels = data_source.get("labels", [])
        values = data_source.get("values", [])
        if not labels or not values: return self._create_empty_figure()
        hex_colors = [DesignSystem.COLOR_MAP.get(self.color_map.get(l, "gray"), DesignSystem.SLATE[5]) for l in labels]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.7, marker=dict(colors=hex_colors), textinfo='percent', textposition='inside')])
        fig.update_layout(paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT, height=210, margin=dict(t=20, b=20, l=20, r=20), showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0))
        return fig