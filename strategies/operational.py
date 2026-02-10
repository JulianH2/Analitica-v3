import plotly.graph_objects as go
import dash_mantine_components as dmc
from dash import html
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
        else:
            x_clean.append(x)
            y_clean.append(0)
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

        if not node:
            return {
                "title": self.title,
                "main_value": "---",
                "icon": self.icon,
                "color": self.color,
                "raw_data": []
            }

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
        return dmc.Text("Detalle de métrica operacional.", size="sm", c=SemanticColors.TEXT_MUTED)

class OpsGaugeStrategy(KPIStrategy):
    def __init__(self, screen_id, kpi_key, title, color="indigo", icon="tabler:gauge", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.kpi_key = kpi_key

    def get_card_config(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        
        if isinstance(raw_node, (int, float)):
            node = {"value": raw_node, "value_formatted": str(raw_node)}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node if isinstance(raw_node, dict) else {}

        if not node:
            return {
                "title": self.title,
                "main_value": "---",
                "icon": self.icon,
                "color": self.color,
                "raw_data": []
            }

        return {
            "title": self.title,
            "icon": self.icon,
            "color": self.color,
            "value": node.get("value_formatted", "---"),
            "main_value": node.get("value_formatted", "---"),
            "vs_last_year_formatted": node.get("vs_last_year_formatted"),
            "vs_last_year_delta": node.get("vs_last_year_delta"),
            "vs_last_year_delta_formatted": node.get("vs_last_year_delta_formatted"),
            "target_formatted": node.get("target_formatted"),
            "target_delta": node.get("target_delta"),
            "target_delta_formatted": node.get("target_delta_formatted"),
            "ytd_formatted": node.get("ytd_formatted"),
            "ytd_delta": node.get("ytd_delta"),
            "ytd_delta_formatted": node.get("ytd_delta_formatted"),
            "status": node.get("status")
        }

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        raw_node = self._resolve_kpi_data(data_context, self.screen_id, self.kpi_key)
        
        if isinstance(raw_node, (int, float)):
            current = raw_node
            target = None
            vs_last_year = None
        elif raw_node and isinstance(raw_node, dict):
            current = safe_float(raw_node.get("value", 0))
            target = safe_float(raw_node.get("target")) if raw_node.get("target") else None
            vs_last_year = safe_float(raw_node.get("vs_last_year")) if raw_node.get("vs_last_year") else None
        else:
            return self._create_empty_figure()
        max_val = safe_max(current, target or 0, vs_last_year or 0, 100)
        
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=current,
            number={"font": {"size": 24, "color": DesignSystem.SLATE[8]}},
            gauge={
                "axis": {"range": [0, max_val * 1.2], "tickwidth": 1, "tickcolor": DesignSystem.SLATE[3]},
                "bar": {"color": self.hex_color, "thickness": 0.95},
                "bgcolor": DesignSystem.SLATE[1],
                "borderwidth": 2,
                "bordercolor": DesignSystem.SLATE[2],
                "steps": [{"range": [0, max_val * 1.2], "color": DesignSystem.SLATE[0]}],
                "threshold": {
                    "line": {"color": DesignSystem.DANGER[5] if target else DesignSystem.SLATE[6], "width": 3},
                    "thickness": 0.9,
                    "value": target if target else max_val
                }
            }
        ))
        if target:
            fig.add_annotation(
                x=0.5, y=-0.12,
                text=f"Meta: {target:,.0f}",
                showarrow=False,
                font=dict(size=10, color=DesignSystem.DANGER[6], weight="bold"),
                xref="paper", yref="paper"
            )
        if vs_last_year:
            fig.add_annotation(
                x=0.5, y=-0.22,
                text=f"Año Ant: {vs_last_year:,.0f}",
                showarrow=False,
                font=dict(size=9, color=DesignSystem.SLATE[6]),
                xref="paper", yref="paper"
            )
        
        fig.update_layout(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(l=5, r=5, t=5, b=35),
            font=dict(size=10)
        )
        return fig


class OpsTrendChartStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-line", color="indigo", has_detail=True, layout_config=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "color": self.color, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure()

        data_source = node.get("data", node)
        categories = data_source.get("categories") or data_source.get("months") or []
        series_list = data_source.get("series", [])

        if not categories:
            return self._create_empty_figure("Sin datos temporales")

        current_month = get_current_month()
        
        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_type = s.get("type", "bar")
            s_name = s.get("name", f"Serie {idx}")
            s_data = s.get("data", []) or []
            s_color = s.get("color", self.hex_color)

            past_data = []
            future_data = []
            
            for i, (x, y) in enumerate(zip(categories, s_data)):
                y_val = safe_float(y)
                if i < current_month:
                    past_data.append((x, y_val))
                    future_data.append((x, None))
                else:
                    past_data.append((x, None))
                    future_data.append((x, y_val))

            past_x = [x for x, y in past_data]
            past_y = [y for x, y in past_data]
            future_x = [x for x, y in future_data]
            future_y = [y for x, y in future_data]

            if s_type == "line" or "Meta" in s_name or "Objetivo" in s_name:
                fig.add_trace(go.Scatter(
                    x=past_x, y=past_y, name=s_name,
                    mode='lines+markers',
                    line=dict(color=s_color, width=3, dash='dot' if "Meta" in s_name or "Objetivo" in s_name else 'solid'),
                    marker=dict(size=6),
                    showlegend=True
                ))
                
                fig.add_trace(go.Scatter(
                    x=future_x, y=future_y, name=f"{s_name} (proyección)",
                    mode='lines+markers',
                    line=dict(color=s_color, width=2, dash='dot'),
                    marker=dict(size=4),
                    opacity=0.3,
                    showlegend=False
                ))
            else:
                past_text = [f"${v/1e6:.1f}M" if v and v >= 1e6 else f"${v/1e3:.0f}k" if v and v >= 1000 else f"${v:.0f}" if v else "" for v in past_y]
                future_text = [f"${v/1e6:.1f}M" if v and v >= 1e6 else f"${v/1e3:.0f}k" if v and v >= 1000 else f"${v:.0f}" if v else "" for v in future_y]
                
                fig.add_trace(go.Bar(
                    x=past_x, y=past_y, name=s_name,
                    marker_color=s_color,
                    text=past_text,
                    textposition='outside',
                    textfont=dict(size=9, color=DesignSystem.SLATE[8]),
                    showlegend=True,
                    width=0.35,
                    cliponaxis=False
                ))
                
                fig.add_trace(go.Bar(
                    x=future_x, y=future_y, name=f"{s_name} (futuro)",
                    marker=dict(color=s_color, opacity=0.2),
                    text=future_text,
                    textposition='outside',
                    textfont=dict(size=8, color=DesignSystem.SLATE[5]),
                    showlegend=False,
                    width=0.35,
                    cliponaxis=False
                ))

        height_val = self.layout.get("height", 350)
        plotly_height = height_val if isinstance(height_val, int) else None

        fig.update_layout(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(t=60, b=50, l=60, r=30),
            height=plotly_height,
            autosize=True,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11)
            ),
            barmode='group',
            bargap=0.40,
            bargroupgap=0.25,
            hovermode='x unified',
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                tickfont=dict(size=10),
                gridcolor=DesignSystem.SLATE[2]
            ),
            uniformtext=dict(mode='hide', minsize=8)
        )
        return fig

