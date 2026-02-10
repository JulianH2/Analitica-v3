from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_operational_filters, get_filter_ids
from strategies.operational import (
    OpsKPIStrategy,
    OpsTrendChartStrategy,
    OpsDonutChartStrategy,
    OpsHorizontalBarStrategy,
    OpsTableStrategy,
    OpsGaugeStrategy
)
from settings.theme import DesignSystem
from utils.helpers import safe_get

dash.register_page(__name__, path="/ops-dashboard", title="Control Operativo")

SCREEN_ID = "operational-dashboard"

def get_current_year():
    return datetime.now().year

def get_previous_year():
    return datetime.now().year - 1

def get_dynamic_title(base_title: str) -> str:
    return f"{base_title} {get_current_year()} vs {get_previous_year()}"
w_inc = SmartWidget(
    "go_inc",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="revenue_total",
        title="Ingreso Viaje",
        icon="tabler:cash",
        color="indigo",
        has_detail=True,
        layout_config={"height": 300}
    )
)

w_tri = SmartWidget(
    "go_tri",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_trips",
        title="Viajes",
        icon="tabler:truck",
        color="green",
        has_detail=True,
        layout_config={"height": 300}
    )
)

w_kms = SmartWidget(
    "go_kms",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_kilometers",
        title="Kilómetros",
        icon="tabler:route",
        color="yellow",
        has_detail=True,
        layout_config={"height": 300}
    )
)

w_avg_trip = SmartWidget(
    "avg_trip",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="revenue_per_trip",
        title="Prom. x Viaje",
        icon="tabler:calculator",
        color="blue",
        has_detail=False
    )
)

w_avg_unit = SmartWidget(
    "avg_unit",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="revenue_per_unit",
        title="Prom. x Unidad",
        icon="tabler:truck-delivery",
        color="indigo",
        has_detail=False
    )
)

w_units_qty = SmartWidget(
    "units_qty",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="units_used",
        title="Unidades Uso",
        icon="tabler:packages",
        color="violet",
        has_detail=False
    )
)

w_customers = SmartWidget(
    "customers",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="customers_served",
        title="Clientes",
        icon="tabler:users",
        color="teal",
        has_detail=False
    )
)

class DynamicTrendChartStrategy(OpsTrendChartStrategy):
    def __init__(self, screen_id, chart_key, base_title, icon="tabler:chart-line", color="indigo", has_detail=True, layout_config=None):
        dynamic_title = get_dynamic_title(base_title)
        super().__init__(screen_id, chart_key, dynamic_title, icon, color, has_detail, layout_config)
        self.base_title = base_title
    
    def get_card_config(self, data_context):
        config = super().get_card_config(data_context)
        config["title"] = get_dynamic_title(self.base_title)
        return config

w_inc_comp = ChartWidget(
    "co_inc_comp",
    DynamicTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="revenue_trends",
        base_title="Ingresos",
        icon="tabler:chart-line",
        color="indigo",
        has_detail=True,
        layout_config={"height": 340}
    )
)

w_trips_comp = ChartWidget(
    "co_trips_comp",
    DynamicTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="trips_trends",
        base_title="Viajes",
        icon="tabler:chart-line",
        color="green",
        has_detail=True,
        layout_config={"height": 340}
    )
)

w_mix = ChartWidget(
    "co_mix",
    OpsDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="revenue_by_operation_type",
        title="Ingreso por Tipo Operación",
        color="indigo",
        has_detail=True,
        layout_config={"height": 360}
    )
)

w_unit_bal = ChartWidget(
    "co_unit_bal",
    OpsHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="revenue_by_unit",
        title="Balanceo Ingresos por Unidad",
        has_detail=True,
        layout_config={"height": 340}
    )
)

WIDGET_REGISTRY = {
    "go_inc": w_inc,
    "go_tri": w_tri,
    "go_kms": w_kms,
    "avg_trip": w_avg_trip,
    "avg_unit": w_avg_unit,
    "units_qty": w_units_qty,
    "customers": w_customers,
    "co_inc_comp": w_inc_comp,
    "co_trips_comp": w_trips_comp,
    "co_mix": w_mix,
    "co_unit_bal": w_unit_bal
}

