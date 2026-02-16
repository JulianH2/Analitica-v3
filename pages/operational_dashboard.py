from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_operational_filters
from strategies.operational import OpsKPIStrategy, OpsTrendChartStrategy, OpsDonutChartStrategy, OpsHorizontalBarStrategy, OpsTableStrategy, OpsGaugeStrategy
from settings.theme import DesignSystem
from utils.helpers import safe_get

dash.register_page(__name__, path="/operational-dashboard", title="Control Operativo")

SCREEN_ID = "operational-dashboard"
PREFIX = "od"

def get_current_year(): return datetime.now().year
def get_previous_year(): return datetime.now().year - 1
def get_dynamic_title(base_title: str) -> str: return f"{base_title} {get_current_year()} vs {get_previous_year()}"

w_inc = SmartWidget(f"{PREFIX}_inc", OpsGaugeStrategy(screen_id=SCREEN_ID, kpi_key="revenue_total", title="Ingreso Viaje", icon="tabler:cash", color="indigo", has_detail=True, layout_config={"height": 300}))
w_tri = SmartWidget(f"{PREFIX}_tri", OpsGaugeStrategy(screen_id=SCREEN_ID, kpi_key="total_trips", title="Viajes", icon="tabler:truck", color="green", has_detail=True, layout_config={"height": 300}))
w_kms = SmartWidget(f"{PREFIX}_kms", OpsGaugeStrategy(screen_id=SCREEN_ID, kpi_key="total_kilometers", title="Kilómetros", icon="tabler:route", color="yellow", has_detail=True, layout_config={"height": 300}))

w_avg_trip = SmartWidget(f"{PREFIX}_avg_trip", OpsKPIStrategy(screen_id=SCREEN_ID, kpi_key="revenue_per_trip", title="Prom. x Viaje", icon="tabler:calculator", color="blue", has_detail=True))
w_avg_unit = SmartWidget(f"{PREFIX}_avg_unit", OpsKPIStrategy(screen_id=SCREEN_ID, kpi_key="revenue_per_unit", title="Prom. x Unidad", icon="tabler:truck-delivery", color="indigo", has_detail=True))
w_units_qty = SmartWidget(f"{PREFIX}_units", OpsKPIStrategy(screen_id=SCREEN_ID, kpi_key="units_used", title="Unidades Uso", icon="tabler:packages", color="violet", has_detail=True))
w_customers = SmartWidget(f"{PREFIX}_customers", OpsKPIStrategy(screen_id=SCREEN_ID, kpi_key="customers_served", title="Clientes", icon="tabler:users", color="teal", has_detail=True))

class DynamicTrendChartStrategy(OpsTrendChartStrategy):
    def __init__(self, screen_id, chart_key, base_title, icon="tabler:chart-line", color="indigo", has_detail=True, layout_config=None):
        self.base_title = base_title
        super().__init__(screen_id, chart_key, get_dynamic_title(base_title), icon, color, has_detail, layout_config)
    def get_card_config(self, data_context):
        config = super().get_card_config(data_context)
        config["title"] = get_dynamic_title(self.base_title)
        return config

c_inc = ChartWidget(f"{PREFIX}_inc_comp", DynamicTrendChartStrategy(screen_id=SCREEN_ID, chart_key="revenue_trends", base_title="Ingresos", icon="tabler:chart-line", color="indigo", has_detail=True, layout_config={"height": 340}))
c_trips = ChartWidget(f"{PREFIX}_trips_comp", DynamicTrendChartStrategy(screen_id=SCREEN_ID, chart_key="trips_trends", base_title="Viajes", icon="tabler:chart-line", color="green", has_detail=True, layout_config={"height": 340}))

c_mix = ChartWidget(f"{PREFIX}_mix", OpsDonutChartStrategy(screen_id=SCREEN_ID, chart_key="revenue_by_operation_type", title="Ingreso por Tipo Operación", color="indigo", has_detail=True, layout_config={"height": 360}))
c_unit = ChartWidget(f"{PREFIX}_unit_bal", OpsHorizontalBarStrategy(screen_id=SCREEN_ID, chart_key="revenue_by_unit", title="Balanceo Ingresos por Unidad", has_detail=True, layout_config={"height": 340}))

t_loaded = TableWidget(f"{PREFIX}_routes_loaded", OpsTableStrategy(SCREEN_ID, "routes_loaded", title="Rutas Cargado"))
t_empty = TableWidget(f"{PREFIX}_routes_empty", OpsTableStrategy(SCREEN_ID, "routes_empty", title="Rutas Vacío"))
t_clients = TableWidget(f"{PREFIX}_top_clients", OpsTableStrategy(SCREEN_ID, "top_clients", title="Top Clientes"))
t_op = TableWidget(f"{PREFIX}_income_op", OpsTableStrategy(SCREEN_ID, "income_by_operator_report", title="Ingreso por Operador"))
t_unit = TableWidget(f"{PREFIX}_income_unit", OpsTableStrategy(SCREEN_ID, "income_by_unit_report", title="Ingreso por Unidad"))

