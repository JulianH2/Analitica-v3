from design_system import dmc as _dmc
from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.time_service import TimeService

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_operational_filters
from strategies.operational import (
    OpsKPIStrategy, OpsTrendChartStrategy, OpsDonutChartStrategy,
    OpsHorizontalBarStrategy, OpsTableStrategy, OpsGaugeStrategy,
)
from settings.theme import DesignSystem
from utils.helpers import safe_get

dash.register_page(__name__, path="/operational-dashboard", title="Control Operativo")

SCREEN_ID = "operational-dashboard"
PREFIX = "od"

_ts = TimeService()


def get_dynamic_title(base_title: str) -> str:
    return f"{base_title} {_ts.current_year} vs. {_ts.previous_year}"


# ── Fila 1: 3 Gauges principales ─────────────────────────────────────────────
w_inc = SmartWidget(
    f"{PREFIX}_inc",
    OpsGaugeStrategy(screen_id=SCREEN_ID, key="revenue_total", title="Ingreso Viaje",
                     icon="tabler:cash", color="indigo", has_detail=True,
                     layout_config={"height": 220}),
)
w_tri = SmartWidget(
    f"{PREFIX}_tri",
    OpsGaugeStrategy(screen_id=SCREEN_ID, key="total_trips", title="Viajes",
                     icon="tabler:truck", color="green", has_detail=True,
                     layout_config={"height": 220}),
)
w_kms = SmartWidget(
    f"{PREFIX}_kms",
    OpsGaugeStrategy(screen_id=SCREEN_ID, key="total_kilometers", title="Kilómetros",
                     icon="tabler:route", color="yellow", has_detail=True,
                     layout_config={"height": 220}),
)

# ── Fila 2: 4 KPIs de promedios ──────────────────────────────────────────────
w_avg_trip = SmartWidget(f"{PREFIX}_avg_trip", OpsKPIStrategy(
    screen_id=SCREEN_ID, key="revenue_per_trip", title="Ingreso x Viaje",
    icon="tabler:calculator", color="blue", has_detail=True))
w_avg_unit = SmartWidget(f"{PREFIX}_avg_unit", OpsKPIStrategy(
    screen_id=SCREEN_ID, key="revenue_per_unit", title="Ingreso x Unidad",
    icon="tabler:truck-delivery", color="indigo", has_detail=True))
w_units_qty = SmartWidget(f"{PREFIX}_units", OpsKPIStrategy(
    screen_id=SCREEN_ID, key="units_used", title="Unidades Utilizadas",
    icon="tabler:packages", color="violet", has_detail=True))
w_customers = SmartWidget(f"{PREFIX}_customers", OpsKPIStrategy(
    screen_id=SCREEN_ID, key="customers_served", title="Clientes Servidos",
    icon="tabler:users", color="teal", has_detail=True))


# ── Fila 3: Tendencias dinámicas ─────────────────────────────────────────────
class DynamicTrendChartStrategy(OpsTrendChartStrategy):
    def __init__(self, screen_id, key, base_title, icon="tabler:chart-line",
                 color="indigo", has_detail=True, layout_config=None):
        self.base_title = base_title
        super().__init__(screen_id, key, get_dynamic_title(base_title),
                         icon, color, has_detail, layout_config)

    def get_card_config(self, ctx):
        config = super().get_card_config(ctx)
        config["title"] = get_dynamic_title(self.base_title)
        return config


c_inc = ChartWidget(
    f"{PREFIX}_inc_comp",
    DynamicTrendChartStrategy(screen_id=SCREEN_ID, key="revenue_trends",
                              base_title="Ingresos", icon="tabler:chart-line",
                              color="indigo", has_detail=True,
                              layout_config={"height": 640}),
)
c_trips = ChartWidget(
    f"{PREFIX}_trips_comp",
    DynamicTrendChartStrategy(screen_id=SCREEN_ID, key="trips_trends",
                              base_title="Viajes", icon="tabler:chart-line",
                              color="green", has_detail=True,
                              layout_config={"height": 640}),
)

# ── Fila 4: Donut + Barras ───────────────────────────────────────────────────
c_mix = ChartWidget(
    f"{PREFIX}_mix",
    OpsDonutChartStrategy(screen_id=SCREEN_ID, key="revenue_by_operation_type",
                          title="Ingreso Viaje Por Tipo Operación/Ruta/Área",
                          color="indigo", has_detail=True,
                          layout_config={"height": 420}),
)
c_unit = ChartWidget(
    f"{PREFIX}_unit_bal",
    OpsHorizontalBarStrategy(screen_id=SCREEN_ID, key="revenue_by_unit",
                             title="Balanceo Ingresos por Unidad",
                             has_detail=True, layout_config={"height": 400}),
)

