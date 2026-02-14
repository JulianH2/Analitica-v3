from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from settings.theme import DesignSystem
from utils.helpers import safe_get

class KPIStrategy(ABC):
    def __init__(self, title="", color="indigo", icon="tabler:chart-bar", has_detail=True, layout_config=None):
        self.title = title
        self.color = color
        self.icon = icon
        self.has_detail = has_detail
        self.hex_color = DesignSystem.COLOR_MAP.get(color, DesignSystem.BRAND[5])
        
        self.layout = {
            "height": 165,
            "span": 2,
            "value_format": "abbreviated" 
        }
        if layout_config: 
            self.layout.update(layout_config)

    @abstractmethod
    def get_card_config(self, data_context: Dict[str, Any]) -> dict:
        pass

    @abstractmethod
    def render_detail(self, data_context: Dict[str, Any]) -> Any:
        pass

    def get_figure(self, data_context: Dict[str, Any]) -> Optional[Any]:
        return None

    def _resolve_kpi_data(self, data_context: Dict[str, Any], screen_id: str, kpi_key: str) -> Optional[Dict]:
        try:
            from services.data_manager import data_manager

            screen_map = data_manager.SCREEN_MAP or {}
            screen_config = screen_map.get(screen_id) or {}

            inject_paths = screen_config.get("inject_paths") or {}
            path = inject_paths.get(kpi_key)

            if not path:
                return None

            return safe_get(data_context, path)

        except Exception as e:
            print(f"⚠️ Error en _resolve_kpi_data para {kpi_key}: {e}")
            return None

    
    def _resolve_chart_data(self, data_context: Dict[str, Any], screen_id: str, chart_key: str) -> Optional[Dict]:
        try:
            from services.data_manager import data_manager

            screen_map = data_manager.SCREEN_MAP or {}
            screen_config = screen_map.get(screen_id) or {}

            inject_paths = screen_config.get("inject_paths") or {}
            path = inject_paths.get(chart_key)

            if not path:
                return None

            return safe_get(data_context, path)

        except Exception as e:
            print(f"⚠️ Error en _resolve_chart_data para {chart_key}: {e}")
            return None

    
    
    def _create_empty_figure(self, message: str = "Sin datos", theme="light"):
        import plotly.graph_objects as go
        
        fig = go.Figure()
        fig.update_layout(
            template="zam_dark" if theme == "dark" else "zam_light", # ✅ USA EL TEMPLATE
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[dict(
                text=message,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="gray")
            )]
        )
        return fig