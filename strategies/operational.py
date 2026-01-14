import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors

class FleetEfficiencyStrategy(KPIStrategy):
    def __init__(self, color="green", has_detail=True):
        super().__init__(title="Eficiencia de Flota", color=color, icon="tabler:truck-delivery", has_detail=has_detail)

    def get_card_config(self, data_context):
        try:
            val = data_context["operaciones"]["dashboard"]["utilizacion"].get("valor", 0)
        # Fallback de datos para evitar errores de renderizado
        except (KeyError, TypeError):
            val = 0
        return {"title": self.title, "value": f"{val:,.1f}%"}

    def get_figure(self, data_context):
        try:
            val = data_context["operaciones"]["dashboard"]["utilizacion"]["valor"]
        except (KeyError, TypeError):
            val = 0
        
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.SUCCESS[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val, 
            number={'suffix': "%", 'font': {'size': 20, 'weight': 'bold'}}, 
            gauge={
                'axis': {'range': [0, 100], 'visible': False}, 
                'bar': {'color': hex_color, 'thickness': 0.8}, 
                'bgcolor': "rgba(148, 163, 184, 0.05)"
            }, 
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        # Ajuste de altura estandarizado para sintonía visual
        fig.update_layout(
            height=DesignSystem.GAUGE_HEIGHT, 
            margin=dict(l=15, r=15, t=35, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    def render_detail(self, data_context): 
        return dmc.Text("Detalle de indicador...", c="dimmed", size="sm") # type: ignore
    
class OpsGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="$", section="dashboard", has_detail=True):
        super().__init__(title=title, color=color, icon="tabler:gauge", has_detail=has_detail)
        self.key, self.prefix, self.section = key, prefix, section

    def get_card_config(self, data_context):
        try:
            node = data_context.get("operaciones", {}).get(self.section, {}).get("indicadores", {}).get(self.key, {})
            val = node.get("valor", 0)
        except (KeyError, AttributeError):
            val = 0
        return {"title": self.title, "value": f"{self.prefix}{val:,.2f}"}

    def get_figure(self, data_context):
        try:
            node = data_context.get("operaciones", {}).get(self.section, {}).get("indicadores", {}).get(self.key, {})
        except (KeyError, AttributeError):
            node = {"valor": 0, "meta": 100}
            
        val, meta = node.get("valor", 0), node.get("meta", 100)
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val, 
            number={'prefix': self.prefix, 'font': {'size': 22, 'weight': 'bold'}}, 
            gauge={
                'axis': {'range': [None, meta * 1.2], 'visible': False}, 
                'bar': {'color': hex_color, 'thickness': 0.8}, 
                'bgcolor': "rgba(148, 163, 184, 0.05)"
            }, 
            domain={'x': [0, 1], 'y': [0.15, 1]}
        ))
        fig.add_annotation(x=0.5, y=0, text=f"Meta: {self.prefix}{meta:,.0f}", showarrow=False, font=dict(size=10))
        fig.update_layout(
            height=DesignSystem.GAUGE_HEIGHT, 
            margin=dict(l=15, r=15, t=35, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    def render_detail(self, data_context): 
        return dmc.Text("Detalle de indicador...", c="dimmed", size="sm") # type: ignore
    
class OpsComparisonStrategy(KPIStrategy):
    def __init__(self, title, data_key, color, section="dashboard", has_detail=True):
        super().__init__(title=title, color=color, icon="tabler:arrows-diff", has_detail=has_detail)
        self.data_key, self.section = data_key, section

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = data_context.get("operaciones", {}).get(self.section, {}).get("graficas", {}).get(self.data_key, {"meses": [], "actual": [], "anterior": []})
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=self.hex_color))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.update_layout(barmode='group', margin=dict(t=40, b=20))
        return fig

    def render_detail(self, data_context): return None

class PerformanceGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="", section="rendimientos", has_detail=True):
        super().__init__(title=title, color=color, icon="tabler:chart-candle", has_detail=has_detail)
        self.key, self.prefix, self.section = key, prefix, section

    def get_card_config(self, data_context):
        try:
            node = data_context.get("operaciones", {}).get(self.section, {}).get("indicadores", {}).get(self.key, {})
            val = node.get("valor", 0)
        except (KeyError, AttributeError):
            val = 0
        return {"title": self.title, "value": f"{self.prefix}{val:,.2f}"}

    def get_figure(self, data_context):
        try:
            node = data_context.get("operaciones", {}).get(self.section, {}).get("indicadores", {}).get(self.key, {})
        except (KeyError, AttributeError):
            node = {"valor": 0, "meta": 1.0}
            
        val, target = node.get("valor", 0), node.get("meta") or 1.0
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val, 
            number={'prefix': self.prefix, 'font': {'size': 22, 'weight': 'bold'}}, 
            gauge={
                'axis': {'range': [None, target * 1.2], 'visible': False}, 
                'bar': {'color': hex_color, 'thickness': 0.8}, 
                'bgcolor': "rgba(148, 163, 184, 0.05)"
            }, 
            domain={'x': [0, 1], 'y': [0.15, 1]}
        ))
        fig.add_annotation(x=0.5, y=0, text=f"Meta: {target:,.2f}", showarrow=False, font=dict(size=10))
        fig.update_layout(
            height=DesignSystem.GAUGE_HEIGHT, 
            margin=dict(l=15, r=15, t=35, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    def render_detail(self, data_context): 
        return dmc.Text("Detalle de indicador...", c="dimmed", size="sm") # type: ignore

class OpsPieStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Ingreso Viaje Por Tipo Operación", icon="tabler:chart-pie", color="indigo", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["dashboard"]["graficas"]["mix_operacion"]
        except: ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.6, textinfo='percent')])
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=30, b=40))
        return fig

    def render_detail(self, data_context): return None

class BalanceUnitStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Balanceo Ingresos por Unidad", icon="tabler:scale", color="blue", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["dashboard"]["graficas"]["balanceo_unidades"]
        except: ds = {"unidades": [], "montos": []}
        fig = go.Figure(go.Bar(y=ds["unidades"], x=ds["montos"], orientation='h', marker_color=self.hex_color))
        fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=30, b=20, l=10, r=20))
        return fig

    def render_detail(self, data_context): return None

class CostUtilityStackedStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Costo Viaje Total y % Utilidad", icon="tabler:chart-arrows", color="indigo", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["costos"]["graficas"]["mensual_utilidad"]
        except: ds = {"meses": [], "costo": [], "utilidad_pct": []}
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["costo"], name="Costo Total (M)", marker_color=self.hex_color))
        fig.add_trace(go.Scatter(x=ds["meses"], y=ds["utilidad_pct"], name="% Utilidad", yaxis="y2", line=dict(color=SemanticColors.INGRESO, width=4, shape='spline')))
        fig.update_layout(
            legend=dict(orientation="h", y=1.1, x=0), 
            yaxis2=dict(overlaying="y", side="right", range=[0, 100], ticksuffix="%", showgrid=False), 
            margin=dict(t=40, b=20),
            hovermode="x unified"
        )
        return fig

    def render_detail(self, data_context): return None

class OpsTableStrategy:
    def render_rutas(self, data_context):
        try: ds = data_context["operaciones"]["dashboard"]["tablas"]["rutas_cargado"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c="dimmed") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])), 
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

    def render_tabbed_table(self, data_context, tab_key): return dmc.Text(f"Cargando {tab_key}...", size="sm", py="xl", ta="center", c="dimmed") # type: ignore

class CostBreakdownStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Costo Total por Concepto", icon="tabler:chart-bar", color="red", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["costos"]["graficas"]["desglose_conceptos"]
        except: ds = {"montos": [], "conceptos": []}
        fig = go.Figure(go.Bar(x=ds["montos"], y=ds["conceptos"], orientation='h', marker_color=self.hex_color))
        fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=30, b=20, l=10, r=20))
        return fig

    def render_detail(self, data_context): return None

class CostTableStrategy:
    def render_margen_ruta(self, data_context):
        try: ds = data_context["operaciones"]["costos"]["tablas"]["margen_ruta"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c="dimmed") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])), 
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

class PerformanceTrendStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Tendencia Rendimiento Real (Kms/Lt)", icon="tabler:timeline", color="indigo", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["rendimientos"]["graficas"]["tendencia"]
        except: ds = {"meses": [], "actual": [], "anterior": []}
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ds["meses"], y=ds["actual"], name="2025", line=dict(color=self.hex_color, width=4, shape='spline')))
        fig.add_trace(go.Scatter(x=ds["meses"], y=ds["anterior"], name="2024", line=dict(color=DesignSystem.SLATE[3], width=2, dash="dash")))
        fig.update_layout(hovermode="x unified", margin=dict(t=40, b=20))
        return fig

    def render_detail(self, data_context): return None

class PerformanceMixStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Distribución de Rendimiento por Operación", icon="tabler:chart-pie-2", color="indigo", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["rendimientos"]["graficas"]["mix_operacion"]
        except: ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.6, marker=dict(colors=DesignSystem.CHART_COLORS))])
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=30, b=40))
        return fig

    def render_detail(self, data_context): return None

class PerformanceTableStrategy:
    def render_unit(self, data_context):
        try: ds = data_context["operaciones"]["rendimientos"]["tablas"]["unidad"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c="dimmed") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])), 
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

    def render_operador(self, data_context):
        try: ds = data_context["operaciones"]["rendimientos"]["tablas"]["operador"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c="dimmed") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])), 
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

class RouteMapStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Mapa de Rutas Activas", icon="tabler:map-2", color="indigo", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["rutas"]["mapa"]["puntos"]
        except: ds = []
        lats, lons, nombres = [p["lat"] for p in ds], [p["lon"] for p in ds], [p["nombre"] for p in ds]
        fig = go.Figure(go.Scattermapbox(lat=lats, lon=lons, mode='markers+lines', marker=dict(size=12, color=self.hex_color), text=nombres))
        fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=4, mapbox_center={"lat": 23.6, "lon": -102.5}, margin=dict(l=0, r=0, t=0, b=0))
        return fig

    def render_detail(self, data_context): return None

class RouteDetailTableStrategy:
    def render_tabla_rutas(self, data_context):
        try: ds = data_context["operaciones"]["rutas"]["tablas"]["detalle_rutas"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c="dimmed") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])), 
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True, highlightOnHover=True)