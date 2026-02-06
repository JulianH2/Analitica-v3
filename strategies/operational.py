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
BAR_WIDTH = 0.35
BAR_GAP = 0.2


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
            "label_prev_year": node.get("label_prev_year", f"Vs {datetime.now().year - 1}"),
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
        return dmc.Text("Detalle de metrica operacional.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


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
            "label_prev_year": node.get("label_prev_year", f"Vs {datetime.now().year - 1}"),
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
            bar_color = DesignSystem.NEXA_GREEN
        elif val_pct >= 80:
            bar_color = DesignSystem.NEXA_GOLD
        else:
            bar_color = DesignSystem.NEXA_RED
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val_pct,
            number={
                'suffix': "%", 
                'font': {'size': 20, 'weight': 'bold', 'color': DesignSystem.NEXA_BLACK}, 
                'valueformat': '.1f'
            },
            gauge={
                'axis': {'range': [0, max(val_pct, 100) * 1.1], 'visible': False},
                'bar': {'color': bar_color, 'thickness': 0.7},
                'bgcolor': DesignSystem.NEXA_GRAY_LIGHT,
                'borderwidth': 0,
                'threshold': {
                    'line': {'color': DesignSystem.NEXA_GRAY, 'width': 3},
                    'thickness': 0.8, 
                    'value': 100
                }
            }
        ))
        if val_pct >= 100:
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
            margin=dict(l=10, r=10, t=20, b=10), 
            paper_bgcolor='rgba(0,0,0,0)', 
            font={'family': DesignSystem.TYPOGRAPHY["family"]}
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Analisis de cumplimiento de meta.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore


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
        color_actual = DesignSystem.NEXA_BLUE
        color_anterior = DesignSystem.NEXA_ORANGE
        color_meta = DesignSystem.NEXA_GRAY
        
        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", f"Serie {idx}")
            s_data = serie.get("data", [])
            
            s_data_filtered = s_data[:current_month]
            
            is_meta = "meta" in s_name.lower()
            is_anterior = "anterior" in s_name.lower() or "2024" in s_name
            is_actual = "actual" in s_name.lower() or "2025" in s_name
            
            x_clean, y_clean = clean_series(categories, s_data_filtered)
            
            if y_clean and any(v > 0 for v in y_clean):
                has_valid_data = True
            
            if is_meta:
                fig.add_trace(go.Scatter(
                    x=x_clean, y=y_clean,
                    name=s_name,
                    mode='lines+markers',
                    line=dict(color=color_meta, width=2, dash='dash'),
                    marker=dict(size=5, symbol='diamond')
                ))
            elif is_anterior and not is_actual:
                fig.add_trace(go.Bar(
                    x=x_clean, y=y_clean,
                    name=s_name,
                    marker_color=color_anterior,
                    marker_line_width=0,
                    width=BAR_WIDTH
                ))
            else:
                fig.add_trace(go.Bar(
                    x=x_clean, y=y_clean,
                    name=s_name,
                    marker_color=color_actual,
                    marker_line_width=0,
                    width=BAR_WIDTH
                ))
        
        if not has_valid_data:
            return self._create_empty_figure("Sin datos validos")
        
        fig.update_layout(
            barmode='group',
            bargap=BAR_GAP,
            bargroupgap=0.1,
            height=300,
            margin=dict(t=20, b=40, l=50, r=20),
            legend=dict(
                orientation="h", 
                y=1.08, 
                x=0.5, 
                xanchor="center",
                font=dict(size=10, color=DesignSystem.NEXA_BLACK)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            xaxis=dict(
                showgrid=False, 
                tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY),
                tickangle=0
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor=DesignSystem.SLATE[2],
                gridwidth=1,
                tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)
            ),
            font=dict(family=DesignSystem.TYPOGRAPHY["family"], color=DesignSystem.NEXA_BLACK)
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
            return self._create_empty_figure("Sin datos de categorias")
        
        clean_values = [safe_float(v) for v in values]
        
        if not any(v > 0 for v in clean_values):
            return self._create_empty_figure("Sin valores validos")
        donut_colors = DesignSystem.CHART_DONUT_COLORS[:len(labels)]
        
        fig = go.Figure(go.Pie(
            labels=labels,
            values=clean_values,
            hole=0.55,
            textinfo='percent',
            textposition='outside',
            textfont=dict(size=10, color=DesignSystem.NEXA_BLACK),
            marker=dict(
                colors=donut_colors,
                line=dict(color='white', width=2)
            ),
            pull=[0.02] * len(labels)
        ))
        
        fig.update_layout(
            height=320,
            margin=dict(t=20, b=20, l=20, r=100),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="v", 
                y=0.5, 
                x=1.02,
                font=dict(size=10, color=DesignSystem.NEXA_BLACK),
                bgcolor='rgba(0,0,0,0)'
            ),
            font=dict(family=DesignSystem.TYPOGRAPHY["family"])
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
        meta_value = data_source.get("meta", None)

        if not categories or not series_list:
            return self._create_empty_figure("Sin datos validos")

        fig = go.Figure()

        for serie in series_list:
            s_name = serie.get("name", "Ingreso")
            s_data = serie.get("data", [])

            clean_data = [safe_float(v) for v in s_data]

            bar_colors = []
            for v in clean_data:
                if meta_value is not None and v >= meta_value:
                    bar_colors.append(DesignSystem.NEXA_GREEN)
                else:
                    bar_colors.append(DesignSystem.NEXA_ORANGE)

            fig.add_trace(go.Bar(
                y=categories,
                x=clean_data,
                orientation="h",
                marker=dict(color=bar_colors),
                width=0.95,
                name=s_name
            ))

        if meta_value is not None:
            fig.add_vline(
                x=meta_value,
                line_width=2,
                line_dash="dash",
                line_color=DesignSystem.NEXA_GRAY
            )

        chart_height = max(380, len(categories) * 36)

        fig.update_layout(
            height=chart_height,
            margin=dict(l=130, r=30, t=20, b=20),

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            bargap=0.02,

            yaxis=dict(
                autorange="reversed",
                showgrid=False,
                tickfont=dict(size=10, color=DesignSystem.NEXA_BLACK)
            ),

            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(120,120,120,0.10)",
                gridwidth=0.5,
                tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)
            ),

            showlegend=False,
            font=dict(
                family=DesignSystem.TYPOGRAPHY["family"],
                color=DesignSystem.NEXA_BLACK
            )
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
                    DashIconify(icon="tabler:table-off", width=40, color=DesignSystem.NEXA_GRAY),
                    dmc.Text(f"Sin datos: {self.table_key}", c="dimmed", size="sm") # type: ignore
                ], align="center", gap="xs"),
                py="xl"
            )

        headers = node.get("headers", [])
        rows = node.get("rows", [])
        summary = node.get("summary", {})
        
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

        if summary:
            summary_row = dmc.TableTr([
                dmc.TableTd(str(summary.get(h.lower().replace(" ", "_"), "---")),
                    style={"fontSize": "11px", "fontWeight": "bold", "backgroundColor": DesignSystem.NEXA_GRAY_LIGHT})
                for h in headers
            ])
            table_rows.append(summary_row)

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


class OpsMapStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title="Mapa de Rutas", icon="tabler:map-2", color="indigo", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node or "data" not in node:
            return self._create_empty_figure("Mapa no disponible")
            
        routes = node["data"].get("routes", [])
        fig = go.Figure()

        for route in routes:
            fig.add_trace(go.Scattergeo(
                lat = [route["origin"]["lat"], route["destination"]["lat"]],
                lon = [route["origin"]["lng"], route["destination"]["lng"]],
                mode = 'lines+markers',
                line = dict(width = 2, color = DesignSystem.NEXA_BLUE),
                marker = dict(size = 6, color = DesignSystem.NEXA_ORANGE)
            ))

        fig.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            geo = dict(
                scope='north america', 
                projection_type='azimuthal equal area', 
                showland=True, 
                landcolor=DesignSystem.NEXA_GRAY_LIGHT,
                showocean=True,
                oceancolor='#e8f4fd'
            )
        )
        return fig

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
        
        for idx, serie in enumerate(series_list):
            s_name = serie.get("name", "")
            s_data = serie.get("data", [])
            s_type = serie.get("type", "bar")
            
            clean_data = [safe_float(v) for v in s_data]
            
            if s_type == "line":
                fig.add_trace(go.Scatter(
                    x=categories, y=clean_data,
                    name=s_name,
                    mode='lines+markers',
                    line=dict(color=DesignSystem.NEXA_GREEN, width=3),
                    marker=dict(size=7, symbol='circle'),
                    yaxis='y2'
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories, y=clean_data,
                    name=s_name,
                    marker_color=DesignSystem.NEXA_BLUE,
                    width=BAR_WIDTH
                ))
        
        fig.update_layout(
            height=320,
            margin=dict(t=20, b=40, l=50, r=50),
            legend=dict(
                orientation="h", 
                y=1.08, 
                x=0.5, 
                xanchor="center",
                font=dict(size=10)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',
            bargap=BAR_GAP,
            xaxis=dict(
                showgrid=False,
                tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=DesignSystem.SLATE[2],
                tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)
            ),
            yaxis2=dict(
                overlaying='y', 
                side='right',
                showgrid=False,
                tickfont=dict(size=10, color=DesignSystem.NEXA_GREEN)
            ),
            font=dict(family=DesignSystem.TYPOGRAPHY["family"], color=DesignSystem.NEXA_BLACK)
        )
        
        return fig

    def render_detail(self, data_context):
        return None