import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy

class FleetEfficiencyStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Eficiencia de Flota"}

    def get_figure(self, data_context):
        val = data_context.get("operaciones", {}).get("dashboard", {}).get("utilizacion", {}).get("valor", 0)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={'suffix': "%"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#40c057"}}
        ))
        fig.update_layout(height=180, margin=dict(l=10, r=10, t=30, b=10))
        return fig

    def render_detail(self, data_context):
        return None

class OpsGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="$", section="dashboard"):
        self.title = title
        self.key = key
        self.color = color
        self.prefix = prefix
        self.section = section

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        node = data_context["operaciones"][self.section]["indicadores"].get(self.key, {})
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=node.get("valor", 0),
            number={'prefix': self.prefix, 'font': {'size': 18}},
            gauge={'axis': {'range': [None, node.get("meta", 100) * 1.2]}, 'bar': {'color': self.color}}
        ))
        fig.add_annotation(x=0.5, y=-0.15, text=f"Mes: {node.get('label_mes', '')}", showarrow=False, font=dict(size=10, color="gray"))
        fig.add_annotation(x=0.5, y=-0.30, text=f"YTD: {node.get('label_ytd', '')}", showarrow=False, font=dict(size=10, color="gray"))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=40), paper_bgcolor='rgba(0,0,0,0)')
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle histórico...")

class OpsComparisonStrategy(KPIStrategy):
    def __init__(self, title, data_key, color, section="dashboard"):
        self.title = title
        self.data_key = data_key
        self.color = color
        self.section = section

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        ds = data_context["operaciones"][self.section]["graficas"].get(self.data_key, {"meses": [], "actual": [], "anterior": []})
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=self.color))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color="#ced4da"))
        
        if "meta" in ds:
            fig.add_trace(go.Scatter(x=ds["meses"], y=ds["meta"], name="Meta", line=dict(color="red", dash="dot")))
            
        fig.update_layout(height=300, barmode='group', margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1))
        return fig

    def render_detail(self, data_context):
        return None

class OpsPieStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Ingreso Viaje Por Tipo Operación"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["dashboard"]["graficas"]["mix_operacion"]
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.6)])
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
        return fig

    def render_detail(self, data_context):
        return None

class BalanceUnitStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Balanceo Ingresos por Unidad"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["dashboard"]["graficas"]["balanceo_unidades"]
        fig = go.Figure(go.Bar(y=ds["unidades"], x=ds["montos"], orientation='h', marker_color="#228be6"))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(autorange="reversed"))
        return fig

    def render_detail(self, data_context):
        return None

class OpsTableStrategy:
    def render_rutas(self, data_context):
        ds = data_context["operaciones"]["dashboard"]["tablas"]["rutas_cargado"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h) for h in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c)) for c in r]) for r in ds["r"]])
        ], striped=True, withTableBorder=True) # type: ignore

    def render_tabbed_table(self, data_context, tab_key):
        return dmc.Text(f"Información de {tab_key} cargada dinámicamente...", size="sm", py="xl", ta="center", c="dimmed") # type: ignore

class CostUtilityStackedStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Costo Viaje Total y Monto Utilidad"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["costos"]["graficas"]["mensual_utilidad"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["costo"], name="Costo Total (M)", marker_color="#228be6"))
        fig.add_trace(go.Scatter(x=ds["meses"], y=ds["utilidad_pct"], name="% Utilidad", yaxis="y2", line=dict(color="#40c057", width=3)))
        fig.update_layout(
            height=350, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1),
            yaxis2=dict(overlaying="y", side="right", range=[0, 100], ticksuffix="%")
        )
        return fig

    def render_detail(self, data_context):
        return None

class CostBreakdownStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Costo Total por Concepto"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["costos"]["graficas"]["desglose_conceptos"]
        fig = go.Figure(go.Bar(x=ds["montos"], y=ds["conceptos"], orientation='h', marker_color="#fa5252"))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(autorange="reversed"))
        return fig

    def render_detail(self, data_context):
        return None

class CostTableStrategy:
    def render_margen_ruta(self, data_context):
        ds = data_context["operaciones"]["costos"]["tablas"]["margen_ruta"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped=True, withTableBorder=True) # type: ignore

class PerformanceGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="", section="rendimientos"):
        self.title = title
        self.key = key
        self.color = color
        self.prefix = prefix
        self.section = section

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        node = data_context["operaciones"][self.section]["indicadores"].get(self.key, {})
        val = node.get("valor", 0)
        target = node.get("meta") or val
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={'prefix': self.prefix, 'font': {'size': 18}},
            gauge={'axis': {'range': [None, target * 1.2]}, 'bar': {'color': self.color}}
        ))
        
        fig.add_annotation(x=0.5, y=-0.15, text=f"Mes: {node.get('label_mes', '')}", showarrow=False, font=dict(size=10))
        fig.add_annotation(x=0.5, y=-0.30, text=f"YTD: {node.get('label_ytd', '')}", showarrow=False, font=dict(size=10))
        
        extra = node.get("extra_info")
        if extra:
            fig.add_annotation(x=0.5, y=0.4, text=f"<b>{extra[0]}</b><br>{extra[1]}", showarrow=False, font=dict(size=11, color="#1c7ed6"))

        fig.update_layout(height=220, margin=dict(l=10, r=10, t=40, b=50), paper_bgcolor='rgba(0,0,0,0)')
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle técnico de rendimientos...")

class PerformanceTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Tendencia Rendimiento Real (Kms/Lt)"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["rendimientos"]["graficas"]["tendencia"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ds["meses"], y=ds["actual"], name="2025", line=dict(color="#228be6", width=3)))
        fig.add_trace(go.Scatter(x=ds["meses"], y=ds["anterior"], name="2024", line=dict(color="#ced4da", dash="dash")))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0))
        return fig

    def render_detail(self, data_context):
        return None

class PerformanceMixStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Distribución por Operación"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["rendimientos"]["graficas"]["mix_operacion"]
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.6)])
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
        return fig

    def render_detail(self, data_context):
        return None

class PerformanceTableStrategy:
    def render_unit(self, data_context):
        ds = data_context["operaciones"]["rendimientos"]["tablas"]["unidad"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped=True, withTableBorder=True) # type: ignore

    def render_operador(self, data_context):
        ds = data_context["operaciones"]["rendimientos"]["tablas"]["operador"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped=True, withTableBorder=True) # type: ignore

class RouteMapStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Mapa de Rutas"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["rutas"]["mapa"]["puntos"]
        lats = [p["lat"] for p in ds]
        lons = [p["lon"] for p in ds]
        nombres = [p["nombre"] for p in ds]
        
        fig = go.Figure(go.Scattermapbox(
            lat=lats, lon=lons, mode='markers+lines',
            marker=dict(size=12, color='#228be6'),
            text=nombres
        ))
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=4,
            mapbox_center={"lat": 23.6, "lon": -102.5},
            height=400, margin=dict(l=0, r=0, t=0, b=0)
        )
        return fig

    def render_detail(self, data_context):
        return None

class RouteDetailTableStrategy:
    def render_tabla_rutas(self, data_context):
        ds = data_context["operaciones"]["rutas"]["tablas"]["detalle_rutas"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped=True, withTableBorder=True, highlightOnHover=True) # type: ignore