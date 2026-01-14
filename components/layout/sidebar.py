from flask import session
import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from typing import Any

def render_sidebar(collapsed=False, current_theme="dark", current_db="db_1", active_path="/"):
    user_data = session.get("user", {})
    user_role = user_data.get("role", "user")
    full_name = user_data.get("name", "Usuario")
    initials = "".join([n[0] for n in full_name.split()[:2]]).upper() if full_name else "U"
    
    theme_icon = "tabler:sun" if current_theme == "dark" else "tabler:moon"
    theme_color = "yellow" if current_theme == "dark" else "indigo"

    def get_section_styles(href, is_active):
        colors = {
            "/": {"main": "#94a3b8", "light": "rgba(148, 163, 184, 0.15)"},
            "ops": {"main": "#228be6", "light": "rgba(34, 139, 230, 0.2)"},
            "taller": {"main": "#40c057", "light": "rgba(64, 192, 87, 0.2)"},
            "admin": {"main": "#fd7e14", "light": "rgba(253, 126, 20, 0.2)"}
        }
        
        section = "main"
        if href.startswith("/ops"): section = "ops"
        elif href.startswith("/taller"): section = "taller"
        elif href.startswith("/admin"): section = "admin"
        elif href == "/": section = "/"
        
        config = colors.get(section, colors["/"])
        
        if not is_active:
            return {"color": "gray", "style": {"borderRadius": "8px", "marginBottom": "4px"}}
            
        return {
            "color": config["main"],
            "style": {
                "borderRadius": "0 8px 8px 0",
                "marginBottom": "4px",
                "borderLeft": f"5px solid {config['main']}",
                "background": f"linear-gradient(90deg, {config['light']} 0%, rgba(0,0,0,0) 100%)",
                "fontWeight": 700
            }
        }

    menu_structure = [
        {"type": "link", "label": "Dashboard Principal", "href": "/", "icon": "tabler:layout-dashboard"},
        {"type": "divider", "label": "Módulos"},
        {
            "type": "group", "label": "OPERACIONES", "icon": "tabler:steering-wheel",
            "children": [
                {"label": "Control Operativo", "href": "/ops-dashboard", "icon": "tabler:dashboard"},
                {"label": "Rendimiento", "href": "/ops-performance", "icon": "tabler:gauge"},
                {"label": "Costos", "href": "/ops-costs", "icon": "tabler:coin"},
                {"label": "Rutas", "href": "/ops-routes", "icon": "tabler:map-pin"},
            ]
        },
        {
            "type": "group", "label": "MANTENIMIENTO", "icon": "tabler:tool",
            "children": [
                {"label": "Dashboard Taller", "href": "/taller-dashboard", "icon": "tabler:activity"},
                {"label": "Disponibilidad", "href": "/taller-availability", "icon": "tabler:clock-play"},
                {"label": "Compras", "href": "/taller-purchases", "icon": "tabler:shopping-cart"},
                {"label": "Almacén", "href": "/taller-inventory", "icon": "tabler:packages"},
            ]
        },
        {
            "type": "group", "label": "ADMINISTRACIÓN", "icon": "tabler:building-bank",
            "children": [
                {"label": "Facturación", "href": "/admin-collection", "icon": "tabler:file-invoice"},
                {"label": "Cuentas x Pagar", "href": "/admin-payables", "icon": "tabler:file-dollar"},
                {"label": "Bancos", "href": "/admin-banks", "icon": "tabler:wallet"},
            ]
        }
    ]

    def render_link(item):
        is_active = active_path == item["href"]
        cfg = get_section_styles(item["href"], is_active)
        link = dmc.NavLink(
            label=item["label"] if not collapsed else None,
            leftSection=DashIconify(icon=item["icon"], width=20),
            href=item["href"],
            active="exact" if is_active else None,
            variant="filled" if is_active else "subtle",
            color=cfg["color"],
            style=cfg["style"]
        )
        return dmc.Tooltip(label=item["label"], position="right", children=link) if collapsed else link

    def render_group(group):
        group_hrefs = [c["href"] for c in group["children"]]
        is_group_active = any(active_path == h for h in group_hrefs)
        cfg = get_section_styles(group_hrefs[0], is_group_active)
        
        children = [
            dmc.NavLink(
                label=child["label"],
                leftSection=DashIconify(icon=child["icon"], width=18),
                href=child["href"],
                active="exact" if active_path == child["href"] else None,
                variant="subtle",
                color=cfg["color"] if active_path == child["href"] else "gray",
                style={"borderRadius": "8px"}
            ) for child in group["children"]
        ]
        
        nav_group = dmc.NavLink(
            label=group["label"] if not collapsed else None,
            leftSection=DashIconify(icon=group["icon"], width=20),
            children=children if not collapsed else None,
            opened=is_group_active and not collapsed,
            active="exact" if is_group_active else None,
            variant="light" if is_group_active else "subtle",
            color=cfg["color"],
            style=cfg["style"] if not collapsed else {"borderRadius": "8px", "marginBottom": "4px"}
        )

        if collapsed:
            menu_items = [dmc.MenuItem(c["label"], href=c["href"], leftSection=DashIconify(icon=c["icon"])) for c in group["children"]]
            return dmc.Menu(
                trigger="hover", position="right-start", offset=15,
                children=[dmc.MenuTarget(nav_group), dmc.MenuDropdown([dmc.MenuLabel(group["label"]), *menu_items])]
            )
        return nav_group

    content = []
    for item in menu_structure:
        if item["type"] == "divider":
            content.append(dmc.Divider(my="sm", label=item["label"] if not collapsed else None))
        elif item["type"] == "link":
            content.append(render_link(item))
        elif item["type"] == "group":
            content.append(render_group(item))

    db_options: Any = [{"label": "Base Principal", "value": "db_1"}, {"label": "Base Auditoría", "value": "db_2"}]
    db_selector = dmc.Select(
        id="db-selector",
        data=db_options,
        value=current_db,
        leftSection=DashIconify(icon="tabler:database", width=16),
        size="xs", radius="md", variant="filled",
        style={"display": "block"
               #if (user_role == "admin" and not collapsed) else "none"
                , "marginBottom": "10px"}
    )

    return dmc.Stack(
        justify="space-between", h="100%", p="xs",
        children=[
            dmc.ScrollArea(style={"flex": 1}, children=dmc.Stack(gap=0, children=content)),
            dmc.Stack(gap="xs", children=[
                dmc.Divider(),
                db_selector,
                dmc.Group(justify="center" if collapsed else "space-between", px=10, children=[
                    dmc.Text("Tema", size="sm") if not collapsed else None,
                    dmc.ActionIcon(id="theme-toggle", variant="light", color=theme_color, size="lg", children=DashIconify(icon=theme_icon, width=20))
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
                        dmc.Anchor("Salir", href="/logout", size="xs", c="red", refresh=True)
                    ], style={"display": "none" if collapsed else "block"})
                ])
            ])
        ]
    )