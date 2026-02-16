from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_filter_section
from strategies.operational import OpsGaugeStrategy, OpsTrendChartStrategy, OpsHorizontalBarStrategy, OpsTableStrategy

dash.register_page(__name__, path="/operational-costs", title="Costos Operaciones")

SCREEN_ID = "operational-costs"
PREFIX = "oc"

w_profit = SmartWidget(f"{PREFIX}_profit", OpsGaugeStrategy(screen_id=SCREEN_ID, kpi_key="profit_per_trip", title="Utilidad Viaje", icon="tabler:trending-up", color="teal", has_detail=True, layout_config={"height": 290}))
w_total = SmartWidget(f"{PREFIX}_total", OpsGaugeStrategy(screen_id=SCREEN_ID, kpi_key="total_trip_cost", title="Costo Viaje Total", icon="tabler:calculator", color="red", has_detail=True, layout_config={"height": 300}))

c_stack = ChartWidget(f"{PREFIX}_stack", OpsTrendChartStrategy(screen_id=SCREEN_ID, chart_key="cost_and_profit_trends", title="Costo y Utilidad", has_detail=True, layout_config={"height": "100%"}))
c_break = ChartWidget(f"{PREFIX}_break", OpsHorizontalBarStrategy(screen_id=SCREEN_ID, chart_key="cost_by_concept", title="Costos por Concepto", has_detail=True, layout_config={"height": 360}))
c_comp = ChartWidget(f"{PREFIX}_comp", OpsTrendChartStrategy(screen_id=SCREEN_ID, chart_key="cost_breakdown", title="Costo Viaje Total 2025 vs 2024", icon="tabler:chart-line", color="red", has_detail=True, layout_config={"height": 360}))

t_route = TableWidget(f"{PREFIX}_route", OpsTableStrategy(SCREEN_ID, "margin_by_route", title="Margen por Ruta"))
t_unit = TableWidget(f"{PREFIX}_unit", OpsTableStrategy(SCREEN_ID, "margin_by_unit", title="Margen por Unidad"))
t_op = TableWidget(f"{PREFIX}_op", OpsTableStrategy(SCREEN_ID, "margin_by_operator", title="Margen por Operador"))
t_trip = TableWidget(f"{PREFIX}_trip", OpsTableStrategy(SCREEN_ID, "margin_by_trip", title="Margen por Viaje"))
t_client = TableWidget(f"{PREFIX}_client", OpsTableStrategy(SCREEN_ID, "margin_by_client", title="Margen por Cliente"))

def _render_cost_tabs(ctx):
    theme = session.get("theme", "dark")
    return dmc.Paper(p=8, withBorder=True, radius="md", children=[
        dmc.Tabs(value="ruta", children=[
            dmc.TabsList([
                dmc.TabsTab("Margen por Ruta", value="ruta"),
                dmc.TabsTab("Margen por Unidad", value="unidad"),
                dmc.TabsTab("Margen por Operador", value="operador"),
                dmc.TabsTab("Margen por Viaje", value="viaje"),
                dmc.TabsTab("Margen por Cliente", value="cliente"),
            ]),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_route.render(ctx, theme=theme)]), value="ruta"),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_unit.render(ctx, theme=theme)]), value="unidad"),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_op.render(ctx, theme=theme)]), value="operador"),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_trip.render(ctx, theme=theme)]), value="viaje"),
            dmc.TabsPanel(html.Div(style={"height": "380px", "overflowY": "auto"}, children=[t_client.render(ctx, theme=theme)]), value="cliente"),
        ])
    ])

def _render_ops_costs_body(ctx):
    theme = session.get("theme", "dark")

    def _card(widget_content, h=None):
        return dmc.Paper(p="xs", radius="md", withBorder=True, shadow=None, style={"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}, children=widget_content)

    return html.Div([
        dmc.Grid(gutter="md", mb="lg", align="stretch", children=[
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[html.Div(style={"display": "grid", "gridTemplateRows": "1fr 1fr", "gap": "0.8rem", "height": "100%"}, children=[_card(w_profit.render(ctx, theme=theme)), _card(w_total.render(ctx, theme=theme))])]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[_card(c_stack.render(ctx, theme=theme))]) # type: ignore
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[_card(c_break.render(ctx, theme=theme)), _card(c_comp.render(ctx, theme=theme))]),
        dmc.Divider(my="lg", label="Análisis de Margen", labelPosition="center"),
        _render_cost_tabs(ctx),
        dmc.Space(h=30),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_profit": w_profit, f"{PREFIX}_total": w_total,
    f"{PREFIX}_stack": c_stack, f"{PREFIX}_break": c_break, f"{PREFIX}_comp": c_comp,
    f"{PREFIX}_route": t_route, f"{PREFIX}_unit": t_unit, f"{PREFIX}_op": t_op, f"{PREFIX}_trip": t_trip, f"{PREFIX}_client": t_client,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        year_id="cost-year",
        month_id="cost-month",
        default_month="enero",
        additional_filters=[
            {"id": "cost-empresa", "label": "Empresa Área", "data": ["Todas"], "value": "Todas"},
            {"id": "cost-clasificacion", "label": "Clasificación", "data": ["Todas"], "value": "Todas"},
            {"id": "cost-concepto", "label": "Concepto Costo", "data": ["Todos"], "value": "Todos"},
            {"id": "cost-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": "cost-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="costs-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("costs-drawer"),
            filters,
            html.Div(id="ops-costs-body", children=get_skeleton(SCREEN_ID)),
        ],
    )

FILTER_IDS = ["cost-year", "cost-month", "cost-empresa", "cost-clasificacion", "cost-concepto", "cost-unidad", "cost-operador"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-costs-body", render_body=_render_ops_costs_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="costs-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)
