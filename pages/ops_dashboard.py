from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.operational import (
    OpsGaugeStrategy, OpsComparisonStrategy, OpsPieStrategy,
    BalanceUnitStrategy, OpsTableStrategy
)
from strategies.admin import AdminRichKPIStrategy
from settings.theme import DesignSystem
from utils.helpers import safe_get

dash.register_page(__name__, path='/ops-dashboard', title='Control Operativo')
data_manager = DataManager()
table_ops_mgr = OpsTableStrategy()

MAIN_KPI_H = 205
VISUAL_H = 360
top_layout = {"height": MAIN_KPI_H, "span": 2}

w_inc = SmartWidget("go_inc", OpsGaugeStrategy("Ingreso Viaje", "ingreso_viaje", "indigo", layout_config=top_layout))
w_tri = SmartWidget("go_tri", OpsGaugeStrategy("Viajes", "viajes", "green", prefix="", layout_config=top_layout))
w_kms = SmartWidget("go_kms", OpsGaugeStrategy("Kilómetros", "kilometros", "yellow", prefix="", layout_config=top_layout))

w_avg_trip = SmartWidget("ko_avg_trip", AdminRichKPIStrategy("operaciones", "ingreso_viaje", "Prom. x Viaje", "tabler:truck-delivery", "indigo", sub_section="promedios", layout_config=top_layout))
w_avg_unit = SmartWidget("ko_avg_unit", AdminRichKPIStrategy("operaciones", "ingreso_unit", "Prom. x Unidad", "tabler:engine", "green", sub_section="promedios", layout_config=top_layout))
w_units_qty = SmartWidget("ko_units", AdminRichKPIStrategy("operaciones", "unidades_utilizadas", "Unidades Uso", "tabler:truck", "cyan", sub_section="promedios", layout_config=top_layout))

w_gauge_inc = ChartWidget("v_go_inc", OpsGaugeStrategy("Visual Ingreso", "ingreso_viaje", "indigo", layout_config={"height": 200}))
w_gauge_tri = ChartWidget("v_go_tri", OpsGaugeStrategy("Visual Viajes", "viajes", "green", prefix="", layout_config={"height": 200}))
w_gauge_kms = ChartWidget("v_go_kms", OpsGaugeStrategy("Visual Kms", "kilometros", "yellow", prefix="", layout_config={"height": 200}))

w_inc_comp = ChartWidget("co_inc_comp", OpsComparisonStrategy("Ingresos 2025 vs 2024", "ingresos_anual", "indigo", layout_config={"height": VISUAL_H}))
w_trips_comp = ChartWidget("co_trips_comp", OpsComparisonStrategy("Viajes 2025 vs 2024", "viajes_anual", "green", layout_config={"height": VISUAL_H}))
w_mix = ChartWidget("co_mix", OpsPieStrategy(layout_config={"height": 380}))
w_unit_bal = ChartWidget("co_unit_bal", BalanceUnitStrategy(layout_config={"height": 380}))

WIDGET_REGISTRY = {
    "go_inc": w_inc, "go_tri": w_tri, "go_kms": w_kms,
    "ko_avg_trip": w_avg_trip, "ko_avg_unit": w_avg_unit, "ko_units": w_units_qty
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    ctx = data_manager.get_data("operaciones")

    def fleet_status():
        val = safe_get(ctx, "operaciones.dashboard.utilizacion.valor", 92)
        return dmc.Paper(p="md", withBorder=True, radius="md", h=420, children=[
            dmc.Stack(justify="center", align="center", h="100%", children=[
                dmc.Text("Estado de Carga de Flota", fw="bold", size="xs", c="dimmed", tt="uppercase"), # type: ignore
                DashIconify(icon="tabler:truck-loading", width=60, color=DesignSystem.SUCCESS[5]),
                dmc.Text(f"{val}% Cargado", fw="bold", size="xl", c="green"),
                dmc.Progress(value=val, color="green", h=22, radius="xl", style={"width": "100%"}),
            ])
        ])

    return dmc.Container(fluid=True, px="xs", children=[
        dmc.Modal(id="ops-smart-modal", size="xl", centered=True, children=[html.Div(id="ops-modal-content")]),

        dmc.SimpleGrid(cols={"base": 2, "sm": 3, "lg": 6}, spacing="xs", mb="md", mt="xs", children=[ # type: ignore
            w_inc.render(ctx), w_tri.render(ctx), w_kms.render(ctx),
            w_avg_trip.render(ctx), w_avg_unit.render(ctx), w_units_qty.render(ctx)
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="xs", mb="md", children=[ # type: ignore
            w_gauge_inc.render(ctx), w_gauge_tri.render(ctx), w_gauge_kms.render(ctx)
        ]),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "md": 6}, children=[w_inc_comp.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 6}, children=[w_trips_comp.render(ctx)]), # type: ignore
        ]),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[fleet_status()]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", h=420, children=[
                    dmc.Tabs(value="rutas", children=[
                        dmc.TabsList([
                            dmc.TabsTab("Rutas Principales", value="rutas", leftSection=DashIconify(icon="tabler:route")),
                            dmc.TabsTab("Zonas de Vacío", value="vacio", leftSection=DashIconify(icon="tabler:map-pin-off"))
                        ]),
                        dmc.TabsPanel(dmc.ScrollArea(h=350, pt="xs", children=[table_ops_mgr.render_rutas(ctx)]), value="rutas"),
                        dmc.TabsPanel(dmc.Center(h=350, children=dmc.Text("Sin datos", c="dimmed")), value="vacio") # type: ignore
                    ])
                ])
            ])
        ]),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[w_mix.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 7}, children=[w_unit_bal.render(ctx)]), # type: ignore
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Tabs(value="cliente", children=[
                dmc.TabsList([
                    dmc.TabsTab("Ingreso Cliente", value="cliente"),
                    dmc.TabsTab("Ingreso Operador", value="operador"),
                    dmc.TabsTab("Ingreso Unidad", value="unidad")
                ]),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[table_ops_mgr.render_tabbed_table(ctx, "cliente")]), value="cliente"),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[table_ops_mgr.render_tabbed_table(ctx, "operador")]), value="operador"),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[table_ops_mgr.render_tabbed_table(ctx, "unidad")]), value="unidad"),
            ])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("ops-smart-modal", "opened"),
    Output("ops-smart-modal", "title"),
    Output("ops-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_ops_dashboard_modal(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update
    
    if dash.ctx.triggered_id is None:
        return no_update, no_update, no_update
    
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    
    if widget:
        ctx = data_manager.get_data("operaciones")
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    
    return no_update, no_update, no_update