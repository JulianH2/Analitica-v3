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
        layout = getattr(self.strategy, 'layout', {})
        fig_height = h if h else layout.get("height", 280)

        if fig:
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                autosize=True,
                margin=dict(t=30, b=10, l=10, r=10)
            )

        return dmc.Paper(
            p="xs",
            radius=layout.get("radius", "md"), 
            withBorder=True, 
            shadow="xs",
            style={
                "height": fig_height, 
                "display": "flex", 
                "flexDirection": "column", 
                "backgroundColor": "transparent", 
                "overflow": "hidden"
            },
            children=[
                dmc.Group(justify="space-between", mb=5, children=[
                    dmc.Group(gap=6, children=[
                        DashIconify(
                            icon=config_data.get("icon", self.strategy.icon), 
                            color=getattr(self.strategy, 'hex_color', '#94a3b8'), 
                            width=16
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
                        config={'displayModeBar': 'hover', 'responsive': True, 'displaylogo': False},
                        style={"height": "100%", "width": "100%"},
                    )
                )
            ]
        )