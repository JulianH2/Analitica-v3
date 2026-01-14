from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from settings.theme import DesignSystem

class KPIStrategy(ABC):
    def __init__(
        self, 
        title: str = "", 
        color: str = "indigo", 
        icon: str = "tabler:chart-bar", 
        has_detail: bool = True
    ):
        self.title = title
        self.color = color
        self.icon = icon
        self.has_detail = has_detail
        self.hex_color = DesignSystem.COLOR_MAP.get(color, DesignSystem.BRAND[5])

    @abstractmethod
    def get_card_config(self, data_context: Dict[str, Any]) -> dict:
        pass

    @abstractmethod
    def render_detail(self, data_context: Dict[str, Any]) -> Any:
        pass

    def get_figure(self, data_context: Dict[str, Any]) -> Optional[Any]:
        return None