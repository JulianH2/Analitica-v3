from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager 
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    InventoryGaugeStrategy, InventoryHistoricalTrendStrategy,
    InventoryAreaDistributionStrategy, InventoryDetailedTableStrategy,
    TallerRichKPIStrategy
)

dash.register_page(__name__, path="/taller-inventory", title="Inventarios Almacén")

SCREEN_ID = "taller-inventory"

table_inv_mgr = InventoryDetailedTableStrategy()

w_ini = SmartWidget("wi_ini", TallerRichKPIStrategy("initial_inventory", "Inventario Inicial", "tabler:database-import", "gray"))
w_ent = SmartWidget("wi_ent", TallerRichKPIStrategy("inventory_entries", "Entradas", "tabler:plus", "green"))
w_sal = SmartWidget("wi_sal", TallerRichKPIStrategy("inventory_exits", "Salidas", "tabler:minus", "red"))
w_his = SmartWidget("wi_his", TallerRichKPIStrategy("historical_valuation_kpi", "Valorización Histórica", "tabler:history", "blue"))
w_cumpl = SmartWidget("wi_cumpl", TallerRichKPIStrategy("min_max_compliance", "Cumplimiento Min/Max", "tabler:check", "teal"))

w_reg = SmartWidget("wi_reg", TallerRichKPIStrategy("registered_skus", "Items Registrados", "tabler:list", "indigo"))
w_con = SmartWidget("wi_con", TallerRichKPIStrategy("skus_in_stock", "Con Existencia", "tabler:box", "cyan"))
w_sin = SmartWidget("wi_sin", TallerRichKPIStrategy("skus_out_of_stock", "Sin Existencia", "tabler:alert-circle", "orange"))

gauge_actual = SmartWidget("wi_gauge", InventoryGaugeStrategy("Valorización Actual", "current_inventory_value", "indigo"))

chart_trend = ChartWidget("ci_trend", InventoryHistoricalTrendStrategy())
chart_area = ChartWidget("ci_area", InventoryAreaDistributionStrategy())

WIDGET_REGISTRY = {
    "wi_ini": w_ini, "wi_ent": w_ent, "wi_sal": w_sal, "wi_his": w_his, "wi_cumpl": w_cumpl,
    "wi_reg": w_reg, "wi_con": w_con, "wi_sin": w_sin, "wi_gauge": gauge_actual
}

def _render_taller_inventory_body(ctx):
    return html.Div([
        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 2}, children=[ # type: ignore
                dmc.Stack(children=[w_ini.render(ctx), w_ent.render(ctx), w_sal.render(ctx)])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 3}, children=[gauge_actual.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 7}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_trend.render(ctx)])
            ])
        ]),

        dmc.SimpleGrid(cols={"base": 2, "lg": 5}, spacing="md", mb="lg", children=[ # type: ignore
            w_his.render(ctx), w_cumpl.render(ctx),
            w_reg.render(ctx), w_con.render(ctx), w_sin.render(ctx)
        ]),

        dmc.Grid(gutter="md", children=[
            dmc.GridCol(span={"base": 12, "lg": 8}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Text("Inventario por Familia", fw="bold", size="lg", mb="md"),
                    table_inv_mgr.render_family(ctx)
                ])
            ]),
            dmc.GridCol(span={"base": 12, "lg": 4}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[chart_area.render(ctx)])
            ])
        ]),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ids = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="inv-smart-modal", size="xl", centered=True, children=[html.Div(id="inv-modal-content")]),
        *refresh_components,
        html.Div(id="taller-inventory-body", children=_render_taller_inventory_body(ctx)),
    ])

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="taller-inventory-body", render_body=_render_taller_inventory_body)

@callback(
    Output("inv-smart-modal", "opened"), Output("inv-smart-modal", "title"), Output("inv-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_inv_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(str(w_id))
    if not widget: return no_update, no_update, no_update
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    cfg = widget.strategy.get_title(ctx) if hasattr(widget.strategy, "get_title") else {}
    title = cfg if isinstance(cfg, str) else "Detalle"
    return True, title, widget.strategy.render_detail(ctx)