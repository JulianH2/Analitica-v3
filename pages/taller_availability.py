from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    AvailabilityTrendStrategy, DowntimeReasonsStrategy, ComplexKPIStrategy
)

dash.register_page(__name__, path='/taller-availability', title='Disponibilidad')
data_manager = DataManager()

w_mtbf = SmartWidget("wa_1", ComplexKPIStrategy("MTBF", "250 hrs", "Tiempo entre fallas", 5, "green", "tabler:clock-play"))
w_mttr = SmartWidget("wa_2", ComplexKPIStrategy("MTTR", "4.5 hrs", "Tiempo reparación", -10, "red", "tabler:clock-stop"))
w_downtime = SmartWidget("wa_3", ComplexKPIStrategy("Horas Paro", "120 hrs", "Acumulado Mes", 0, "orange", "tabler:alert-triangle"))

c_trend = ChartWidget("ca_trend", AvailabilityTrendStrategy())
c_reasons = ChartWidget("ca_reasons", DowntimeReasonsStrategy())

WIDGET_REGISTRY = { "wa_1": w_mtbf, "wa_2": w_mttr, "wa_3": w_downtime, "ca_trend": c_trend, "ca_reasons": c_reasons }

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado. Redirigiendo...", id="redirect-login")
    
    data_context = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="avail-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="avail-modal-content")]),
        
        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Análisis de Disponibilidad", order=3, c="dark"),
            dmc.Button("Reporte Fallas", variant="default", size="xs")
        ]),

        dmc.SimpleGrid(cols=3, spacing="lg", mb="xl", children=[
            w_mtbf.render(data_context), w_mttr.render(data_context), w_downtime.render(data_context)
        ]),

        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 8}, children=[c_trend.render(data_context)]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[c_reasons.render(data_context)]) # type: ignore
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("avail-smart-modal", "opened"),
    Output("avail-smart-modal", "title"),
    Output("avail-modal-content", "children"),
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
        config = widget.strategy.get_card_config(ctx)
        content = widget.strategy.render_detail(ctx) or dmc.Text("Sin detalles.")
        return True, dmc.Text(config["title"], fw="bold"), content
    return no_update, no_update, no_update