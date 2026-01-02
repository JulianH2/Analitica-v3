import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from services.data_manager import DataManager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from components.table_widget import TableWidget

from strategies.financial import IncomeStrategy, CostStrategy, MarginStrategy, BalanceStrategy
from strategies.operational import TripsStrategy, FleetEfficiencyStrategy, UnitCostStrategy
from strategies.charts import MainTrendChartStrategy
from strategies.tabular import MainTableStrategy

dash.register_page(__name__, path='/', title='Executive Summary')

data_manager = DataManager()

MAIN_CHART = ChartWidget("w_main_trend", MainTrendChartStrategy())
MAIN_TABLE = TableWidget(MainTableStrategy())

WIDGET_CONFIG = [
    SmartWidget("w_income", IncomeStrategy()),
    SmartWidget("w_costs", CostStrategy()),
    SmartWidget("w_margin", MarginStrategy()),
    SmartWidget("w_balance", BalanceStrategy()),
    SmartWidget("w_trips", TripsStrategy()),
    SmartWidget("w_fuel", FleetEfficiencyStrategy()),
    SmartWidget("w_unit_cost", UnitCostStrategy()),
]

WIDGET_REGISTRY = {w.widget_id: w for w in WIDGET_CONFIG}

def layout():
    data_context = data_manager.get_data()

    return dmc.Container(fluid=True, children=[
        dmc.Modal(
            id="home-smart-modal",
            size="xl", centered=True, zIndex=10000,
            children=[html.Div(id="home-modal-content")]
        ),
        dmc.Group(justify="space-between", mb="lg", children=[
            dmc.Stack(gap=0, children=[
                dmc.Title("Executive Summary", order=2, c="indigo"),
                dmc.Text("Strategic Overview & Operational KPIs", size="sm", c="dimmed")
            ]),
            dmc.Button(
                "Refresh Data",
                leftSection=DashIconify(icon="tabler:refresh"),
                variant="light", color="indigo", id="btn-global-refresh"
            )
        ]),
        MAIN_CHART.render(data_context),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 3, "lg": 4},
            spacing="lg",
            children=[w.render(data_context) for w in WIDGET_CONFIG]
        ),
        MAIN_TABLE.render()
    ])

@callback(
    Output("home-smart-modal", "opened"),
    Output("home-smart-modal", "title"),
    Output("home-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_widget_click(n_clicks):
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