class OpsDonutChartStrategy(KPIStrategy):
    def __init__(
        self,
        screen_id,
        chart_key,
        title,
        icon="tabler:chart-pie",
        color="indigo",
        color_map=None,
        has_detail=True,
        layout_config=None
    ):
        super().__init__(
            title=title,
            icon=icon,
            color=color,
            has_detail=has_detail,
            layout_config=layout_config
        )

        self.screen_id = screen_id
        self.chart_key = chart_key
        self.color_map = color_map or {}

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key) or {}
        data_source = node.get("data", node)

        labels = data_source.get("labels", [])
        values = data_source.get("values", [])
        colors = data_source.get("colors", [])
        total = data_source.get("total_formatted", "")

        if not labels or not values:
            return self._create_empty_figure()

        if not colors:
            default_colors = [
                DesignSystem.BRAND[5],
                DesignSystem.SUCCESS[5],
                DesignSystem.WARNING[5],
                DesignSystem.DANGER[5],
                DesignSystem.INFO[5],
                DesignSystem.SLATE[6],
                DesignSystem.SLATE[7],
                DesignSystem.SLATE[8],
            ]
            colors = [default_colors[i % len(default_colors)] for i in range(len(labels))]

        fig_height = self.layout.get("height", 260)

        max_index = max(range(len(values)), key=lambda i: values[i])

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.60,
                    marker=dict(colors=colors, line=dict(color="white", width=2)),
                    textinfo="none",
                    hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
                    pull=[0.05 if i == max_index else 0 for i in range(len(values))],
                )
            ]
        )

        if total:
            fig.add_annotation(
                text=f"<b>Total</b><br>{total}",
                x=0.30,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color=DesignSystem.SLATE[8]),
                xref="paper",
                yref="paper",
            )

        fig.update_traces(
            domain=dict(
                x=[0.0, 0.60],
                y=[0.0, 1.0]
            )
        )

        fig.update_layout(
            height=fig_height,
            autosize=True,
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(t=30, b=20, l=10, r=10),

            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=0.65,
                font=dict(size=10),
                bgcolor="rgba(255,255,255,0.90)",
                bordercolor=DesignSystem.SLATE[3],
                borderwidth=1,
                itemsizing="constant",
            )
        )

        return fig
class OpsHorizontalBarStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:chart-bar", color="indigo", has_detail=True, layout_config=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        if not node:
            return self._create_empty_figure()

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        values = data_source.get("values", [])

        if not categories:
            return self._create_empty_figure("Sin categorías")

        num_bars = len(categories)
        bar_height_px = 50
        min_height = self.layout.get("height", 300)
        calculated_height = max(min_height, num_bars * bar_height_px + 140)

        avg_value = sum(values) / len(values) if values else 0

        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=values,
            y=categories,
            orientation='h',
            marker=dict(color=self.hex_color),
            text=[f"${v/1e6:.2f}M" if v >= 1e6 else f"${v/1e3:.0f}k" if v >= 1000 else f"${v:.0f}" for v in values],
            textposition='outside',
            textfont=dict(size=11, color=DesignSystem.SLATE[8]),
            hovertemplate='<b>%{y}</b><br>$%{x:,.2f}<extra></extra>',
            width=0.65
        ))
        
        fig.add_vline(
            x=avg_value,
            line_width=3,
            line_dash="solid",
            line_color=DesignSystem.WARNING[6],
            annotation_text=f"Promedio: ${avg_value/1e6:.2f}M" if avg_value >= 1e6 else f"${avg_value/1e3:.0f}k",
            annotation_position="top",
            annotation_font_size=11,
            annotation_font_color=DesignSystem.WARNING[7]
        )

        fig.update_layout(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(t=30, b=30, l=180, r=120),
            height=calculated_height,
            showlegend=False,
            xaxis=dict(
                tickfont=dict(size=11),
                gridcolor=DesignSystem.SLATE[2],
                showgrid=True,
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor=DesignSystem.SLATE[3],
                type='linear',
                tickformat='$,.0f'
            ),
            yaxis=dict(
                tickfont=dict(size=11, color=DesignSystem.SLATE[7]),
                automargin=True,
                type='category'
            ),
            bargap=0.35
        )
        return fig


