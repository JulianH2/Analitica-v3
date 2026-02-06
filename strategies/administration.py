from typing import Any, Dict
import plotly.graph_objects as go
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import format_value, safe_get
from dash import dcc
from datetime import datetime

def get_current_month():
    return datetime.now().month

def safe_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            clean = val.replace('%', '').replace('$', '').replace(',', '').strip()
            return float(clean) if clean else default
        except:
            return default
    return default
BAR_WIDTH = 0.35
BAR_GAP = 0.2


class AdminKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, icon, color, has_detail=True, layout_config=None, inverse=False):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.kpi_key = kpi_key
        self.inverse = inverse

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        
        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        return {
            "title": self.title,
            "icon": self.icon,
            "color": self.color,
            "inverse": self.inverse,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year", f"Vs {datetime.now().year - 1}"),
            "target_formatted": node.get("target_formatted"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "trend": node.get("trend_direction"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status"),
            "status_color": node.get("status_color") or self.color
        }

    def render_detail(self, data_context):
        return dmc.Text("Detalle de metrica administrativa.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


class AdminGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, color="indigo", icon="tabler:gauge", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.kpi_key = kpi_key

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node
        
        return {
            "title": self.title,
            "icon": self.icon,
            "value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year"),
            "target_formatted": node.get("target_formatted"),
            "meta_text": f"Meta: {node.get('target_formatted')}" if node.get('target_formatted') else ""
        }

    def get_figure(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node
        
        current_val = safe_float(node.get("value", 0))
        target_val = safe_float(node.get("target", 0))
        
        max_val = max(current_val, target_val) if target_val else current_val
        if max_val <= 0:
            return None
        
        val_pct = (current_val / max_val * 100) if max_val > 0 else 0
        target_pct = (target_val / max_val * 100) if max_val > 0 and target_val > 0 else 100
        
        exceeds = val_pct > target_pct
        if exceeds:
            bar_color = DesignSystem.NEXA_GREEN
        elif val_pct >= 80:
            bar_color = DesignSystem.NEXA_GOLD
        else:
            bar_color = DesignSystem.NEXA_BLUE
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_pct,
            number={
                'suffix': "%",
                'font': {'size': 18, 'weight': 'bold', 'color': DesignSystem.NEXA_BLACK},
                'valueformat': '.1f'
            },
            gauge={
                'axis': {'range': [0, max(val_pct, target_pct) * 1.1], 'visible': False},
                'bar': {'color': bar_color, 'thickness': 0.7},
                'bgcolor': DesignSystem.NEXA_GRAY_LIGHT,
                'borderwidth': 0,
                'threshold': {
                    'line': {'color': DesignSystem.NEXA_GRAY, 'width': 3},
                    'thickness': 0.8,
                    'value': target_pct
                }
            }
        ))
        
        if exceeds:
            fig.add_annotation(
                x=0.5, y=0.3,
                text="META SUPERADA",
                showarrow=False,
                font=dict(color=DesignSystem.NEXA_GREEN, size=9, weight="bold"),
                bgcolor="rgba(76, 159, 84, 0.1)",
                bordercolor=DesignSystem.NEXA_GREEN,
                borderwidth=1,
                borderpad=3
            )
        
        fig.update_layout(
            height=110,
            margin=dict(l=10, r=10, t=15, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': DesignSystem.TYPOGRAPHY["family"]}
        )
        
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Analisis de eficiencia operativa.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


class AdminDonutChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-pie", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure()
        
        data_source = node.get("data", node)
        labels = data_source.get("labels", [])
        values = data_source.get("values", [])
        total = data_source.get("total_formatted", "")
        
        if not labels or not values:
            return self._create_empty_figure("Sin datos")
        colors = DesignSystem.CHART_DONUT_COLORS[:len(labels)]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0.55,
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            textinfo='percent',
            textposition='outside',
            textfont=dict(size=10, color=DesignSystem.NEXA_BLACK),
            pull=[0.02] * len(labels)
        )])
        
        if total:
            fig.add_annotation(
                text=total, x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, weight="bold", color=DesignSystem.NEXA_BLACK)
            )
        
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v", 
                y=0.5, 
                x=1.02,
                font=dict(size=10, color=DesignSystem.NEXA_BLACK)
            ),
            margin=dict(t=20, b=20, l=20, r=90),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            height=300,
            font=dict(family=DesignSystem.TYPOGRAPHY["family"])
        )
        
        return fig

    def render_detail(self, data_context):
        return None


class AdminTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure()
        
        data_source = node.get("data", node)
        all_categories = (data_source.get("categories") or data_source.get("months") or [])
        series_list = data_source.get("series", [])
        
        if not all_categories or not series_list:
            return self._create_empty_figure("Sin datos")
        
        current_month = get_current_month()
        categories = all_categories[:current_month]
        
        fig = go.Figure()
        series_colors = [DesignSystem.NEXA_BLUE, DesignSystem.NEXA_ORANGE, DesignSystem.NEXA_GREEN]
        
        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", f"Serie {idx}")
            s_data = serie.get("data", [])[:current_month]
            s_type = serie.get("type", "bar")
            is_dashed = serie.get("dashed", False) or "Meta" in s_name
            
            s_color = series_colors[idx % len(series_colors)]
            
            if s_type == "line" or is_dashed:
                fig.add_trace(go.Scatter(
                    x=categories, y=s_data, name=s_name,
                    mode='lines+markers',
                    line=dict(color=DesignSystem.NEXA_GRAY if is_dashed else s_color, width=2, dash='dash' if is_dashed else 'solid'),
                    marker=dict(size=5)
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories, y=s_data, name=s_name,
                    marker_color=s_color,
                    width=BAR_WIDTH
                ))
        
        fig.update_layout(
            barmode='group',
            bargap=BAR_GAP,
            height=320,
            margin=dict(t=20, b=40, l=50, r=20),
            legend=dict(
                orientation="h", 
                y=1.08, 
                x=0.5, 
                xanchor="center",
                font=dict(size=10)
            ),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            hovermode='x unified',
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)),
            yaxis=dict(showgrid=True, gridcolor=DesignSystem.SLATE[2], tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)),
            font=dict(family=DesignSystem.TYPOGRAPHY["family"], color=DesignSystem.NEXA_BLACK)
        )
        
        return fig

    def render_detail(self, data_context):
        return None


class AdminHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure()
        
        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])
        
        if not categories:
            return self._create_empty_figure("Sin categorias")
        
        fig = go.Figure()
        
        bar_colors = [DesignSystem.NEXA_BLUE, DesignSystem.NEXA_ORANGE, DesignSystem.NEXA_GREEN]
        
        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", "Valor")
            s_data = serie.get("data", [])
            clean_data = [safe_float(v) for v in s_data]
            bar_color = bar_colors[idx % len(bar_colors)]
            
            fig.add_trace(go.Bar(
                y=categories, x=clean_data, name=s_name,
                orientation='h',
                marker_color=bar_color,
                width=0.6
            ))
        
        chart_height = max(280, min(len(categories) * 32, 450))
        
        fig.update_layout(
            barmode='group',
            bargap=0.2,
            height=chart_height,
            margin=dict(l=100, r=30, t=20, b=30),
            yaxis=dict(autorange="reversed", tickfont=dict(size=10, color=DesignSystem.NEXA_BLACK), showgrid=False),
            xaxis=dict(tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY), showgrid=True, gridcolor=DesignSystem.SLATE[2]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=len(series_list) > 1,
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center", font=dict(size=10)),
            font=dict(family=DesignSystem.TYPOGRAPHY["family"], color=DesignSystem.NEXA_BLACK)
        )
        
        return fig

    def render_detail(self, data_context):
        return None


class AdminStackedBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure()
        
        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])
        
        if not categories:
            return self._create_empty_figure("Sin categorias")
        
        fig = go.Figure()
        stack_colors = [DesignSystem.NEXA_BLUE, DesignSystem.NEXA_ORANGE, DesignSystem.NEXA_GREEN, DesignSystem.NEXA_GOLD]
        
        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", f"Rango {idx}")
            s_data = serie.get("data", [])
            clean_data = [safe_float(v) for v in s_data]
            
            fig.add_trace(go.Bar(
                x=categories, y=clean_data, name=s_name,
                marker_color=stack_colors[idx % len(stack_colors)],
                width=0.5
            ))
        
        fig.update_layout(
            barmode='stack',
            height=350,
            margin=dict(t=20, b=40, l=50, r=20),
            legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center", font=dict(size=10)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)),
            yaxis=dict(showgrid=True, gridcolor=DesignSystem.SLATE[2], tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)),
            font=dict(family=DesignSystem.TYPOGRAPHY["family"], color=DesignSystem.NEXA_BLACK)
        )
        
        return fig

    def render_detail(self, data_context):
        return None


class AdminTableStrategy:
    def __init__(self, screen_id, table_key):
        self.screen_id = screen_id
        self.table_key = table_key

    def _resolve_table_data(self, data_context):
        from services.data_manager import data_manager
        
        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {}) # type: ignore
        inject_paths = screen_config.get("inject_paths", {})
        
        path = inject_paths.get(self.table_key)
        if not path:
            return safe_get(data_context, ["administration", "tables", self.table_key])
        
        return safe_get(data_context, path)

    def render(self, data_context, **kwargs):
        node = self._resolve_table_data(data_context)
        
        if not node:
            return dmc.Center(
                dmc.Stack([
                    DashIconify(icon="tabler:table-off", width=40, color=DesignSystem.NEXA_GRAY),
                    dmc.Text(f"Sin datos: {self.table_key}", c="dimmed", size="sm") # type: ignore
                ], align="center", gap="xs"),
                py="xl"
            )

        headers = node.get("headers", [])
        rows = node.get("rows", [])
        
        if not headers and "data" in node:
            data_source = node.get("data", {})
            headers = data_source.get("headers", [])
            rows = data_source.get("rows", [])

        if not headers:
            return dmc.Text(f"Sin headers: {self.table_key}", c="dimmed", ta="center", py="xl") # type: ignore

        table_rows = [
            dmc.TableTr([
                dmc.TableTd(str(cell) if cell is not None else "", 
                    style={"fontSize": "11px", "whiteSpace": "nowrap", "padding": "6px 12px"}) 
                for cell in row
            ]) for row in rows[:50]
        ]

        return dmc.Table(
            [
                dmc.TableThead(
                    dmc.TableTr([
                        dmc.TableTh(str(h), 
                            style={
                                "fontSize": "11px", 
                                "fontWeight": "600", 
                                "whiteSpace": "nowrap",
                                "backgroundColor": DesignSystem.NEXA_GRAY_LIGHT, 
                                "color": DesignSystem.NEXA_BLACK,
                                "padding": "8px 12px"
                            }) 
                        for h in headers
                    ])
                ),
                dmc.TableTbody(table_rows)
            ], 
            striped=True, # type: ignore
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
            style={"width": "100%"}
        )