import dash_mantine_components as mantine
from dash import dcc, html
from dash_iconify import DashIconify
from typing import Any
from design_system import DesignSystem as DS, Typography, ComponentSizes, dmc as ds_token
import math


class ChartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context: Any, h=None, theme="light"):
        self.theme = theme
        fig = self.strategy.get_figure(data_context, theme=theme)
        config_data = self.strategy.get_card_config(data_context)
        layout = getattr(self.strategy, "layout", {})

        fig_height = h if h else layout.get("height", ComponentSizes.CHART_HEIGHT_MD)
        height_style = f"{fig_height}px" if isinstance(fig_height, int) else fig_height

        valid_fig = self._validate_figure(fig)
        icon_color = self._get_icon_color()

        if valid_fig:
            self._configure_figure(fig, fig_height)
            graph_content = self._create_graph_component(fig, fig_height)
        else:
            graph_content = self._create_empty_state()

        is_dark = theme == "dark"
        is_pie = valid_fig and any(getattr(t, "type", "") == "pie" for t in fig.data) if fig else False

        return mantine.Paper(
            p=0,
            radius="md",
            withBorder=True,
            shadow=None,
            style={
                "height": height_style,
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "transparent",
                "border": DS.CARD_BORDER_DARK if is_dark else DS.CARD_BORDER_LIGHT,
                "overflow": "visible" if is_pie else "hidden",
            },
            children=[
                self._create_header(config_data, icon_color, is_dark),
                html.Div(
                    style={
                        "flex": 1,
                        "minHeight": 0,
                        "width": "100%",
                        "position": "relative",
                        "overflow": "visible" if is_pie else "hidden",
                    },
                    children=graph_content,
                ),
            ],
        )

    def _validate_figure(self, fig) -> bool:
        if not fig or not hasattr(fig, "data") or len(fig.data) == 0:
            return False

        try:
            for trace in fig.data:
                for attr in ["x", "y", "values", "lat", "lon", "value"]:
                    if hasattr(trace, attr):
                        data_vals = getattr(trace, attr)

                        if attr == "value" and isinstance(data_vals, (int, float)):
                            if not math.isnan(data_vals):
                                return True

                        if data_vals and isinstance(data_vals, (list, tuple)):
                            valid_subset = [
                                v
                                for v in data_vals
                                if v is not None
                                and isinstance(v, (int, float))
                                and not math.isnan(v)
                            ]
                            if valid_subset:
                                return True

            return False
        except Exception:
            return False

    def _get_icon_color(self) -> str:
        icon_color = getattr(self.strategy, "hex_color", DS.NEXA_GRAY)
        if not icon_color.startswith("#"):
            icon_color = DS.COLOR_MAP.get(icon_color, DS.NEXA_GRAY)
        return icon_color

    def _configure_figure(self, fig, fig_height):
        is_pie = any(getattr(trace, "type", "") == "pie" for trace in fig.data)

        HEADER_HEIGHT = 40
        plotly_height = (fig_height - HEADER_HEIGHT) if isinstance(fig_height, int) else None

        fig.update_layout(
            autosize=True,
            height=plotly_height,
            template="zam_dark" if self.theme == "dark" else "zam_light",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        if not is_pie:
            fig.update_layout(
                margin=dict(t=5, b=25, l=40, r=10),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                ),
            )
            fig.update_xaxes(automargin=True)
            fig.update_yaxes(automargin=True)
        else:
            fig.update_layout(showlegend=False)

    def _create_graph_component(self, fig, fig_height):
        return dcc.Graph(
            id={"type": "interactive-graph", "index": self.widget_id},
            figure=fig,
            config={
                "displayModeBar": "hover",
                "responsive": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d", "zoom2d"],
            },
            style={"height": "100%", "width": "100%"},
        )

    def _create_empty_state(self):
        return mantine.Center(
            mantine.Stack(
                gap=5,
                align="center",
                children=[
                    DashIconify(icon="tabler:chart-off", width=24, color=DS.NEXA_GRAY),
                    mantine.Text(
                        "Sin datos disponibles",
                        size="xs",
                        c=ds_token("dimmed"),
                        style={"fontSize": f"{Typography.XS}px"},
                    ),
                ],
            ),
            style={"height": "100%", "opacity": 0.7},
        )

    def _create_header(self, config_data, icon_color, is_dark):
        has_detail = getattr(self.strategy, "has_detail", False)

        return mantine.Group(
            justify="space-between",
            px="sm",
            pt="xs",
            mb=5,
            wrap="nowrap",
            children=[
                mantine.Group(
                    gap=8,
                    wrap="nowrap",
                    children=[
                        DashIconify(
                            icon=config_data.get(
                                "icon",
                                getattr(self.strategy, "icon", "tabler:chart-bar"),
                            ),
                            color=icon_color,
                            width=18,
                        ),
                        mantine.Text(
                            config_data.get(
                                "title",
                                getattr(self.strategy, "title", "Gráfica"),
                            ),
                            fw=ds_token(700),
                            size="xs",
                            c=ds_token("dimmed"),
                            tt="uppercase",
                            style={"fontSize": "10px"},
                        ),
                    ],
                ),
                mantine.ActionIcon(
                    DashIconify(icon="tabler:layers-linked", width=16),
                    variant="subtle",
                    color="gray",
                    size="sm",
                    id={"type": "open-smart-drawer", "index": self.widget_id},
                )
                if has_detail
                else html.Div(),
            ],
        )