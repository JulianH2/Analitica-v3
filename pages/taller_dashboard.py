from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    TallerGaugeStrategy, TallerNeedleGaugeStrategy, TallerTrendStrategy,
    TallerHorizontalBarStrategy, TallerDonutStrategy, TallerMaintenanceTypeStrategy
)

dash.register_page(__name__, path="/taller-dashboard", title="Mantenimiento")

SCREEN_ID = "taller-dashboard"

w_interno = SmartWidget("wt_int", TallerGaugeStrategy("Costo Interno", "internal_labour_cost", "indigo"))
w_externo = SmartWidget("wt_ext", TallerGaugeStrategy("Costo Externo", "external_labour_cost", "yellow"))
w_llantas = SmartWidget("wt_lla", TallerGaugeStrategy("Costo Llantas", "tire_cost", "red"))
w_total = SmartWidget("wt_tot", TallerGaugeStrategy("Total Mant.", "total_maintenance_cost", "green"))
w_disp = SmartWidget("wt_disp", TallerNeedleGaugeStrategy("Disponibilidad", "availability_pct"))
w_ckm = SmartWidget("wt_ckm", TallerGaugeStrategy("Costo por Km", "cost_per_km", "indigo"))

chart_taller_trend = ChartWidget("ct_trend", TallerTrendStrategy()) 
chart_taller_fam = ChartWidget("ct_fam", TallerHorizontalBarStrategy("Costo por Familia", "cost_by_family"))
chart_taller_flota = ChartWidget("ct_flota", TallerHorizontalBarStrategy("Costo por Flota", "cost_by_fleet"))
chart_taller_donut = ChartWidget("ct_donut", TallerDonutStrategy("Costo por Operación", "cost_by_operation"))
chart_taller_unit = ChartWidget("ct_unit", TallerHorizontalBarStrategy("Costo/Km por Unidad", "cost_per_km_unit")) 
chart_taller_marca = ChartWidget("ct_marca", TallerHorizontalBarStrategy("Costo/Km por Marca", "cost_per_km_brand"))
chart_taller_entry = ChartWidget("ct_entry", TallerHorizontalBarStrategy("Entradas por Unidad", "entries_per_unit"))

chart_taller_type = ChartWidget("ct_type", TallerMaintenanceTypeStrategy())

WIDGET_REGISTRY = {
    "wt_int": w_interno, "wt_ext": w_externo, "wt_lla": w_llantas,
    "wt_tot": w_total, "wt_disp": w_disp, "wt_ckm": w_ckm
}

def _render_taller_dashboard_body(ctx):
    return html.Div([
        dmc.SimpleGrid(cols={"base": 2, "md": 3, "lg": 6}, spacing="md", mb="lg", children=[ # type: ignore
            w_interno.render(ctx), w_externo.render(ctx), w_llantas.render(ctx),
            w_total.render(ctx), w_disp.render(ctx), w_ckm.render(ctx)
        ]),

        dmc.Grid(gutter="md", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_taller_trend.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_taller_donut.render(ctx)])
            ])
        ]),

        dmc.Grid(gutter="md", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_taller_fam.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_taller_flota.render(ctx)])
            ])
        ]),

        dmc.Grid(gutter="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_taller_unit.render(ctx)])
            ]),
             dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_taller_marca.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_taller_entry.render(ctx)])
            ])
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ids = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="taller-smart-modal", size="xl", centered=True, children=[html.Div(id="taller-modal-content")]),
        *refresh_components,
        html.Div(id="taller-dashboard-body", children=_render_taller_dashboard_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="taller-dashboard-body", render_body=_render_taller_dashboard_body)

@callback(
    Output("taller-smart-modal", "opened"),
    Output("taller-smart-modal", "title"),
    Output("taller-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)