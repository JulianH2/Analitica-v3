from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_filter_section, get_filter_ids
from strategies.operational import OpsMapStrategy, OpsTableStrategy

dash.register_page(__name__, path="/ops-routes", title="Análisis de Rutas")

SCREEN_ID = "operational-routes"

ADDITIONAL_FILTERS = [
    {
        "id": "route-d_viaje__ind_cargado",
        "label": "Vista",
        "type": "segmented",
        "data": [
            {"label": "Vacíos", "value": "0"},
            {"label": "Cargados", "value": "1"}
        ],
        "value": "0"
    },
    {
        "id": "route-foranea",
        "label": "Foránea",
        "type": "select",
        "data": ["Todas", "Sí", "No"],
        "value": "Todas"
    },
    {
        "id": "route-origen",
        "label": "Origen",
        "type": "select",
        "data": ["Todas"],
        "value": "Todas"
    },
    {
        "id": "route-destino",
        "label": "Destino",
        "type": "select",
        "data": ["Todas"],
        "value": "Todas"
    }
]
FILTER_IDS = ["route-year", "route-month"] + [f["id"] for f in ADDITIONAL_FILTERS]




def skeleton_ops_routes():
    
    from components.skeleton import skeleton_chart, skeleton_table, skeleton_box
    
    return html.Div(
        className="skeleton-layout",
        children=[
            skeleton_box("24px", "180px", "skeleton-title"),
            html.Div(
                style={"marginTop": "1.5rem"},
                children=[
                    skeleton_box("14px", "200px", "skeleton-subtitle"),
                    skeleton_chart("650px"),
                ]
            ),
            html.Div(
                style={"marginTop": "1.5rem"},
                children=[
                    skeleton_box("14px", "280px", "skeleton-subtitle"),
                    skeleton_table(12, 6)
                ]
            )
        ]
    )

chart_route_map = ChartWidget(
    "wr_map", 
    OpsMapStrategy(
        SCREEN_ID, 
        "routes_map", 
        "Mapa de Rutas Activas", 
        icon="tabler:map-2", 
        color="indigo",
        layout_config={"height": 650}
    )
)

WIDGET_REGISTRY = {"wr_map": chart_route_map}





def _render_ops_routes_body(ctx):
    theme = session.get("theme", "dark")
    
    return html.Div([
        dmc.Title("Análisis de Rutas", order=3, mb="lg", c="dimmed"), # type: ignore
        
        dmc.Paper(
            p="md", 
            withBorder=True, 
            mb="xl",
            style={"backgroundColor": "transparent"},
            children=[
                dmc.Text("MAPA ANÁLISIS DE RUTAS", fw="bold", size="xs", c="gray", mb="md"),
                dcc.Graph(
                    figure=chart_route_map.strategy.get_figure(ctx, theme=theme),
                    style={"height": "650px"}, 
                    config={"displayModeBar": False}
                )
            ]
        ),
        
        dmc.Paper(
            p="md", 
            withBorder=True,
            style={"backgroundColor": "transparent"},
            children=[
                dmc.Text("DETALLE DE RUTAS Y UTILIZACIÓN", fw="bold", size="xs", c="gray", mb="md"),
                dmc.ScrollArea(
                    h=500, 
                    children=[
                        OpsTableStrategy(SCREEN_ID, "main_routes").render(ctx, theme=theme)
                    ]
                )
            ]
        ),
        
        dmc.Space(h=50)
    ])
    
WIDGET_REGISTRY = {
    "wr_map": chart_route_map,
    "operational-routes-main_routes": TableWidget(
        "operational-routes-main_routes", 
        OpsTableStrategy(SCREEN_ID, "main_routes", title="Detalle de Rutas")
    )
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=60 * 60 * 1000,
        max_intervals=-1
    )

    filters = create_filter_section(
        year_id="route-year",
        month_id="route-month",
        additional_filters=ADDITIONAL_FILTERS
    )

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="route-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("route-drawer"),
            filters,
            html.Div(id="ops-routes-body", children=skeleton_ops_routes())
        ]
    )

FILTER_IDS = [
    "route-year", 
    "route-month", 
    "route-d_viaje__ind_cargado", 
    "route-foranea", 
    "route-origen", 
    "route-destino"
]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-routes-body",
    render_body=_render_ops_routes_body,
    filter_ids=FILTER_IDS
)

register_drawer_callback(
    drawer_id="route-drawer", 
    widget_registry=WIDGET_REGISTRY, 
    screen_id=SCREEN_ID, 
    filter_ids=FILTER_IDS
)