import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.taller import (
    InventoryTurnoverStrategy, PartsTableStrategy, ComplexKPIStrategy
)

dash.register_page(__name__, path='/taller-inventory', title='Inventario')
data_manager = DataManager()
table_strat = PartsTableStrategy()

w_val = SmartWidget("wi_1", ComplexKPIStrategy("Valor Inventario", "$1.2M", "Refacciones", 0, "blue", "tabler:packages"))
w_crit = SmartWidget("wi_2", ComplexKPIStrategy("Stock Crítico", "15 SKUs", "Bajo Mínimo", 0, "red", "tabler:alert-circle"))
w_rot = SmartWidget("wi_3", ComplexKPIStrategy("Rotación Global", "3.5", "Vueltas/Año", 0, "green", "tabler:refresh"))

c_rot = ChartWidget("ci_rot", InventoryTurnoverStrategy())
t_parts = TableWidget(table_strat)

WIDGET_REGISTRY = { "wi_1": w_val, "wi_2": w_crit, "wi_3": w_rot, "ci_rot": c_rot }

def layout():
    data_context = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="inv-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="inv-modal-content")]),
        
        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Almacén", order=3, c="dark"),
            dmc.Button("Surtir Stock", leftSection=DashIconify(icon="tabler:shopping-cart"), variant="filled", color="orange", size="xs")
        ]),

        dmc.SimpleGrid(cols=3, spacing="lg", mb="xl", children=[
            w_val.render(data_context), w_crit.render(data_context), w_rot.render(data_context)
        ]),

        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[c_rot.render(data_context)]),
            dmc.GridCol(span={"base": 12, "md": 7}, children=[
                dmc.Paper(p="xs", withBorder=True, shadow="sm", children=[
                    dmc.Text("Refacciones Críticas (Reorder Point)", fw=700, size="sm", mb="xs"),
                    t_parts.render()
                ])
            ])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("inv-smart-modal", "opened"),
    Output("inv-smart-modal", "title"),
    Output("inv-modal-content", "children"),
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