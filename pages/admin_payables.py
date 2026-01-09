from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, PayablesGaugeStrategy, PayablesComparisonStrategy,
    PayablesMixStrategy, SupplierSaldoStrategy, PayablesAgingTableStrategy
)

dash.register_page(__name__, path='/admin-payables', title='Cuentas por Pagar')
data_manager = DataManager()

gauge_pay_efficiency = ChartWidget("gp_efficiency", PayablesGaugeStrategy("CXP vs Pagado", "cxp_vs_pagado", "cxp_vs_pagado", "indigo"))
gauge_pay_timing = ChartWidget("gp_timing", PayablesGaugeStrategy("Promedio Días Pago", "promedio_pago", "promedio_pago", "yellow"))

kpi_pay_acc_initial = SmartWidget("kp_initial", AdminRichKPIStrategy("cuentas_por_pagar", "saldo_inicial", "Saldo Inicial", "tabler:database-import", "indigo", sub_section="acumulado"))
kpi_pay_acc_cxp = SmartWidget("kp_cxp", AdminRichKPIStrategy("cuentas_por_pagar", "cxp", "CxP", "tabler:file-invoice", "indigo", sub_section="acumulado"))
kpi_pay_acc_debit = SmartWidget("kp_debit", AdminRichKPIStrategy("cuentas_por_pagar", "notas_cargo", "Notas Cargo", "tabler:file-plus", "gray", sub_section="acumulado"))
kpi_pay_acc_credit = SmartWidget("kp_credit", AdminRichKPIStrategy("cuentas_por_pagar", "notas_credito", "Notas Crédito", "tabler:file-minus", "red", sub_section="acumulado"))
kpi_pay_acc_advances = SmartWidget("kp_advances", AdminRichKPIStrategy("cuentas_por_pagar", "anticipo", "Anticipo", "tabler:receipt-2", "green", sub_section="acumulado"))
kpi_pay_acc_total = SmartWidget("kp_total", AdminRichKPIStrategy("cuentas_por_pagar", "cxp_total", "CxP Total", "tabler:sum", "indigo", sub_section="acumulado"))
kpi_pay_acc_payments = SmartWidget("kp_payments", AdminRichKPIStrategy("cuentas_por_pagar", "pago_proveedores", "Pago Proveedores", "tabler:truck-delivery", "green", sub_section="acumulado"))
kpi_pay_acc_balance = SmartWidget("kp_balance", AdminRichKPIStrategy("cuentas_por_pagar", "saldo", "Saldo", "tabler:wallet", "yellow", sub_section="acumulado"))

chart_pay_mix = ChartWidget("cp_mix", PayablesMixStrategy())
chart_pay_supplier_stack = ChartWidget("cp_stack", SupplierSaldoStrategy())
chart_pay_comparison = ChartWidget("cp_comp", PayablesComparisonStrategy())
table_pay_aging = TableWidget(PayablesAgingTableStrategy())

WIDGET_REGISTRY = {
    "gp_efficiency": gauge_pay_efficiency, 
    "gp_timing": gauge_pay_timing,
    "kp_initial": kpi_pay_acc_initial, 
    "kp_cxp": kpi_pay_acc_cxp,
    "kp_debit": kpi_pay_acc_debit, 
    "kp_credit": kpi_pay_acc_credit,
    "kp_advances": kpi_pay_acc_advances, 
    "kp_total": kpi_pay_acc_total, 
    "kp_payments": kpi_pay_acc_payments, 
    "kp_balance": kpi_pay_acc_balance,
    "cp_mix": chart_pay_mix, 
    "cp_stack": chart_pay_supplier_stack, 
    "cp_comp": chart_pay_comparison
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="pay-smart-modal", size="lg", centered=True, children=[html.Div(id="pay-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 6}, spacing="xs", children=[# type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["09-Sep"], value="09-Sep", size="xs"),
                dmc.Select(label="Empresa Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Proveedor", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Proveedor", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Concepto Proveedor", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.Text("INDICADORES CLAVE", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "md": 2}, spacing="lg", mb="xl", children=[# type: ignore
            gauge_pay_efficiency.render(ctx), gauge_pay_timing.render(ctx)
        ]),

        dmc.Text("RESUMEN ACUMULADO", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "md": 4}, spacing="sm", mb="xl", children=[# type: ignore
            kpi_pay_acc_initial.render(ctx), kpi_pay_acc_cxp.render(ctx), 
            kpi_pay_acc_debit.render(ctx), kpi_pay_acc_credit.render(ctx),
            kpi_pay_acc_advances.render(ctx), kpi_pay_acc_total.render(ctx), 
            kpi_pay_acc_payments.render(ctx), kpi_pay_acc_balance.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_pay_mix.render(ctx)]),# type: ignore
            dmc.GridCol(span={"base": 12, "md": 8}, children=[chart_pay_supplier_stack.render(ctx)]),# type: ignore
        ]),

        table_pay_aging.render(ctx, title="ANTIGÜEDAD DE SALDOS"),
        dmc.Paper(p="md", withBorder=True, mt="lg", children=[chart_pay_comparison.render(ctx)]),
        dmc.Space(h=50)
    ])

@callback(
    Output("pay-smart-modal", "opened"),
    Output("pay-smart-modal", "title"),
    Output("pay-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_payables_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]# type: ignore
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update