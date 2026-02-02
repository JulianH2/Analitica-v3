from flask import session
import dash
from dash import html, dcc, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.workshop import (
    TallerGaugeStrategy, TallerNeedleGaugeStrategy, TallerTrendStrategy,
    TallerHorizontalBarStrategy, TallerDonutStrategy, TallerMaintenanceTypeStrategy
)

dash.register_page(__name__, path="/taller-dashboard", title="Mantenimiento")

SCREEN_ID = "taller-dashboard"

w_interno = SmartWidget("wt_int", TallerGaugeStrategy("Costo Interno", "costo_interno", "indigo"))
w_externo = SmartWidget("wt_ext", TallerGaugeStrategy("Costo Externo", "costo_externo", "yellow"))
w_llantas = SmartWidget("wt_lla", TallerGaugeStrategy("Costo Llantas", "costo_llantas", "red"))
w_total = SmartWidget("wt_tot", TallerGaugeStrategy("Total Mant.", "total_mantenimiento", "green"))
w_disp = SmartWidget("wt_disp", TallerNeedleGaugeStrategy("% Disponibilidad", "disponibilidad"))
w_ckm = SmartWidget("wt_ckm", TallerGaugeStrategy("Costo por Km", "costo_km", "indigo"))

chart_taller_trend = ChartWidget("ct_trend", TallerTrendStrategy())
chart_taller_type = ChartWidget("ct_type", TallerMaintenanceTypeStrategy())
chart_taller_fam = ChartWidget("ct_fam", TallerHorizontalBarStrategy("Costo por Familia", "por_familia"))
chart_taller_flota = ChartWidget("ct_flota", TallerHorizontalBarStrategy("Costo por Flota", "por_flota"))
chart_taller_donut = ChartWidget("ct_donut", TallerDonutStrategy("Costo por Tipo Operación", "por_operacion"))
chart_taller_unit = ChartWidget("ct_unit", TallerHorizontalBarStrategy("Costo x Km por Unidad", "costo_km_unidad", "red"))
chart_taller_marca = ChartWidget("ct_marca", TallerHorizontalBarStrategy("Costo x Km por Marca", "costo_km_marca", "yellow"))
chart_taller_entry = ChartWidget("ct_entry", TallerHorizontalBarStrategy("Entradas a Taller por Unidad", "entradas_unidad", "indigo"))

WIDGET_REGISTRY = {
    "wt_int": w_interno, "wt_ext": w_externo, "wt_lla": w_llantas,
    "wt_tot": w_total, "wt_disp": w_disp, "wt_ckm": w_ckm,
    "ct_trend": chart_taller_trend, "ct_type": chart_taller_type, "ct_fam": chart_taller_fam,
    "ct_flota": chart_taller_flota, "ct_donut": chart_taller_donut, "ct_unit": chart_taller_unit,
    "ct_marca": chart_taller_marca, "ct_entry": chart_taller_entry
}

def _render_taller_dashboard_body(ctx):
    return html.Div([
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[ # type: ignore
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

        dmc.SimpleGrid(cols={"base": 1, "lg": 2}, spacing="md", mb="md", children=[ # type: ignore
            w_interno.render(ctx, mode="combined"),
            w_externo.render(ctx, mode="combined"),
            w_llantas.render(ctx, mode="combined"),
            w_total.render(ctx, mode="combined"),
        ]),

        dmc.SimpleGrid(cols={"base": 1, "lg": 2}, spacing="md", mb="xl", children=[ # type: ignore
            w_disp.render(ctx, mode="combined"),
            w_ckm.render(ctx, mode="combined"),
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 7}, children=[chart_taller_trend.render(ctx, h=450)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[chart_taller_type.render(ctx, h=450)]), # type: ignore
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="lg", children=[ # type: ignore
            chart_taller_fam.render(ctx, h=450),
            chart_taller_flota.render(ctx, h=450),
            chart_taller_donut.render(ctx, h=450),
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", children=[ # type: ignore
            chart_taller_unit.render(ctx, h=450),
            chart_taller_marca.render(ctx, h=450),
            chart_taller_entry.render(ctx, h=450),
        ]),

        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="taller-smart-modal", size="xl", centered=True, children=[html.Div(id="taller-modal-content")]),

        *refresh_components,

        html.Div(id="taller-dashboard-body", children=_render_taller_dashboard_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-dashboard-body",
    render_body=_render_taller_dashboard_body,
)

@callback(
    Output("taller-smart-modal", "opened"),
    Output("taller-smart-modal", "title"),
    Output("taller-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_modal_click(n_clicks):
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