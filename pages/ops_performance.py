from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from strategies.operational import (
    PerformanceGaugeStrategy, PerformanceTrendStrategy, 
    PerformanceMixStrategy, PerformanceTableStrategy
)

dash.register_page(__name__, path='/ops-performance', title='Rendimientos')
data_manager = DataManager()
table_perf_mgr = PerformanceTableStrategy()

gauge_perf_kms_lt = ChartWidget("gp_kms_lt", PerformanceGaugeStrategy("Kms. Reales/Lt", "kms_lt", "#228be6"))
gauge_perf_kms_total = ChartWidget("gp_kms_total", PerformanceGaugeStrategy("Kms. Reales", "kms_reales", "#40c057"))
gauge_perf_litros = ChartWidget("gp_litros", PerformanceGaugeStrategy("Litros Totales", "litros", "#fab005"))

chart_perf_trend = ChartWidget("cp_trend", PerformanceTrendStrategy())
chart_perf_mix = ChartWidget("cp_mix", PerformanceMixStrategy())

WIDGET_REGISTRY = {
    "gp_kms_lt": gauge_perf_kms_lt,
    "gp_kms_total": gauge_perf_kms_total,
    "gp_litros": gauge_perf_litros,
    "cp_trend": chart_perf_trend,
    "cp_mix": chart_perf_mix
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="perf-smart-modal", size="lg", centered=True, children=[html.Div(id="perf-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 5}, spacing="xs", children=[  # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["septiembre"], value="septiembre", size="xs"),
                dmc.Select(label="Empresa Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Operador", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),
        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="xl", children=[  # type: ignore
            gauge_perf_kms_lt.render(ctx), gauge_perf_kms_total.render(ctx), gauge_perf_litros.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 8}, children=[chart_perf_trend.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_perf_mix.render(ctx)]),  # type: ignore
        ]),

        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("Rendimiento Real por Unidad", fw="bold", size="sm", mb="md"),
                    table_perf_mgr.render_unit(ctx)
                ])
            ]),
            dmc.GridCol(span={"base": 12, "md": 8}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("Rendimiento por Operador", fw="bold", size="sm", mb="md"),
                    dmc.ScrollArea(h=300, children=[table_perf_mgr.render_operador(ctx)])
                ])
            ])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("perf-smart-modal", "opened"), Output("perf-smart-modal", "title"), Output("perf-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_perf_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]  # type: ignore
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update