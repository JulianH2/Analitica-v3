from components.skeleton import get_skeleton
from flask import session
import dash
from dash import html
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_filter_section
from strategies.administration import (
    AdminKPIStrategy, AdminTrendChartStrategy,
    AdminDonutChartStrategy, AdminTableStrategy
)

dash.register_page(__name__, path="/admin-banks", title="Bancos")

SCREEN_ID = "administration-banks"

kpi_bank_initial = SmartWidget(
    "kb_initial",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="initial_balance",
        title="Saldo Inicial",
        icon="tabler:wallet",
        color="gray",
        layout_config={"height": 160}
    )
)

kpi_bank_incomes = SmartWidget(
    "kb_incomes",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_income",
        title="Ingresos",
        icon="tabler:trending-up",
        color="green",
        layout_config={"height": 160}
    )
)

kpi_bank_expenses = SmartWidget(
    "kb_expenses",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_expenses",
        title="Egresos",
        icon="tabler:trending-down",
        color="red",
        layout_config={"height": 160}
    )
)

kpi_bank_final = SmartWidget(
    "kb_final",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="final_balance",
        title="Saldo Final",
        icon="tabler:cash",
        color="indigo",
        layout_config={"height": 160}
    )
)

chart_bank_daily = ChartWidget(
    "cb_daily",
    AdminTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="daily_cash_flow",
        title="Evolución Diaria de Flujo",
        icon="tabler:chart-line",
        layout_config={"height": 360}
    )
)

chart_bank_donut = ChartWidget(
    "cb_donut",
    AdminDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="balance_by_bank",
        title="Saldo por Institución Bancaria",
        icon="tabler:chart-pie",
        layout_config={"height": 380}
    )
)

WIDGET_REGISTRY = {
    "kb_initial": kpi_bank_initial,
    "kb_incomes": kpi_bank_incomes,
    "kb_expenses": kpi_bank_expenses,
    "kb_final": kpi_bank_final
}

def _render_admin_banks_body(ctx):
    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 2, "lg": 4}, # type: ignore
            spacing="md",
            mb="lg",
            children=[
                kpi_bank_initial.render(ctx),
                kpi_bank_incomes.render(ctx),
                kpi_bank_expenses.render(ctx),
                kpi_bank_final.render(ctx)
            ]
        ),
        
        chart_bank_daily.render(ctx, h=360),
        dmc.Space(h="lg"),
        
        dmc.Grid(
            gutter="md",
            align="stretch",
            children=[
                dmc.GridCol(
                    span={"base": 12, "md": 5}, # type: ignore
                    children=[chart_bank_donut.render(ctx, h=380)]
                ),
                dmc.GridCol(
                    span={"base": 12, "md": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            shadow="sm",
                            h=380,
                            children=[
                                dmc.Text(
                                    "INGRESOS Y EGRESOS POR CONCEPTO",
                                    fw="bold",
                                    size="xs",
                                    c="dimmed", # type: ignore
                                    mb="md"
                                ),
                                dmc.ScrollArea(
                                    h=320,
                                    children=[
                                        AdminTableStrategy(
                                            SCREEN_ID,
                                            "income_expense_concepts"
                                        ).render(ctx)
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
        dmc.Space(h=30)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    
    filters = create_filter_section(
        year_id="bank-year",
        month_id="bank-month",
        default_month="septiembre",
        additional_filters=[
            {"id": "bank-empresa", "label": "Empresa Área", "data": ["Todas"], "value": "Todas"},
            {"id": "bank-institucion", "label": "Institución Bancaria", "data": ["Todas"], "value": "Todas"}
        ]
    )
    
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            create_smart_modal("bank-modal"),
            *refresh_components,
            filters,
            html.Div(id="admin-banks-body", children=get_skeleton(SCREEN_ID))
        ]
    )

FILTER_IDS = ["bank-year", "bank-month", "bank-empresa", "bank-institucion"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="admin-banks-body",
    render_body=_render_admin_banks_body,
    filter_ids=FILTER_IDS
)

register_modal_callback("bank-modal", WIDGET_REGISTRY, SCREEN_ID)