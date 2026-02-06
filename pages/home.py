from flask import session
import dash_mantine_components as dmc
from dash import html
import dash
from dash import callback, Input, Output, ALL, no_update
from dash_iconify import DashIconify
from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.skeleton import get_skeleton
from strategies.executive import ExecutiveKPIStrategy, ExecutiveMiniKPIStrategy, ExecutiveDonutStrategy
from strategies.charts import MainTrendChartStrategy
from utils.helpers import safe_get

dash.register_page(__name__, path="/", title="Dashboard Principal")
SCREEN_ID = "home"

top_layout = {"height": 180, "span": 2}
mini_layout = {"height": 120, "span": 2}
compact_layout = {"height": 95, "span": 2} 

w_income = SmartWidget("h_inc", ExecutiveKPIStrategy(SCREEN_ID, "trip_revenue", "Ingresos", "tabler:coin", "blue", layout_config=top_layout))
w_costs = SmartWidget("h_cost", ExecutiveKPIStrategy(SCREEN_ID, "trip_costs", "Costos", "tabler:wallet", "red", layout_config=top_layout, inverse=True))
w_margin = SmartWidget("h_marg", ExecutiveKPIStrategy(SCREEN_ID, "profit_margin", "% Margen", "tabler:chart-pie", "green", is_pct=True, layout_config=top_layout))
w_bank = SmartWidget("h_bank", ExecutiveKPIStrategy(SCREEN_ID, "bank_balance", "Bancos M.N.", "tabler:building-bank", "indigo", layout_config=top_layout))
w_yield = SmartWidget("h_yld", ExecutiveKPIStrategy(SCREEN_ID, "fuel_yield", "Rendimiento", "tabler:gas-station", "orange", layout_config=compact_layout))
w_km = SmartWidget("h_km", ExecutiveKPIStrategy(SCREEN_ID, "total_km", "Kilómetros", "tabler:road", "blue", layout_config=compact_layout))
w_liters = SmartWidget("h_lit", ExecutiveKPIStrategy(SCREEN_ID, "total_liters", "Litros Total", "tabler:droplet", "cyan", layout_config=compact_layout))

w_cvkm = SmartWidget("h_cvkm", ExecutiveKPIStrategy(SCREEN_ID, "revenue_per_km", "Ingreso x Km", "tabler:ruler-2", "teal", layout_config=compact_layout))
w_cmkm = SmartWidget("h_cmkm", ExecutiveKPIStrategy(SCREEN_ID, "maintenance_cost_per_km", "Mtto x Km", "tabler:tool", "red", layout_config=compact_layout, inverse=True))

w_viajes = SmartWidget("h_via", ExecutiveKPIStrategy(SCREEN_ID, "trips", "Viajes", "tabler:steering-wheel", "blue", layout_config=compact_layout))
w_units = SmartWidget("h_uni", ExecutiveKPIStrategy(SCREEN_ID, "units_used", "Unidades", "tabler:bus", "cyan", layout_config=compact_layout))
w_clients = SmartWidget("h_cli", ExecutiveKPIStrategy(SCREEN_ID, "customers_served", "Clientes", "tabler:users", "indigo", layout_config=compact_layout))

w_total_mtto = SmartWidget("h_mt", ExecutiveKPIStrategy(SCREEN_ID, "total_maintenance", "Total Mtto", "tabler:tool", "red", layout_config=top_layout, inverse=True))

w_mi = SmartWidget("h_mi", ExecutiveMiniKPIStrategy(SCREEN_ID, "mtto_interno", "Interno", "teal", "tabler:building", layout_config=top_layout))
w_me = SmartWidget("h_me", ExecutiveMiniKPIStrategy(SCREEN_ID, "mtto_externo", "Externo", "lime", "tabler:building-store", layout_config=top_layout))
w_ml = SmartWidget("h_ml", ExecutiveMiniKPIStrategy(SCREEN_ID, "mtto_llantas", "Llantas", "gray", "tabler:circle", layout_config=top_layout))

w_main_chart = ChartWidget("h_chart", MainTrendChartStrategy(SCREEN_ID, "main_indicators", "Tendencia", layout_config={"height": 400}))
w_port = ChartWidget("h_port", ExecutiveDonutStrategy(SCREEN_ID, "client_portfolio", "Cartera", layout_config={"height": 280}))
w_supp = ChartWidget("h_supp", ExecutiveDonutStrategy(SCREEN_ID, "supplier_balance", "Proveedores", layout_config={"height": 280}))

