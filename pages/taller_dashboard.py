import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.taller import (
    WorkshopStatusStrategy, TopFailuresStrategy, WorkshopTableStrategy, ComplexKPIStrategy
)

dash.register_page(__name__, path='/taller-dashboard', title='Taller General')
data_manager = DataManager()
table_strat = WorkshopTableStrategy()

w_disp = SmartWidget("wt_1", ComplexKPIStrategy("Disponibilidad", "92.5%", "Meta: 95%", -2.5, "red", "tabler:activity"))
w_taller = SmartWidget("wt_2", ComplexKPIStrategy("Unidades Taller", "12", "4 Criticas", 0, "orange", "tabler:tool"))
w_ordenes = SmartWidget("wt_3", ComplexKPIStrategy("Ordenes Abiertas", "25", "5 por cerrar", 0, "blue", "tabler:file-text"))
w_costo = SmartWidget("wt_4", ComplexKPIStrategy("Gasto Mes", "$450k", "Presup: $500k", 10, "green", "tabler:currency-dollar"))

c_status = ChartWidget("ct_status", WorkshopStatusStrategy())
c_pareto = ChartWidget("ct_pareto", TopFailuresStrategy())
t_piso = TableWidget(table_strat)

WIDGET_REGISTRY = { "wt_1": w_disp, "wt_2": w_taller, "wt_3": w_ordenes, "wt_4": w_costo, "ct_status": c_status, "ct_pareto": c_pareto }

def layout():
    data_context = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="taller-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="taller-modal-content")]),
        
        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Gestión de Mantenimiento", order=3, c="dark"),
            dmc.Button("Nueva Orden", leftSection=DashIconify(icon="tabler:plus"), variant="filled", size="xs")
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 4}, spacing="lg", mb="xl", children=[
            w_disp.render(data_context), w_taller.render(data_context), w_ordenes.render(data_context), w_costo.render(data_context)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[c_status.render(data_context)]),
            dmc.GridCol(span={"base": 12, "md": 8}, children=[c_pareto.render(data_context)])
        ]),

        dmc.Paper(p="xs", withBorder=True, shadow="sm", children=[
            dmc.Text("Control de Piso (Unidades en Servicio)", fw=700, size="sm", mb="xs"),
            t_piso.render()
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("taller-smart-modal", "opened"),
    Output("taller-smart-modal", "title"),
    Output("taller-modal-content", "children"),
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