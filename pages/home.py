import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import DataManager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget

from strategies.financial import (
    IncomeStrategy, CostStrategy, MarginStrategy, 
    PortfolioStrategy, SuppliersStrategy, SimpleTextStrategy
)
from strategies.operational import FleetEfficiencyStrategy
from strategies.charts import MainTrendChartStrategy

dash.register_page(__name__, path='/', title='Dashboard Principal')

data_manager = DataManager()

w_income = SmartWidget("w_income", IncomeStrategy())
w_costs = SmartWidget("w_costs", CostStrategy())
w_margin = SmartWidget("w_margin", MarginStrategy())

w_main_chart = ChartWidget("w_main_chart", MainTrendChartStrategy())

w_ops_viajes = SmartWidget("w_viajes", SimpleTextStrategy("viajes", "Viajes", "", "", "blue", "tabler:steering-wheel"))
w_ops_units = SmartWidget("w_units", SimpleTextStrategy("unidades", "Unidades Util.", "", "", "cyan", "tabler:bus"))
w_ops_clients = SmartWidget("w_clients", SimpleTextStrategy("clientes", "Clientes Serv.", "", "", "indigo", "tabler:users"))
w_ops_costkm = SmartWidget("w_costkm", SimpleTextStrategy("costkm", "Costo Km", "$", "", "orange", "tabler:ruler-2"))

w_mtto_total = SmartWidget("w_m_total", SimpleTextStrategy("mtotal", "Total Mtto", "$", "", "green", "tabler:tool"))
w_mtto_int = SmartWidget("w_m_int", SimpleTextStrategy("mint", "Taller Interno", "$", "", "teal", "tabler:building-factory"))
w_mtto_ext = SmartWidget("w_m_ext", SimpleTextStrategy("mext", "Taller Externo", "$", "", "lime", "tabler:building-store"))
w_mtto_llantas = SmartWidget("w_m_llantas", SimpleTextStrategy("mllantas", "Costo Llantas", "$", "", "gray", "tabler:circle"))
w_yield = SmartWidget("w_yield", FleetEfficiencyStrategy())
w_portfolio = ChartWidget("w_portfolio", PortfolioStrategy())
w_suppliers = ChartWidget("w_suppliers", SuppliersStrategy())

WIDGET_REGISTRY = {
    "w_income": w_income, "w_costs": w_costs, "w_margin": w_margin,
    "w_main_chart": w_main_chart,
    "w_viajes": w_ops_viajes, "w_units": w_ops_units, "w_clients": w_ops_clients, "w_costkm": w_ops_costkm,
    "w_m_total": w_mtto_total, "w_m_int": w_mtto_int, "w_m_ext": w_mtto_ext, "w_m_llantas": w_mtto_llantas,
    "w_yield": w_yield, "w_portfolio": w_portfolio, "w_suppliers": w_suppliers
}

def layout():
    data_context = data_manager.get_data()

    def truck_visual():
        return dmc.Paper(
            p="md", withBorder=True, shadow="sm", radius="md", h="100%",
            children=[
                dmc.Text("Estado Flota", size="xs", c="dimmed", fw=700),
                dmc.Center(h=100, children=DashIconify(icon="tabler:truck", width=60, color="green")),
                dmc.Progress(value=92, color="green", size="lg")
            ]
        )

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="home-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="home-modal-content")]),

        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Resumen Ejecutivo", order=3, c="dark"),
            dmc.Button("Actualizar", leftSection=DashIconify(icon="tabler:refresh"), variant="light", size="xs")
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="lg", children=[
            w_income.render(data_context),
            w_costs.render(data_context),
            w_margin.render(data_context)
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[
                w_main_chart.render(data_context)
            ]),
            
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[
                dmc.SimpleGrid(cols=2, spacing="sm", mb="sm", children=[
                    w_ops_viajes.render(data_context),
                    w_ops_units.render(data_context),
                    w_ops_clients.render(data_context),
                    w_ops_costkm.render(data_context)
                ]),
                dmc.SimpleGrid(cols=2, spacing="sm", children=[
                    w_mtto_total.render(data_context),
                    w_mtto_int.render(data_context),
                    w_mtto_ext.render(data_context),
                    w_mtto_llantas.render(data_context)
                ])
            ])
        ]),

        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="lg", children=[
            truck_visual(),                 
            w_yield.render(data_context),   
            w_portfolio.render(data_context), 
            w_suppliers.render(data_context)  
        ]),
        
        dmc.Space(h=50)
    ])

@callback(
    Output("home-smart-modal", "opened"),
    Output("home-smart-modal", "title"),
    Output("home-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_home_click(n_clicks):
    if not dash.ctx.triggered: return no_update, no_update, no_update
    btn_id = dash.ctx.triggered_id
    if not btn_id or "index" not in btn_id: return no_update, no_update, no_update
    
    w_id = btn_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        content = widget.get_detail(ctx) if hasattr(widget, 'get_detail') else widget.strategy.render_detail(ctx)
        cfg = widget.strategy.get_card_config(ctx)
        title = dmc.Text(cfg.get("title"), fw=700)
        return True, title, content
    return no_update, no_update, no_update