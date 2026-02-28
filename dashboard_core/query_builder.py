from .metadata_engine import MetadataEngine
import datetime
import re

class SmartQueryBuilder:

    _SQL_EXPRESSION_SKIP = frozenset(
        s.upper() for s in (
            "day", "month", "year", "getdate", "datediff", "sum", "avg", "count",
            "min", "max", "null", "getutcdate", "sysdatetime", "current_timestamp",
            "week", "quarter", "isnull", "coalesce", "abs", "round", "cast", "convert",
            "case", "when", "then", "else", "end", "in", "and", "or", "not", "is",
            "like", "between", "exists", "as", "asc", "desc", "distinct"
        )
    )

    def _qualify_expression(self, expression: str, table_alias: str) -> str:
        """Qualify column identifiers with table alias. Skips SQL keywords and
        identifiers inside single-quoted string literals (e.g. IN ('A','C','L'))."""
        def repl(m):
            word = m.group(0)
            if word.upper() in self._SQL_EXPRESSION_SKIP:
                return word
            return f"{table_alias}.{word}"

        # Split by single-quoted literals so we only qualify identifiers outside quotes.
        # Pattern: optional content, then '...' (literal), allowing escaped quotes ''
        parts = re.split(r"('(?:[^']|'')*')", expression)
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                result.append(part)  # literal: leave unchanged
            else:
                result.append(re.sub(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", repl, part))
        return "".join(result)

    MONTH_MAP = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }

    def _build_date_range(self, year: int, month: int | None = None, ytd: bool = False):
        """Genera tupla (start_date, end_date) para filtros de rango."""
        if month is None:
            return f"{year}-01-01", f"{year + 1}-01-01"
        elif ytd:
            end_month = month + 1 if month < 12 else 1
            end_year = year if month < 12 else year + 1
            return f"{year}-01-01", f"{end_year}-{end_month:02d}-01"
        else:
            end_month = month + 1 if month < 12 else 1
            end_year = year if month < 12 else year + 1
            return f"{year}-{month:02d}-01", f"{end_year}-{end_month:02d}-01"
    
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
    
    def get_dataframe_query(self, metrics: list, dimensions: list, filters=None, page_filters=None):
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
        group_by_year_month = False

        if "__month__" in dimensions:
            group_by_month = True
            dimensions = [d for d in dimensions if d != "__month__"]

        if "__year_month__" in dimensions:
            group_by_year_month = True
            dimensions = [d for d in dimensions if d != "__year_month__"]

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
            # Expression: contains operators, parens, or spaces (e.g. "duracion * costo"); metadata stays table-agnostic
            is_expression = isinstance(col, str) and (
                "(" in col or "*" in col or "+" in col or "-" in col or "/" in col or (" " in col and "." not in col)
            )

            def get_agg_expr(table_alias, column_name, aggregation_type):
                is_distinct_count = aggregation_type in ("DISTINCTCOUNT", "COUNT_DISTINCT")
                if is_expression:
                    inner = self._qualify_expression(column_name, table_alias)
                    if is_distinct_count:
                        return f"COUNT(DISTINCT {inner})"
                    return f"{aggregation_type}({inner})"
                if is_distinct_count:
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

        if not fact_def.get('date_column'):
            for j_key, j_def in fact_def.get('joins', {}).items():
                target_table = j_def.get('target_table')
                if target_table:
                    t_def = self.tables.get(target_table)
                    if t_def and t_def.get('date_column'):
                        joins_needed.add(target_table)
                        break


        if filters:
            _skip_vals = {"Todas", "Todos", "All", None, ""}
            for _fk, _fv in filters.items():
                if _fk in ('year', 'month'):
                    continue
                if _fv in _skip_vals:
                    continue
                if "." in _fk:
                    _fk_tbl = _fk.split(".")[0]
                    if _fk_tbl != fact_alias:
                        joins_needed.add(_fk_tbl)

        # Inject JOINs for page_filter tables so their filters can be applied (even if no metric/dimension uses them)
        if page_filters:
            _pf_list = page_filters if isinstance(page_filters, list) else [page_filters]
            for pf in _pf_list:
                if not isinstance(pf, dict) or "field" not in pf or "." not in pf.get("field", ""):
                    continue
                table_alias = pf["field"].split(".", 1)[0]
                if table_alias in joins_needed or table_alias == fact_alias or table_alias not in self.tables:
                    continue
                path = self._find_join_path(fact_alias, table_alias)
                if path:
                    for neighbor, _ in path:
                        joins_needed.add(neighbor)

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
    
        used_tables = {fact_alias} | processed_joins
    
        wheres = []
    
        target_year = datetime.datetime.now().year
        target_month = None
    
        if filters:
            if filters.get('year'):
                target_year = int(filters['year'])
    
            if filters.get('month'):
                m_val = filters['month']
                try:
                    target_month = int(m_val)
                    if 1 <= target_month <= 12:
                        pass
                    else:
                        target_month = None
                except (TypeError, ValueError):
                    m_name = str(m_val).lower()
                    if hasattr(self, 'MONTH_MAP') and m_name in self.MONTH_MAP:
                        target_month = self.MONTH_MAP[m_name]
                    else:
                        target_month = None
        

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
            if group_by_year_month:
                # Multi-year series: GROUP BY year+month, no lower-bound filter
                selects.insert(0, f"YEAR({date_col_to_use}) as anio")
                selects.insert(1, f"MONTH({date_col_to_use}) as mes")
                group_bys.insert(0, f"YEAR({date_col_to_use})")
                group_bys.insert(1, f"MONTH({date_col_to_use})")
                end_m = target_month if target_month else 12
                end_y = target_year if end_m < 12 else target_year + 1
                end_m_next = end_m + 1 if end_m < 12 else 1
                wheres.append(f"{date_col_to_use} < '{end_y}-{end_m_next:02d}-01'")
            else:
                if group_by_month:
                    selects.insert(0, f"MONTH({date_col_to_use}) as period")
                    group_bys.insert(0, f"MONTH({date_col_to_use})")
                    start, end = self._build_date_range(target_year)
                elif target_month is not None:
                    is_ytd = (time_modifier == 'ytd')
                    start, end = self._build_date_range(target_year, target_month, ytd=is_ytd)
                else:
                    start, end = self._build_date_range(target_year)
                wheres.append(f"{date_col_to_use} >= '{start}'")
                wheres.append(f"{date_col_to_use} < '{end}'")

        if page_filters:
            _pf_list = page_filters if isinstance(page_filters, list) else [page_filters]
            for pf in _pf_list:
                if not isinstance(pf, dict) or "field" not in pf or "operator" not in pf or "value" not in pf:
                    continue
                field = pf.get("field", "")
                if "." not in field:
                    continue
                table_alias, column = field.split(".", 1)
                if table_alias not in used_tables or table_alias not in self.tables:
                    continue
                col_name = f"{table_alias}.{column}"
                op = pf["operator"].strip().upper()
                val = pf["value"]
                if isinstance(val, list):
                    if not val:
                        continue
                    clean_vals = [f"'{x}'" if isinstance(x, str) else str(x) for x in val]
                    if op == "NOT IN":
                        wheres.append(f"{col_name} NOT IN ({', '.join(clean_vals)})")
                    else:
                        wheres.append(f"{col_name} IN ({', '.join(clean_vals)})")
                else:
                    clean_val = f"'{val}'" if isinstance(val, str) else str(val)
                    wheres.append(f"{col_name} {pf['operator']} {clean_val}")

        if filters:
            ignore_keys = ['year', 'month']
            ignore_values = ["Todas", "Todos", "All", None]
    
            for k, v in filters.items():
                if k in ignore_keys: continue
                if v in ignore_values: continue

                # Determinar nombre de columna (con alias si es necesario)
                col_name = k if "." in k else f"{fact_alias}.{k}"

                # Si el filtro referencia una tabla externa (dot-notation), sólo
                # aplicarlo cuando esa tabla fue realmente joinada en esta query.
                # Esto evita errores 42000 cuando la tabla de hecho (ej. d_meta_tiempo)
                # no tiene camino hacia d_personal, d_area, etc.
                if "." in k:
                    filter_tbl = k.split(".")[0]
                    if filter_tbl != fact_alias and filter_tbl not in processed_joins:
                        continue

                # CASO 1: Filtro Avanzado (Diccionario con operador)
                if isinstance(v, dict) and "operator" in v and "value" in v:
                    op = v["operator"]
                    val = v["value"]
                    clean_val = f"'{val}'" if isinstance(val, str) else str(val)
                    wheres.append(f"{col_name} {op} {clean_val}")

                # CASO 2: Lista de valores (IN)
                elif isinstance(v, list):
                    if not v: continue
                    clean_vals = [f"'{x}'" if isinstance(x, str) else str(x) for x in v]
                    wheres.append(f"{col_name} IN ({', '.join(clean_vals)})")

                # CASO 3: Filtro Normal (Igualdad)
                else:
                    clean_val = f"'{v}'" if isinstance(v, str) else str(v)
                    wheres.append(f"{col_name} = {clean_val}")

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