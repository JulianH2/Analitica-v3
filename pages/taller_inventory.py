from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.taller import (
    InventoryGaugeStrategy, InventoryHistoricalTrendStrategy, 
    InventoryAreaDistributionStrategy, InventoryDetailedTableStrategy
)
from strategies.admin import AdminRichKPIStrategy

dash.register_page(__name__, path='/taller-inventory', title='Inventarios Almacén')
data_manager = DataManager()
table_inv_mgr = InventoryDetailedTableStrategy()

# --- INDICADORES (Math Row) ---
w_ini = SmartWidget("wi_ini", AdminRichKPIStrategy("almacen", "inventario_inicial", "Inventario Inicial", "tabler:database-import", "gray", sub_section="indicadores"))
w_ent = SmartWidget("wi_ent", AdminRichKPIStrategy("almacen", "entradas", "Entradas", "tabler:plus", "green", sub_section="indicadores"))
w_sal = SmartWidget("wi_sal", AdminRichKPIStrategy("almacen", "salidas", "Salidas", "tabler:minus", "red", sub_section="indicadores"))
w_his = SmartWidget("wi_his", AdminRichKPIStrategy("almacen", "valorizacion_historica", "Valorización Histórica", "tabler:history", "blue", sub_section="indicadores"))

# --- INDICADORES LATERALES ---
w_cumpl = SmartWidget("wi_cumpl", AdminRichKPIStrategy("almacen", "cumplimiento", "Cumplimiento Max Min", "tabler:checkup-list", "teal", sub_section="indicadores"))
w_reg = SmartWidget("wi_reg", AdminRichKPIStrategy("almacen", "registrados", "Insumos Registrados", "tabler:list-numbers", "indigo", sub_section="indicadores"))
w_con = SmartWidget("wi_con", AdminRichKPIStrategy("almacen", "con_existencia", "Con Existencia", "tabler:package", "blue", sub_section="indicadores"))
w_sin = SmartWidget("wi_sin", AdminRichKPIStrategy("almacen", "sin_existencia", "Sin Existencia", "tabler:package-off", "red", sub_section="indicadores"))

# --- VISUALIZACIONES ---
gauge_actual = ChartWidget("gi_actual", InventoryGaugeStrategy("Valorización Actual", "valorizacion_actual", "#228be6"))
chart_trend = ChartWidget("ci_trend", InventoryHistoricalTrendStrategy())
chart_area = ChartWidget("ci_area", InventoryAreaDistributionStrategy())

WIDGET_REGISTRY = {
    "wi_ini": w_ini, "wi_ent": w_ent, "wi_sal": w_sal, "wi_his": w_his,
    "wi_cumpl": w_cumpl, "wi_reg": w_reg, "wi_con": w_con, "wi_sin": w_sin,
    "gi_actual": gauge_actual, "ci_trend": chart_trend, "ci_area": chart_area
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="inv-smart-modal", size="lg", centered=True, children=[html.Div(id="inv-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[ # type: ignore
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
            dmc.Grid(align="center", gutter="xs", children=[
                dmc.GridCol(span=2.2, children=[w_ini.render(ctx)]),
                dmc.GridCol(span=0.3, children=[dmc.Text("+", fw=900, size="xl", ta="center")]), # type: ignore
                dmc.GridCol(span=2.2, children=[w_ent.render(ctx)]), # type: ignore
                dmc.GridCol(span=0.3, children=[dmc.Text("-", fw=900, size="xl", ta="center")]), # type: ignore
                dmc.GridCol(span=2.2, children=[w_sal.render(ctx)]),
                dmc.GridCol(span=0.3, children=[dmc.Text("=", fw=900, size="xl", ta="center")]), # type: ignore
                dmc.GridCol(span=2.2, children=[w_his.render(ctx)]),
                dmc.GridCol(span=2, children=[gauge_actual.render(ctx)])
            ])
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 9}, children=[chart_trend.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 3}, children=[ # type: ignore
                dmc.Stack(gap="sm", children=[
                    w_cumpl.render(ctx), w_reg.render(ctx), w_con.render(ctx), w_sin.render(ctx)
                ])
            ]),
        ]),
        dmc.Grid(gutter="lg", children=[
            dmc.GridCol(span={"base": 12, "md": 5}, children=[chart_area.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "md": 7}, children=[ # type: ignore
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Tabs(value="fam", children=[
                        dmc.TabsList([
                            dmc.TabsTab("Valorización por Familia", value="fam"),
                            dmc.TabsTab("Detalle Histórico", value="hist")
                        ]),
                        dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_inv_mgr.render_family(ctx)]), value="fam"),
                        dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_inv_mgr.render_history(ctx)]), value="hist"),
                    ])
                ])
            ])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("inv-smart-modal", "opened"), Output("inv-smart-modal", "title"), Output("inv-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_inv_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"] # type: ignore
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update