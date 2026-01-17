from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager  # singleton
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from strategies.operational import (
    OpsGaugeStrategy, CostUtilityStackedStrategy,
    CostBreakdownStrategy, OpsComparisonStrategy, OpsTableStrategy
)

dash.register_page(__name__, path="/ops-costs", title="Costos Operaciones")

SCREEN_ID = "ops-costs"

table_ops_mgr = OpsTableStrategy()

gauge_cost_utility = ChartWidget("gc_utility", OpsGaugeStrategy("Utilidad Viaje", "utilidad_viaje", "green", prefix="%", section="costos"))
kpi_cost_utility = SmartWidget("kc_utility", OpsGaugeStrategy("Utilidad Viaje", "utilidad_viaje", "green", prefix="%", section="costos"))

gauge_cost_total = ChartWidget("gc_total", OpsGaugeStrategy("Costo Viaje Total", "costo_total", "red", section="costos"))
kpi_cost_total = SmartWidget("kc_total", OpsGaugeStrategy("Costo Viaje Total", "costo_total", "red", section="costos"))

chart_cost_stack = ChartWidget("cc_stack", CostUtilityStackedStrategy(layout_config={"height": 380}))
chart_cost_breakdown = ChartWidget("cc_break", CostBreakdownStrategy(layout_config={"height": 380}))

chart_cost_yearly_comp = ChartWidget(
    "cc_comp",
    OpsComparisonStrategy(
        "Costo Viaje Total 2025 vs 2024",
        "comparativa_costos",
        "red",
        section="costos",
        layout_config={"height": 380},
        indicator_key_for_meta="costo_total",
    )
)

WIDGET_REGISTRY = {
    "kc_utility": kpi_cost_utility,
    "kc_total": kpi_cost_total,
}


def _render_ops_costs_body(ctx):
    return html.Div([
        dmc.Grid(gutter="md", mt="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Stack(gap="xs", children=[
                        dmc.Group([gauge_cost_utility.render(ctx), kpi_cost_utility.render(ctx)], grow=True, align="center"),
                        dmc.Divider(my="sm", variant="dashed"),
                        dmc.Group([gauge_cost_total.render(ctx), kpi_cost_total.render(ctx)], grow=True, align="center"),
                    ])
                ])
            ]),

            dmc.GridCol(span={"base": 12, "lg": 7}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    chart_cost_stack.render(ctx)
                ])
            ]),

            dmc.GridCol(span={"base": 12, "lg": 5}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    chart_cost_breakdown.render(ctx)
                ])
            ]),

            dmc.GridCol(span={"base": 12, "lg": 7}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    chart_cost_yearly_comp.render(ctx)
                ])
            ]),
        ]),

        dmc.Divider(my="xl", label="Análisis de Margen por Ruta", labelPosition="center"),

        dmc.Paper(p="md", withBorder=True, radius="md", children=[
            dmc.Tabs(value="cliente", children=[
                dmc.TabsList([
                    dmc.TabsTab("Costos por Cliente", value="cliente"),
                    dmc.TabsTab("Costos por Unidad", value="unidad")
                ]),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[table_ops_mgr.render_tabbed_table(ctx, "cliente")]), value="cliente"),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[table_ops_mgr.render_tabbed_table(ctx, "unidad")]), value="unidad"),
            ])
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
        dmc.Modal(id="costs-smart-modal", size="xl", centered=True, children=[html.Div(id="costs-modal-content")]),

        *refresh_components,

        html.Div(id="ops-costs-body", children=_render_ops_costs_body(ctx)),
    ])


data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-costs-body",
    render_body=_render_ops_costs_body,
)


@callback(
    Output("costs-smart-modal", "opened"),
    Output("costs-smart-modal", "title"),
    Output("costs-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_cost_modal_click(n_clicks):
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
