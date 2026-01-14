import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem

class ExecutiveKPIStrategy(KPIStrategy):
    def __init__(self, section, sub_section, key, title, icon, color, is_pct=False, has_detail=True):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail)
        self.section, self.sub_section, self.key, self.is_pct = section, sub_section, key, is_pct

    def get_card_config(self, data_context):
        node = data_context[self.section][self.sub_section]["indicadores"][self.key]
        val = node["valor"]
        meta = node.get("meta", 0)
        trend = ((val - meta) / meta * 100) if meta > 0 else 0
        return {
            "title": self.title,
            "value": f"{val:,.2f}%" if self.is_pct else f"${val/1e6:.2f}M",
            "meta_text": f"Meta: ${meta/1e6:.1f}M" if meta > 0 else "",
            "trend": trend,
            "icon": self.icon,
            "color": self.color
        }
    def render_detail(self, data_context): return dmc.Text("Detalle histórico...", c="gray")
    
class ExecutiveMiniKPIStrategy(KPIStrategy):
    def __init__(self, section, sub_section, key, title, color, icon, prefix="", has_detail=False):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail)
        self.section, self.sub_section, self.key, self.prefix = section, sub_section, key, prefix

    def get_card_config(self, data_context):
        parent = data_context[self.section][self.sub_section]
        node = parent.get("indicadores", {}).get(self.key) or parent.get("promedios", {}).get(self.key)
        val = node["valor"] if node else 0
        return {
            "title": self.title,
            "value": f"{self.prefix}{val:,.0f}" if val > 100 else f"{self.prefix}{val:,.2f}",
            "color": self.color,
            "icon": self.icon,
            "is_simple": True
        }
    def render_detail(self, data_context): return None

class ExecutiveDonutStrategy(KPIStrategy):
    def __init__(self, title, section, sub_section, color_map, has_detail=True):
        super().__init__(title=title, has_detail=has_detail, icon="tabler:chart-pie")
        self.section, self.sub_section, self.color_map = section, sub_section, color_map

    def get_card_config(self, data_context): return {"title": self.title, "icon": self.icon} 
    def get_figure(self, data_context):
        ds = data_context["administracion"][self.sub_section]["graficas"]["mix"]
        # Usamos COLOR_MAP de theme.py para evitar inconsistencias
        hex_colors = [DesignSystem.COLOR_MAP.get(self.color_map.get(label, "gray"), DesignSystem.SLATE[5]) for label in ds["labels"]]
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.7, marker=dict(colors=hex_colors), textinfo='none')])
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None