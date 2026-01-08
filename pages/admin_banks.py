from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, BankDailyEvolutionStrategy, 
    BankDonutStrategy, BankConceptsStrategy
)

dash.register_page(__name__, path='/admin-banks', title='Bancos')
data_manager = DataManager()

kpi_bank_initial_balance = SmartWidget("kb_initial", AdminRichKPIStrategy("bancos", "saldo_inicial", "Saldo Inicial Consolidado", "tabler:wallet", "gray"))
kpi_bank_total_incomes = SmartWidget("kb_incomes", AdminRichKPIStrategy("bancos", "ingresos", "Ingresos Consolidado", "tabler:trending-up", "green"))
kpi_bank_total_expenses = SmartWidget("kb_expenses", AdminRichKPIStrategy("bancos", "egresos", "Egresos Consolidado", "tabler:trending-down", "red"))
kpi_bank_final_balance = SmartWidget("kb_final", AdminRichKPIStrategy("bancos", "saldo_final", "Saldo Final Consolidado", "tabler:cash", "blue"))

chart_bank_daily_evolution = ChartWidget("cb_daily", BankDailyEvolutionStrategy())
chart_bank_institutions_donut = ChartWidget("cb_donut", BankDonutStrategy())
table_bank_concepts_detail = TableWidget(BankConceptsStrategy())

WIDGET_REGISTRY = {
    "kb_initial": kpi_bank_initial_balance,
    "kb_incomes": kpi_bank_total_incomes,
    "kb_expenses": kpi_bank_total_expenses,
    "kb_final": kpi_bank_final_balance,
    "cb_daily": chart_bank_daily_evolution,
    "cb_donut": chart_bank_institutions_donut
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="bank-smart-modal", size="lg", centered=True, children=[html.Div(id="bank-modal-content")]),
        
        dmc.Title("Administración - Bancos", order=3, mb="lg"),
        
        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "md": 4}, spacing="lg", mb="xl", children=[
            kpi_bank_initial_balance.render(ctx), 
            kpi_bank_total_incomes.render(ctx), 
            kpi_bank_total_expenses.render(ctx), 
            kpi_bank_final_balance.render(ctx)
        ]),

        dmc.Paper(p="md", withBorder=True, mb="lg", children=[chart_bank_daily_evolution.render(ctx)]),
        
        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_bank_institutions_donut.render(ctx)]),
            dmc.GridCol(span={"base": 12, "md": 8}, children=[
                table_bank_concepts_detail.render(ctx, title="Ingresos y Egresos por Concepto")
            ])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("bank-smart-modal", "opened"), 
    Output("bank-smart-modal", "title"), 
    Output("bank-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), 
    prevent_initial_call=True
)
def handle_bank_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg["title"], widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update