# ── Tablas ────────────────────────────────────────────────────────────────────
t_loaded = TableWidget(f"{PREFIX}_routes_loaded", OpsTableStrategy(SCREEN_ID, "routes_loaded", title="Rutas Cargado"))
t_empty = TableWidget(f"{PREFIX}_routes_empty", OpsTableStrategy(SCREEN_ID, "routes_empty", title="Rutas Vacío"))
t_clients = TableWidget(f"{PREFIX}_top_clients", OpsTableStrategy(SCREEN_ID, "top_clients", title="Ingreso Cliente"))
t_op = TableWidget(f"{PREFIX}_income_op", OpsTableStrategy(SCREEN_ID, "income_by_operator_report", title="Ingreso por Operador"))
t_unit = TableWidget(f"{PREFIX}_income_unit", OpsTableStrategy(SCREEN_ID, "income_by_unit_report", title="Ingreso por Unidad"))


# ─────────────────────────────────────────────────────────────────────────────
# Badge compacto de estado de flota
# ─────────────────────────────────────────────────────────────────────────────
def _render_fleet_badge(ctx):
    load_data = safe_get(ctx, ["operational", "dashboard", "kpis", "load_status"], {})
    val = load_data.get("value", 0) if isinstance(load_data, dict) else (float(load_data) if load_data else 0)
    if val < 1:
        val *= 100
    if val >= 80:
        color, bar_color = "green", DesignSystem.SUCCESS[5]
    elif val >= 60:
        color, bar_color = "yellow", DesignSystem.WARNING[5]
    else:
        color, bar_color = "red", DesignSystem.DANGER[5]

    return dmc.Group(
        gap="sm", align="center", mb=4,
        children=[
            DashIconify(icon="tabler:truck-loading", width=18, color=bar_color),
            dmc.Text("Estado de Carga:", size="xs", c=_dmc("dimmed"), fw=_dmc(600), tt="uppercase"),
            dmc.Text(f"{val:.1f}%", size="sm", fw=_dmc(700), c=color),
            dmc.Progress(value=min(val, 100), color=color, h=8, radius="xl",
                         style={"flex": 1, "maxWidth": "200px"}),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Render body
# ─────────────────────────────────────────────────────────────────────────────
def _render_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        # ── Fila 1: 3 Gauges principales ────────────────────────────
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                "gap": "0.8rem",
                "marginBottom": "1rem",
            },
            children=[
                w_inc.render(ctx, theme=theme),
                w_tri.render(ctx, theme=theme),
                w_kms.render(ctx, theme=theme),
            ],
        ),

        # ── Fila 2: Promedios Operativos ────────────────────────────
        dmc.Divider(my="sm", label="Promedios Operativos", labelPosition="center"),
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "0.6rem",
                "marginBottom": "1rem",
            },
            children=[
                w_avg_trip.render(ctx, theme=theme),
                w_avg_unit.render(ctx, theme=theme),
                w_units_qty.render(ctx, theme=theme),
                w_customers.render(ctx, theme=theme),
            ],
        ),

        # ── Fila 3: Tendencias (izq) | Rutas + Estado carga (der) ──
        dmc.Grid(gutter="md", mb="lg", children=[
            # Izquierda: Ingresos y Viajes apilados verticalmente
            dmc.GridCol(span=_dmc({"base": 12, "lg": 7}), children=[
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "0.8rem"},
                    children=[
                        c_inc.render(ctx, theme=theme),
                        c_trips.render(ctx, theme=theme),
                    ],
                ),
            ]),
            # Derecha: Estado de carga + tabs rutas
            dmc.GridCol(span=_dmc({"base": 12, "lg": 5}), children=[
                dmc.Paper(
                    p=8, withBorder=True, radius="md",
                    style={"height": "100%", "minHeight": "720px",
                           "backgroundColor": "transparent"},
                    children=[
                        _render_fleet_badge(ctx),
                        dmc.Tabs(value="rutas_cargado", children=[
                            dmc.TabsList([
                                dmc.TabsTab("Rutas Vacío", value="rutas_vacio",
                                            leftSection=DashIconify(icon="tabler:map-pin-off", width=14)),
                                dmc.TabsTab("Rutas Cargado", value="rutas_cargado",
                                            leftSection=DashIconify(icon="tabler:map-pin", width=14)),
                            ]),
                            dmc.TabsPanel(
                                html.Div(style={"height": "640px", "overflowY": "auto"},
                                         children=[t_empty.render(ctx, theme=theme)]),
                                value="rutas_vacio"),
                            dmc.TabsPanel(
                                html.Div(style={"height": "640px", "overflowY": "auto"},
                                         children=[t_loaded.render(ctx, theme=theme)]),
                                value="rutas_cargado"),
                        ]),
                    ],
                ),
            ]),
        ]),

        # ── Fila 4: Donut + Barras (izq) | Tablas ingreso (der) ────
        dmc.Grid(gutter="md", mb="lg", children=[
            # Izquierda: Donut + Barras apilados
            dmc.GridCol(span=_dmc({"base": 12, "lg": 5}), children=[
                html.Div(
                    style={"display": "flex", "flexDirection": "column", "gap": "0.8rem"},
                    children=[
                        c_mix.render(ctx, theme=theme),
                        c_unit.render(ctx, theme=theme),
                    ],
                ),
            ]),
            # Derecha: Tablas Ingreso (Unidad → Operador → Cliente)
            dmc.GridCol(span=_dmc({"base": 12, "lg": 7}), children=[
                dmc.Paper(
                    p=8, withBorder=True, radius="md",
                    style={"height": "100%", "backgroundColor": "transparent"},
                    children=[
                        dmc.Tabs(value="ingreso_unidad", children=[
                            dmc.TabsList([
                                dmc.TabsTab("Ingreso Unidad", value="ingreso_unidad",
                                            leftSection=DashIconify(icon="tabler:truck", width=14)),
                                dmc.TabsTab("Ingreso Operador", value="ingreso_operador",
                                            leftSection=DashIconify(icon="tabler:user", width=14)),
                                dmc.TabsTab("Ingreso Cliente", value="ingreso_cliente",
                                            leftSection=DashIconify(icon="tabler:building", width=14)),
                            ]),
                            dmc.TabsPanel(
                                html.Div(style={"height": "680px", "overflowY": "auto"},
                                         children=[t_unit.render(ctx, theme=theme)]),
                                value="ingreso_unidad"),
                            dmc.TabsPanel(
                                html.Div(style={"height": "680px", "overflowY": "auto"},
                                         children=[t_op.render(ctx, theme=theme)]),
                                value="ingreso_operador"),
                            dmc.TabsPanel(
                                html.Div(style={"height": "680px", "overflowY": "auto"},
                                         children=[t_clients.render(ctx, theme=theme)]),
                                value="ingreso_cliente"),
                        ]),
                    ],
                ),
            ]),
        ]),

        dmc.Space(h=30),
    ])


