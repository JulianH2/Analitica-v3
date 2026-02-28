import dash_mantine_components as mantine
from dash import dcc, html
from dash_iconify import DashIconify
from typing import Any
from design_system import DesignSystem as DS, Colors, Typography, ComponentSizes, dmc as ds_token
from components.card_wrapper import make_card
import math


class ChartWidget:
    def __init__(self, widget_id: str, strategy: Any, height: int | None = None):
        self.widget_id = widget_id
        self.strategy = strategy
        self._height = height

    def render(self, data_context: Any, h=None, theme="light"):
        self.theme = theme
        fig = self.strategy.get_figure(data_context, theme=theme)
        config_data = self.strategy.get_card_config(data_context)
        layout = getattr(self.strategy, "layout", {})

        _HEADER_H = 42
        fig_height = h if h else (self._height or layout.get("height", ComponentSizes.CHART_HEIGHT_MD))
        if fig and hasattr(fig, "layout") and isinstance(fig.layout.height, (int, float)):
            natural_h = int(fig.layout.height)
            if isinstance(fig_height, int) and (natural_h + _HEADER_H) > fig_height:
                fig_height = natural_h + _HEADER_H

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

        content_h = (fig_height - _HEADER_H) if isinstance(fig_height, int) else None
        content_height_style = f"{content_h}px" if content_h is not None else "calc(100% - 42px)"

        return make_card(
            children=[
                self._create_header(config_data, icon_color, is_dark),
                html.Div(
                    style={
                        "height": content_height_style,
                        "width": "100%",
                        "position": "relative",
                        "overflow": "visible" if is_pie else "hidden",
                    },
                    children=graph_content,
                ),
            ],
            height=height_style,
            is_dark=is_dark,
            overflow="visible" if is_pie else "hidden",
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
        is_hbar = any(getattr(t, "orientation", "") == "h" for t in fig.data)

        _HEADER_H = 42
        plotly_h = (fig_height - _HEADER_H) if isinstance(fig_height, int) else None
        _is_dark = self.theme == "dark"
        _tmpl = "zam_dark" if _is_dark else "zam_light"
        _bg = Colors.BG_DARK_CARD if _is_dark else Colors.BG_LIGHT_CARD

        if is_pie:
            fig.layout.height = plotly_h
            fig.update_layout(
                autosize=True,
                template=_tmpl,
                paper_bgcolor=_bg,
                plot_bgcolor=_bg,
                showlegend=False,
            )
            return

        current_t = getattr(fig.layout.margin, "t", None) or 0
        current_r = getattr(fig.layout.margin, "r", None) or 0
        current_l = getattr(fig.layout.margin, "l", None) or 0

        if is_hbar:
            current_b = getattr(fig.layout.margin, "b", None) or 25
            fig.update_layout(
                autosize=True,
                template=_tmpl,
                paper_bgcolor=_bg,
                plot_bgcolor=_bg,
                height=plotly_h,
                margin=dict(
                    t=max(20, current_t),
                    b=max(25, current_b),
                    l=max(10, current_l),
                    r=max(80, current_r),
                ),
                yaxis=dict(type="category", autorange="reversed", automargin=True),
                xaxis=dict(side="top", automargin=True, tickformat="$,.0f", showgrid=True, zeroline=False),
            )
            fig.layout.yaxis.type = "category"
            fig.layout.yaxis.autorange = "reversed"
        else:
            fig.layout.height = plotly_h
            existing_xtype = getattr(fig.layout.xaxis, "type", None)
            xaxis_opts: dict = {"automargin": True}
            if existing_xtype == "category":
                xaxis_opts["type"] = "category"
            fig.update_layout(
                autosize=True,
                template=_tmpl,
                paper_bgcolor=_bg,
                plot_bgcolor=_bg,
                margin=dict(t=max(20, current_t), b=25, l=40, r=10),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                ),
                xaxis=xaxis_opts,
            )
            fig.update_yaxes(automargin=True)

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
            p="sm",
            mb=4,
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