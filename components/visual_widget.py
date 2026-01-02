import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

class ChartWidget:
    def __init__(self, widget_id, strategy):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context):
        fig = self.strategy.get_figure(data_context)
        config = self.strategy.get_card_config(data_context)

        return dmc.Paper(
            p="md", radius="md", withBorder=True, shadow="sm", mb="xl",
            children=[
                dmc.Group(justify="space-between", mb="sm", children=[
                    dmc.Text(config.get("title"), fw=700, size="lg", c="dark"),
                    dmc.ActionIcon(
                        DashIconify(icon="tabler:dots"), 
                        variant="subtle", color="gray"
                    )
                ]),
                dcc.Graph(
                    figure=fig, 
                    config={'displayModeBar': False, 'responsive': True},
                    style={"width": "100%"}
                )
            ]
        )