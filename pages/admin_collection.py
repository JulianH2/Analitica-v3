from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.admin import (
    AdminRichKPIStrategy, CollectionGaugeStrategy,
    CollectionComparisonStrategy, CollectionMixStrategy,
    DebtorsStackedStrategy, CollectionAgingTableStrategy
)

dash.register_page(__name__, path="/admin-collection", title="Cobranza")

SCREEN_ID = "admin-collection"

table_aging = CollectionAgingTableStrategy()

kpi_billing = SmartWidget("ka_billing", AdminRichKPIStrategy("facturacion_cobranza", "accumulated_billed", "Facturado", "tabler:file-invoice", "indigo", sub_section="acumulado"))
kpi_credit = SmartWidget("ka_credit", AdminRichKPIStrategy("facturacion_cobranza", "accumulated_credit_notes", "Notas Crédito", "tabler:file-minus", "red", sub_section="acumulado"))
kpi_debit = SmartWidget("ka_debit", AdminRichKPIStrategy("facturacion_cobranza", "accumulated_debit_notes", "Notas Cargo", "tabler:file-plus", "gray", sub_section="acumulado"))
kpi_payments = SmartWidget("ka_payments", AdminRichKPIStrategy("facturacion_cobranza", "accumulated_collected", "Cobrado", "tabler:cash", "green", sub_section="acumulado"))
kpi_portfolio = SmartWidget("ka_portfolio", AdminRichKPIStrategy("facturacion_cobranza", "customer_portfolio", "Cartera Total", "tabler:briefcase", "blue", sub_section="acumulado"))

w_gauge_port = SmartWidget("col_gauge_p", CollectionGaugeStrategy("Cartera Clientes", "customer_portfolio", "indigo"))
w_gauge_net = SmartWidget("col_gauge_n", CollectionGaugeStrategy("Saldo Neto", "customer_portfolio", "teal"))
w_gauge_comp = SmartWidget("col_gauge_c", CollectionGaugeStrategy("Facturado vs Cobrado", "billed_vs_collected", "orange" ))
w_gauge_days = SmartWidget("col_gauge_d", CollectionGaugeStrategy("Días Cartera", "average_payment_days", "red"))

chart_comp = ChartWidget("cc_comp", CollectionComparisonStrategy())
chart_mix = ChartWidget("cc_mix", CollectionMixStrategy())
chart_debtors = ChartWidget("cc_debtors", DebtorsStackedStrategy())

WIDGET_REGISTRY = {
    "ka_billing": kpi_billing,
    "ka_credit": kpi_credit,
    "ka_debit": kpi_debit,
    "ka_payments": kpi_payments,
    "ka_portfolio": kpi_portfolio
}

def _render_collection_body(ctx):
    return html.Div([
        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 2, "xl": 2}, children=[kpi_billing.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 2, "xl": 2}, children=[kpi_credit.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 2, "xl": 2}, children=[kpi_debit.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3, "xl": 3}, children=[kpi_payments.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3, "xl": 3}, children=[kpi_portfolio.render(ctx)]), # type: ignore
        ]),

        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="md", mb="md", children=[ # type: ignore
            w_gauge_port.render(ctx), w_gauge_net.render(ctx), w_gauge_comp.render(ctx), w_gauge_days.render(ctx)
        ]),

        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_comp.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_mix.render(ctx)])
            ]),
        ]),

        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Top Deudores", fw="bold", size="lg", mb="md"),
                    chart_debtors.render(ctx)
                ])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Antigüedad de Saldos", fw="bold", size="lg", mb="md"),
                    table_aging.render(ctx)
                ])
            ]),
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ids = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, p="md", children=[
        dmc.Modal(id="col-smart-modal", size="xl", centered=True, children=[html.Div(id="col-modal-content")]),
        *refresh_components,
        html.Div(id="admin-collection-body", children=_render_collection_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="admin-collection-body", render_body=_render_collection_body)

@callback(
    Output("col-smart-modal", "opened"), Output("col-smart-modal", "title"), Output("col-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_collection_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if not dash.ctx.triggered_id: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    return True, widget.strategy.get_title(ctx), widget.strategy.render_detail(ctx)