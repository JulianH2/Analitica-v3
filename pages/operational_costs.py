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
        color="teal",
        has_detail=True,
        layout_config={"height": 290}
    )
)

w_costo_total = SmartWidget(
    "kc_total",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_trip_cost",
        title="Costo Viaje Total",
        icon="tabler:calculator",
        color="red",
        has_detail=True,
        layout_config={"height": 300}
    )
)

chart_cost_stack = ChartWidget(
    "cc_stack",
    OpsTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="cost_and_profit_trends",
        title="Costo y Utilidad",
        has_detail=True,
        layout_config={"height": "100%"}
    )
)

chart_cost_breakdown = ChartWidget(
    "cc_break",
    OpsHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="cost_by_concept",
        title="Costos por Concepto",
        has_detail=True,
        layout_config={"height": 360}
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
        has_detail=True,
        layout_config={"height": 360}
    )
)

WIDGET_REGISTRY = {
    "kc_utility": w_utilidad,
    "kc_total": w_costo_total,
    "cc_stack": chart_cost_stack,
    "cc_break": chart_cost_breakdown,
    "cc_comp": chart_cost_yearly_comp
}

def _render_cost_tabs(ctx):
    return dmc.Paper(
        p=8,
        withBorder=True,
        radius="md",
        children=[
            dmc.Tabs(
                value="ruta",
                children=[
                    dmc.TabsList([
                        dmc.TabsTab("Margen por Ruta", value="ruta"),
                        dmc.TabsTab("Margen por Unidad", value="unidad"),
                        dmc.TabsTab("Margen por Operador", value="operador"),
                        dmc.TabsTab("Margen por Viaje", value="viaje"),
                        dmc.TabsTab("Margen por Cliente", value="cliente")
                    ]),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "margin_by_route").render(ctx)]
                        ),
                        value="ruta"
                    ),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "margin_by_unit").render(ctx)]
                        ),
                        value="unidad"
                    ),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "margin_by_operator").render(ctx)]
                        ),
                        value="operador"
                    ),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "margin_by_trip").render(ctx)]
                        ),
                        value="viaje"
                    ),
                    dmc.TabsPanel(
                        html.Div(
                            style={"height": "380px", "overflowY": "auto"},
                            children=[OpsTableStrategy(SCREEN_ID, "margin_by_client").render(ctx)]
                        ),
                        value="cliente"
                    )
                ]
            )
        ]
    )

def _render_ops_costs_body(ctx):
    return html.Div([
        dmc.Grid(
            gutter="md",
            mb="lg",
            align="stretch",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 4},
                    children=[
                        html.Div(
                            style={"display": "grid", "gridTemplateRows": "1fr 1fr", "gap": "0.8rem", "height": "100%"},
                            children=[w_utilidad.render(ctx), w_costo_total.render(ctx)]
                        )
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 8},
                    children=[chart_cost_stack.render(ctx)]
                )
            ]
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"},
            children=[chart_cost_breakdown.render(ctx), chart_cost_yearly_comp.render(ctx)]
        ),
        dmc.Divider(
            my="lg",
            label="Análisis de Margen",
            labelPosition="center"
        ),
        _render_cost_tabs(ctx),
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
        year_id="cost-year",
        month_id="cost-month",
        default_month="enero",
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
        px="md",
        children=[
            dcc.Store(id="costs-load-trigger", data={"loaded": False}),
            *refresh_components,
            create_smart_drawer("costs-drawer"),
            filters,
            html.Div(id="ops-costs-body", children=get_skeleton(SCREEN_ID))
        ]
    )

@callback(
    Output("costs-load-trigger", "data"),
    Input("costs-load-trigger", "data"),
    prevent_initial_call=False
)
def trigger_costs_load(data):
    if data is None or not data.get("loaded"):
        import time
        time.sleep(0.8)
        return {"loaded": True}
    return no_update

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

register_drawer_callback("costs-drawer", WIDGET_REGISTRY, SCREEN_ID)