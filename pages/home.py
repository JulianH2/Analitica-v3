from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from strategies.executive import ExecutiveKPIStrategy, ExecutiveMiniKPIStrategy, ExecutiveDonutStrategy
from strategies.charts import MainTrendChartStrategy
from strategies.operational import FleetEfficiencyStrategy
from settings.theme import DesignSystem

dash.register_page(__name__, path='/', title='Dashboard Principal')
data_manager = DataManager()

w_income = SmartWidget("h_inc", ExecutiveKPIStrategy("operaciones", "dashboard", "ingreso_viaje", "Ingresos Totales", "tabler:coin", "indigo"))
w_costs = SmartWidget("h_cost", ExecutiveKPIStrategy("operaciones", "costos", "costo_total", "Costos Operativos", "tabler:wallet", "red"))
w_margin = SmartWidget("h_marg", ExecutiveKPIStrategy("operaciones", "costos", "utilidad_viaje", "Margen Bruto", "tabler:chart-pie", "green", is_pct=True))

w_viajes = SmartWidget("h_via", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "viajes", "Viajes", "indigo", "tabler:steering-wheel"))
w_units = SmartWidget("h_uni", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "unidades_utilizadas", "Unidades Util.", "indigo", "tabler:bus"))
w_clients = SmartWidget("h_cli", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "clientes_servidos", "Clientes Serv.", "indigo", "tabler:users"))
w_costkm = SmartWidget("h_ckm", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_km", "Costo Mtto Km", "yellow", "tabler:ruler-2", prefix="$"))

w_m_total = SmartWidget("h_mt", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "total_mantenimiento", "Total Mtto", "green", "tabler:tool", prefix="$"))
w_m_int = SmartWidget("h_mi", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_interno", "Taller Interno", "green", "tabler:building-factory", prefix="$"))
w_m_ext = SmartWidget("h_me", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_externo", "Taller Externo", "green", "tabler:building-store", prefix="$"))
w_m_llantas = SmartWidget("h_ml", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_llantas", "Costo Llantas", "gray", "tabler:circle", prefix="$"))

w_main_chart = ChartWidget("h_chart", MainTrendChartStrategy())
w_yield = SmartWidget("h_yield", FleetEfficiencyStrategy())
w_portfolio = ChartWidget("h_port", ExecutiveDonutStrategy("Cartera Clientes", "administracion", "facturacion_cobranza", {"SIN CARTA COBRO": "indigo", "POR VENCER": "yellow", "VENCIDO": "red"}))
w_suppliers = ChartWidget("h_supp", ExecutiveDonutStrategy("Saldo Proveedores", "administracion", "cuentas_por_pagar", {"POR VENCER": "indigo", "VENCIDO": "red"}))

WIDGET_REGISTRY = {
    "h_inc": w_income, "h_cost": w_costs, "h_marg": w_margin, "h_yield": w_yield
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()

    def truck_visual():
        val = ctx["operaciones"]["dashboard"]["utilizacion"]["valor"]
        return dmc.Paper(p="md", withBorder=True, shadow="sm", radius="md", h="100%", children=[
            dmc.Text("Estado Carga Flota", size="xs", c="gray", fw="bold"),
            dmc.Center(h=100, children=DashIconify(icon="tabler:truck", width=60, color=DesignSystem.SUCCESS[5])),
            dmc.Progress(value=val, color="green", size="lg"),
            dmc.Text(f"{val}% Cargado", size="xs", ta="center", mt=5, fw="bold")
        ])

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="home-smart-modal", size="xl", centered=True, children=[html.Div(id="home-modal-content")]),
        dmc.Title("Resumen Ejecutivo", order=3, mb="lg"),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="lg", children=[ # type: ignore
            w_income.render(ctx), w_costs.render(ctx), w_margin.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[w_main_chart.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.SimpleGrid(cols=2, spacing="sm", mb="sm", children=[
                    w_viajes.render(ctx), w_units.render(ctx), w_clients.render(ctx), w_costkm.render(ctx)
                ]),
                dmc.SimpleGrid(cols=2, spacing="sm", children=[
                    w_m_total.render(ctx), w_m_int.render(ctx), w_m_ext.render(ctx), w_m_llantas.render(ctx)
                ])
            ])
        ]),

        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="lg", children=[ # type: ignore
            truck_visual(), w_yield.render(ctx), w_portfolio.render(ctx), w_suppliers.render(ctx)
        ])
    ])

@callback(
    Output("home-smart-modal", "opened"), Output("home-smart-modal", "title"), Output("home-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_home_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"] # type: ignore
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update