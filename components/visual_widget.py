import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from typing import Any
from settings.theme import DesignSystem
import math

class ChartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context: Any, h=None):
        fig = self.strategy.get_figure(data_context)
        config_data = self.strategy.get_card_config(data_context)
        layout = getattr(self.strategy, 'layout', {})
        fig_height = h if h else layout.get("height", 280)

        valid_fig = False
        if fig and hasattr(fig, 'data') and len(fig.data) > 0:
            try:
                has_valid_points = False
                for trace in fig.data:
                    for attr in ['x', 'y', 'values', 'lat', 'lon', 'value']:
                        if hasattr(trace, attr):
                            data_vals = getattr(trace, attr)
                            
                            if attr == 'value' and isinstance(data_vals, (int, float)):
                                if not math.isnan(data_vals):
                                    has_valid_points = True
                                    break
                    
                            elif data_vals and isinstance(data_vals, (list, tuple)):
                                valid_subset = [
                                    v for v in data_vals 
                                    if v is not None and isinstance(v, (int, float)) and not math.isnan(v)
                                ]
                                if len(valid_subset) > 0:
                                    has_valid_points = True
                                    break
                    if has_valid_points: break
                
                if has_valid_points:
                    valid_fig = True
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        autosize=True,
                        margin=dict(t=30, b=10, l=10, r=10)
                    )
            except Exception:
                valid_fig = False

        icon_color = getattr(self.strategy, 'hex_color', '#94a3b8')
        if not icon_color.startswith("#"):
            icon_color = DesignSystem.COLOR_MAP.get(icon_color, '#94a3b8')

        if valid_fig:
            graph_content = dcc.Graph(
                id={"type": "interactive-graph", "index": self.widget_id},
                figure=fig, 
                config={'displayModeBar': 'hover', 'responsive': True, 'displaylogo': False},
                style={"height": "100%", "width": "100%"},
            )
        else:
            graph_content = dmc.Center(
                dmc.Stack(gap=5, align="center", children=[
                    DashIconify(icon="tabler:chart-off", width=30, color="gray"),
                    dmc.Text("Sin datos disponibles", size="xs", c="dimmed") # type: ignore
                ]),
                style={"height": "100%", "opacity": 0.7}
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
                            icon=config_data.get("icon", getattr(self.strategy, 'icon', "tabler:chart-bar")), 
                            color=icon_color, 
                            width=16
                        ),
                        dmc.Text(
                            config_data.get("title", getattr(self.strategy, 'title', "Gráfica")), 
                            fw=700, size="xs", c="dimmed", tt="uppercase"  # type: ignore
                        ),
                    ]),
                    dmc.ActionIcon(
                        DashIconify(icon="tabler:maximize"), variant="subtle", color="gray", size="sm",
                        id={"type": "open-smart-detail", "index": self.widget_id} 
                    ) if getattr(self.strategy, 'has_detail', False) else html.Div()
                ]),
                html.Div(
                    style={"flex": 1, "minHeight": 0, "width": "100%"},
                    children=graph_content
                )
            ]
        )