def _render_home_body(ctx):
    val_disp = safe_get(ctx, "main.dashboard.kpis.units_availability.value", 0)
    if val_disp <= 1:
        val_disp *= 100
    val_disp = int(val_disp)

    truck_visual = dmc.Paper(
        p="md",
        withBorder=True,
        shadow="sm",
        radius="md",
        h=280,
        children=[
            dmc.Stack(
                justify="center",
                align="center",
                h="100%",
                gap="sm",
                children=[
                    dmc.Text("Disponibilidad Flota", size="xs", c="gray", fw="bold", tt="uppercase", ta="center"),
                    dmc.Center(h=100, children=DashIconify(icon="tabler:truck-loading", width=70, color="green")),
                    dmc.Progress(value=val_disp, color="green", h=25, radius="xl", style={"width": "100%"}),
                    dmc.Text(f"{val_disp}% Disponible", size="xl", fw="bold", ta="center", mt=5)
                ]
            )
        ]
    )

    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 2, "sm": 2, "lg": 4}, # type: ignore
            spacing="md",
            mb="lg",
            children=[w_income.render(ctx), w_costs.render(ctx), w_margin.render(ctx), w_bank.render(ctx)]
        ),
        dmc.Grid(
            gutter="md",
            mb="lg",
            align="stretch",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 8}, # type: ignore
                    children=[w_main_chart.render(ctx)]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 4}, # type: ignore
                    children=[
                        dmc.SimpleGrid(
                            cols=2,
                            spacing="sm",
                            verticalSpacing="sm",
                            children=[
                                w_yield.render(ctx), w_km.render(ctx),
                                w_liters.render(ctx), w_cvkm.render(ctx),
                                w_cmkm.render(ctx), w_viajes.render(ctx),
                                w_units.render(ctx), w_clients.render(ctx)
                            ]
                        )
                    ]
                )
            ]
        ),
        dmc.Divider(label="Desglose de Mantenimiento", mb="md", labelPosition="center"),
        dmc.SimpleGrid(
            cols={"base": 2, "sm": 2, "lg": 4}, # type: ignore
            spacing="md",
            mb="lg",
            children=[w_total_mtto.render(ctx), w_mi.render(ctx), w_me.render(ctx), w_ml.render(ctx)]
        ),
        dmc.Divider(label="Análisis de Cartera y Flota", mb="md", labelPosition="center"),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 3}, # type: ignore
            spacing="md",
            children=[truck_visual, w_port.render(ctx), w_supp.render(ctx)]
        ),
        dmc.Space(h=30)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado")
    comps, _ = data_manager.dash_refresh_components(SCREEN_ID)
    return dmc.Container(
        fluid=True,
        children=[
            dmc.Modal(id="home-smart-modal", size="xl", centered=True, children=[html.Div(id="home-modal-content")]),
            *comps,
            html.Div(id="hb", children=get_skeleton(SCREEN_ID))
        ]
    )

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="hb",
    render_body=_render_home_body
)

@callback(
    Output("home-smart-modal", "opened"),
    Output("home-smart-modal", "title"),
    Output("home-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update
    if dash.ctx.triggered_id is None:
        return no_update, no_update, no_update

    wid = dash.ctx.triggered_id["index"]
    target_w = {
        "h_inc": w_income, "h_cost": w_costs, "h_marg": w_margin, "h_bank": w_bank,
        "h_yld": w_yield, "h_km": w_km, "h_lit": w_liters,
        "h_cvkm": w_cvkm, "h_cmkm": w_cmkm,
        "h_via": w_viajes, "h_uni": w_units, "h_cli": w_clients,
        "h_mi": w_mi, "h_me": w_me, "h_ml": w_ml, "h_mt": w_total_mtto,
        "h_port": w_port, "h_supp": w_supp
    }.get(wid)

    if not target_w:
        return no_update, no_update, no_update

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True)
    cfg = target_w.strategy.get_card_config(ctx)
    return True, cfg.get("title"), target_w.strategy.render_detail(ctx)