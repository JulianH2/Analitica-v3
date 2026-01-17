from .metadata_engine import MetadataEngine

class SmartQueryBuilder:
    def __init__(self, tenant_db=None):
        self.meta = MetadataEngine().get_context(tenant_db)

    def build_kpi_query(self, kpi_key):
        """
        Construye la consulta SQL para un KPI.
        """
        # 1. Obtener el bloque de métricas
        metrics_block = self.meta.get('metrics', {})
        
        # Si por error 'metrics' se cargó como string (pasa si el JSON está mal)
        if isinstance(metrics_block, str):
            print(f"❌ ERROR: El archivo metrics.json se cargó como texto, no como objeto.")
            return None

        kpi = metrics_block.get(kpi_key)
        
        # Validar que el KPI exista y sea un diccionario
        if not kpi or not isinstance(kpi, dict):
            print(f"⚠️ KPI '{kpi_key}' no encontrado o no es un objeto válido.")
            return None

        recipe = kpi.get('recipe', {})
        if not isinstance(recipe, dict):
            print(f"❌ ERROR: 'recipe' en {kpi_key} debe ser un objeto {{...}}")
            return None

        # 1. Validar existencia
        # Nota: Asegúrate que tu MetadataEngine devuelva 'kpis' o 'metrics'. 
        # Si usas 'metrics.json', la llave suele ser 'metrics' o 'kpis' según tu defaults.py
        kpi = self.meta.get('metrics', {}).get(kpi_key) or self.meta.get('kpis', {}).get(kpi_key)
        
        if not kpi:
            print(f"⚠️ KPI '{kpi_key}' no encontrado en metadatos.")
            return None

        recipe = kpi.get('recipe', {})
        
        # 2. Construir Query Base
        # Asume que recipe tiene 'table' y 'column'
        table = recipe.get('table')
        column = recipe.get('column')
        aggregation = recipe.get('aggregation', 'SUM')
        
        if not table or not column:
             return None

        query = f"SELECT {aggregation}({table}.{column}) FROM {table}"
        
        # 3. Filtros Simplificados (Sin joins mágicos)
        wheres = []
        
        # Filtros por defecto (ej: anio_actual)
        if 'default_filters' in recipe:
            for f in recipe['default_filters']:
                if f == 'anio_actual':
                    # Intenta leer 'date_column' del KPI, o fallback a 'fecha_consulta'
                    date_col = recipe.get('date_column', 'fecha_consulta')
                    wheres.append(f"YEAR({table}.{date_col}) = YEAR(GETDATE())")
                
                # Agrega aquí más lógica si tienes otros filtros (ej: 'mes_actual')
        
        if wheres:
            query += " WHERE " + " AND ".join(wheres)
            
        return {
            "query": query,
            "name": kpi.get('name'),
            "format": kpi.get('format')
        }