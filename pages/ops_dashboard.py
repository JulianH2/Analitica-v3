from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from strategies.operational import (
    OpsGaugeStrategy, OpsComparisonStrategy, OpsPieStrategy, 
    BalanceUnitStrategy, OpsTableStrategy
)
from strategies.admin import AdminRichKPIStrategy
from settings.theme import DesignSystem

dash.register_page(__name__, path='/ops-dashboard', title='Operaciones')
data_manager = DataManager()
table_ops_mgr = OpsTableStrategy()

gauge_ops_income = ChartWidget("go_income", OpsGaugeStrategy("Ingreso Viaje", "ingreso_viaje", "indigo"))
gauge_ops_trips = ChartWidget("go_trips", OpsGaugeStrategy("Viajes", "viajes", "green", prefix=""))
gauge_ops_kms = ChartWidget("go_kms", OpsGaugeStrategy("Kilómetros", "kilometros", "yellow", prefix=""))

chart_ops_inc_comp = ChartWidget("co_inc_comp", OpsComparisonStrategy("Ingresos 2025 vs 2024", "ingresos_anual", "indigo"))
chart_ops_trips_comp = ChartWidget("co_trips_comp", OpsComparisonStrategy("Viajes 2025 vs 2024", "viajes_anual", "green"))
chart_ops_mix = ChartWidget("co_mix", OpsPieStrategy())
chart_ops_unit_bal = ChartWidget("co_unit_bal", BalanceUnitStrategy())

kpi_ops_avg_trip = SmartWidget("ko_avg_trip", AdminRichKPIStrategy("operaciones", "ingreso_viaje", "Ingreso x Viaje", "tabler:truck-delivery", "indigo", sub_section="promedios"))
kpi_ops_avg_unit = SmartWidget("ko_avg_unit", AdminRichKPIStrategy("operaciones", "ingreso_unit", "Ingreso x Unidad", "tabler:engine", "green", sub_section="promedios"))
kpi_ops_units_qty = SmartWidget("ko_units", AdminRichKPIStrategy("operaciones", "unidades_utilizadas", "Unidades Utilizadas", "tabler:truck", "yellow", sub_section="promedios"))
kpi_ops_clients_qty = SmartWidget("ko_clients", AdminRichKPIStrategy("operaciones", "clientes_servidos", "Clientes Servidos", "tabler:users", "indigo", sub_section="promedios"))

WIDGET_REGISTRY = {
    "go_income": gauge_ops_income, "go_trips": gauge_ops_trips, "go_kms": gauge_ops_kms,
    "co_inc_comp": chart_ops_inc_comp, "co_trips_comp": chart_ops_trips_comp,
    "co_mix": chart_ops_mix, "co_unit_bal": chart_ops_unit_bal,
    "ko_avg_trip": kpi_ops_avg_trip, "ko_avg_unit": kpi_ops_avg_unit,
    "ko_units": kpi_ops_units_qty, "ko_clients": kpi_ops_clients_qty
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()
    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="ops-smart-modal", size="lg", centered=True, children=[html.Div(id="ops-modal-content")]),
        
        dmc.Paper(p="md", withBorder=True, mb="lg", children=[
            dmc.SimpleGrid(cols={"base": 2, "md": 5}, spacing="xs", children=[ # type: ignore
                dmc.Select(label="Año", data=["2025"], value="2025", size="xs"),
                dmc.Select(label="Mes", data=["septiembre"], value="septiembre", size="xs"),
                dmc.Select(label="Área", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Unidad", data=["Todas"], value="Todas", size="xs"),
                dmc.Select(label="Cliente", data=["Todas"], value="Todas", size="xs"),
            ])
        ]),

        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="xl", children=[ # type: ignore
            gauge_ops_income.render(ctx), gauge_ops_trips.render(ctx), gauge_ops_kms.render(ctx)
        ]),
        
        dmc.SimpleGrid(cols={"base": 1, "md": 2}, spacing="lg", mb="xl", children=[ # type: ignore
            chart_ops_inc_comp.render(ctx), chart_ops_trips_comp.render(ctx)
        ]),
        
        dmc.SimpleGrid(cols={"base": 1, "md": 2}, spacing="lg", mb="xl", children=[ # type: ignore
            chart_ops_mix.render(ctx), chart_ops_unit_bal.render(ctx)
        ]),

        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[# type: ignore
                dmc.Paper(p="md", withBorder=True, radius="md", children=[
                    dmc.Group(justify="space-between", mb="md", children=[
                        dmc.Text("Utilización de Flota", fw="bold", size="xs"),
                        dmc.Anchor(DashIconify(icon="tabler:map-2", width=20), href="/ops-routes", underline="never")
                    ]),
                    dmc.Center(dmc.Stack(align="center", gap=0, children=[
                        DashIconify(icon="tabler:truck-loading", width=48, color=DesignSystem.SUCCESS[5]),
                        dmc.Text("92% Cargado", fw="bold", size="xl", c="green")
                    ])),
                    dmc.ProgressRoot(size="xl", mt="md", children=[
                        dmc.ProgressSection(value=92, color="green", children=[dmc.ProgressLabel("92%")]),
                        dmc.ProgressSection(value=8, color="gray", children=[dmc.ProgressLabel("8%")])
                    ])
                ])
            ]),
            dmc.GridCol(span={"base": 12, "md": 8}, children=[# type: ignore
                dmc.Tabs(value="rutas", children=[
                    dmc.TabsList([dmc.TabsTab("Rutas Cargado", value="rutas"), dmc.TabsTab("Rutas Vacío", value="vacio")]),
                    dmc.TabsPanel(table_ops_mgr.render_rutas(ctx), value="rutas", pt="xs"),
                    dmc.TabsPanel(dmc.Text("Sin datos de rutas vacías", py="xl", ta="center", c="gray"), value="vacio")
                ])
            ])
        ]),

        dmc.Text("PROMEDIOS OPERATIVOS", fw="bold", mb="md", size="sm", c="gray"),
        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "md": 4}, spacing="sm", mb="xl", children=[# type: ignore
            kpi_ops_avg_trip.render(ctx), kpi_ops_avg_unit.render(ctx), 
            kpi_ops_units_qty.render(ctx), kpi_ops_clients_qty.render(ctx)
        ]),

        dmc.Paper(p="md", withBorder=True, children=[
            dmc.Tabs(value="cliente", children=[
                dmc.TabsList([
                    dmc.TabsTab("Ingreso Cliente", value="cliente"), 
                    dmc.TabsTab("Ingreso Operador", value="operador"), 
                    dmc.TabsTab("Ingreso Unidad", value="unidad")
                ]),
                dmc.TabsPanel(table_ops_mgr.render_tabbed_table(ctx, "cliente"), value="cliente", pt="md"),
                dmc.TabsPanel(table_ops_mgr.render_tabbed_table(ctx, "operador"), value="operador", pt="md"),
                dmc.TabsPanel(table_ops_mgr.render_tabbed_table(ctx, "unidad"), value="unidad", pt="md"),
            ])
        ]),
        dmc.Space(h=50)
    ])

@callback(
    Output("ops-smart-modal", "opened"), Output("ops-smart-modal", "title"), Output("ops-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_ops_dashboard_modal(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"]# type: ignore
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title", "Detalle"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update