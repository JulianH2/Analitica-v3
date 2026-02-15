from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_workshop_filters
from strategies.workshop import (
    WorkshopKPIStrategy,
    WorkshopGaugeStrategy,
    WorkshopTrendChartStrategy,
    WorkshopDonutChartStrategy,
    WorkshopHorizontalBarStrategy
)

dash.register_page(__name__, path="/taller-dashboard", title="Mantenimiento")

SCREEN_ID = "workshop-dashboard"

w_interno = SmartWidget(
    "wt_int",
    WorkshopKPIStrategy(SCREEN_ID, "internal_cost", "Costo Interno", "tabler:tools", "indigo")
)
w_externo = SmartWidget(
    "wt_ext",
    WorkshopKPIStrategy(SCREEN_ID, "external_cost", "Costo Externo", "tabler:truck-delivery", "yellow")
)
w_llantas = SmartWidget(
    "wt_lla",
    WorkshopKPIStrategy(SCREEN_ID, "tire_cost", "Costo Llantas", "tabler:tire", "red")
)
w_total = SmartWidget(
    "wt_tot",
    WorkshopKPIStrategy(SCREEN_ID, "total_maintenance", "Total Mant.", "tabler:sum", "green")
)

w_disp = SmartWidget(
    "wt_disp",
    WorkshopGaugeStrategy(
        SCREEN_ID, "availability_percent", "% Disponibilidad", "green",
        icon="tabler:gauge", use_needle=True, layout_config={"height": 300}
    )
)
w_ckm = SmartWidget(
    "wt_ckm",
    WorkshopGaugeStrategy(
        SCREEN_ID, "cost_per_km", "Costo por Km", "indigo",
        icon="tabler:route", use_needle=False, layout_config={"height": 300}
    )
)

chart_taller_trend = ChartWidget(
    "ct_trend",
    WorkshopTrendChartStrategy(SCREEN_ID, "maintenance_costs_trend", "Costo Mantenimiento 2025 vs 2024")
)
chart_taller_type = ChartWidget(
    "ct_type",
    WorkshopDonutChartStrategy(SCREEN_ID, "maintenance_by_type", "Mantenimiento por Tipo")
)
chart_taller_fam = ChartWidget(
    "ct_fam",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "maintenance_by_family", "Costo por Familia")
)
chart_taller_flota = ChartWidget(
    "ct_flota",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "maintenance_by_fleet", "Costo por Flota")
)
chart_taller_donut = ChartWidget(
    "ct_donut",
    WorkshopDonutChartStrategy(SCREEN_ID, "maintenance_by_operation", "Costo por Tipo Operación")
)
chart_taller_unit = ChartWidget(
    "ct_unit",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "cost_per_km_by_unit", "Costo x Km por Unidad", color="red")
)
chart_taller_marca = ChartWidget(
    "ct_marca",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "cost_per_km_by_brand", "Costo x Km por Marca", color="yellow")
)
chart_taller_entry = ChartWidget(
    "ct_entry",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "workshop_entries_by_unit", "Entradas a Taller por Unidad", color="indigo")
)

WIDGET_REGISTRY = {
    "wt_int": w_interno,
    "wt_ext": w_externo,
    "wt_lla": w_llantas,
    "wt_tot": w_total,
    "wt_disp": w_disp,
    "wt_ckm": w_ckm
}





def _render_taller_dashboard_body(ctx):
    theme = session.get("theme", "dark")
    
    def _card(widget_content, h=None):
        style = {"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}
        return dmc.Paper(
            p="xs", radius="md", withBorder=True, shadow=None,
            style=style, children=widget_content
        )
    
    return html.Div([

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "0.6rem",
                "marginBottom": "1rem"
            },
            children=[
                _card(w_interno.render(ctx, theme=theme)),
                _card(w_externo.render(ctx, theme=theme)),
                _card(w_llantas.render(ctx, theme=theme)),
                _card(w_total.render(ctx, theme=theme))
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
                _card(w_disp.render(ctx, theme=theme)),
                _card(w_ckm.render(ctx, theme=theme))
            ]
        ),
        

        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 7}, children=[_card(chart_taller_trend.render(ctx, h=420, theme=theme))]), # type: ignore
                dmc.GridCol(span={"base": 12, "lg": 5}, children=[_card(chart_taller_type.render(ctx, h=420, theme=theme))]) # type: ignore
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
                _card(chart_taller_fam.render(ctx, h=420, theme=theme)),
                _card(chart_taller_flota.render(ctx, h=420, theme=theme)),
                _card(chart_taller_donut.render(ctx, h=420, theme=theme))
            ]
        ),
        

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                "gap": "0.8rem"
            },
            children=[
                _card(chart_taller_unit.render(ctx, h=420, theme=theme)),
                _card(chart_taller_marca.render(ctx, h=420, theme=theme)),
                _card(chart_taller_entry.render(ctx, h=420, theme=theme))
            ]
        ),
        
        dmc.Space(h=50)
    ])

WIDGET_REGISTRY = {
    "wt_int": w_interno,
    "wt_ext": w_externo,
    "wt_lla": w_llantas,
    "wt_tot": w_total,
    "wt_disp": w_disp,
    "wt_ckm": w_ckm,
    "ct_trend": chart_taller_trend,
    "ct_type": chart_taller_type,
    "ct_fam": chart_taller_fam,
    "ct_flota": chart_taller_flota,
    "ct_donut": chart_taller_donut,
    "ct_unit": chart_taller_unit,
    "ct_marca": chart_taller_marca,
    "ct_entry": chart_taller_entry
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=60 * 60 * 1000,
        max_intervals=-1
    )
    
    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="taller-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("taller-drawer"),
            create_workshop_filters(prefix="taller"),
            html.Div(id="taller-dashboard-body", children=get_skeleton(SCREEN_ID))
        ]
    )

FILTER_IDS = [
    "taller-year", 
    "taller-month", 
    "taller-empresa", 
    "taller-unidad",
    "taller-tipo-op", 
    "taller-clasificacion", 
    "taller-razon", 
    "taller-motor"
]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-dashboard-body",
    render_body=_render_taller_dashboard_body,
    filter_ids=FILTER_IDS
)


register_drawer_callback(
    drawer_id="taller-drawer",
    widget_registry=WIDGET_REGISTRY,
    screen_id=SCREEN_ID,
    filter_ids=FILTER_IDS
)