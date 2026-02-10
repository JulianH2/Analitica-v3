import dash_mantine_components as dmc
from dash_iconify import DashIconify
from settings.theme import DesignSystem

class TableWidget:
    def __init__(self, strategy):
        self.strategy = strategy

    def render(self, data_context, title="Detalle de Datos", **kwargs):
        table_component = self.strategy.render(data_context, **kwargs)
        
        return dmc.Paper(
            p=8,  # Reducido de "md"
            radius="md",
            withBorder=True,
            shadow="sm",
            mt="lg",  # Reducido de "xl"
            children=[
                dmc.Group(
                    justify="space-between",
                    mb="sm",  # Reducido de "md"
                    children=[
                        dmc.Group(
                            gap=5,  # Reducido
                            children=[
                                DashIconify(icon="tabler:list-details", width=22, color=DesignSystem.BRAND[5]),  # Reducido de 24
                                dmc.Text(title, fw="bold", size="lg") 
                            ]
                        ),
                        dmc.Badge("Vista Completa", variant="light", color="gray", size="sm")
                    ]
                ),
                html.Div(
                    style={"height": "auto", "maxHeight": "480px", "overflowY": "auto"},  # Altura fija sin ScrollArea
                    children=table_component
                )
            ]
        )