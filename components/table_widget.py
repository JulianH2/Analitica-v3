import dash_mantine_components as dmc
from dash_iconify import DashIconify

class TableWidget:
    def __init__(self, strategy):
        self.strategy = strategy

    def render(self, title="Detalle de Datos", **kwargs):
        table_component = self.strategy.render(**kwargs)
        
        return dmc.Paper(
            p="md", radius="md", withBorder=True, shadow="sm", mt="xl",
            children=[
                dmc.Group(justify="space-between", mb="md", children=[
                    dmc.Group([
                        DashIconify(icon="tabler:list-details", width=24, color="#228be6"),
                        dmc.Text(title, fw="bold", size="lg") 
                    ]),
                    dmc.Badge("Vista Completa", variant="light", color="gray")
                ]),
                dmc.ScrollArea(
                    h="auto",
                    mah=500,
                    offsetScrollbars="present",
                    children=table_component
                )
            ]
        )