from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.table_widget import TableWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.filter_manager import create_filter_section
from strategies.administration import AdminKPIStrategy, AdminGaugeStrategy, AdminTrendChartStrategy, AdminHistoricalForecastLineStrategy, AdminDonutChartStrategy, AdminStackedBarStrategy, AdminTableStrategy

dash.register_page(__name__, path="/administration-payables", title="Cuentas por Pagar")

SCREEN_ID = "administration-payables"
PREFIX = "ap"

def skeleton_admin_payables():
    from components.skeleton import skeleton_kpi, skeleton_gauge, skeleton_chart, skeleton_table, skeleton_box
    return html.Div(className="skeleton-layout", children=[
        skeleton_box("24px", "300px", "skeleton-title"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(160px, 1fr))", "gap": "0.6rem", "marginTop": "1.5rem", "marginBottom": "1.5rem"}, children=[skeleton_kpi() for _ in range(8)]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[skeleton_gauge() for _ in range(2)]),
        skeleton_chart("400px"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem", "marginTop": "1.5rem", "marginBottom": "1.5rem"}, children=[skeleton_table(10, 4), skeleton_chart("500px")]),
        html.Div(style={"marginTop": "1.5rem"}, children=[html.Div(style={"display": "flex", "gap": "0.5rem", "marginBottom": "1rem", "borderBottom": "1px solid rgba(255,255,255,0.1)"}, children=[skeleton_box("32px", "140px") for _ in range(3)]), skeleton_chart("400px")]),
    ])

k_init = SmartWidget(f"{PREFIX}_init", AdminKPIStrategy(SCREEN_ID, "initial_balance", "Saldo Inicial", "tabler:database-import", "indigo"))
k_cxp = SmartWidget(f"{PREFIX}_cxp", AdminKPIStrategy(SCREEN_ID, "accounts_payable", "CxP", "tabler:file-invoice", "blue"))
k_debit = SmartWidget(f"{PREFIX}_debit", AdminKPIStrategy(SCREEN_ID, "debit_notes", "Notas Cargo", "tabler:receipt", "orange"))
k_credit = SmartWidget(f"{PREFIX}_credit", AdminKPIStrategy(SCREEN_ID, "credit_notes", "Notas Crédito", "tabler:file-minus", "teal"))
k_adv = SmartWidget(f"{PREFIX}_adv", AdminKPIStrategy(SCREEN_ID, "advances", "Anticipo", "tabler:receipt-2", "green"))
k_total = SmartWidget(f"{PREFIX}_total", AdminKPIStrategy(SCREEN_ID, "payables_total", "CxP Total", "tabler:sum", "violet"))
k_pay = SmartWidget(f"{PREFIX}_pay", AdminKPIStrategy(SCREEN_ID, "supplier_payments", "Pago Proveedores", "tabler:truck-delivery", "red"))
k_bal = SmartWidget(f"{PREFIX}_bal", AdminKPIStrategy(SCREEN_ID, "final_balance", "Saldo", "tabler:wallet", "yellow"))

g_eff = SmartWidget(f"{PREFIX}_eff", AdminGaugeStrategy(SCREEN_ID, "payment_efficiency", "CXP vs Pagado", "red", icon="tabler:target", layout_config={"height": 300}))
g_days = SmartWidget(f"{PREFIX}_days", AdminGaugeStrategy(SCREEN_ID, "average_payment_days", "Días Pago", "yellow", icon="tabler:calendar", layout_config={"height": 300}))

c_mix = ChartWidget(f"{PREFIX}_mix", AdminDonutChartStrategy(SCREEN_ID, "payables_by_status", "Distribución Saldo por Clasificación", has_detail=True, layout_config={"height": 400}))
c_stack = ChartWidget(f"{PREFIX}_stack", AdminStackedBarStrategy(SCREEN_ID, "suppliers_by_range", "Saldo por Proveedor", has_detail=True, layout_config={"height": 500}))

t_aging = TableWidget(f"{PREFIX}_aging", AdminTableStrategy(SCREEN_ID, "aging_by_supplier", "Antigüedad de Saldos", "tabler:clock", "orange"))

c_comp = ChartWidget(f"{PREFIX}_comp", AdminTrendChartStrategy(SCREEN_ID, "payables_trends", "Cuentas x Pagar 2025 vs. 2024", has_detail=True, color="red"))
c_paid = ChartWidget(f"{PREFIX}_paid", AdminTrendChartStrategy(SCREEN_ID, "pago_proveedores_trends", "Pago Proveedores 2025 vs. 2024", has_detail=True, color="red"))
c_forecast = ChartWidget(f"{PREFIX}_forecast", AdminHistoricalForecastLineStrategy(SCREEN_ID, "pronostico_pago_proveedores", "Pago Proveedores Histórica vs Pronóstico", has_detail=True, color="red"))

def _render_payables_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        dmc.Title("Administración - Cuentas por Pagar", order=3, mb="lg", c="dimmed"), # type: ignore
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "0.6rem", "marginBottom": "1rem"}, children=[
            k_init.render(ctx, theme=theme),
            k_cxp.render(ctx, theme=theme),
            k_debit.render(ctx, theme=theme),
            k_credit.render(ctx, theme=theme),
            k_adv.render(ctx, theme=theme),
            k_total.render(ctx, theme=theme),
            k_pay.render(ctx, theme=theme),
            k_bal.render(ctx, theme=theme),
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            g_eff.render(ctx, theme=theme),
            g_days.render(ctx, theme=theme)
        ]),
        c_mix.render(ctx, h=400, theme=theme),
        dmc.Space(h="md"),
        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[html.Div(style={"height": "500px", "overflowY": "auto"}, children=[t_aging.render(ctx, theme=theme)])]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[c_stack.render(ctx, h=500, theme=theme)]) # type: ignore
        ]),
        dmc.Paper(
            p="md",
            withBorder=True,
            shadow="sm",
            style={"backgroundColor": "transparent"},
            children=[dmc.Tabs(value="cuentas_x_pagar", children=[
                dmc.TabsList([
                    dmc.TabsTab("Cuentas x Pagar", value="cuentas_x_pagar"),
                    dmc.TabsTab("Pago Proveedores", value="pago_proveedores"),
                    dmc.TabsTab("Pronóstico Pago Prov", value="pronostico_pago_prov")
                ]),
                dmc.TabsPanel(dmc.Box(c_comp.render(ctx, h=400, theme=theme), pt="md"), value="cuentas_x_pagar"),
                dmc.TabsPanel(dmc.Box(c_paid.render(ctx, h=400, theme=theme), pt="md"), value="pago_proveedores"),
                dmc.TabsPanel(dmc.Box(c_forecast.render(ctx, h=400, theme=theme), pt="md"), value="pronostico_pago_prov"),
            ])]
        ),
        dmc.Space(h=60)
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_init": k_init, f"{PREFIX}_cxp": k_cxp, f"{PREFIX}_debit": k_debit, f"{PREFIX}_credit": k_credit, f"{PREFIX}_adv": k_adv, f"{PREFIX}_total": k_total, f"{PREFIX}_pay": k_pay, f"{PREFIX}_bal": k_bal,
    f"{PREFIX}_eff": g_eff, f"{PREFIX}_days": g_days,
    f"{PREFIX}_mix": c_mix, f"{PREFIX}_stack": c_stack,
    f"{PREFIX}_aging": t_aging,
    f"{PREFIX}_comp": c_comp, f"{PREFIX}_paid": c_paid, f"{PREFIX}_forecast": c_forecast,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        year_id="pay-year",
        month_id="pay-month",
        additional_filters=[
            {"id": "pay-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": "pay-proveedor", "label": "Proveedor", "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="pay-load-trigger", data={"loaded": True}),
            *refresh,
            create_smart_drawer("pay-drawer"),
            filters,
            html.Div(id="admin-payables-body", children=skeleton_admin_payables()),
        ],
    )

FILTER_IDS = ["pay-year", "pay-month", "pay-empresa", "pay-proveedor"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="admin-payables-body", render_body=_render_payables_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="pay-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)