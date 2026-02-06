from components.skeleton import get_skeleton
from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_filter_section
from strategies.operational import OpsMapStrategy, OpsTableStrategy

dash.register_page(__name__, path="/ops-routes", title="Analisis de Rutas")

SCREEN_ID = "operational-routes"

chart_route_map = ChartWidget(
    "wr_map",
    OpsMapStrategy(
        screen_id=SCREEN_ID,
        chart_key="routes_map",
        title="Mapa de Rutas Activas",
        icon="tabler:map-2",
        color="indigo"
    )
)

WIDGET_REGISTRY = {
    "wr_map": chart_route_map
}

def _render_ops_routes_body(ctx):
    return html.Div([
        dmc.Paper(
            p="md",
            withBorder=True,
            mb="lg",
            children=[
                dmc.Text("MAPA ANALISIS DE RUTAS", fw="bold", size="xs", c="gray", mb="md"),
                dcc.Graph(
                    figure=chart_route_map.strategy.get_figure(ctx),
                    style={"height": "550px"},
                    config={"displayModeBar": False}
                )
            ]
        ),
        dmc.Paper(
            p="md",
            withBorder=True,
            children=[
                dmc.Text("DETALLE DE RUTAS Y UTILIZACION", fw="bold", size="xs", c="gray", mb="md"),
                dmc.ScrollArea(
                    h=400,
                    children=[OpsTableStrategy(SCREEN_ID, "main_routes").render(ctx)]
                )
            ]
        ),
        dmc.Space(h=30)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    filters = create_filter_section(
        year_id="route-year",
        month_id="route-month",
        default_month="septiembre",
        additional_filters=[
            {"id": "route-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": "route-clasificacion", "label": "Clasificacion", "data": ["Todas"], "value": "Todas"},
            {"id": "route-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": "route-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"},
            {"id": "route-ruta", "label": "Ruta", "data": ["Todas"], "value": "Todas"},
            {"id": "route-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"},
            {"id": "route-cargado", "label": "Cargado/Vacio", "data": ["Todas"], "value": "Todas"},
            {"id": "route-origen", "label": "Origen", "data": ["Todas"], "value": "Todas"},
            {"id": "route-destino", "label": "Destino", "data": ["Todas"], "value": "Todas"}
        ]
    )
    return dmc.Container(
        fluid=True,
        children=[
            create_smart_modal("route-modal"),
            *refresh_components,
            filters,
            html.Div(id="ops-routes-body", children=get_skeleton(SCREEN_ID))
        ]
    )

FILTER_IDS = [
    "route-year",
    "route-month",
    "route-empresa",
    "route-clasificacion",
    "route-unidad",
    "route-operador",
    "route-ruta",
    "route-cliente",
    "route-cargado",
    "route-origen",
    "route-destino"
]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-routes-body",
    render_body=_render_ops_routes_body,
    filter_ids=FILTER_IDS
)

register_modal_callback("route-modal", WIDGET_REGISTRY, SCREEN_ID)