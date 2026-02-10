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
        
        height_style = f"{fig_height}px" if isinstance(fig_height, int) else fig_height

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
                    
                    plotly_height = None if height_style == "100%" else (fig_height if isinstance(fig_height, int) else None)
                    
                    # FIX CRÍTICO 1: Separación entre barras (25% - muy clara)
                    # FIX CRÍTICO 2: Overflow controlado con cliponaxis
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        autosize=True,
                        height=plotly_height,
                        margin=dict(t=25, b=30, l=40, r=15),
                        font=dict(size=10),
                        bargap=0.25,  # 25% de separación - MUY VISIBLE
                        bargroupgap=0.18,  # 18% entre grupos
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=9)
                        ),
                        xaxis=dict(
                            tickfont=dict(size=9),
                            title_font=dict(size=10)
                        ),
                        yaxis=dict(
                            tickfont=dict(size=9),
                            title_font=dict(size=10)
                        )
                    )
                    
                    # FIX CRÍTICO 3: Evitar que las barras se salgan del contenedor
                    fig.update_xaxes(fixedrange=True)
                    fig.update_yaxes(fixedrange=True)
                    
            except Exception:
                valid_fig = False

        icon_color = getattr(self.strategy, 'hex_color', '#94a3b8')
        if not icon_color.startswith("#"):
            icon_color = DesignSystem.COLOR_MAP.get(icon_color, '#94a3b8')

        if valid_fig:
            graph_content = dcc.Graph(
                id={"type": "interactive-graph", "index": self.widget_id},
                figure=fig, 
                config={
                    'displayModeBar': 'hover', 
                    'responsive': True, 
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                },
                style={"height": "100%", "width": "100%"},
            )
        else:
            graph_content = dmc.Center(
                dmc.Stack(gap=5, align="center", children=[
                    DashIconify(icon="tabler:chart-off", width=24, color="gray"),
                    dmc.Text("Sin datos disponibles", size="xs", c="dimmed")
                ]),
                style={"height": "100%", "opacity": 0.7}
            )

        # SIN CAMBIOS en estructura - solo contenido interior optimizado
        return dmc.Paper(
            p="xs",
            radius=layout.get("radius", "md"),
            withBorder=True,
            shadow="xs",
            style={
                "height": height_style,
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "transparent",
                "overflow": "hidden"  # FIX: Evitar desbordamiento
            },
            children=[
                dmc.Group(
                    justify="space-between",
                    mb=4,
                    wrap="nowrap",
                    gap="xs",
                    children=[
                        dmc.Group(
                            gap=4,
                            wrap="nowrap",
                            style={"flex": 1, "overflow": "hidden"},
                            children=[
                                DashIconify(
                                    icon=config_data.get("icon", getattr(self.strategy, "icon", "tabler:chart-bar")),
                                    color=icon_color,
                                    width=14,
                                    style={"flexShrink": 0}
                                ),
                                dmc.Text(
                                    config_data.get("title", getattr(self.strategy, "title", "Gráfica")),
                                    fw=600,
                                    size="xs",
                                    c="dimmed",
                                    tt="uppercase",
                                    style={
                                        "whiteSpace": "nowrap",
                                        "overflow": "hidden",
                                        "textOverflow": "ellipsis"
                                    }
                                ),
                            ]
                        ),

                        dmc.Group(
                            gap=2,
                            wrap="nowrap",
                            style={"flexShrink": 0},
                            children=[
                                dmc.ActionIcon(
                                    DashIconify(icon="tabler:layers-linked", width=14),
                                    variant="subtle",
                                    color="gray",
                                    size="xs",
                                    id={"type": "open-smart-drawer", "index": self.widget_id},
                                    style={"flexShrink": 0}
                                ) if getattr(self.strategy, "has_detail", False) else html.Div()
                            ]
                        ) if getattr(self.strategy, "has_detail", False) else html.Div()
                    ]
                ),

                html.Div(
                    style={
                        "flex": 1,
                        "minHeight": 0,
                        "width": "100%",
                        "overflow": "hidden"  # FIX: Contener gráfica dentro del widget
                    },
                    children=graph_content
                )
            ]
        )