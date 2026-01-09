import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem

COLOR_MAP = {
    "indigo": DesignSystem.BRAND[5],
    "green": DesignSystem.SUCCESS[5],
    "red": DesignSystem.DANGER[5],
    "yellow": DesignSystem.WARNING[5],
    "blue": DesignSystem.BRAND[5],
    "teal": DesignSystem.SUCCESS[5],
    "orange": DesignSystem.WARNING[5],
    "gray": DesignSystem.SLATE[5],
    "cyan": DesignSystem.BRAND[3],
    "lime": DesignSystem.SUCCESS[3]
}

class ExecutiveKPIStrategy(KPIStrategy):
    """Estrategia para los 3 KPIs grandes (Ingresos, Costos, Margen)"""
    def __init__(self, section, sub_section, key, title, icon, color, is_pct=False):
        self.section, self.sub_section, self.key = section, sub_section, key
        self.title, self.icon, self.color, self.is_pct = title, icon, color, is_pct

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
    
    def render_detail(self, data_context): 
        return dmc.Text("Detalle histórico...", c="gray")
    
class ExecutiveMiniKPIStrategy(KPIStrategy):
    """Estrategia para los bloques pequeños"""
    def __init__(self, section, sub_section, key, title, color, icon, prefix=""):
        self.section, self.sub_section, self.key = section, sub_section, key
        self.title, self.color, self.icon, self.prefix = title, color, icon, prefix

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
    """Estrategia para las donas de Cartera y Proveedores"""
    def __init__(self, title, section, sub_section, color_map):
        self.title, self.section, self.sub_section = title, section, sub_section
        self.color_map = color_map

    def get_card_config(self, data_context): 
        return {"title": self.title, "icon": "tabler:chart-pie"} 
    
    def get_figure(self, data_context):
        ds = data_context["administracion"][self.sub_section]["graficas"]["mix"]
        
        hex_colors = []
        for label in ds["labels"]:
            c_name = self.color_map.get(label, "gray")
            hex_colors.append(COLOR_MAP.get(c_name, DesignSystem.SLATE[5]))

        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], values=ds["values"], hole=.7,
            marker=dict(colors=hex_colors),
            textinfo='none'
        )])
        
        fig.update_layout(
            height=160, 
            margin=dict(l=5, r=5, t=5, b=5), 
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
        
    def render_detail(self, data_context): return None