def _render_fleet_status(ctx):
    load_data = safe_get(ctx, ["operational", "dashboard", "kpis", "load_status"], {})
    
    if isinstance(load_data, dict):
        val = load_data.get("value", 0)
        val_formatted = load_data.get("value_formatted", f"{val:.1f}%")
    else:
        val = float(load_data) if load_data else 0
        val_formatted = f"{val:.1f}%"
    
    if val < 1:
        val = val * 100
    
    if val >= 80:
        color = "green"
        icon_color = DesignSystem.SUCCESS[5]
    elif val >= 60:
        color = "yellow"
        icon_color = DesignSystem.WARNING[5]
    else:
        color = "red"
        icon_color = DesignSystem.DANGER[5]
    
    return dmc.Paper(
        p=10,
        withBorder=True,
        radius="md",
        style={"height": "390px"},
        children=[
            dmc.Stack(
                justify="center",
                align="center",
                style={"height": "100%"},
                gap=8,
                children=[
                    dmc.Text("Estado de Carga de Flota", fw="bold", size="xs", c="dimmed", tt="uppercase"),
                    DashIconify(icon="tabler:truck-loading", width=52, color=icon_color),
                    dmc.Text(f"{val:.1f}%", fw="bold", size="1.8rem", c=color),
                    dmc.Text("Cargado", size="sm", c="dimmed"),
                    dmc.Progress(value=min(val, 100), color=color, h=20, radius="xl", style={"width": "90%"})
                ]
            )
        ]
    )

def _render_routes_tabs(ctx):
    return dmc.Paper(
        p=8,
        withBorder=True,
        radius="md",
        style={"height": "390px"},
        children=[
            dmc.Tabs(
                value="rutas_cargado",
                children=[
                    dmc.TabsList([
                        dmc.TabsTab("Rutas Vacío", value="rutas_vacio", leftSection=DashIconify(icon="tabler:map-pin-off")),
                        dmc.TabsTab("Rutas Cargado", value="rutas_cargado", leftSection=DashIconify(icon="tabler:map-pin"))
                    ]),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "330px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "routes_empty").render(ctx)]
                        ),
                        value="rutas_vacio"
                    ),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "330px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "routes_loaded").render(ctx)]
                        ),
                        value="rutas_cargado"
                    )
                ]
            )
        ]
    )

def _render_income_tabs(ctx):
    return dmc.Paper(
        p=8,
        withBorder=True,
        children=[
            dmc.Tabs(
                value="ingreso_cliente",
                children=[
                    dmc.TabsList([
                        dmc.TabsTab("Ingreso Cliente", value="ingreso_cliente"),
                        dmc.TabsTab("Ingreso Operador", value="ingreso_operador"),
                        dmc.TabsTab("Ingreso Unidad", value="ingreso_unidad")
                    ]),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "top_clients").render(ctx)]
                        ),
                        value="ingreso_cliente"
                    ),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "income_by_operator_report").render(ctx)]
                        ),
                        value="ingreso_operador"
                    ),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "income_by_unit_report").render(ctx)]
                        ),
                        value="ingreso_unidad"
                    )
                ]
            )
        ]
    )

def _render_body(ctx):
    return html.Div([
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))", "gap": "0.8rem", "marginBottom": "1rem"},
            children=[w_inc.render(ctx), w_tri.render(ctx), w_kms.render(ctx)]
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.6rem", "marginBottom": "1rem"},
            children=[w_avg_trip.render(ctx), w_avg_unit.render(ctx), w_units_qty.render(ctx), w_customers.render(ctx)]
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))", "gap": "0.8rem", "marginBottom": "1rem"},
            children=[w_inc_comp.render(ctx), w_trips_comp.render(ctx)]
        ),
        dmc.Grid(
            gutter="md",
            mb="lg",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 4}, children=[_render_fleet_status(ctx)]),
                dmc.GridCol(span={"base": 12, "lg": 8}, children=[_render_routes_tabs(ctx)])
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="lg",
            children=[
                dmc.GridCol(span={"base": 12, "md": 5}, children=[w_mix.render(ctx)]),
                dmc.GridCol(
                    span={"base": 12, "md": 7},
                    children=[
                        dmc.Paper(
                            p=6,
                            withBorder=True,
                            radius="md",
                            style={"height": "360px"},
                            children=[
                                html.Div(
                                    style={"height": "100%", "overflowY": "auto"},
                                    children=[w_unit_bal.render(ctx)]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        _render_income_tabs(ctx),
        dmc.Space(h=30)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID, 
        interval_ms=60 * 60 * 1000, 
        max_intervals=-1
    )
    
    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="ops-load-trigger", data={"loaded": False}),
            *refresh_components,
            create_smart_drawer("ops-drawer"),
            create_operational_filters(prefix="ops"),
            html.Div(id="ops-body", children=get_skeleton(SCREEN_ID))
        ]
    )

@callback(
    Output("ops-load-trigger", "data"),
    Input("ops-load-trigger", "data"),
    prevent_initial_call=False
)
def trigger_ops_load(data):
    if data is None or not data.get("loaded"):
        import time
        time.sleep(0.8)
        return {"loaded": True}
    return no_update

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-body",
    render_body=_render_body,
    filter_ids=get_filter_ids("ops", 5)
)

register_drawer_callback("ops-drawer", WIDGET_REGISTRY, SCREEN_ID)