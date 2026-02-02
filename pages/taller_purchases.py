from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    TallerGaugeStrategy, PurchasesTrendStrategy,
    PurchasesAreaBarStrategy, PurchasesTypeDonutStrategy,
    WorkshopPurchasesTableStrategy
)

dash.register_page(__name__, path="/taller-purchases", title="Compras Taller")

SCREEN_ID = "taller-purchases"

table_pur_mgr = WorkshopPurchasesTableStrategy()

w_total = SmartWidget("wp_total", TallerGaugeStrategy("Total Compra", "total", "indigo", section="compras", has_detail=True))
w_diesel = SmartWidget("wp_diesel", TallerGaugeStrategy("Compra Diesel", "diesel", "green", section="compras", has_detail=False))
w_stock = SmartWidget("wp_stock", TallerGaugeStrategy("Compra Stock", "stock", "orange", section="compras", has_detail=False))

chart_trend = ChartWidget("cp_trend", PurchasesTrendStrategy())
chart_area = ChartWidget("cp_area", PurchasesAreaBarStrategy())
chart_type = ChartWidget("cp_type", PurchasesTypeDonutStrategy())

WIDGET_REGISTRY = {
    "wp_total": w_total, 
    "wp_diesel": w_diesel, 
    "wp_stock": w_stock
}

def _render_taller_purchases_body(ctx):
    return html.Div([
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[ # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["07-Jul"], value="07-Jul", size="xs"),
                dmc.Select(label="Proveedor", data=["Todos"], value="Todos", size="xs"),
                dmc.Select(label="Tipo Compra", data=["Todos"], value="Todos", size="xs"),
                dmc.Select(label="Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Insumo", data=["Todos"], value="Todos", size="xs"),
                dmc.Select(label="Estado", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Orden", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.SimpleGrid(cols={"base": 1, "lg": 3}, spacing="md", mb="xl", children=[ # type: ignore
            w_total.render(ctx, mode="simple"),
            w_diesel.render(ctx, mode="simple"),
            w_stock.render(ctx, mode="simple"),
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span={"base": 15, "lg": 8}, children=[chart_trend.render(ctx, h=450)]), # type: ignore
            dmc.GridCol(span={"base": 15, "lg": 4}, children=[chart_type.render(ctx, h=450)]), # type: ignore
        ]),
        
        dmc.Grid(gutter="lg", mb="lg", children=[           
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, style={"height": "100%"}, children=[
                    dmc.Text("TOP PROVEEDORES", fw="bold", size="xs", mb="md", c="dimmed"), # type: ignore
                    dmc.ScrollArea(h=400, children=[table_pur_mgr.render_proveedor(ctx)])
                ])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 7}, children=[ # type: ignore
                chart_area.render(ctx, h=450)
            ]), 
            
        ]),

        dmc.SimpleGrid( spacing="lg", mb="lg", children=[ # type: ignore
            dmc.Paper(p="md", withBorder=True, children=[
                dmc.Text("TOP PROVEEDORES", fw="bold", size="xs", mb="md", c="dimmed"), # type: ignore
                dmc.ScrollArea(h=350, children=[table_pur_mgr.render_proveedor(ctx)])
            ])
        ]),

        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.Tabs(value="ordenes", children=[
                dmc.TabsList([
                    dmc.TabsTab("Órdenes de Compra", value="ordenes"),
                    dmc.TabsTab("Detalle de Insumos", value="insumos"),
                ]),
                dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_pur_mgr.render_ordenes(ctx)]), value="ordenes"),
                dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_pur_mgr.render_insumos(ctx)]), value="insumos"),
            ])
        ]),

        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, px="md", children=[
        dmc.Modal(id="pur-smart-modal", size="xl", centered=True, children=[html.Div(id="pur-modal-content")]),
        *refresh,
        html.Div(id="taller-purchases-body", children=_render_taller_purchases_body(ctx)),
    ])