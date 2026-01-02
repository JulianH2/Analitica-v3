import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html
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
            "title": "Total Income",
            "value": f"${val/1000000:.2f}M",
            "meta_text": f"Target: ${meta/1000000:.1f}M",
            "trend": trend,
            "icon": "tabler:coin",
            "color": "blue"
        }

    def render_detail(self, data_context):
        ops_data = data_manager.service.get_ops_income_data()
        clients = ops_data.get("tablas", {}).get("clientes", [])[:5]

        rows = [
            dmc.TableTr([
                dmc.TableTd(c.get("cliente", "Unknown")),
                dmc.TableTd(str(c.get("viajes", 0))),
                dmc.TableTd(f"{c.get('kms', 0):,.0f}")
            ]) for c in clients
        ]

        return dmc.Stack([
            dmc.Alert("Income is performing above projected target.", title="Status: Healthy", color="green", variant="light"),
            dmc.Text("Top Clients Analysis", fw=700, mt="md"),
            dmc.Table(
                striped=True, 
                withTableBorder=True,
                children=[
                    dmc.TableThead(dmc.TableTr([dmc.TableTh("Client"), dmc.TableTh("Trips"), dmc.TableTh("Kms")])),
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
            "title": "Operational Costs",
            "value": f"${val/1000000:.2f}M",
            "meta_text": f"Budget: ${meta/1000000:.1f}M",
            "trend": trend,
            "icon": "tabler:wallet",
            "color": "red",
            "reverse_trend": True
        }

    def render_detail(self, data_context):
        maintenance = data_context.get("main_dashboard", {}).get("mantenimiento", {})
        
        def get_val(key):
            v = maintenance.get(key, 0)
            return v.get("valor", 0) if isinstance(v, dict) else v

        total = get_val("total")
        internal = get_val("taller_interno")
        external = get_val("taller_externo")
        
        pct_internal = (internal / total * 100) if total > 0 else 0

        return dmc.Stack([
            dmc.Text("Maintenance Cost Breakdown", fw=700, size="lg"),
            dmc.SimpleGrid(cols=2, children=[
                dmc.Paper(p="sm", withBorder=True, children=[
                    dmc.Text("Internal", c="dimmed", size="xs"), 
                    dmc.Text(f"${internal:,.0f}", fw=700, c="blue")
                ]),
                dmc.Paper(p="sm", withBorder=True, children=[
                    dmc.Text("External", c="dimmed", size="xs"), 
                    dmc.Text(f"${external:,.0f}", fw=700, c="orange")
                ]),
            ]),
            dmc.Box([
                dmc.Group(justify="space-between", mb=5, children=[
                    dmc.Text("Internal Share", size="sm", fw=500),
                    dmc.Text(f"{int(pct_internal)}%", size="sm", fw=700, c="blue")
                ]),
                dmc.ProgressRoot(size="xl", children=[
                    dmc.ProgressSection(value=pct_internal, color="blue", children=[dmc.ProgressLabel(f"{int(pct_internal)}%")]),
                    dmc.ProgressSection(value=100-pct_internal, color="gray", children=[dmc.ProgressLabel("Ext")])
                ])
            ])
        ])

class MarginStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        kpi = data_context.get("main_dashboard", {}).get("indicadores_principales", {}).get("margen_por_viaje", {})
        val = kpi.get("valor", 0)
        meta = kpi.get("meta", 0)
        trend = ((val - meta) / meta) * 100 if meta != 0 else 0

        return {
            "title": "Gross Margin",
            "value": f"{val}%",
            "meta_text": f"Target: >{meta}%",
            "trend": trend,
            "icon": "tabler:chart-pie",
            "color": "green"
        }

    def render_detail(self, data_context):
        return dmc.Stack([
            dmc.Alert("Net margin reflects revenue minus direct and indirect costs.", title="Margin Analysis", color="cyan", variant="light"),
            dmc.Text("Detailed waterfall chart coming soon...", c="dimmed", fs="italic")
        ])

class BalanceStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        banks = data_context.get("main_dashboard", {}).get("resumenes", {}).get("bancos_mn", {})
        current = banks.get("saldo", 0)
        initial = banks.get("saldo_inicial", 0)
        trend = ((current - initial) / initial) * 100 if initial != 0 else 0

        return {
            "title": "Treasury Balance",
            "value": f"${current:,.0f}",
            "meta_text": f"Start: ${initial:,.0f}",
            "trend": trend,
            "icon": "tabler:building-bank",
            "color": "violet"
        }

    def render_detail(self, data_context):
        banks = data_context.get("main_dashboard", {}).get("resumenes", {}).get("bancos_mn", {})
        income = banks.get("ingresos", 0)
        expense = banks.get("egresos", 0)
        net = income - expense

        return dmc.Stack([
            dmc.Text("Monthly Cash Flow", fw=700),
            dmc.SimpleGrid(cols=3, children=[
                dmc.Paper(p="md", bg="green.0", children=[dmc.Text("Inflow", size="xs"), dmc.Text(f"${income:,.0f}", fw=700, c="green")]),
                dmc.Paper(p="md", bg="red.0", children=[dmc.Text("Outflow", size="xs"), dmc.Text(f"${expense:,.0f}", fw=700, c="red")]),
                dmc.Paper(p="md", children=[dmc.Text("Net Flow", size="xs"), dmc.Text(f"${net:,.0f}", fw=700, c="blue")]),
            ])
        ])