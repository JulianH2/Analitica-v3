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
    WorkshopTrendChartStrategy,
    WorkshopHorizontalBarStrategy,
    WorkshopDonutChartStrategy,
    WorkshopTableStrategy
)
from flask import session

dash.register_page(__name__, path="/taller-purchases", title="Compras Taller")

SCREEN_ID = "workshop-purchases"

w_total = SmartWidget(
    "wp_total",
    WorkshopKPIStrategy(SCREEN_ID, "total_purchases", "Total Compras", "tabler:shopping-cart", "indigo")
)
w_diesel = SmartWidget(
    "wp_diesel",
    WorkshopKPIStrategy(SCREEN_ID, "fuel_purchases", "Compras Combustible", "tabler:gas-station", "green")
)
w_parts = SmartWidget(
    "wp_parts",
    WorkshopKPIStrategy(SCREEN_ID, "parts_purchases", "Refacciones/Insumos", "tabler:box", "orange")
)
w_tires = SmartWidget(
    "wp_tires",
    WorkshopKPIStrategy(SCREEN_ID, "tire_purchases", "Llantas", "tabler:tire", "red")
)

chart_trend = ChartWidget(
    "cp_trend",
    WorkshopTrendChartStrategy(SCREEN_ID, "purchases_trend", "Tendencia de Compras")
)
chart_area = ChartWidget(
    "cp_area",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "purchases_by_area", "Compras por Área")
)
chart_type = ChartWidget(
    "cp_type",
    WorkshopDonutChartStrategy(SCREEN_ID, "purchases_by_type", "Distribución por Tipo")
)
chart_top_prov = ChartWidget(
    "cp_prov",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "top_suppliers_chart", "Top Proveedores")
)

WIDGET_REGISTRY = {
    "wp_total": w_total,
    "wp_diesel": w_diesel,
    "wp_parts": w_parts,
    "wp_tires": w_tires
}

def _render_taller_purchases_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 1, "sm": 2, "lg": 4},
            spacing="md",
            mb="xl",
            children=[
                w_total.render(ctx, mode="combined"),
                w_diesel.render(ctx, mode="combined"),
                w_parts.render(ctx, mode="combined"),
                w_tires.render(ctx, mode="combined")
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 8}, children=[chart_trend.render(ctx, h=400)]),
                dmc.GridCol(span={"base": 12, "lg": 4}, children=[chart_type.render(ctx, h=400)])
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 6}, children=[chart_area.render(ctx, h=400)]),
                dmc.GridCol(span={"base": 12, "lg": 6}, children=[chart_top_prov.render(ctx, h=400)])
            ]
        ),
        dmc.Paper(
            p="md",
            withBorder=True,
            mb="lg",
            children=[
                dmc.Tabs(
                    value="ordenes",
                    children=[
                        dmc.TabsList([
                            dmc.TabsTab("Órdenes de Compra", value="ordenes"),
                            dmc.TabsTab("Detalle de Insumos", value="insumos"),
                            dmc.TabsTab("Proveedores Detalle", value="prov")
                        ]),
                        dmc.TabsPanel(
                            dmc.ScrollArea(
                                h=400,
                                pt="md",
                                children=[WorkshopTableStrategy(SCREEN_ID, "purchase_orders_detail").render(ctx, theme=theme)]
                            ),
                            value="ordenes"
                        ),
                        dmc.TabsPanel(
                            dmc.ScrollArea(
                                h=400,
                                pt="md",
                                children=[WorkshopTableStrategy(SCREEN_ID, "inventory_detail").render(ctx, theme=theme)]
                            ),
                            value="insumos"
                        ),
                        dmc.TabsPanel(
                            dmc.ScrollArea(
                                h=400,
                                pt="md",
                                children=[WorkshopTableStrategy(SCREEN_ID, "top_suppliers").render(ctx, theme=theme)]
                            ),
                            value="prov"
                        )
                    ]
                )
            ]
        ),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    return dmc.Container(
        fluid=True,
        children=[
            create_smart_modal("pur-modal"),
            *refresh,
            create_workshop_filters(prefix="pur"),
            html.Div(id="taller-purchases-body", children=_render_taller_purchases_body(ctx))
        ]
    )

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-purchases-body",
    render_body=_render_taller_purchases_body,
    filter_ids=get_filter_ids("pur", 5)
)

register_modal_callback("pur-modal", WIDGET_REGISTRY, SCREEN_ID)
