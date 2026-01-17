from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager  # singleton
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.operational import (
    PerformanceGaugeStrategy, PerformanceTrendStrategy,
    PerformanceMixStrategy, PerformanceTableStrategy
)

dash.register_page(__name__, path="/ops-performance", title="Rendimientos")

SCREEN_ID = "ops-performance"

table_perf_mgr = PerformanceTableStrategy()

MAIN_KPI_H = 195
top_layout = {"height": MAIN_KPI_H, "span": 2}

w_kms_lt = SmartWidget("rp_kms_lt", PerformanceGaugeStrategy("Rendimiento Kms/Lt", "kms_lt", "indigo", layout_config=top_layout))
w_kms_tot = SmartWidget("rp_kms_tot", PerformanceGaugeStrategy("Kilómetros Reales", "kms_reales", "green", layout_config=top_layout))
w_litros = SmartWidget("rp_litros", PerformanceGaugeStrategy("Litros Consumidos", "litros", "yellow", layout_config=top_layout))

w_gauge_kms_lt = ChartWidget("gp_kms_lt", PerformanceGaugeStrategy("Visual Rendimiento", "kms_lt", "indigo", layout_config={"height": 180}))
w_gauge_kms_tot = ChartWidget("gp_kms_tot", PerformanceGaugeStrategy("Visual Kms", "kms_reales", "green", layout_config={"height": 180}))
w_gauge_litros = ChartWidget("gp_litros", PerformanceGaugeStrategy("Visual Litros", "litros", "yellow", layout_config={"height": 180}))

w_trend = ChartWidget("cp_trend", PerformanceTrendStrategy(layout_config={"height": 350}))
w_mix = ChartWidget("cp_mix", PerformanceMixStrategy(layout_config={"height": 350}))

WIDGET_REGISTRY = {
    "rp_kms_lt": w_kms_lt,
    "rp_kms_tot": w_kms_tot,
    "rp_litros": w_litros
}


def _render_ops_performance_body(ctx):
    return html.Div([
        dmc.Paper(p="xs", withBorder=True, mb="md", mt="xs", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 5}, spacing="xs", children=[  # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["septiembre"], value="septiembre", size="xs"),
                dmc.Select(label="Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Operador", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.SimpleGrid(cols={"base": 1, "sm": 3}, spacing="xs", mb="md", children=[  # type: ignore
            w_kms_lt.render(ctx), w_kms_tot.render(ctx), w_litros.render(ctx)
        ]),

        dmc.SimpleGrid(cols={"base": 1, "sm": 3}, spacing="xs", mb="md", children=[  # type: ignore
            w_gauge_kms_lt.render(ctx), w_gauge_kms_tot.render(ctx), w_gauge_litros.render(ctx)
        ]),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "md": 8}, children=[w_trend.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[w_mix.render(ctx)]),    # type: ignore
        ]),

        dmc.Grid(gutter="xs", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Rendimiento por Unidad", fw="bold", size="sm", mb="md"),
                    dmc.ScrollArea(h=350, children=[table_perf_mgr.render_unit(ctx)])
                ])
            ]),
            dmc.GridCol(span={"base": 12, "md": 7}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Rendimiento por Operador", fw="bold", size="sm", mb="md"),
                    dmc.ScrollArea(h=350, children=[table_perf_mgr.render_operador(ctx)])
                ])
            ]),
        ]),

        dmc.Space(h=50)
    ])


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    # primer paint rápido (base/cache slice)
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    # auto-refresh 1 vez al entrar
    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, px="xs", children=[
        dmc.Modal(id="perf-smart-modal", size="xl", centered=True, children=[html.Div(id="perf-modal-content")]),

        *refresh_components,

        html.Div(id="ops-performance-body", children=_render_ops_performance_body(ctx)),
    ])


data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-performance-body",
    render_body=_render_ops_performance_body,
)


@callback(
    Output("perf-smart-modal", "opened"),
    Output("perf-smart-modal", "title"),
    Output("perf-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_perf_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update

    if dash.ctx.triggered_id is None:
        return no_update, no_update, no_update

    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget:
        return no_update, no_update, no_update

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
