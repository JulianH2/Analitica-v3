from flask import session
import dash
from dash import html
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
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
    WorkshopKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="internal_cost",
        title="Costo Interno",
        icon="tabler:tools",
        color="indigo"
    )
)

w_externo = SmartWidget(
    "wt_ext",
    WorkshopKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="external_cost",
        title="Costo Externo",
        icon="tabler:truck-delivery",
        color="yellow"
    )
)

w_llantas = SmartWidget(
    "wt_lla",
    WorkshopKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="tire_cost",
        title="Costo Llantas",
        icon="tabler:tire",
        color="red"
    )
)

w_total = SmartWidget(
    "wt_tot",
    WorkshopKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_maintenance",
        title="Total Mant.",
        icon="tabler:sum",
        color="green"
    )
)

w_disp = SmartWidget(
    "wt_disp",
    WorkshopGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="availability_percent",
        title="% Disponibilidad",
        icon="tabler:gauge",
        color="green",
        use_needle=True
    )
)

w_ckm = SmartWidget(
    "wt_ckm",
    WorkshopGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="cost_per_km",
        title="Costo por Km",
        icon="tabler:route",
        color="indigo",
        use_needle=False
    )
)

chart_taller_trend = ChartWidget(
    "ct_trend",
    WorkshopTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="maintenance_costs_trend",
        title="Costo Mantenimiento 2025 vs 2024"
    )
)

chart_taller_type = ChartWidget(
    "ct_type",
    WorkshopDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="maintenance_by_type",
        title="Mantenimiento por Tipo"
    )
)

chart_taller_fam = ChartWidget(
    "ct_fam",
    WorkshopHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="maintenance_by_family",
        title="Costo por Familia"
    )
)

chart_taller_flota = ChartWidget(
    "ct_flota",
    WorkshopHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="maintenance_by_fleet",
        title="Costo por Flota"
    )
)

chart_taller_donut = ChartWidget(
    "ct_donut",
    WorkshopDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="maintenance_by_operation",
        title="Costo por Tipo Operación"
    )
)

chart_taller_unit = ChartWidget(
    "ct_unit",
    WorkshopHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="cost_per_km_by_unit",
        title="Costo x Km por Unidad",
        color="red"
    )
)

chart_taller_marca = ChartWidget(
    "ct_marca",
    WorkshopHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="cost_per_km_by_brand",
        title="Costo x Km por Marca",
        color="yellow"
    )
)

chart_taller_entry = ChartWidget(
    "ct_entry",
    WorkshopHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="workshop_entries_by_unit",
        title="Entradas a Taller por Unidad",
        color="indigo"
    )
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
    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 1, "md": 2},
            spacing="md",
            mb="md",
            children=[
                w_interno.render(ctx, mode="combined"),
                w_externo.render(ctx, mode="combined"),
                w_llantas.render(ctx, mode="combined"),
                w_total.render(ctx, mode="combined")
            ]
        ),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 2},
            spacing="md",
            mb="xl",
            children=[
                w_disp.render(ctx, mode="combined"),
                w_ckm.render(ctx, mode="combined")
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 7}, children=[chart_taller_trend.render(ctx, h=420)]),
                dmc.GridCol(span={"base": 12, "lg": 5}, children=[chart_taller_type.render(ctx, h=420)])
            ]
        ),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 3},
            spacing="md",
            mb="xl",
            children=[
                chart_taller_fam.render(ctx, h=420),
                chart_taller_flota.render(ctx, h=420),
                chart_taller_donut.render(ctx, h=420)
            ]
        ),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 3},
            spacing="md",
            children=[
                chart_taller_unit.render(ctx, h=420),
                chart_taller_marca.render(ctx, h=420),
                chart_taller_entry.render(ctx, h=420)
            ]
        ),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    return dmc.Container(
        fluid=True,
        children=[
            create_smart_modal("taller-modal"),
            *refresh_components,
            create_workshop_filters(prefix="taller"),
            html.Div(id="taller-dashboard-body", children=_render_taller_dashboard_body(ctx))
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

register_modal_callback("taller-modal", WIDGET_REGISTRY, SCREEN_ID)
