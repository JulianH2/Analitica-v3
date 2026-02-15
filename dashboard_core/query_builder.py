from .metadata_engine import MetadataEngine
import datetime
import re

class SmartQueryBuilder:

    _SQL_EXPRESSION_SKIP = frozenset(
        s.upper() for s in (
            "day", "month", "year", "getdate", "datediff", "sum", "avg", "count",
            "min", "max", "null", "getutcdate", "sysdatetime", "current_timestamp",
            "week", "quarter", "isnull", "coalesce", "abs", "round", "cast", "convert"
        )
    )

    def _qualify_expression(self, expression: str, table_alias: str) -> str:
        
        def repl(m):
            word = m.group(0)
            if word.upper() in self._SQL_EXPRESSION_SKIP:
                return word
            return f"{table_alias}.{word}"
        return re.sub(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", repl, expression)

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
    
    def get_dataframe_query(self, metrics: list, dimensions: list, filters=None):
        first_metric = self.metrics.get(metrics[0])
        if not first_metric: 
            return None
        
        if first_metric.get('type') == 'placeholder':
            return {"type": "placeholder", "default_value": []}
        
        if first_metric.get('type') == 'derived':
            for m in metrics:
                metric_def = self.metrics.get(m)
                if metric_def and metric_def.get('recipe'):
                    first_metric = metric_def
                    break
            else:
                return {"error": "No se encontró métrica base para el dataframe"}
    
        fact_alias = first_metric.get('recipe', {}).get('table')
        if not fact_alias:
            return {"error": "Métrica sin tabla definida"}
            
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
        group_by_month = False
        
        if "__month__" in dimensions:
            group_by_month = True
            dimensions = [d for d in dimensions if d != "__month__"]

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
            if not m or m.get('type') in ['derived', 'placeholder']: 
                continue
    
            recipe = m.get('recipe', {})
            m_table = recipe.get('table')
            col = recipe.get('column')
            agg = recipe.get('aggregation', 'SUM')
            is_expression = isinstance(col, str) and "(" in col

            def get_agg_expr(table_alias, column_name, aggregation_type):
                if is_expression:
                    inner = self._qualify_expression(column_name, table_alias)
                    if aggregation_type == "DISTINCTCOUNT":
                        return f"COUNT(DISTINCT {inner})"
                    return f"{aggregation_type}({inner})"
                if aggregation_type == "DISTINCTCOUNT":
                    return f"COUNT(DISTINCT {table_alias}.{column_name})"
                return f"{aggregation_type}({table_alias}.{column_name})"


            if m_table != fact_alias:
                path = self._find_join_path(fact_alias, m_table)
                if path:
                    for neighbor, _ in path:
                        joins_needed.add(neighbor)
                    expr = get_agg_expr(m_table, col, agg)
                    selects.append(f"{expr} as {m_key}")
                else:
                    print(f"WARNING: No join path found from {fact_alias} to {m_table} for metric {m_key}")
            else:
                expr = get_agg_expr(fact_alias, col, agg)
                selects.append(f"{expr} as {m_key}")


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
        

        time_modifier = None
        for m_key in metrics:
            m_def = self.metrics.get(m_key)
            if m_def and 'recipe' in m_def and m_def['recipe'].get('time_modifier'):
                time_modifier = m_def['recipe']['time_modifier']
                break
        

        month_operator = "="
        
        if time_modifier == 'previous_year':
            target_year -= 1
        elif time_modifier == 'ytd':
            month_operator = "<="


        date_col_to_use = None
        if fact_def.get('date_column'):
            date_col_to_use = f"{fact_alias}.{fact_def['date_column']}"
        elif active_tables_with_date:
            tbl = active_tables_with_date[0]
            col = self.tables[tbl]['date_column']
            date_col_to_use = col if "." in col else f"{tbl}.{col}"
    
        if date_col_to_use:
            if group_by_month:
                selects.insert(0, f"MONTH({date_col_to_use}) as period")
                group_bys.insert(0, f"MONTH({date_col_to_use})")

            wheres.append(f"YEAR({date_col_to_use}) = {target_year}")
            if target_month and not group_by_month:

                wheres.append(f"MONTH({date_col_to_use}) {month_operator} {target_month}")


        if filters:
            ignore_keys = ['year', 'month']
            ignore_values = ["Todas", "Todos", "All", None]
    
            for k, v in filters.items():
                if k in ignore_keys: continue
                if v in ignore_values: continue
                val = f"'{v}'" if isinstance(v, str) else v
                if "." in k: wheres.append(f"{k} = {val}")
                else: wheres.append(f"{fact_alias}.{k} = {val}")

        where_sql = " WHERE " + " AND ".join(wheres) if wheres else ""


        group_by_clause = f"GROUP BY {', '.join(group_bys)}" if group_bys else ""

        query = f"""
            SELECT {', '.join(selects)}
            FROM {fact_def['table_name']} as {fact_alias}
            {joins_sql}
            {where_sql}
            {group_by_clause}
        """


        return {"type": "sql", "query": query}