from design_system import dmc as _dmc
from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_workshop_filters, register_filter_modal_callback
from strategies.workshop import WorkshopKPIStrategy, WorkshopGaugeStrategy, WorkshopTrendChartStrategy, WorkshopDonutChartStrategy, WorkshopHorizontalBarStrategy
from services.time_service import TimeService

_ts = TimeService()

def get_dynamic_title(base_title: str) -> str:
    return f"{base_title} {_ts.current_year} vs. {_ts.previous_year}"

dash.register_page(__name__, path="/workshop-dashboard", title="Mantenimiento")

SCREEN_ID = "workshop-dashboard"
PREFIX = "wd"

w_int = SmartWidget(f"{PREFIX}_int", WorkshopKPIStrategy(SCREEN_ID, "internal_cost", "Costo Interno", "tabler:tools", "indigo"))
w_ext = SmartWidget(f"{PREFIX}_ext", WorkshopKPIStrategy(SCREEN_ID, "external_cost", "Costo Externo", "tabler:truck-delivery", "yellow"))
w_lla = SmartWidget(f"{PREFIX}_lla", WorkshopKPIStrategy(SCREEN_ID, "tire_cost", "Costo Llantas", "tabler:tire", "red"))
w_tot = SmartWidget(f"{PREFIX}_tot", WorkshopKPIStrategy(SCREEN_ID, "total_maintenance", "Total Mantenimiento", "tabler:sum", "green"))

w_disp = SmartWidget(f"{PREFIX}_disp", WorkshopGaugeStrategy(SCREEN_ID, "availability_percent", "% Disponibilidad", "green", icon="tabler:gauge", use_needle=True, layout_config={"height": 220}))
w_ckm = SmartWidget(f"{PREFIX}_ckm", WorkshopGaugeStrategy(SCREEN_ID, "cost_per_km", "Costo por Km", "indigo", icon="tabler:route", use_needle=False, layout_config={"height": 220}))

class DynamicWorkshopTrendStrategy(WorkshopTrendChartStrategy):
    def __init__(self, screen_id, key, base_title, has_detail=True, layout_config=None):
        self.base_title = base_title
        super().__init__(screen_id, key, get_dynamic_title(base_title), has_detail=has_detail, layout_config=layout_config)
    def get_card_config(self, ctx):
        config = super().get_card_config(ctx)
        config["title"] = get_dynamic_title(self.base_title)
        return config

c_trend = ChartWidget(f"{PREFIX}_trend", DynamicWorkshopTrendStrategy(SCREEN_ID, "maintenance_costs_trend", "Costo Total Mantenimiento", has_detail=True))
c_type = ChartWidget(f"{PREFIX}_type", WorkshopDonutChartStrategy(SCREEN_ID, "maintenance_by_type", "Costo Total Mantenimiento por Clasificación Unidad y Tipo Razón y Razón Reparación", has_detail=True))
c_fam = ChartWidget(f"{PREFIX}_fam", WorkshopHorizontalBarStrategy(SCREEN_ID, "maintenance_by_family", "Costo Total Mantenimiento por Familia y Subfamilia", has_detail=True))
c_fleet = ChartWidget(f"{PREFIX}_fleet", WorkshopHorizontalBarStrategy(SCREEN_ID, "maintenance_by_fleet", "Costo Total Mantenimiento por Flota\\Marca\\Modelo", has_detail=True))
c_op = ChartWidget(f"{PREFIX}_op", WorkshopDonutChartStrategy(SCREEN_ID, "maintenance_by_operation", "Costo Total Mantenimiento por Tipo de Operación/Área/Razón de Reparación", has_detail=True))
c_unit = ChartWidget(f"{PREFIX}_unit", WorkshopHorizontalBarStrategy(SCREEN_ID, "cost_per_km_by_unit", "Costo por Kilómetro por Unidad y Modelo", color="red", has_detail=True))
c_brand = ChartWidget(f"{PREFIX}_brand", WorkshopHorizontalBarStrategy(SCREEN_ID, "cost_per_km_by_brand", "Costo por Kilómetro por Marca, Modelo y Unidad", color="yellow", has_detail=True))
c_entry = ChartWidget(f"{PREFIX}_entry", WorkshopHorizontalBarStrategy(SCREEN_ID, "workshop_entries_by_unit", "Entradas a Taller por Unidad", color="indigo", has_detail=True))

def _render_taller_dashboard_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.6rem", "marginBottom": "1rem"}, children=[
            w_int.render(ctx, theme=theme),
            w_ext.render(ctx, theme=theme),
            w_lla.render(ctx, theme=theme),
            w_tot.render(ctx, theme=theme)
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            w_disp.render(ctx, theme=theme),
            w_ckm.render(ctx, theme=theme)
        ]),
        dmc.Grid(gutter="md", mb="xl", children=[
            dmc.GridCol(span=_dmc({"base": 12, "lg": 7}), children=[c_trend.render(ctx, h=420, theme=theme)]),
            dmc.GridCol(span=_dmc({"base": 12, "lg": 5}), children=[c_type.render(ctx, h=420, theme=theme)])
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            c_fam.render(ctx, h=420, theme=theme),
            c_fleet.render(ctx, h=420, theme=theme),
            c_op.render(ctx, h=420, theme=theme)
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem"}, children=[
            c_unit.render(ctx, h=420, theme=theme),
            c_brand.render(ctx, h=420, theme=theme),
            c_entry.render(ctx, h=420, theme=theme)
        ]),
        dmc.Space(h=50),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_int": w_int, f"{PREFIX}_ext": w_ext, f"{PREFIX}_lla": w_lla, f"{PREFIX}_tot": w_tot,
    f"{PREFIX}_disp": w_disp, f"{PREFIX}_ckm": w_ckm,
    f"{PREFIX}_trend": c_trend, f"{PREFIX}_type": c_type, f"{PREFIX}_fam": c_fam, f"{PREFIX}_fleet": c_fleet,
    f"{PREFIX}_op": c_op, f"{PREFIX}_unit": c_unit, f"{PREFIX}_brand": c_brand, f"{PREFIX}_entry": c_entry,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)
    return dmc.Container(fluid=True, px="md", children=[
        dcc.Store(id="taller-load-trigger", data={"loaded": True}),
        *refresh_components,
        create_smart_drawer("taller-drawer"),
        create_workshop_filters(prefix="taller"),
        html.Div(id="taller-dashboard-body", children=get_skeleton(SCREEN_ID))
    ])

FILTER_IDS = ["taller-year", "taller-month", "taller-empresa", "taller-unidad", "taller-tipo-op", "taller-clasificacion", "taller-razon", "taller-motor"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="taller-dashboard-body", render_body=_render_taller_dashboard_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="taller-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)

register_filter_modal_callback("taller-year")