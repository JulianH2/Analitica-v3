from .metadata_engine import MetadataEngine
import datetime

class SmartQueryBuilder:
    def __init__(self, tenant_db=None):
        self.meta = MetadataEngine().get_context(tenant_db)
        self.tables = self.meta.get('tables', {})
        self.metrics = self.meta.get('metrics', {})

    def _find_join_path(self, start_table_alias, target_dimension_key, visited=None):
        """
        Algoritmo BFS (Breadth-First Search) para encontrar el camino de JOINS
        desde la tabla origen hasta la dimensión deseada.
        Retorna: Lista de tuplas [(alias_destino, definición_join), ...]
        """
        if visited is None: visited = set()
        visited.add(start_table_alias)

        start_def = self.tables.get(start_table_alias)
        if not start_def: return None

        # 1. Búsqueda directa: ¿La tabla actual tiene el join que busco?
        joins = start_def.get('joins', {})
        if target_dimension_key in joins:
            return [(joins[target_dimension_key]['target_table'], joins[target_dimension_key])]

        # 2. Búsqueda recursiva: Preguntar a los vecinos
        for join_key, join_def in joins.items():
            neighbor_alias = join_def.get('target_table')
            if neighbor_alias not in visited:
                path = self._find_join_path(neighbor_alias, target_dimension_key, visited)
                if path:
                    # Camino encontrado! Retornamos: Este salto + el resto del camino
                    return [(neighbor_alias, join_def)] + path
        
        return None

    def build_series_query(self, kpi_key):
        """Construye consulta agrupada por MES (Series de Tiempo)."""
        kpi = self.metrics.get(kpi_key)
        if not kpi: return {"error": "KPI not found"}

        recipe = kpi.get('recipe', {})
        table_alias = recipe.get('table')
        column = recipe.get('column')
        aggregation = recipe.get('aggregation', 'SUM')
        time_modifier = recipe.get('time_modifier')

        table_def = self.tables.get(table_alias)
        if not table_def: return {"error": f"Tabla {table_alias} no encontrada"}

        date_col = table_def.get('date_column')
        if not date_col: return {"error": "Tabla sin columna de fecha"}

        query = f"SELECT MONTH({table_alias}.{date_col}) as period, {aggregation}({table_alias}.{column}) as value FROM {table_def['table_name']} as {table_alias}"
        wheres = []

        if time_modifier == 'previous_year':
            wheres.append(f"YEAR({table_alias}.{date_col}) = YEAR(GETDATE()) - 1")
        else:
            wheres.append(f"YEAR({table_alias}.{date_col}) = YEAR(GETDATE())")

        if wheres: query += " WHERE " + " AND ".join(wheres)
        query += f" GROUP BY MONTH({table_alias}.{date_col}) ORDER BY period"

        return {"type": "sql", "query": query}

    def build_categorical_query(self, kpi_key, dimension_key):
        """Construye query con JOINS automáticos (Drill-Down)."""
        kpi = self.metrics.get(kpi_key)
        if not kpi: return {"error": f"KPI {kpi_key} no encontrado"}

        recipe = kpi.get('recipe', {})
        fact_alias = recipe.get('table')
        fact_col = recipe.get('column')
        agg = recipe.get('aggregation', 'SUM')
        fact_def = self.tables.get(fact_alias)
        
        if not fact_def: return {"error": f"Tabla base {fact_alias} no existe"}

        # --- AUTO-DISCOVERY DE JOINS (BFS) ---
        join_path = self._find_join_path(fact_alias, dimension_key)
        
        if not join_path:
             return {"error": f"No se encontró ruta de relación entre '{fact_alias}' y '{dimension_key}'"}

        joins_sql = ""
        current_alias = fact_alias
        
        # El último elemento es la dimensión objetivo
        target_dim_alias, _ = join_path[-1] 
        target_dim_def = self.tables.get(target_dim_alias)
        if not target_dim_def:
            return {"error": f"Definición de tabla para '{target_dim_alias}' no encontrada"}
        label_col = target_dim_def.get('label_column', 'id')

        for next_alias, join_def in join_path:
            next_table = self.tables.get(next_alias)
            if not next_table:
                return {"error": f"Definición de tabla para '{next_alias}' no encontrada"}
            table_name = next_table.get('table_name')
            join_type = join_def.get('type', 'INNER')
            join_on = join_def.get('on')
            
            joins_sql += f" {join_type} JOIN {table_name} as {next_alias} ON {join_on}"

        # Query Final SIN TOP 10
        query = f"""
            SELECT {target_dim_alias}.{label_col} as label, 
                   {agg}({fact_alias}.{fact_col}) as value
            FROM {fact_def['table_name']} as {fact_alias}
            {joins_sql}
            WHERE YEAR({fact_alias}.{fact_def['date_column']}) = YEAR(GETDATE())
            GROUP BY {target_dim_alias}.{label_col}
            ORDER BY value DESC
        """
        
        return {"type": "sql", "query": query}