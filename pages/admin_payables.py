from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from strategies.admin import (
    AdminRichKPIStrategy, PayablesGaugeStrategy, PayablesComparisonStrategy,
    PayablesMixStrategy, SupplierSaldoStrategy, PayablesAgingTableStrategy
)

dash.register_page(__name__, path="/admin-payables", title="Cuentas por Pagar")

SCREEN_ID = "admin-payables"

table_pay_aging = PayablesAgingTableStrategy()

kpi_pay_initial = SmartWidget("kp_initial", AdminRichKPIStrategy("cuentas_por_pagar", "initial_balance", "Saldo Inicial", "tabler:database-import", "indigo", sub_section="acumulado"))
kpi_pay_cxp = SmartWidget("kp_cxp", AdminRichKPIStrategy("cuentas_por_pagar", "accounts_payable", "CxP Mes", "tabler:file-invoice", "indigo", sub_section="acumulado"))
kpi_pay_credit = SmartWidget("kp_credit", AdminRichKPIStrategy("cuentas_por_pagar", "credit_notes_payable", "Notas Crédito", "tabler:file-minus", "red", sub_section="acumulado"))
kpi_pay_advances = SmartWidget("kp_advances", AdminRichKPIStrategy("cuentas_por_pagar", "advance_payment", "Anticipos", "tabler:cash-banknote", "green", sub_section="acumulado"))
kpi_pay_payments = SmartWidget("kp_payments", AdminRichKPIStrategy("cuentas_por_pagar", "supplier_payments", "Pagado", "tabler:cash", "teal", sub_section="acumulado"))
kpi_pay_balance = SmartWidget("kp_balance", AdminRichKPIStrategy("cuentas_por_pagar", "total_accounts_payable", "Saldo Final", "tabler:scale", "orange", sub_section="acumulado"))

w_gauge_cxp = SmartWidget("pg_cxp", PayablesGaugeStrategy("Saldo CxP", "total_accounts_payable", "red"))
w_gauge_vs = SmartWidget("pg_vs", PayablesGaugeStrategy("CxP vs Pagado", "accounts_payable_vs_paid", "orange"))
w_gauge_days = SmartWidget("pg_days", PayablesGaugeStrategy("Promedio Pago", "average_payment_days_payable", "blue"))

chart_pay_comp_strat = PayablesComparisonStrategy()
chart_pay_comp = ChartWidget("cp_comp", chart_pay_comp_strat)
chart_pay_mix = ChartWidget("cp_mix", PayablesMixStrategy())
chart_supp_saldo = ChartWidget("cp_supp", SupplierSaldoStrategy())

WIDGET_REGISTRY = {
    "kp_initial": kpi_pay_initial, "kp_cxp": kpi_pay_cxp,
    "kp_credit": kpi_pay_credit, "kp_advances": kpi_pay_advances,
    "kp_payments": kpi_pay_payments, "kp_balance": kpi_pay_balance
}

def _render_payables_body(ctx):
    return html.Div([
        dmc.SimpleGrid(cols={"base": 2, "md": 3, "lg": 6}, spacing="sm", mb="md", children=[  # type: ignore
            kpi_pay_initial.render(ctx), kpi_pay_cxp.render(ctx),
            kpi_pay_credit.render(ctx), kpi_pay_advances.render(ctx),
            kpi_pay_payments.render(ctx), kpi_pay_balance.render(ctx),
        ]),

        dmc.SimpleGrid(cols={"base": 1, "sm": 3}, spacing="md", mb="md", children=[  # type: ignore
            w_gauge_cxp.render(ctx), w_gauge_vs.render(ctx), w_gauge_days.render(ctx)
        ]),

          dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Group([
                        dmc.Text("Evolución de Pagos", fw="bold", size="lg"),
                        dmc.SegmentedControl(
                            id="pay-comp-selector",
                            value="mensual",
                            data=[
                                {"label": "Mensual", "value": "mensual"},
                                {"label": "Acumulado", "value": "acumulado"}
                            ],
                            size="xs"
                        )
                    ], justify="space-between", mb="md"),
                    html.Div(id="pay-comp-dynamic-container", children=chart_pay_comp.render(ctx))
                ])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_pay_mix.render(ctx)])
            ]),
        ]),
          
        dmc.Grid(gutter="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Saldo por Proveedor (Top 10)", fw="bold", size="lg", mb="md"),
                    chart_supp_saldo.render(ctx)
                ])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Antigüedad de Saldos", fw="bold", size="lg", mb="md"),
                    table_pay_aging.render(ctx)
                ])
            ]),
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)[0]
    return dmc.Container(fluid=True, p="md", children=[
        dmc.Modal(id="pay-smart-modal", size="xl", centered=True, children=[html.Div(id="pay-modal-content")]),
        *refresh,
        html.Div(id="admin-payables-body", children=_render_payables_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(SCREEN_ID, "admin-payables-body", _render_payables_body)

@callback(
    Output("pay-comp-dynamic-container", "children"),
    Input("pay-comp-selector", "value"),
    prevent_initial_call=True
)
def update_pay_comparison_chart(selected_view):
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True)
    fig = chart_pay_comp_strat.get_figure(ctx, view=selected_view)
    return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={"height": "400px"})

@callback(
    Output("pay-smart-modal", "opened"), Output("pay-smart-modal", "title"), Output("pay-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_payables_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    triggered_id = dash.ctx.triggered_id
    if not triggered_id: return no_update, no_update, no_update
    w_id = triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    return True, widget.strategy.get_title(ctx), widget.strategy.render_detail(ctx)