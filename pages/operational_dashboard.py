from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.operational import (
    OpsGaugeStrategy, OpsComparisonStrategy, OpsPieStrategy,
    BalanceUnitStrategy, OpsTableStrategy
)
from strategies.administration import AdminRichKPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import safe_get

dash.register_page(__name__, path="/ops-dashboard", title="Control Operativo")

SCREEN_ID = "ops-dashboard"
table_ops_mgr = OpsTableStrategy()

MAIN_KPI_H = 205
VISUAL_H = 360
top_layout = {"height": MAIN_KPI_H, "span": 2}

w_inc = SmartWidget("go_inc", OpsGaugeStrategy("Ingreso Viaje", "ingreso_viaje", "indigo", layout_config=top_layout))
w_tri = SmartWidget("go_tri", OpsGaugeStrategy("Viajes", "viajes", "green", prefix="", layout_config=top_layout))
w_kms = SmartWidget("go_kms", OpsGaugeStrategy("Kilómetros", "kilometros", "yellow", prefix="", layout_config=top_layout))

w_avg_trip = SmartWidget("avg_trip", OpsGaugeStrategy("Prom. x Viaje", "ingreso_viaje", "blue"))
w_avg_unit = SmartWidget("avg_unit", OpsGaugeStrategy("Prom. x Unidad", "ingreso_unit", "indigo"))
w_units_qty = SmartWidget("units_qty", OpsGaugeStrategy("Unidades Uso", "unidades_utilizadas", "violet"))
w_customers = SmartWidget("customers", OpsGaugeStrategy("Clientes", "clientes_servidos", "teal"))

w_inc_comp = ChartWidget("co_inc_comp", OpsComparisonStrategy("Ingresos 2025 vs 2024", "ingresos_anual", "indigo", layout_config={"height": VISUAL_H}))
w_trips_comp = ChartWidget("co_trips_comp", OpsComparisonStrategy("Viajes 2025 vs 2024", "viajes_anual", "green", layout_config={"height": VISUAL_H}))
w_mix = ChartWidget("co_mix", OpsPieStrategy(layout_config={"height": 445}))
w_unit_bal = ChartWidget("co_unit_bal", BalanceUnitStrategy(layout_config={"height": 380}))

WIDGET_REGISTRY = {
    "go_inc": w_inc, "go_tri": w_tri, "go_kms": w_kms,
    "ko_avg_trip": w_avg_trip, "ko_avg_unit": w_avg_unit, "ko_units": w_units_qty
}

def get_filters_layout():
    filter_content = html.Div([
        dmc.Grid(align="center", gutter="sm", mb="xs", children=[
            dmc.GridCol(span="content", children=[
                dmc.Select(id="ops-year", data=["2026","2025", "2024"], value="2026", variant="filled", style={"width": "100px"}, allowDeselect=False, size="sm")
            ]),
            dmc.GridCol(span="auto", children=[
                dmc.ScrollArea(w="100%", type="scroll", scrollbarSize=6, offsetScrollbars=True, children=[ # type: ignore
                    dmc.SegmentedControl(
                        id="ops-month", value="enero", color="blue", radius="md", size="sm", fullWidth=True, style={"minWidth": "800px"},
                        data=[{"label": m, "value": m.lower()} for m in ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]] # type: ignore
                    )
                ])
            ])
        ]),
        dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 5}, spacing="xs", children=[ # type: ignore
            dmc.Select(id="d_empresa", label="Empresa Área", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(id="d_clasificacion", label="Clasificación", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(id="d_cliente", label="Cliente", data=["Todos"], value="Todos", size="xs"),
            dmc.Select(id="d_unidad", label="Unidad", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(id="d_operador", label="Operador", data=["Todas"], value="Todas", size="xs"),
        ])
    ])

    return dmc.Accordion(
        value="filtros",
        variant="contained",
        radius="md",
        mb="lg",
        children=[
            dmc.AccordionItem(value="filtros", children=[
                dmc.AccordionControl(dmc.Group([DashIconify(icon="tabler:filter"), dmc.Text("Filtros y Controles")]), h=40),
                dmc.AccordionPanel(filter_content)
            ])
        ]
    )

