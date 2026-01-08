from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from strategies.operational import (
    OpsGaugeStrategy, CostUtilityStackedStrategy, 
    CostBreakdownStrategy, OpsComparisonStrategy, CostTableStrategy
)

dash.register_page(__name__, path='/ops-costs', title='Costos Operativos')
data_manager = DataManager()
table_cost_mgr = CostTableStrategy()

# --- INDICADORES DE COSTO (Gauges) ---
gauge_cost_utility = ChartWidget("gc_utility", OpsGaugeStrategy("Utilidad Viaje", "utilidad_viaje", "#40c057", prefix="%", section="costos"))
gauge_cost_total = ChartWidget("gc_total", OpsGaugeStrategy("Costo Viaje Total", "costo_total", "#fa5252", section="costos"))

# --- ANÁLISIS VISUAL (Charts) ---
chart_cost_stack = ChartWidget("cc_stack", CostUtilityStackedStrategy())
chart_cost_breakdown = ChartWidget("cc_break", CostBreakdownStrategy())
chart_cost_yearly_comp = ChartWidget("cc_comp", OpsComparisonStrategy("Costo Viaje Total 2025 vs 2024", "comparativa_costos", "#fa5252", section="costos"))

# Registro de Widgets para Callbacks
WIDGET_REGISTRY = {
    "gc_utility": gauge_cost_utility, "gc_total": gauge_cost_total,
    "cc_stack": chart_cost_stack, "cc_break": chart_cost_breakdown, "cc_comp": chart_cost_yearly_comp
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="cost-smart-modal", size="lg", centered=True, children=[html.Div(id="cost-modal-content")]),
        
        # Filtros de Operación
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 5}, spacing="xs", children=[ # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["septiembre"], value="septiembre", size="xs"),
                dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Ruta", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Operador", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        # Gauges de Eficiencia de Costo
        dmc.SimpleGrid(cols={"base": 1, "md": 2}, spacing="lg", mb="xl", children=[  # type: ignore
            gauge_cost_utility.render(ctx), gauge_cost_total.render(ctx)
        ]),

        # Análisis Mensual y por Concepto
        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 6}, children=[chart_cost_stack.render(ctx)]),  # type: ignore
            dmc.GridCol(span={"base": 12, "md": 6}, children=[chart_cost_breakdown.render(ctx)]),  # type: ignore
        ]),

        # Comparativa Anual
        dmc.Paper(p="md", withBorder=True, mb="xl", children=[chart_cost_yearly_comp.render(ctx)]),

        # SECCIÓN DE MÁRGENES (100% de Pestañas Recuperadas)
        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Tabs(value="ruta", children=[
                dmc.TabsList([
                    dmc.TabsTab("Margen por Ruta", value="ruta"),
                    dmc.TabsTab("Margen por Unidad", value="unidad"),
                    dmc.TabsTab("Margen por Operador", value="operador"),
                    dmc.TabsTab("Margen por Viaje", value="viaje"),
                    dmc.TabsTab("Margen por Cliente", value="cliente"),
                ]),
                dmc.TabsPanel(dmc.ScrollArea(h=400, mt="md", children=[table_cost_mgr.render_margen_ruta(ctx)]), value="ruta"),
                dmc.TabsPanel(dmc.Text("Seleccione unidad...", py="xl", ta="center", c="dimmed"), value="unidad"),  # type: ignore
                dmc.TabsPanel(dmc.Text("Seleccione operador...", py="xl", ta="center", c="dimmed"), value="operador"),  # type: ignore
                dmc.TabsPanel(dmc.Text("Seleccione viaje...", py="xl", ta="center", c="dimmed"), value="viaje"),  # type: ignore
                dmc.TabsPanel(dmc.Text("Seleccione cliente...", py="xl", ta="center", c="dimmed"), value="cliente"),  # type: ignore
            ])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("cost-smart-modal", "opened"), Output("cost-smart-modal", "title"), Output("cost-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_cost_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]  # type: ignore
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update