from design_system import dmc as _dmc
from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.filter_manager import create_filter_section, register_filter_modal_callback
from strategies.administration import AdminKPIStrategy, AdminGaugeStrategy, AdminTrendChartStrategy, AdminHistoricalForecastLineStrategy, AdminDonutChartStrategy, AdminBarChartStrategy, AdminTableStrategy

dash.register_page(__name__, path="/administration-receivables", title="Facturación y Cobranza")

SCREEN_ID = "administration-receivables"
PREFIX = "ar"

def skeleton_admin_collection():
    from components.skeleton import skeleton_kpi, skeleton_gauge, skeleton_chart, skeleton_table, skeleton_box
    return html.Div(className="skeleton-layout", children=[
        skeleton_box("24px", "250px", "skeleton-title"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))", "gap": "0.6rem", "marginTop": "1.5rem", "marginBottom": "1.5rem"}, children=[skeleton_kpi() for _ in range(5)]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[skeleton_gauge() for _ in range(2)]),
        skeleton_chart("400px"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "7fr 5fr", "gap": "1rem", "marginTop": "1.5rem", "marginBottom": "1.5rem"}, children=[skeleton_table(10, 5), skeleton_chart("480px")]),
        html.Div(style={"marginTop": "1.5rem"}, children=[html.Div(style={"display": "flex", "gap": "0.5rem", "marginBottom": "1rem", "borderBottom": "1px solid rgba(255,255,255,0.1)"}, children=[skeleton_box("32px", "120px") for _ in range(4)]), skeleton_chart("400px")]),
    ])

k_billing = SmartWidget(f"{PREFIX}_billing", AdminKPIStrategy(SCREEN_ID, "billed_amount", "Facturado Acumulado", "tabler:file-invoice", "indigo"))
k_credit = SmartWidget(f"{PREFIX}_credit", AdminKPIStrategy(SCREEN_ID, "credit_notes", "Notas Crédito Acumulado", "tabler:file-minus", "red"))
k_debit = SmartWidget(f"{PREFIX}_debit", AdminKPIStrategy(SCREEN_ID, "debit_notes", "Notas Cargo", "tabler:file-plus", "gray"))
k_payments = SmartWidget(f"{PREFIX}_payments", AdminKPIStrategy(SCREEN_ID, "collected_amount", "Cobrado Acumulado", "tabler:cash", "green"))
k_portfolio = SmartWidget(f"{PREFIX}_portfolio", AdminKPIStrategy(SCREEN_ID, "accounts_receivable", "Cartera de Clientes", "tabler:users", "yellow"))

g_eff = SmartWidget(f"{PREFIX}_eff", AdminGaugeStrategy(SCREEN_ID, "collection_efficiency", "Facturado vs Cobrado", "indigo", icon="tabler:target", layout_config={"height": 220}))
g_days = SmartWidget(f"{PREFIX}_days", AdminGaugeStrategy(SCREEN_ID, "average_collection_days", "Prom Días Cartera", "yellow", icon="tabler:calendar", layout_config={"height": 220}))

c_mix = ChartWidget(f"{PREFIX}_mix", AdminDonutChartStrategy(SCREEN_ID, "receivables_by_status", "Cartera M.N. por Clasificación", has_detail=True, layout_config={"height": 400}))
c_stack = ChartWidget(f"{PREFIX}_stack", AdminBarChartStrategy(SCREEN_ID, "debtors_by_range", "Cartera M.N. por cliente", has_detail=True, layout_config={"height": 480}))

t_aging = TableWidget(f"{PREFIX}_aging", AdminTableStrategy(SCREEN_ID, "aging_by_client", "Antigüedad de Saldos", "tabler:clock", "orange"))

c_fact = ChartWidget(f"{PREFIX}_fact", AdminTrendChartStrategy(SCREEN_ID, "collection_chart_facturado", "Facturado", has_detail=True, color="indigo"))
c_days_trend = ChartWidget(f"{PREFIX}_days_trend", AdminTrendChartStrategy(SCREEN_ID, "collection_chart_dias_cartera", "Días Cartera", has_detail=True, color="yellow"))
c_forecast_col = ChartWidget(f"{PREFIX}_forecast_col", AdminTrendChartStrategy(SCREEN_ID, "collection_chart_pronostico_cobranza", "Pronóstico Cobranza", has_detail=True, color="green"))
c_forecast_bill = ChartWidget(f"{PREFIX}_forecast_bill", AdminHistoricalForecastLineStrategy(SCREEN_ID, "collection_chart_pronostico_facturacion", "Facturación Histórica vs Pronóstico", has_detail=True, color="violet"))

