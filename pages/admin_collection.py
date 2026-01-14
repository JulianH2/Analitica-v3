from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, CollectionGaugeStrategy, 
    CollectionComparisonStrategy, CollectionMixStrategy, 
    DebtorsStackedStrategy, CollectionAgingTableStrategy
)

dash.register_page(__name__, path='/admin-collection', title='Cobranza')
data_manager = DataManager()

gauge_col_billing_vs_payment = ChartWidget("gc_billing", CollectionGaugeStrategy("Facturado vs Cobrado", "facturado_vs_cobrado", "facturado_vs_cobrado", "indigo"))
gauge_col_portfolio_days = ChartWidget("gc_days", CollectionGaugeStrategy("Prom Días Cartera", "prom_dias_cartera", "prom_dias_cartera", "yellow"))

kpi_col_acc_billing = SmartWidget("ka_billing", AdminRichKPIStrategy("facturacion_cobranza", "facturado_acumulado", "Facturado Acumulado", "tabler:file-invoice", "indigo", sub_section="acumulado"))
kpi_col_acc_credit_notes = SmartWidget("ka_credit", AdminRichKPIStrategy("facturacion_cobranza", "notas_credito_acumulado", "Notas Crédito Acum.", "tabler:file-minus", "red", sub_section="acumulado"))
kpi_col_acc_debit_notes = SmartWidget("ka_debit", AdminRichKPIStrategy("facturacion_cobranza", "notas_cargo", "Notas Cargo", "tabler:file-plus", "gray", sub_section="acumulado"))
kpi_col_acc_payments = SmartWidget("ka_payments", AdminRichKPIStrategy("facturacion_cobranza", "cobrado_acumulado", "Cobrado Acumulado", "tabler:cash", "green", sub_section="acumulado"))
kpi_col_acc_portfolio = SmartWidget("ka_portfolio", AdminRichKPIStrategy("facturacion_cobranza", "cartera_clientes", "Cartera de Clientes", "tabler:users", "yellow", sub_section="acumulado"))

kpi_col_mon_billing = SmartWidget("km_billing", AdminRichKPIStrategy("facturacion_cobranza", "facturado_mes", "Facturado Mes", "tabler:calendar-event", "indigo", sub_section="mensual"))
kpi_col_mon_credit = SmartWidget("km_credit", AdminRichKPIStrategy("facturacion_cobranza", "credito", "Crédito (Mes)", "tabler:arrow-down-right", "red", sub_section="mensual"))
kpi_col_mon_debit = SmartWidget("km_debit", AdminRichKPIStrategy("facturacion_cobranza", "cargo", "Cargo (Mes)", "tabler:arrow-up-right", "indigo", sub_section="mensual"))
kpi_col_mon_payments = SmartWidget("km_payments", AdminRichKPIStrategy("facturacion_cobranza", "cobrado", "Cobrado (Mes)", "tabler:wallet", "green", sub_section="mensual"))

chart_col_yearly_comp = ChartWidget("cc_comp", CollectionComparisonStrategy())
chart_col_portfolio_mix = ChartWidget("cc_mix", CollectionMixStrategy())
chart_col_debtors_stack = ChartWidget("cc_stack", DebtorsStackedStrategy())
table_col_aging_detail = TableWidget(CollectionAgingTableStrategy())

WIDGET_REGISTRY = {
    "gc_billing": gauge_col_billing_vs_payment, "gc_days": gauge_col_portfolio_days,
    "ka_billing": kpi_col_acc_billing, "ka_credit": kpi_col_acc_credit_notes,
    "ka_debit": kpi_col_acc_debit_notes, "ka_payments": kpi_col_acc_payments,
    "ka_portfolio": kpi_col_acc_portfolio, "km_billing": kpi_col_mon_billing,
    "km_credit": kpi_col_mon_credit, "km_debit": kpi_col_mon_debit,
    "km_payments": kpi_col_mon_payments, "cc_comp": chart_col_yearly_comp,
    "cc_mix": chart_col_portfolio_mix, "cc_stack": chart_col_debtors_stack
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data("administracion")
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="col-smart-modal", size="lg", centered=True, children=[html.Div(id="col-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 5}, spacing="xs", children=[# type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["09-Sep"], value="09-Sep", size="xs"),
                dmc.Select(label="Empresa Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Cliente", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Operación", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.Text("INDICADORES CLAVE", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "md": 2}, spacing="lg", mb="xl", children=[# type: ignore
            gauge_col_billing_vs_payment.render(ctx), gauge_col_portfolio_days.render(ctx)
        ]),

        dmc.Text("ACUMULADO", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "sm": 3, "md": 5}, spacing="sm", mb="xl", children=[# type: ignore
            kpi_col_acc_billing.render(ctx), kpi_col_acc_credit_notes.render(ctx), 
            kpi_col_acc_debit_notes.render(ctx), kpi_col_acc_payments.render(ctx), 
            kpi_col_acc_portfolio.render(ctx)
        ]),

        dmc.Text("MENSUAL", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "md": 4}, spacing="sm", mb="xl", children=[# type: ignore
            kpi_col_mon_billing.render(ctx), kpi_col_mon_credit.render(ctx), 
            kpi_col_mon_debit.render(ctx), kpi_col_mon_payments.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_col_portfolio_mix.render(ctx)]),# type: ignore
            dmc.GridCol(span={"base": 12, "md": 8}, children=[chart_col_debtors_stack.render(ctx)])# type: ignore
        ]),

        table_col_aging_detail.render(ctx, title="ANTIGÜEDAD DE SALDOS POR ÁREA"),
        dmc.Paper(p="md", withBorder=True, mt="lg", children=[chart_col_yearly_comp.render(ctx)]),
        dmc.Space(h=50)
    ])

@callback(
    Output("col-smart-modal", "opened"), 
    Output("col-smart-modal", "title"), 
    Output("col-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), 
    prevent_initial_call=True
)
def handle_collection_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data("administracion")
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg["title"], widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update