"""
Visual Widget (Chart Widget) - Actualizado con Design System
Widgets para gráficas con estilos según mockups
"""

import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from typing import Any
from design_system import DesignSystem as DS, Typography, ComponentSizes, Space
import math


class ChartWidget:
    """
    Widget para renderizar gráficas con estilo del design system
    """
    
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy
        

    def render(self, data_context: Any, h=None, theme="light"):
        self.theme = theme
        fig = self.strategy.get_figure(data_context, theme=theme)
        config_data = self.strategy.get_card_config(data_context)
        layout = getattr(self.strategy, 'layout', {})
        
        fig_height = h if h else layout.get("height", ComponentSizes.CHART_HEIGHT_MD)
        height_style = f"{fig_height}px" if isinstance(fig_height, int) else fig_height

        valid_fig = self._validate_figure(fig)
        icon_color = self._get_icon_color()
        
        if valid_fig:
            self._configure_figure(fig, fig_height)
            graph_content = self._create_graph_component(fig, height_style)
        else:
            graph_content = self._create_empty_state()

        is_dark = theme == "dark"
        
        return dmc.Paper(
            p=0,
            radius="md",
            withBorder=False,
            shadow="none",
            style={
                "height": height_style,
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "transparent",
                "overflow": "hidden"
            },
            children=[
                self._create_header(config_data, icon_color, is_dark),
                html.Div(
                    style={
                        "flex": 1,
                        "minHeight": 0,
                        "width": "100%",
                        "position": "relative",
                        "overflow": "hidden"
                    },
                    children=graph_content
                )
            ]
        )
        
    def _validate_figure(self, fig) -> bool:
        """Valida si la figura tiene datos válidos"""
        if not fig or not hasattr(fig, 'data') or len(fig.data) == 0:
            return False
            
        try:
            has_valid_points = False
            for trace in fig.data:
                for attr in ['x', 'y', 'values', 'lat', 'lon', 'value']:
                    if hasattr(trace, attr):
                        data_vals = getattr(trace, attr)
                        
                        # Valor escalar
                        if attr == 'value' and isinstance(data_vals, (int, float)):
                            if not math.isnan(data_vals):
                                has_valid_points = True
                                break
                
                        # Lista/tuple de valores
                        elif data_vals and isinstance(data_vals, (list, tuple)):
                            valid_subset = [
                                v for v in data_vals 
                                if v is not None and isinstance(v, (int, float)) and not math.isnan(v)
                            ]
                            if len(valid_subset) > 0:
                                has_valid_points = True
                                break
                if has_valid_points:
                    break
            
            return has_valid_points
                    
        except Exception:
            return False
    
    def _get_icon_color(self) -> str:
        """Obtiene color del icono desde la estrategia o usa default"""
        icon_color = getattr(self.strategy, 'hex_color', DS.NEXA_GRAY)
        if not icon_color.startswith("#"):
            icon_color = DS.COLOR_MAP.get(icon_color, DS.NEXA_GRAY)
        return icon_color
    
    def _configure_figure(self, fig, fig_height):
        # Detectamos si la gráfica es de tipo Pie/Donut
        is_pie = any(getattr(trace, 'type', '') == 'pie' for trace in fig.data)

        # Configuración Base
        fig.update_layout(
            autosize=True,
            height=None,
            template="zam_dark" if self.theme == "dark" else "zam_light",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        if is_pie:
            # DISEÑO PARA DONA: Gráfica izquierda, Info derecha
            fig.update_traces(domain=dict(x=[0, 0.55], y=[0, 1])) 
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=0.6,
                    itemsizing="constant"
                )
            )
        else:
            # DISEÑO NORMAL: Leyenda arriba
            fig.update_layout(
                margin=dict(t=5, b=25, l=40, r=10),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                )
            )
            fig.update_xaxes(automargin=True)
            fig.update_yaxes(automargin=True)
    
    def _create_graph_component(self, fig, height_style):
        """Crea el componente dcc.Graph"""
        return dcc.Graph(
            id={"type": "interactive-graph", "index": self.widget_id},
            figure=fig, 
            config={
                'displayModeBar': 'hover', 
                'responsive': True, 
                'displaylogo': False,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'zoom2d']
            },
            style={"height": "100%", "width": "100%"},
        )
    
    def _create_empty_state(self):
        """Crea estado vacío cuando no hay datos"""
        return dmc.Center(
            dmc.Stack(
                gap=5, 
                align="center", 
                children=[
                    DashIconify(
                        icon="tabler:chart-off", 
                        width=24, 
                        color=DS.NEXA_GRAY
                    ),
                    dmc.Text(
                        "Sin datos disponibles", 
                        size="xs", 
                        c="dimmed",
                        style={
                            "fontSize": f"{Typography.XS}px"
                        }
                    )
                ]
            ),
            style={"height": "100%", "opacity": 0.7}
        )

    def _create_header(self, config_data, icon_color, is_dark):
        has_detail = getattr(self.strategy, "has_detail", False)
        
        return dmc.Group(
            justify="space-between",
            px="sm",
            pt="xs",
            mb=5,
            wrap="nowrap",
            children=[
                dmc.Group(
                    gap=8,
                    wrap="nowrap",
                    children=[
                        DashIconify(
                            icon=config_data.get("icon", getattr(self.strategy, "icon", "tabler:chart-bar")),
                            color=icon_color,
                            width=18
                        ),
                        dmc.Text(
                            config_data.get("title", getattr(self.strategy, "title", "Gráfica")),
                            fw=700,
                            size="xs",
                            c="dimmed",
                            tt="uppercase",
                            style={"fontSize": "10px"}
                        ),
                    ]
                ),
                dmc.ActionIcon(
                    DashIconify(icon="tabler:layers-linked", width=16),
                    variant="subtle",
                    color="gray",
                    size="sm",
                    id={"type": "open-smart-drawer", "index": self.widget_id},
                ) if has_detail else html.Div()
            ]
        )