def _render_collection_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        dmc.Title("Facturación y Cobranza", order=3, mb="lg", c=_dmc("dimmed")),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))", "gap": "0.6rem", "marginBottom": "1rem"}, children=[
            k_billing.render(ctx, theme=theme),
            k_credit.render(ctx, theme=theme),
            k_debit.render(ctx, theme=theme),
            k_payments.render(ctx, theme=theme),
            k_portfolio.render(ctx, theme=theme)
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            g_eff.render(ctx, theme=theme),
            g_days.render(ctx, theme=theme)
        ]),
        c_mix.render(ctx, h=400, theme=theme),
        dmc.Space(h="md"),
        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span=_dmc({"base": 12, "lg": 7}), children=[html.Div(style={"height": "480px", "overflowY": "auto"}, children=[t_aging.render(ctx, theme=theme)])]),
            dmc.GridCol(span=_dmc({"base": 12, "lg": 5}), children=[c_stack.render(ctx, h=480, theme=theme)])
        ]),
        dmc.Paper(
            p="md",
            withBorder=False,
            mb="xl",
            shadow=None,
            style={"backgroundColor": "transparent"},
            children=[dmc.Tabs(value="facturado", children=[
                dmc.TabsList([
                    dmc.TabsTab("Facturado", value="facturado"),
                    dmc.TabsTab("Días Cartera", value="dias_cartera"),
                    dmc.TabsTab("Pronóstico Cobranza", value="pronostico_cobranza"),
                    dmc.TabsTab("Pronóstico Facturación", value="pronostico_facturacion")
                ]),
                dmc.TabsPanel(dmc.Box(c_fact.render(ctx, h=400, theme=theme), pt="md"), value="facturado"),
                dmc.TabsPanel(dmc.Box(c_days_trend.render(ctx, h=400, theme=theme), pt="md"), value="dias_cartera"),
                dmc.TabsPanel(dmc.Box(c_forecast_col.render(ctx, h=400, theme=theme), pt="md"), value="pronostico_cobranza"),
                dmc.TabsPanel(dmc.Box(c_forecast_bill.render(ctx, h=400, theme=theme), pt="md"), value="pronostico_facturacion"),
            ])]
        ),
        dmc.Space(h=60)
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_billing": k_billing, f"{PREFIX}_credit": k_credit, f"{PREFIX}_debit": k_debit, f"{PREFIX}_payments": k_payments, f"{PREFIX}_portfolio": k_portfolio,
    f"{PREFIX}_eff": g_eff, f"{PREFIX}_days": g_days,
    f"{PREFIX}_mix": c_mix, f"{PREFIX}_stack": c_stack,
    f"{PREFIX}_aging": t_aging,
    f"{PREFIX}_fact": c_fact, f"{PREFIX}_days_trend": c_days_trend, f"{PREFIX}_forecast_col": c_forecast_col, f"{PREFIX}_forecast_bill": c_forecast_bill,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        year_id="col-year",
        month_id="col-month",
        additional_filters=[
            {"id": "col-empresa", "label": "Empresa\\Área", "data": ["Todas"], "value": "Todas"},
            {"id": "col-tipo-op", "label": "Tipo Operación", "data": ["Todas"], "value": "Todas"},
            {"id": "col-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"},
            {"id": "col-estatus-cliente", "label": "Estatus Cliente", "data": ["Todas"], "value": "Todas"},
            {"id": "col-factura", "label": "Factura", "data": ["Todas"], "value": "Todas"},
            {"id": "col-serie-factura", "label": "Serie Factura", "data": ["Todas"], "value": "Todas"},
            {"id": "col-estatus-serie", "label": "Estatus Serie", "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="col-load-trigger", data={"loaded": True}),
            *refresh,
            create_smart_drawer("col-drawer"),
            filters,
            html.Div(id="administration-receivables-body", children=skeleton_admin_collection()),
        ],
    )

FILTER_IDS = ["col-year", "col-month", "col-empresa", "col-tipo-op", "col-cliente", "col-estatus-cliente", "col-factura", "col-serie-factura", "col-estatus-serie"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="administration-receivables-body", render_body=_render_collection_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="col-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)

register_filter_modal_callback("col-year")