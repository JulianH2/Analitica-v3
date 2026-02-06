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
    AdminKPIStrategy, AdminGaugeStrategy,
    AdminTrendChartStrategy, AdminDonutChartStrategy,
    AdminStackedBarStrategy, AdminTableStrategy
)

dash.register_page(__name__, path="/admin-collection", title="Cobranza")

SCREEN_ID = "administration-receivables"
kpi_billing = SmartWidget(
    "ka_billing",
    AdminKPIStrategy(SCREEN_ID, "billed_amount", "Facturado", "tabler:file-invoice", "indigo", layout_config={"height": 115})
)
kpi_credit = SmartWidget(
    "ka_credit",
    AdminKPIStrategy(SCREEN_ID, "credit_notes", "Notas Crédito", "tabler:file-minus", "red", layout_config={"height": 115})
)
kpi_debit = SmartWidget(
    "ka_debit",
    AdminKPIStrategy(SCREEN_ID, "debit_notes", "Notas Cargo", "tabler:file-plus", "gray", layout_config={"height": 115})
)
kpi_payments = SmartWidget(
    "ka_payments",
    AdminKPIStrategy(SCREEN_ID, "collected_amount", "Cobrado", "tabler:cash", "green", layout_config={"height": 115})
)
kpi_portfolio = SmartWidget(
    "ka_portfolio",
    AdminKPIStrategy(SCREEN_ID, "accounts_receivable", "Cartera", "tabler:users", "yellow", layout_config={"height": 115})
)
kpi_balance = SmartWidget(
    "ka_balance",
    AdminKPIStrategy(SCREEN_ID, "net_balance", "Saldo Neto", "tabler:calculator", "indigo", layout_config={"height": 115})
)

w_gauge_eff = SmartWidget(
    "gc_billing",
    AdminGaugeStrategy(SCREEN_ID, "collection_efficiency", "Eficiencia Cobro", "indigo", icon="tabler:target", layout_config={"height": 180})
)
w_gauge_days = SmartWidget(
    "gc_days",
    AdminGaugeStrategy(SCREEN_ID, "average_collection_days", "Días Cartera", "yellow", icon="tabler:calendar", layout_config={"height": 180})
)

chart_mix = ChartWidget(
    "cc_mix",
    AdminDonutChartStrategy(SCREEN_ID, "receivables_by_status", "Distribución de Cartera", layout_config={"height": 360})
)
chart_stack = ChartWidget(
    "cc_stack",
    AdminStackedBarStrategy(SCREEN_ID, "debtors_by_range", "Deudores por Rango", layout_config={"height": 440})
)
chart_comp = ChartWidget(
    "cc_comp",
    AdminTrendChartStrategy(SCREEN_ID, "collection_trends", "Facturado vs Cobrado (Comparativo)", layout_config={"height": 360})
)

WIDGET_REGISTRY = {
    "ka_billing": kpi_billing, "ka_credit": kpi_credit, "ka_debit": kpi_debit,
    "ka_payments": kpi_payments, "ka_portfolio": kpi_portfolio, "ka_balance": kpi_balance,
    "gc_billing": w_gauge_eff, "gc_days": w_gauge_days
}

def _render_collection_body(ctx):
    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 2, "sm": 3, "lg": 6}, # type: ignore
            spacing="sm",
            mb="lg",
            children=[
                kpi_billing.render(ctx),
                kpi_credit.render(ctx),
                kpi_debit.render(ctx),
                kpi_payments.render(ctx),
                kpi_portfolio.render(ctx),
                kpi_balance.render(ctx)
            ]
        ),
        
        dmc.Grid(
            gutter="md",
            mb="lg",
            align="stretch",
            children=[
                dmc.GridCol(
                    span={"base": 12, "md": 6}, # type: ignore
                    children=[
                        dmc.SimpleGrid(cols=2, spacing="md", children=[
                            w_gauge_eff.render(ctx, mode="combined"),
                            w_gauge_days.render(ctx, mode="combined")
                        ])
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "md": 6}, # type: ignore
                    children=[chart_mix.render(ctx, h=360)]
                )
            ]
        ),
        
        dmc.Grid(
            gutter="md",
            mb="lg",
            align="stretch",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            shadow="sm",
                            h=440,
                            children=[
                                dmc.Text("ANTIGÜEDAD DE SALDOS POR CLIENTE", fw="bold", size="xs", c="dimmed", mb="md"), # type: ignore
                                dmc.ScrollArea(
                                    h=380,
                                    children=[AdminTableStrategy(SCREEN_ID, "aging_by_client").render(ctx)]
                                )
                            ]
                        )
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 5}, # type: ignore
                    children=[chart_stack.render(ctx, h=440)]
                )
            ]
        ),
        
        chart_comp.render(ctx, h=360),
        
        dmc.Space(h=30)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    
    filters = create_filter_section(
        year_id="col-year", month_id="col-month",
        additional_filters=[
            {"id": "col-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": "col-tipo-op", "label": "Tipo Op.", "data": ["Todas"], "value": "Todas"},
            {"id": "col-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"}
        ]
    )
    
    return dmc.Container(
        fluid=True, p="md",
        children=[
            create_smart_modal("col-modal"),
            *refresh,
            filters,
            html.Div(id="admin-collection-body", children=get_skeleton(SCREEN_ID))
        ]
    )

FILTER_IDS = ["col-year", "col-month", "col-empresa", "col-tipo-op", "col-cliente"]
data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID, body_output_id="admin-collection-body",
    render_body=_render_collection_body, filter_ids=FILTER_IDS
)
register_modal_callback("col-modal", WIDGET_REGISTRY, SCREEN_ID)