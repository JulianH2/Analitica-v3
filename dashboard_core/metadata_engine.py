import json
import os
from django.conf import settings

class MetadataEngine:
    # Singleton para eficiencia (lee los archivos solo una vez o cuando se necesita)
    _instance = None
    base_path: str
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetadataEngine, cls).__new__(cls)
            # Asume que la carpeta 'metadata' está en la raíz del proyecto Django
            cls._instance.base_path = os.path.join(settings.BASE_DIR, 'metadata')
        return cls._instance

    def _load_json(self, path):
        """Helper para cargar JSON de forma segura"""
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando metadatos en {path}: {e}")
            return {}

    def get_context(self, tenant_db=None):
        """
        Retorna el contexto completo (Tablas + Métricas + Modifiers).
        Fusiona 'defaults' con 'tenants/{db}' si existe.
        """
        # 1. Cargar la configuración BASE (Defaults)
        defaults_path = os.path.join(self.base_path, 'defaults')
        tables = self._load_json(os.path.join(defaults_path, 'tables.json'))
        metrics = self._load_json(os.path.join(defaults_path, 'metrics.json'))
        modifiers = self._load_json(os.path.join(defaults_path, 'modifiers.json'))

        # 2. Aplicar Overrides del Cliente (Si aplica)
        if tenant_db:
            tenant_path = os.path.join(self.base_path, 'tenants', tenant_db)
            
            # Sobreescribir Métricas (KPIs personalizados)
            tenant_metrics = self._load_json(os.path.join(tenant_path, 'metrics.json'))
            if tenant_metrics:
                metrics.update(tenant_metrics)
            
            # Sobreescribir Tablas (Si el cliente tiene tablas extra)
            tenant_tables = self._load_json(os.path.join(tenant_path, 'tables.json'))
            if tenant_tables:
                tables.update(tenant_tables)
                
            # Sobreescribir Modifiers (Filtros especiales)
            tenant_modifiers = self._load_json(os.path.join(tenant_path, 'modifiers.json'))
            if tenant_modifiers:
                modifiers.update(tenant_modifiers)

        return {
            "tables": tables,
            "metrics": metrics,
            "modifiers": modifiers
        }