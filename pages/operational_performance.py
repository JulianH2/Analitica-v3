from design_system import dmc as _dmc
from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc
from services.time_service import TimeService

_ts = TimeService()

def get_dynamic_title(base_title: str) -> str:
    return f"{base_title} {_ts.current_year} vs. {_ts.previous_year}"

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_filter_section, register_filter_modal_callback
from strategies.operational import OpsGaugeStrategy, OpsTrendChartStrategy, OpsDonutChartStrategy, OpsTableStrategy

dash.register_page(__name__, path="/operational-performance", title="Rendimientos")

SCREEN_ID = "operational-performance"
PREFIX = "op"

w_kms_lt = SmartWidget(f"{PREFIX}_kms_lt", OpsGaugeStrategy(screen_id=SCREEN_ID, key="real_yield", title="Kms. Viaje/Lt", icon="tabler:gauge", color="green", has_detail=True, layout_config={"height": 220}))
w_kms_re = SmartWidget(f"{PREFIX}_kms_tot", OpsGaugeStrategy(screen_id=SCREEN_ID, key="real_kilometers", title="Kms. Real", icon="tabler:route", color="blue", has_detail=True, layout_config={"height": 220}))
w_litros = SmartWidget(f"{PREFIX}_litros", OpsGaugeStrategy(screen_id=SCREEN_ID, key="liters_consumed", title="Litros", icon="tabler:droplet", color="orange", has_detail=True, layout_config={"height": 220}))

class DynamicPerfTrendStrategy(OpsTrendChartStrategy):
    def __init__(self, screen_id, key, base_title, icon="tabler:timeline", color="indigo", has_detail=True, layout_config=None):
        self.base_title = base_title
        super().__init__(screen_id, key, get_dynamic_title(base_title), icon, color, has_detail, layout_config=layout_config)
    def get_card_config(self, ctx):
        config = super().get_card_config(ctx)
        config["title"] = get_dynamic_title(self.base_title)
        return config

c_trend = ChartWidget(f"{PREFIX}_trend", DynamicPerfTrendStrategy(screen_id=SCREEN_ID, key="yield_trends", base_title="Rendimiento Viaje", icon="tabler:timeline", color="indigo", has_detail=True, layout_config={"height": 340}))
c_mix = ChartWidget(f"{PREFIX}_mix", OpsDonutChartStrategy(screen_id=SCREEN_ID, key="yield_by_operation", title="Rendimiento Viaje por Tipo Operación, Marca y Modelo", icon="tabler:chart-pie-2", color="green", has_detail=True, layout_config={"height": 340}))

t_unit = TableWidget(f"{PREFIX}_unit", OpsTableStrategy(SCREEN_ID, "performance_by_unit", title="Rendimientos Viaje por Unidad"))
t_oper = TableWidget(f"{PREFIX}_oper", OpsTableStrategy(SCREEN_ID, "operator_performance", title="Rendimientos por Operador"))

def _render_ops_performance_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            w_kms_lt.render(ctx, theme=theme),
            w_kms_re.render(ctx, theme=theme),
            w_litros.render(ctx, theme=theme),
        ]),
        html.Div(style={"marginBottom": "1.5rem"}, children=[
            c_trend.render(ctx, h=420, theme=theme),
        ]),
        dmc.Grid(gutter="md", children=[
            dmc.GridCol(span=_dmc({"base": 12, "lg": 4}), children=[c_mix.render(ctx, h=420, theme=theme)]),
            dmc.GridCol(span=_dmc({"base": 12, "lg": 4}), children=[html.Div(style={"height": "420px", "overflowY": "auto"}, children=[t_unit.render(ctx, theme=theme)])]),
            dmc.GridCol(span=_dmc({"base": 12, "lg": 4}), children=[html.Div(style={"height": "420px", "overflowY": "auto"}, children=[t_oper.render(ctx, theme=theme)])]),
        ]),
        dmc.Space(h=30),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_kms_lt": w_kms_lt,
    f"{PREFIX}_kms_tot": w_kms_re,
    f"{PREFIX}_litros": w_litros,
    f"{PREFIX}_trend": c_trend,
    f"{PREFIX}_mix": c_mix,
    f"{PREFIX}_unit": t_unit,
    f"{PREFIX}_oper": t_oper,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")


    theme = session.get("theme", "dark")
    
    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        theme=theme,
        year_id="perf-year",
        month_id="perf-month",
        additional_filters=[
            {"id": "perf-empresa", "label": "Empresa\\Área", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-tipo-unidad", "label": "Tipo Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-no-viaje", "label": "No. Viaje", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-tipo-operacion", "label": "Tipo Operación", "data": ["Todas"], "value": "Todas"},
            {"id": "perf-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="perf-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("perf-drawer"),
            filters,
            html.Div(id="ops-performance-body", children=get_skeleton(SCREEN_ID)),
        ],
    )

FILTER_IDS = ["perf-year", "perf-month", "perf-empresa", "perf-unidad", "perf-tipo-unidad", "perf-no-viaje", "perf-operador", "perf-tipo-operacion", "perf-cliente"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-performance-body", render_body=_render_ops_performance_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="perf-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)

register_filter_modal_callback("perf-year")