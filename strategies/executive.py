import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import format_value, safe_get

class ExecutiveKPIStrategy(KPIStrategy):
    def __init__(self, section, sub_section, key, title, icon, color, is_pct=False, has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.section, self.sub_section, self.key, self.is_pct = section, sub_section, key, is_pct

    def get_card_config(self, data_context):
        path = f"{self.section}.{self.sub_section}.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        
        val = node.get("value", 0)
        meta = node.get("target", 0)
        trend = ((val - meta) / meta * 100) if meta > 0 else 0
        fmt = self.layout.get("value_format", "abbreviated")
        
        display_val = f"{val:,.2f}%" if self.is_pct else format_value(val, "$", format_type=fmt)
        meta_text = f"Meta: {format_value(meta, '$')}" if meta > 0 else ""
        
        return {
            "title": self.title,
            "value": display_val,
            "meta_text": meta_text,
            "trend": trend,
            "label_mes": node.get("label_mes"),
            "label_ytd": node.get("label_ytd"),
            "icon": self.icon,
            "color": self.color
        }

    def render_detail(self, data_context): 
        return dmc.Text("Detalle histórico...", c=SemanticColors.TEXT_MUTED) # type: ignore

class ExecutiveMiniKPIStrategy(KPIStrategy):
    def __init__(self, section, sub_section, key, title, color, icon, prefix="", has_detail=False, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.section, self.sub_section, self.key, self.prefix = section, sub_section, key, prefix

    def get_card_config(self, data_context):
        path = f"{self.section}.{self.sub_section}.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        
        val = node.get("value", 0)
        
        l_mes = node.get("label_mes")
        l_ytd = node.get("label_ytd")
        l_title = "Este Mes:"
        
        if not l_mes and "delta" in node:
            delta = node.get("delta", 0)
            if delta != 0:
                l_mes = f"{delta:+.1f}%"
                l_title = "vs Meta:"
        
        display_val = f"{self.prefix}{val:,.0f}" if val > 100 else f"{self.prefix}{val:,.2f}"
        
        return {
            "title": self.title,
            "value": display_val,
            "label_mes": l_mes,
            "label_mes_title": l_title,
            "label_ytd": l_ytd,
            "color": self.color,
            "icon": self.icon,
            "is_simple": True
        }

    def render_detail(self, data_context): return None

class ExecutiveDonutStrategy(KPIStrategy):
    def __init__(self, title, section, sub_section, chart_key, color_map, has_detail=True, layout_config=None):
        super().__init__(title=title, has_detail=has_detail, icon="tabler:chart-pie", layout_config=layout_config)
        self.section, self.sub_section, self.chart_key, self.color_map = section, sub_section, chart_key, color_map

    def get_card_config(self, data_context): return {"title": self.title, "icon": self.icon} 
    
    def get_figure(self, data_context):
        path = f"{self.section}.{self.sub_section}.charts.{self.chart_key}"
        ds = safe_get(data_context, path, {"labels": [], "values": []})
        
        labels = ds.get("labels", [])
        values = ds.get("values", [])
        
        hex_colors = [DesignSystem.COLOR_MAP.get(self.color_map.get(label, "gray"), DesignSystem.SLATE[5]) for label in labels]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.7, 
            marker=dict(colors=hex_colors), 
            textinfo='percent', 
            textposition='inside'
        )])
        
        fig.update_layout(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            height=210, 
            margin=dict(l=10, r=10, t=10, b=30), 
            showlegend=True, 
            legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(size=9))
        )
        return fig

    def render_detail(self, data_context): return None