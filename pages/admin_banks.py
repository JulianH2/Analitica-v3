from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.admin import (
    AdminRichKPIStrategy, BankDailyEvolutionStrategy,
    BankDonutStrategy, BankConceptsStrategy
)

dash.register_page(__name__, path="/admin-banks", title="Bancos")

SCREEN_ID = "admin-banks"

table_bank_concepts = BankConceptsStrategy()

kpi_bank_initial = SmartWidget("kb_initial", AdminRichKPIStrategy("bancos", "initial_balance", "Saldo Inicial Consolidado", "tabler:wallet", "gray"))
kpi_bank_incomes  = SmartWidget("kb_incomes", AdminRichKPIStrategy("bancos", "monthly_collected", "Ingresos Consolidado", "tabler:trending-up", "green"))
kpi_bank_expenses = SmartWidget("kb_expenses", AdminRichKPIStrategy("bancos", "supplier_payments", "Egresos Consolidado", "tabler:trending-down", "red"))
kpi_bank_final    = SmartWidget("kb_final", AdminRichKPIStrategy("bancos", "final_balance", "Saldo Final Consolidado", "tabler:cash", "indigo"))

chart_bank_daily = ChartWidget("cb_daily", BankDailyEvolutionStrategy())
chart_bank_donut = ChartWidget("cb_donut", BankDonutStrategy())

WIDGET_REGISTRY = {
    "kb_initial": kpi_bank_initial,
    "kb_incomes": kpi_bank_incomes,
    "kb_expenses": kpi_bank_expenses,
    "kb_final": kpi_bank_final
}

def _render_admin_banks_body(ctx):
    return html.Div([
        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_initial.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_incomes.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_expenses.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_final.render(ctx)]), # type: ignore
        ]),

        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_bank_daily.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_bank_donut.render(ctx)])
            ]),
        ]),

        dmc.Paper(p="md", withBorder=True, radius="md", children=[
            dmc.Text("Desglose por Conceptos", fw="bold", size="lg", mb="md"),
            table_bank_concepts.render(ctx) 
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ids = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, p="md", children=[
        dmc.Modal(id="bank-smart-modal", size="lg", centered=True, children=[html.Div(id="bank-modal-content")]),
        *refresh_components,
        html.Div(id="admin-banks-body", children=_render_admin_banks_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="admin-banks-body", render_body=_render_admin_banks_body)

@callback(
    Output("bank-smart-modal", "opened"),
    Output("bank-smart-modal", "title"),
    Output("bank-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def handle_bank_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if not dash.ctx.triggered_id: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if not widget: return no_update, no_update, no_update

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    return True, widget.strategy.get_title(ctx), widget.strategy.render_detail(ctx)