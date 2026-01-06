import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
import plotly.express as px
from .base_strategy import KPIStrategy
from services.data_manager import DataManager

data_manager = DataManager()

class TallerRichKPIStrategy(KPIStrategy):
    def __init__(self, key_data, title, icon, color):
        self.key = key_data
        self.title = title
        self.icon = icon
        self.color = color

    def get_card_config(self, data_context):
        try:
            data = data_context["mantenimiento"]["indicadores"].get(self.key, {})
        except KeyError:
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
        
        def pct(v):
            return f"{v:+.1%}" if isinstance(v, (int, float)) else "0%"

        return dmc.Stack(gap=4, mt="sm", children=[
            dmc.Group(justify="space-between", children=[
                dmc.Text("Meta:", size="xs", style={"color": "var(--mantine-color-dimmed)"}),
                dmc.Text(f"{cfg['meta']}", size="xs", fw="normal")
            ]),
            dmc.Group(justify="space-between", children=[
                dmc.Text("vs 2024:", size="xs", style={"color": "var(--mantine-color-dimmed)"}),
                dmc.Text(pct(cfg['vs_2024']), size="xs", c="teal")
            ])
        ])

class CostBreakdownStrategy(KPIStrategy):
    def get_card_config(self, data_context): 
        return {"title": "Distribución del Gasto de Mantenimiento"}

    def get_figure(self, data_context):
        try:
            mtto = data_context["mantenimiento"]["indicadores"]
            labels = ["Interno", "Externo", "Llantas"]
            values = [
                mtto["costo_interno"]["valor"], 
                mtto["costo_externo"]["valor"], 
                mtto["costo_llantas"]["valor"]
            ]
        except KeyError:
            labels, values = ["Interno", "Externo", "Llantas"], [60, 30, 10]

        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.5, 
            marker=dict(colors=["#228be6", "#fab005", "#fa5252"]), 
            textinfo='label+percent'
        )])

        fig.update_layout(
            height=280, 
            margin=dict(l=10, r=10, t=30, b=10), 
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def render_detail(self, data_context): return None

class RealInventoryTableStrategy:
    def render(self):
        rows_data = [
            ("03-MTY MULTIF", "0117001006", "ACEITE MOTOR 15W40", "555.00 L", "$96"),
            ("03-MTY MULTIF", "0117001006", "ACEITE MOTOR (Reserva)", "80.00 L", "$78"),
            ("04-MUL CAD", "0117001006", "ACEITE MOTOR 15W40", "45.00 L", "$96"),
            ("01-TINSA", "0107001001", "ACEITE HIDRAULICO", "0.00 L", "$1,501"),
            ("01-TINSA", "0107001003", "ACEITE NEUMATICO", "0.00 L", "$192"),
            ("01-TINSA", "0107001006", "ACEITE MOTOR 15W40", "120.00 L", "$96"),
        ]
        
        rows = []
        for area, codigo, desc, cant, precio in rows_data:
            cant_color = "red" if "0.00" in cant else "dark"
            
            rows.append(dmc.TableTr([
                dmc.TableTd(area, style={"fontSize": "11px"}),
                dmc.TableTd(codigo, style={"color": "var(--mantine-color-dimmed)", "fontSize": "11px"}),
                dmc.TableTd(desc, fw="normal", style={"fontSize": "11px"}),
                dmc.TableTd(cant, fw="bold", c=cant_color, style={"fontSize": "11px"}),
                dmc.TableTd(precio, style={"fontSize": "11px"})
            ]))

        return dmc.Table(
            [dmc.TableThead(dmc.TableTr([
                dmc.TableTh("Almacén"), 
                dmc.TableTh("Código"), 
                dmc.TableTh("Descripción"), 
                dmc.TableTh("Stock"), 
                dmc.TableTh("Costo")
            ]))] + [dmc.TableTbody(rows)],
            striped="odd", highlightOnHover=True, withTableBorder=True, verticalSpacing="xs"
        )

class AvailabilityGaugeStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Disponibilidad de Flota"}

    def get_figure(self, data_context):
        try:
            val = data_context["mantenimiento"].get("disponibilidad", 0) * 100
        except:
            val = 92

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = val,
            number = {'suffix': "%", 'font': {'size': 40}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#228be6"},
                'steps': [
                    {'range': [0, 70], 'color': "#ffe3e3"},
                    {'range': [70, 85], 'color': "#fff3bf"},
                    {'range': [85, 100], 'color': "#d3f9d8"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 95}
            }
        ))
        fig.update_layout(height=200, margin=dict(l=30, r=30, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

    def render_detail(self, data_context): return None

class WorkshopStatusStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Estatus Ordenes"}
    
    def get_figure(self, data_context):
        labels = ["En Proceso", "Esperando Ref.", "Por Asignar", "Terminado"]
        values = [12, 5, 3, 25]
        colors = ["#228be6", "#fab005", "#fa5252", "#40c057"]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors), textinfo='value')])
        fig.update_layout(height=220, margin=dict(l=10, r=10, t=20, b=10), showlegend=True, legend=dict(orientation="h", y=-0.1))
        return fig
    def render_detail(self, data_context): return None

class TopFailuresStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Top Fallas (Pareto)"}
    
    def get_figure(self, data_context):
        sistemas = ["Motor", "Frenos", "Eléctrico", "Suspensión", "Llantas", "Transmisión"]
        conteo = [45, 32, 28, 15, 12, 8]
        fig = go.Figure(go.Bar(
            x=conteo, y=sistemas, orientation='h', marker_color="#fa5252",
            text=conteo, textposition="auto"
        ))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(autorange="reversed"), xaxis=dict(showgrid=False))
        return fig
    def render_detail(self, data_context): return dmc.Text("Análisis causa raíz...")

class WorkshopTableStrategy:
    def render(self):
        rows_data = [("U-105", "Preventivo", "2 días", "Juan P.", "En Proceso"), ("U-88", "Correctivo", "5 días", "Carlos R.", "Esperando Ref.")]
        rows = []
        for u, tipo, dias, mec, st in rows_data:
            st_color = "blue" if st == "En Proceso" else "orange"
            rows.append(dmc.TableTr([dmc.TableTd(u, fw="bold"), dmc.TableTd(tipo), dmc.TableTd(dias), dmc.TableTd(mec), dmc.TableTd(dmc.Badge(st, color=st_color, variant="light"))]))
        return dmc.Table([dmc.TableThead(dmc.TableTr([dmc.TableTh("Unidad"), dmc.TableTh("Tipo"), dmc.TableTh("Estadía"), dmc.TableTh("Mecánico"), dmc.TableTh("Estatus")]))] + [dmc.TableTbody(rows)], striped="odd", highlightOnHover=True, withTableBorder=True, fz="xs")

class AvailabilityTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Tendencia Disponibilidad"}
    def get_figure(self, data_context):
        dias = list(range(1, 31))
        real = [92 + (i%3 - 1)*2 for i in dias] 
        meta = [95] * 30
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dias, y=real, name="Real %", mode='lines+markers', line=dict(color='#228be6', width=2)))
        fig.add_trace(go.Scatter(x=dias, y=meta, name="Meta", mode='lines', line=dict(color='#40c057', dash='dot')))
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(range=[80, 100]))
        return fig
    def render_detail(self, data_context): return None

class DowntimeReasonsStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Causas Inactividad"}
    def get_figure(self, data_context):
        fig = go.Figure(go.Treemap(labels=["Falta Ref", "Mano Obra"], parents=["", ""], values=[10, 20]))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
        return fig
    def render_detail(self, data_context): return None

class InventoryTurnoverStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Rotación de Stock"}
    def get_figure(self, data_context):
        cats = ["Filtros", "Aceites", "Frenos"]
        rot = [4.5, 5.2, 3.1]
        fig = go.Figure(go.Bar(x=cats, y=rot, marker_color="#12b886"))
        fig.update_layout(height=220, margin=dict(l=0, r=0, t=30, b=0))
        return fig
    def render_detail(self, data_context): return None

class PartsTableStrategy:
    def render(self): 
        return RealInventoryTableStrategy().render()

class TirePressureStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Semáforo Presiones"}
    def get_figure(self, data_context):
        fig = go.Figure(go.Indicator(mode = "gauge+number", value = 94, gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#40c057"}}))
        fig.update_layout(height=160, margin=dict(l=20, r=20, t=20, b=20))
        return fig
    def render_detail(self, data_context): return None

class TireCostPerMmStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Costo por MM"}
    def get_figure(self, data_context):
        marcas = ["Michelin", "Bridgestone", "Continental"]
        costo = [120, 135, 140]
        fig = go.Figure(go.Bar(x=marcas, y=costo, marker_color="#228be6"))
        fig.update_layout(height=220, margin=dict(l=0, r=0, t=30, b=0))
        return fig
    def render_detail(self, data_context): return None

class ComplexKPIStrategy(KPIStrategy):
    def __init__(self, title, value, subtext, trend, color, icon):
        self.title, self.value, self.subtext, self.trend, self.color, self.icon = title, value, subtext, trend, color, icon
    def get_card_config(self, data_context):
        return {"title": self.title, "value": self.value, "meta_text": self.subtext, "trend": self.trend, "color": self.color, "icon": self.icon}
    def render_detail(self, data_context): return dmc.Text("Detalle...")