from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    TallerNeedleGaugeStrategy, AvailabilityMonthlyStrategy,
    AvailabilityKmEntriesStrategy, AvailabilityTableStrategy,
    TallerRichKPIStrategy
)

dash.register_page(__name__, path="/taller-availability", title="Disponibilidad")

SCREEN_ID = "taller-availability"

table_avail_mgr = AvailabilityTableStrategy()

ga_pct_disp = SmartWidget("ga_disp", TallerNeedleGaugeStrategy("% Disponibilidad", "availability_pct"))

ga_entries = SmartWidget("ga_ent", TallerRichKPIStrategy("workshop_entries_count", "Entradas a Taller", "tabler:truck-entry", "indigo"))

ca_trend = ChartWidget("ca_trend", AvailabilityMonthlyStrategy())
ca_km_entry = ChartWidget("ca_km_entry", AvailabilityKmEntriesStrategy())

WIDGET_REGISTRY = {
    "ga_disp": ga_pct_disp,
    "ga_ent": ga_entries,
}

def _render_taller_availability_body(ctx):
    return html.Div([
        dmc.Paper(p="md", withBorder=True, mb="md", children=[
            dmc.Grid(gutter="md", align="center", children=[
                dmc.GridCol(span={"base": 12, "md": 4}, children=[ga_pct_disp.render(ctx)]), # type: ignore
                dmc.GridCol(span={"base": 12, "md": 4}, children=[ga_entries.render(ctx)]), # type: ignore
                dmc.GridCol(span={"base": 12, "md": 4}, children=[ # type: ignore
                    dmc.Alert("La disponibilidad se calcula en base a la flota activa vs unidades en taller.", title="Nota", color="blue")
                ])
            ])
        ]),

        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                 dmc.Paper(p="md", withBorder=True, radius="md", children=[ca_trend.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                 dmc.Paper(p="md", withBorder=True, radius="md", children=[ca_km_entry.render(ctx)])
            ]),
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Text("Detalle de Disponibilidad por Unidad", fw="bold", size="lg", mb="md"),
            table_avail_mgr.render(ctx)
        ]),

        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="avail-smart-modal", size="lg", centered=True, children=[html.Div(id="avail-modal-content")]),

        *refresh_components,

        html.Div(id="taller-availability-body", children=_render_taller_availability_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-availability-body",
    render_body=_render_taller_availability_body,
)

@callback(
    Output("avail-smart-modal", "opened"),
    Output("avail-smart-modal", "title"),
    Output("avail-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update
    if dash.ctx.triggered_id is None:
        return no_update, no_update, no_update
    
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_title(ctx) if hasattr(widget.strategy, "get_title") else "Detalle"
    return True, cfg, widget.strategy.render_detail(ctx)