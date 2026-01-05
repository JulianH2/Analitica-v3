import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

def render_sidebar(collapsed=False):
    
    def get_icon(icon):
        return DashIconify(icon=icon, width=20)

    def render_link(label, href, icon):
        return dmc.NavLink(
            label=label if not collapsed else None,
            leftSection=get_icon(icon),
            href=href,
            active=False,
            variant="subtle",
            color="indigo",
            style={"borderRadius": "8px", "marginBottom": "4px"}
        )

    def render_group(label, icon, children):
        return dmc.NavLink(
            label=label if not collapsed else None,
            leftSection=get_icon(icon),
            childrenOffset=28,
            children=children,
            variant="subtle",
            opened=True, 
            color="indigo",
            style={"borderRadius": "8px", "fontWeight": 500}
        )

    return dmc.Stack(
        justify="space-between",
        h="100%",
        p="xs",
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"flex": 1},
                children=dmc.Stack(gap=0, children=[
                    
                    render_link("Dashboard Principal", "/", "tabler:layout-dashboard"),
                    
                    dmc.Divider(my="sm", label="Módulos" if not collapsed else None),

                    render_group("OPERACIONES", "tabler:steering-wheel", [
                        render_link("Control Operativo", "/ops-dashboard", "tabler:dashboard"),
                        render_link("Rendimiento", "/ops-performance", "tabler:gauge"),
                        render_link("Costos", "/ops-costs", "tabler:coin"),
                    ]),
                        render_group("MANTENIMIENTO", "tabler:tool", [
                        render_link("Mantenimiento", "/taller-dashboard", "tabler:activity"),
                        render_link("Análisis de Disponibilidad", "/taller-availability", "tabler:clock-play"),
                        render_link("Compras",  "/taller-tires", "tabler:circle"), 
                        render_link("Almacén", "/taller-inventory", "tabler:packages"),
            
                    ]),
                        render_group("ADMINISTRACIÓN", "tabler:building-bank", [
                        render_link("Facturación y Cobranza", "/admin-collection", "tabler:file-invoice"),
                        render_link("Cuentas por Pagar", "/admin-payables", "tabler:file-dollar"),
                        render_link("Bancos", "/admin-banks", "tabler:wallet"),
                    ]),

                ])
            ),
            dmc.Stack(gap="xs", children=[
                dmc.Divider(),
                dmc.ActionIcon(
                    DashIconify(icon="tabler:chevrons-right" if collapsed else "tabler:chevrons-left", width=18),
                    id="btn-sidebar-toggle",
                    variant="light",
                    color="gray",
                    size="lg",
                    style={"alignSelf": "center" if collapsed else "flex-end"}
                ),
                dmc.Group(
                    gap="xs",
                    justify="center" if collapsed else "flex-start",
                    children=[
                        dmc.Avatar("AD", radius="xl", color="indigo"),
                        html.Div([
                            dmc.Text("Admin User", size="sm", fw=500),
                            dmc.Text("TINSA", size="xs", c="dimmed")
                        ], style={"display": "none" if collapsed else "block"}),
                    ]
                )
            ])
        ]
    )