# pages/admin_banks.py

from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager  # <-- usa el singleton exportado
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, BankDailyEvolutionStrategy,
    BankDonutStrategy, BankConceptsStrategy
)

dash.register_page(__name__, path="/admin-banks", title="Bancos")

SCREEN_ID = "admin-banks"

kpi_bank_initial = SmartWidget("kb_initial", AdminRichKPIStrategy("bancos", "saldo_inicial", "Saldo Inicial Consolidado", "tabler:wallet", "gray"))
kpi_bank_incomes  = SmartWidget("kb_incomes", AdminRichKPIStrategy("bancos", "ingresos", "Ingresos Consolidado", "tabler:trending-up", "green"))
kpi_bank_expenses = SmartWidget("kb_expenses", AdminRichKPIStrategy("bancos", "egresos", "Egresos Consolidado", "tabler:trending-down", "red"))
kpi_bank_final    = SmartWidget("kb_final", AdminRichKPIStrategy("bancos", "saldo_final", "Saldo Final Consolidado", "tabler:cash", "indigo"))

chart_bank_daily = ChartWidget("cb_daily", BankDailyEvolutionStrategy())
chart_bank_donut = ChartWidget("cb_donut", BankDonutStrategy())
table_bank_concepts = TableWidget(BankConceptsStrategy())

WIDGET_REGISTRY = {
    "kb_initial": kpi_bank_initial,
    "kb_incomes": kpi_bank_incomes,
    "kb_expenses": kpi_bank_expenses,
    "kb_final": kpi_bank_final,
    "cb_daily": chart_bank_daily,
    "cb_donut": chart_bank_donut,
}


def _render_admin_banks_body(ctx):
    return html.Div([
        dmc.Title("Administración - Bancos", order=3, mb="lg"),

        dmc.Grid(gutter="md", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_initial.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_incomes.render(ctx)]),   # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_expenses.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_final.render(ctx)]),     # type: ignore
        ]),

        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            chart_bank_daily.render(ctx, h=400)
        ]),

        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_bank_donut.render(ctx, h=420)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 8}, children=[  # type: ignore
                table_bank_concepts.render(ctx, title="Ingresos y Egresos por Concepto")
            ])
        ]),

        dmc.Space(h=50),
    ])


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    # 1) primer paint rápido (base/cache slice)
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    # 2) Store + Interval (auto refresh 1 vez al entrar)
    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, p="md", children=[
        dmc.Modal(id="bank-smart-modal", size="lg", centered=True, children=[html.Div(id="bank-modal-content")]),

        *refresh_components,

        html.Div(id="admin-banks-body", children=_render_admin_banks_body(ctx)),
    ])


# 3) callbacks estándar: Interval -> refresh async -> token; token -> rerender sync
data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="admin-banks-body",
    render_body=_render_admin_banks_body,
)


@callback(
    Output("bank-smart-modal", "opened"),
    Output("bank-smart-modal", "title"),
    Output("bank-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def handle_bank_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update

    if not dash.ctx.triggered_id:
        return no_update, no_update, no_update

    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget:
        return no_update, no_update, no_update

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
