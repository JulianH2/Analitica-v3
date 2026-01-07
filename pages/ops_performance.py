from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.operational import (
    PerformanceGaugeStrategy, PerformanceTrendStrategy, PerformanceMixStrategy,
    TableDataStrategy
)

dash.register_page(__name__, path='/ops-performance', title='Rendimiento')

data_manager = DataManager()
table_data = TableDataStrategy()

w_gauge_rend = ChartWidget("w_p_rend", PerformanceGaugeStrategy("Rend. Real/Lt", 1.86, 2.1, " km/L"))
w_gauge_kms = ChartWidget("w_p_kms", PerformanceGaugeStrategy("Kms Reales", 513, 600, "k"))
w_gauge_lts = ChartWidget("w_p_lts", PerformanceGaugeStrategy("Litros", 275, 300, "k"))

w_chart_trend = ChartWidget("w_p_trend", PerformanceTrendStrategy())
w_chart_mix = ChartWidget("w_p_mix", PerformanceMixStrategy())

WIDGET_REGISTRY = {
    "w_p_rend": w_gauge_rend, "w_p_kms": w_gauge_kms, "w_p_lts": w_gauge_lts,
    "w_p_trend": w_chart_trend, "w_p_mix": w_chart_mix
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado. Redirigiendo...", id="redirect-login")
    
    data_context = data_manager.get_data()
    
    def simple_table(headers, rows):
        return dmc.Table(
            striped="odd", withTableBorder=True, fz="xs",
            children=[
                dmc.TableThead(dmc.TableTr([dmc.TableTh(h) for h in headers])),
                dmc.TableTbody([dmc.TableTr([dmc.TableTd(c) for c in r]) for r in rows])
            ]
        )

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="perf-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="perf-modal-content")]),

        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Dashboard Rendimientos", order=3, c="dark"),
            dmc.Button("Reporte", leftSection=DashIconify(icon="tabler:download"), variant="light", size="xs")
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="lg", children=[ # type: ignore
            w_gauge_rend.render(data_context),
            w_gauge_kms.render(data_context),
            w_gauge_lts.render(data_context),
        ]),

        dmc.Paper(p="xs", withBorder=True, shadow="sm", mb="lg", children=[
            w_chart_trend.render(data_context)
        ]),

        dmc.SimpleGrid(cols={"base": 1, "lg": 3}, spacing="lg", children=[ # type: ignore
            w_chart_mix.render(data_context),
            
            dmc.Paper(p="xs", withBorder=True, shadow="sm", children=[
                dmc.Text("Rendimiento por Unidad", fw="bold", size="sm", mb="xs"),
                simple_table(["Unidad", "Rend.", "Viajes"], table_data.get_perf_unit_data())
            ]),

            dmc.Paper(p="xs", withBorder=True, shadow="sm", children=[
                dmc.Text("Rendimiento por Operador", fw="bold", size="sm", mb="xs"),
                simple_table(["Operador", "Rend.", "Viajes"], table_data.get_perf_op_data())
            ])
        ]),
        
        dmc.Space(h=50)
    ])

@callback(
    Output("perf-smart-modal", "opened"),
    Output("perf-smart-modal", "title"),
    Output("perf-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_perf_click(n_clicks):
    if not dash.ctx.triggered or not isinstance(dash.ctx.triggered_id, dict):
        return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        content = widget.strategy.render_detail(ctx) or dmc.Text("Sin detalles.")
        return True, dmc.Text(cfg.get("title"), fw="bold"), content
    return no_update, no_update, no_update