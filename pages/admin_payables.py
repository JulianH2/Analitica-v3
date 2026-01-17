from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager  # singleton
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, PayablesGaugeStrategy, PayablesComparisonStrategy,
    PayablesMixStrategy, SupplierSaldoStrategy, PayablesAgingTableStrategy
)

dash.register_page(__name__, path="/admin-payables", title="Cuentas por Pagar")

SCREEN_ID = "admin-payables"

kpi_pay_initial = SmartWidget("kp_initial", AdminRichKPIStrategy("cuentas_por_pagar", "saldo_inicial", "Saldo Inicial", "tabler:database-import", "indigo", sub_section="acumulado"))
kpi_pay_cxp = SmartWidget("kp_cxp", AdminRichKPIStrategy("cuentas_por_pagar", "cxp", "CxP Mes", "tabler:file-invoice", "indigo", sub_section="acumulado"))
kpi_pay_credit = SmartWidget("kp_credit", AdminRichKPIStrategy("cuentas_por_pagar", "notas_credito", "Notas Crédito", "tabler:file-minus", "red", sub_section="acumulado"))
kpi_pay_advances = SmartWidget("kp_advances", AdminRichKPIStrategy("cuentas_por_pagar", "anticipo", "Anticipos", "tabler:receipt-2", "green", sub_section="acumulado"))
kpi_pay_payments = SmartWidget("kp_payments", AdminRichKPIStrategy("cuentas_por_pagar", "pago_proveedores", "Pagos", "tabler:truck-delivery", "green", sub_section="acumulado"))
kpi_pay_balance = SmartWidget("kp_balance", AdminRichKPIStrategy("cuentas_por_pagar", "saldo", "Saldo Final", "tabler:wallet", "yellow", sub_section="acumulado"))

gauge_pay_eff = ChartWidget("gp_eff", PayablesGaugeStrategy("CXP vs Pagado", "cxp_vs_pagado", "cxp_vs_pagado", "indigo"))
gauge_pay_days = ChartWidget("gp_days", PayablesGaugeStrategy("Días Pago", "promedio_pago", "promedio_pago", "yellow", prefix=""))
chart_pay_mix = ChartWidget("cp_mix", PayablesMixStrategy())

chart_pay_stack = ChartWidget("cp_stack", SupplierSaldoStrategy())
chart_pay_comp = ChartWidget("cp_comp", PayablesComparisonStrategy())
table_pay_aging = TableWidget(PayablesAgingTableStrategy())

WIDGET_REGISTRY = {
    "kp_initial": kpi_pay_initial, "kp_cxp": kpi_pay_cxp, "kp_credit": kpi_pay_credit,
    "kp_advances": kpi_pay_advances, "kp_payments": kpi_pay_payments, "kp_balance": kpi_pay_balance,
    "gp_eff": gauge_pay_eff, "gp_days": gauge_pay_days, "cp_mix": chart_pay_mix,
    "cp_stack": chart_pay_stack, "cp_comp": chart_pay_comp
}


def _render_payables_body(ctx):
    return html.Div([
        dmc.SimpleGrid(cols={"base": 2, "sm": 3, "lg": 6}, spacing="sm", mb="xl", children=[  # type: ignore
            kpi_pay_initial.render(ctx), kpi_pay_cxp.render(ctx), kpi_pay_credit.render(ctx),
            kpi_pay_advances.render(ctx), kpi_pay_payments.render(ctx), kpi_pay_balance.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[gauge_pay_eff.render(ctx, h=320)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[gauge_pay_days.render(ctx, h=320)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_pay_mix.render(ctx, h=320)]),  # type: ignore
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "lg": 7}, children=[  # type: ignore
                table_pay_aging.render(ctx, title="ANTIGÜEDAD DE SALDOS POR PROVEEDOR")
            ]),
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[chart_pay_stack.render(ctx, h=550)]),  # type: ignore
        ]),

        dmc.Grid(children=[
            dmc.GridCol(span=12, children=[chart_pay_comp.render(ctx, h=400)])
        ]),

        dmc.Space(h=60)
    ])


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    # primer paint rápido (base/cache slice)
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    # auto-refresh 1 vez al entrar (sin duplicar)
    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, p="md", children=[
        dmc.Modal(id="pay-smart-modal", size="xl", centered=True, children=[html.Div(id="pay-modal-content")]),

        *refresh_components,

        html.Div(id="admin-payables-body", children=_render_payables_body(ctx)),
    ])


# callbacks estándar (Interval -> refresh async; token -> rerender sync)
data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="admin-payables-body",
    render_body=_render_payables_body,
)


@callback(
    Output("pay-smart-modal", "opened"),
    Output("pay-smart-modal", "title"),
    Output("pay-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_payables_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update

    triggered_id = dash.ctx.triggered_id
    if not triggered_id:
        return no_update, no_update, no_update

    w_id = triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget:
        return no_update, no_update, no_update

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)