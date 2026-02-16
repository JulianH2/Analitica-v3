import dash
from dash import html, callback, Input, Output, ALL, State, no_update, dcc, ctx as dash_ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from design_system import DesignSystem as DS, Typography
from services.drawer_data_service import DrawerDataService
from flask import session


def create_smart_drawer(drawer_id: str = "smart-drawer"):
    return html.Div(
        [
            dcc.Download(id=f"{drawer_id}-download"),
            dcc.Store(id=f"{drawer_id}-export-data"),
            dcc.Store(id=f"{drawer_id}-theme", data="dark"),
            html.Div(
                id=f"{drawer_id}-placeholder",
                style={"display": "none"},
                children=[dmc.ActionIcon(id=f"{drawer_id}-close", n_clicks=0)],
            ),
            dmc.Drawer(
                id=drawer_id,
                position="right",
                size="65%",  # type: ignore
                padding=0,
                withCloseButton=False,
                opened=False,
                zIndex=1200,
                styles={"drawer": {"backgroundColor": "transparent", "border": "none"}},
                children=[html.Div(id=f"{drawer_id}-content", children=[])],
            ),
        ]
    )


def _create_drawer_content(drawer_id: str, theme: str, drawer_data: dict):
    is_dark = theme == "dark"

    # Colores base del Design System
    bg_main = DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT
    bg_secondary = DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY
    border_color = DS.SLATE[7] if is_dark else DS.SLATE[3]
    text_color = DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT
    
    # Gradiente Azul Marca para Insights
    brand_gradient = f"linear-gradient(135deg, {DS.NEXA_BLUE} 0%, {DS.BRAND[8]} 100%)"
    icon_color = DS.NEXA_BLUE

    # --- CORRECCIÓN AQUÍ: Claves alineadas con DrawerDataService (tab_...) ---
    tab_defs = [
        ("tab_resumen", "Resumen", "tabler:chart-pie"),
        ("tab_desglose", "Desglose", "tabler:list"),
        ("tab_datos", "Datos", "tabler:table"),
        ("tab_insights", "Insights", "tabler:bulb"),
        ("tab_acciones", "Acciones", "tabler:bolt"),
    ]

    # Seleccionar tab por defecto
    available_tabs = [key for key, _, _ in tab_defs if drawer_data.get(key)]
    default_tab = available_tabs[0] if available_tabs else "tab_resumen"

    return html.Div(
        style={"display": "flex", "flexDirection": "column", "height": "100%", "backgroundColor": bg_main},
        children=[
            # --- HEADER ---
            dmc.Paper(
                p="lg",
                radius=0,
                shadow="sm",
                style={
                    "borderBottom": f"1px solid {border_color}",
                    "backgroundColor": bg_secondary,
                },
                children=dmc.Group(
                    justify="space-between",
                    children=[
                        dmc.Group(
                            gap="md",
                            children=[
                                dmc.ThemeIcon(
                                    children=DashIconify(icon=drawer_data.get("icon", "tabler:info-circle"), width=28),
                                    size="xl",
                                    variant="light",
                                    color="blue", 
                                    style={"color": DS.NEXA_BLUE, "backgroundColor": "rgba(65, 140, 223, 0.15)"},
                                    radius="md",
                                ),
                                html.Div(
                                    [
                                        dmc.Text(
                                            drawer_data.get("title", "Detalle"),
                                            size="xl",
                                            fw=700,  # type: ignore
                                            c=text_color,  # type: ignore
                                        ),
                                        dmc.Text(
                                            drawer_data.get("subtitle", ""),
                                            size="sm",
                                            c="dimmed",  # type: ignore
                                            mt=4,
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        dmc.Tooltip(
                            label="Cerrar",
                            children=dmc.ActionIcon(
                                id=f"{drawer_id}-close",
                                children=DashIconify(icon="tabler:x", width=20),
                                variant="subtle",
                                color="red", 
                                size="xl",
                            ),
                        ),
                    ],
                ),
            ),
            # --- TABS ---
            dmc.Tabs(
                value=default_tab,
                variant="pills",
                color="blue",
                radius="md",
                style={
                    "flex": 1,
                    "display": "flex",
                    "flexDirection": "column",
                    "overflow": "hidden",
                },
                children=[
                    dmc.TabsList(
                        px="md",
                        pt="sm",
                        pb="md",
                        style={
                            "borderBottom": f"1px solid {border_color}",
                            "backgroundColor": bg_secondary,
                        },
                        children=[
                            dmc.TabsTab(
                                dmc.Group(
                                    gap="xs",
                                    children=[
                                        DashIconify(icon=icon, width=16, color="white" if key == "tab_insights" else icon_color),
                                        dmc.Text(label, size="sm", fw=600),  # type: ignore
                                    ],
                                ),
                                value=key,
                                style={
                                    "background": brand_gradient if key == "tab_insights" else None,
                                    "color": "white" if key == "tab_insights" else None,
                                    "borderRadius": "8px" if key == "tab_insights" else None,
                                    "marginLeft": "auto" if key == "tab_insights" else None
                                } if key == "tab_insights" else {}
                            ) for key, label, icon in tab_defs if drawer_data.get(key)
                        ],
                    ),
                    # Paneles de contenido
                    *[
                        dmc.TabsPanel(
                            drawer_data[key],
                            value=key,
                            style={
                                "flex": 1,
                                "overflow": "auto",
                                "padding": "1.5rem",
                                "backgroundColor": bg_main,
                            },
                        ) for key, label, icon in tab_defs if drawer_data.get(key)
                    ]
                ],
            ),
        ],
    )


def register_drawer_callback(drawer_id: str, widget_registry: dict, screen_id: str, filter_ids: list = None):  # type: ignore
    from services.data_manager import data_manager

    f_ids = filter_ids or []

    @callback(
        Output(drawer_id, "opened"),
        Output(f"{drawer_id}-content", "children"),
        [
            Input({"type": "open-smart-drawer", "index": dash.ALL}, "n_clicks"),
            Input(f"{drawer_id}-close", "n_clicks"),
        ],
        [
            State(drawer_id, "opened"),
            [State(fid, "value") for fid in f_ids],
        ],
        prevent_initial_call=True,
    )
    def manage_drawer(open_clicks, close_click, is_open, filter_values):
        if not dash_ctx.triggered:
            return no_update, no_update

        trigger = dash_ctx.triggered_id

        if trigger == f"{drawer_id}-close":
            return False, no_update

        if isinstance(trigger, dict) and trigger.get("type") == "open-smart-drawer":
            if not any(click for click in open_clicks if click):
                return no_update, no_update

            active_filters = {}
            if filter_ids and filter_values:
                for fid, val in zip(filter_ids, filter_values):
                    key = fid.split("-")[-1] if "-" in fid else fid
                    if val not in [None, "", "Todas", "Todos", "0", 0]:
                        active_filters[key] = val

            widget_id = trigger.get("index")
            widget = widget_registry.get(widget_id)
            if not widget:
                return no_update, no_update

            ctx = data_manager.get_screen(screen_id, filters=active_filters, use_cache=True)

            if isinstance(ctx, str):
                import json
                try:
                    ctx = json.loads(ctx)
                except:
                    ctx = {}

            theme = session.get("theme", "dark")

            drawer_data = DrawerDataService.get_widget_drawer_data(
                widget_id=widget_id, widget=widget, ctx=ctx, theme=theme  # type: ignore
            )

            content = _create_drawer_content(drawer_id, theme, drawer_data)
            return True, content

        return no_update, no_update

    return manage_drawer