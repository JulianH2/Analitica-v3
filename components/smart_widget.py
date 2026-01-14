import dash_mantine_components as dmc
from dash_iconify import DashIconify
from settings.theme import DesignSystem, SemanticColors
from typing import Any, List

class SmartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context: Any):
        config = self.strategy.get_card_config(data_context)
        
        trend = config.get("trend", 0)
        reverse = config.get("reverse_trend", False)
        is_positive = trend >= 0
        
        if reverse:
            trend_color = SemanticColors.EGRESO if is_positive else SemanticColors.INGRESO
        else:
            trend_color = SemanticColors.INGRESO if is_positive else SemanticColors.EGRESO
            
        trend_icon = "tabler:trending-up" if is_positive else "tabler:trending-down"
        card_color = DesignSystem.COLOR_MAP.get(self.strategy.color, "indigo")

        content: List[Any] = [
            dmc.Group(justify="space-between", mb="xs", children=[
                dmc.Text(config.get("title", self.strategy.title), size="xs", c="dimmed", fw="bold", tt="uppercase"), # type: ignore
                dmc.ThemeIcon(
                    DashIconify(icon=config.get("icon", self.strategy.icon), width=20), 
                    variant="light", 
                    color=self.strategy.color, 
                    size="lg", 
                    radius="md"
                )
            ]),
            dmc.Group(align="flex-end", gap="xs", children=[
                dmc.Text(config.get("value", "0"), fw="bold", size="xl", style={"fontSize": "1.8rem"}),             
                dmc.Badge(
                    f"{trend:+.1f}%", 
                    color=trend_color,  # type: ignore
                    variant="light", 
                    leftSection=DashIconify(icon=trend_icon)
                ) if "trend" in config or trend != 0 else None
            ]),
            dmc.Text(config.get("meta_text", ""), size="xs", c="dimmed", mt=5) # type: ignore
        ]

        if getattr(self.strategy, 'has_detail', False):
            content.extend([
                dmc.Divider(my="sm", variant="dashed"),
                dmc.Button(
                    "Ver Detalles",
                    id={"type": "open-smart-detail", "index": self.widget_id},
                    variant="subtle", color="gray", size="xs", fullWidth=True,
                    rightSection=DashIconify(icon="tabler:maximize", width=16)
                )
            ])

        return dmc.Paper(p="lg", radius="md", withBorder=True, shadow="sm", style={"backgroundColor": "transparent"}, children=content)