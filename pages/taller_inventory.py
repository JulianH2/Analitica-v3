from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager 
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.table_widget import TableWidget
from strategies.taller import (
    InventoryGaugeStrategy, InventoryHistoricalTrendStrategy,
    InventoryAreaDistributionStrategy, InventoryDetailedTableStrategy
)
from strategies.admin import AdminRichKPIStrategy

dash.register_page(__name__, path="/taller-inventory", title="Inventarios Almacén")

SCREEN_ID = "taller-inventory"

table_inv_mgr = InventoryDetailedTableStrategy()

w_ini = SmartWidget("wi_ini", AdminRichKPIStrategy("almacen", "inventario_inicial", "Inventario Inicial", "tabler:database-import", "gray", sub_section="indicadores"))
w_ent = SmartWidget("wi_ent", AdminRichKPIStrategy("almacen", "entradas", "Entradas", "tabler:plus", "green", sub_section="indicadores"))
w_sal = SmartWidget("wi_sal", AdminRichKPIStrategy("almacen", "salidas", "Salidas", "tabler:minus", "red", sub_section="indicadores"))
w_his = SmartWidget("wi_his", AdminRichKPIStrategy("almacen", "valorizacion_historica", "Valorización Histórica", "tabler:history", "blue", sub_section="indicadores"))

w_cumpl = SmartWidget("wi_cumpl", AdminRichKPIStrategy("almacen", "cumplimiento", "Cumplimiento Max Min", "tabler:checkup-list", "teal", sub_section="indicadores"))
w_reg = SmartWidget("wi_reg", AdminRichKPIStrategy("almacen", "registrados", "Insumos Registrados", "tabler:list-numbers", "indigo", sub_section="indicadores"))
w_con = SmartWidget("wi_con", AdminRichKPIStrategy("almacen", "con_existencia", "Con Existencia", "tabler:package", "blue", sub_section="indicadores"))
w_sin = SmartWidget("wi_sin", AdminRichKPIStrategy("almacen", "sin_existencia", "Sin Existencia", "tabler:package-off", "red", sub_section="indicadores"))

gauge_actual = SmartWidget("gi_actual", InventoryGaugeStrategy("Valorización Actual", "valorizacion_actual", "blue"))
chart_trend = ChartWidget("ci_trend", InventoryHistoricalTrendStrategy())
chart_area = ChartWidget("ci_area", InventoryAreaDistributionStrategy())

WIDGET_REGISTRY = {
    "wi_ini": w_ini, "wi_ent": w_ent, "wi_sal": w_sal, "wi_his": w_his,
    "wi_cumpl": w_cumpl, "wi_reg": w_reg, "wi_con": w_con, "wi_sin": w_sin,
    "gi_actual": gauge_actual, "ci_trend": chart_trend, "ci_area": chart_area
}


def _render_taller_inventory_body(ctx):
    return html.Div([
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[  # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["07-Jul"], value="07-Jul", size="xs"),
                dmc.Select(label="Empresa/Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Almacén", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Familia", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Insumo", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Estado", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="U. Medida", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.Paper(p="md", withBorder=True, mb="xl", children=[
            dmc.Box(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr auto 1fr auto 1fr auto 1fr 1.5fr",
                    "gap": "10px",
                    "alignItems": "center",
                },
                children=[
                    w_ini.render(ctx),
                    dmc.Text("+", fw="bold", size="xl", ta="center", c="gray"),
                    w_ent.render(ctx),
                    dmc.Text("-", fw="bold", size="xl", ta="center", c="gray"),
                    w_sal.render(ctx),
                    dmc.Text("=", fw="bold", size="xl", ta="center", c="gray"),
                    w_his.render(ctx),
                    gauge_actual.render(ctx, mode="combined"),
                ],
            )
        ]),

        dmc.Paper(p="md", withBorder=True, mb="lg", children=[  # type: ignore
            dmc.Text("TENDENCIA HISTÓRICA DE VALORIZACIÓN", fw="bold", size="xs", c="dimmed", mb="md"),  # type: ignore
            chart_trend.render(ctx, h=450)
        ]),

        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="lg", mb="xl", children=[  # type: ignore
            w_cumpl.render(ctx),
            w_reg.render(ctx),
            w_con.render(ctx),
            w_sin.render(ctx),
        ]),

        dmc.Grid(gutter="lg", grow=True, children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[chart_area.render(ctx, h=480)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 7}, children=[  # type: ignore
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Tabs(value="fam", children=[
                        dmc.TabsList([
                            dmc.TabsTab("Valorización por Familia", value="fam"),
                            dmc.TabsTab("Detalle Histórico", value="hist"),
                        ]),
                        dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_inv_mgr.render_family(ctx)]), value="fam"),
                        dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_inv_mgr.render_history(ctx)]), value="hist"),
                    ])
                ])
            ])
        ]),

        dmc.Space(h=50)
    ])


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")

    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)

    refresh_components, _ids = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1,
    )

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="inv-smart-modal", size="xl", centered=True, children=[html.Div(id="inv-modal-content")]),

        *refresh_components,

        html.Div(id="taller-inventory-body", children=_render_taller_inventory_body(ctx)),
    ])


data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-inventory-body",
    render_body=_render_taller_inventory_body,
)


@callback(
    Output("inv-smart-modal", "opened"),
    Output("inv-smart-modal", "title"),
    Output("inv-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_inv_modal_click(n_clicks):
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