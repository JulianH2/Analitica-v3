import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy

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
            meta = node.get("meta", 100)
        except (KeyError, TypeError):
            val, meta = 0, 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={
                'prefix': self.prefix,
                'suffix': self.suffix,
                'font': {'size': 16}
            },
            gauge={
                'axis': {'range': [None, meta * 1.5 if meta > 0 else 100]},
                'bar': {'color': self.color}
            }
        ))
        fig.update_layout(
            height=100,
            margin=dict(l=5, r=5, t=20, b=10),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    def render_detail(self, data_context):
        try:
            node = data_context["mantenimiento"][self.section]["indicadores"][self.key]
            vs = node.get("vs_2024", 0)
            ytd = node.get("ytd", 0)
        except (KeyError, TypeError):
            vs, ytd = 0, 0

        return dmc.Stack(gap=2, children=[
            dmc.Group(justify="space-between", children=[
                dmc.Text("vs 2024:", size="xs", c="dimmed"),
                dmc.Text(f"{self.prefix}{vs:,.0f}", size="xs")
            ]),
            dmc.Group(justify="space-between", children=[
                dmc.Text("YTD:", size="xs", c="dimmed"),
                dmc.Text(f"{self.prefix}{ytd:,.0f}", size="xs", c="blue")
            ])
        ])

class AvailabilityMonthlyStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "% Disponibilidad Unidades 2025 vs. 2024"}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["disponibilidad"]["graficas"]["disponibilidad_mensual"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds["meses"], y=ds["anterior"], marker_color='#ced4da'))
        fig.add_trace(go.Bar(name='2025', x=ds["meses"], y=ds["actual"], marker_color='#228be6'))
        fig.add_trace(go.Scatter(
            name='Meta',
            x=ds["meses"],
            y=ds["meta"],
            mode='lines',
            line=dict(color='green', width=2, dash='dot')
        ))
        fig.update_layout(
            barmode='group',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", y=1.1, x=0),
            yaxis=dict(ticksuffix="%")
        )
        return fig

    def render_detail(self, data_context):
        return None

class AvailabilityKmEntriesStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Entradas a Taller y Kms Recorridos"}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["disponibilidad"]["graficas"]["entradas_vs_kms"]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=ds["unidades"],
            y=ds["entradas"],
            name="Entradas",
            yaxis='y',
            marker_color='#fa5252'
        ))
        fig.add_trace(go.Scatter(
            x=ds["unidades"],
            y=ds["kms"],
            name="Kilómetros",
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#228be6')
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", y=1.1, x=0),
            yaxis=dict(title="Entradas"),
            yaxis2=dict(title="Kms", overlaying='y', side='right')
        )
        return fig

    def render_detail(self, data_context):
        return None

class AvailabilityTableStrategy:
    def render(self, data_context):
        ds = data_context["mantenimiento"]["disponibilidad"]["tablas"]["detalle"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(h, style={"fontSize": "11px"}) for h in ds["h"]
            ])),
            dmc.TableTbody([
                dmc.TableTr([
                    dmc.TableTd(
                        str(c),
                        fw="bold" if str(row[0]) in ["Total", "SIN ASIGNAR"] else "normal",
                        style={"fontSize": "11px"}
                    ) for c in row
                ]) for row in ds["r"]
            ])
        ], striped=True, withTableBorder=True)

class TallerTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Costo Total Mantenimiento 2025 vs. 2024"}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"]["tendencia_anual"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds["meses"], y=ds["anterior"], marker_color='#ced4da'))
        fig.add_trace(go.Bar(name='2025', x=ds["meses"], y=ds["actual"], marker_color='#228be6'))
        fig.add_trace(go.Scatter(
            name='Meta',
            x=ds["meses"],
            y=ds["meta"],
            mode='lines+markers',
            line=dict(color='#fd7e14', width=2)
        ))
        fig.update_layout(
            barmode='group',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", y=1.1, x=0)
        )
        return fig

    def render_detail(self, data_context):
        return None

class TallerMaintenanceTypeStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Costo por Clasificación y Razón"}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"]["corrective_preventive"]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Correctivo',
            x=['CORRECTIVO'],
            y=[ds["values"][0]],
            marker_color="#228be6"
        ))
        fig.add_trace(go.Bar(
            name='Preventivo',
            x=['PREVENTIVO'],
            y=[ds["values"][1]],
            marker_color="#40c057"
        ))
        fig.update_layout(
            barmode='stack',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        return fig

    def render_detail(self, data_context):
        return None

class TallerHorizontalBarStrategy(KPIStrategy):
    def __init__(self, title, data_key, color="#228be6"):
        self.title = title
        self.data_key = data_key
        self.color = color

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"][self.data_key]
        fig = go.Figure(go.Bar(
            x=ds["values"],
            y=ds["labels"],
            orientation='h',
            marker_color=self.color,
            text=ds["values"],
            textposition="auto"
        ))
        fig.update_layout(
            height=250,
            margin=dict(l=0, r=0, t=30, b=20),
            yaxis=dict(autorange="reversed")
        )
        return fig

    def render_detail(self, data_context):
        return None

class TallerDonutStrategy(KPIStrategy):
    def __init__(self, title, data_key):
        self.title = title
        self.data_key = data_key

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["dashboard"]["graficas"][self.data_key]
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"],
            values=ds["values"],
            hole=.6
        )])
        fig.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        return fig

    def render_detail(self, data_context):
        return None

class PurchasesTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Compras 2025 vs. 2024"}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["graficas"]["tendencia"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds["meses"], y=ds["anterior"], marker_color='#ced4da'))
        fig.add_trace(go.Bar(name='2025', x=ds["meses"], y=ds["actual"], marker_color='#228be6'))
        fig.update_layout(
            barmode='group',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", y=1.1, x=0)
        )
        return fig

    def render_detail(self, data_context):
        return None

class PurchasesAreaBarStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Total Compra por Área"}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["graficas"]["por_area"]
        fig = go.Figure(go.Bar(
            x=ds["valores"],
            y=ds["areas"],
            orientation='h',
            marker_color="#40c057",
            text=[f"${v}M" for v in ds["valores"]],
            textposition="auto"
        ))
        fig.update_layout(
            height=250,
            margin=dict(l=0, r=0, t=30, b=20),
            yaxis=dict(autorange="reversed")
        )
        return fig

    def render_detail(self, data_context):
        return None

class PurchasesTypeDonutStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Compras por Tipo Compra"}

    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["graficas"]["tipo"]
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"],
            values=ds["values"],
            hole=.6,
            marker_colors=["#e03131", "#228be6", "#fab005"]
        )])
        fig.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        return fig

    def render_detail(self, data_context):
        return None

class WorkshopPurchasesTableStrategy:
    def _build(self, h, r):
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(x, style={"fontSize": "11px"}) for x in h
            ])),
            dmc.TableTbody([
                dmc.TableTr([
                    dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row
                ]) for row in r
            ])
        ], striped=True, withTableBorder=True, highlightOnHover=True)

    def render_proveedor(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["tablas"]["proveedores"]
        return self._build(ds["h"], ds["r"])

    def render_ordenes(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["tablas"]["ordenes"]
        return self._build(ds["h"], ds["r"])

    def render_insumos(self, data_context):
        ds = data_context["mantenimiento"]["compras"]["tablas"]["insumos"]
        return self._build(ds["h"], ds["r"])
    
class InventoryGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color):
        self.title, self.key, self.color = title, key, color
    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        node = data_context["mantenimiento"]["almacen"]["indicadores"][self.key]
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=node["valor"],
            number={'prefix': "$", 'font': {'size': 18}},
            gauge={'axis': {'range': [None, node["meta"]*1.1 if node["meta"] > 0 else node["valor"]*1.5]}, 'bar': {'color': self.color}}
        ))
        fig.update_layout(height=140, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return None

class InventoryHistoricalTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Valorización Histórica 2025 vs. 2024"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["graficas"]["historico_anual"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='2024', x=ds["meses"], y=ds["anterior"], mode='lines+markers', line=dict(color='#ced4da')))
        fig.add_trace(go.Scatter(name='2025', x=ds["meses"], y=ds["actual"], mode='lines+markers', line=dict(color='#228be6', width=3)))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.1, x=0))
        return fig
    def render_detail(self, data_context): return None

class InventoryAreaDistributionStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Valorización Actual por Área"}
    def get_figure(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["graficas"]["por_area"]
        fig = go.Figure(go.Bar(x=ds["labels"], y=ds["values"], marker_color="#228be6", text=[f"${v/1e6:.1f}M" for v in ds["values"]], textposition="auto"))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        return fig
    def render_detail(self, data_context): return None

class InventoryDetailedTableStrategy:
    def render_family(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["tablas"]["familia"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in ds["r"]])
        ], striped=True, withTableBorder=True)

    def render_history(self, data_context):
        ds = data_context["mantenimiento"]["almacen"]["tablas"]["historico"]
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in ds["r"]])
        ], striped=True, withTableBorder=True)