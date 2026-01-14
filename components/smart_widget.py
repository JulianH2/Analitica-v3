import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html
from settings.theme import SemanticColors

class SmartWidget:
    def __init__(self, widget_id, strategy):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context):
        config = self.strategy.get_card_config(data_context)
        
        trend = config.get("trend", 0)
        reverse = config.get("reverse_trend", False)
        is_positive = trend >= 0
        if reverse:
            color = SemanticColors.EGRESO if is_positive else SemanticColors.INGRESO
            icon = "tabler:trending-up" if is_positive else "tabler:trending-down"
        else:
            color = SemanticColors.INGRESO if is_positive else SemanticColors.EGRESO
            icon = "tabler:trending-up" if is_positive else "tabler:trending-down"

        card_color = config.get("color", "indigo")
        if card_color == "brand": card_color = "indigo"
        if card_color == "warning": card_color = "yellow"
        if card_color == "danger": card_color = "red"
        if card_color == "success": card_color = "green"

        return dmc.Paper(
            p="lg", radius="md", withBorder=True, shadow="sm",
            children=[
                dmc.Group(justify="space-between", mb="xs", children=[
                    dmc.Text(config.get("title"), size="xs", c="gray", fw="bold", tt="uppercase"),
                    dmc.ThemeIcon(
                        DashIconify(icon=config.get("icon"), width=20), 
                        variant="light", 
                        color=card_color, 
                        size="lg", 
                        radius="md"
                    )
                ]),
                dmc.Group(align="flex-end", gap="xs", children=[
                    dmc.Text(config.get("value"), fw="bolder", size="xl", style={"fontSize": "1.8rem"}),             
                    dmc.Badge(
                        f"{trend:+.1f}%", 
                        color=color,  # type: ignore
                        variant="light", 
                        leftSection=DashIconify(icon=icon)
                    )
                ]),
                dmc.Text(config.get("meta_text"), size="xs", c="gray", mt=5),
                dmc.Divider(my="sm", variant="dashed"),
                dmc.Button(
                    "Ver Detalles",
                    id={"type": "open-smart-detail", "index": self.widget_id},
                    variant="subtle", color="gray", size="xs", fullWidth=True,
                    rightSection=DashIconify(icon="tabler:maximize", width=16)
                )
            ]
        )

    def get_detail(self, data_context):
        return self.strategy.render_detail(data_context)