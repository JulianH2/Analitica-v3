import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import DataManager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.table_widget import TableWidget 

from strategies.operational import TripsStrategy, FleetEfficiencyStrategy, UnitCostStrategy, UnitUtilizationStrategy, ClientImpactStrategy
from strategies.tabular import OpsUnitTableStrategy
from strategies.charts import OpsFleetStatusStrategy, OpsUnitPerformanceStrategy, OpsRoutesChartStrategy

dash.register_page(__name__, path='/ops-dashboard', title='Operations Control')

data_manager = DataManager()

CHART_FLEET = ChartWidget("w_ops_fleet_pie", OpsFleetStatusStrategy())
CHART_UNITS = ChartWidget("w_ops_unit_perf", OpsUnitPerformanceStrategy())
CHART_ROUTES = ChartWidget("w_ops_routes_bar", OpsRoutesChartStrategy())

OPS_TABLE = TableWidget(OpsUnitTableStrategy())

WIDGET_CONFIG = [
    SmartWidget("w_ops_trips", TripsStrategy()),
    SmartWidget("w_ops_units", UnitUtilizationStrategy()),
    SmartWidget("w_ops_fuel", FleetEfficiencyStrategy()),
    SmartWidget("w_ops_cost", UnitCostStrategy()),
]

WIDGET_REGISTRY = {w.widget_id: w for w in WIDGET_CONFIG}

def layout():
    data_context = data_manager.get_data()

    return dmc.Container(fluid=True, children=[
        dmc.Modal(
            id="ops-smart-modal",
            size="xl", centered=True, zIndex=10000,
            children=[html.Div(id="ops-modal-content")]
        ),
        dmc.Group(justify="space-between", mb="lg", children=[
            dmc.Stack(gap=0, children=[
                dmc.Title("Operations Center", order=2, c="orange"),
                dmc.Text("Real-time Fleet & Route Monitoring", size="sm", c="dimmed")
            ]),
            dmc.Group([
                dmc.Badge("Operational", color="green", variant="dot"),
                dmc.ActionIcon(DashIconify(icon="tabler:refresh"), variant="default", size="lg", id="btn-ops-refresh")
            ])
        ]),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 2, "lg": 4},
            spacing="lg",
            mb="xl",
            children=[w.render(data_context) for w in WIDGET_CONFIG]
        ),
        dmc.Grid(gutter="lg", mb="xl", children=[
            dmc.GridCol(span={"base": 12, "md": 4}, children=[
                CHART_FLEET.render(data_context)
            ]),
            dmc.GridCol(span={"base": 12, "md": 8}, children=[
                dmc.Tabs(value="units", children=[
                    dmc.TabsList([
                        dmc.TabsTab("Unit Efficiency", value="units", leftSection=DashIconify(icon="tabler:bus")),
                        dmc.TabsTab("Top Routes", value="routes", leftSection=DashIconify(icon="tabler:route")),
                    ]),
                    dmc.TabsPanel(value="units", pt="xs", children=CHART_UNITS.render(data_context)),
                    dmc.TabsPanel(value="routes", pt="xs", children=CHART_ROUTES.render(data_context)),
                ])
            ])
        ]),
        dmc.Text("Unit Breakdown", fw=700, size="lg", mb="sm"),
        OPS_TABLE.render()
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
        content = widget.get_detail(data_context)
        
        config = widget.strategy.get_card_config(data_context)
        modal_title = dmc.Group([
            DashIconify(icon=config.get("icon"), color=config.get("color"), width=24),
            dmc.Text(config.get("title"), fw=700, size="lg")
        ])
        
        return True, modal_title, content
    
    return no_update, no_update, no_update