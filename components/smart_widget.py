import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from settings.theme import DesignSystem, SemanticColors
from typing import Any

class SmartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context: Any, mode: str = "auto"):
        try:
            config = self.strategy.get_card_config(data_context)
        except Exception as e:
            print(f"Error rendering widget {self.widget_id}: {e}")
            config = {"title": "Error", "value": "Err"}

        layout = getattr(self.strategy, 'layout', {})
        card_height = layout.get("height", 195)
        
        figure = None
        if hasattr(self.strategy, 'get_figure'):
            try: figure = self.strategy.get_figure(data_context)
            except: pass

        val = config.get("main_value") or config.get("value")

        if figure and val and not config.get("is_chart", False):
            return self._render_combined(config, figure, card_height)
        
        if config.get("is_chart") or (figure and not val):
            return self._render_chart_only(config, figure, card_height)

        return self._render_scalar(config, card_height)

    def _render_scalar(self, config, height):
        header = self._build_header(config)
        footer = self._build_footer(config)
        
        display_val = config.get("main_value") or config.get("value", "---")

        main_value = dmc.Center(style={"flex": 1, "flexDirection": "column"}, children=[
            dmc.Text(display_val, fw=800, fz="2rem", lh="1", ta="center", c=SemanticColors.TEXT_MAIN), # type: ignore
        ])

        return dmc.Paper(
            p="md", radius="md", withBorder=True, shadow="sm",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT},
            children=dmc.Stack(justify="space-between", h="100%", gap=0, children=[
                header,
                main_value,
                footer
            ])
        )

    def _render_combined(self, config, figure, height):
        header = self._build_header(config)
        footer = self._build_footer(config)
        display_val = config.get("main_value") or config.get("value", "---")

        if figure:
            figure.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=height - 90, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        return dmc.Paper(
            p="sm", radius="md", withBorder=True, shadow="sm",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT},
            children=dmc.Grid(gutter="xs", align="stretch", style={"height": "100%"}, children=[
                dmc.GridCol(span=5, children=dmc.Stack(justify="space-between", h="100%", gap=0, children=[
                    header, dmc.Text(display_val, fw=800, fz="1.5rem", lh=1, mt=5), footer # type: ignore
                ])),
                dmc.GridCol(span=7, children=html.Div(style={"height": "100%", "width": "100%"}, children=[
                    dcc.Graph(figure=figure, config={'displayModeBar': False}, style={"height": "100%", "width": "100%"})
                ]))
            ])
        )

    def _render_chart_only(self, config, figure, height):
        header = self._build_header(config)
        if figure:
            figure.update_layout(margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        return dmc.Paper(
            p="sm", radius="md", withBorder=True, shadow="sm",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT},
            children=dmc.Stack(h="100%", gap=0, children=[
                header,
                html.Div(style={"flex": 1, "marginTop": "-10px", "minHeight": 0}, children=dcc.Graph(figure=figure, config={'displayModeBar': False, 'responsive': True}, style={"height": "100%", "width": "100%"}))
            ])
        )

    def _build_header(self, config):
        title = config.get("title") or getattr(self.strategy, 'title', "")
        icon = config.get("icon") or getattr(self.strategy, 'icon', "tabler:chart-bar")
        color = config.get("color") or config.get("main_color") or getattr(self.strategy, 'color', "gray")
        hex_color = DesignSystem.COLOR_MAP.get(color, color) if not color.startswith("#") else color

        return dmc.Group(justify="space-between", align="flex-start", w="100%", mb=0, children=[
            dmc.Text(title, size="xs", c="dimmed", fw="bold", tt="uppercase"), # type: ignore
            dmc.ThemeIcon(DashIconify(icon=icon, width=18), variant="light", color=hex_color, size="md", radius="md") # type: ignore
        ])

    def _build_footer(self, config):
        if config.get("extra_rows"):
            rows = []
            for item in config.get("extra_rows"):
                color = item.get("color", "dimmed")
                if color == "green": color = "green"
                elif color == "red": color = "red"
                elif color == "blue": color = "blue"
                rows.append(dmc.Group(justify="space-between", w="100%", children=[
                    dmc.Text(item.get("label"), size="10px", c="dimmed", fw=500), # type: ignore
                    dmc.Text(item.get("value"), size="10px", fw=700, c=color) # type: ignore
                ]))
            return dmc.Card(p=5, radius="sm", bg="gray.0", children=dmc.Stack(gap=2, w="100%", children=rows)) # type: ignore
    
        footer_items = []
        is_inverse = config.get("inverse", False)
        
        def make_row(label, value, delta=None, delta_fmt=None, is_inverse=False):
            if value in (None, "---"):
                return None

            badge = None
            badge_text = None
            badge_color = "gray"

            try:
                delta_num = float(delta) # type: ignore
                badge_text = delta_fmt if delta_fmt else f"{'+' if delta_num > 0 else ''}{delta_num:.1f}%"
                
                if delta_num > 0:
                    badge_color = "red" if is_inverse else "green"
                elif delta_num < 0:
                    badge_color = "green" if is_inverse else "red"
                else:
                    badge_color = "gray"
            except (TypeError, ValueError):
                if delta:
                    badge_text = str(delta)
                    badge_color = "gray"

            if badge_text:
                badge = dmc.Badge(
                    badge_text,
                    color=badge_color,
                    variant="light",
                    size="xs",
                    style={
                        "padding": "0 4px",
                        "height": "16px",
                        "fontSize": "9px",
                    },
                )

            return dmc.Group(
                justify="space-between",
                w="100%",
                children=[
                    dmc.Group(
                        gap=4,
                        children=[
                            dmc.Text(label, size="10px", c="dimmed"), # type: ignore
                            dmc.Text(str(value), size="11px", fw=600, c="dark"), # type: ignore
                        ],
                    ),
                    badge,
                ],
            )

        prev_row = make_row(config.get("label_prev_year", "Año Ant:"), config.get("vs_last_year_formatted"), config.get("vs_last_year_delta"), config.get("vs_last_year_delta_formatted"))
        if prev_row: footer_items.append(prev_row)

        if config.get("target_formatted"):
             meta_row = make_row("Meta:", config.get("target_formatted"), config.get("trend"), config.get("target_delta_formatted"))
             if meta_row: footer_items.append(meta_row)

        ytd_row = make_row("YTD:", config.get("ytd_formatted"), config.get("ytd_delta"), config.get("ytd_delta_formatted"))
        if ytd_row: footer_items.append(ytd_row)

        if not footer_items and config.get("trend") is not None:
             trend = config.get("trend")
             trend_txt = config.get("trend_text") or "vs Meta"
             
             try:
                 trend_val = float(trend)
                 badge_txt = f"{trend_val:+.1f}%"
                 badge_color = "blue"
             except (TypeError, ValueError):
                 badge_txt = str(trend)
                 badge_color = "gray"

             return dmc.Group(gap=4, mt=10, children=[
                 dmc.Badge(badge_txt, color=badge_color, variant="light", size="xs"),
                 dmc.Text(trend_txt, size="10px", c="dimmed") # type: ignore
             ])

        if not footer_items: return html.Div(style={"height": "10px"})

        return dmc.Stack(gap=4, w="100%", mt=8, children=footer_items)