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
from flask import session

dash.register_page(__name__, path="/admin-banks", title="Bancos")

SCREEN_ID = "administration-banks"

kpi_bank_initial = SmartWidget(
    "kb_initial",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="initial_balance",
        title="Saldo Inicial Consolidado",
        icon="tabler:wallet",
        color="gray"
    )
)

kpi_bank_incomes = SmartWidget(
    "kb_incomes",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_income",
        title="Ingresos Consolidado",
        icon="tabler:trending-up",
        color="green"
    )
)

kpi_bank_expenses = SmartWidget(
    "kb_expenses",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_expenses",
        title="Egresos Consolidado",
        icon="tabler:trending-down",
        color="red"
    )
)

kpi_bank_final = SmartWidget(
    "kb_final",
    AdminKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="final_balance",
        title="Saldo Final Consolidado",
        icon="tabler:cash",
        color="indigo"
    )
)

chart_bank_daily = ChartWidget(
    "cb_daily",
    AdminTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="daily_cash_flow",
        title="Evolución Diaria de Flujo",
        icon="tabler:chart-line"
    )
)

chart_bank_donut = ChartWidget(
    "cb_donut",
    AdminDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="balance_by_bank",
        title="Saldo por Institución Bancaria",
        icon="tabler:chart-pie"
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
        dmc.Title("Administración - Bancos", order=3, mb="lg", c="dimmed"),
        
        dmc.SimpleGrid(
            cols={"base": 1, "sm": 2, "lg": 4},
            spacing="md",
            mb="xl",
            children=[
                kpi_bank_initial.render(ctx, theme=theme),
                kpi_bank_incomes.render(ctx, theme=theme),
                kpi_bank_expenses.render(ctx, theme=theme),
                kpi_bank_final.render(ctx, theme=theme)
            ]
        ),
        
        dmc.Paper(
            p="md",
            withBorder=True,
            mb="xl",
            shadow="sm",
            children=[chart_bank_daily.render(ctx, h=380)]
        ),
        
        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(
                    span={"base": 12, "md": 5},
                    children=[chart_bank_donut.render(ctx, h=400)]
                ),
                dmc.GridCol(
                    span={"base": 12, "md": 7},
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            shadow="sm",
                            children=[
                                dmc.Text(
                                    "INGRESOS Y EGRESOS POR CONCEPTO",
                                    fw="bold",
                                    size="xs",
                                    c="dimmed",
                                    mb="md"
                                ),
                                dmc.ScrollArea(
                                    h=360,
                                    children=[
                                        AdminTableStrategy(
                                            SCREEN_ID,
                                            "income_expense_concepts"
                                        ).render(ctx, theme=theme)
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
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
        year_id="bank-year",
        month_id="bank-month",
        default_month="enero",
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
            html.Div(id="admin-banks-body", children=_render_admin_banks_body(ctx))
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