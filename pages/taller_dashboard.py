from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from strategies.taller import (
    TallerGaugeStrategy, TallerTrendStrategy, TallerHorizontalBarStrategy, 
    TallerDonutStrategy, TallerMaintenanceTypeStrategy
)

dash.register_page(__name__, path='/taller-dashboard', title='Mantenimiento')
data_manager = DataManager()

def kpi_block(title, key, color, widget_id, data_context, prefix="$", suffix=""):
    node = data_context["mantenimiento"]["dashboard"]["indicadores"][key]
    gauge = ChartWidget(f"g_{widget_id}", TallerGaugeStrategy(title, key, color, prefix, suffix))
    
    return dmc.Paper(p="xs", withBorder=True, children=[
        dmc.Group(justify="space-between", children=[
            dmc.Stack(gap=0, children=[
                dmc.Text(title, size="xs", fw="bold", c="dimmed"),
                dmc.Text(f"{prefix}{node['valor']:,.2f}{suffix}", size="md", fw=900),
            ]),
            html.Div(gauge.render(data_context), style={"width": "100px"})
        ]),
        dmc.SimpleGrid(cols=3, mt="xs", children=[
            dmc.Stack(gap=0, children=[dmc.Text("Meta", size="10px", c="dimmed"), dmc.Text(f"{prefix}{node['meta']:,.0f}{suffix}", size="xs")]),
            dmc.Stack(gap=0, children=[dmc.Text("vs 2024", size="10px", c="dimmed"), dmc.Text(f"{prefix}{node['vs_2024']:,.0f}", size="xs", c="red")]),
            dmc.Stack(gap=0, children=[dmc.Text("YTD", size="10px", c="dimmed"), dmc.Text(f"{prefix}{node['ytd']:,.0f}", size="xs", c="blue")]),
        ])
    ])
    
chart_taller_trend = ChartWidget("ct_trend", TallerTrendStrategy())
chart_taller_type = ChartWidget("ct_type", TallerMaintenanceTypeStrategy())
chart_taller_fam = ChartWidget("ct_fam", TallerHorizontalBarStrategy("Costo por Familia", "por_familia"))
chart_taller_flota = ChartWidget("ct_flota", TallerHorizontalBarStrategy("Costo por Flota", "por_flota"))
chart_taller_donut = ChartWidget("ct_donut", TallerDonutStrategy("Costo por Tipo Operación", "por_operacion"))
chart_taller_unit = ChartWidget("ct_unit", TallerHorizontalBarStrategy("Costo x Km por Unidad", "costo_km_unidad", "#fa5252"))
chart_taller_marca = ChartWidget("ct_marca", TallerHorizontalBarStrategy("Costo x Km por Marca", "costo_km_marca", "#fab005"))
chart_taller_entry = ChartWidget("ct_entry", TallerHorizontalBarStrategy("Entradas a Taller por Unidad", "entradas_unit", "#228be6"))

WIDGET_REGISTRY = {
    "ct_trend": chart_taller_trend, "ct_type": chart_taller_type, "ct_fam": chart_taller_fam,
    "ct_flota": chart_taller_flota, "ct_donut": chart_taller_donut, "ct_unit": chart_taller_unit,
    "ct_marca": chart_taller_marca, "ct_entry": chart_taller_entry
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="taller-smart-modal", size="lg", centered=True, children=[html.Div(id="taller-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["07-Jul"], value="07-Jul", size="xs"),
                dmc.Select(label="Empresa/Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Operación", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Clasificación", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Razón Reparación", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Tipo Motor", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.Grid(gutter="md", mb="md", children=[
            dmc.GridCol(span=3, children=[kpi_block("Costo Interno", "costo_interno", "#228be6", "int", ctx)]),
            dmc.GridCol(span=3, children=[kpi_block("Costo Externo", "costo_externo", "#fab005", "ext", ctx)]),
            dmc.GridCol(span=3, children=[kpi_block("Costo Llantas", "costo_llantas", "#fa5252", "llant", ctx)]),
            dmc.GridCol(span=3, children=[kpi_block("Total Mantenimiento", "total_mantenimiento", "#12b886", "tot", ctx)]),
        ]),

        dmc.Grid(gutter="md", mb="xl", children=[
            dmc.GridCol(span=6, children=[kpi_block("% Disponibilidad", "disponibilidad", "#fab005", "disp", ctx, prefix="", suffix="%")]),
            dmc.GridCol(span=6, children=[kpi_block("Costo por Km", "costo_km", "#228be6", "ckm", ctx)]),
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span=7, children=[chart_taller_trend.render(ctx)]),
            dmc.GridCol(span=5, children=[chart_taller_type.render(ctx)]),
        ]),

        dmc.SimpleGrid(cols=3, spacing="lg", mb="lg", children=[
            chart_taller_fam.render(ctx), chart_taller_flota.render(ctx), chart_taller_donut.render(ctx)
        ]),

        dmc.SimpleGrid(cols=3, spacing="lg", children=[
            chart_taller_unit.render(ctx), chart_taller_marca.render(ctx), chart_taller_entry.render(ctx)
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("taller-smart-modal", "opened"), Output("taller-smart-modal", "title"), Output("taller-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_modal_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update