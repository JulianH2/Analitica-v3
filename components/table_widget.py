import dash_mantine_components as dmc
from dash_iconify import DashIconify

class TableWidget:
    def __init__(self, strategy):
        self.strategy = strategy

    def render(self):
        table_component = self.strategy.render()
        
        return dmc.Paper(
            p="md", radius="md", withBorder=True, shadow="sm", mt="xl",
            children=[
                dmc.Group(justify="space-between", mb="md", children=[
                    dmc.Group([
                        DashIconify(icon="tabler:list-details", width=24, color="#228be6"),
                        dmc.Text("Detailed Operational Indicators", fw=700, size="lg")
                    ]),
                    dmc.Badge("Full View", variant="light", color="gray")
                ]),
                dmc.ScrollArea(
                    h=400,
                    offsetScrollbars=True,
                    children=table_component
                )
            ]
        )