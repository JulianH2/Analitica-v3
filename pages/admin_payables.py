from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, PayablesForecastStrategy, SupplierMixStrategy, 
    PayablesRankingStrategy, PayablesAgingStrategy, AdminTableStrategy
)

dash.register_page(__name__, path='/admin-payables', title='Cuentas por Pagar')
data_manager = DataManager()
table_strat = AdminTableStrategy()

w1 = SmartWidget("wp_1", AdminRichKPIStrategy("cuentas_por_pagar", "total_cxp", "Total CXP", "tabler:file-dollar", "red"))
w2 = SmartWidget("wp_2", AdminRichKPIStrategy("cuentas_por_pagar", "vencido", "Saldo Vencido", "tabler:alert-triangle", "orange"))
w3 = SmartWidget("wp_3", AdminRichKPIStrategy("cuentas_por_pagar", "proveedores_activos", "Prov. Activos", "tabler:users", "blue"))

c_aging = ChartWidget("cp_aging", PayablesAgingStrategy())
c_mix = ChartWidget("cp_mix", SupplierMixStrategy())
c_rank = ChartWidget("cp_rank", PayablesRankingStrategy())
c_fore = ChartWidget("cp_fore", PayablesForecastStrategy())

t_detail = TableWidget(table_strat)

WIDGET_REGISTRY = { "wp_1": w1, "wp_2": w2, "wp_3": w3, "cp_aging": c_aging }

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado. Redirigiendo...", id="redirect-login")
    
    data_context = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="pay-smart-modal", size="lg", centered=True, children=[html.Div(id="pay-modal-content")]),
        
        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Cuentas por Pagar", order=3, c="dark"),
            dmc.Button("Programar Pagos", leftSection=DashIconify(icon="tabler:calendar-dollar"), variant="filled", color="red", size="xs")
        ]),

        dmc.SimpleGrid(cols=1, spacing="lg", mb="xl", children=[
            w1.render(data_context), w2.render(data_context), w3.render(data_context)
        ]),

        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span=12, spanMd=7, children=[
                dmc.SimpleGrid(cols=2, spacing="md", mb="md", children=[
                    c_aging.render(data_context),
                    c_mix.render(data_context)
                ]),
                c_fore.render(data_context)
            ]),
            dmc.GridCol(span=12, spanMd=5, children=[
                c_rank.render(data_context)
            ])
        ]),

        t_detail.render(title="Próximos Vencimientos", mode="payables"),
        
        dmc.Space(h=50)
    ])

@callback(
    Output("pay-smart-modal", "opened"),
    Output("pay-smart-modal", "title"),
    Output("pay-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_click(n_clicks):
    if not dash.ctx.triggered or not isinstance(dash.ctx.triggered_id, dict): 
        return no_update, no_update, no_update
    
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, dmc.Text(cfg["title"], fw="bold"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update