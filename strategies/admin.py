import plotly.graph_objects as go
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem

COLOR_MAP = {
    "indigo": DesignSystem.BRAND[5],
    "green": DesignSystem.SUCCESS[5],
    "red": DesignSystem.DANGER[5],
    "yellow": DesignSystem.WARNING[5],
    "blue": DesignSystem.BRAND[5],
    "teal": DesignSystem.SUCCESS[5],
    "orange": DesignSystem.WARNING[5],
    "gray": DesignSystem.SLATE[5],
}

class AdminRichKPIStrategy(KPIStrategy):
    def __init__(self, section, key, title, icon, color, sub_section="indicadores"):
        self.section, self.key, self.title, self.icon, self.color, self.sub_section = section, key, title, icon, color, sub_section

    def get_card_config(self, data_context):
        try:
            node = data_context["administracion"][self.section][self.sub_section]
            data = node.get(self.key, {"valor": 0})
            val = data.get('valor', 0) if isinstance(data, dict) else data
        except (KeyError, TypeError): val = 0
        return {"title": self.title, "value": val, "color": self.color, "icon": self.icon}

    def render_detail(self, data_context): 
        return dmc.Text("Cargando detalle dinámico...", size="sm", c="gray")

class CollectionGaugeStrategy(KPIStrategy):
    def __init__(self, title, val_key, target_key, color):
        self.title, self.val_key, self.target_key, self.color = title, val_key, target_key, color

    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        node = data_context["administracion"]["facturacion_cobranza"]["indicadores"]
        val = node.get(self.val_key, {}).get("valor", 0)
        target = node.get(self.target_key, {}).get("valor", 100)
        
        hex_color = COLOR_MAP.get(self.color, DesignSystem.BRAND[5])

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={'prefix': "$", 'font': {'size': 22}},
            gauge={'axis': {'range': [None, target * 1.2]}, 'bar': {'color': hex_color}}
        ))
        fig.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class CollectionComparisonStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Facturado 2025 vs. 2024"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["facturacion_cobranza"]["graficas"]["comparativa"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=DesignSystem.BRAND[5]))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3]))
        fig.update_layout(
            height=300, barmode='group', margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class CollectionMixStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Cartera M.N. por Clasificación"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["facturacion_cobranza"]["graficas"]["mix"]
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"],
            values=ds["values"],
            hole=.6,
            marker=dict(colors=[DesignSystem.WARNING[5], DesignSystem.SUCCESS[5], DesignSystem.DANGER[5]])
        )])
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class DebtorsStackedStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Cartera M.N. por Cliente"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["facturacion_cobranza"]["graficas"]["stack"]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["por_vencer"], name="Por Vencer", orientation='h', marker_color=DesignSystem.SUCCESS[5]))
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["sin_carta"], name="Sin Carta", orientation='h', marker_color=DesignSystem.WARNING[5]))
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["vencido"], name="Vencido", orientation='h', marker_color=DesignSystem.DANGER[5]))
        fig.update_layout(
            barmode='stack', height=350, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(autorange="reversed"),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class CollectionAgingTableStrategy:
    def render(self, data_context):
        ds = data_context["administracion"]["facturacion_cobranza"]["antiguedad"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(c) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

class BankDailyEvolutionStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Ingresos y Egresos Por Día"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["bancos"]["graficas"]["diaria"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ds["dias"], y=ds["ingresos"], name="Ingresos", line=dict(color=DesignSystem.SUCCESS[5], width=3)))
        fig.add_trace(go.Scatter(x=ds["dias"], y=ds["egresos"], name="Egresos", line=dict(color=DesignSystem.DANGER[5], width=3)))
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class BankDonutStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Saldo por Banco"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["bancos"]["graficas"]["donut"]
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"],
            values=ds["values"],
            hole=.6,
            marker=dict(colors=[DesignSystem.WARNING[6]])
        )])
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class BankConceptsStrategy:
    def render(self, data_context):
        ds = data_context["administracion"]["bancos"]["conceptos"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(c) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

class PayablesGaugeStrategy(KPIStrategy):
    def __init__(self, title, val_key, target_key, color):
        self.title, self.val_key, self.target_key, self.color = title, val_key, target_key, color

    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        node = data_context["administracion"]["cuentas_por_pagar"]["indicadores"]
        val = node.get(self.val_key, {}).get("valor", 0)
        target = node.get(self.target_key, {}).get("valor", 100)
        
        hex_color = COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={'prefix': "$", 'font': {'size': 22}},
            gauge={'axis': {'range': [None, target * 1.2]}, 'bar': {'color': hex_color}}
        ))
        fig.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class PayablesComparisonStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Cuentas x Pagar 2025 vs. 2024"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["comparativa"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=DesignSystem.BRAND[5]))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3]))
        fig.update_layout(
            height=300, barmode='group', margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class PayablesMixStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Saldo por Clasificación"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["mix"]
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"],
            values=ds["values"],
            hole=.6,
            marker=dict(colors=[DesignSystem.SUCCESS[5], DesignSystem.DANGER[5]])
        )])
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class SupplierSaldoStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Saldo por Proveedor"}
    def get_figure(self, data_context):
        ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["saldo_proveedor"]
        fig = go.Figure()
        fig.add_trace(go.Bar(y=ds["prov"], x=ds["por_vencer"], name="Por Vencer", orientation='h', marker_color=DesignSystem.SUCCESS[5]))
        fig.add_trace(go.Bar(y=ds["prov"], x=ds["vencido"], name="Vencido", orientation='h', marker_color=DesignSystem.DANGER[5]))
        fig.update_layout(
            barmode='stack', height=350, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=1.1, x=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class PayablesAgingTableStrategy:
    def render(self, data_context):
        ds = data_context["administracion"]["cuentas_por_pagar"]["antiguedad"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(c, style={"fontSize": "11px"}) for c in r]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)