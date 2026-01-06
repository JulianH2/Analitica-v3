from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.operational import (
    CostConceptStrategy, CostTrendVerticalStrategy,
    TableDataStrategy
)

dash.register_page(__name__, path='/ops-costs', title='Costos')

data_manager = DataManager()
table_data = TableDataStrategy()

w_concept_chart = ChartWidget("w_c_concept", CostConceptStrategy())
w_trend_chart = ChartWidget("w_c_trend", CostTrendVerticalStrategy())

WIDGET_REGISTRY = { "w_c_concept": w_concept_chart, "w_c_trend": w_trend_chart }

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado. Redirigiendo...", id="redirect-login")
    
    data_context = data_manager.get_data()

    def cost_block(title, value, var, color="green"):
        return dmc.Paper(
            p="xs", 
            withBorder=True, 
            # bg ya no acepta '{color}.0'. Usamos style para forzar el color de fondo exacto.
            style={"backgroundColor": f"var(--mantine-color-{color}-0)"}, 
            children=[
                # 'dimmed' ya no es un valor directo para 'c' en el tipado estricto, mejor usar style.
                dmc.Text(title, size="xs", style={"color": "var(--mantine-color-dimmed)"}, fw="bold", tt="uppercase"),
                dmc.Text(value, size="sm", fw="bold"),
                dmc.Badge(var, size="xs", color="green", variant="light")
            ]
        )

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="cost-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="cost-modal-content")]),

        dmc.Group(justify="space-between", mb="md", children=[
            dmc.Title("Dashboard Costos Operaciones", order=3, c="dark"),
            dmc.ActionIcon(DashIconify(icon="tabler:filter"), variant="default")
        ]),

        dmc.Grid(gutter="md", mb="lg", children=[
            dmc.GridCol(span= 12, spanMd= 4, children=[
                dmc.SimpleGrid(cols=2, spacing="sm", children=[
                    dmc.Paper(p="md", withBorder=True, shadow="sm", children=[
                        dmc.Text("Utilidad Viaje", size="xs", style={"color": "var(--mantine-color-dimmed)"}), dmc.Text("18.19%", fw="bold", size="xl", c="blue")
                    ]),
                    dmc.Paper(p="md", withBorder=True, shadow="sm", children=[
                        dmc.Text("Costo Viaje Total", size="xs", style={"color": "var(--mantine-color-dimmed)"}), dmc.Text("$17.1M", fw="bold", size="xl", c="red")
                    ])
                ])
            ]),
            dmc.GridCol(span=12, spanMd=8, children=[
                dmc.SimpleGrid(cols=4, spacing="xs", children=[
                    cost_block("Combustible", "$8.5M", "+2%", "red"),
                    cost_block("Sueldos", "$4.2M", "-1%", "green"),
                    cost_block("Llantas", "$1.5M", "+5%", "red"),
                    cost_block("Mtto", "$1.2M", "0%", "gray"),
                    cost_block("Peajes", "$800k", "+1%", "red"),
                    cost_block("Otros", "$500k", "-2%", "green"),
                    cost_block("Seguros", "$300k", "0%", "gray"),
                    cost_block("Impuestos", "$200k", "0%", "gray"),
                ])
            ])
        ]),

        dmc.SimpleGrid(cols=1, colMd=2, spacing="lg", mb="lg", children=[
            w_concept_chart.render(data_context),
            w_trend_chart.render(data_context)
        ]),

        dmc.Paper(withBorder=True, shadow="sm", p="xs", children=[
            dmc.Tabs(value="ruta", color="teal", variant="outline", children=[
                dmc.TabsList(children=[
                    dmc.TabsTab("Margen por Ruta", value="ruta"),
                    dmc.TabsTab("Margen por Unidad", value="unidad"),
                    dmc.TabsTab("Margen por Cliente", value="cliente"),
                ]),
                dmc.TabsPanel(value="ruta", children=[
                     dmc.Table(
                        striped="odd", highlightOnHover=True, fz="xs", mt="xs",
                        children=[
                            dmc.TableThead(dmc.TableTr([dmc.TableTh("No."), dmc.TableTh("Ruta"), dmc.TableTh("Flete"), dmc.TableTh("Costo"), dmc.TableTh("Utilidad")])),
                            dmc.TableTbody([
                                dmc.TableTr([dmc.TableTd("261"), dmc.TableTd("3T-LYCRA"), dmc.TableTd("$247k"), dmc.TableTd("$198k"), dmc.TableTd("$48k", c="green", fw="bold")]),
                                dmc.TableTr([dmc.TableTd("355"), dmc.TableTd("APAXCO"), dmc.TableTd("$150k"), dmc.TableTd("$140k"), dmc.TableTd("$10k", c="green", fw="bold")])
                            ])
                        ]
                    )
                ])
            ])
        ]),
        
        dmc.Space(h=50)
    ])

@callback(
    Output("cost-smart-modal", "opened"),
    Output("cost-smart-modal", "title"),
    Output("cost-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_cost_click(n_clicks):
    if not dash.ctx.triggered or not isinstance(dash.ctx.triggered_id, dict): 
        return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        content = widget.strategy.render_detail(ctx) or dmc.Text("Sin detalles.")
        return True, dmc.Text(cfg.get("title"), fw="bold"), content
    return no_update, no_update, no_update