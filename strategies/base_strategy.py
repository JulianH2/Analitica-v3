from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from settings.theme import DesignSystem

class KPIStrategy(ABC):
    def __init__(self, title="", color="indigo", icon="tabler:chart-bar", has_detail=True, layout_config=None):
        self.title, self.color, self.icon, self.has_detail = title, color, icon, has_detail
        self.hex_color = DesignSystem.COLOR_MAP.get(color, DesignSystem.BRAND[5])
        
        self.layout = {
            "height": 165,
            "span": 2,
            "value_format": "abbreviated" 
        }
        if layout_config: self.layout.update(layout_config)

    @abstractmethod
    def get_card_config(self, data_context: Dict[str, Any]) -> dict:
        pass

    @abstractmethod
    def render_detail(self, data_context: Dict[str, Any]) -> Any:
        pass

    def get_figure(self, data_context: Dict[str, Any]) -> Optional[Any]:
        return None