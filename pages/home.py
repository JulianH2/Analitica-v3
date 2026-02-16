from flask import session
import dash_mantine_components as dmc
from dash import html, dcc
import dash
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from strategies.executive import ExecutiveKPIStrategy, ExecutiveMiniKPIStrategy, ExecutiveDonutStrategy
from strategies.charts import MainTrendChartStrategy
from utils.helpers import safe_get

dash.register_page(__name__, path="/", title="Dashboard Principal")

SCREEN_ID = "home"
PREFIX = "h"

top_layout = {"height": 220}
mini_layout = {"height": 150}
chart_donut_layout = {"height": 300}

w_income = SmartWidget("h_inc", ExecutiveKPIStrategy(SCREEN_ID, "trip_revenue", "Ingresos", "tabler:coin", "blue", has_detail=True, layout_config=top_layout))
w_costs = SmartWidget("h_cost", ExecutiveKPIStrategy(SCREEN_ID, "trip_costs", "Costos", "tabler:wallet", "red", has_detail=True, layout_config=top_layout, inverse=True))
w_margin = SmartWidget("h_marg", ExecutiveKPIStrategy(SCREEN_ID, "profit_margin", "% Margen", "tabler:chart-pie", "green", is_pct=True, has_detail=True, layout_config=top_layout))
w_bank = SmartWidget("h_bank", ExecutiveKPIStrategy(SCREEN_ID, "bank_balance", "Bancos M.N.", "tabler:building-bank", "indigo", has_detail=True, layout_config=top_layout))

w_yield = SmartWidget("h_yld", ExecutiveKPIStrategy(SCREEN_ID, "fuel_yield", "Rendimiento", "tabler:gas-station", "orange", has_detail=True, layout_config=mini_layout))
w_km = SmartWidget("h_km", ExecutiveKPIStrategy(SCREEN_ID, "total_km", "Kilómetros", "tabler:road", "blue", has_detail=True, layout_config=mini_layout))
w_liters = SmartWidget("h_lit", ExecutiveKPIStrategy(SCREEN_ID, "total_liters", "Litros Total", "tabler:droplet", "cyan", has_detail=True, layout_config=mini_layout))
w_cvkm = SmartWidget("h_cvkm", ExecutiveKPIStrategy(SCREEN_ID, "revenue_per_km", "Ingreso x Km", "tabler:ruler-2", "teal", has_detail=True, layout_config=mini_layout))
w_cmkm = SmartWidget("h_cmkm", ExecutiveKPIStrategy(SCREEN_ID, "maintenance_cost_per_km", "Mtto x Km", "tabler:tool", "red", has_detail=True, layout_config=mini_layout, inverse=True))
w_viajes = SmartWidget("h_via", ExecutiveKPIStrategy(SCREEN_ID, "trips", "Viajes", "tabler:steering-wheel", "blue", has_detail=True, layout_config=mini_layout))
w_units = SmartWidget("h_uni", ExecutiveKPIStrategy(SCREEN_ID, "units_used", "Unidades", "tabler:bus", "cyan", has_detail=True, layout_config=mini_layout))
w_clients = SmartWidget("h_cli", ExecutiveKPIStrategy(SCREEN_ID, "customers_served", "Clientes", "tabler:users", "indigo", has_detail=True, layout_config=mini_layout))

w_total_mtto = SmartWidget("h_mt", ExecutiveKPIStrategy(SCREEN_ID, "total_maintenance", "Total Mtto", "tabler:tool", "red", has_detail=True, layout_config={"height": 200}))
w_mi = SmartWidget("h_mi", ExecutiveMiniKPIStrategy(SCREEN_ID, "mtto_interno", "Interno", "teal", "tabler:building", has_detail=True, layout_config={"height": 200}))
w_me = SmartWidget("h_me", ExecutiveMiniKPIStrategy(SCREEN_ID, "mtto_externo", "Externo", "lime", "tabler:building-store", has_detail=True, layout_config={"height": 200}))
w_ml = SmartWidget("h_ml", ExecutiveMiniKPIStrategy(SCREEN_ID, "mtto_llantas", "Llantas", "gray", "tabler:circle", has_detail=True, layout_config={"height": 200}))

