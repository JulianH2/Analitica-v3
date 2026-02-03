import plotly.graph_objects as go
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import format_value, safe_get
from datetime import datetime

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

def safe_max(*args):
    valid = [safe_float(v) for v in args if v is not None]
    return max(valid) if valid else 0.0

def clean_series(x_data, y_data):
    import math
    x_clean, y_clean = [], []
    for x, y in zip(x_data or [], y_data or []):
        y_val = safe_float(y)
        if not math.isnan(y_val):
            x_clean.append(x)
            y_clean.append(y_val)
    return x_clean, y_clean

def get_current_year():
    return datetime.now().year

def get_previous_year():
    return datetime.now().year - 1

def get_current_month():
    return datetime.now().month

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


class OpsKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, icon, color, has_detail=True, layout_config=None, inverse=False):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.kpi_key = kpi_key
        self.inverse = inverse

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node, "value_formatted": str(raw_node)}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node if isinstance(raw_node, dict) else {}

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
            "status_color": node.get("status_color")
        }

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica operacional.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore

class OpsGaugeStrategy(KPIStrategy):
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
            node = raw_node if isinstance(raw_node, dict) else {}
        
        return {
            "title": self.title,
            "icon": self.icon,
            "color": self.color,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "label_prev_year": node.get("label_prev_year", "Año Ant."),
            "target_formatted": node.get("target_formatted"),
            "target_delta": node.get("target_delta"),
            "trend": node.get("trend"),
            "meta_text": f"Meta: {node.get('target_formatted')}" if node.get('target_formatted') and node.get('target_formatted') != '---' else ""
        }

    def get_figure(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        
        if raw_node is None:
            return None
        
        node = raw_node if isinstance(raw_node, dict) else {"value": raw_node}
        
        current_val = safe_float(node.get("value", 0))
        target_val = safe_float(node.get("target", 0))
        
        if target_val <= 0 and current_val <= 0:
            return None
        
        if target_val <= 0:
            target_val = current_val * 1.2
        
        max_val = safe_max(current_val, target_val)
        if max_val <= 0:
            return None

        val_pct = (current_val / target_val * 100) if target_val > 0 else 0
        
        if val_pct >= 100:
            bar_color = DesignSystem.SUCCESS[5]
        elif val_pct >= 80:
            bar_color = DesignSystem.WARNING[5]
        else:
            bar_color = DesignSystem.DANGER[5]
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_pct,
            number={
                'suffix': "%", 
                'font': {'size': 18, 'weight': 'bold'}, 
                'valueformat': '.1f'
            },
            gauge={
                'axis': {'range': [0, max(val_pct, 100) * 1.15], 'visible': False},
                'bar': {'color': bar_color, 'thickness': 0.8},
                'bgcolor': DesignSystem.SLATE[1],
                'threshold': {
                    'line': {'color': DesignSystem.WARNING[5], 'width': 5},
                    'thickness': 0.75, 
                    'value': 100
                }
            }
        ))
        
        if val_pct >= 100:
            fig.add_annotation(
                x=0.5, y=1.05,
                text="★ META SUPERADA",
                showarrow=False,
                font=dict(color=DesignSystem.SUCCESS[5], size=9, weight="bold")
            )
        
        fig.update_layout(
            height=120, 
            margin=dict(l=5, r=5, t=25, b=5), 
            paper_bgcolor='rgba(0,0,0,0)', 
            font={'family': "Inter, sans-serif"}
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Análisis de cumplimiento de meta.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore

class OpsTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure("Sin datos de tendencia")
        
        data_source = node.get("data", node)
        all_categories = (
            data_source.get("categories") or 
            data_source.get("months") or 
            data_source.get("meses") or 
            MESES
        )
        series_list = data_source.get("series", [])
        
        if not series_list:
            return self._create_empty_figure("Sin series de datos")
        
        current_month = get_current_month()
        categories = all_categories[:current_month]
        
        fig = go.Figure()
        has_valid_data = False
        
        color_actual = DesignSystem.BRAND[5]
        color_anterior = DesignSystem.BRAND[3]
        color_meta = DesignSystem.WARNING[5]
        
        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", f"Serie {idx}")
            s_data = serie.get("data", [])
            
            s_data_filtered = s_data[:current_month]
            
            is_meta = "meta" in s_name.lower()
            is_anterior = "anterior" in s_name.lower() or "2024" in s_name or "2025" in s_name
            is_actual = "actual" in s_name.lower() or "2025" in s_name or "2026" in s_name
            
            x_clean, y_clean = clean_series(categories, s_data_filtered)
            
            if y_clean and any(v > 0 for v in y_clean):
                has_valid_data = True
            
            if is_meta:
                fig.add_trace(go.Scatter(
                    x=x_clean, y=y_clean,
                    name=s_name,
                    mode='lines+markers',
                    line=dict(color=color_meta, width=2, dash='dot'),
                    marker=dict(size=4)
                ))
            elif is_anterior and not is_actual:
                fig.add_trace(go.Bar(
                    x=x_clean, y=y_clean,
                    name=s_name,
                    marker_color=color_anterior,
                    opacity=0.6
                ))
            else:
                fig.add_trace(go.Bar(
                    x=x_clean, y=y_clean,
                    name=s_name,
                    marker_color=color_actual
                ))
        
        if not has_valid_data:
            return self._create_empty_figure("Sin datos válidos")
        
        fig.update_layout(
            barmode='group',
            height=300,
            margin=dict(t=30, b=40, l=50, r=20),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            xaxis=dict(showgrid=False, color=DesignSystem.SLATE[5]),
            yaxis=dict(showgrid=True, gridcolor=DesignSystem.SLATE[2], color=DesignSystem.SLATE[5]),
            font=dict(family="Inter, sans-serif", color=DesignSystem.SLATE[6])
        )
        
        return fig

    def render_detail(self, data_context):
        return None

class OpsDonutChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-pie", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure("Sin datos")
        
        data_source = node.get("data", node)
        labels = data_source.get("labels") or data_source.get("categories", [])
        values = data_source.get("values", [])
        
        if not labels or not values:
            return self._create_empty_figure("Sin datos de categorías")
        
        clean_values = [safe_float(v) for v in values]
        
        if not any(v > 0 for v in clean_values):
            return self._create_empty_figure("Sin valores válidos")
        
        fig = go.Figure(go.Pie(
            labels=labels,
            values=clean_values,
            hole=0.5,
            textinfo='percent',
            textposition='outside',
            marker=dict(colors=[
                DesignSystem.BRAND[5], DesignSystem.BRAND[4], DesignSystem.BRAND[3],
                DesignSystem.INFO[5], DesignSystem.SUCCESS[5], DesignSystem.WARNING[5]
            ])
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(orientation="v", y=0.5, x=1.05, font=dict(color=DesignSystem.SLATE[6]))
        )
        
        return fig

    def render_detail(self, data_context):
        return None

class OpsHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure("Sin datos")
        
        data_source = node.get("data", node)
        categories = data_source.get("categories") or data_source.get("labels", [])
        series_list = data_source.get("series", [])
        
        if not categories:
            return self._create_empty_figure("Sin categorías")
        
        fig = go.Figure()
        
        for serie in series_list:
            s_name = serie.get("name", "Valor")
            s_data = serie.get("data", [])
            
            clean_data = [safe_float(v) for v in s_data]
            
            fig.add_trace(go.Bar(
                y=categories,
                x=clean_data,
                name=s_name,
                orientation='h',
                marker_color=DesignSystem.BRAND[5]
            ))
        
        fig.update_layout(
            barmode='stack',
            height=max(300, len(categories) * 35),
            margin=dict(l=120, r=40, t=30, b=40),
            yaxis=dict(autorange="reversed", color=DesignSystem.SLATE[5]),
            xaxis=dict(color=DesignSystem.SLATE[5]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=len(series_list) > 1,
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
            font=dict(family="Inter, sans-serif", color=DesignSystem.SLATE[6])
        )
        
        return fig

    def render_detail(self, data_context):
        return None

class OpsTableStrategy:
    def __init__(self, screen_id, table_key):
        self.screen_id = screen_id
        self.table_key = table_key

    def _resolve_table_data(self, data_context):
        from services.data_manager import data_manager
        
        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {}) # type: ignore
        inject_paths = screen_config.get("inject_paths", {})
        
        path = inject_paths.get(self.table_key)
        if not path:
            return safe_get(data_context, ["operational", "dashboard", "tables", self.table_key])
        
        return safe_get(data_context, path)

    def render(self, data_context, **kwargs):
        node = self._resolve_table_data(data_context)
        
        if not node:
            return dmc.Center(
                dmc.Stack([
                    DashIconify(icon="tabler:table-off", width=40, color=DesignSystem.SLATE[4]),
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
        
        if not rows:
            return dmc.Text("Sin filas de datos", c="dimmed", ta="center", py="xl") # type: ignore
        
        return dmc.Table(
            [
                dmc.TableThead(
                    dmc.TableTr([
                        dmc.TableTh(
                            str(h), 
                            style={
                                "fontSize": "11px", 
                                "fontWeight": "600", 
                                "whiteSpace": "nowrap",
                                "backgroundColor": DesignSystem.SLATE[0],
                                "color": DesignSystem.SLATE[7],
                                "padding": "8px 12px"
                            }
                        ) 
                        for h in headers
                    ])
                ),
                dmc.TableTbody([
                    dmc.TableTr([
                        dmc.TableTd(
                            str(cell) if cell is not None else "", 
                            style={
                                "fontSize": "11px", 
                                "whiteSpace": "nowrap",
                                "padding": "6px 12px"
                            }
                        ) 
                        for cell in row
                    ]) 
                    for row in rows[:50]
                ])
            ], 
            striped=True, # type: ignore
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
            style={"width": "100%"}
        )


class OpsMapStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title="Mapa de Rutas", icon="tabler:map-2", color="indigo", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context):
        return self._create_empty_figure("Mapa no disponible")

    def render_detail(self, data_context):
        return None


class OpsComboChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", layout_config=None):
        super().__init__(title=title, color=color, icon=icon, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure()
        
        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])
        
        if not categories or not series_list:
            return self._create_empty_figure("Sin datos")
        
        fig = go.Figure()
        
        for serie in series_list:
            s_name = serie.get("name", "")
            s_data = serie.get("data", [])
            s_type = serie.get("type", "bar")
            
            clean_data = [safe_float(v) for v in s_data]
            
            if s_type == "line":
                fig.add_trace(go.Scatter(
                    x=categories, y=clean_data,
                    name=s_name,
                    mode='lines+markers',
                    line=dict(color=DesignSystem.SUCCESS[5], width=3),
                    marker=dict(size=6),
                    yaxis='y2'
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories, y=clean_data,
                    name=s_name,
                    marker_color=DesignSystem.BRAND[5]
                ))
        
        fig.update_layout(
            height=350,
            margin=dict(t=30, b=40, l=40, r=40),
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            yaxis=dict(title="", color=DesignSystem.SLATE[5]),
            yaxis2=dict(title="", overlaying='y', side='right', color=DesignSystem.SLATE[5]),
            font=dict(family="Inter, sans-serif", color=DesignSystem.SLATE[6])
        )
        
        return fig

    def render_detail(self, data_context):
        return None