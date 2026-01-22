from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from strategies.operational import (
    OpsGaugeStrategy, CostUtilityStackedStrategy,
    CostBreakdownStrategy, OpsComparisonStrategy, OpsTableStrategy
)

dash.register_page(__name__, path="/ops-costs", title="Costos Operaciones")

SCREEN_ID = "ops-costs"
table_ops_mgr = OpsTableStrategy()

w_utilidad = SmartWidget("kc_utility", OpsGaugeStrategy("Utilidad Viaje", "utilidad_viaje", "teal", prefix="%", section="costos"))
w_costo_total = SmartWidget("kc_total", OpsGaugeStrategy("Costo Viaje Total", "costo_total", "red", section="costos"))

chart_cost_stack = ChartWidget("cc_stack", CostUtilityStackedStrategy(layout_config={"height": 380}))
chart_cost_breakdown = ChartWidget("cc_break", CostBreakdownStrategy(layout_config={"height": 380}))
chart_cost_yearly_comp = ChartWidget(
    "cc_comp",
    OpsComparisonStrategy(
        "Costo Viaje Total 2025 vs 2024", "comparativa_costos", "red", section="costos",
        layout_config={"height": 380}, indicator_key_for_meta="costo_total",
    )
)

WIDGET_REGISTRY = {"kc_utility": w_utilidad, "kc_total": w_costo_total}

def _render_ops_costs_body(ctx):
    filter_content = html.Div([
        dmc.Grid(align="center", gutter="sm", mb="xs", children=[
            dmc.GridCol(span="content", children=[
                dmc.Select(id="cost-year", data=["2025", "2024"], value="2025", variant="filled", style={"width": "100px"}, allowDeselect=False, size="sm")
            ]),
            dmc.GridCol(span="auto", children=[
                dmc.ScrollArea(w="100%", type="scroll", scrollbarSize=6, offsetScrollbars=True, children=[ # type: ignore
                    dmc.SegmentedControl(
                        id="cost-month", value="septiembre", color="blue", radius="md", size="sm", fullWidth=True, style={"minWidth": "800px"},
                        data=[{"label": m, "value": m.lower()} for m in ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]] # type: ignore
                    )
                ])
            ])
        ]),
        dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 5}, spacing="xs", children=[ # type: ignore
            dmc.Select(label="Empresa Área", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Clasificación", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Concepto Costo", data=["Todos"], value="Todos", size="xs"),
            dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Operador", data=["Todas"], value="Todas", size="xs"),
        ])
    ])

    collapsible_filters = dmc.Accordion(
        value="filtros", variant="contained", radius="md", mb="lg",
        children=[
            dmc.AccordionItem(value="filtros", children=[
                dmc.AccordionControl(dmc.Group([DashIconify(icon="tabler:filter"), dmc.Text("Filtros y Controles")]), h=40),
                dmc.AccordionPanel(filter_content)
            ])
        ]
    )

    return html.Div([
        collapsible_filters,

        dmc.Grid(gutter="md", mt="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Stack(gap="md", children=[
                    w_utilidad.render(ctx, mode="combined"),
                    w_costo_total.render(ctx, mode="combined"),
                ])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_cost_stack.render(ctx)], style={"height": "100%"})
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_cost_breakdown.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_cost_yearly_comp.render(ctx)])
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
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, px="xs", children=[
        dmc.Modal(id="costs-smart-modal", size="xl", centered=True, children=[html.Div(id="costs-modal-content")]),
        *refresh_components,
        html.Div(id="ops-costs-body", children=_render_ops_costs_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-costs-body", render_body=_render_ops_costs_body)

@callback(
    Output("costs-smart-modal", "opened"),
    Output("costs-smart-modal", "title"),
    Output("costs-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_cost_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)