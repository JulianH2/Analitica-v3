import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import DesignSystem as DS


class TableWidget:
    def __init__(self, widget_id, strategy):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, ctx, theme="dark", mode="dashboard"):
        has_detail = getattr(self.strategy, "has_detail", False)

        config = self.strategy.get_card_config(ctx)
        title = config.get("title", "Tabla")
        icon = config.get("icon", "tabler:table")
        icon_color = self._get_icon_color()

        table_content = self.strategy.render(ctx, mode=mode, theme=theme)

        header = dmc.Group(
            justify="space-between",
            px="sm",
            pt="xs",
            mb="sm",
            wrap="nowrap",
            children=[
                dmc.Group(
                    gap=8,
                    wrap="nowrap",
                    children=[
                        DashIconify(icon=icon, color=icon_color, width=18),
                        dmc.Text(
                            title,
                            fw=700, # type: ignore
                            size="xs",
                            c="dimmed", # type: ignore
                            tt="uppercase",
                            style={"fontSize": "10px"},
                        ),
                    ],
                ),
                dmc.ActionIcon(
                    DashIconify(icon="tabler:zoom-in", width=16),
                    variant="subtle",
                    color="blue",
                    size="sm",
                    id={"type": "open-smart-drawer", "index": self.widget_id},
                )
                if has_detail
                else html.Div(),
            ],
        )

        return dmc.Paper(
            p=0,
            radius="md",
            withBorder=False,
            shadow=None,
            style={
                "height": "100%",
                "display": "flex",
                "flexDirection": "column",
                "backgroundColor": "transparent",
                "overflow": "hidden",
            },
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
        )

    def _get_icon_color(self) -> str:
        icon_color = getattr(self.strategy, "hex_color", DS.NEXA_GRAY)
        if not icon_color.startswith("#"):
            icon_color = DS.COLOR_MAP.get(icon_color, DS.NEXA_GRAY)
        return icon_color
