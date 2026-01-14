import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors

class AdminRichKPIStrategy(KPIStrategy):
    def __init__(self, section, key, title, icon, color, sub_section="indicadores", has_detail=True):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail)
        self.section, self.key, self.sub_section = section, key, sub_section

    def get_card_config(self, data_context):
        root = data_context.get("administracion", data_context)
        try:
            section_data = root.get(self.section, data_context.get(self.section, {}))
            node = section_data.get(self.sub_section, {}).get(self.key, {"valor": 0})
            val = node.get('valor', 0) if isinstance(node, dict) else node
        except:
            val = 0
            node = {"valor": 0}
            
        return {
            "title": self.title, 
            "node_data": node if isinstance(node, dict) else {"valor": node},
            "value": f"${val/1e6:,.2f}M" if val > 1000 else f"${val:,.2f}", 
            "color": self.color, 
            "icon": self.icon
        }

    def render_detail(self, data_context):
        return dmc.Text("Cargando detalle administrativo...", c="dimmed", size="sm") # type: ignore

class CollectionGaugeStrategy(KPIStrategy):
    def __init__(self, title, val_key, target_key, color, icon="tabler:rebound", has_detail=True):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail)
        self.val_key, self.target_key = val_key, target_key

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        node = data_context.get("administracion", {}).get("facturacion_cobranza", {}).get("indicadores", {})
        val = node.get(self.val_key, {}).get("valor", 0)
        target = node.get(self.target_key, {}).get("valor", 1)
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val, 
            number={'prefix': "$", 'font': {'size': 20, 'weight': 'bold'}}, 
            gauge={'axis': {'range': [None, target * 1.2], 'visible': False}, 'bar': {'color': hex_color, 'thickness': 0.8}, 'bgcolor': "rgba(148, 163, 184, 0.05)"}, 
            domain={'x': [0, 1], 'y': [0.15, 1]}
        ))
        fig.add_annotation(x=0.5, y=0.05, text=f"Meta: ${target/1e6:,.1f}M", showarrow=False, font=dict(size=10))
        fig.update_layout(height=DesignSystem.GAUGE_HEIGHT, margin=dict(l=15, r=15, t=35, b=5))
        return fig
    def render_detail(self, data_context): return dmc.Text("Detalle de cobranza...", c="dimmed") # type: ignore
    
class CollectionComparisonStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Facturado 2025 vs. 2024", color="indigo", icon="tabler:arrows-diff", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["facturacion_cobranza"]["graficas"]["comparativa"]
        except:
            ds = {"meses": [], "actual": [], "anterior": []}
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=self.hex_color))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.update_layout(barmode='group', margin=dict(t=40, b=20))
        return fig

    def render_detail(self, data_context):
        return None

class CollectionMixStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Cartera M.N. por Clasificación", color="indigo", icon="tabler:chart-pie", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["facturacion_cobranza"]["graficas"]["mix"]
        except:
            ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], 
            values=ds["values"], 
            hole=.6, 
            marker=dict(colors=[SemanticColors.META, SemanticColors.INGRESO, SemanticColors.EGRESO])
        )])
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=30, b=40))
        return fig

    def render_detail(self, data_context):
        return None

class DebtorsStackedStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Cartera M.N. por Cliente", color="indigo", icon="tabler:users", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["facturacion_cobranza"]["graficas"]["stack"]
        except:
            ds = {"clientes": [], "por_vencer": [], "sin_carta": [], "vencido": []}
        fig = go.Figure()
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["por_vencer"], name="Vigente", orientation='h', marker_color=SemanticColors.INGRESO))
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["sin_carta"], name="Pendiente", orientation='h', marker_color=SemanticColors.META))
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["vencido"], name="Vencido", orientation='h', marker_color=SemanticColors.EGRESO))
        fig.update_layout(barmode='stack', yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=30, b=10))
        return fig

    def render_detail(self, data_context):
        return None

class CollectionAgingTableStrategy:
    def render(self, data_context):
        try:
            ds = data_context["administracion"]["facturacion_cobranza"]["antiguedad"]
        except:
            return dmc.Text("Sin datos de antigüedad", c="dimmed", ta="center", py="xl") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True, highlightOnHover=True)

class BankDailyEvolutionStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Flujo Diario de Caja", color="green", icon="tabler:timeline", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["bancos"]["graficas"]["diaria"]
        except:
            ds = {"dias": [], "ingresos": [], "egresos": []}
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ds["dias"], y=ds["ingresos"], name="Ingresos", line=dict(color=SemanticColors.INGRESO, width=4, shape='spline')))
        fig.add_trace(go.Scatter(x=ds["dias"], y=ds["egresos"], name="Egresos", line=dict(color=SemanticColors.EGRESO, width=4, shape='spline')))
        fig.update_layout(hovermode="x unified", margin=dict(t=40, b=20))
        return fig

    def render_detail(self, data_context):
        return None

class BankDonutStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Saldo por Banco", color="orange", icon="tabler:building-bank", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["bancos"]["graficas"]["donut"]
        except:
            ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.6, marker=dict(colors=DesignSystem.CHART_COLORS))])
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1), margin=dict(t=30, b=40))
        return fig

    def render_detail(self, data_context):
        return None

class BankConceptsStrategy:
    def render(self, data_context):
        try:
            ds = data_context["administracion"]["bancos"]["conceptos"]
        except:
            return dmc.Text("Sin datos bancarios", c="dimmed", ta="center", py="xl") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)
        
class PayablesGaugeStrategy(KPIStrategy):
    def __init__(self, title, val_key, target_key, color, icon="tabler:wallet", has_detail=True):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail)
        self.val_key, self.target_key = val_key, target_key
    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        node = data_context.get("administracion", {}).get("cuentas_por_pagar", {}).get("indicadores", {})
        val = node.get(self.val_key, {}).get("valor", 0)
        target = node.get(self.target_key, {}).get("valor", 1)
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val, 
            number={'prefix': "$", 'font': {'size': 20, 'weight': 'bold'}}, 
            gauge={'axis': {'range': [None, target * 1.2], 'visible': False}, 'bar': {'color': hex_color, 'thickness': 0.8}, 'bgcolor': "rgba(148, 163, 184, 0.05)"}, 
            domain={'x': [0, 1], 'y': [0.15, 1]}
        ))
        fig.add_annotation(x=0.5, y=0.05, text=f"Meta: ${target/1e6:,.1f}M", showarrow=False, font=dict(size=10))
        fig.update_layout(height=DesignSystem.GAUGE_HEIGHT, margin=dict(l=15, r=15, t=35, b=5))
        return fig
    def render_detail(self, data_context): return dmc.Text("Detalle de pagos...", c="dimmed") # type: ignore
    
class PayablesComparisonStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Cuentas x Pagar 2025 vs. 2024", color="red", icon="tabler:scale", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["comparativa"]
        except:
            ds = {"meses": [], "actual": [], "anterior": []}
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=self.hex_color))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.update_layout(barmode='group', margin=dict(t=40, b=20))
        return fig

    def render_detail(self, data_context):
        return None

class PayablesMixStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Saldo por Clasificación", color="red", icon="tabler:chart-pie-2", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["mix"]
        except:
            ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], 
            values=ds["values"], 
            hole=.6, 
            marker=dict(colors=[SemanticColors.INGRESO, SemanticColors.EGRESO])
        )])
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1), margin=dict(t=30, b=40))
        return fig

    def render_detail(self, data_context):
        return None

class SupplierSaldoStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Saldo por Proveedor", color="red", icon="tabler:truck-loading", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["saldo_proveedor"]
        except:
            ds = {"prov": [], "por_vencer": [], "vencido": []}
        fig = go.Figure()
        fig.add_trace(go.Bar(y=ds["prov"], x=ds["por_vencer"], name="Vigente", orientation='h', marker_color=SemanticColors.INGRESO))
        fig.add_trace(go.Bar(y=ds["prov"], x=ds["vencido"], name="Vencido", orientation='h', marker_color=SemanticColors.EGRESO))
        fig.update_layout(barmode='stack', yaxis=dict(autorange="reversed"), margin=dict(l=10, r=10, t=30, b=10))
        return fig

    def render_detail(self, data_context):
        return None

class PayablesAgingTableStrategy:
    def render(self, data_context):
        try:
            ds = data_context["administracion"]["cuentas_por_pagar"]["antiguedad"]
        except:
            return dmc.Text("Sin datos de proveedores", c="dimmed", ta="center", py="xl") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)