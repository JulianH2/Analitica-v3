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
            p="sm", 
            radius="md", 
            withBorder=True, 
            shadow="sm", 
            mb="sm",
            style={"overflow": "hidden", "minWidth": 0},
            children=[
                dmc.Group(justify="space-between", mb="xs", children=[
                    dmc.Text(config.get("title"), fw="bold", size="xs", c="dimmed", tt="uppercase"), # type: ignore
                    
                    dmc.ActionIcon(
                        DashIconify(icon="tabler:maximize"), 
                        variant="subtle", 
                        color="gray", 
                        size="xs",
                        id={"type": "open-smart-detail", "index": self.widget_id} 
                    )
                ]),
                
                dcc.Graph(
                    id={"type": "interactive-graph", "index": self.widget_id},
                    figure=fig, 
                    config={'displayModeBar': False, 'responsive': True},
                    style={"width": "100%", "height": "auto"} 
                )
            ]
        )