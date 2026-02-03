from flask import session
import dash
from dash import html
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
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
        color="green"
    )
)

w_kms_re = SmartWidget(
    "rp_kms_tot",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="real_kilometers",
        title="Kms Reales",
        icon="tabler:route",
        color="blue"
    )
)

w_litros = SmartWidget(
    "rp_litros",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="liters_consumed",
        title="Litros Consumidos",
        icon="tabler:droplet",
        color="orange"
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
        layout_config={"height": 380}
    )
)

w_mix = ChartWidget(
    "cp_mix",
    OpsDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="yield_by_operation",
        title="Distribución de Rendimiento por Operación",
        icon="tabler:chart-pie-2",
        color="indigo",
        layout_config={"height": 380}
    )
)

WIDGET_REGISTRY = {
    "rp_kms_lt": w_kms_lt,
    "rp_kms_tot": w_kms_re,
    "rp_litros": w_litros
}

def _render_performance_tables(ctx):
    return dmc.Grid(
        gutter="md",
        children=[
            dmc.GridCol(
                span={"base": 12, "md": 5}, # type: ignore
                children=[
                    dmc.Paper(
                        p="md",
                        withBorder=True,
                        radius="md",
                        children=[
                            dmc.Text("Rendimiento por Unidad", fw="bold", size="sm", mb="md"),
                            dmc.ScrollArea(
                                h=350,
                                children=[OpsTableStrategy(SCREEN_ID, "operator_performance").render(ctx)]
                            )
                        ]
                    )
                ]
            ),
            dmc.GridCol(
                span={"base": 12, "md": 7}, # type: ignore
                children=[
                    dmc.Paper(
                        p="md",
                        withBorder=True,
                        radius="md",
                        children=[
                            dmc.Text("Rendimiento por Operador", fw="bold", size="sm", mb="md"),
                            dmc.ScrollArea(
                                h=350,
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
        dmc.SimpleGrid(
            cols={"base": 1, "md": 3}, # type: ignore
            spacing="md",
            mb="xl",
            children=[
                w_kms_lt.render(ctx, mode="combined"),
                w_kms_re.render(ctx, mode="combined"),
                w_litros.render(ctx, mode="combined")
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "md": 8}, children=[w_trend.render(ctx)]), # type: ignore
                dmc.GridCol(span={"base": 12, "md": 4}, children=[w_mix.render(ctx)]) # type: ignore
            ]
        ),
        _render_performance_tables(ctx),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    filters = create_filter_section(
        year_id="perf-year",
        month_id="perf-month",
        default_month="septiembre",
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
        px="xs",
        children=[
            create_smart_modal("perf-modal"),
            *refresh_components,
            filters,
            html.Div(id="ops-performance-body", children=_render_ops_performance_body(ctx))
        ]
    )

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

register_modal_callback("perf-modal", WIDGET_REGISTRY, SCREEN_ID)
