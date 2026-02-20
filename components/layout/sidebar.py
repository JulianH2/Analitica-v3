from design_system import dmc as _dmc
from flask import session
import dash_mantine_components as dmc
from dash import html, dcc
from dash_iconify import DashIconify
from typing import Any

def render_sidebar(collapsed=False, current_theme="dark", current_db="db_1", active_path="/"):
    user_data = session.get("user", {})
    user_role = user_data.get("role", "user")
    full_name = user_data.get("name", "Usuario")
    initials = "".join([n[0] for n in full_name.split()[:2]]).upper() if full_name else "U"
    
    theme_icon = "tabler:sun" if current_theme == "dark" else "tabler:moon"
    theme_color = "yellow" if current_theme == "dark" else "indigo"

    if not collapsed:
        logo_content = dmc.Group(
            justify="center",
            mb="md", 
            mt="xl",
            children=[
                html.Img(
                    src="/assets/AnaliticaGerencial-LOGO.svg", 
                    style={"height": "80px", "width": "auto", "objectFit": "contain"}
                )
            ]
        )
    else:
        logo_content = dmc.Stack(
            align="center",
            mb="md",
            mt="xl",
            children=[
                html.Img(
                    src="/assets/AnaliticaGerencial-LOGO.svg", 
                    style={"height": "50px", "width": "auto"}
                )
            ]
        )

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
        
        base_style = {
            "textDecoration": "none",
            "padding": "10px 12px",
            "display": "block",
            "borderRadius": "8px",
            "marginBottom": "4px",
            "cursor": "pointer",
            "transition": "background-color 0.2s ease"
        }

        if not is_active:
            base_style.update({"color": "#C1C2C5" if current_theme == "dark" else "#495057"})
            return {"color": "gray", "style": base_style, "bg": "transparent"}
        
        base_style.update({
            "color": config["main"],
            "borderRadius": "0 8px 8px 0",
            "borderLeft": f"5px solid {config['main']}",
            "background": f"linear-gradient(90deg, {config['light']} 0%, rgba(0,0,0,0) 100%)",
            "fontWeight": 700
        }) # type: ignore
        return {"color": config["main"], "style": base_style, "bg": config["light"]}

    menu_structure = [
    {"type": "link", "label": "Dashboard Principal", "href": "/", "icon": "tabler:layout-dashboard"},
    {"type": "divider", "label": "Módulos"},
    {
        "type": "group",
        "label": "OPERACIONES",
        "icon": "tabler:steering-wheel",
        "children": [
            {"label": "Dashboard Operativo", "href": "/operational-dashboard", "icon": "tabler:dashboard"},
            {"label": "Rendimiento", "href": "/operational-performance", "icon": "tabler:gauge"},
            {"label": "Costos", "href": "/operational-costs", "icon": "tabler:coin"},
            {"label": "Rutas", "href": "/operational-routes", "icon": "tabler:map-pin"},
        ],
    },

    {
        "type": "group",
        "label": "MANTENIMIENTO",
        "icon": "tabler:tool",
        "children": [
            {"label": "Dashboard Taller", "href": "/workshop-dashboard", "icon": "tabler:activity"},
            {"label": "Disponibilidad", "href": "/workshop-availability", "icon": "tabler:clock-play"},
            {"label": "Compras", "href": "/workshop-purchases", "icon": "tabler:shopping-cart"},
            {"label": "Almacén", "href": "/workshop-inventory", "icon": "tabler:packages"},
        ],
    },

    {
        "type": "group",
        "label": "ADMINISTRACIÓN",
        "icon": "tabler:building-bank",
        "children": [
            {"label": "Facturación", "href": "/administration-receivables", "icon": "tabler:file-invoice"},
            {"label": "Cuentas por Pagar", "href": "/administration-payables", "icon": "tabler:file-dollar"},
            {"label": "Bancos", "href": "/administration-banks", "icon": "tabler:wallet"},
        ],
    },
]


    def render_link(item):
        is_active = active_path == item["href"]
        cfg = get_section_styles(item["href"], is_active)
        link_content = dmc.Group(
            gap="sm",
            children=[
                DashIconify(icon=item["icon"], width=20, color=cfg["color"] if is_active else "inherit"),
                dmc.Text(item["label"], size="sm", fw=_dmc(700 if is_active else 400)) if not collapsed else None
            ]
        )
        
        link = dcc.Link(
            link_content,
            href=item["href"],
            style=cfg["style"],
            className="nav-link-hover"
        )
        
        return dmc.Tooltip(label=item["label"], position="right", children=link) if collapsed else link

    def render_group(group):
        group_hrefs = [c["href"] for c in group["children"]]
        is_group_active = any(active_path == h for h in group_hrefs)
        cfg = get_section_styles(group_hrefs[0], is_group_active)
        
        children = []
        for child in group["children"]:
            is_child_active = active_path == child["href"]
            child_cfg = get_section_styles(child["href"], is_child_active)
            child_content = dmc.Group(
                gap="sm",
                children=[
                    DashIconify(icon=child["icon"], width=18, color=child_cfg["color"] if is_child_active else "inherit"),
                    dmc.Text(child["label"], size="sm", fw=_dmc(700 if is_child_active else 400))
                ]
            )
            
            children.append(
                dcc.Link(
                    child_content, 
                    href=child["href"], 
                    style={**child_cfg["style"], "marginLeft": "10px"}
                )
            )
        
        nav_group = dmc.NavLink(
            label=group["label"] if not collapsed else None,
            leftSection=DashIconify(icon=group["icon"], width=20),
            children=children if not collapsed else None,
            opened=is_group_active and not collapsed,
            active="exact" if is_group_active else None,
            variant="light" if is_group_active else "subtle",
            color=_dmc(cfg["color"] if isinstance(cfg["color"], str) else "gray"),
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

    raw_databases = session.get("databases", [])
    
    db_options = []
    if raw_databases:
        for db in raw_databases:
            nombre = db.get("nombre_cliente") or db.get("nombre") or "Desconocido"
            bd_id = db.get("base_de_datos") or db.get("id_bd")
            if bd_id: 
                db_options.append({"label": nombre, "value": bd_id})
    
    if not db_options:
        db_options = [{"label": "Sin bases asignadas", "value": "error", "disabled": True}]

    valid_values = [opt['value'] for opt in db_options if not opt.get('disabled', False)]
    
    if current_db and current_db in valid_values:
        final_value = current_db
    elif valid_values:
        final_value = valid_values[0] 
    else:
        final_value = None

    show_selector = not collapsed

    db_selector = dmc.Select(
        id="db-selector",
        data=_dmc(db_options),
        value=final_value,
        leftSection=DashIconify(icon="tabler:database", width=16),
        size="xs", radius="md", variant="filled",
        style={"display": "block" if show_selector else "none", "marginBottom": "10px"}
    )

    return dmc.Stack(
        justify="space-between", h="100%", p="xs",
        children=[

            logo_content,


            dmc.ScrollArea(
                style={"flex": 1}, 
                children=dmc.Stack(gap=0, children=content)
            ),


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