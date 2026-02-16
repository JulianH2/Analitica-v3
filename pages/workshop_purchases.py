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
from strategies.workshop import WorkshopKPIStrategy, WorkshopTrendChartStrategy, WorkshopHorizontalBarStrategy, WorkshopDonutChartStrategy, WorkshopTableStrategy

dash.register_page(__name__, path="/workshop-purchases", title="Compras Taller")

SCREEN_ID = "workshop-purchases"
PREFIX = "wp"

w_tot = SmartWidget(f"{PREFIX}_tot", WorkshopKPIStrategy(SCREEN_ID, "total_purchases", "Total Compras", "tabler:shopping-cart", "indigo"))
w_die = SmartWidget(f"{PREFIX}_die", WorkshopKPIStrategy(SCREEN_ID, "fuel_purchases", "Compras Combustible", "tabler:gas-station", "green"))
w_par = SmartWidget(f"{PREFIX}_par", WorkshopKPIStrategy(SCREEN_ID, "parts_purchases", "Refacciones/Insumos", "tabler:box", "orange"))
w_tir = SmartWidget(f"{PREFIX}_tir", WorkshopKPIStrategy(SCREEN_ID, "tire_purchases", "Llantas", "tabler:tire", "red"))

c_trend = ChartWidget(f"{PREFIX}_trend", WorkshopTrendChartStrategy(SCREEN_ID, "purchases_trend", "Tendencia de Compras", has_detail=True, layout_config={"height": 400}))
c_area = ChartWidget(f"{PREFIX}_area", WorkshopHorizontalBarStrategy(SCREEN_ID, "purchases_by_area", "Compras por Área", has_detail=True, layout_config={"height": 400}))
c_type = ChartWidget(f"{PREFIX}_type", WorkshopDonutChartStrategy(SCREEN_ID, "purchases_by_type", "Distribución por Tipo", has_detail=True, layout_config={"height": 400}))
c_prov = ChartWidget(f"{PREFIX}_prov", WorkshopHorizontalBarStrategy(SCREEN_ID, "top_suppliers_chart", "Top Proveedores", has_detail=True, layout_config={"height": 400}))

t_ord = TableWidget(f"{SCREEN_ID}-purchase_orders_detail", WorkshopTableStrategy(SCREEN_ID, "purchase_orders_detail", title="Órdenes de Compra"))
t_inp = TableWidget(f"{SCREEN_ID}-inventory_detail", WorkshopTableStrategy(SCREEN_ID, "inventory_detail", title="Detalle de Insumos"))
t_sup = TableWidget(f"{SCREEN_ID}-top_suppliers", WorkshopTableStrategy(SCREEN_ID, "top_suppliers", title="Proveedores Detalle"))

def _render_taller_purchases_body(ctx):
    theme = session.get("theme", "dark")
    def _card(widget_content, h=None): return dmc.Paper(p="xs", radius="md", withBorder=True, shadow=None, style={"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}, children=widget_content)

    return html.Div([
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.6rem", "marginBottom": "1.5rem"}, children=[_card(w_tot.render(ctx, theme=theme)), _card(w_die.render(ctx, theme=theme)), _card(w_par.render(ctx, theme=theme)), _card(w_tir.render(ctx, theme=theme))]),
        dmc.Grid(gutter="md", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[_card(c_trend.render(ctx, theme=theme))]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[_card(c_type.render(ctx, theme=theme))]), # type: ignore
        ]),
        dmc.Grid(gutter="md", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[_card(c_area.render(ctx, theme=theme))]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 6}, children=[_card(c_prov.render(ctx, theme=theme))]), # type: ignore
        ]),
        dmc.Paper(p="md", withBorder=True, mb="lg", style={"backgroundColor": "transparent"}, children=[
            dmc.Tabs(value="ordenes", children=[
                dmc.TabsList([dmc.TabsTab("Órdenes de Compra", value="ordenes"), dmc.TabsTab("Detalle de Insumos", value="insumos"), dmc.TabsTab("Proveedores Detalle", value="prov")]),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[t_ord.render(ctx, theme=theme)]), value="ordenes"),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[t_inp.render(ctx, theme=theme)]), value="insumos"),
                dmc.TabsPanel(dmc.ScrollArea(h=400, pt="md", children=[t_sup.render(ctx, theme=theme)]), value="prov"),
            ])
        ]),
        dmc.Space(h=50),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_tot": w_tot, f"{PREFIX}_die": w_die, f"{PREFIX}_par": w_par, f"{PREFIX}_tir": w_tir,
    f"{PREFIX}_trend": c_trend, f"{PREFIX}_area": c_area, f"{PREFIX}_type": c_type, f"{PREFIX}_prov": c_prov,
    f"{SCREEN_ID}-purchase_orders_detail": t_ord, f"{SCREEN_ID}-inventory_detail": t_inp, f"{SCREEN_ID}-top_suppliers": t_sup,
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)
    return dmc.Container(fluid=True, px="md", children=[dcc.Store(id="pur-load-trigger", data={"loaded": True}), *refresh, create_smart_drawer("pur-drawer"), create_workshop_filters(prefix="pur"), html.Div(id="taller-purchases-body", children=get_skeleton(SCREEN_ID))])

FILTER_IDS = ["pur-year", "pur-month"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="taller-purchases-body", render_body=_render_taller_purchases_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="pur-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)
