import plotly.graph_objects as go
import dash_mantine_components as dmc
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

class TallerGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="$", suffix="", section="dashboard"):
        self.title = title
        self.key = key
        self.color = color
        self.prefix = prefix
        self.suffix = suffix
        self.section = section

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            node = data_context["mantenimiento"][self.section]["indicadores"][self.key]
            val = node.get("valor", 0)
            meta = node.get("meta", 0)
        except (KeyError, TypeError): val, meta = 0, 0
        
        hex_color = COLOR_MAP.get(self.color, "#228be6")

        if meta > 0:
            pct_val = (val / meta) * 100
            max_range = 100 
        else:
            pct_val = 100 if val > 0 else 0
            max_range = 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct_val,
            number={
                'suffix': "%", 
                'font': {'size': 15, 'weight': 'bold', 'color': "#495057"} 
            },
            gauge={
                'shape': "angular",
                'axis': {
                    'range': [None, max(pct_val, max_range)], 
                    'visible': True, 
                    'tickwidth': 1, 
                    'tickcolor': "white", 
                    'ticklen': 5,
                    'tickmode': 'array',
                    'tickvals': [0, 50, 100], 
                    'showticklabels': False 
                }, 
                'bar': {'color': hex_color, 'thickness': 0.8}, 
                'bgcolor': "rgba(0,0,0,0.08)", 
                'borderwidth': 0,
                'bordercolor': "rgba(0,0,0,0)"
            }
        ))
        
        fig.update_layout(
            height=75,
            margin=dict(l=15, r=15, t=10, b=0), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': "Arial"}
        )
        return fig

    def render_detail(self, data_context):
        return None
class AvailabilityMonthlyStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "% Disponibilidad Unidades 2025 vs. 2024"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["disponibilidad"]["graficas"]["disponibilidad_mensual"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds["meses"], y=ds["anterior"], marker_color=DesignSystem.SLATE[3]))
        fig.add_trace(go.Bar(name='2025', x=ds["meses"], y=ds["actual"], marker_color=DesignSystem.BRAND[5]))
        fig.add_trace(go.Scatter(name='Meta', x=ds["meses"], y=ds["meta"], mode='lines', line=dict(color=DesignSystem.SUCCESS[5], width=2, dash='dot')))
        fig.update_layout(
            barmode='group', height=300, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0), yaxis=dict(ticksuffix="%"),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class AvailabilityKmEntriesStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Entradas a Taller y Kms Recorridos"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["disponibilidad"]["graficas"]["entradas_vs_kms"]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["unidades"], y=ds["entradas"], name="Entradas", yaxis='y', marker_color=DesignSystem.DANGER[5]))
        fig.add_trace(go.Scatter(x=ds["unidades"], y=ds["kms"], name="Kilómetros", yaxis='y2', mode='lines+markers', line=dict(color=DesignSystem.BRAND[5])))
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0),
            yaxis=dict(title="Entradas"), yaxis2=dict(title="Kms", overlaying='y', side='right'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class AvailabilityTableStrategy:
    def render(self, data_context):
        ds = data_context["mantenimiento"]["disponibilidad"]["tablas"]["detalle"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), fw="bold" if str(row[0]) in ["Total", "SIN ASIGNAR"] else "normal", style={"fontSize": "11px"}) for c in row]) for row in ds["r"]])
        ], striped="odd", withTableBorder=True)

class TallerTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Costo Total Mantenimiento 2025 vs. 2024"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"]["tendencia_anual"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds["meses"], y=ds["anterior"], marker_color=DesignSystem.SLATE[3]))
        fig.add_trace(go.Bar(name='2025', x=ds["meses"], y=ds["actual"], marker_color=DesignSystem.BRAND[5]))
        fig.add_trace(go.Scatter(name='Meta', x=ds["meses"], y=ds["meta"], mode='lines+markers', line=dict(color=DesignSystem.WARNING[5], width=2)))
        fig.update_layout(
            barmode='group', height=300, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class TallerMaintenanceTypeStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Costo por Clasificación y Razón"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"]["corrective_preventive"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Correctivo', x=['CORRECTIVO'], y=[ds["values"][0]], marker_color=DesignSystem.DANGER[5]))
        fig.add_trace(go.Bar(name='Preventivo', x=['PREVENTIVO'], y=[ds["values"][1]], marker_color=DesignSystem.SUCCESS[5]))
        fig.update_layout(barmode='stack', height=300, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class TallerHorizontalBarStrategy(KPIStrategy):
    def __init__(self, title, data_key, color="indigo"):
        self.title, self.data_key, self.color = title, data_key, color
    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"][self.data_key]
        hex_color = COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        fig = go.Figure(go.Bar(x=ds["values"], y=ds["labels"], orientation='h', marker_color=hex_color, text=ds["values"], textposition="auto"))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=20), yaxis=dict(autorange="reversed"), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class TallerDonutStrategy(KPIStrategy):
    def __init__(self, title, data_key):
        self.title, self.data_key = title, data_key
    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"][self.data_key]
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.6)])
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), showlegend=True, legend=dict(orientation="h", y=-0.1), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class PurchasesTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Compras 2025 vs. 2024"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["graficas"]["tendencia"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds["meses"], y=ds["anterior"], marker_color=DesignSystem.SLATE[3]))
        fig.add_trace(go.Bar(name='2025', x=ds["meses"], y=ds["actual"], marker_color=DesignSystem.BRAND[5]))
        fig.update_layout(
            barmode='group', height=300, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return None

class PurchasesAreaBarStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Total Compra por Área"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["graficas"]["por_area"]
        fig = go.Figure(go.Bar(x=ds["valores"], y=ds["areas"], orientation='h', marker_color=DesignSystem.SUCCESS[5], text=[f"${v}M" for v in ds["valores"]], textposition="auto"))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=20), yaxis=dict(autorange="reversed"), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class PurchasesTypeDonutStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Compras por Tipo Compra"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["graficas"]["tipo"]
        fig = go.Figure(data=[go.Pie(labels=ds["labels"], values=ds["values"], hole=.6, marker_colors=[DesignSystem.DANGER[5], DesignSystem.BRAND[5], DesignSystem.WARNING[5]])])
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), showlegend=True, legend=dict(orientation="h", y=-0.1), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class WorkshopPurchasesTableStrategy:
    def _build(self, h, r):
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in h])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in r])
        ], striped="odd", withTableBorder=True, highlightOnHover=True)
    def render_proveedor(self, data_context): return self._build(data_context["mantenimiento"]["compras"]["tablas"]["proveedores"]["h"], data_context["mantenimiento"]["compras"]["tablas"]["proveedores"]["r"])
    def render_ordenes(self, data_context): return self._build(data_context["mantenimiento"]["compras"]["tablas"]["ordenes"]["h"], data_context["mantenimiento"]["compras"]["tablas"]["ordenes"]["r"])
    def render_insumos(self, data_context): return self._build(data_context["mantenimiento"]["compras"]["tablas"]["insumos"]["h"], data_context["mantenimiento"]["compras"]["tablas"]["insumos"]["r"])
    
class InventoryGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color):
        self.title, self.key, self.color = title, key, color
    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        node = data_context["mantenimiento"]["almacen"]["indicadores"][self.key]
        hex_color = COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=node["valor"], number={'prefix': "$", 'font': {'size': 18}},
            gauge={'axis': {'range': [None, node["meta"]*1.1 if node["meta"] > 0 else node["valor"]*1.5]}, 'bar': {'color': hex_color}}
        ))
        fig.update_layout(height=140, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class InventoryHistoricalTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Valorización Histórica 2025 vs. 2024"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["graficas"]["historico_anual"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='2024', x=ds["meses"], y=ds["anterior"], mode='lines+markers', line=dict(color=DesignSystem.SLATE[3])))
        fig.add_trace(go.Scatter(name='2025', x=ds["meses"], y=ds["actual"], mode='lines+markers', line=dict(color=DesignSystem.BRAND[5], width=3)))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class InventoryAreaDistributionStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Valorización Actual por Área"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["graficas"]["por_area"]
        fig = go.Figure(go.Bar(x=ds["labels"], y=ds["values"], marker_color=DesignSystem.BRAND[5], text=[f"${v/1e6:.1f}M" for v in ds["values"]], textposition="auto"))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class InventoryDetailedTableStrategy:
    def render_family(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["tablas"]["familia"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in ds["r"]])
        ], striped="odd", withTableBorder=True)
    def render_history(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["tablas"]["historico"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in ds["r"]])
        ], striped="odd", withTableBorder=True)