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
    AdminRichKPIStrategy, CollectionEvolutionStrategy, 
    CollectionMixStrategy, DebtorsRankingStrategy, AdminTableStrategy
)

dash.register_page(__name__, path='/admin-collection', title='Cobranza')
data_manager = DataManager()
table_strat = AdminTableStrategy()

w1 = SmartWidget("wc_1", AdminRichKPIStrategy("facturacion_cobranza", "facturado_vs_cobrado", "Facturado vs Cobrado", "tabler:file-invoice", "blue"))
w2 = SmartWidget("wc_2", AdminRichKPIStrategy("facturacion_cobranza", "dias_cartera", "Días Cartera", "tabler:calendar-stats", "orange"))
w3 = SmartWidget("wc_3", AdminRichKPIStrategy("facturacion_cobranza", "facturado_acumulado", "Facturado YTD", "tabler:chart-bar", "indigo"))
w4 = SmartWidget("wc_4", AdminRichKPIStrategy("facturacion_cobranza", "cobrado_acumulado", "Cobrado YTD", "tabler:cash", "green"))

c_evol = ChartWidget("cc_evol", CollectionEvolutionStrategy())
c_mix = ChartWidget("cc_mix", CollectionMixStrategy())
c_rank = ChartWidget("cc_rank", DebtorsRankingStrategy())

t_detail = TableWidget(table_strat)

WIDGET_REGISTRY = { "wc_1": w1, "wc_2": w2, "wc_3": w3, "wc_4": w4, "cc_evol": c_evol, "cc_mix": c_mix, "cc_rank": c_rank }

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado. Redirigiendo...", id="redirect-login")
    data_context = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="col-smart-modal", size="lg", centered=True, children=[html.Div(id="col-modal-content")]),
        
        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Facturacion y Cobranza", order=3, c="dark"),
            dmc.Group([
                dmc.Button("Antigüedad", variant="default", size="xs"),
                dmc.Button("Estados de Cuenta", leftSection=DashIconify(icon="tabler:mail"), variant="filled", color="blue", size="xs")
            ])
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 4}, spacing="lg", mb="xl", children=[ # type: ignore
            w1.render(data_context), w2.render(data_context), w3.render(data_context), w4.render(data_context)
        ]),

        dmc.Grid(gutter="md", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[c_evol.render(data_context)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 3}, children=[c_mix.render(data_context)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[c_rank.render(data_context)]), # type: ignore
        ]),

        t_detail.render(title="Resumen de Cartera por Área", mode="collection"),
        
        dmc.Space(h=50)
    ])

@callback(
    Output("col-smart-modal", "opened"),
    Output("col-smart-modal", "title"),
    Output("col-modal-content", "children"),
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