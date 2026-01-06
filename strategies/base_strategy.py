from abc import ABC, abstractmethod
from typing import Any

class KPIStrategy(ABC):
    @abstractmethod
    def get_card_config(self, data_context) -> dict:
        pass

    @abstractmethod
    def render_detail(self, data_context)-> Any:
        pass