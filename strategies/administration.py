from typing import Any, Dict
import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import format_value
from dash import dcc

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

        config = {
            "title": self.title,
            "icon": self.icon,
            "color": self.color,
            "inverse": self.inverse,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year", "Año Ant"),
            "target_formatted": node.get("target_formatted"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "trend": node.get("trend_direction"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status"),
            "status_color": node.get("status_color")
        }
        
        return config

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


class AdminGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, color="indigo", icon="tabler:gauge", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.kpi_key = kpi_key
        self.gauge_params = {
            "range_max_mult": 1.15,
            "threshold_width": 5,
            "threshold_color": "#f59e0b",
            "exceed_color": "#228be6",
            "bg_color": "rgba(0,0,0,0.05)",
            "font_size": 18
        }

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
        
        current_val = node.get("value", 0)
        target_val = node.get("target", 0)
        
        max_val = max(current_val, target_val) if target_val else current_val
        
        val_pct = (current_val / max_val * 100) if max_val > 0 else 0
        target_pct = (target_val / max_val * 100) if max_val > 0 and target_val > 0 else 100
        
        exceeds = val_pct > target_pct
        bar_color = self.gauge_params["exceed_color"] if exceeds else self.hex_color
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_pct,
            number={
                'suffix': "%",
                'font': {'size': self.gauge_params["font_size"], 'weight': 'bold'},
                'valueformat': '.1f'
            },
            gauge={
                'axis': {
                    'range': [0, max(val_pct, target_pct) * self.gauge_params["range_max_mult"]],
                    'visible': False
                },
                'bar': {'color': bar_color, 'thickness': 0.8},
                'bgcolor': self.gauge_params["bg_color"],
                'threshold': {
                    'line': {
                        'color': self.gauge_params["threshold_color"],
                        'width': self.gauge_params["threshold_width"]
                    },
                    'thickness': 0.75,
                    'value': target_pct
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        
        if exceeds:
            fig.add_annotation(
                x=0.5, y=1.05,
                text="★ META SUPERADA",
                showarrow=False,
                font=dict(color=bar_color, size=9, weight="bold")
            )
        
        fig.update_layout(
            height=150,
            margin=dict(l=5, r=5, t=0, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': "Inter, sans-serif"}
        )
        
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Análisis de eficiencia operativa.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


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
        colors = data_source.get("colors", [])
        
        if not labels or not values:
            return self._create_empty_figure("Sin datos de cartera")
        
        if not colors:
            colors = [DesignSystem.COLOR_MAP.get("green"), 
                     DesignSystem.COLOR_MAP.get("yellow"), 
                     DesignSystem.COLOR_MAP.get("red")]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0.5,
            marker=dict(colors=colors),
            textinfo='percent+label',
            textposition='auto'
        )])
        
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            height=300
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
        
        categories = (data_source.get("categories") or 
                     data_source.get("months") or 
                     data_source.get("meses") or [])
        
        series_list = data_source.get("series", [])
        
        if not categories or not series_list:
            return self._create_empty_figure("Sin datos temporales")
        
        fig = go.Figure()
        
        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", f"Serie {idx}")
            s_data = serie.get("data", [])
            s_color = serie.get("color", DesignSystem.BRAND[5])
            s_type = serie.get("type", "bar")
            is_dashed = serie.get("dashed", False) or "Meta" in s_name or "Presupuesto" in s_name
            
            if s_type == "line" or is_dashed:
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    mode='lines+markers',
                    line=dict(
                        color=s_color,
                        width=3,
                        dash='dot' if is_dashed else 'solid'
                    ),
                    marker=dict(size=6)
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    marker_color=s_color
                ))
        
        fig.update_layout(
            barmode='group',
            height=350,
            margin=dict(t=30, b=40, l=40, r=20),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            hovermode='x unified'
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
            return self._create_empty_figure("Sin categorías")
        
        fig = go.Figure()
        
        for serie in series_list:
            s_name = serie.get("name", "Valor")
            s_data = serie.get("data", [])
            s_color = serie.get("color", self.hex_color)
            
            fig.add_trace(go.Bar(
                y=categories,
                x=s_data,
                name=s_name,
                orientation='h',
                marker_color=s_color,
                text=[f"${v:,.0f}" if v > 1000 else f"${v:.2f}" for v in s_data],
                textposition='outside'
            ))
        
        fig.update_layout(
            barmode='stack' if len(series_list) > 1 else 'relative',
            height=max(300, len(categories) * 30),
            margin=dict(l=120, r=40, t=30, b=40),
            yaxis=dict(autorange="reversed"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            showlegend=len(series_list) > 1
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
            return self._create_empty_figure("Sin categorías")
        
        fig = go.Figure()
        
        for serie in series_list:
            s_name = serie.get("name", "Valor")
            s_data = serie.get("data", [])
            s_color = serie.get("color", self.hex_color)
            
            fig.add_trace(go.Bar(
                y=categories,
                x=s_data,
                name=s_name,
                orientation='h',
                marker_color=s_color
            ))
        
        fig.update_layout(
            barmode='stack',
            height=max(300, len(categories) * 40),
            margin=dict(l=120, r=40, t=30, b=40),
            yaxis=dict(autorange="reversed"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            showlegend=True,
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center")
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
            return None
        
        from utils.helpers import safe_get
        return safe_get(data_context, path)

    def render(self, data_context, **kwargs):
        node = self._resolve_table_data(data_context)
        
        if not node:
            return dmc.Text("Sin datos de tabla", c="dimmed", ta="center", py="xl") # type: ignore
        
        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])
        
        if not headers or not rows:
            return dmc.Text("Sin datos", c="dimmed", ta="center", py="xl") # type: ignore
        
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(h, style={"fontSize": "11px", "fontWeight": "bold"}) 
                for h in headers
            ])),
            dmc.TableTbody([
                dmc.TableTr([
                    dmc.TableTd(str(cell), style={"fontSize": "11px"}) 
                    for cell in row
                ]) 
                for row in rows
            ])
        ], striped="odd", withTableBorder=True, withColumnBorders=True)


class AdminCashFlowChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:cash", color="blue", layout_config=None):
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
        
        if not categories or not series_list:
            return self._create_empty_figure("Sin datos de flujo")
        
        fig = go.Figure()
        
        for serie in series_list:
            s_name = serie.get("name", "")
            s_data = serie.get("data", [])
            s_color = serie.get("color", self.hex_color)
            
            fig.add_trace(go.Bar(
                x=categories,
                y=s_data,
                name=s_name,
                marker_color=s_color
            ))
        
        fig.update_layout(
            barmode='group',
            height=350,
            margin=dict(t=30, b=40, l=40, r=20),
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            hovermode='x unified'
        )
        
        return fig

    def render_detail(self, data_context):
        return None


class AdminMultiLineChartStrategy(KPIStrategy):
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
        
        categories = (data_source.get("months") or 
                     data_source.get("categories") or [])
        series_list = data_source.get("series", [])
        
        if not categories or not series_list:
            return self._create_empty_figure("Sin datos")
        
        fig = go.Figure()
        
        for serie in series_list:
            s_name = serie.get("name", "")
            s_data = serie.get("data", [])
            s_color = serie.get("color", self.hex_color)
            
            fig.add_trace(go.Scatter(
                x=categories,
                y=s_data,
                name=s_name,
                mode='lines+markers',
                line=dict(color=s_color, width=3),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            height=350,
            margin=dict(t=30, b=40, l=40, r=20),
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            hovermode='x unified'
        )
        
        return fig

    def render_detail(self, data_context):
        return None