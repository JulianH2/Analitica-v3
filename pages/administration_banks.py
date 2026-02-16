from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.filter_manager import create_filter_section
from strategies.administration import (
    AdminKPIStrategy,
    AdminTrendChartStrategy,
    AdminDonutChartStrategy,
    AdminTableStrategy
)

dash.register_page(__name__, path="/administration-banks", title="Bancos")

SCREEN_ID = "administration-banks"
PREFIX = "ab"

def skeleton_admin_banks():
    from components.skeleton import skeleton_kpi, skeleton_chart, skeleton_table, skeleton_box
    def tab_content():
        return html.Div(style={"paddingTop": "1rem"}, children=[
            html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[skeleton_kpi() for _ in range(4)]),
            html.Div(style={"marginBottom": "1.5rem"}, children=[skeleton_chart("380px")]),
            html.Div(style={"display": "grid", "gridTemplateColumns": "5fr 7fr", "gap": "1rem"}, children=[skeleton_chart("400px"), skeleton_table(8, 4)])
        ])
    return html.Div(className="skeleton-layout", children=[
        skeleton_box("24px", "200px", "skeleton-title"),
        html.Div(style={"marginTop": "1.5rem"}, children=[
            html.Div(style={"display": "flex", "gap": "0.5rem", "marginBottom": "1rem", "borderBottom": "1px solid rgba(255,255,255,0.1)"}, children=[skeleton_box("32px", "100px") for _ in range(3)]),
            tab_content()
        ])
    ])

w_init_con = SmartWidget(f"{PREFIX}_init_con", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="initial_balance", title="Saldo Inicial Consolidado", icon="tabler:wallet", color="gray", variant="consolidado"))
w_inc_con = SmartWidget(f"{PREFIX}_inc_con", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="total_income", title="Ingresos Consolidado", icon="tabler:trending-up", color="green", variant="consolidado"))
w_exp_con = SmartWidget(f"{PREFIX}_exp_con", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="total_expenses", title="Egresos Consolidado", icon="tabler:trending-down", color="red", variant="consolidado"))
w_fin_con = SmartWidget(f"{PREFIX}_fin_con", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="final_balance", title="Saldo Final Consolidado", icon="tabler:cash", color="indigo", variant="consolidado"))
c_daily_con = ChartWidget(f"{PREFIX}_daily_con", AdminTrendChartStrategy(screen_id=SCREEN_ID, chart_key="daily_cash_flow", title="Evolución Diaria de Flujo Consolidado", icon="tabler:chart-line", variant="consolidado", has_detail=True, layout_config={"height": 380}))
c_donut_con = ChartWidget(f"{PREFIX}_donut_con", AdminDonutChartStrategy(screen_id=SCREEN_ID, chart_key="balance_by_bank", title="Saldo por Institución Bancaria Consolidado", icon="tabler:chart-pie", variant="consolidado", has_detail=True, layout_config={"height": 400}))
t_concepts_con = TableWidget(f"{PREFIX}_concepts_con", AdminTableStrategy(screen_id=SCREEN_ID, table_key="income_expense_concepts", title="Conceptos Consolidado", icon="tabler:table", variant="consolidado"))

w_init_mxn = SmartWidget(f"{PREFIX}_init_mxn", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="initial_balance", title="Saldo Inicial MXN", icon="tabler:wallet", color="gray", variant="pesos"))
w_inc_mxn = SmartWidget(f"{PREFIX}_inc_mxn", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="total_income", title="Ingresos MXN", icon="tabler:trending-up", color="green", variant="pesos"))
w_exp_mxn = SmartWidget(f"{PREFIX}_exp_mxn", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="total_expenses", title="Egresos MXN", icon="tabler:trending-down", color="red", variant="pesos"))
w_fin_mxn = SmartWidget(f"{PREFIX}_fin_mxn", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="final_balance", title="Saldo Final MXN", icon="tabler:cash", color="indigo", variant="pesos"))
c_daily_mxn = ChartWidget(f"{PREFIX}_daily_mxn", AdminTrendChartStrategy(screen_id=SCREEN_ID, chart_key="daily_cash_flow", title="Evolución Diaria de Flujo MXN", icon="tabler:chart-line", variant="pesos", has_detail=True, layout_config={"height": 380}))
c_donut_mxn = ChartWidget(f"{PREFIX}_donut_mxn", AdminDonutChartStrategy(screen_id=SCREEN_ID, chart_key="balance_by_bank", title="Saldo por Institución Bancaria MXN", icon="tabler:chart-pie", variant="pesos", has_detail=True, layout_config={"height": 400}))
t_concepts_mxn = TableWidget(f"{PREFIX}_concepts_mxn", AdminTableStrategy(screen_id=SCREEN_ID, table_key="income_expense_concepts", title="Conceptos MXN", icon="tabler:table", variant="pesos"))

