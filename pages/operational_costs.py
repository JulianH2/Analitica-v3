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
    OpsHorizontalBarStrategy,
    OpsTableStrategy
)

dash.register_page(__name__, path="/ops-costs", title="Costos Operaciones")

SCREEN_ID = "operational-costs"

w_utilidad = SmartWidget(
    "kc_utility",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="profit_per_trip",
        title="Utilidad Viaje",
        icon="tabler:trending-up",
        color="teal"
    )
)

w_costo_total = SmartWidget(
    "kc_total",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_trip_cost",
        title="Costo Viaje Total",
        icon="tabler:calculator",
        color="red"
    )
)

chart_cost_stack = ChartWidget(
    "cc_stack",
    OpsTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="cost_and_profit_trends",
        title="Costo y Utilidad",
        layout_config={"height": 380}
    )
)

chart_cost_breakdown = ChartWidget(
    "cc_break",
    OpsHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="cost_by_concept",
        title="Costos por Concepto",
        layout_config={"height": 380}
    )
)

chart_cost_yearly_comp = ChartWidget(
    "cc_comp",
    OpsTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="cost_breakdown",
        title="Costo Viaje Total 2025 vs 2024",
        icon="tabler:chart-line",
        color="red",
        layout_config={"height": 380}
    )
)

WIDGET_REGISTRY = {
    "kc_utility": w_utilidad,
    "kc_total": w_costo_total
}

def _render_cost_tabs(ctx):
    return dmc.Paper(
        p="md",
        withBorder=True,
        radius="md",
        children=[
            dmc.Tabs(
                value="cliente",
                children=[
                    dmc.TabsList([
                        dmc.TabsTab("Costos por Cliente", value="cliente"),
                        dmc.TabsTab("Costos por Unidad", value="unidad")
                    ]),
                    dmc.TabsPanel(
                        dmc.ScrollArea(
                            h=400,
                            pt="md",
                            children=[OpsTableStrategy(SCREEN_ID, "margin_by_route").render(ctx)]
                        ),
                        value="cliente"
                    ),
                    dmc.TabsPanel(
                        dmc.ScrollArea(
                            h=400,
                            pt="md",
                            children=[OpsTableStrategy(SCREEN_ID, "income_by_unit_report").render(ctx)]
                        ),
                        value="unidad"
                    )
                ]
            )
        ]
    )

def _render_ops_costs_body(ctx):
    return html.Div([
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 4}, # type: ignore
                    children=[
                        dmc.Stack(
                            gap="md",
                            children=[
                                w_utilidad.render(ctx, mode="combined"),
                                w_costo_total.render(ctx, mode="combined")
                            ]
                        )
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 8}, # type: ignore
                    children=[chart_cost_stack.render(ctx)]
                )
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 5}, # type: ignore
                    children=[chart_cost_breakdown.render(ctx)]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 7}, # type: ignore
                    children=[chart_cost_yearly_comp.render(ctx)]
                )
            ]
        ),
        dmc.Divider(
            my="xl",
            label="Análisis de Margen por Ruta",
            labelPosition="center"
        ),
        _render_cost_tabs(ctx),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=60 * 60 * 1000,
        max_intervals=1
    )
    filters = create_filter_section(
        year_id="cost-year",
        month_id="cost-month",
        default_month="septiembre",
        additional_filters=[
            {"id": "cost-empresa", "label": "Empresa Área", "data": ["Todas"], "value": "Todas"},
            {"id": "cost-clasificacion", "label": "Clasificación", "data": ["Todas"], "value": "Todas"},
            {"id": "cost-concepto", "label": "Concepto Costo", "data": ["Todos"], "value": "Todos"},
            {"id": "cost-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": "cost-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"}
        ]
    )
    return dmc.Container(
        fluid=True,
        px="xs",
        children=[
            create_smart_modal("costs-modal"),
            *refresh_components,
            filters,
            html.Div(id="ops-costs-body", children=_render_ops_costs_body(ctx))
        ]
    )

FILTER_IDS = [
    "cost-year",
    "cost-month",
    "cost-empresa",
    "cost-clasificacion",
    "cost-concepto",
    "cost-unidad",
    "cost-operador"
]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-costs-body",
    render_body=_render_ops_costs_body,
    filter_ids=FILTER_IDS
)

register_modal_callback("costs-modal", WIDGET_REGISTRY, SCREEN_ID)
