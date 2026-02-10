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

        if not node:
            return {
                "title": self.title,
                "main_value": "---",
                "icon": self.icon,
                "color": self.color,
                "raw_data": []
            }

        config = node.copy()

        val = config.get("value")
        if val is None: val = config.get("current_value")
        if val is None: val = config.get("valor", 0)

        if "value_formatted" not in config:
            fmt = self.layout.get("value_format", "abbreviated")
            config["value_formatted"] = f"{val:,.2f}%" if self.is_pct else format_value(val, "$", format_type=fmt)

        meta = config.get("target") or config.get("target_value") or config.get("meta", 0)
        trend = config.get("trend_percent")
        if trend is None and meta and meta > 0:
             trend = ((val - meta) / meta) * 100
             config["trend"] = trend

        config.update({
            "title": self.title,
            "icon": self.icon,
            "color": self.color,
            "inverse": self.inverse,
            "value": config.get("value_formatted", "---"),
            "main_value": config.get("value_formatted", "---"),
            "status_color": config.get("status_color") or self.color
        })

        return config

    def render_detail(self, data_context):
        return dmc.Text("Detalle no disponible", c="dimmed")

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

        if not node:
            return {
                "title": self.title,
                "value": "---",
                "icon": self.icon,
                "color": self.color
            }

        val = node.get("value") or node.get("current_value") or node.get("valor", 0)
        formatted = node.get("value_formatted")

        if not formatted:
             formatted = format_value(val, "$", format_type="abbreviated")

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
        colors = data_source.get("colors", [])
        total = data_source.get("total_formatted", "")

        if not labels or not values: 
            return self._create_empty_figure()
        
        if not colors:
            colors = [DesignSystem.COLOR_MAP.get(self.color_map.get(l, "gray"), DesignSystem.SLATE[5]) for l in labels]
        
        fig_height = self.layout.get("height", 260)
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.65,
            marker=dict(colors=colors, line=dict(color='white', width=2)), 
            textinfo='percent',
            textposition='auto',
            textfont=dict(size=11, color='white'),
            hovertemplate='<b>%{label}</b><br>%{percent}<br>%{value}<extra></extra>'
        )])

        if total:
            font_size = 16 if fig_height > 240 else 14 if fig_height > 200 else 12
            fig.add_annotation(
                text=total,
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=font_size, color=DesignSystem.SLATE[7]),
                xref="paper",
                yref="paper"
            )

        legend_y_pos = 0.5
        legend_x_pos = 1.05
        
        fig.update_layout(
            paper_bgcolor=DesignSystem.TRANSPARENT, 
            plot_bgcolor=DesignSystem.TRANSPARENT, 
            height=fig_height - 40,
            margin=dict(t=10, b=10, l=10, r=80),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=legend_y_pos,
                xanchor="left",
                x=legend_x_pos,
                font=dict(size=10),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor=DesignSystem.SLATE[2],
                borderwidth=1
            ),
            autosize=True
        )
        return fig