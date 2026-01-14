from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from strategies.operational import RouteMapStrategy, RouteDetailTableStrategy

dash.register_page(__name__, path='/ops-routes', title='Análisis de Rutas')
data_manager = DataManager()
table_route_mgr = RouteDetailTableStrategy()

chart_route_map = ChartWidget("wr_map", RouteMapStrategy())

WIDGET_REGISTRY = {"wr_map": chart_route_map}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data("operaciones")
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="route-smart-modal", size="lg", centered=True, children=[html.Div(id="route-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 6}, spacing="xs", children=[# type: ignore
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

@callback(
    Output("route-smart-modal", "opened"), Output("route-smart-modal", "title"), Output("route-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_route_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data("operaciones")
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle de Ruta"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update