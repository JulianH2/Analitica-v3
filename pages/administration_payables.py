from flask import session
import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_filter_section
from strategies.administration import (
    AdminKPIStrategy, AdminGaugeStrategy,
    AdminTrendChartStrategy, AdminDonutChartStrategy,
    AdminStackedBarStrategy, AdminTableStrategy
)

dash.register_page(__name__, path="/admin-payables", title="Cuentas por Pagar")

SCREEN_ID = "administration-payables"

kpi_pay_initial = SmartWidget(
    "kp_initial",
    AdminKPIStrategy(SCREEN_ID, "initial_balance", "Saldo Inicial", "tabler:database-import", "indigo")
)
kpi_pay_cxp = SmartWidget(
    "kp_cxp",
    AdminKPIStrategy(SCREEN_ID, "accounts_payable", "CxP Mes", "tabler:file-invoice", "indigo")
)
kpi_pay_credit = SmartWidget(
    "kp_credit",
    AdminKPIStrategy(SCREEN_ID, "credit_notes", "Notas Crédito", "tabler:file-minus", "red")
)
kpi_pay_advances = SmartWidget(
    "kp_advances",
    AdminKPIStrategy(SCREEN_ID, "advances", "Anticipos", "tabler:receipt-2", "green")
)
kpi_pay_payments = SmartWidget(
    "kp_payments",
    AdminKPIStrategy(SCREEN_ID, "supplier_payments", "Pagos", "tabler:truck-delivery", "green")
)
kpi_pay_balance = SmartWidget(
    "kp_balance",
    AdminKPIStrategy(SCREEN_ID, "final_balance", "Saldo Final", "tabler:wallet", "yellow")
)

gauge_pay_eff = SmartWidget(
    "gp_eff",
    AdminGaugeStrategy(SCREEN_ID, "payment_efficiency", "CXP vs Pagado", "red", icon="tabler:target")
)
gauge_pay_days = SmartWidget(
    "gp_days",
    AdminGaugeStrategy(SCREEN_ID, "average_payment_days", "Días Pago", "yellow", icon="tabler:calendar")
)

chart_pay_mix = ChartWidget(
    "cp_mix",
    AdminDonutChartStrategy(SCREEN_ID, "payables_by_status", "Distribución CxP")
)
chart_pay_stack = ChartWidget(
    "cp_stack",
    AdminStackedBarStrategy(SCREEN_ID, "suppliers_by_range", "Proveedores por Rango")
)
chart_pay_comp = ChartWidget(
    "cp_comp",
    AdminTrendChartStrategy(SCREEN_ID, "payables_trends", "Tendencia CxP", color="red")
)

WIDGET_REGISTRY = {
    "kp_initial": kpi_pay_initial,
    "kp_cxp": kpi_pay_cxp,
    "kp_credit": kpi_pay_credit,
    "kp_advances": kpi_pay_advances,
    "kp_payments": kpi_pay_payments,
    "kp_balance": kpi_pay_balance,
    "gp_eff": gauge_pay_eff,
    "gp_days": gauge_pay_days
}

def _render_payables_body(ctx):
    return html.Div([
        dmc.Title("Administración - Cuentas por Pagar", order=3, mb="lg", c="dimmed"), # type: ignore
        dmc.SimpleGrid(
            cols={"base": 2, "sm": 3, "lg": 6}, # type: ignore
            spacing="sm",
            mb="xl",
            children=[
                kpi_pay_initial.render(ctx),
                kpi_pay_cxp.render(ctx),
                kpi_pay_credit.render(ctx),
                kpi_pay_advances.render(ctx),
                kpi_pay_payments.render(ctx),
                kpi_pay_balance.render(ctx)
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(
                    span={"base": 12, "md": 6}, # type: ignore
                    children=[
                        dmc.SimpleGrid(
                            cols=2,
                            spacing="md",
                            children=[
                                gauge_pay_eff.render(ctx, mode="combined"),
                                gauge_pay_days.render(ctx, mode="combined")
                            ]
                        )
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "md": 6}, # type: ignore
                    children=[chart_pay_mix.render(ctx, h=360)]
                )
            ]
        ),
        dmc.Grid(
            gutter="lg",
            mb="xl",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 6}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            shadow="sm",
                            children=[
                                dmc.Text(
                                    "ANTIGÜEDAD DE SALDOS POR PROVEEDOR",
                                    fw="bold",
                                    size="xs",
                                    c="dimmed", # type: ignore
                                    mb="md"
                                ),
                                dmc.ScrollArea(
                                    h=460,
                                    children=[
                                        AdminTableStrategy(
                                            SCREEN_ID,
                                            "aging_by_supplier"
                                        ).render(ctx)
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 6}, # type: ignore
                    children=[chart_pay_stack.render(ctx, h=500)]
                )
            ]
        ),
        dmc.Paper(
            p="md",
            withBorder=True,
            shadow="sm",
            children=[
                dmc.Group(
                    justify="space-between",
                    mb="md",
                    children=[
                        dmc.Text(
                            "CUENTAS POR PAGAR (COMPARATIVO)",
                            fw="bold",
                            size="xs",
                            c="dimmed" # type: ignore
                        ),
                        dmc.SegmentedControl(
                            id="pay-comp-selector",
                            data=[
                                {"label": "Vista Mensual", "value": "monthly"},
                                {"label": "Vista Acumulada", "value": "cumulative"},
                                {"label": "Vista Comparativa", "value": "comparison"}
                            ], # type: ignore
                            value="monthly",
                            size="xs",
                            color="red"
                        )
                    ]
                ),
                html.Div(
                    id="pay-comp-dynamic-container",
                    children=[chart_pay_comp.render(ctx, h=400)]
                )
            ]
        ),
        dmc.Space(h=60)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    filters = create_filter_section(
        year_id="pay-year",
        month_id="pay-month",
        additional_filters=[
            {"id": "pay-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": "pay-proveedor", "label": "Proveedor", "data": ["Todas"], "value": "Todas"}
        ]
    )
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            create_smart_modal("pay-modal"),
            *refresh,
            filters,
            html.Div(
                id="admin-payables-body",
                children=_render_payables_body(ctx)
            )
        ]
    )

FILTER_IDS = ["pay-year", "pay-month", "pay-empresa", "pay-proveedor"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="admin-payables-body",
    render_body=_render_payables_body,
    filter_ids=FILTER_IDS
)

register_modal_callback("pay-modal", WIDGET_REGISTRY, SCREEN_ID)

@callback(
    Output("pay-comp-dynamic-container", "children"),
    Input("pay-comp-selector", "value"),
    prevent_initial_call=True
)
def update_pay_comparison_chart(selected_view):
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True)
    fig = chart_pay_comp.strategy.get_figure(ctx)
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False},
        style={"height": "400px"}
    )
