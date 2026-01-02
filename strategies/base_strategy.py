from abc import ABC, abstractmethod

class KPIStrategy(ABC):
    @abstractmethod
    def get_card_config(self, data_context):
        pass

    @abstractmethod
    def render_detail(self, data_context):
        pass