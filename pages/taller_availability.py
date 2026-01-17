from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager  # singleton
from components.visual_widget import ChartWidget
from strategies.taller import (
    TallerGaugeStrategy, AvailabilityMonthlyStrategy,
    AvailabilityKmEntriesStrategy, AvailabilityTableStrategy
)

dash.register_page(__name__, path="/taller-availability", title="Disponibilidad")

SCREEN_ID = "taller-availability"

table_avail_mgr = AvailabilityTableStrategy()

ga_pct_disp = ChartWidget("ga_disp", TallerGaugeStrategy("% Disponibilidad", "pct_disponibilidad", "yellow", suffix="%", section="disponibilidad"))
ga_entries = ChartWidget("ga_ent", TallerGaugeStrategy("Entradas a Taller", "entradas_taller", "indigo", prefix="", section="disponibilidad"))

ca_trend = ChartWidget("ca_trend", AvailabilityMonthlyStrategy())
ca_km_entry = ChartWidget("ca_km_entry", AvailabilityKmEntriesStrategy())

WIDGET_REGISTRY = {
    "ga_disp": ga_pct_disp,
    "ga_ent": ga_entries,
    "ca_trend": ca_trend,
    "ca_km_entry": ca_km_entry,
}


def _render_taller_availability_body(ctx):
    return html.Div([
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[  # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["07-Jul"], value="07-Jul", size="xs"),
                dmc.Select(label="Empresa/Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Operación", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Clasificación", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Razón Reparación", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Motor", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.Text("INDICADORES DE DISPONIBILIDAD", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "md": 2}, spacing="lg", mb="xl", children=[  # type: ignore
            ga_pct_disp.render(ctx), ga_entries.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 6}, children=[ca_trend.render(ctx)]),     # type: ignore
            dmc.GridCol(span={"base": 12, "md": 6}, children=[ca_km_entry.render(ctx)]),  # type: ignore
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Text("DETALLE DE DISPONIBILIDAD POR ÁREA / UNIDAD", fw="bold", mb="md", size="xs"),
            dmc.ScrollArea(h=450, children=[table_avail_mgr.render(ctx)])
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
    if not widget:
        return no_update, no_update, no_update

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
