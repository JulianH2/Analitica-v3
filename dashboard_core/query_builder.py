from .metadata_engine import MetadataEngine
import datetime

class SmartQueryBuilder:
        
    MONTH_MAP = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    
    def __init__(self, tenant_db=None):
        self.meta = MetadataEngine().get_context(tenant_db)
        self.tables = self.meta.get('tables', {})
        self.metrics = self.meta.get('metrics', {})
    
    def _find_join_path(self, start_table_alias, target_dimension_key, visited=None):
        if visited is None: visited = set()
        visited.add(start_table_alias)
    
        start_def = self.tables.get(start_table_alias)
        if not start_def: return None
    
        joins = start_def.get('joins', {})
    
        for join_key, join_def in joins.items():
            if join_def.get('target_table') == target_dimension_key:
                return [(join_def.get('target_table'), join_def)]
    
        if target_dimension_key in joins:
            return [(joins[target_dimension_key]['target_table'], joins[target_dimension_key])]
    
        for join_key, join_def in joins.items():
            neighbor_alias = join_def.get('target_table')
            if neighbor_alias not in visited:
                path = self._find_join_path(neighbor_alias, target_dimension_key, visited)
                if path:
                    return [(neighbor_alias, join_def)] + path
    
        return None
    
    def build_kpi_query(self, kpi_key, filters=None):
        kpi = self.metrics.get(kpi_key)
        if not kpi: return {"error": f"KPI '{kpi_key}' no encontrado"}
    
        if kpi.get('type') == 'derived':
            return {"type": "derived", "formula": kpi.get('formula'), "format": kpi.get('format')}
    
        recipe = kpi.get('recipe', {})
        target_alias = recipe.get('table')
        column = recipe.get('column')
        aggregation = recipe.get('aggregation')
        time_modifier = recipe.get('time_modifier')
    
        fact_alias = target_alias
        fact_def = self.tables.get(fact_alias)
    
        if not fact_def: return {"error": f"Tabla '{fact_alias}' no encontrada"}
    
        joins_sql = ""
        date_col = fact_def.get('date_column')
    
        if not date_col:
            for potential_parent in ["h_viaje", "d_meta_tiempo"]:
                if potential_parent in self.tables and potential_parent != target_alias:
                    path = self._find_join_path(potential_parent, target_alias)
                    if path:
                        fact_alias = potential_parent
                        fact_def = self.tables[fact_alias]
                        date_col = fact_def.get('date_column')
                        for next_alias, join_def in path:
                            t_name = self.tables[next_alias]['table_name']
                            joins_sql += f" {join_def.get('type', 'INNER')} JOIN {t_name} as {next_alias} ON {join_def['on']}"
                        break
                    
        if aggregation == "DISTINCTCOUNT":
            select_expr = f"COUNT(DISTINCT {target_alias}.{column})"
        else:
            select_expr = f"{aggregation}({target_alias}.{column})"
    
        query = f"SELECT {select_expr} as valor FROM {fact_def['table_name']} as {fact_alias} {joins_sql}"
        wheres = []
    
        if date_col:
            base_year = datetime.datetime.now().year
            if filters and filters.get('year'): base_year = int(filters['year'])
            if time_modifier == 'previous_year': base_year -= 1
    
            wheres.append(f"YEAR({fact_alias}.{date_col}) = {base_year}")
    
            if filters and filters.get('month'):
                m_name = filters['month'].lower()
                if m_name in self.MONTH_MAP:
                    m_num = self.MONTH_MAP[m_name]
                    if time_modifier == 'ytd':
                        wheres.append(f"MONTH({fact_alias}.{date_col}) <= {m_num}")
                    elif time_modifier == 'mes_anterior':
                        wheres.append(f"MONTH({fact_alias}.{date_col}) = {12 if m_num == 1 else m_num - 1}")
                    else:
                        wheres.append(f"MONTH({fact_alias}.{date_col}) = {m_num}")
    
        if filters:
            ignore = ['year', 'month']
            for k, v in filters.items():
                if k not in ignore and v not in ["Todas", "Todos", None]:
                    ref = k if "." in k else f"{target_alias}.{k}"
                    val = f"'{v}'" if isinstance(v, str) else v
                    wheres.append(f"{ref} = {val}")
    
        if wheres: query += " WHERE " + " AND ".join(wheres)
    
        return {"type": "sql", "query": query, "format": kpi.get('format')}
    
    def build_series_query(self, kpi_key, filters=None):
        kpi = self.metrics.get(kpi_key)
        if not kpi: return {"error": "KPI not found"}
    
        recipe = kpi.get('recipe', {})
        table_alias = recipe.get('table')
        column = recipe.get('column')
        aggregation = recipe.get('aggregation')
        time_modifier = recipe.get('time_modifier')
    
        table_def = self.tables.get(table_alias)
        if not table_def: return {"error": f"Tabla {table_alias} no encontrada"}
    
        date_col = table_def.get('date_column')
        if not date_col: return {"error": "Tabla sin columna de fecha"}
    
        query = f"SELECT MONTH({table_alias}.{date_col}) as period, {aggregation}({table_alias}.{column}) as value FROM {table_def['table_name']} as {table_alias}"
        wheres = []
    
        target_year = datetime.datetime.now().year
        if filters and filters.get('year'):
            target_year = int(filters['year'])
    
        if time_modifier == 'previous_year':
            target_year -= 1
    
        if filters:
            ignore = ['year', 'month']
            for k, v in filters.items():
                if k not in ignore and v not in ["Todas", "Todos", None]:
                    val = f"'{v}'" if isinstance(v, str) else v
                    wheres.append(f"{table_alias}.{k} = {val}")
    
        wheres.append(f"YEAR({table_alias}.{date_col}) = {target_year}")
    
        if wheres: query += " WHERE " + " AND ".join(wheres)
        query += f" GROUP BY MONTH({table_alias}.{date_col}) ORDER BY period"
    
        return {"type": "sql", "query": query}
    
    def build_categorical_query(self, kpi_key, dimension_key, filters=None):
        kpi = self.metrics.get(kpi_key)
        if not kpi: return {"error": f"KPI {kpi_key} no encontrado"}
    
        recipe = kpi.get('recipe', {})
        fact_alias = recipe.get('table')
        fact_col = recipe.get('column')
        agg = recipe.get('aggregation', 'SUM')
        fact_def = self.tables.get(fact_alias)
    
        if not fact_def: return {"error": f"Tabla base {fact_alias} no existe"}
    
        join_path = self._find_join_path(fact_alias, dimension_key)
    
        if not join_path:
             return {"error": f"No se encontró ruta de relación entre '{fact_alias}' y '{dimension_key}'"}
    
        joins_sql = ""
    
        for next_alias, join_def in join_path:
            next_table = self.tables.get(next_alias)
            if not next_table:
                return {"error": f"Definición de tabla para '{next_alias}' no encontrada"}
            table_name = next_table.get('table_name')
            join_type = join_def.get('type', 'INNER')
            join_on = join_def.get('on')
    
            joins_sql += f" {join_type} JOIN {table_name} as {next_alias} ON {join_on}"
    
        target_dim_alias, _ = join_path[-1]
        target_dim_def = self.tables.get(target_dim_alias)
    
        if not target_dim_def:
            return {"error": f"Definición de tabla objetivo '{target_dim_alias}' no encontrada"}
    
        label_col = target_dim_def.get('label_column', 'id')
    
        wheres = []
        date_col = fact_def.get('date_column')
    
        if date_col:
            target_year = 2025
            if filters and filters.get('year'):
                target_year = int(filters['year'])
    
            wheres.append(f"YEAR({fact_alias}.{date_col}) = {target_year}")
    
            if filters and filters.get('month'):
                m_name = filters['month'].lower()
                if hasattr(self, 'MONTH_MAP') and m_name in self.MONTH_MAP:
                    m_num = self.MONTH_MAP[m_name]
                    wheres.append(f"MONTH({fact_alias}.{date_col}) = {m_num}")
    
        if filters:
            ignore = ['year', 'month']
            for k, v in filters.items():
                if k not in ignore and v not in ["Todas", "Todos", None]:
                    val = f"'{v}'" if isinstance(v, str) else v
                    wheres.append(f"{fact_alias}.{k} = {val}")
    
        where_sql = (" WHERE " + " AND ".join(wheres)) if wheres else ""
    
        query = f"""
            SELECT {target_dim_alias}.{label_col} as label,
                   {agg}({fact_alias}.{fact_col}) as value
            FROM {fact_def['table_name']} as {fact_alias}
            {joins_sql}
            {where_sql}
            GROUP BY {target_dim_alias}.{label_col}
            ORDER BY value DESC
        """
    
        return {"type": "sql", "query": query}
    
    def get_dataframe_query(self, metrics: list, dimensions: list, filters=None):
        first_metric = self.metrics.get(metrics[0])
        if not first_metric: return None
    
        fact_alias = first_metric['recipe']['table']
        fact_def = self.tables.get(fact_alias)
        if not fact_def:
            return {"error": f"Table definition for '{fact_alias}' not found"}
    
        if not fact_def.get('date_column'):
            for potential_parent, defs in self.tables.items():
                if defs.get('date_column') and potential_parent != fact_alias:
                    path = self._find_join_path(potential_parent, fact_alias)
                    if path:
                        fact_alias = potential_parent
                        fact_def = defs
                        break
                    
        selects = []
        group_bys = []
        joins_needed = set()
    
        for dim in dimensions:
            if "." in dim:
                tbl, col = dim.split(".")
                selects.append(f"{tbl}.{col} as '{dim}'")
                group_bys.append(f"{tbl}.{col}")
                if tbl != fact_alias:
                    path = self._find_join_path(fact_alias, tbl)
                    if path:
                        for neighbor, _ in path:
                            joins_needed.add(neighbor)
            else:
                selects.append(f"{fact_alias}.{dim}")
                group_bys.append(f"{fact_alias}.{dim}")
    
        for m_key in metrics:
            m = self.metrics.get(m_key)
            if not m or m.get('type') == 'derived': continue
    
            recipe = m['recipe']
            m_table = recipe['table']
            col = recipe.get('column')
            agg = recipe.get('aggregation', 'SUM')
    
            if m_table != fact_alias:
                path = self._find_join_path(fact_alias, m_table)
                if path:
                    for neighbor, _ in path:
                        joins_needed.add(neighbor)
                    selects.append(f"{agg}({m_table}.{col}) as {m_key}")
                else:
                    print(f"WARNING: No join path found from {fact_alias} to {m_table} for metric {m_key}")
            else:
                selects.append(f"{agg}({fact_alias}.{col}) as {m_key}")
    
        joins_sql = ""
        processed_joins = set()
        active_tables_with_date = []
    
        if fact_alias != fact_alias:
            joins_needed.add(fact_alias)
    
        sorted_targets = sorted(list(joins_needed))
    
        for target in sorted_targets:
             path = self._find_join_path(fact_alias, target)
             if path:
                 for next_alias, join_def in path:
                     if next_alias in processed_joins: continue
    
                     next_table_def = self.tables.get(next_alias)
                     if not next_table_def:
                         continue
                     
                     if next_table_def.get('date_column'):
                         active_tables_with_date.append(next_alias)
    
                     t_name = next_table_def['table_name']
                     j_type = join_def.get('type', 'INNER')
                     j_on = join_def.get('on')
    
                     joins_sql += f" {j_type} JOIN {t_name} as {next_alias} ON {j_on}"
                     processed_joins.add(next_alias)
    
        wheres = []
    
        target_year = datetime.datetime.now().year
        target_month = None
    
        if filters:
            if filters.get('year'):
                target_year = int(filters['year'])
    
            if filters.get('month'):
                m_name = filters['month'].lower()
                if hasattr(self, 'MONTH_MAP') and m_name in self.MONTH_MAP:
                    target_month = self.MONTH_MAP[m_name]
    
        date_col_to_use = None
        if fact_def.get('date_column'):
            date_col_to_use = f"{fact_alias}.{fact_def['date_column']}"
        elif active_tables_with_date:
            tbl = active_tables_with_date[0]
            col = self.tables[tbl]['date_column']
            date_col_to_use = col if "." in col else f"{tbl}.{col}"
    
        if date_col_to_use:
            wheres.append(f"YEAR({date_col_to_use}) = {target_year}")
            if target_month:
                wheres.append(f"MONTH({date_col_to_use}) = {target_month}")
    
        if filters:
            ignore_keys = ['year', 'month']
            ignore_values = ["Todas", "Todos", "All", None]
    
            for k, v in filters.items():
                if k in ignore_keys: continue
                if v in ignore_values: continue
                val = f"'{v}'" if isinstance(v, str) else v
                if "." in k:
                    wheres.append(f"{k} = {val}")
                else:
                    wheres.append(f"{fact_alias}.{k} = {val}")
    
        where_sql = " WHERE " + " AND ".join(wheres) if wheres else ""
    
        query = f"""
            SELECT {', '.join(selects)}
            FROM {fact_def['table_name']} as {fact_alias}
            {joins_sql}
            {where_sql}
            GROUP BY {', '.join(group_bys)}
        """
    
        return {"type": "sql", "query": query}