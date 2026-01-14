from typing import Dict, Any, Optional
from .real_data_service import RealDataService

class DataManager:
    _instance: Optional['DataManager'] = None
    service: RealDataService
    cache: Dict[str, Any]

    def __new__(cls) -> 'DataManager':
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.service = RealDataService()
            cls._instance.cache = {}
        return cls._instance

    def get_data(self, section: Optional[str] = None) -> Dict[str, Any]:
        if not self.cache:
            self.cache = self.service.get_full_dashboard_data()
        
        if section and section in self.cache:
            return {section: self.cache[section]}
            
        return self.cache

    def clear_cache(self) -> None:
        self.cache = {}

data_manager = DataManager()