w_init_usd = SmartWidget(f"{PREFIX}_init_usd", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="initial_balance", title="Saldo Inicial USD", icon="tabler:wallet", color="gray", variant="dolares"))
w_inc_usd = SmartWidget(f"{PREFIX}_inc_usd", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="total_income", title="Ingresos USD", icon="tabler:trending-up", color="green", variant="dolares"))
w_exp_usd = SmartWidget(f"{PREFIX}_exp_usd", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="total_expenses", title="Egresos USD", icon="tabler:trending-down", color="red", variant="dolares"))
w_fin_usd = SmartWidget(f"{PREFIX}_fin_usd", AdminKPIStrategy(screen_id=SCREEN_ID, kpi_key="final_balance", title="Saldo Final USD", icon="tabler:cash", color="indigo", variant="dolares"))
c_daily_usd = ChartWidget(f"{PREFIX}_daily_usd", AdminTrendChartStrategy(screen_id=SCREEN_ID, chart_key="daily_cash_flow", title="Evolución Diaria de Flujo USD", icon="tabler:chart-line", variant="dolares", has_detail=True, layout_config={"height": 380}))
c_donut_usd = ChartWidget(f"{PREFIX}_donut_usd", AdminDonutChartStrategy(screen_id=SCREEN_ID, chart_key="balance_by_bank", title="Saldo por Institución Bancaria USD", icon="tabler:chart-pie", variant="dolares", has_detail=True, layout_config={"height": 400}))
t_concepts_usd = TableWidget(f"{PREFIX}_concepts_usd", AdminTableStrategy(screen_id=SCREEN_ID, table_key="income_expense_concepts", title="Conceptos USD", icon="tabler:table", variant="dolares"))

def _banks_tab_content(ctx, variant, theme):
    def _card(widget_content, h=None):
        return dmc.Paper(p="xs", radius="md", withBorder=True, shadow=None, style={"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}, children=widget_content)

    if variant == "consolidado": k1, k2, k3, k4, c1, c2, t1 = w_init_con, w_inc_con, w_exp_con, w_fin_con, c_daily_con, c_donut_con, t_concepts_con
    elif variant == "pesos": k1, k2, k3, k4, c1, c2, t1 = w_init_mxn, w_inc_mxn, w_exp_mxn, w_fin_mxn, c_daily_mxn, c_donut_mxn, t_concepts_mxn
    else: k1, k2, k3, k4, c1, c2, t1 = w_init_usd, w_inc_usd, w_exp_usd, w_fin_usd, c_daily_usd, c_donut_usd, t_concepts_usd

    return [
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[_card(k1.render(ctx, theme=theme)), _card(k2.render(ctx, theme=theme)), _card(k3.render(ctx, theme=theme)), _card(k4.render(ctx, theme=theme))]),
        _card(c1.render(ctx, h=380, theme=theme)),
        dmc.Space(h="md"),
        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[_card(c2.render(ctx, h=400, theme=theme))]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 7}, children=[_card(t1.render(ctx, theme=theme), h=400)]) # type: ignore
        ])
    ]

def _render_admin_banks_body(ctx):
    theme = session.get("theme", "dark")
    return html.Div([
        dmc.Title("Administración - Bancos", order=3, mb="lg", c="dimmed"), # type: ignore
        dmc.Tabs(
            value="consolidado",
            children=[
                dmc.TabsList([dmc.TabsTab("Consolidado", value="consolidado"), dmc.TabsTab("Pesos", value="pesos"), dmc.TabsTab("Dólares", value="dolares")]),
                dmc.TabsPanel(html.Div(_banks_tab_content(ctx, "consolidado", theme), style={"paddingTop": "1rem"}), value="consolidado"),
                dmc.TabsPanel(html.Div(_banks_tab_content(ctx, "pesos", theme), style={"paddingTop": "1rem"}), value="pesos"),
                dmc.TabsPanel(html.Div(_banks_tab_content(ctx, "dolares", theme), style={"paddingTop": "1rem"}), value="dolares"),
            ]
        ),
        dmc.Space(h=50)
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_init_con": w_init_con, f"{PREFIX}_inc_con": w_inc_con, f"{PREFIX}_exp_con": w_exp_con, f"{PREFIX}_fin_con": w_fin_con, f"{PREFIX}_daily_con": c_daily_con, f"{PREFIX}_donut_con": c_donut_con, f"{PREFIX}_concepts_con": t_concepts_con,
    f"{PREFIX}_init_mxn": w_init_mxn, f"{PREFIX}_inc_mxn": w_inc_mxn, f"{PREFIX}_exp_mxn": w_exp_mxn, f"{PREFIX}_fin_mxn": w_fin_mxn, f"{PREFIX}_daily_mxn": c_daily_mxn, f"{PREFIX}_donut_mxn": c_donut_mxn, f"{PREFIX}_concepts_mxn": t_concepts_mxn,
    f"{PREFIX}_init_usd": w_init_usd, f"{PREFIX}_inc_usd": w_inc_usd, f"{PREFIX}_exp_usd": w_exp_usd, f"{PREFIX}_fin_usd": w_fin_usd, f"{PREFIX}_daily_usd": c_daily_usd, f"{PREFIX}_donut_usd": c_donut_usd, f"{PREFIX}_concepts_usd": t_concepts_usd,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        year_id="bank-year",
        month_id="bank-month",
        default_month="enero",
        additional_filters=[
            {"id": "bank-empresa", "label": "Empresa Área", "data": ["Todas"], "value": "Todas"},
            {"id": "bank-institucion", "label": "Institución Bancaria", "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="bank-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("bank-drawer"),
            filters,
            html.Div(id="admin-banks-body", children=skeleton_admin_banks()),
        ],
    )

FILTER_IDS = ["bank-year", "bank-month", "bank-empresa", "bank-institucion"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="admin-banks-body", render_body=_render_admin_banks_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="bank-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)
