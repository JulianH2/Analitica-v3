from flask import session
import dash
from dash import html, dcc, callback, Input, Output, ALL, no_update
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
    
    strategy = TallerGaugeStrategy(title, key, color, prefix, suffix)
    fig = strategy.get_figure(data_context)
    
    def mini_stat(label, val, color_val="dimmed"):
        return dmc.Stack(gap=0, align="flex-end", children=[
            dmc.Text(label, size="xs", c="gray"),
            dmc.Text(val, size="xs",fw="bold", c="gray")
        ])

    return dmc.Paper(
        p="sm", 
        withBorder=True, 
        shadow="sm", 
        radius="md",
        children=[
            dmc.Group(justify="space-between", align="start", mb=0, children=[
                dmc.Text(title, size="xs", fw="bold", c="gray", tt="uppercase", style={"maxWidth": "50%"}), 
                dmc.Group(gap="md", children=[
                    mini_stat("Meta", f"{prefix}{node['meta']:,.0f}{suffix}"),
                    mini_stat("vs '24", f"{prefix}{node['vs_2024']:,.0f}", "red" if node['vs_2024'] < 0 else "teal"),
                    mini_stat("YTD", f"{prefix}{node['ytd']:,.0f}", "blue")
                ])
            ]),
            
            dmc.Grid(gutter="sm", align="flex-end", children=[
                dmc.GridCol(span=5, children=[
                    dmc.Text(f"{prefix}{node['valor']:,.2f}{suffix}", size="lg", fw="bold", style={"lineHeight": 1}) 
                ]),
                dmc.GridCol(span=7, children=[
                    dcc.Graph(
                        id=f"g_{widget_id}",
                        figure=fig,
                        config={'displayModeBar': False, 'responsive': True},
                        style={"height": "65px", "width": "100%", "margin": "0"}
                    )
                ])
            ])
        ]
    )
    
chart_taller_trend = ChartWidget("ct_trend", TallerTrendStrategy())
chart_taller_type = ChartWidget("ct_type", TallerMaintenanceTypeStrategy())
chart_taller_fam = ChartWidget("ct_fam", TallerHorizontalBarStrategy("Costo por Familia", "por_familia"))
chart_taller_flota = ChartWidget("ct_flota", TallerHorizontalBarStrategy("Costo por Flota", "por_flota"))
chart_taller_donut = ChartWidget("ct_donut", TallerDonutStrategy("Costo por Tipo Operación", "por_operacion"))
chart_taller_unit = ChartWidget("ct_unit", TallerHorizontalBarStrategy("Costo x Km por Unidad", "costo_km_unidad", "red"))
chart_taller_marca = ChartWidget("ct_marca", TallerHorizontalBarStrategy("Costo x Km por Marca", "costo_km_marca", "yellow"))
chart_taller_entry = ChartWidget("ct_entry", TallerHorizontalBarStrategy("Entradas a Taller por Unidad", "entradas_unidad", "indigo"))

WIDGET_REGISTRY = {
    "ct_trend": chart_taller_trend, "ct_type": chart_taller_type, "ct_fam": chart_taller_fam,
    "ct_flota": chart_taller_flota, "ct_donut": chart_taller_donut, "ct_unit": chart_taller_unit,
    "ct_marca": chart_taller_marca, "ct_entry": chart_taller_entry
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data("mantenimiento")
    
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="taller-smart-modal", size="lg", centered=True, children=[html.Div(id="taller-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 4, "lg": 8}, spacing="xs", children=[ # type: ignore
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

        dmc.SimpleGrid(cols={"base": 1, "lg": 2}, spacing="md", mb="md", children=[ # type: ignore
            kpi_block("Costo Interno", "costo_interno", "indigo", "int", ctx),
            kpi_block("Costo Externo", "costo_externo", "yellow", "ext", ctx),
            kpi_block("Costo Llantas", "costo_llantas", "red", "llant", ctx),
            kpi_block("Total Mantenimiento", "total_mantenimiento", "green", "tot", ctx),
        ]),

        dmc.SimpleGrid(cols={"base": 1, "lg": 2}, spacing="md", mb="xl", children=[ # type: ignore
            kpi_block("% Disponibilidad", "disponibilidad", "yellow", "disp", ctx, prefix="", suffix="%"),
            kpi_block("Costo por Km", "costo_km", "indigo", "ckm", ctx),
        ]),

        dmc.Grid(gutter="lg", mb="lg", children=[
            dmc.GridCol(span={"base": 12, "lg": 7}, children=[chart_taller_trend.render(ctx)]), # type: ignore
            dmc.GridCol(span={"base": 12, "lg": 5}, children=[chart_taller_type.render(ctx)]), # type: ignore
        ]),

        dmc.SimpleGrid(cols=3, spacing="lg", mb="lg", children=[ # type: ignore
            chart_taller_fam.render(ctx), chart_taller_flota.render(ctx), chart_taller_donut.render(ctx)
        ]),

        dmc.SimpleGrid(cols=3, spacing="lg", children=[ # type: ignore
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
    if dash.ctx.triggered_id is None: return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data("mantenimiento")
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update