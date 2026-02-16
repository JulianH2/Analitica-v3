from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_workshop_filters
from strategies.workshop import WorkshopKPIStrategy, WorkshopGaugeStrategy, WorkshopTrendChartStrategy, WorkshopComboChartStrategy, WorkshopTableStrategy

dash.register_page(__name__, path="/workshop-availability", title="Disponibilidad")

SCREEN_ID = "workshop-availability"
PREFIX = "wa"

w_disp = SmartWidget(f"{PREFIX}_disp", WorkshopGaugeStrategy(SCREEN_ID, "availability_percent", "% Disponibilidad", "green", icon="tabler:gauge", use_needle=True, layout_config={"height": 300}))
w_entries = SmartWidget(f"{PREFIX}_ent", WorkshopKPIStrategy(SCREEN_ID, "workshop_entries", "Entradas a Taller", "tabler:truck-loading", "indigo"))

c_trend = ChartWidget(f"{PREFIX}_trend", WorkshopTrendChartStrategy(SCREEN_ID, "availability_trends", "Disponibilidad Mensual 2025 vs 2024", icon="tabler:calendar-stats", has_detail=True))
c_combo = ChartWidget(f"{PREFIX}_combo", WorkshopComboChartStrategy(SCREEN_ID, "entries_and_km_by_unit", "Entradas vs Kilómetros Recorridos", icon="tabler:chart-arrows-vertical", has_detail=True))

t_detail = TableWidget(f"{PREFIX}_detail", WorkshopTableStrategy(SCREEN_ID, "availability_detail", title="Detalle de Disponibilidad"))

def _render_taller_availability_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            w_disp.render(ctx, theme=theme),
            w_entries.render(ctx, theme=theme)
        ]),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(400px, 1fr))", "gap": "0.8rem", "marginBottom": "1.5rem"}, children=[
            c_trend.render(ctx, h=420, theme=theme),
            c_combo.render(ctx, h=420, theme=theme)
        ]),
        dmc.Paper(
            p="md",
            withBorder=True,
            radius="md",
            style={"backgroundColor": "transparent"},
            children=[
                dmc.Text("DETALLE DE DISPONIBILIDAD POR ÁREA / UNIDAD", fw="bold", mb="md", size="xs", c="dimmed"), # type: ignore
                dmc.ScrollArea(h=450, children=[t_detail.render(ctx, theme=theme)]),
            ],
        ),
        dmc.Space(h=50),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_disp": w_disp,
    f"{PREFIX}_ent": w_entries,
    f"{PREFIX}_trend": c_trend,
    f"{PREFIX}_combo": c_combo,
    f"{PREFIX}_detail": t_detail,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="avail-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("avail-drawer"),
            create_workshop_filters(prefix="avail"),
            html.Div(id="taller-avail-body", children=get_skeleton(SCREEN_ID)),
        ],
    )

FILTER_IDS = ["avail-year", "avail-month"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="taller-avail-body", render_body=_render_taller_availability_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="avail-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)