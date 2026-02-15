from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_workshop_filters, get_filter_ids
from strategies.workshop import (
    WorkshopKPIStrategy,
    WorkshopTrendChartStrategy,
    WorkshopHorizontalBarStrategy,
    WorkshopDonutChartStrategy,
    WorkshopTableStrategy
)

dash.register_page(__name__, path="/taller-purchases", title="Compras Taller")

SCREEN_ID = "workshop-purchases"

w_total = SmartWidget("wp_total", WorkshopKPIStrategy(SCREEN_ID, "total_purchases", "Total Compras", "tabler:shopping-cart", "indigo"))
w_diesel = SmartWidget("wp_diesel", WorkshopKPIStrategy(SCREEN_ID, "fuel_purchases", "Compras Combustible", "tabler:gas-station", "green"))
w_parts = SmartWidget("wp_parts", WorkshopKPIStrategy(SCREEN_ID, "parts_purchases", "Refacciones/Insumos", "tabler:box", "orange"))
w_tires = SmartWidget("wp_tires", WorkshopKPIStrategy(SCREEN_ID, "tire_purchases", "Llantas", "tabler:tire", "red"))

chart_trend = ChartWidget("cp_trend", WorkshopTrendChartStrategy(SCREEN_ID, "purchases_trend", "Tendencia de Compras"))
chart_area = ChartWidget("cp_area", WorkshopHorizontalBarStrategy(SCREEN_ID, "purchases_by_area", "Compras por Área"))
chart_type = ChartWidget("cp_type", WorkshopDonutChartStrategy(SCREEN_ID, "purchases_by_type", "Distribución por Tipo"))
chart_top_prov = ChartWidget("cp_prov", WorkshopHorizontalBarStrategy(SCREEN_ID, "top_suppliers_chart", "Top Proveedores"))

WIDGET_REGISTRY = {
    "wp_total": w_total,
    "wp_diesel": w_diesel,
    "wp_parts": w_parts,
    "wp_tires": w_tires
}

def _render_taller_purchases_body(ctx):
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
                "marginBottom": "1.5rem"
            },
            children=[
                _card(w_total.render(ctx, theme=theme)),
                _card(w_diesel.render(ctx, theme=theme)),
                _card(w_parts.render(ctx, theme=theme)),
                _card(w_tires.render(ctx, theme=theme))
            ]
        ),
        

        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 8}, children=[_card(chart_trend.render(ctx, h=400, theme=theme))]), # type: ignore
                dmc.GridCol(span={"base": 12, "lg": 4}, children=[_card(chart_type.render(ctx, h=400, theme=theme))]) # type: ignore
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 6}, children=[_card(chart_area.render(ctx, h=400, theme=theme))]), # type: ignore
                dmc.GridCol(span={"base": 12, "lg": 6}, children=[_card(chart_top_prov.render(ctx, h=400, theme=theme))]) # type: ignore
            ]
        ),   
        dmc.Paper(
            p="md",
            withBorder=True,
            mb="lg",
            style={"backgroundColor": "transparent"},
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

WIDGET_REGISTRY = {
    "wp_total": w_total,
    "wp_diesel": w_diesel,
    "wp_parts": w_parts,
    "wp_tires": w_tires,
    "cp_trend": chart_trend,
    "cp_area": chart_area,
    "cp_type": chart_type,
    "cp_prov": chart_top_prov,
    "workshop-purchases-purchase_orders_detail": TableWidget(
        "workshop-purchases-purchase_orders_detail", 
        WorkshopTableStrategy(SCREEN_ID, "purchase_orders_detail")
    ),
    "workshop-purchases-inventory_detail": TableWidget(
        "workshop-purchases-inventory_detail", 
        WorkshopTableStrategy(SCREEN_ID, "inventory_detail")
    ),
    "workshop-purchases-top_suppliers": TableWidget(
        "workshop-purchases-top_suppliers", 
        WorkshopTableStrategy(SCREEN_ID, "top_suppliers")
    )
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    refresh, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=60 * 60 * 1000,
        max_intervals=-1
    )
    
    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="pur-load-trigger", data={"loaded": True}),
            *refresh,
            create_smart_drawer("pur-drawer"),
            create_workshop_filters(prefix="pur"),
            html.Div(id="taller-purchases-body", children=get_skeleton(SCREEN_ID))
        ]
    )

FILTER_IDS = ["pur-year", "pur-month"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-purchases-body",
    render_body=_render_taller_purchases_body,
    filter_ids=FILTER_IDS
)

register_drawer_callback(
    drawer_id="pur-drawer", 
    widget_registry=WIDGET_REGISTRY, 
    screen_id=SCREEN_ID, 
    filter_ids=FILTER_IDS
)