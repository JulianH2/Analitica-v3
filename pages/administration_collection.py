from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.filter_manager import create_filter_section
from strategies.administration import (
    AdminKPIStrategy, AdminGaugeStrategy,
    AdminTrendChartStrategy, AdminHistoricalForecastLineStrategy,
    AdminDonutChartStrategy, AdminStackedBarStrategy, AdminTableStrategy
)

dash.register_page(__name__, path="/admin-collection", title="Cobranza")

SCREEN_ID = "administration-receivables"





def skeleton_admin_collection():
    
    from components.skeleton import skeleton_kpi, skeleton_gauge, skeleton_chart, skeleton_table, skeleton_box
    
    return html.Div(
        className="skeleton-layout",
        children=[
            skeleton_box("24px", "250px", "skeleton-title"),
            

            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                    "gap": "0.6rem",
                    "marginTop": "1.5rem",
                    "marginBottom": "1.5rem"
                },
                children=[skeleton_kpi() for _ in range(5)]
            ),
            

            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                    "gap": "0.8rem",
                    "marginBottom": "1.5rem"
                },
                children=[skeleton_gauge() for _ in range(2)]
            ),
            

            skeleton_chart("400px"),
            

            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "7fr 5fr",
                    "gap": "1rem",
                    "marginTop": "1.5rem",
                    "marginBottom": "1.5rem"
                },
                children=[
                    skeleton_table(10, 5),
                    skeleton_chart("480px")
                ]
            ),
            

            html.Div(
                style={"marginTop": "1.5rem"},
                children=[

                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "0.5rem",
                            "marginBottom": "1rem",
                            "borderBottom": "1px solid rgba(255,255,255,0.1)"
                        },
                        children=[skeleton_box("32px", "120px") for _ in range(4)]
                    ),
                    skeleton_chart("400px")
                ]
            )
        ]
    )





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
    AdminGaugeStrategy(
        SCREEN_ID, "collection_efficiency", "Facturado vs Cobrado", "indigo", 
        icon="tabler:target", layout_config={"height": 300}
    )
)
w_gauge_days = SmartWidget(
    "gc_days",
    AdminGaugeStrategy(
        SCREEN_ID, "average_collection_days", "Prom Días Cartera", "yellow", 
        icon="tabler:calendar", layout_config={"height": 300}
    )
)

chart_mix = ChartWidget(
    "cc_mix",
    AdminDonutChartStrategy(
        SCREEN_ID, "receivables_by_status", "Cartera M.N. por Clasificación",
        layout_config={"height": 400}
    )
)
chart_stack = ChartWidget(
    "cc_stack",
    AdminStackedBarStrategy(
        SCREEN_ID, "debtors_by_range", "Cartera M.N. por cliente",
        layout_config={"height": 480}
    )
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
    theme = session.get("theme", "dark")
    
    def _card(widget_content, h=None):
        style = {"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}
        return dmc.Paper(
            p="xs", radius="md", withBorder=True, shadow=None,
            style=style, children=widget_content
        )
    
    return html.Div([
        dmc.Title("Administración - Cobranza", order=3, mb="lg", c="dimmed"), # type: ignore


        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                "gap": "0.6rem",
                "marginBottom": "1rem"
            },
            children=[
                _card(kpi_billing.render(ctx, theme=theme)),
                _card(kpi_credit.render(ctx, theme=theme)),
                _card(kpi_debit.render(ctx, theme=theme)),
                _card(kpi_payments.render(ctx, theme=theme)),
                _card(kpi_portfolio.render(ctx, theme=theme))
            ]
        ),
        

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                "gap": "0.8rem",
                "marginBottom": "1.5rem"
            },
            children=[
                _card(w_gauge_eff.render(ctx, theme=theme)),
                _card(w_gauge_days.render(ctx, theme=theme))
            ]
        ),
        

        _card(chart_mix.render(ctx, h=400, theme=theme)),
        
        dmc.Space(h="md"),
        

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
                            style={"backgroundColor": "transparent"},
                            children=[
                                dmc.Text("ANTIGÜEDAD DE SALDOS", fw="bold", size="xs", c="dimmed", mb="md"), # type: ignore
                                dmc.ScrollArea(
                                    h=440,
                                    children=[AdminTableStrategy(SCREEN_ID, "aging_by_client").render(ctx, theme=theme)]
                                )
                            ]
                        )
                    ]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 5}, # type: ignore
                    children=[_card(chart_stack.render(ctx, h=480, theme=theme))]
                )
            ]
        ),
        

        dmc.Paper(
            p="md", 
            withBorder=True, 
            mb="xl", 
            shadow="sm",
            style={"backgroundColor": "transparent"},
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
                        dmc.TabsPanel(dmc.Box(chart_facturado.render(ctx, h=400, theme=theme), pt="md"), value="facturado"),
                        dmc.TabsPanel(dmc.Box(chart_dias_cartera.render(ctx, h=400, theme=theme), pt="md"), value="dias_cartera"),
                        dmc.TabsPanel(dmc.Box(chart_pronostico_cobranza.render(ctx, h=400, theme=theme), pt="md"), value="pronostico_cobranza"),
                        dmc.TabsPanel(dmc.Box(chart_pronostico_facturacion.render(ctx, h=400, theme=theme), pt="md"), value="pronostico_facturacion")
                    ]
                )
            ]
        ),
        
        dmc.Space(h=60)
    ])
WIDGET_REGISTRY = {
    "ka_billing": kpi_billing, 
    "ka_credit": kpi_credit, 
    "ka_debit": kpi_debit,
    "ka_payments": kpi_payments, 
    "ka_portfolio": kpi_portfolio,
    "gc_billing": w_gauge_eff, 
    "gc_days": w_gauge_days,
    "cc_mix": chart_mix,
    "cc_stack": chart_stack,
    "cc_facturado": chart_facturado,
    "cc_dias_cartera": chart_dias_cartera,
    "cc_pronostico_cobranza": chart_pronostico_cobranza,
    "cc_pronostico_facturacion": chart_pronostico_facturacion
}

def layout():
    if not session.get("user"): 
        return dmc.Text("No autorizado...")
    
    refresh, _ = data_manager.dash_refresh_components(
        SCREEN_ID, 
        interval_ms=60 * 60 * 1000,
        max_intervals=-1
    )
    
    filters = create_filter_section(
        year_id="col-year", 
        month_id="col-month",
        additional_filters=[
            {"id": "col-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": "col-tipo-op", "label": "Tipo Op.", "data": ["Todas"], "value": "Todas"},
            {"id": "col-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"}
        ]
    )
    
    return dmc.Container(
        fluid=True, 
        px="md",
        children=[
            dcc.Store(id="col-load-trigger", data={"loaded": True}),
            *refresh,
            create_smart_drawer("col-drawer"),
            filters,
            html.Div(id="administration-receivables-body", children=skeleton_admin_collection())
        ]
    )

FILTER_IDS = ["col-year", "col-month", "col-empresa", "col-tipo-op", "col-cliente"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID, 
    body_output_id="administration-receivables-body",
    render_body=_render_collection_body, 
    filter_ids=FILTER_IDS
)

register_drawer_callback(
    drawer_id="col-drawer", 
    widget_registry=WIDGET_REGISTRY, 
    screen_id=SCREEN_ID, 
    filter_ids=FILTER_IDS
)