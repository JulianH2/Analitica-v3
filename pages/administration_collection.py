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
from strategies.administration import (
    AdminKPIStrategy, AdminGaugeStrategy,
    AdminTrendChartStrategy, AdminHistoricalForecastLineStrategy,
    AdminDonutChartStrategy, AdminHorizontalBarStrategy, AdminTableStrategy,
)

dash.register_page(__name__, path="/administration-receivables", title="Facturación y Cobranza")

SCREEN_ID = "administration-receivables"
PREFIX = "ar"


def skeleton_admin_collection():
    from components.skeleton import skeleton_kpi, skeleton_gauge, skeleton_chart, skeleton_table
    return html.Div(className="skeleton-layout", children=[
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))", "gap": "0.5rem", "marginBottom": "0.6rem"}, children=[skeleton_kpi() for _ in range(5)]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr 2fr", "gap": "0.5rem", "marginBottom": "0.6rem"}, children=[skeleton_gauge(), skeleton_gauge(), skeleton_chart("280px")]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "7fr 5fr", "gap": "0.6rem", "marginBottom": "0.6rem"}, children=[skeleton_table(10, 5), skeleton_chart("360px")]),
        html.Div(style={"marginBottom": "0.6rem"}, children=[skeleton_chart("300px")]),
    ])


# ── KPIs acumulados ──────────────────────────────────────────────────────────
k_billing  = SmartWidget(f"{PREFIX}_billing",  AdminKPIStrategy(SCREEN_ID, "billed_amount",      "Facturado Acum.",   "tabler:file-invoice", "indigo"))
k_credit   = SmartWidget(f"{PREFIX}_credit",   AdminKPIStrategy(SCREEN_ID, "credit_notes",        "N. Crédito Acum.",  "tabler:file-minus",   "red"))
k_debit    = SmartWidget(f"{PREFIX}_debit",    AdminKPIStrategy(SCREEN_ID, "debit_notes",          "Notas Cargo",       "tabler:file-plus",    "gray"))
k_payments = SmartWidget(f"{PREFIX}_payments", AdminKPIStrategy(SCREEN_ID, "collected_amount",    "Cobrado Acum.",     "tabler:cash",         "green"))
k_portfolio= SmartWidget(f"{PREFIX}_portfolio",AdminKPIStrategy(SCREEN_ID, "accounts_receivable", "Cartera Clientes",  "tabler:users",        "yellow"))

# ── Gauges + Donut ────────────────────────────────────────────────────────────
g_eff  = SmartWidget(f"{PREFIX}_eff",  AdminGaugeStrategy(SCREEN_ID, "collection_efficiency",    "Facturado vs Cobrado", "indigo", icon="tabler:target",   layout_config={"height": 300}))
g_days = SmartWidget(f"{PREFIX}_days", AdminGaugeStrategy(SCREEN_ID, "average_collection_days",  "Prom Días Cartera",    "yellow", icon="tabler:calendar", inverse=True, layout_config={"height": 300}))
c_mix  = ChartWidget(f"{PREFIX}_mix",  AdminDonutChartStrategy(SCREEN_ID, "receivables_by_status", "Cartera M.N. por Clasificación", has_detail=True, layout_config={"height": 260}))

# ── Cartera por cliente: horizontal (categorías largas → horizontal siempre) ─
c_stack = ChartWidget(f"{PREFIX}_stack", AdminHorizontalBarStrategy(SCREEN_ID, "debtors_by_range", "Cartera M.N. por Cliente", has_detail=True, layout_config={"height": 360}))

# ── Tabla antigüedad con pivot (Área × Rango) ────────────────────────────────
_AGING_RANGES = [
    "SIN CARTA COBRO", "POR VENCER",
    "00", "01-08", "09-15", "16-30", "31-45", "46-60", "61-90", "91-120", ">120",
]
_t_aging_strategy = AdminTableStrategy(
    SCREEN_ID, "aging_by_client", "Antigüedad de Saldos",
    "orange", "tabler:clock", pivot_col=1,
)
_t_aging_strategy.pivot_order = _AGING_RANGES
t_aging = TableWidget(f"{PREFIX}_aging", _t_aging_strategy)

# ── Tendencias ────────────────────────────────────────────────────────────────
c_fact         = ChartWidget(f"{PREFIX}_fact",         AdminTrendChartStrategy(SCREEN_ID, "collection_chart_facturado",              "Facturado",                      has_detail=True, color="indigo"))
c_days_trend   = ChartWidget(f"{PREFIX}_days_trend",   AdminTrendChartStrategy(SCREEN_ID, "collection_chart_dias_cartera",            "Días Cartera",                   has_detail=True, color="yellow"))
c_forecast_col = ChartWidget(f"{PREFIX}_forecast_col", AdminHistoricalForecastLineStrategy(SCREEN_ID, "collection_chart_pronostico_cobranza", "Pronóstico Cobranza",            has_detail=True, color="green"))
c_forecast_bill= ChartWidget(f"{PREFIX}_forecast_bill",AdminHistoricalForecastLineStrategy(SCREEN_ID, "collection_chart_pronostico_facturacion", "Facturación Histórica vs Pronóstico", has_detail=True, color="violet"))


