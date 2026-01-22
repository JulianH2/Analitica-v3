from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.admin import (
    AdminRichKPIStrategy, CollectionGaugeStrategy,
    CollectionComparisonStrategy, CollectionMixStrategy,
    DebtorsStackedStrategy, CollectionAgingTableStrategy
)

dash.register_page(__name__, path="/admin-collection", title="Cobranza")

SCREEN_ID = "admin-collection"

kpi_billing = SmartWidget("ka_billing", AdminRichKPIStrategy("facturacion_cobranza", "facturado_acumulado", "Facturado", "tabler:file-invoice", "indigo", sub_section="acumulado"))
kpi_credit = SmartWidget("ka_credit", AdminRichKPIStrategy("facturacion_cobranza", "notas_credito_acumulado", "Notas Crédito", "tabler:file-minus", "red", sub_section="acumulado"))
kpi_debit = SmartWidget("ka_debit", AdminRichKPIStrategy("facturacion_cobranza", "notas_cargo", "Notas Cargo", "tabler:file-plus", "gray", sub_section="acumulado"))
kpi_payments = SmartWidget("ka_payments", AdminRichKPIStrategy("facturacion_cobranza", "cobrado_acumulado", "Cobrado", "tabler:cash", "green", sub_section="acumulado"))
kpi_portfolio = SmartWidget("ka_portfolio", AdminRichKPIStrategy("facturacion_cobranza", "cartera_clientes", "Cartera", "tabler:users", "yellow", sub_section="acumulado"))
kpi_balance = SmartWidget("ka_balance", AdminRichKPIStrategy("facturacion_cobranza", "saldo_neto", "Saldo Neto", "tabler:calculator", "indigo", sub_section="acumulado"))

w_gauge_eff = SmartWidget("gc_billing", CollectionGaugeStrategy("Eficiencia de Cobro", "facturado_vs_cobrado", "indigo"))
w_gauge_days = SmartWidget("gc_days", CollectionGaugeStrategy("Días de Cartera", "prom_dias_cartera", "yellow", prefix=""))

chart_mix = ChartWidget("cc_mix", CollectionMixStrategy())
chart_stack = ChartWidget("cc_stack", DebtorsStackedStrategy())
chart_comp = ChartWidget("cc_comp", CollectionComparisonStrategy())
table_aging = TableWidget(CollectionAgingTableStrategy())

WIDGET_REGISTRY = {
    "ka_billing": kpi_billing, "ka_credit": kpi_credit, "ka_debit": kpi_debit,
    "ka_payments": kpi_payments, "ka_portfolio": kpi_portfolio, "ka_balance": kpi_balance,
    "gc_billing": w_gauge_eff, "gc_days": w_gauge_days
}

def _render_collection_body(ctx):
    filter_content = html.Div([
        dmc.Grid(align="center", gutter="sm", mb="xs", children=[
            dmc.GridCol(span="content", children=[
                dmc.Select(id="col-year-filter", data=["2025", "2024"], value="2025", variant="filled", style={"width": "100px"}, allowDeselect=False, size="sm")
            ]),
            dmc.GridCol(span="auto", children=[
                dmc.ScrollArea(w="100%", type="scroll", scrollbarSize=6, offsetScrollbars=True, children=[ # type: ignore
                    dmc.SegmentedControl(
                        id="col-month-filter", value="septiembre", color="blue", radius="md", size="sm", fullWidth=True, style={"minWidth": "800px"},
                        data=[{"label": m, "value": m.lower()} for m in ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]] # type: ignore
                    )
                ])
            ])
        ]),
        dmc.SimpleGrid(cols={"base": 2, "md": 3, "lg": 6}, spacing="xs", children=[ # type: ignore
            dmc.Select(label="Empresa Área", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Tipo Operación", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Cliente", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Estatus Cliente", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Factura", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
            dmc.Select(label="Serie Factura", placeholder="Todas", data=["Todas"], value="Todas", size="xs"),
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

        dmc.SimpleGrid(cols={"base": 2, "sm": 3, "lg": 6}, spacing="sm", mb="xl", children=[ # type: ignore
            kpi_billing.render(ctx), kpi_credit.render(ctx), kpi_debit.render(ctx),
            kpi_payments.render(ctx), kpi_portfolio.render(ctx), kpi_balance.render(ctx)
        ]),
        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 6, "lg":6 }, children=[ # type: ignore
                dmc.Stack(gap="md", children=[
                    w_gauge_eff.render(ctx, mode="combined"),
                    w_gauge_days.render(ctx, mode="combined")
                ])
            ]),
            
            dmc.GridCol(span={"base": 12, "md": 6, "lg": 6}, children=[ # type: ignore
                dmc.Paper(withBorder=True, p="xs", radius="md", shadow="sm", style={"height": "100%"}, children=[
                    chart_mix.render(ctx, h=330) 
                ])
            ]),
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "lg": 7}, children=[table_aging.render(ctx, title="ANTIGÜEDAD DE SALDOS POR CLIENTE")]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[dmc.Paper(p="md", withBorder=True, shadow="sm", children=[chart_stack.render(ctx, h=500)])]), # type: ignore
        ]),

        dmc.Grid(children=[
            dmc.GridCol(span=12, children=[dmc.Paper(p="md", withBorder=True, shadow="sm", children=[chart_comp.render(ctx, h=420)])])
        ]),
        dmc.Space(h=60)
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
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)