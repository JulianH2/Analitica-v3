from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from strategies.operational import RouteMapStrategy, RouteDetailTableStrategy

dash.register_page(__name__, path="/ops-routes", title="Análisis de Rutas")

SCREEN_ID = "ops-routes"

table_route_mgr = RouteDetailTableStrategy()
chart_route_map = ChartWidget("wr_map", RouteMapStrategy())

WIDGET_REGISTRY = {"wr_map": chart_route_map}

def _render_ops_routes_body(ctx):
    filter_content = html.Div([
         dmc.Grid(align="center", gutter="sm", mb="xs", children=[
            dmc.GridCol(span="content", children=[
                dmc.Select(id="perf-year", data=["2025"], value="2025", variant="filled", style={"width": "100px"}, allowDeselect=False, size="sm")
            ]),
            dmc.GridCol(span="auto", children=[
                dmc.ScrollArea(w="100%", type="scroll", scrollbarSize=6, offsetScrollbars="present", children=[
                    dmc.SegmentedControl(
                        id="perf-month", value="septiembre", color="blue", radius="md", size="sm", fullWidth=True, style={"minWidth": "800px"},
                        data=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                    )
                ])
            ])
        ]),
        dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 6}, spacing="xs", children=[ # type: ignore
            dmc.Select(label="Empresa Área", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Clasificación", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Operador", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Ruta", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Cliente", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Cargado/Vacío", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Origen", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Destino", data=["Todas"], value="Todas", size="xs"),
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

        dmc.Title("Análisis de Rutas", order=3, mb="lg"),

        dmc.Paper(p="md", withBorder=True, mb="xl", children=[
            dmc.Text("MAPA ANÁLISIS DE RUTAS", fw="bold", size="xs", c="gray", mb="md"),
            dcc.Graph(
                figure=chart_route_map.strategy.get_figure(ctx),
                style={"height": "650px"},
                config={"displayModeBar": False}
            )
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Text("DETALLE DE RUTAS Y UTILIZACIÓN", fw="bold", size="xs", c="gray", mb="md"),
            dmc.ScrollArea(h=500, children=[table_route_mgr.render_tabla_rutas(ctx)])
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="route-smart-modal", size="lg", centered=True, children=[html.Div(id="route-modal-content")]),
        *refresh_components,
        html.Div(id="ops-routes-body", children=_render_ops_routes_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-routes-body", render_body=_render_ops_routes_body)

@callback(
    Output("route-smart-modal", "opened"),
    Output("route-smart-modal", "title"),
    Output("route-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_route_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle de Ruta"), widget.strategy.render_detail(ctx)