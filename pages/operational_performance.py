from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_filter_section
from strategies.operational import (
    OpsKPIStrategy,
    OpsGaugeStrategy,
    OpsTrendChartStrategy,
    OpsDonutChartStrategy,
    OpsTableStrategy
)

dash.register_page(__name__, path="/ops-performance", title="Rendimientos")

SCREEN_ID = "operational-performance"
w_kms_lt = SmartWidget(
    "rp_kms_lt",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="real_yield",
        title="Rendimiento (Kms/Lt)",
        icon="tabler:gauge",
        color="green",
        has_detail=True,
        layout_config={"height": 300}
    )
)

w_kms_re = SmartWidget(
    "rp_kms_tot",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="real_kilometers",
        title="Kms Reales",
        icon="tabler:route",
        color="blue",
        has_detail=True,
        layout_config={"height": 300}
    )
)

w_litros = SmartWidget(
    "rp_litros",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="liters_consumed",
        title="Litros Consumidos",
        icon="tabler:droplet",
        color="orange",
        has_detail=True,
        layout_config={"height": 300}
    )
)

w_trend = ChartWidget(
    "cp_trend",
    OpsTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="yield_trends",
        title="Tendencia Rendimiento Real (Kms/Lt)",
        icon="tabler:timeline",
        color="indigo",
        has_detail=True,
        layout_config={"height": 340}
    )
)

w_mix = ChartWidget(
    "cp_mix",
    OpsDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="yield_by_operation",
        title="Distribución de Rendimiento por Operación",
        icon="tabler:chart-pie-2",
        color="green",
        has_detail=True,
        layout_config={"height": 340}
    )
)

WIDGET_REGISTRY = {
    "rp_kms_lt": w_kms_lt,
    "rp_kms_tot": w_kms_re,
    "rp_litros": w_litros,
    "cp_trend": w_trend,
    "cp_mix": w_mix
}

def _render_performance_tables(ctx):
    return dmc.Grid(
        gutter="md",
        children=[
            dmc.GridCol(
                span={"base": 12, "md": 5},
                children=[
                    dmc.Paper(
                        p=8,
                        withBorder=True,
                        radius="md",
                        children=[
                            dmc.Text("Rendimiento por Unidad", fw="bold", size="sm", mb="sm"),
                            html.Div(
                                style={"height": "330px", "overflowY": "auto"},
                                children=[OpsTableStrategy(SCREEN_ID, "performance_by_unit").render(ctx)]
                            )
                        ]
                    )
                ]
            ),
            dmc.GridCol(
                span={"base": 12, "md": 7},
                children=[
                    dmc.Paper(
                        p=8,
                        withBorder=True,
                        radius="md",
                        children=[
                            dmc.Text("Rendimiento por Operador", fw="bold", size="sm", mb="sm"),
                            html.Div(
                                style={"height": "330px", "overflowY": "auto"},
                                children=[OpsTableStrategy(SCREEN_ID, "operator_performance").render(ctx)]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def _render_ops_performance_body(ctx):
    return html.Div([
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"},
            children=[w_kms_lt.render(ctx), w_kms_re.render(ctx), w_litros.render(ctx)]
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"},
            children=[w_trend.render(ctx), w_mix.render(ctx)]
        ),
        _render_performance_tables(ctx),
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
    
    filters = create_filter_section(
        year_id="perf-year",
        month_id="perf-month",
        default_month="enero",
        additional_filters=[
            {"id": "perf-area", "label": "Área", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-ruta", "label": "Ruta", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"}
        ]
    )
    
    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="perf-load-trigger", data={"loaded": False}),
            *refresh_components,
            create_smart_drawer("perf-drawer"),
            filters,
            html.Div(id="ops-performance-body", children=get_skeleton(SCREEN_ID))
        ]
    )

@callback(
    Output("perf-load-trigger", "data"),
    Input("perf-load-trigger", "data"),
    prevent_initial_call=False
)
def trigger_perf_load(data):
    if data is None or not data.get("loaded"):
        import time
        time.sleep(0.8)
        return {"loaded": True}
    return no_update

FILTER_IDS = [
    "perf-year",
    "perf-month",
    "perf-area",
    "perf-unidad",
    "perf-operador",
    "perf-ruta",
    "perf-cliente"
]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-performance-body",
    render_body=_render_ops_performance_body,
    filter_ids=FILTER_IDS
)

register_drawer_callback("perf-drawer", WIDGET_REGISTRY, SCREEN_ID)