# ─────────────────────────────────────────────────────────────────────────────
# Registry, layout, callbacks
# ─────────────────────────────────────────────────────────────────────────────
WIDGET_REGISTRY = {
    f"{PREFIX}_inc": w_inc, f"{PREFIX}_tri": w_tri, f"{PREFIX}_kms": w_kms,
    f"{PREFIX}_avg_trip": w_avg_trip, f"{PREFIX}_avg_unit": w_avg_unit,
    f"{PREFIX}_units": w_units_qty, f"{PREFIX}_customers": w_customers,
    f"{PREFIX}_inc_comp": c_inc, f"{PREFIX}_trips_comp": c_trips,
    f"{PREFIX}_mix": c_mix, f"{PREFIX}_unit_bal": c_unit,
    f"{PREFIX}_routes_loaded": t_loaded, f"{PREFIX}_routes_empty": t_empty,
    f"{PREFIX}_top_clients": t_clients, f"{PREFIX}_income_op": t_op,
    f"{PREFIX}_income_unit": t_unit,
}

FILTER_IDS = [
    "ops-year", "ops-month", "ops-empresa", "ops-unidad", "ops-tipo-unidad",
    "ops-no-viaje", "ops-operador", "ops-tipo-operacion", "ops-clasificacion",
    "ops-cliente",
]


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    return dmc.Container(
        fluid=True, px="md",
        children=[
            dcc.Store(id="ops-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("ops-drawer"),
            create_operational_filters(prefix="ops"),
            html.Div(id="ops-body", children=get_skeleton(SCREEN_ID)),
        ],
    )


data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-body", render_body=_render_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="ops-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)