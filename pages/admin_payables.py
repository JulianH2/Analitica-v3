from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from components.visual_widget import ChartWidget
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

gauge_pay_eff = SmartWidget("gp_eff", PayablesGaugeStrategy("CXP vs Pagado", "cxp_vs_pagado", "red"))
gauge_pay_days = SmartWidget("gp_days", PayablesGaugeStrategy("Días Pago", "promedio_pago", "yellow", prefix=""))

chart_pay_mix = ChartWidget("cp_mix", PayablesMixStrategy())
chart_pay_stack = ChartWidget("cp_stack", SupplierSaldoStrategy())
table_pay_aging = TableWidget(PayablesAgingTableStrategy())
chart_pay_comp_strat = PayablesComparisonStrategy()

WIDGET_REGISTRY = {
    "kp_initial": kpi_pay_initial, "kp_cxp": kpi_pay_cxp, "kp_credit": kpi_pay_credit,
    "kp_advances": kpi_pay_advances, "kp_payments": kpi_pay_payments, "kp_balance": kpi_pay_balance,
    "gp_eff": gauge_pay_eff, "gp_days": gauge_pay_days
}

def _render_payables_body(ctx):
    filter_content = html.Div([
        dmc.Grid(align="center", gutter="sm", mb="xs", children=[
            dmc.GridCol(span="content", children=[
                dmc.Select(id="pay-year-filter", data=["2025", "2024"], value="2025", variant="filled", style={"width": "100px"}, allowDeselect=False, size="sm")
            ]),
            dmc.GridCol(span="auto", children=[
                dmc.ScrollArea(w="100%", type="scroll", scrollbarSize=6, offsetScrollbars=True, children=[ # type: ignore
                    dmc.SegmentedControl(
                        id="pay-month-filter", value="septiembre", color="blue", radius="md", size="sm", fullWidth=True, style={"minWidth": "800px"},
                        data=[{"label": m, "value": m.lower()} for m in ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]] # type: ignore
                    )
                ])
            ])
        ]),
        dmc.SimpleGrid(cols={"base": 2, "md": 4}, spacing="xs", children=[ # type: ignore
            dmc.Select(label="Empresa Área", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Proveedor", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Tipo Proveedor", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Concepto Proveedor", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
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
        collapsible_filters,

        dmc.SimpleGrid(cols={"base": 2, "sm": 3, "lg": 6}, spacing="sm", mb="xl", children=[  # type: ignore
            kpi_pay_initial.render(ctx), kpi_pay_cxp.render(ctx), kpi_pay_credit.render(ctx),
            kpi_pay_advances.render(ctx), kpi_pay_payments.render(ctx), kpi_pay_balance.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            
            dmc.GridCol(span={"base": 12, "md": 6, "lg": 6}, children=[ # type: ignore
                dmc.Stack(gap="md", children=[
                    gauge_pay_eff.render(ctx, mode="combined"),
                    gauge_pay_days.render(ctx, mode="combined")
                ])
            ]),

            dmc.GridCol(span={"base": 12, "md": 6, "lg": 6}, children=[ # type: ignore
                dmc.Paper(withBorder=True, p="xs", radius="md", shadow="sm", style={"height": "100%"}, children=[
                    chart_pay_mix.render(ctx, h=330) 
                ])
            ]),
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                table_pay_aging.render(ctx, title="ANTIGÜEDAD DE SALDOS POR PROVEEDOR")
            ]),
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, shadow="sm", children=[
                    chart_pay_stack.render(ctx, h=500)
                ])
            ]),
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Group(justify="space-between", mb="md", children=[
                dmc.Text("CUENTAS POR PAGAR 2025 VS. 2024", fw="bold", size="xs", c="dimmed"), # type: ignore
                dmc.SegmentedControl(
                    id="pay-comp-selector",
                    data=[
                        {"label": "Vista Mensual", "value": "monthly"},
                        {"label": "Vista Acumulada", "value": "cumulative"},
                        {"label": "Vista Comparativa", "value": "comparison"},
                    ], # type: ignore
                    value="monthly", size="xs", color="red",
                ),
            ]),
            html.Div(id="pay-comp-dynamic-container", children=chart_pay_comp_strat.get_figure_by_view(ctx, view="monthly"))
        ]),
        dmc.Space(h=60)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, p="md", children=[
        dmc.Modal(id="pay-smart-modal", size="xl", centered=True, children=[html.Div(id="pay-modal-content")]),
        *refresh,
        html.Div(id="admin-payables-body", children=_render_payables_body(ctx)),
    ])

FILTROS_ACTIVOS = []

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID, 
    body_output_id="admin-payables-body", 
    render_body=_render_payables_body,
    filter_ids=FILTROS_ACTIVOS
)

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
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)