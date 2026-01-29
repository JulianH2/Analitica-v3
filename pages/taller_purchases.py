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

w_total = SmartWidget("wp_total", TallerGaugeStrategy("Total Compra", "total_purchase", "indigo", section="compras", has_detail=True))
w_diesel = SmartWidget("wp_diesel", TallerGaugeStrategy("Compra Diesel", "diesel_purchase", "green", section="compras", has_detail=False))
w_stock = SmartWidget("wp_stock", TallerGaugeStrategy("Compra Stock", "stock_purchase", "orange", section="compras", has_detail=False))

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
        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="md", mb="lg", children=[ # type: ignore
            w_total.render(ctx), w_diesel.render(ctx), w_stock.render(ctx)
        ]),

        dmc.Grid(gutter="md", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_trend.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Stack(children=[
                    dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_type.render(ctx)]),
                    dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_area.render(ctx)])
                ])
            ])
        ]),

        dmc.Grid(gutter="md", mb="lg", children=[ 
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                 dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("TOP PROVEEDORES", fw="bold", size="xs", mb="md", c="dimmed"),  # type: ignore
                    dmc.ScrollArea(h=350, children=[table_pur_mgr.render_proveedor(ctx)])
                ])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[ # type: ignore
                 dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("TOP INSUMOS", fw="bold", size="xs", mb="md", c="dimmed"),  # type: ignore
                    dmc.ScrollArea(h=350, children=[table_pur_mgr.render_insumos(ctx)])
                ])
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
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="pur-smart-modal", size="xl", centered=True, children=[html.Div(id="pur-modal-content")]),
        *refresh,
        html.Div(id="taller-purchases-body", children=_render_taller_purchases_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="taller-purchases-body", render_body=_render_taller_purchases_body)

@callback(
    Output("pur-smart-modal", "opened"),
    Output("pur-smart-modal", "title"),
    Output("pur-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_pur_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)