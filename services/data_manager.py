from services.real_data_service import RealDataService

class DataManager:
    _instance = None
    service: RealDataService
    cache = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.service = RealDataService()
            cls._instance.cache = None
        return cls._instance

    def get_data(self):
        if self.cache is None:
            self.cache = self.service.get_full_dashboard_data()
        return self.cache

    def refresh_data(self):
        self.cache = self.service.get_full_dashboard_data()
        return self.cache