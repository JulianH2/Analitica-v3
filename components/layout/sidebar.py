import dash_mantine_components as dmc
from dash import html  # <--- FALTABA ESTA IMPORTACIÓN
from dash_iconify import DashIconify

def render_sidebar(collapsed=False):
    def get_icon(icon):
        return DashIconify(icon=icon, width=20)

    # --- HELPER PARA GRUPOS (Operaciones, Taller, Admin) ---
    def render_nav_group(label, icon, items):
        """
        Si está colapsado: Muestra un Menú Flotante al pasar el mouse.
        Si está extendido: Muestra un NavLink tipo Acordeón.
        """
        if collapsed:
            # MODO COLAPSADO: Menú flotante (Dropdown)
            return dmc.Menu(
                trigger="hover",
                position="right",
                offset=10,
                withArrow=True,
                arrowPosition="center",
                children=[
                    dmc.MenuTarget(
                        # Usamos NavLink vacío para mantener el estilo visual consistente
                        dmc.NavLink(
                            label=None,
                            leftSection=get_icon(icon),
                            variant="subtle",
                            color="indigo",
                            style={"borderRadius": "8px", "marginBottom": "4px", "justifyContent": "center"}
                        )
                    ),
                    dmc.MenuDropdown([
                        dmc.Text(label, size="xs", fw=700, c="dimmed", p="xs"), # Título del grupo
                        *[
                            dmc.MenuItem(
                                item["label"],
                                href=item["href"],
                                leftSection=get_icon(item["icon"])
                            ) for item in items
                        ]
                    ])
                ]
            )
        else:
            # MODO EXTENDIDO: Acordeón normal
            return dmc.NavLink(
                label=label,
                leftSection=get_icon(icon),
                childrenOffset=28,
                variant="subtle",
                opened=True, # Por defecto abierto para ver las opciones
                children=[
                    dmc.NavLink(
                        label=item["label"],
                        href=item["href"],
                        leftSection=get_icon(item["icon"]),
                        variant="subtle",
                        style={"borderRadius": "8px"}
                    ) for item in items
                ],
                style={"borderRadius": "8px", "marginBottom": "4px"}
            )

    # --- HELPER PARA LINKS SIMPLES (Home) ---
    def render_single_link(label, icon, href):
        link = dmc.NavLink(
            label="" if collapsed else label,
            leftSection=get_icon(icon),
            href=href,
            variant="subtle",
            active=True if href == "/" else False, # Lógica simple para ejemplo
            color="indigo",
            style={"borderRadius": "8px", "marginBottom": "4px", "justifyContent": "center" if collapsed else "flex-start"}
        )
        
        if collapsed:
            # Añadir Tooltip si está colapsado para saber qué es
            return dmc.Tooltip(
                label=label,
                position="right",
                withArrow=True,
                children=link
            )
        return link

    # --- ESTRUCTURA DEL SIDEBAR ---
    return dmc.Stack(
        justify="space-between",
        h="100%",
        p="xs",
        children=[
            # ZONA SUPERIOR (Scrollable)
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"flex": 1},
                children=dmc.Stack(gap=0, children=[
                    
                    # 1. RESUMEN EJECUTIVO
                    render_single_link("Resumen Ejecutivo", "tabler:layout-dashboard", "/"),
                    
                    dmc.Divider(my="sm"),

                    # 2. OPERACIONES
                    render_nav_group("Operaciones", "tabler:steering-wheel", [
                        {"label": "Tablero General", "href": "/ops-dashboard", "icon": "tabler:dashboard"},
                        {"label": "Rendimiento", "href": "/ops-performance", "icon": "tabler:gauge"},
                        {"label": "Costos", "href": "/ops-costs", "icon": "tabler:calculator"},
                    ]),

                    # 3. MANTENIMIENTO
                    render_nav_group("Mantenimiento", "tabler:tool", [
                        {"label": "Visión General", "href": "/taller-dashboard", "icon": "tabler:activity"},
                        {"label": "Disponibilidad", "href": "/taller-availability", "icon": "tabler:clock-play"},
                        {"label": "Inventario", "href": "/taller-inventory", "icon": "tabler:packages"},
                        {"label": "Llantas", "href": "/taller-tires", "icon": "tabler:circle"},
                    ]),

                    # 4. ADMINISTRACIÓN
                    render_nav_group("Finanzas", "tabler:building-bank", [
                        {"label": "Cobranza", "href": "/admin-collection", "icon": "tabler:cash-banknote"},
                        {"label": "Cuentas x Pagar", "href": "/admin-payables", "icon": "tabler:file-invoice"},
                        {"label": "Tesorería", "href": "/admin-banks", "icon": "tabler:wallet"},
                    ]),
                ])
            ),
            
            # ZONA INFERIOR (Usuario y Toggle)
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
                            dmc.Text("Administrator", size="xs", c="dimmed")
                        ], style={"display": "none" if collapsed else "block"}),
                    ]
                )
            ])
        ]
    )