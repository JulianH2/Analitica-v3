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

kpi_billing = SmartWidget("ka_billing", AdminRichKPIStrategy("facturacion_cobranza", "facturado_acumulado", "Facturado", "tabler:file-invoice", "indigo", sub_section="acumulado"))
kpi_credit = SmartWidget("ka_credit", AdminRichKPIStrategy("facturacion_cobranza", "notas_credito_acumulado", "Notas Crédito", "tabler:file-minus", "red", sub_section="acumulado"))
kpi_debit = SmartWidget("ka_debit", AdminRichKPIStrategy("facturacion_cobranza", "notas_cargo", "Notas Cargo", "tabler:file-plus", "gray", sub_section="acumulado"))
kpi_payments = SmartWidget("ka_payments", AdminRichKPIStrategy("facturacion_cobranza", "cobrado_acumulado", "Cobrado", "tabler:cash", "green", sub_section="acumulado"))
kpi_portfolio = SmartWidget("ka_portfolio", AdminRichKPIStrategy("facturacion_cobranza", "cartera_clientes", "Cartera", "tabler:users", "yellow", sub_section="acumulado"))
kpi_balance = SmartWidget("ka_balance", AdminRichKPIStrategy("facturacion_cobranza", "saldo_neto", "Saldo Neto", "tabler:calculator", "indigo", sub_section="acumulado"))

gauge_eff = ChartWidget("gc_billing", CollectionGaugeStrategy("Eficiencia de Cobro", "facturado_vs_cobrado", "facturado_vs_cobrado", "indigo"))
gauge_days = ChartWidget("gc_days", CollectionGaugeStrategy("Días de Cartera", "prom_dias_cartera", "prom_dias_cartera", "yellow", prefix=""))
chart_mix = ChartWidget("cc_mix", CollectionMixStrategy())

chart_stack = ChartWidget("cc_stack", DebtorsStackedStrategy())
chart_comp = ChartWidget("cc_comp", CollectionComparisonStrategy())
table_aging = TableWidget(CollectionAgingTableStrategy())

WIDGET_REGISTRY = {
    "ka_billing": kpi_billing, "ka_credit": kpi_credit, "ka_debit": kpi_debit,
    "ka_payments": kpi_payments, "ka_portfolio": kpi_portfolio, "ka_balance": kpi_balance,
    "gc_billing": gauge_eff, "gc_days": gauge_days, "cc_mix": chart_mix,
    "cc_stack": chart_stack, "cc_comp": chart_comp
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    ctx = data_manager.get_data("administracion")

    return dmc.Container(fluid=True, p="md", children=[
        dmc.Modal(id="col-smart-modal", size="xl", centered=True, children=[html.Div(id="col-modal-content")]),

        dmc.SimpleGrid(cols={"base": 2, "sm": 3, "lg": 6}, spacing="sm", mb="xl", children=[ # type: ignore
            kpi_billing.render(ctx), kpi_credit.render(ctx), kpi_debit.render(ctx),
            kpi_payments.render(ctx), kpi_portfolio.render(ctx), kpi_balance.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[gauge_eff.render(ctx, h=320)]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[gauge_days.render(ctx, h=320)]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_mix.render(ctx, h=320)]), # type: ignore
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "lg": 7}, children=[ # type: ignore
                table_aging.render(ctx, title="ANTIGÜEDAD DE SALDOS POR CLIENTE")
            ]),
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[chart_stack.render(ctx, h=550)]), # type: ignore
        ]),

        dmc.Grid(children=[
            dmc.GridCol(span=12, children=[chart_comp.render(ctx, h=400)])
        ]),

        dmc.Space(h=60)
    ])

@callback(
    Output("col-smart-modal", "opened"),
    Output("col-smart-modal", "title"),
    Output("col-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_collection_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update
    
    if not dash.ctx.triggered_id:
        return no_update, no_update, no_update
    
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    
    if widget:
        ctx = data_manager.get_data("administracion")
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    
    return no_update, no_update, no_update