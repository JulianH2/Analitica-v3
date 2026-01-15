import dash_mantine_components as dmc
from dash_iconify import DashIconify
from settings.theme import DesignSystem, SemanticColors
from typing import Any

class SmartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context: Any):
        config = self.strategy.get_card_config(data_context)
        layout = getattr(self.strategy, 'layout', {})
        is_simple = config.get("is_simple", False)
        card_height = layout.get("height", 195) # type: ignore

        extra_details = dmc.Stack(gap=2, mt=8, children=[ # type: ignore
            dmc.Group(justify="space-between", children=[
                dmc.Text(config.get("label_mes_title", "Este Mes:"), size="10px", c="dimmed"), # type: ignore
                dmc.Text(config.get("label_mes", "N/A"), size="10px", fw=700, c="gray") # type: ignore
            ]) if config.get("label_mes") else None,
            dmc.Group(justify="space-between", children=[
                dmc.Text("Acumulado:", size="10px", c="dimmed"), # type: ignore
                dmc.Text(config.get("label_ytd", "N/A"), size="10px", fw=700, c="gray") # type: ignore
            ]) if config.get("label_ytd") else None,
        ])

        trend = config.get("trend", 0)
        reverse = config.get("reverse_trend", False)
        is_positive = trend >= 0
        trend_color = SemanticColors.INGRESO if (is_positive ^ reverse) else SemanticColors.EGRESO
        trend_icon = "tabler:trending-up" if is_positive else "tabler:trending-down"

        return dmc.Paper(
            p="sm", radius="md", withBorder=True, shadow="xs",
            style={"height": card_height, "backgroundColor": "transparent"},
            children=dmc.Stack(justify="space-between", h="100%", gap=0, children=[
                dmc.Group(justify="space-between", align="flex-start", w="100%", children=[
                    dmc.Text(config.get("title", self.strategy.title), size="xs", c="dimmed", fw="bold", tt="uppercase"), # type: ignore
                    dmc.ThemeIcon(
                        DashIconify(icon=config.get("icon", self.strategy.icon), width=18),
                        variant="light", color=self.strategy.color, size="md", radius="md"
                    )
                ]),
                dmc.Center(style={"flex": 1, "flexDirection": "column", "padding": "10px 0"}, children=[ # type: ignore
                    dmc.Text(config.get("value", "0"), fw=800, style={"fontSize": "1.6rem", "lineHeight": "1"}, ta="center"), # type: ignore
                    extra_details
                ]),
                None if is_simple else dmc.Group(justify="space-between", align="flex-end", w="100%", children=[
                    dmc.Stack(gap=0, align="flex-start", children=[
                        dmc.Badge(
                            f"{trend:+.1f}%", color=trend_color, variant="light", # type: ignore
                            leftSection=DashIconify(icon=trend_icon, width=10), size="xs"
                        ) if trend != 0 else None,
                        dmc.Text(config.get("meta_text", ""), size="10px", c="dimmed") # type: ignore
                    ]),
                    dmc.Button(
                        "Detalles", id={"type": "open-smart-detail", "index": self.widget_id},
                        variant="subtle", color="gray", size="compact-xs", 
                        style={"width": "90px"}, 
                        rightSection=DashIconify(icon="tabler:maximize", width=12)
                    ) if getattr(self.strategy, 'has_detail', False) else None
                ])
            ])
        )