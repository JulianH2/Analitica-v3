from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from settings.theme import DesignSystem
from utils.helpers import safe_get

class KPIStrategy(ABC):
    def __init__(self, screen_id, key, title="", color="blue", icon="", has_detail=True, variant=None, layout_config=None):
        self.screen_id = screen_id
        self.key = key
        self.title = title
        self.color = color
        self.icon = icon
        self.has_detail = has_detail
        self.variant = variant
        self.hex_color = DesignSystem.COLOR_MAP.get(color, DesignSystem.BRAND[5])

        self.layout = {"height": 165, "span": 4, "value_format": "abbreviated"}
        if layout_config:
            self.layout.update(layout_config)

    def set_layout(self, layout_config):
        if layout_config:
            self.layout.update(layout_config)

    @abstractmethod
    def get_card_config(self, ctx: Dict[str, Any]) -> dict:
        pass

    def render(self, ctx: Dict[str, Any], mode: str = "dashboard", theme: str = "dark") -> Any:
        if mode in ["analysis", "analyst"]:
            return self._render_detailed_view(ctx, theme)
        return self._render_standard_view(ctx, theme)

    def _render_standard_view(self, ctx: Dict[str, Any], theme: str) -> Any:
        return None

    def _render_detailed_view(self, ctx: Dict[str, Any], theme: str) -> Any:
        return None

    def get_figure(self, ctx: Dict[str, Any], theme: str = "dark") -> Optional[Any]:
        return None

    def _resolve_kpi_data(self, ctx: Dict[str, Any], screen_id: str, key: str, variant: Optional[str] = None) -> Optional[Dict]:
        try:
            from services.data_manager import data_manager

            screen_map = data_manager.SCREEN_MAP or {}
            screen_config = screen_map.get(screen_id) or {}
            inject_paths = screen_config.get("inject_paths") or {}

            variant_to_use = variant or self.variant

            if variant_to_use:
                lookup_key = f"{key}_{variant_to_use}"
                path = inject_paths.get(lookup_key) or inject_paths.get(key)
            else:
                path = inject_paths.get(key)

            if not path:
                return None

            return safe_get(ctx, path)

        except Exception as e:
            print(f"⚠️ Error en _resolve_kpi_data para {key}: {e}")
            return None

    def _resolve_chart_data(self, ctx: Dict[str, Any], screen_id: str, key: str, variant: Optional[str] = None) -> Optional[Dict]:
        try:
            from services.data_manager import data_manager

            screen_map = data_manager.SCREEN_MAP or {}
            screen_config = screen_map.get(screen_id) or {}
            inject_paths = screen_config.get("inject_paths") or {}

            variant_to_use = variant or self.variant

            if variant_to_use:
                lookup_key = f"{key}_{variant_to_use}"
                path = inject_paths.get(lookup_key) or inject_paths.get(key)
            else:
                path = inject_paths.get(key)

            if not path:
                return None

            return safe_get(ctx, path)

        except Exception as e:
            print(f"⚠️ Error en _resolve_chart_data para {key}: {e}")
            return None

    def _create_empty_figure(self, message: str = "Sin datos", theme: str = "dark"):
        import plotly.graph_objects as go

        template = "plotly_dark" if theme == "dark" else "plotly"

        fig = go.Figure()
        fig.update_layout(
            template=template,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            annotations=[
                dict(
                    text=message,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="gray"),
                )
            ],
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig