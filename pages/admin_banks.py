import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, CashFlowWaterfallStrategy, DailyCashflowStrategy, 
    BankBreakdownStrategy, AdminTableStrategy
)

dash.register_page(__name__, path='/admin-banks', title='Bancos')
data_manager = DataManager()
table_strat = AdminTableStrategy()

w1 = SmartWidget("wb_1", AdminRichKPIStrategy("flujo_efectivo", "ingresos_totales", "Ingresos Totales", "tabler:arrow-up", "green"))
w2 = SmartWidget("wb_2", AdminRichKPIStrategy("flujo_efectivo", "egresos_totales", "Egresos Totales", "tabler:arrow-down", "red"))
w3 = SmartWidget("wb_3", AdminRichKPIStrategy("flujo_efectivo", "flujo_neto", "Flujo Neto", "tabler:scale", "indigo"))

c_water = ChartWidget("cb_water", CashFlowWaterfallStrategy())
c_daily = ChartWidget("cb_daily", DailyCashflowStrategy())
c_pie = ChartWidget("cb_pie", BankBreakdownStrategy())

t_detail = TableWidget(table_strat)

WIDGET_REGISTRY = { "wb_1": w1, "wb_2": w2, "wb_3": w3, "cb_water": c_water }

def layout():
    data_context = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="bank-smart-modal", size="lg", centered=True, children=[html.Div(id="bank-modal-content")]),
        
        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Bancos", order=3, c="dark"),
            dmc.Button("Conciliación", leftSection=DashIconify(icon="tabler:checks"), variant="light", size="xs")
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="xl", children=[
            w1.render(data_context), w2.render(data_context), w3.render(data_context)
        ]),

        dmc.Paper(p="xs", withBorder=True, shadow="sm", mb="lg", children=[
            c_water.render(data_context)
        ]),
        
        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 8}, children=[
                c_daily.render(data_context)
            ]),
            dmc.GridCol(span={"base": 12, "md": 4}, children=[
                c_pie.render(data_context)
            ])
        ]),

        t_detail.render(title="Saldos Bancarios Hoy", mode="banks"),
        
        dmc.Space(h=50)
    ])

@callback(
    Output("bank-smart-modal", "opened"),
    Output("bank-smart-modal", "title"),
    Output("bank-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_click(n_clicks):
    if not dash.ctx.triggered: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, dmc.Text(cfg["title"], fw=700), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update