def _render_body(ctx):
    def fleet_status():
        val = safe_get(ctx, "operaciones.dashboard.utilizacion.valor", 92)
        return dmc.Paper(p="md", withBorder=True, radius="md", h=420, children=[
            dmc.Stack(justify="center", align="center", h="100%", children=[
                dmc.Text("Estado de Carga de Flota", fw="bold", size="xs", c="dimmed", tt="uppercase"),  # type: ignore
                DashIconify(icon="tabler:truck-loading", width=60, color=DesignSystem.SUCCESS[5]),
                dmc.Text(f"{val}% Cargado", fw="bold", size="xl", c="green"),
                dmc.Progress(value=val, color="green", h=22, radius="xl", style={"width": "100%"}),
            ])
        ])

    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 1, "lg": 3},  # type: ignore
            spacing="md", mb="md", mt="xs", 
            children=[w_inc.render(ctx, mode="combined"), w_tri.render(ctx, mode="combined"), w_kms.render(ctx, mode="combined")]
        ),
        dmc.SimpleGrid(
            cols={"base": 2, "sm": 4, "lg": 4},  # type: ignore
            spacing="xs", mb="md", 
            children=[w_avg_trip.render(ctx), w_avg_unit.render(ctx), w_units_qty.render(ctx), w_customers.render(ctx)]
        ),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "md": 6}, children=[w_inc_comp.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 6}, children=[w_trips_comp.render(ctx)]),  # type: ignore
        ]),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[fleet_status()]),  # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", h=420, children=[
                    dmc.Tabs(value="rutas_vacio", children=[
                        dmc.TabsList([
                            dmc.TabsTab("Rutas Vacío", value="rutas_vacio", leftSection=DashIconify(icon="tabler:map-pin-off")),
                            dmc.TabsTab("Rutas Cargado", value="rutas_cargado", leftSection=DashIconify(icon="tabler:map-pin")),
                        ]),
                        dmc.TabsPanel(
                            dmc.ScrollArea(h=350, pt="xs", children=[
                                table_ops_mgr.render_tabbed_table(ctx, "rutas_vacio")
                            ]), 
                            value="rutas_vacio"
                        ),
                        dmc.TabsPanel(
                            dmc.ScrollArea(h=350, pt="xs", children=[
                                table_ops_mgr.render_tabbed_table(ctx, "rutas_cargado")
                            ]), 
                            value="rutas_cargado"
                        )
                    ])
                ])
            ])
        ]),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[w_mix.render(ctx)]),  # type: ignore

            dmc.GridCol(span={"base": 12, "md": 7}, children=[ # type: ignore
                 dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Balanceo de Ingresos por Unidad", fw=600, size="sm", mb="sm", c="dimmed"), # type: ignore
                    dmc.ScrollArea(
                        h=380,
                        type="auto",
                        offsetScrollbars=True, # type: ignore
                        children=[
                            dcc.Graph(
                                figure=w_unit_bal.strategy.get_figure(ctx),
                                config={"displayModeBar": False},
                                style={"height": "100%", "width": "100%"}
                            )
                        ]
                    )
                ])
            ]),
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Tabs(value="ingreso_cliente", children=[ 
                dmc.TabsList([
                    dmc.TabsTab("Ingreso Cliente", value="ingreso_cliente"),
                    dmc.TabsTab("Ingreso Operador", value="ingreso_operador"),
                    dmc.TabsTab("Ingreso Unidad", value="ingreso_unidad")
                ]),
                
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", type="auto", children=[
                    table_ops_mgr.render_tabbed_table(ctx, "ingreso_cliente")
                ]), value="ingreso_cliente"),
                
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", type="auto", children=[
                    table_ops_mgr.render_tabbed_table(ctx, "ingreso_operador")
                ]), value="ingreso_operador"),
                
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", type="auto", children=[
                    table_ops_mgr.render_tabbed_table(ctx, "ingreso_unidad")
                ]), value="ingreso_unidad"),
            ])
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, ids = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, px="xs", children=[
        dmc.Modal(id="ops-smart-modal", size="xl", centered=True, children=[html.Div(id="ops-modal-content")]),
        *refresh_components,
        get_filters_layout(),
        html.Div(id="ops-body", children=_render_body(ctx)),
    ])

FILTROS_ACTIVOS = [
    "ops-year", 
    "ops-month", 
    "d_empresa", 
    "d_clasificacion", 
    "d_cliente", 
    "d_unidad", 
    "d_operador"
]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID, 
    body_output_id="ops-body", 
    render_body=_render_body,
    filter_ids=FILTROS_ACTIVOS
)

@callback(
    Output("ops-smart-modal", "opened"), Output("ops-smart-modal", "title"), Output("ops-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_ops_dashboard_modal(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)