import math
import dash_ag_grid as dag
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html
from dash_iconify import DashIconify
from design_system import DesignSystem, Colors, SemanticColors, ComponentSizes, Space, Typography, dmc as _dmc
from utils.helpers import safe_get
from .base_strategy import KPIStrategy
from .chart_engine import ChartEngine


class WorkshopKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="", has_detail=True, variant=None, inverse=False, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)
        self.inverse = inverse

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        config = {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": False,
            "color": self.color,
            "inverse": self.inverse,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year", "Año Ant."),
            "target_formatted": node.get("target_formatted"),
            "target_delta": node.get("target_delta"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "trend": node.get("trend"),
            "trend_direction": node.get("trend_direction"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status"),
            "status_color": node.get("status_color") or self.color,
            "raw_data": node,
        }

        if node.get("percentage_of_total"):
            config["percentage_of_total"] = node.get("percentage_of_total")

        return config

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle de métrica de mantenimiento.", size="sm", c=_dmc("dimmed"))
class WorkshopGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:gauge", has_detail=True, variant=None, use_needle=False, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)
        self.use_needle = use_needle
        self.gauge_params = {
            "range_max_mult": 1.15,
            "threshold_width": 5,
            "threshold_color": DesignSystem.WARNING[5],
            "exceed_color": DesignSystem.INFO[5],
            "bg_color": "rgba(148, 163, 184, 0.05)",
            "font_size": 18,
        }

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        cfg = {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": False,
            "color": self.color,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year", "Año Ant."),
            "target_formatted": node.get("target_formatted"),
            "target_delta": node.get("target_delta"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "trend": node.get("trend"),
            "trend_direction": node.get("trend_direction"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status"),
            "status_color": node.get("status_color") or self.color,
            "meta_text": f"Meta: {node.get('target_formatted')}" if node.get("target_formatted") else "",
            "hide_meta": self.use_needle,
            "raw_data": node,
        }
        if self.key in ("availability_percent", "current_valuation"):
            cfg["vs_last_year_formatted"] = None
            cfg["vs_last_year_delta"] = None
            cfg["vs_last_year_delta_formatted"] = None
        return cfg

    def get_figure(self, ctx, theme="dark"):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)

        if self.use_needle:
            if isinstance(raw_node, (int, float)):
                node = {"value": raw_node}
            elif raw_node is None:
                node = {}
            else:
                node = raw_node

            current_val = node.get("value", 0)
            target_val = node.get("target", 0)

            if isinstance(current_val, float) and current_val <= 1.0:
                current_val *= 100
            if isinstance(target_val, float) and target_val <= 1.0:
                target_val *= 100

            return self._create_needle_gauge(current_val, target_val, theme)

        fig = ChartEngine.render_gauge(raw_node, theme, self.layout, self.hex_color)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig

    def _create_needle_gauge(self, current_val, target_val, theme="light"):
        is_dark = theme == "dark"
        # Colores sólidos por zona (como imagen de referencia)
        if current_val >= 92:
            zone_color = "#2f9e44"
            status_label = "Óptimo"
        elif current_val >= 85:
            zone_color = "#f08c00"
            status_label = "Aceptable"
        else:
            zone_color = "#c92a2a"
            status_label = "Crítico"

        fig = go.Figure(go.Indicator(
            mode="gauge",
            value=current_val,
            gauge={
                "axis": {
                    "range": [0, 100],
                    "visible": True,
                    "tickwidth": 1,
                    "tickcolor": "rgba(120,120,120,0.6)",
                    "tickfont": {"size": 9, "color": "#9ca3af" if is_dark else "#888"},
                    "nticks": 6,
                },
                "bar": {"color": Colors.TRANSPARENT, "thickness": 0},
                "bgcolor": Colors.BG_DARK_CARD if is_dark else Colors.BG_LIGHT_CARD,
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 60],  "color": "#c92a2a"},
                    {"range": [60, 75], "color": "#e67700"},
                    {"range": [75, 85], "color": "#f08c00"},
                    {"range": [85, 92], "color": "#94d82d"},
                    {"range": [92, 100],"color": "#2f9e44"},
                ],
                "threshold": {
                    "line": {"color": "#1971c2", "width": 3},
                    "thickness": 0.85,
                    "value": target_val if target_val else 90,
                },
            },
        ))

        # ── Aguja como SVG path shape (layer="above" → encima del arco) ──
        # Pivote en la base del arco (centro-abajo del gauge)
        theta = 180 - (current_val * 1.8)
        r_needle = 0.32          # largo de la aguja
        r_base = 0.025           # ancho de la base
        x_pivot, y_pivot = 0.5, 0.22   # base del arco del gauge

        x_tip = x_pivot + r_needle * math.cos(math.radians(theta))
        y_tip = y_pivot + r_needle * math.sin(math.radians(theta))

        x_bl = x_pivot + r_base * math.cos(math.radians(theta + 90))
        y_bl = y_pivot + r_base * math.sin(math.radians(theta + 90))
        x_br = x_pivot + r_base * math.cos(math.radians(theta - 90))
        y_br = y_pivot + r_base * math.sin(math.radians(theta - 90))

        needle_color = "#e8eaed" if is_dark else "#1a1a2e"
        hub_color = "#1a1a2e" if not is_dark else "#e8eaed"

        # Triángulo de la aguja como shape path (se renderiza ENCIMA del gauge)
        path_str = f"M {x_bl} {y_bl} L {x_tip} {y_tip} L {x_br} {y_br} Z"
        fig.add_shape(
            type="path", path=path_str,
            fillcolor=needle_color, line=dict(color=needle_color, width=0),
            xref="paper", yref="paper", layer="above",
        )

        # Hub central
        fig.add_shape(type="circle",
            x0=x_pivot - 0.028, y0=y_pivot - 0.028,
            x1=x_pivot + 0.028, y1=y_pivot + 0.028,
            fillcolor=needle_color, line=dict(color=hub_color, width=2),
            xref="paper", yref="paper", layer="above")
        fig.add_shape(type="circle",
            x0=x_pivot - 0.010, y0=y_pivot - 0.010,
            x1=x_pivot + 0.010, y1=y_pivot + 0.010,
            fillcolor=hub_color, line=dict(color=hub_color, width=0),
            xref="paper", yref="paper", layer="above")

        height = self.layout.get("height", 280)

        fig.update_layout(
            template="zam_dark" if is_dark else "zam_light",
            height=height,
            margin=dict(l=20, r=20, t=30, b=15),
            paper_bgcolor=Colors.BG_DARK_CARD if is_dark else Colors.BG_LIGHT_CARD,
            plot_bgcolor=Colors.BG_DARK_CARD if is_dark else Colors.BG_LIGHT_CARD,
            annotations=[
                dict(x=0.5, y=0.38, text=f"<b>{current_val:.0f}%</b>",
                    showarrow=False,
                    font=dict(size=20, color=zone_color, family="Nexa, Montserrat, sans-serif"),
                    xref="paper", yref="paper"),
                dict(x=0.5, y=0.20, text=status_label,
                    showarrow=False,
                    font=dict(size=10, color="#9ca3af" if is_dark else "#888888"),
                    xref="paper", yref="paper"),
            ],
        )
        return fig

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Análisis de eficiencia de mantenimiento.", size="sm", c=_dmc("dimmed"))
class WorkshopTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-line", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_trend(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopDonutChartStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-pie", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_donut(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-bar", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_horizontal_bar(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopBarChartStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-bar", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_bar_chart(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopComboChartStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-line", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="dark"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_combo_chart(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig


class WorkshopTableStrategy:
    def __init__(self, screen_id, key, title="", color="gray", icon="tabler:table", has_detail=True, variant=None):
        self.screen_id = screen_id
        self.key = key
        self.title = title
        self.icon = icon
        self.color = color
        self.has_detail = has_detail
        self.variant = variant

    def _get_data(self, ctx):
        from flask import session
        from services.data_manager import data_manager

        screen_map = data_manager.get_screen_map(session.get("current_db")) or {}
        screen_config = screen_map.get(self.screen_id, {})
        inject_paths = screen_config.get("inject_paths", {})

        if self.variant:
            lookup_key = f"{self.key}_{self.variant}"
            path = inject_paths.get(lookup_key) or inject_paths.get(self.key)
        else:
            path = inject_paths.get(self.key)

        if not path:
            return None, None
        
        node = safe_get(ctx, path)
        if not node:
            return None, None

        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])
        
        return headers, rows

    def get_card_config(self, ctx):
        headers, rows = self._get_data(ctx)
        
        export_data = []
        if headers and rows:
            for row in rows:
                if isinstance(row, (list, tuple)):
                    row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
                else:
                    row_dict = row
                export_data.append(row_dict)
        
        return {
            "title": self.title or self.key,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": True,
            "is_chart": False,
            "main_value": f"{len(rows)} registros" if rows else "0",
            "raw_data": export_data,
        }

    def render(self, ctx, mode="dashboard", theme="dark"):
        headers, rows = self._get_data(ctx)
        if not headers or not rows:
            return dmc.Center(style={"height": 200}, children=[
                dmc.Stack(align="center", gap=Space.XS, children=[
                    DashIconify(icon="tabler:table-off", width=40, color=Colors.NEXA_GRAY),
                    dmc.Text("Sin datos disponibles", size="xs", c=_dmc("dimmed"), style={"fontFamily": Typography.FAMILY}),
                ])
            ])

        if mode in ["analyst", "analysis"]:
            return self._render_simple_table(headers, rows, theme)

        unique_key = f"{self.screen_id}-{self.key}"

        column_defs = []
        for i, h in enumerate(headers):
            col_def = {
                "field": f"col_{i}",
                "headerName": h,
                "sortable": True,
                "resizable": True,
                "suppressMenu": True,
                "tooltipField": f"col_{i}",
            }
            if i == 0:
                col_def.update({"pinned": "left", "width": 90, "flex": 0})
            else:
                col_def.update({"minWidth": 120, "flex": 1})
            column_defs.append(col_def)

        row_data = []
        for row in rows:
            if isinstance(row, (list, tuple)):
                row_data.append({f"col_{i}": (v if v is not None else "") for i, v in enumerate(row)})
            elif isinstance(row, dict):
                row_data.append({f"col_{i}": (row.get(h, "") or "") for i, h in enumerate(headers)})

        def _parse_cell(v):
            if isinstance(v, (int, float)):
                return float(v) if v == v else None
            if not isinstance(v, str):
                return None
            s = v.strip()
            if s in ("", "---", "-"):
                return None
            neg = s.startswith("-")
            s = s.lstrip("+-$").strip()
            mult = 1.0
            if s.endswith("B"):
                mult = 1e9; s = s[:-1]
            elif s.endswith("M"):
                mult = 1e6; s = s[:-1]
            elif s.endswith("m"):
                mult = 1e3; s = s[:-1]
            elif s.upper().endswith("K"):
                mult = 1e3; s = s[:-1]
            elif s.endswith("%"):
                return None
            try:
                num = float(s.replace(",", "")) * mult
                return -num if neg else num
            except ValueError:
                return None

        total_row = {}
        for i in range(len(headers)):
            field = f"col_{i}"
            if i == 0:
                total_row[field] = "TOTAL"
                continue
            vals = [r.get(field, "") for r in row_data]
            nums = [_parse_cell(v) for v in vals]
            valid = [n for n in nums if n is not None]
            if valid and len(valid) == len(vals):
                s = sum(valid)
                first = str(vals[0]).strip().lstrip("-")
                is_currency = first.startswith("$")
                a = abs(s)
                if is_currency:
                    if a >= 1e9:
                        total_row[field] = f"${s/1e9:.1f}B"
                    elif a >= 1e6:
                        total_row[field] = f"${s/1e6:.1f}M"
                    elif a >= 1e3:
                        total_row[field] = f"${s/1e3:.1f}m"
                    else:
                        total_row[field] = f"${s:,.0f}"
                else:
                    total_row[field] = f"{int(s):,}" if s == int(s) else f"{s:,.2f}"
            else:
                total_row[field] = ""

        grid = dag.AgGrid(
            id={"type": "ag-grid-dashboard", "index": unique_key},
            rowData=row_data,
            columnDefs=column_defs,
            defaultColDef={"sortable": True, "resizable": True, "filter": False},
            dashGridOptions={
                "domLayout": "autoHeight",
                "pagination": True,
                "paginationPageSize": 20,
                "rowHeight": ComponentSizes.TABLE_ROW_HEIGHT,
                "headerHeight": ComponentSizes.TABLE_HEADER_HEIGHT,
                "suppressFieldDotNotation": True,
                "quickFilterText": "",
                "pinnedBottomRowData": [total_row],
            },
            style={"width": "100%"},
            className=f"ag-theme-alpine{'-dark' if theme == 'dark' else ''} compact",
        )

        return html.Div(
            style={"height": "100%", "display": "flex", "flexDirection": "column"},
            children=[html.Div(style={"flex": 1, "minHeight": "250px", "overflow": "hidden"}, children=grid)],
        )

    def _render_simple_table(self, headers, rows, theme="dark"):
        is_dark = theme == "dark"
        cell_style = {"fontSize": "11px", "color": "#e8eaed" if is_dark else "#1d1d1b"}
        head_style = {"fontSize": "11px", "fontWeight": "bold", "color": "#9ca3af" if is_dark else "#6b7280"}
        table_body = [
            dmc.TableTr([dmc.TableTd(str(cell), style=cell_style) for cell in row])
            for row in rows[:100]
        ]
        return dmc.Table(
            [
                dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style=head_style) for h in headers])),
                dmc.TableTbody(table_body),
            ],
            striped="odd",
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
        )

    def _resolve_table_data(self, ctx):
        from flask import session
        from services.data_manager import data_manager

        screen_map = data_manager.get_screen_map(session.get("current_db")) or {}
        screen_config = screen_map.get(self.screen_id, {})
        inject_paths = screen_config.get("inject_paths", {})

        if self.variant:
            lookup_key = f"{self.key}_{self.variant}"
            path = inject_paths.get(lookup_key) or inject_paths.get(self.key)
        else:
            path = inject_paths.get(self.key)

        if not path:
            return None
        return safe_get(ctx, path)