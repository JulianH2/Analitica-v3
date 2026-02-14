from flask import session
import dash
from dash import html
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_filter_section
from strategies.administration import (
    AdminKPIStrategy, AdminGaugeStrategy,
    AdminTrendChartStrategy, AdminHistoricalForecastLineStrategy,
    AdminDonutChartStrategy, AdminStackedBarStrategy, AdminTableStrategy
)

dash.register_page(__name__, path="/administration-receivables", title="Cobranza")

SCREEN_ID = "administration-receivables"

kpi_billing = SmartWidget(
    "ka_billing",
    AdminKPIStrategy(SCREEN_ID, "billed_amount", "Facturado", "tabler:file-invoice", "indigo")
)
kpi_credit = SmartWidget(
    "ka_credit",
    AdminKPIStrategy(SCREEN_ID, "credit_notes", "Notas Crédito", "tabler:file-minus", "red")
)
kpi_debit = SmartWidget(
    "ka_debit",
    AdminKPIStrategy(SCREEN_ID, "debit_notes", "Notas Cargo Acumulado", "tabler:file-plus", "gray")
)
kpi_payments = SmartWidget(
    "ka_payments",
    AdminKPIStrategy(SCREEN_ID, "collected_amount", "Cobrado", "tabler:cash", "green")
)
kpi_portfolio = SmartWidget(
    "ka_portfolio",
    AdminKPIStrategy(SCREEN_ID, "accounts_receivable", "Cartera", "tabler:users", "yellow")
)

w_gauge_eff = SmartWidget(
    "gc_billing",
    AdminGaugeStrategy(SCREEN_ID, "collection_efficiency", "Facturado vs Cobrado", "indigo", icon="tabler:target")
)
w_gauge_days = SmartWidget(
    "gc_days",
    AdminGaugeStrategy(SCREEN_ID, "average_collection_days", "Prom Días Cartera", "yellow", icon="tabler:calendar")
)

chart_mix = ChartWidget(
    "cc_mix",
    AdminDonutChartStrategy(SCREEN_ID, "receivables_by_status", "Cartera M.N. por Clasificación")
)
chart_stack = ChartWidget(
    "cc_stack",
    AdminStackedBarStrategy(SCREEN_ID, "debtors_by_range", "Cartera M.N. por cliente")
)
chart_facturado = ChartWidget(
    "cc_facturado",
    AdminTrendChartStrategy(SCREEN_ID, "collection_chart_facturado", "Facturado", color="indigo")
)
chart_dias_cartera = ChartWidget(
    "cc_dias_cartera",
    AdminTrendChartStrategy(SCREEN_ID, "collection_chart_dias_cartera", "Días Cartera", color="yellow")
)
chart_pronostico_cobranza = ChartWidget(
    "cc_pronostico_cobranza",
    AdminTrendChartStrategy(SCREEN_ID, "collection_chart_pronostico_cobranza", "Pronóstico Cobranza", color="green")
)
chart_pronostico_facturacion = ChartWidget(
    "cc_pronostico_facturacion",
    AdminHistoricalForecastLineStrategy(SCREEN_ID, "collection_chart_pronostico_facturacion", "Facturación Histórica vs Pronóstico", color="violet")
)

WIDGET_REGISTRY = {
    "ka_billing": kpi_billing, "ka_credit": kpi_credit, "ka_debit": kpi_debit,
    "ka_payments": kpi_payments, "ka_portfolio": kpi_portfolio,
    "gc_billing": w_gauge_eff, "gc_days": w_gauge_days
}

def _render_collection_body(ctx):
    return html.Div([
        dmc.Title("Administración - Cobranza", order=3, mb="lg", c="dimmed"), # type: ignore

        dmc.SimpleGrid(
            cols={"base": 2, "sm": 3, "lg": 6}, # type: ignore
            spacing="sm",
            mb="xl",
            children=[
                kpi_billing.render(ctx),
                kpi_credit.render(ctx),
                kpi_debit.render(ctx),
                kpi_payments.render(ctx),
                kpi_portfolio.render(ctx)
            ]
        ),
        
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(
                    span={"base": 12, "md": 6}, # type: ignore
                    children=[
                        dmc.SimpleGrid(cols=2, spacing="md", children=[
                            w_gauge_eff.render(ctx, mode="combined"),
                            w_gauge_days.render(ctx, mode="combined")
                        ])
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "md": 6}, # type: ignore
                    children=[chart_mix.render(ctx, h=360)]
                )
            ]
        ),
        
        dmc.Grid(
            gutter="lg",
            mb="xl",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            shadow="sm",
                            children=[
                                dmc.Text("ANTIGÜEDAD DE SALDOS", fw="bold", size="xs", c="dimmed", mb="md"), # type: ignore
                                dmc.ScrollArea(
                                    h=440,
                                    children=[AdminTableStrategy(SCREEN_ID, "aging_by_client").render(ctx)]
                                )
                            ]
                        )
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 5}, # type: ignore
                    children=[chart_stack.render(ctx, h=480)]
                )
            ]
        ),
        
        dmc.Paper(
            p="md", withBorder=True, mb="xl", shadow="sm",
            children=[
                dmc.Tabs(
                    value="facturado",
                    children=[
                        dmc.TabsList([
                            dmc.TabsTab("Facturado", value="facturado"),
                            dmc.TabsTab("Días Cartera", value="dias_cartera"),
                            dmc.TabsTab("Pronóstico Cobranza", value="pronostico_cobranza"),
                            dmc.TabsTab("Pronóstico Facturación", value="pronostico_facturacion")
                        ]),
                        dmc.TabsPanel(dmc.Box(chart_facturado.render(ctx, h=400), pt="md"), value="facturado"),
                        dmc.TabsPanel(dmc.Box(chart_dias_cartera.render(ctx, h=400), pt="md"), value="dias_cartera"),
                        dmc.TabsPanel(dmc.Box(chart_pronostico_cobranza.render(ctx, h=400), pt="md"), value="pronostico_cobranza"),
                        dmc.TabsPanel(dmc.Box(chart_pronostico_facturacion.render(ctx, h=400), pt="md"), value="pronostico_facturacion")
                    ]
                )
            ]
        ),
        
        dmc.Space(h=60)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    
    filters = create_filter_section(
        year_id="col-year", month_id="col-month",
        additional_filters=[
            {"id": "col-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": "col-tipo-op", "label": "Tipo Op.", "data": ["Todas"], "value": "Todas"},
            {"id": "col-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"}
        ]
    )
    
    return dmc.Container(
        fluid=True, p="md",
        children=[
            create_smart_modal("col-modal"),
            *refresh,
            filters,
            html.Div(id="administration-receivables-body", children=_render_collection_body(ctx))
        ]
    )

FILTER_IDS = ["col-year", "col-month", "col-empresa", "col-tipo-op", "col-cliente"]
data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID, body_output_id="administration-receivables-body",
    render_body=_render_collection_body, filter_ids=FILTER_IDS
)
register_modal_callback("col-modal", WIDGET_REGISTRY, SCREEN_ID)