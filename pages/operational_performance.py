from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_filter_section
from strategies.operational import OpsGaugeStrategy, OpsTrendChartStrategy, OpsDonutChartStrategy, OpsTableStrategy

dash.register_page(__name__, path="/operational-performance", title="Rendimientos")

SCREEN_ID = "operational-performance"
PREFIX = "op"

w_kms_lt = SmartWidget(f"{PREFIX}_kms_lt", OpsGaugeStrategy(screen_id=SCREEN_ID, key="real_yield", title="Rendimiento (Kms/Lt)", icon="tabler:gauge", color="green", has_detail=True, layout_config={"height": 300}))
w_kms_re = SmartWidget(f"{PREFIX}_kms_tot", OpsGaugeStrategy(screen_id=SCREEN_ID, key="real_kilometers", title="Kms Reales", icon="tabler:route", color="blue", has_detail=True, layout_config={"height": 300}))
w_litros = SmartWidget(f"{PREFIX}_litros", OpsGaugeStrategy(screen_id=SCREEN_ID, key="liters_consumed", title="Litros Consumidos", icon="tabler:droplet", color="orange", has_detail=True, layout_config={"height": 300}))

c_trend = ChartWidget(f"{PREFIX}_trend", OpsTrendChartStrategy(screen_id=SCREEN_ID, key="yield_trends", title="Tendencia Rendimiento Real (Kms/Lt)", icon="tabler:timeline", color="indigo", has_detail=True, layout_config={"height": 340}))
c_mix = ChartWidget(f"{PREFIX}_mix", OpsDonutChartStrategy(screen_id=SCREEN_ID, key="yield_by_operation", title="Distribución de Rendimiento por Operación", icon="tabler:chart-pie-2", color="green", has_detail=True, layout_config={"height": 340}))

t_unit = TableWidget(f"{PREFIX}_unit", OpsTableStrategy(SCREEN_ID, "performance_by_unit", title="Rendimiento por Unidad"))
t_oper = TableWidget(f"{PREFIX}_oper", OpsTableStrategy(SCREEN_ID, "operator_performance", title="Rendimiento por Operador"))

def _render_ops_performance_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            w_kms_lt.render(ctx, theme=theme),
            w_kms_re.render(ctx, theme=theme),
            w_litros.render(ctx, theme=theme),
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            c_trend.render(ctx, theme=theme),
            c_mix.render(ctx, theme=theme),
        ]),
        dmc.Grid(gutter="md", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[html.Div(style={"height": "330px", "overflowY": "auto"}, children=[t_unit.render(ctx, theme=theme)])]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 7}, children=[html.Div(style={"height": "330px", "overflowY": "auto"}, children=[t_oper.render(ctx, theme=theme)])]), # type: ignore
        ]),
        dmc.Space(h=30),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_kms_lt": w_kms_lt,
    f"{PREFIX}_kms_tot": w_kms_re,
    f"{PREFIX}_litros": w_litros,
    f"{PREFIX}_trend": c_trend,
    f"{PREFIX}_mix": c_mix,
    f"{PREFIX}_unit": t_unit,
    f"{PREFIX}_oper": t_oper,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")


    theme = session.get("theme", "dark")
    
    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        theme=theme,
        year_id="perf-year",
        month_id="perf-month",
        default_month="enero",
        additional_filters=[
            {"id": "perf-area", "label": "Área", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-ruta", "label": "Ruta", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="perf-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("perf-drawer"),
            filters,
            html.Div(id="ops-performance-body", children=get_skeleton(SCREEN_ID)),
        ],
    )

FILTER_IDS = ["perf-year", "perf-month", "perf-area", "perf-unidad", "perf-operador", "perf-ruta", "perf-cliente"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-performance-body", render_body=_render_ops_performance_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="perf-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)