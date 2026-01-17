from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager  # singleton
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from strategies.executive import ExecutiveKPIStrategy, ExecutiveMiniKPIStrategy, ExecutiveDonutStrategy
from strategies.charts import MainTrendChartStrategy
from strategies.operational import FleetEfficiencyStrategy
from utils.helpers import safe_get

dash.register_page(__name__, path="/", title="Dashboard Principal")

SCREEN_ID = "home"

MAIN_KPI_H = 205
top_layout = {"height": MAIN_KPI_H, "span": 2}

w_income = SmartWidget("h_inc", ExecutiveKPIStrategy("operaciones", "dashboard", "ingreso_viaje", "Ingresos", "tabler:coin", "blue", layout_config=top_layout))
w_costs = SmartWidget("h_cost", ExecutiveKPIStrategy("operaciones", "costos", "costo_total", "Costos", "tabler:wallet", "red", layout_config=top_layout))
w_margin = SmartWidget("h_marg", ExecutiveKPIStrategy("operaciones", "costos", "utilidad_viaje", "% Margen", "tabler:chart-pie", "green", is_pct=True, layout_config=top_layout))

w_viajes = SmartWidget("h_via", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "viajes", "Viajes", "blue", "tabler:steering-wheel", layout_config=top_layout))
w_units = SmartWidget("h_uni", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "unidades_utilizadas", "Unidades", "cyan", "tabler:bus", layout_config=top_layout))
w_clients = SmartWidget("h_cli", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "clientes_servidos", "Clientes", "indigo", "tabler:users", layout_config=top_layout))

w_cost_viaje_km = SmartWidget("h_cvkm", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "ingreso_viaje", "Ingreso x Km", "orange", "tabler:ruler-2", layout_config={"height": 140}))
w_cost_mtto_km = SmartWidget("h_cmkm", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_km", "Mtto x Km", "red", "tabler:tool", layout_config={"height": 140}))

w_main_chart = ChartWidget("h_chart", MainTrendChartStrategy(layout_config={"height": 380}))
w_yield = SmartWidget("h_yield", FleetEfficiencyStrategy(layout_config={"height": 220}))
w_portfolio = ChartWidget("h_port", ExecutiveDonutStrategy(
    "Cartera Clientes M.N.",
    "administracion",
    "facturacion_cobranza",
    {"SIN CARTA COBRO": "blue", "POR VENCER": "yellow", "VENCIDO": "red"},
    layout_config={"height": 220}
))
w_suppliers = ChartWidget("h_supp", ExecutiveDonutStrategy(
    "Saldo Proveedores M.N.",
    "administracion",
    "cuentas_por_pagar",
    {"POR VENCER": "blue", "VENCIDO": "red"},
    layout_config={"height": 220}
))

WIDGET_REGISTRY = {
    "h_inc": w_income, "h_cost": w_costs, "h_marg": w_margin, "h_yield": w_yield,
    "h_via": w_viajes, "h_uni": w_units, "h_cli": w_clients, "h_cvkm": w_cost_viaje_km,
    "h_cmkm": w_cost_mtto_km
}


def _render_home_body(ctx):
    def truck_visual():
        val = safe_get(ctx, "operaciones.dashboard.utilizacion.valor", 0)
        return dmc.Paper(p="md", withBorder=True, shadow="xs", radius="md", h=220, children=[
            dmc.Stack(justify="center", align="center", h="100%", gap="sm", children=[
                dmc.Text("Estado Carga Flota", size="xs", c="gray", fw="bold", tt="uppercase", ta="center"),  # type: ignore
                dmc.Center(h=70, children=DashIconify(icon="tabler:truck-loading", width=55, color="green")),
                dmc.Progress(value=val, color="green", h=22, radius="xl", style={"width": "100%"}),
                dmc.Text(f"{val}% Cargado", size="sm", fw="bold", ta="center", mt=5)  # type: ignore
            ])
        ])

    return html.Div([
        dmc.Group(justify="space-between", mb="sm", mt="xs", children=[
            dmc.Group(gap="xs", children=[
                DashIconify(icon="tabler:hexagon-letter-a", width=25, color="indigo"),
                dmc.Title("Resultado Financiero Mensual", order=4),
            ]),
            dmc.Badge("Enero 2026", size="md", variant="light", color="blue")
        ]),

        dmc.SimpleGrid(cols={"base": 2, "sm": 3, "lg": 6}, spacing="xs", mb="md", children=[  # type: ignore
            w_income.render(ctx), w_costs.render(ctx), w_margin.render(ctx),
            w_viajes.render(ctx), w_units.render(ctx), w_clients.render(ctx)
        ]),

        dmc.Grid(gutter="xs", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[w_main_chart.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[  # type: ignore
                dmc.Stack(justify="center", h="100%", gap="xs", children=[
                    dmc.Text("Eficiencia Operativa", size="xs", fw=700, c="dimmed", tt="uppercase", ta="center"),  # type: ignore
                    w_cost_viaje_km.render(ctx),
                    w_cost_mtto_km.render(ctx)
                ])
            ])
        ]),

        dmc.Divider(label="Mantenimiento", labelPosition="left", mb="xs"),
        dmc.SimpleGrid(cols={"base": 2, "md": 4}, spacing="xs", mb="md", children=[  # type: ignore
            SmartWidget("h_mt", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "total_mantenimiento", "Total", "green", "tabler:tool", layout_config={"height": 130})).render(ctx),
            SmartWidget("h_mi", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_interno", "Interno", "teal", "tabler:building", layout_config={"height": 130})).render(ctx),
            SmartWidget("h_me", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_externo", "Externo", "lime", "tabler:building-store", layout_config={"height": 130})).render(ctx),
            SmartWidget("h_ml", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_llantas", "Llantas", "gray", "tabler:circle", layout_config={"height": 130})).render(ctx),
        ]),

        dmc.Divider(label="Análisis de Cartera y Activos", labelPosition="left", mb="xs"),
        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="xs", children=[  # type: ignore
            w_yield.render(ctx),
            truck_visual(),
            w_portfolio.render(ctx),
            w_suppliers.render(ctx)
        ]),

        dmc.Space(h=50)
    ])


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")  # type: ignore

    # primer paint rápido (base/cache slice)
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    # home suele querer refresco (aunque sea 1 vez). puedes subir max_intervals si quieres polling leve.
    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, px="xs", children=[
        dmc.Modal(id="home-smart-modal", size="xl", centered=True, children=[html.Div(id="home-modal-content")]),

        *refresh_components,

        html.Div(id="home-body", children=_render_home_body(ctx)),
    ])


data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="home-body",
    render_body=_render_home_body,
)


@callback(
    Output("home-smart-modal", "opened"),
    Output("home-smart-modal", "title"),
    Output("home-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def handle_home_click(n_clicks):
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
    return True, cfg.get("title"), widget.strategy.render_detail(ctx)