class OpsTableStrategy:
    def __init__(self, screen_id, table_key):
        self.screen_id = screen_id
        self.table_key = table_key

    def render(self, data_context):
        from services.data_manager import data_manager
        screen_config = data_manager.SCREEN_MAP.get(self.screen_id, {})
        inject_paths = screen_config.get("inject_paths", {})
        path = inject_paths.get(self.table_key)
        
        if not path:
            return dmc.Alert("Configuración de tabla no encontrada", color="yellow")
        
        node = safe_get(data_context, path)
        if not node:
            return dmc.Alert("Sin datos disponibles", color="gray", icon=DashIconify(icon="tabler:table-off"))
        
        data_source = node.get("data", node) if isinstance(node, dict) else node
        
        if isinstance(data_source, dict):
            headers = data_source.get("headers", [])
            rows = data_source.get("rows", [])
        elif isinstance(data_source, list) and data_source and isinstance(data_source[0], dict):
            headers = list(data_source[0].keys())
            rows = [[str(row.get(h, "")) for h in headers] for row in data_source]
        else:
            return dmc.Alert("Formato de datos no válido", color="orange")
        
        if not headers:
            return dmc.Alert("Sin estructura de tabla", color="gray")
        
        table_header = dmc.Group(
            justify="space-between",
            mb="xs",
            children=[
                dmc.Text(f"{len(rows)} registros", size="xs", c="dimmed", fw=500)
            ]
        )
        
        table = dmc.Table(
            striped=True,
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
            stickyHeader=True,
            horizontalSpacing="sm",
            verticalSpacing="xs",
            style={"minWidth": "600px"},
            children=[
                dmc.TableThead(
                    dmc.TableTr([
                        dmc.TableTh(
                            h, 
                            style={
                                "fontSize": "10px", 
                                "fontWeight": 700, 
                                "textTransform": "uppercase",
                                "whiteSpace": "nowrap",
                                "padding": "8px 12px"
                            }
                        )
                        for h in headers
                    ]),
                    style={"backgroundColor": "var(--mantine-color-gray-0)"}
                ),
                dmc.TableTbody([
                    dmc.TableTr([
                        dmc.TableTd(
                            str(cell), 
                            style={
                                "fontSize": "11px",
                                "whiteSpace": "nowrap",
                                "padding": "6px 12px"
                            }
                        )
                        for cell in row
                    ])
                    for row in rows[:100]
                ])
            ]
        )
        
        return html.Div([table_header, table])


class OpsMapStrategy(KPIStrategy):
    def __init__(self, screen_id, chart_key, title, icon="tabler:map", color="indigo", has_detail=False, layout_config=None):
        super().__init__(title=title, icon=icon, color=color, has_detail=has_detail, layout_config=layout_config)
        self.screen_id = screen_id
        self.chart_key = chart_key

    def get_card_config(self, data_context):
        return {"title": self.title, "icon": self.icon, "is_chart": True}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        node = self._resolve_chart_data(data_context, self.screen_id, self.chart_key)
        
        if not node:
            return self._create_empty_figure("Sin datos de mapa")
        
        data_source = node.get("data", node)
        routes = data_source.get("routes", [])
        
        if not routes:
            return self._create_empty_figure("Sin rutas disponibles")
        
        fig = go.Figure()
        
        for route in routes:
            lats = route.get("lat", [])
            lons = route.get("lon", [])
            name = route.get("name", "Ruta")
            color = route.get("color", DesignSystem.BRAND[5])
            
            if lats and lons:
                fig.add_trace(go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode='lines+markers',
                    name=name,
                    line=dict(width=3, color=color),
                    marker=dict(size=8, color=color)
                ))
        
        center_lat = 20.5937
        center_lon = -100.3897
        
        if routes:
            all_lats = [lat for r in routes for lat in (r.get("lat", []) or [])]
            all_lons = [lon for r in routes for lon in (r.get("lon", []) or [])]
            if all_lats and all_lons:
                center_lat = sum(all_lats) / len(all_lats)
                center_lon = sum(all_lons) / len(all_lons)
        
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=self.layout.get("height", 600),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.8)"
            )
        )
        
        return fig