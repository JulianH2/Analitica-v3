import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
from .base_strategy import KPIStrategy
from services.data_manager import DataManager

data_manager = DataManager()

class IncomeStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        kpi = data_context.get("main_dashboard", {}).get("indicadores_principales", {}).get("ingresos_por_viajes", {})
        val = kpi.get("valor", 0)
        meta = kpi.get("meta", 0)
        trend = ((val - meta) / meta) * 100 if meta != 0 else 0
        
        return {
            "title": "Ingresos por Viajes",
            "value": f"${val/1000000:.2f}M",
            "meta_text": f"Meta: ${meta/1000000:.1f}M",
            "trend": trend,
            "icon": "tabler:coin",
            "color": "blue"
        }

    def render_detail(self, data_context):
        ops_data = data_manager.service.get_ops_income_data()
        clients = ops_data.get("tablas", {}).get("clientes", [])[:10]

        rows = [
            dmc.TableTr([
                dmc.TableTd(c.get("cliente", "")),
                dmc.TableTd(str(c.get("viajes", 0))),
                dmc.TableTd(f"${c.get('kms', 0):,.0f}")
            ]) for c in clients
        ]

        return dmc.Stack([
            dmc.Alert("Ingresos superan la meta mensual proyectada.", title="Análisis de Ingresos", color="green", variant="light"),
            dmc.Text("Desglose por Cliente (Top 10)", fw="bold", mt="md"),
            dmc.Table(
                striped="odd", withTableBorder=True, highlightOnHover=True,
                children=[
                    dmc.TableThead(dmc.TableTr([dmc.TableTh("Cliente"), dmc.TableTh("Viajes"), dmc.TableTh("Monto/Kms")])),
                    dmc.TableTbody(rows)
                ]
            )
        ])

class CostStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        kpi = data_context.get("main_dashboard", {}).get("indicadores_principales", {}).get("costos_por_viajes", {})
        val = kpi.get("valor", 0)
        meta = kpi.get("meta", 0)
        trend = ((val - meta) / meta) * 100 if meta != 0 else 0
        
        return {
            "title": "Costos Operativos",
            "value": f"${val/1000000:.2f}M",
            "meta_text": f"Meta: ${meta/1000000:.1f}M",
            "trend": trend,
            "icon": "tabler:wallet",
            "color": "red",
            "reverse_trend": True
        }

    def render_detail(self, data_context):
        mtto = data_context.get("main_dashboard", {}).get("mantenimiento", {})
        
        def get_val(key):
            v = mtto.get(key, 0)
            return v.get("valor", 0) if isinstance(v, dict) else v

        total = get_val("total")
        interno = get_val("taller_interno")
        externo = get_val("taller_externo")
        llantas = get_val("costo_llantas")
        
        pct_interno = (interno / total * 100) if total > 0 else 0

        return dmc.Stack([
            dmc.Text("Estructura de Costos de Mantenimiento", fw="bold", size="lg"),
            dmc.SimpleGrid(cols=3, children=[
                dmc.Paper(p="sm", withBorder=True, children=[
                    dmc.Text("Taller Interno", size="xs", c="dimmed"), # type: ignore
                    dmc.Text(f"${interno:,.0f}", fw="bold", c="blue")
                ]),
                dmc.Paper(p="sm", withBorder=True, children=[
                    dmc.Text("Taller Externo", size="xs", c="dimmed"), # type: ignore
                    dmc.Text(f"${externo:,.0f}", fw="bold", c="orange")
                ]),
                dmc.Paper(p="sm", withBorder=True, children=[
                    dmc.Text("Llantas", size="xs", c="dimmed"), # type: ignore
                    dmc.Text(f"${llantas:,.0f}", fw="bold")
                ]),
            ]),
            dmc.Box([
                dmc.Group(justify="space-between", mb=5, children=[
                    dmc.Text("Distribución Gasto Interno", size="sm", fw="normal"),
                    dmc.Text(f"{int(pct_interno)}%", size="sm", fw="bold", c="blue")
                ]),
                dmc.ProgressRoot(size="xl", children=[
                    dmc.ProgressSection(value=pct_interno, color="blue", children=[dmc.ProgressLabel(f"{int(pct_interno)}%")]),
                    dmc.ProgressSection(value=100-pct_interno, color="gray", children=[dmc.ProgressLabel("Ext")])
                ])
            ]),
            dmc.Text("Top Fallas Recurrentes", fw="bold", mt="md"),
            dmc.Table(
                data={"head": ["Sistema", "Costo"], "body": [["Motor", "$129k"], ["Frenos", "$111k"], ["Remolques", "$99k"]]},
                striped="odd", withTableBorder=True
            )
        ])

class MarginStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        kpi = data_context.get("main_dashboard", {}).get("indicadores_principales", {}).get("margen_por_viaje", {})
        val = kpi.get("valor", 0)
        trend = 5.4 

        return {
            "title": "Margen Bruto",
            "value": f"{val}%",
            "meta_text": "Meta: >50%",
            "trend": trend,
            "icon": "tabler:chart-pie",
            "color": "green"
        }

    def render_detail(self, data_context):
        return dmc.Stack([
            dmc.Alert("Utilidad neta refleja ingreso menos costos directos e indirectos.", title="Margen Operativo", color="green", variant="light"),
            dmc.SimpleGrid(cols=2, children=[
                dmc.Paper(p="md", withBorder=True, children=[dmc.Text("Utilidad Operativa", c="dimmed"), dmc.Text("$11.2M", fw="bold", size="xl")]), # type: ignore
                dmc.Paper(p="md", withBorder=True, children=[dmc.Text("EBITDA", c="dimmed"), dmc.Text("18%", fw="bold", size="xl")]), # type: ignore
            ])
        ])

class BalanceStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        bancos = data_context.get("main_dashboard", {}).get("resumenes", {}).get("bancos_mn", {})
        saldo_actual = bancos.get("saldo", 0)
        saldo_inicial = bancos.get("saldo_inicial", 0)
        trend = ((saldo_actual - saldo_inicial) / saldo_inicial) * 100 if saldo_inicial != 0 else 0

        return {
            "title": "Saldo Bancos",
            "value": f"${saldo_actual:,.0f}",
            "meta_text": f"Inicial: ${saldo_inicial:,.0f}",
            "trend": trend,
            "icon": "tabler:building-bank",
            "color": "violet"
        }

    def render_detail(self, data_context):
        bancos = data_context.get("main_dashboard", {}).get("resumenes", {}).get("bancos_mn", {})
        ingresos = bancos.get("ingresos", 0)
        egresos = bancos.get("egresos", 0)
        flujo_neto = ingresos - egresos

        return dmc.Stack([
            dmc.Text("Flujo de Caja del Periodo", fw="bold", size="lg"),
            dmc.SimpleGrid(cols=3, children=[
                dmc.Paper(p="md", withBorder=True, style={"backgroundColor": "var(--mantine-color-green-0)"}, children=[
                    dmc.Text("Entradas", c="dimmed", size="xs"), # type: ignore
                    dmc.Text(f"${ingresos:,.0f}", fw="bold", c="green")
                ]),
                dmc.Paper(p="md", withBorder=True, style={"backgroundColor": "var(--mantine-color-red-0)"}, children=[
                    dmc.Text("Salidas", c="dimmed", size="xs"), # type: ignore
                    dmc.Text(f"${egresos:,.0f}", fw="bold", c="red")
                ]),
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("Flujo Neto", c="dimmed", size="xs"), # type: ignore
                    dmc.Text(f"${flujo_neto:,.0f}", fw="bold", c="blue")
                ])
            ]),
            dmc.Alert("Saldo consolidado Bancos Moneda Nacional.", title="Tesorería", color="gray", variant="light")
        ])

class PortfolioStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Cartera Clientes"}
    def get_figure(self, data_context):
        fig = go.Figure(data=[go.Pie(
            labels=['Al Corriente', 'Vencido 30', 'Vencido 60+'], 
            values=[70, 20, 10], 
            hole=.6, 
            marker_colors=["#40c057", "#fab005", "#fa5252"],
            textinfo='none'
        )])
        fig.update_layout(
            height=140, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
            annotations=[dict(text='<b>$18M</b>', x=0.5, y=0.5, font_size=12, showarrow=False)],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return dmc.Text("Detalle de Cartera por Antigüedad...")

class SuppliersStrategy(KPIStrategy):
    def get_card_config(self, data_context): return {"title": "Saldo Proveedores"}
    def get_figure(self, data_context):
        fig = go.Figure(data=[go.Pie(
            labels=['Al Corriente', 'Por Vencer'], 
            values=[85, 15], 
            hole=.6, 
            marker_colors=["#228be6", "#fd7e14"],
            textinfo='none'
        )])
        fig.update_layout(
            height=140, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
            annotations=[dict(text='<b>$9M</b>', x=0.5, y=0.5, font_size=12, showarrow=False)],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    def render_detail(self, data_context): return dmc.Text("Detalle de Cuentas por Pagar...")

class SimpleTextStrategy(KPIStrategy):
    def __init__(self, key, title, prefix="", suffix="", color="gray", icon="tabler:circle"):
        self.key = key
        self.title = title
        self.prefix = prefix
        self.suffix = suffix
        self.color = color
        self.icon = icon 

    def get_card_config(self, data_context):
        val = 1234 
        return {
            "title": self.title,
            "value": f"{self.prefix}{val}{self.suffix}",
            "color": self.color,
            "icon": self.icon, 
            "is_simple": True
        }
    def render_detail(self, data_context): return dmc.Text(f"Detalle de {self.title}")