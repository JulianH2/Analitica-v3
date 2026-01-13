from flask import session
import dash_mantine_components as dmc
from dash import html, dcc
from dash_iconify import DashIconify
from settings.theme import DesignSystem

def render_sidebar(collapsed=False, current_theme="dark"):
    user_data = session.get("user", {})
    full_name = user_data.get("name", "Usuario")
    initials = "".join([n[0] for n in full_name.split()[:2]]).upper() if full_name else "U"
    
    theme_icon = "tabler:sun" if current_theme == "dark" else "tabler:moon"
    theme_color = "yellow" if current_theme == "dark" else "indigo"

    menu_structure = [
        {"type": "link", "label": "Dashboard Principal", "href": "/", "icon": "tabler:layout-dashboard"},
        {"type": "divider", "label": "Módulos"},
        
        {
            "type": "group", 
            "label": "OPERACIONES", 
            "icon": "tabler:steering-wheel",
            "children": [
                {"label": "Control Operativo", "href": "/ops-dashboard", "icon": "tabler:dashboard"},
                {"label": "Rendimiento", "href": "/ops-performance", "icon": "tabler:gauge"},
                {"label": "Costos", "href": "/ops-costs", "icon": "tabler:coin"},
                {"label": "Rutas", "href": "/ops-routes", "icon": "tabler:map-pin"},
            ]
        },
        
        {
            "type": "group", 
            "label": "MANTENIMIENTO", 
            "icon": "tabler:tool",
            "children": [
                {"label": "Dashboard Taller", "href": "/taller-dashboard", "icon": "tabler:activity"},
                {"label": "Disponibilidad", "href": "/taller-availability", "icon": "tabler:clock-play"},
                {"label": "Compras", "href": "/taller-purchases", "icon": "tabler:shopping-cart"},
                {"label": "Almacén", "href": "/taller-inventory", "icon": "tabler:packages"},
            ]
        },
        
        {
            "type": "group", 
            "label": "ADMINISTRACIÓN", 
            "icon": "tabler:building-bank",
            "children": [
                {"label": "Facturación", "href": "/admin-collection", "icon": "tabler:file-invoice"},
                {"label": "Cuentas x Pagar", "href": "/admin-payables", "icon": "tabler:file-dollar"},
                {"label": "Bancos", "href": "/admin-banks", "icon": "tabler:wallet"},
            ]
        }
    ]
    def get_icon(icon):
        return DashIconify(icon=icon, width=20)

    def render_link(item):
        link = dmc.NavLink(
            label=item["label"] if not collapsed else None,
            leftSection=get_icon(item["icon"]),
            href=item["href"],
            active="exact",
            variant="subtle",
            color="indigo",
            style={"borderRadius": "8px", "marginBottom": "4px"}
        )
        if collapsed:
            return dmc.Tooltip(
                label=item["label"], 
                position="right", 
                withArrow=True,
                children=link
            )
        return link

    def render_group_expanded(group):
        children = [
            dmc.NavLink(
                label=child["label"],
                leftSection=get_icon(child["icon"]),
                href=child["href"],
                active="exact",
                variant="subtle",
                color="indigo",
                style={"borderRadius": "8px"}
            ) for child in group["children"]
        ]
        return dmc.NavLink(
            label=group["label"],
            leftSection=get_icon(group["icon"]),
            children=children,
            childrenOffset=28,
            variant="subtle",
            opened=True,
            color="indigo",
            style={"borderRadius": "8px", "fontWeight": 500}
        )
        
    def render_group_collapsed(group):
        menu_items = [
            dmc.MenuItem(
                child["label"],
                href=child["href"],
                leftSection=get_icon(child["icon"])
            ) for child in group["children"]
        ]
        
        return dmc.Menu(
            trigger="hover",
            position="right-start",
            offset=15,
            withArrow=True,
            children=[
                dmc.MenuTarget(
                    dmc.NavLink(
                        label=None,
                        leftSection=get_icon(group["icon"]),
                        variant="subtle",
                        style={"borderRadius": "8px", "marginBottom": "4px"}
                    )
                ),
                dmc.MenuDropdown([
                    dmc.MenuLabel(group["label"]), 
                    *menu_items
                ])
            ]
        )

    content = []
    for item in menu_structure:
        if item["type"] == "divider":
            content.append(dmc.Divider(my="sm", label=item["label"] if not collapsed else None))
        elif item["type"] == "link":
            content.append(render_link(item))
        elif item["type"] == "group":
            if collapsed:
                content.append(render_group_collapsed(item))
            else:
                content.append(render_group_expanded(item))

    return dmc.Stack(
        justify="space-between", h="100%", p="xs",
        children=[
            dmc.ScrollArea(
                style={"flex": 1, "overflow": "visible"}, 
                children=dmc.Stack(gap=0, children=content)
            ),
            
            dmc.Stack(gap="xs", children=[
                dmc.Divider(),
                dmc.Group(justify="center" if collapsed else "space-between", px=10, children=[
                    dmc.Text("Tema", size="sm") if not collapsed else None,
                    dmc.ActionIcon(
                        id="theme-toggle", variant="light", color=theme_color, size="lg",
                        children=DashIconify(icon=theme_icon, width=20)
                    )
                ]),
                dmc.ActionIcon(
                    id="btn-sidebar-toggle", variant="subtle", color="gray", size="lg",
                    children=DashIconify(icon="tabler:chevrons-right" if collapsed else "tabler:chevrons-left", width=20),
                    style={"alignSelf": "center" if collapsed else "flex-end"}
                ),
                dmc.Group(gap="xs", justify="center" if collapsed else "flex-start", children=[
                    dmc.Avatar(initials, radius="xl", color="indigo"),
                    html.Div([
                        dmc.Text(full_name, size="sm", fw="bold"),
                        dmc.Anchor("Cerrar Sesión", href="/logout", size="xs", c="red", refresh=True)
                    ], style={"display": "none" if collapsed else "block"})
                ])
            ])
        ]
    )