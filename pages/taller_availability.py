from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from strategies.taller import (
    TallerGaugeStrategy, AvailabilityMonthlyStrategy, 
    AvailabilityKmEntriesStrategy, AvailabilityTableStrategy
)

dash.register_page(__name__, path='/taller-availability', title='Disponibilidad')
data_manager = DataManager()
table_avail_mgr = AvailabilityTableStrategy()

ga_pct_disp = ChartWidget("ga_disp", TallerGaugeStrategy("% Disponibilidad", "pct_disponibilidad", "#fab005", suffix="%", section="disponibilidad"))
ga_entries = ChartWidget("ga_ent", TallerGaugeStrategy("Entradas a Taller", "entradas_taller", "#228be6", prefix="", section="disponibilidad"))

ca_trend = ChartWidget("ca_trend", AvailabilityMonthlyStrategy())
ca_km_entry = ChartWidget("ca_km_entry", AvailabilityKmEntriesStrategy())

WIDGET_REGISTRY = {"ga_disp": ga_pct_disp, "ga_ent": ga_entries, "ca_trend": ca_trend, "ca_km_entry": ca_km_entry}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="avail-smart-modal", size="lg", centered=True, children=[html.Div(id="avail-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[
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

        dmc.Text("INDICADORES DE DISPONIBILIDAD", fw="bold", mb="md", size="sm", c="dimmed"),
        dmc.SimpleGrid(cols={"base": 1, "md": 2}, spacing="lg", mb="xl", children=[
            ga_pct_disp.render(ctx), ga_entries.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 6}, children=[ca_trend.render(ctx)]),
            dmc.GridCol(span={"base": 12, "md": 6}, children=[ca_km_entry.render(ctx)]),
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Text("DETALLE DE DISPONIBILIDAD POR ÁREA / UNIDAD", fw="bold", mb="md", size="xs"),
            dmc.ScrollArea(h=450, children=[table_avail_mgr.render(ctx)])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("avail-smart-modal", "opened"), Output("avail-smart-modal", "title"), Output("avail-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update