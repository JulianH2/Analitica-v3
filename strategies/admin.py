import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
import plotly.express as px
from .base_strategy import KPIStrategy
from services.data_manager import DataManager

data_manager = DataManager()

class AdminRichKPIStrategy(KPIStrategy):
    def __init__(self, section, key, title, icon, color):
        self.section = section
        self.key = key
        self.title = title
        self.icon = icon
        self.color = color

    def get_card_config(self, data_context):
        try:
            data = data_context["administracion"][self.section]["indicadores"].get(self.key, {})
        except:
            data = {}

        return {
            "title": self.title,
            "value": data.get('valor', 0),
            "meta": data.get('meta', 0),
            "vs_2024": data.get('vs_2024', 0),
            "ytd": data.get('ytd', 0),
            "color": self.color,
            "icon": self.icon
        }

    def render_detail(self, data_context):
        cfg = self.get_card_config(data_context)
        
        def fmt(v): 
            return f"${v:,.0f}" if isinstance(v, (int, float)) else "$0"
        
        def pct(v):
            return f"{v:+.1%}" if isinstance(v, (int, float)) else "0%"

        return dmc.Stack(gap=4, mt="sm", children=[
            dmc.Group(justify="space-between", children=[
                dmc.Text("Meta:", size="xs", c="dimmed"),  # type: ignore
                dmc.Text(fmt(cfg['meta']), size="xs", fw="normal")
            ]),
            dmc.Group(justify="space-between", children=[
                dmc.Text("vs 2024:", size="xs", c="dimmed"),  # type: ignore
                dmc.Text(pct(cfg['vs_2024']), size="xs", c="red" if cfg.get('vs_2024', 0) < 0 else "teal")
            ]),
            dmc.Divider(my=4),
            dmc.Group(justify="space-between", children=[
                dmc.Text("YTD:", size="xs", fw="bold"), 
                dmc.Text(pct(cfg['ytd']), size="xs", fw="bold", c="blue")
            ])
        ])

class CollectionEvolutionStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Facturación vs Cobranza (YTD)"}
    
    def get_figure(self, data_context):
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"]
        facturado = [12, 14, 13, 15, 16, 14, 13, 15, 14]
        cobrado = [11, 13, 12, 14, 15, 13, 12, 14, 13]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses, y=facturado, name="Facturado", marker_color="#228be6", opacity=0.7))
        fig.add_trace(go.Scatter(x=meses, y=cobrado, name="Cobrado", mode='lines+markers', line=dict(color='#fd7e14', width=3)))
        
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", y=1.1, x=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            title=dict(text="<b>Tendencia Anual</b>", font=dict(size=12)),
            yaxis=dict(showgrid=True, gridcolor="#f1f3f5"), xaxis=dict(showgrid=False)
        )
        return fig
    def render_detail(self, data_context): return None

class CollectionTrendStrategy(CollectionEvolutionStrategy): pass

class DebtorsRankingStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Top Clientes Deudores"}
    
    def get_figure(self, data_context):
        clientes = ["MATRIMAR", "CEMEX", "VITRO", "TERNIUM", "HEB", "WALMART"]
        monto = [5.2, 3.1, 1.8, 1.2, 0.9, 0.5]
        colors = ["#fa5252", "#fa5252", "#fab005", "#fab005", "#40c057", "#40c057"]
        
        fig = go.Figure(go.Bar(
            x=monto, y=clientes, orientation='h', marker_color=colors,
            text=[f"${m}M" for m in monto], textposition="inside"
        ))
        fig.update_layout(
            height=280, margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(autorange="reversed"), xaxis=dict(showgrid=False),
            title=dict(text="<b>Cartera Vencida por Cliente</b>", font=dict(size=12))
        )
        return fig
    def render_detail(self, data_context): return None

class CollectionMixStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Mix Cartera"}
    def get_figure(self, data_context):
        fig = go.Figure(data=[go.Pie(
            labels=['Corriente', '1-30', '30-60', '60+'], 
            values=[60, 20, 15, 5], hole=.6, 
            marker=dict(colors=["#40c057", "#fab005", "#fd7e14", "#fa5252"]),
            textinfo='percent'
        )])
        fig.update_layout(
            height=220, margin=dict(l=10, r=10, t=30, b=10), showlegend=True,
            title=dict(text="<b>Cartera Por Clasificación</b>", font=dict(size=11)),
            legend=dict(font=dict(size=9))
        )
        return fig
    def render_detail(self, data_context): return None

class PayablesForecastStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Proyección de Pagos"}
    def get_figure(self, data_context):
        semanas = ["Sem 1", "Sem 2", "Sem 3", "Sem 4"]
        monto = [2.5, 3.1, 1.8, 2.2]
        fig = go.Figure(go.Bar(x=semanas, y=monto, marker_color="#228be6"))
        fig.add_trace(go.Scatter(x=semanas, y=[2.8]*4, mode='lines', name='Límite', line=dict(color='red', dash='dot')))
        fig.update_layout(height=220, margin=dict(l=0, r=0, t=30, b=0), showlegend=False, title=dict(text="<b>Requerimiento Semanal</b>", font=dict(size=12)))
        return fig
    def render_detail(self, data_context): return None

class SupplierMixStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Mix Proveedores"}
    def get_figure(self, data_context):
        fig = go.Figure(data=[go.Pie(labels=['Combustibles', 'Arrendadora', 'Refacciones', 'Otros'], values=[40, 25, 15, 20], hole=.6, marker=dict(colors=["#e03131", "#1971c2", "#0ca678", "#868e96"]), textinfo='percent')])
        fig.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10), showlegend=True, legend=dict(font=dict(size=10)))
        return fig
    def render_detail(self, data_context): return None

class PayablesRankingStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Saldo por Proveedor"}
    def get_figure(self, data_context):
        prov = ["Combustibles SA", "Arrendadora Fin", "Llantas Mx", "Refacciones", "Seguros"]
        saldo = [4.2, 1.5, 0.8, 0.6, 0.4]
        fig = go.Figure(go.Bar(x=saldo, y=prov, orientation='h', marker_color="#fab005", text=[f"${s}M" for s in saldo], textposition="auto"))
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(autorange="reversed"), xaxis=dict(showgrid=False), title=dict(text="<b>Top Proveedores (Saldo)</b>", font=dict(size=11)))
        return fig
    def render_detail(self, data_context): return None

class PayablesAgingStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Antigüedad de Saldos"}
    def get_figure(self, data_context):
        cats = ["Corriente", "1-30 Días", "31-60 Días", "60+ Días"]
        vals = [70, 15, 10, 5]
        fig = go.Figure(go.Bar(x=cats, y=vals, marker_color='#228be6'))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), title=dict(text="<b>Pasivos por Vencimiento</b>", font=dict(size=12)))
        return fig
    def render_detail(self, data_context): return None

class PayablesComparisonStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "CXP vs Pasado"}
    def get_figure(self, data_context):
        cats = ["1-15", "16-30"]
        val = [10, 5]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cats, y=val, marker_color="#228be6"))
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0), title=dict(text="<b>Comparativa Vencimiento</b>", font=dict(size=11)))
        return fig
    def render_detail(self, data_context): return None

class CashFlowWaterfallStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Flujo de Efectivo Detallado"}

    def get_figure(self, data_context):
        try:
            flujo = data_context["administracion"]["flujo_efectivo"]["indicadores"]
            ingreso = flujo["ingresos_totales"]["valor"]
            egreso_total = flujo["egresos_totales"]["valor"]
        except:
            ingreso = 426000000
            egreso_total = 425000000

        nomina = egreso_total * 0.05
        almacen = egreso_total * 0.08
        casetas = egreso_total * 0.10
        general = egreso_total * 0.77 
        
        labels = ["Ingresos", "Nómina", "Almacén", "Casetas", "Prov. Gral", "Flujo Neto"]
        values = [ingreso, -nomina, -almacen, -casetas, -general, 0]
        values[-1] = sum(values[:-1])

        fig = go.Figure(go.Waterfall(
            name = "Flujo", orientation = "v",
            measure = ["absolute", "relative", "relative", "relative", "relative", "total"],
            x = labels, textposition = "outside",
            text = [f"${x/1000000:,.1f}M" for x in values],
            y = values,
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
            decreasing = {"marker":{"color":"#fa5252"}},
            increasing = {"marker":{"color":"#40c057"}},
            totals = {"marker":{"color":"#15aabf"}}
        ))
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), title=dict(text="<b>Cascada de Resultados (Mes)</b>", font=dict(size=12)))
        return fig
    def render_detail(self, data_context): return None

class DailyCashflowStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Evolución Saldo Diario"}
    def get_figure(self, data_context):
        import numpy as np 
        dias = list(range(1, 31))
        saldo = [20 + (i%5 - 2) * 0.8 for i in dias] 
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dias, y=saldo, fill='tozeroy', mode='lines', line=dict(color='#40c057', width=2), name='Saldo MXN'))
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f1f3f5"), title=dict(text="<b>Comportamiento de Liquidez (Mes Actual)</b>", font=dict(size=12)))
        return fig
    def render_detail(self, data_context): return dmc.Text("Movimientos detallados...")

class BankBreakdownStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Saldo por Banco"}
    def get_figure(self, data_context):
        labels = ["Banorte", "BBVA", "Santander", "Banregio"]
        values = [45, 30, 15, 10]
        colors = ["#e03131", "#1971c2", "#e8590c", "#f08c00"]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors), textinfo='percent')])
        fig.update_layout(height=220, margin=dict(l=10, r=10, t=30, b=10), showlegend=True, legend=dict(font=dict(size=10)))
        return fig
    def render_detail(self, data_context): return None

class AdminTableStrategy:
    def render(self, data_context, mode="collection"):
        if mode == "collection":
            headers = ["Cliente", "Facturado", "Cobrado", "Saldo", "Antigüedad", "Estatus"]
            rows_data = [
                ("CLIENTE A", "$12.5M", "$10.1M", "$2.4M", "35 días", "Riesgo"),
                ("CLIENTE B", "$8.2M", "$8.2M", "$0.0", "0 días", "Al día"),
                ("CLIENTE C", "$5.1M", "$1.0M", "$4.1M", "95 días", "Legal"),
                ("CLIENTE D", "$3.5M", "$3.0M", "$0.5M", "15 días", "Corriente"),
                ("CLIENTE E", "$1.2M", "$0.0M", "$1.2M", "60 días", "Riesgo"),
            ]
        elif mode == "payables":
            headers = ["Proveedor", "Rubro", "Vencimiento", "Monto", "Prioridad"]
            rows_data = [
                ("COMBUSTIBLES NORTE", "Operativo", "05-Nov", "$2.1M", "Alta"),
                ("REFACCIONES MTY", "Almacén", "12-Nov", "$850k", "Media"),
                ("CASETAS NACIONALES", "Casetas", "01-Nov", "$1.9M", "Alta"),
                ("SEGUROS ATLAS", "Admin", "15-Nov", "$450k", "Baja"),
                ("RENTA DE NAVES", "Inmuebles", "01-Nov", "$120k", "Media"),
            ]
        else: 
            headers = ["Banco", "Cuenta", "Divisa", "Saldo Ayer", "Saldo Hoy"]
            rows_data = [
                ("BANORTE", "**9921", "MXN", "$12.1M", "$11.8M"),
                ("BBVA", "**8822", "MXN", "$5.5M", "$5.2M"),
                ("SANTANDER", "**1102", "USD", "$150k", "$152k"),
                ("BANREGIO", "**3301", "MXN", "$2.1M", "$2.3M"),
                ("CAJA CHICA", "Efec.", "MXN", "$50k", "$45k"),
            ]

        rows = []
        for r in rows_data:
            cells = [dmc.TableTd(c, style={"fontSize": "12px"}) for c in r]
            rows.append(dmc.TableTr(cells))

        return dmc.Table(
            [dmc.TableThead(dmc.TableTr([dmc.TableTh(h) for h in headers]))] + [dmc.TableTbody(rows)],
            striped="odd", highlightOnHover=True, withTableBorder=True, verticalSpacing="xs"
        )

class PayablesListStrategy(AdminTableStrategy):
    def render(self, data_context, mode=None): 
        return super().render(data_context, mode="payables")

class TreasuryTableStrategy(AdminTableStrategy):
    def render(self, data_context, mode=None): 
        return super().render(data_context, mode="banks")

class ComplexKPIStrategy(KPIStrategy):
    def __init__(self, title, value, subtext, trend, color, icon):
        self.title, self.value, self.subtext, self.trend, self.color, self.icon = title, value, subtext, trend, color, icon
    def get_card_config(self, data_context):
        return {"title": self.title, "value": self.value, "meta_text": self.subtext, "trend": self.trend, "color": self.color, "icon": self.icon}
    def render_detail(self, data_context): return dmc.Text("Detalle del indicador...")