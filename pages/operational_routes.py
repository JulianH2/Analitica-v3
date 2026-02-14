from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_filter_section
from strategies.operational import OpsMapStrategy, OpsTableStrategy

dash.register_page(__name__, path="/ops-routes", title="Análisis de Rutas")
SCREEN_ID = "operational-routes"

chart_route_map = ChartWidget("wr_map", OpsMapStrategy(SCREEN_ID, "routes_map", "Mapa de Rutas Activas", icon="tabler:map-2", color="indigo"))
WIDGET_REGISTRY = {"wr_map": chart_route_map}

def _render_ops_routes_body(ctx):
    theme = session.get("theme", "dark")
    return html.Div([
        dmc.Title("Análisis de Rutas", order=3, mb="lg"),
        dmc.Paper(p="md", withBorder=True, mb="xl", children=[
            dmc.Text("MAPA ANÁLISIS DE RUTAS", fw="bold", size="xs", c="gray", mb="md"),
            dcc.Graph(figure=chart_route_map.strategy.get_figure(ctx, theme=theme),
                style={"height": "650px"}, config={"displayModeBar": False})
        ]),
        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Text("DETALLE DE RUTAS Y UTILIZACIÓN", fw="bold", size="xs", c="gray", mb="md"),
            dmc.ScrollArea(h=500, children=[OpsTableStrategy(SCREEN_ID, "main_routes").render(ctx, theme=theme)])
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    filters = create_filter_section(year_id="route-year", month_id="route-month", default_month="enero",
        checkbox_filters=[
            {"id": "route-foranea", "label": "Ruta foránea"},
            {"id": "route-local", "label": "Ruta local"},
            {"id": "route-normal", "label": "Ruta normal"},
            {"id": "route-circuito", "label": "Ruta circuito"}
        ],
        additional_filters=[
            {"id": "route-d_viaje__ind_cargado", "label": "Vista Mapa",
             "data": [{"label": "Ver mapa de vacíos", "value": "0"}, {"label": "Ver mapa cargados", "value": "1"}], "value": "0"},
            {"id": "route-origen", "label": "Origen", "data": ["Todas"], "value": "Todas"},
            {"id": "route-destino", "label": "Destino", "data": ["Todas"], "value": "Todas"}
        ])
    return dmc.Container(fluid=True, children=[create_smart_modal("route-modal"), *refresh_components, filters,
        html.Div(id="ops-routes-body", children=_render_ops_routes_body(ctx))])

FILTER_IDS = ["route-year", "route-month", "route-d_viaje__ind_cargado", "route-foranea", "route-local",
              "route-normal", "route-circuito", "route-origen", "route-destino"]
data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-routes-body",
    render_body=_render_ops_routes_body, filter_ids=FILTER_IDS)
register_modal_callback("route-modal", WIDGET_REGISTRY, SCREEN_ID)