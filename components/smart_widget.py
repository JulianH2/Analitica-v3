import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html

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
            color = "red" if is_positive else "green"
            icon = "tabler:trending-up" if is_positive else "tabler:trending-down"
        else:
            color = "green" if is_positive else "red"
            icon = "tabler:trending-up" if is_positive else "tabler:trending-down"

        return dmc.Paper(
            p="lg", radius="md", withBorder=True, shadow="sm",
            children=[
                dmc.Group(justify="space-between", mb="xs", children=[
                    dmc.Text(config.get("title"), size="xs", c="dimmed", fw=700, tt="uppercase"),
                    dmc.ThemeIcon(
                        DashIconify(icon=config.get("icon"), width=20), 
                        variant="light", 
                        color=config.get("color"), 
                        size="lg", 
                        radius="md"
                    )
                ]),
                dmc.Group(align="flex-end", gap="xs", children=[
                    dmc.Text(config.get("value"), fw=800, size="xl", style={"fontSize": "1.8rem"}),
                    dmc.Badge(
                        f"{trend:+.1f}%", 
                        color=color, 
                        variant="light", 
                        leftSection=DashIconify(icon=icon)
                    )
                ]),
                dmc.Text(config.get("meta_text"), size="xs", c="dimmed", mt=5),
                dmc.Divider(my="sm", variant="dashed"),
                dmc.Button(
                    "View Details",
                    id={"type": "open-smart-detail", "index": self.widget_id},
                    variant="subtle", color="gray", size="xs", fullWidth=True,
                    rightSection=DashIconify(icon="tabler:maximize", width=16)
                )
            ]
        )

    def get_detail(self, data_context):
        return self.strategy.render_detail(data_context)