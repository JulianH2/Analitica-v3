import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import DesignSystem as DS, dmc as _dmc
from components.card_wrapper import make_card


class TableWidget:
    def __init__(self, widget_id, strategy):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, ctx, theme="dark", mode="dashboard"):
        has_detail = getattr(self.strategy, "has_detail", False)
        is_dark = theme == "dark"

        config = self.strategy.get_card_config(ctx)
        title = config.get("title", "Tabla")
        icon = config.get("icon", "tabler:table")
        icon_color = self._get_icon_color()

        table_content = self.strategy.render(ctx, mode=mode, theme=theme)

        # Search input — placed in the header before the expand icon
        # Only added when the strategy uses AgGrid (has screen_id + key attrs)
        screen_id = getattr(self.strategy, "screen_id", None)
        key = getattr(self.strategy, "key", None)
        search_input = html.Div()
        if screen_id and key:
            search_input = dmc.TextInput(
                id={"type": "ag-quick-search", "index": f"{screen_id}-{key}"},
                placeholder="Buscar...",
                size="xs",
                radius="xl",
                leftSection=DashIconify(icon="tabler:search", width=14),
                style={"width": "180px"},
                styles={"input": {
                    "backgroundColor": "rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.03)",
                }},
            )

        header = dmc.Group(
            justify="space-between",
            p="sm",
            mb=4,
            wrap="nowrap",
            children=[
                dmc.Group(
                    gap=8,
                    wrap="nowrap",
                    children=[
                        DashIconify(icon=icon, color=icon_color, width=18),
                        search_input,
                    ],
                ),
                dmc.Group(
                    gap=6,
                    wrap="nowrap",
                    children=[
                        
                        dmc.ActionIcon(
                            DashIconify(icon="tabler:zoom-in", width=16),
                            variant="subtle",
                            color="blue",
                            size="sm",
                            n_clicks=0,
                            id={"type": "open-smart-drawer", "index": self.widget_id},
                            style={"flexShrink": 0},
                        )
                        if has_detail
                        else html.Div(),
                    ],
                ),
            ],
        )

        return make_card(
            children=[
                header,
                html.Div(
                    style={
                        "flex": 1,
                        "minHeight": 0,
                        "width": "100%",
                        "position": "relative",
                        "overflow": "auto",
                    },
                    children=table_content,
                ),
            ],
            height="100%",
            is_dark=is_dark,
        )

    def _get_icon_color(self) -> str:
        icon_color = getattr(self.strategy, "hex_color", DS.NEXA_GRAY)
        if not icon_color.startswith("#"):
            icon_color = DS.COLOR_MAP.get(icon_color, DS.NEXA_GRAY)
        return icon_color
