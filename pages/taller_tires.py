import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    TirePressureStrategy, TireCostPerMmStrategy, ComplexKPIStrategy
)

dash.register_page(__name__, path='/taller-tires', title='Llantas')
data_manager = DataManager()

w_gasto = SmartWidget("wl_1", ComplexKPIStrategy("Gasto Llantas", "$250k", "Mes Actual", 0, "orange", "tabler:circle"))
w_desecho = SmartWidget("wl_2", ComplexKPIStrategy("En Desecho", "12", "Pila Scrap", 0, "gray", "tabler:trash"))
w_renov = SmartWidget("wl_3", ComplexKPIStrategy("Renovabilidad", "1.8", "Vidas Promedio", 0, "green", "tabler:recycle"))

c_press = ChartWidget("cl_press", TirePressureStrategy())
c_cost = ChartWidget("cl_cost", TireCostPerMmStrategy())

WIDGET_REGISTRY = { "wl_1": w_gasto, "wl_2": w_desecho, "wl_3": w_renov, "cl_press": c_press, "cl_cost": c_cost }

def layout():
    data_context = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="tires-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="tires-modal-content")]),
        
        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Gestión de Llantas", order=3, c="dark"),
            dmc.Button("Semáforo Presiones", variant="light", size="xs")
        ]),

        dmc.SimpleGrid(cols=3, spacing="lg", mb="xl", children=[
            w_gasto.render(data_context), w_desecho.render(data_context), w_renov.render(data_context)
        ]),

        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[c_press.render(data_context)]),
            dmc.GridCol(span={"base": 12, "md": 8}, children=[c_cost.render(data_context)])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("tires-smart-modal", "opened"),
    Output("tires-smart-modal", "title"),
    Output("tires-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_click(n_clicks):
    if not dash.ctx.triggered: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        config = widget.strategy.get_card_config(ctx)
        content = widget.strategy.render_detail(ctx) or dmc.Text("Sin detalles.")
        return True, dmc.Text(config["title"], fw=700), content
    return no_update, no_update, no_update