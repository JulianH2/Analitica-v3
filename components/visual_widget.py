import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from typing import Any
from settings.theme import DesignSystem

class ChartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context: Any, h=None):
        fig = self.strategy.get_figure(data_context)
        config_data = self.strategy.get_card_config(data_context)
        
        fig_height = fig.layout.height if fig and fig.layout.height else DesignSystem.STANDARD_CHART_HEIGHT
        container_height = h if h is not None else fig_height

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=True
        )

        return dmc.Paper(
            p="md", radius="md", withBorder=True, shadow="sm",
            style={
                "height": container_height, 
                "display": "flex", 
                "flexDirection": "column", 
                "backgroundColor": "transparent", 
                "overflow": "hidden"
            },
            children=[
                dmc.Group(justify="space-between", mb="xs", children=[
                    dmc.Group(gap="sm", children=[
                        DashIconify(
                            icon=config_data.get("icon", self.strategy.icon), 
                            color=getattr(self.strategy, 'hex_color', '#94a3b8'), 
                            width=18
                        ),
                        dmc.Text(
                            config_data.get("title", self.strategy.title), 
                            fw=700, size="xs", c="dimmed", tt="uppercase" # type: ignore
                        ),
                    ]),
                    dmc.ActionIcon(
                        DashIconify(icon="tabler:maximize"), variant="subtle", color="gray", size="sm",
                        id={"type": "open-smart-detail", "index": self.widget_id} 
                    ) if getattr(self.strategy, 'has_detail', False) else html.Div()
                ]),
                html.Div(
                    style={"flex": 1, "minHeight": 0, "width": "100%"},
                    children=dcc.Graph(
                        id={"type": "interactive-graph", "index": self.widget_id},
                        figure=fig, 
                        config={
                            'displayModeBar': 'hover',
                            'responsive': True,
                            'toImageButtonOptions': {
                                'format': 'png',
                                'filename': f'export_{self.widget_id}',
                                'scale': 2 
                            },
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['lasso2d', 'select2d'], 
                        },
                        style={"height": "100%", "width": "100%"},
                    )
                )
            ]
        )