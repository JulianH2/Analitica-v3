from flask import session
import dash
from dash import html, dcc, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from strategies.operational import (
    GaugeKPIStrategy, 
    MonthlyComparisonStrategy, 
    OpsPieStrategy, 
    BalanceUnitStrategy
)

dash.register_page(__name__, path='/ops-dashboard', title='Control Operativo')

data_manager = DataManager()

gauge_ingreso = ChartWidget("g_ingreso", GaugeKPIStrategy("ingresos", "Ingreso Total", "#228be6"))
gauge_viajes = ChartWidget("g_viajes", GaugeKPIStrategy("viajes", "Viajes Totales", "#12b886"))
gauge_kms = ChartWidget("g_kms", GaugeKPIStrategy("kms", "Kms Recorridos", "#fab005"))

bar_ingresos = ChartWidget("b_ingresos", MonthlyComparisonStrategy("Ingresos", "#228be6"))
bar_viajes = ChartWidget("b_viajes", MonthlyComparisonStrategy("Viajes", "#fd7e14"))

pie_ops = ChartWidget("p_ops", OpsPieStrategy())
bar_balance = ChartWidget("b_balance", BalanceUnitStrategy())

WIDGET_REGISTRY = {
    "g_ingreso": gauge_ingreso,
    "g_viajes": gauge_viajes,
    "g_kms": gauge_kms,
    "b_ingresos": bar_ingresos,
    "b_viajes": bar_viajes,
    "p_ops": pie_ops,
    "b_balance": bar_balance
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado. Redirigiendo...", id="redirect-login")
    
    data_context = data_manager.get_data()

    def mini_kpi(title, value, subtext, color="blue"):
        return dmc.Paper(
            p="xs", withBorder=True, shadow="xs", radius="md",
            children=[
                dmc.Text(title, size="xs", c="dimmed", fw="bold", tt="uppercase"), # type: ignore
                dmc.Group(justify="space-between", mt=4, children=[
                    dmc.Text(value, fw="bolder", size="lg"),
                    dmc.Badge(subtext, color="blue", variant="light", size="xs")
                ])
            ]
        )

    return dmc.Container(fluid=True, children=[
        
        dmc.Modal(id="ops-smart-modal", size="xl", centered=True, zIndex=10000, children=[html.Div(id="ops-modal-content")]),

        dmc.Group(justify="space-between", mb="sm", children=[
            dmc.Group([
                DashIconify(icon="tabler:layout-dashboard", width=28, color="#228be6"),
                dmc.Title("Dashboard Operaciones", order=3, c="dark")
            ]),
            dmc.Group(gap="xs", children=[
                dmc.Select(value="2025", data=["2025", "2024"], size="xs", w=100, allowDeselect=False),
                dmc.Select(value="Septiembre", data=["Agosto", "Septiembre"], size="xs", w=120, allowDeselect=False),
                dmc.Button(leftSection=DashIconify(icon="tabler:filter"), variant="default", size="xs")
            ])
        ]),

        dmc.Grid(gutter="md", children=[
            
            dmc.GridCol(span= "content", miw=0, children=[
                
                dmc.SimpleGrid(cols= 1, spacing="sm", mb="sm", children=[
                    gauge_ingreso.render(data_context),
                    gauge_viajes.render(data_context),
                    gauge_kms.render(data_context),
                ]),

                dmc.SimpleGrid(cols= 1, spacing="sm", mb="sm", children=[
                    bar_ingresos.render(data_context),
                    bar_viajes.render(data_context),
                ]),

                dmc.Text("Indicadores de Eficiencia", size="sm", fw="bold", c="dimmed", mb=5), # type: ignore
                dmc.SimpleGrid(cols= 2, spacing="sm", mb="sm", children=[
                    mini_kpi("Ingreso x Viaje", "$29,191", "+11%"),
                    mini_kpi("Ingreso x Unidad", "$254,889", "+25%"),
                    mini_kpi("Unidades Activas", "82", "-2 uds", "red"),
                    mini_kpi("Clientes Activos", "15", "+3 new", "green"),
                ]),

                dmc.SimpleGrid(cols= 1, spacing="sm", children=[
                    pie_ops.render(data_context),
                    bar_balance.render(data_context),
                ])
            ]),

            dmc.GridCol(span=12, miw=0, children=[
                
                dmc.Paper(withBorder=True, shadow="sm", p="sm", mb="sm", radius="md", style={"backgroundColor": "var(--mantine-color-gray-0)"}, children=[
                    dmc.Text("Estado de Flota", size="xs", fw="bold", c="dimmed", tt="uppercase", mb="xs"), # type: ignore
                    dmc.Center(mb="md", children=[
                        dmc.Stack(gap=0, align="center", children=[
                            DashIconify(icon="tabler:truck-loading", width=48, color="#40c057"),
                            dmc.Text("92% Cargado", fw="bolder", size="xl", c="green")
                        ])
                    ]),
                    dmc.ProgressRoot(size="xl", children=[
                        dmc.ProgressSection(value=92, color="green", children=[dmc.ProgressLabel("92%")]),
                        dmc.ProgressSection(value=8, color="gray", children=[dmc.ProgressLabel("8%")])
                    ])
                ]),

                dmc.Paper(withBorder=True, shadow="sm", p="xs", mb="sm", radius="md", children=[
                    dmc.Tabs(value="vacio", color="red", variant="pills", children=[
                        dmc.TabsList(children=[
                            dmc.TabsTab("Vacío", value="vacio", style={"fontSize": "0.8rem"}),
                            dmc.TabsTab("Cargado", value="cargado", style={"fontSize": "0.8rem"}),
                        ], grow=True, mb="xs"),
                        
                        dmc.TabsPanel(value="vacio", children=[
                            dmc.Table(
                                data={
                                    "head": ["Ruta", "Viajes"],
                                    "body": [
                                        ["3T-LYCRA", "12"],
                                        ["APAXCO", "8"],
                                        ["CANOITAS", "5"],
                                        ["LA MORITA", "3"],
                                        ["LA SILLA", "2"],
                                        ["SALTILLO", "1"],
                                    ]
                                },
                                striped="odd", highlightOnHover=True, withTableBorder=False, fz="xs"
                            )
                        ]),
                         dmc.TabsPanel(value="cargado", children=[
                            dmc.Text("Lista de rutas cargadas...", size="xs", c="dimmed", ta="center", py="xl") # type: ignore
                        ]),
                    ])
                ]),

                dmc.Paper(withBorder=True, shadow="sm", p="xs", radius="md", children=[
                    dmc.Text("Top Ingresos", size="xs", fw="bold", c="dimmed", mb="xs"), # type: ignore
                    dmc.Tabs(value="cliente", color="blue", variant="default", children=[
                        dmc.TabsList(children=[
                            dmc.TabsTab("Cliente", value="cliente", px="xs"),
                            dmc.TabsTab("Unidad", value="unidad", px="xs"),
                        ], grow=True, mb="xs"),

                        dmc.TabsPanel(value="cliente", children=[
                            dmc.ScrollArea(h=300, children=[
                                dmc.Table(
                                    data={
                                        "head": ["Cliente", "Total"],
                                        "body": [
                                            ["LITECRETE", "$200k"],
                                            ["CONCRETOS", "$662k"],
                                            ["K&P SOL.", "$34k"],
                                            ["VITRO", "$3.9M"],
                                            ["OWENS", "$5.4M"],
                                            ["HELLMANN", "$340k"],
                                            ["TERNIUM", "$1.2M"],
                                        ]
                                    },
                                    striped="odd", highlightOnHover=True, fz="xs"
                                )
                            ])
                        ])
                    ])
                ])

            ])
        ])
    ])

@callback(
    Output("ops-smart-modal", "opened"),
    Output("ops-smart-modal", "title"),
    Output("ops-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_ops_widget_click(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered: return no_update, no_update, no_update
    
    button_id = ctx.triggered_id
    if not button_id or "index" not in button_id: return no_update, no_update, no_update

    widget_id = button_id["index"]
    widget = WIDGET_REGISTRY.get(widget_id)
    
    if widget:
        data_context = data_manager.get_data()
        content = widget.strategy.render_detail(data_context)
        config = widget.strategy.get_card_config(data_context)
        title = dmc.Text(f"Detalle: {config.get('title')}", fw="bold")
        return True, title, content
    
    return no_update, no_update, no_update