def _render_fleet_status(ctx):
    load_data = safe_get(ctx, ["operational", "dashboard", "kpis", "load_status"], {})
    val = load_data.get("value", 0) if isinstance(load_data, dict) else (float(load_data) if load_data else 0)
    if val < 1: val *= 100
    if val >= 80: color, icon_color = "green", DesignSystem.SUCCESS[5]
    elif val >= 60: color, icon_color = "yellow", DesignSystem.WARNING[5]
    else: color, icon_color = "red", DesignSystem.DANGER[5]
    return dmc.Paper(p=10, withBorder=True, radius="md", style={"height": "390px", "backgroundColor": "transparent"}, children=[
        dmc.Stack(justify="center", align="center", style={"height": "100%"}, gap=8, children=[
            dmc.Text("Estado de Carga de Flota", fw="bold", size="xs", c="dimmed", tt="uppercase"), # type: ignore
            DashIconify(icon="tabler:truck-loading", width=52, color=icon_color),
            dmc.Text(f"{val:.1f}%", fw="bold", size="1.8rem", c=color), # type: ignore
            dmc.Text("Cargado", size="sm", c="dimmed"), # type: ignore
            dmc.Progress(value=min(val, 100), color=color, h=20, radius="xl", style={"width": "90%"}),
        ])
    ])

def _render_routes_tabs(ctx, theme):
    return dmc.Paper(p=8, withBorder=True, radius="md", style={"height": "390px", "backgroundColor": "transparent"}, children=[
        dmc.Tabs(value="rutas_cargado", children=[
            dmc.TabsList([
                dmc.TabsTab("Rutas Vacío", value="rutas_vacio", leftSection=DashIconify(icon="tabler:map-pin-off")),
                dmc.TabsTab("Rutas Cargado", value="rutas_cargado", leftSection=DashIconify(icon="tabler:map-pin")),
            ]),
            dmc.TabsPanel(html.Div(style={"height": "330px", "overflowY": "auto"}, children=[t_empty.render(ctx, theme=theme)]), value="rutas_vacio"),
            dmc.TabsPanel(html.Div(style={"height": "330px", "overflowY": "auto"}, children=[t_loaded.render(ctx, theme=theme)]), value="rutas_cargado"),
        ])
    ])

def _render_income_tabs(ctx, theme):
    return dmc.Paper(p=8, withBorder=True, children=[
        dmc.Tabs(value="ingreso_cliente", children=[
            dmc.TabsList([
                dmc.TabsTab("Ingreso Cliente", value="ingreso_cliente"),
                dmc.TabsTab("Ingreso Operador", value="ingreso_operador"),
                dmc.TabsTab("Ingreso Unidad", value="ingreso_unidad"),
            ]),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_clients.render(ctx, theme=theme)]), value="ingreso_cliente"),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_op.render(ctx, theme=theme)]), value="ingreso_operador"),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_unit.render(ctx, theme=theme)]), value="ingreso_unidad"),
        ])
    ])

def _render_body(ctx):
    theme = session.get("theme", "dark")
    def _card(widget_content, h=None): return dmc.Paper(p="xs", radius="md", withBorder=True, shadow="md", style={"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}, children=widget_content)

    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))", "gap": "0.8rem", "marginBottom": "1rem"}, children=[_card(w_inc.render(ctx, theme=theme)), _card(w_tri.render(ctx, theme=theme)), _card(w_kms.render(ctx, theme=theme))]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.6rem", "marginBottom": "1rem"}, children=[_card(w_avg_trip.render(ctx, theme=theme)), _card(w_avg_unit.render(ctx, theme=theme)), _card(w_units_qty.render(ctx, theme=theme)), _card(w_customers.render(ctx, theme=theme))]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))", "gap": "0.8rem", "marginBottom": "1rem"}, children=[_card(c_inc.render(ctx, theme=theme)), _card(c_trips.render(ctx, theme=theme))]),
        dmc.Grid(gutter="md", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[_render_fleet_status(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[_render_routes_tabs(ctx, theme)]), # type: ignore
        ]),
        dmc.Grid(gutter="md", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[_card(c_mix.render(ctx, theme=theme))]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 7}, children=[dmc.Paper(p=6, withBorder=True, radius="md", style={"height": "360px", "backgroundColor": "transparent"}, children=[html.Div(style={"height": "100%", "overflowY": "auto"}, children=[c_unit.render(ctx, theme=theme)])])]), # type: ignore
        ]),
        _render_income_tabs(ctx, theme),
        dmc.Space(h=30),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_inc": w_inc, f"{PREFIX}_tri": w_tri, f"{PREFIX}_kms": w_kms,
    f"{PREFIX}_avg_trip": w_avg_trip, f"{PREFIX}_avg_unit": w_avg_unit, f"{PREFIX}_units": w_units_qty, f"{PREFIX}_customers": w_customers,
    f"{PREFIX}_inc_comp": c_inc, f"{PREFIX}_trips_comp": c_trips,
    f"{PREFIX}_mix": c_mix, f"{PREFIX}_unit_bal": c_unit,
    f"{PREFIX}_routes_loaded": t_loaded, f"{PREFIX}_routes_empty": t_empty,
    f"{PREFIX}_top_clients": t_clients, f"{PREFIX}_income_op": t_op, f"{PREFIX}_income_unit": t_unit,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="ops-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("ops-drawer"),
            create_operational_filters(prefix="ops"),
            html.Div(id="ops-body", children=get_skeleton(SCREEN_ID)),
        ],
    )

FILTER_IDS = ["ops-year", "ops-month", "ops-empresa", "ops-clasificacion", "ops-cliente", "ops-unidad", "ops-operador"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-body", render_body=_render_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="ops-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)
