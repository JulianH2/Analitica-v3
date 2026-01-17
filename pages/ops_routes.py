from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager  # singleton
from components.visual_widget import ChartWidget
from strategies.operational import RouteMapStrategy, RouteDetailTableStrategy

dash.register_page(__name__, path="/ops-routes", title="Análisis de Rutas")

SCREEN_ID = "ops-routes"

table_route_mgr = RouteDetailTableStrategy()
chart_route_map = ChartWidget("wr_map", RouteMapStrategy())

WIDGET_REGISTRY = {"wr_map": chart_route_map}


def _render_ops_routes_body(ctx):
    return html.Div([
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 6}, spacing="xs", children=[  # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["septiembre"], value="septiembre", size="xs"),
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
        ]),

        dmc.Title("Análisis de Rutas", order=3, mb="lg"),

        dmc.Paper(p="md", withBorder=True, mb="xl", children=[
            dmc.Text("MAPA ANÁLISIS DE RUTAS", fw="bold", size="xs", c="gray", mb="md"),
            chart_route_map.render(ctx)
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Text("DETALLE DE RUTAS Y UTILIZACIÓN", fw="bold", size="xs", c="gray", mb="md"),
            dmc.ScrollArea(h=500, children=[table_route_mgr.render_tabla_rutas(ctx)])
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

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="route-smart-modal", size="lg", centered=True, children=[html.Div(id="route-modal-content")]),

        *refresh_components,

        html.Div(id="ops-routes-body", children=_render_ops_routes_body(ctx)),
    ])


data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-routes-body",
    render_body=_render_ops_routes_body,
)


@callback(
    Output("route-smart-modal", "opened"),
    Output("route-smart-modal", "title"),
    Output("route-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_route_modal_click(n_clicks):
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
    return True, cfg.get("title", "Detalle de Ruta"), widget.strategy.render_detail(ctx)