def _render_collection_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        # ── Bloque 1: KPIs acumulados (fila compacta) ───────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.6rem", "marginBottom": "1rem"},
            children=[
                k_billing.render(ctx, theme=theme),
                k_credit.render(ctx, theme=theme),
                k_debit.render(ctx, theme=theme),
                k_payments.render(ctx, theme=theme),
                k_portfolio.render(ctx, theme=theme),
            ],
        ),

        # ── Bloque 2: Gauges + Donut en la misma fila ───────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "0.8rem", "marginBottom": "1rem"},
            children=[
                g_eff.render(ctx, theme=theme),
                g_days.render(ctx, theme=theme),
                c_mix.render(ctx, h=300, theme=theme),
            ],
        ),

        # ── Bloque 3: Tabla antigüedad | Cartera por cliente ────────
        dmc.Grid(gutter="sm", mb="sm", children=[
            dmc.GridCol(span=_dmc({"base": 12, "lg": 7}), children=[
                html.Div(style={"height": "360px", "overflowY": "auto", "overflowX": "auto"},
                         children=[t_aging.render(ctx, theme=theme)]),
            ]),
            dmc.GridCol(span=_dmc({"base": 12, "lg": 5}), children=[
                c_stack.render(ctx, h=360, theme=theme),
            ]),
        ]),

        # ── Bloque 4: Tendencias mensuales (tabs compactos) ─────────
        dmc.Paper(
            p="xs",
            withBorder=False,
            mb="sm",
            shadow=None,
            style={"backgroundColor": "transparent"},
            children=[dmc.Tabs(value="facturado", children=[
                dmc.TabsList([
                    dmc.TabsTab("Facturado",             value="facturado"),
                    dmc.TabsTab("Días Cartera",           value="dias_cartera"),
                    dmc.TabsTab("Pronóstico Cobranza",   value="pronostico_cobranza"),
                    dmc.TabsTab("Pronóstico Facturación",value="pronostico_facturacion"),
                ]),
                dmc.TabsPanel(c_fact.render(ctx, h=300, theme=theme),          value="facturado"),
                dmc.TabsPanel(c_days_trend.render(ctx, h=300, theme=theme),    value="dias_cartera"),
                dmc.TabsPanel(c_forecast_col.render(ctx, h=300, theme=theme),  value="pronostico_cobranza"),
                dmc.TabsPanel(c_forecast_bill.render(ctx, h=300, theme=theme), value="pronostico_facturacion"),
            ])]
        ),
        dmc.Space(h=20),
    ])


WIDGET_REGISTRY = {
    f"{PREFIX}_billing":   k_billing,  f"{PREFIX}_credit":      k_credit,
    f"{PREFIX}_debit":     k_debit,    f"{PREFIX}_payments":    k_payments,
    f"{PREFIX}_portfolio": k_portfolio,
    f"{PREFIX}_eff":       g_eff,      f"{PREFIX}_days":        g_days,
    f"{PREFIX}_mix":       c_mix,      f"{PREFIX}_stack":       c_stack,
    f"{PREFIX}_aging":     t_aging,
    f"{PREFIX}_fact":           c_fact,
    f"{PREFIX}_days_trend":     c_days_trend,
    f"{PREFIX}_forecast_col":   c_forecast_col,
    f"{PREFIX}_forecast_bill":  c_forecast_bill,
}


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        year_id="col-year",
        month_id="col-month",
        additional_filters=[
            {"id": "col-empresa",        "label": "Empresa\\Área",   "data": ["Todas"], "value": "Todas"},
            {"id": "col-tipo-op",        "label": "Tipo Operación",  "data": ["Todas"], "value": "Todas"},
            {"id": "col-cliente",        "label": "Cliente",         "data": ["Todas"], "value": "Todas"},
            {"id": "col-estatus-cliente","label": "Estatus Cliente", "data": ["Todas"], "value": "Todas"},
            {"id": "col-factura",        "label": "Factura",         "data": ["Todas"], "value": "Todas"},
            {"id": "col-serie-factura",  "label": "Serie Factura",   "data": ["Todas"], "value": "Todas"},
            {"id": "col-estatus-serie",  "label": "Estatus Serie",   "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(
        fluid=True, px="md",
        children=[
            dcc.Store(id="col-load-trigger", data={"loaded": True}),
            *refresh,
            create_smart_drawer("col-drawer"),
            filters,
            dcc.Loading(
                id="col-loading",
                type="dot",
                color="#228be6",
                children=html.Div(id="administration-receivables-body", children=skeleton_admin_collection()),
            ),
        ],
    )


FILTER_IDS = ["col-year", "col-month", "col-empresa", "col-tipo-op", "col-cliente",
              "col-estatus-cliente", "col-factura", "col-serie-factura", "col-estatus-serie"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="administration-receivables-body",
    render_body=_render_collection_body,
    filter_ids=FILTER_IDS,
    global_token_output_id="current-page-token-store",
)

register_drawer_callback(drawer_id="col-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)

register_filter_modal_callback("col-year")
