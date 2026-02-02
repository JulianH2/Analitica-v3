import json
import os
from django.conf import settings

class MetadataEngine:
    _instance = None
    base_path: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetadataEngine, cls).__new__(cls)
            cls._instance.base_path = os.path.join(settings.BASE_DIR, 'metadata')
        return cls._instance

    def _load_json(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando metadatos en {path}: {e}")
            return {}

    def get_context(self, tenant_db=None):
        defaults_path = os.path.join(self.base_path, 'defaults')
        tables = self._load_json(os.path.join(defaults_path, 'tables.json'))
        metrics = self._load_json(os.path.join(defaults_path, 'metrics.json'))
        modifiers = self._load_json(os.path.join(defaults_path, 'modifiers.json'))

        if tenant_db:
            tenant_path = os.path.join(self.base_path, 'tenants', tenant_db)

            tenant_metrics = self._load_json(os.path.join(tenant_path, 'metrics.json'))
            if tenant_metrics:
                metrics.update(tenant_metrics)

            tenant_tables = self._load_json(os.path.join(tenant_path, 'tables.json'))
            if tenant_tables:
                tables.update(tenant_tables)

            tenant_modifiers = self._load_json(os.path.join(tenant_path, 'modifiers.json'))
            if tenant_modifiers:
                modifiers.update(tenant_modifiers)

        return {
            "tables": tables,
            "metrics": metrics,
            "modifiers": modifiers
        }