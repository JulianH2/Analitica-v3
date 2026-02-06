from components.skeleton import get_skeleton
from flask import session
import dash
from dash import html
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_workshop_filters, get_filter_ids
from strategies.workshop import (
    WorkshopKPIStrategy,
    WorkshopGaugeStrategy,
    WorkshopTrendChartStrategy,
    WorkshopComboChartStrategy,
    WorkshopTableStrategy
)

dash.register_page(__name__, path="/taller-availability", title="Disponibilidad")

SCREEN_ID = "workshop-availability"

w_disp = SmartWidget(
    "wa_disp",
    WorkshopGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="availability_percent",
        title="% Disponibilidad",
        icon="tabler:gauge",
        color="green",
        use_needle=True,
        layout_config={"height": 180}
    )
)

w_entries = SmartWidget(
    "wa_ent",
    WorkshopKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="workshop_entries",
        title="Entradas a Taller",
        icon="tabler:truck-entry",
        color="indigo",
        layout_config={"height": 180}
    )
)

chart_trend = ChartWidget(
    "ca_trend",
    WorkshopTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="availability_trends",
        title="Disponibilidad Mensual 2025 vs 2024",
        icon="tabler:calendar-stats",
        layout_config={"height": 380}
    )
)

chart_combo = ChartWidget(
    "ca_combo",
    WorkshopComboChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="entries_and_km_by_unit",
        title="Entradas vs Kilómetros Recorridos",
        icon="tabler:chart-arrows-vertical",
        layout_config={"height": 380}
    )
)

WIDGET_REGISTRY = {
    "wa_disp": w_disp,
    "wa_ent": w_entries
}

def _render_taller_availability_body(ctx):
    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 1, "md": 2},
            spacing="md",
            mb="lg",
            children=[
                w_disp.render(ctx, mode="combined"),
                w_entries.render(ctx, mode="combined")
            ]
        ),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 2},
            spacing="md",
            mb="lg",
            children=[
                chart_trend.render(ctx, h=380),
                chart_combo.render(ctx, h=380)
            ]
        ),
        dmc.Paper(
            p="md",
            withBorder=True,
            radius="md",
            children=[
                dmc.Text(
                    "DETALLE DE DISPONIBILIDAD POR ÁREA / UNIDAD",
                    fw="bold",
                    mb="md",
                    size="xs",
                    c="dimmed"
                ),
                dmc.ScrollArea(
                    h=400,
                    children=[
                        WorkshopTableStrategy(SCREEN_ID, "availability_detail").render(ctx)
                    ]
                )
            ]
        ),
        dmc.Space(h=30)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    return dmc.Container(
        fluid=True,
        children=[
            create_smart_modal("avail-modal"),
            *refresh_components,
            create_workshop_filters(prefix="avail"),
            html.Div(id="taller-avail-body", children=get_skeleton(SCREEN_ID))
        ]
    )

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-avail-body",
    render_body=_render_taller_availability_body,
    filter_ids=get_filter_ids("avail", 5)
)

register_modal_callback("avail-modal", WIDGET_REGISTRY, SCREEN_ID)