w_main_chart = ChartWidget("h_chart", MainTrendChartStrategy(SCREEN_ID, "main_indicators", "Tendencia Principal", has_detail=True, layout_config={"height": "100%"}))
w_port = ChartWidget("h_port", ExecutiveDonutStrategy(SCREEN_ID, "client_portfolio", "Cartera de Clientes", has_detail=True, layout_config=chart_donut_layout))
w_supp = ChartWidget("h_supp", ExecutiveDonutStrategy(SCREEN_ID, "supplier_balance", "Balance Proveedores", has_detail=True, layout_config=chart_donut_layout))

def _render_home_body(ctx):
    theme = session.get("theme", "dark")

    val_disp = safe_get(ctx, "main.dashboard.kpis.units_availability.value", 0)
    if val_disp <= 1:
        val_disp *= 100
    val_disp = int(val_disp)

    truck_visual = dmc.Paper(
        p="lg",
        withBorder=True,
        shadow="sm",
        radius="md",
        h=300,
        style={"backgroundColor": "transparent"},
        children=[dmc.Stack(justify="center", align="center", h="100%", gap="md", children=[
            dmc.ThemeIcon(DashIconify(icon="tabler:truck-loading", width=48), size=80, radius="xl", variant="light", color="green"),
            dmc.Text("Disponibilidad de Flota", size="sm", c="dimmed", fw=600, tt="uppercase", ta="center"), # type: ignore
            dmc.Progress(value=val_disp, color="green", h=28, radius="xl", style={"width": "90%"}, striped=True, animated=True),
            dmc.Text(f"{val_disp}% Operativa", size="xl", fw=700, c="green", ta="center") # type: ignore
        ])]
    )

    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))", "gap": "1rem", "marginBottom": "2rem"}, children=[
            w_income.render(ctx, theme=theme),
            w_costs.render(ctx, theme=theme),
            w_margin.render(ctx, theme=theme),
            w_bank.render(ctx, theme=theme)
        ]),
        dmc.Grid(gutter="md", mb="xl", align="stretch", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[w_main_chart.render(ctx, theme=theme)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(2, 1fr)", "gridTemplateRows": "repeat(4, 1fr)", "gap": "0.5rem", "height": "100%"}, children=[ # type: ignore
                w_yield.render(ctx, theme=theme),
                w_km.render(ctx, theme=theme),
                w_liters.render(ctx, theme=theme),
                w_cvkm.render(ctx, theme=theme),
                w_cmkm.render(ctx, theme=theme),
                w_viajes.render(ctx, theme=theme),
                w_units.render(ctx, theme=theme),
                w_clients.render(ctx, theme=theme)
            ])])
        ]),
        dmc.Divider(label="Desglose de Mantenimiento", labelPosition="center", mb="lg", size="sm", variant="dashed"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))", "gap": "1rem", "marginBottom": "2rem"}, children=[
            w_total_mtto.render(ctx, theme=theme),
            w_mi.render(ctx, theme=theme),
            w_me.render(ctx, theme=theme),
            w_ml.render(ctx, theme=theme)
        ]),
        dmc.Divider(label="Análisis de Cartera y Flota", labelPosition="center", mb="lg", size="sm", variant="dashed"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "1rem", "marginBottom": "2rem"}, children=[
            truck_visual,
            w_port.render(ctx, theme=theme),
            w_supp.render(ctx, theme=theme)
        ]),
        dmc.Space(h=60)
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_inc": w_income, f"{PREFIX}_cost": w_costs, f"{PREFIX}_marg": w_margin, f"{PREFIX}_bank": w_bank,
    f"{PREFIX}_yld": w_yield, f"{PREFIX}_km": w_km, f"{PREFIX}_lit": w_liters, f"{PREFIX}_cvkm": w_cvkm,
    f"{PREFIX}_cmkm": w_cmkm, f"{PREFIX}_via": w_viajes, f"{PREFIX}_uni": w_units, f"{PREFIX}_cli": w_clients,
    f"{PREFIX}_mi": w_mi, f"{PREFIX}_me": w_me, f"{PREFIX}_ml": w_ml, f"{PREFIX}_mt": w_total_mtto,
    f"{PREFIX}_chart": w_main_chart, f"{PREFIX}_port": w_port, f"{PREFIX}_supp": w_supp,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado")

    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="home-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("home-drawer"),
            html.Div(id="hb", children=get_skeleton(SCREEN_ID)),
        ],
    )

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="hb", render_body=_render_home_body)

register_drawer_callback(drawer_id="home-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID)