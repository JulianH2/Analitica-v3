from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager  # singleton
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    PurchasesTrendStrategy, PurchasesAreaBarStrategy,
    PurchasesTypeDonutStrategy, WorkshopPurchasesTableStrategy
)
from strategies.admin import AdminRichKPIStrategy

dash.register_page(__name__, path="/taller-purchases", title="Compras Taller")

SCREEN_ID = "taller-purchases"

table_purch_mgr = WorkshopPurchasesTableStrategy()

kpi_purch_total = SmartWidget("wk_total", AdminRichKPIStrategy("compras", "total", "Compras Totales", "tabler:shopping-cart", "indigo"))
kpi_purch_diesel = SmartWidget("wk_diesel", AdminRichKPIStrategy("compras", "diesel", "Combustible", "tabler:gas-station", "red"))
kpi_purch_stock = SmartWidget("wk_stock", AdminRichKPIStrategy("compras", "stock", "Stock / No Stock", "tabler:box", "yellow"))

chart_purch_trend = ChartWidget("cp_trend", PurchasesTrendStrategy())
chart_purch_area = ChartWidget("cp_area", PurchasesAreaBarStrategy())
chart_purch_type = ChartWidget("cp_type", PurchasesTypeDonutStrategy())

WIDGET_REGISTRY = {
    "wk_total": kpi_purch_total, "wk_diesel": kpi_purch_diesel, "wk_stock": kpi_purch_stock,
    "cp_trend": chart_purch_trend, "cp_area": chart_purch_area, "cp_type": chart_purch_type
}


def _render_taller_purchases_body(ctx):
    return html.Div([
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 5}, spacing="xs", children=[  # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["07-Jul"], value="07-Jul", size="xs"),
                dmc.Select(label="Empresa/Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Compra", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Insumo", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.Text("INDICADORES DE COMPRAS", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="xl", children=[  # type: ignore
            kpi_purch_total.render(ctx), kpi_purch_diesel.render(ctx), kpi_purch_stock.render(ctx)
        ]),

        dmc.Paper(p="md", withBorder=True, mb="xl", children=[chart_purch_trend.render(ctx)]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[chart_purch_area.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 3}, children=[chart_purch_type.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 4}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("COMPRA POR PROVEEDOR", fw="bold", size="xs", mb="md"),
                    dmc.ScrollArea(h=210, children=[table_purch_mgr.render_proveedor(ctx)])
                ])
            ])
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Tabs(value="orders", children=[
                dmc.TabsList([
                    dmc.TabsTab("Resumen de Órdenes", value="orders"),
                    dmc.TabsTab("Detalle de Insumos", value="items")
                ]),
                dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_purch_mgr.render_ordenes(ctx)]), value="orders"),
                dmc.TabsPanel(dmc.Text("Seleccione una orden para ver el detalle de insumos...", size="sm", c="gray", ta="center", py="xl"), value="items")
            ])
        ]),

        dmc.Space(h=50)
    ])


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    # primer paint rápido (base/cache slice)
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    # auto-refresh 1 vez al entrar
    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="purch-smart-modal", size="lg", centered=True, children=[html.Div(id="purch-modal-content")]),

        *refresh_components,

        html.Div(id="taller-purchases-body", children=_render_taller_purchases_body(ctx)),
    ])


data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-purchases-body",
    render_body=_render_taller_purchases_body,
)


@callback(
    Output("purch-smart-modal", "opened"),
    Output("purch-smart-modal", "title"),
    Output("purch-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_purch_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks):
        return no_update, no_update, no_update
    if dash.ctx.triggered_id is None:
        return no_update, no_update, no_update

    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget:
        return no_update, no_update, no_update

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_card_config(ctx)
    return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
