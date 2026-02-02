from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.administration import (
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
    filter_content = html.Div([
        dmc.Grid(align="center", gutter="sm", mb="xs", children=[
            dmc.GridCol(span="content", children=[
                dmc.Select(id="bank-year-filter", data=["2025", "2024"], value="2025", variant="filled", style={"width": "100px"}, allowDeselect=False, size="sm")
            ]),
            dmc.GridCol(span="auto", children=[
                dmc.ScrollArea(w="100%", type="scroll", scrollbarSize=6, offsetScrollbars=True, children=[ # type: ignore
                    dmc.SegmentedControl(
                        id="bank-month-filter", value="septiembre", color="blue", radius="md", size="sm", fullWidth=True, style={"minWidth": "800px"},
                        data=[{"label": m, "value": m.lower()} for m in ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]] # type: ignore
                    )
                ])
            ])
        ]),
        dmc.SimpleGrid(cols={"base": 2, "md": 4}, spacing="xs", children=[ # type: ignore
            dmc.Select(label="Empresa Área", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Institución Bancaria", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
        ])
    ])

    collapsible_filters = dmc.Accordion(
        value="filtros", variant="contained", radius="md", mb="lg",
        children=[
            dmc.AccordionItem(value="filtros", children=[
                dmc.AccordionControl(dmc.Group([DashIconify(icon="tabler:filter"), dmc.Text("Filtros y Controles")]), h=40),
                dmc.AccordionPanel(filter_content)
            ])
        ]
    )

    return html.Div([
        dmc.Title("Administración - Bancos", order=3, mb="lg"),

        collapsible_filters,

        dmc.Grid(gutter="md", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_initial.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_incomes.render(ctx)]),   # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_expenses.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "sm": 6, "lg": 3}, children=[kpi_bank_final.render(ctx)]),     # type: ignore
        ]),

        dmc.Paper(p="md", withBorder=True, mb="lg", children=[chart_bank_daily.render(ctx, h=400)]),

        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[chart_bank_donut.render(ctx, h=420)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 8}, children=[table_bank_concepts.render(ctx, title="Ingresos y Egresos por Concepto")]) # type: ignore
        ]),
        dmc.Space(h=50),
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
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)