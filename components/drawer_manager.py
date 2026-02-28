import dash
from dash import html, callback, Input, Output, ALL, State, no_update, dcc, ctx as dash_ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from design_system import DesignSystem as DS, Typography, dmc as _dmc
from services.drawer_data_service import DrawerDataService
from flask import session

# Global catalog: screen_id -> [{id, name, type}]
# Populated by register_drawer_callback when a page registers its widget_registry.
_SCREEN_WIDGET_CATALOG: dict[str, list] = {}


def get_screen_widget_catalog(screen_id: str) -> list:
    """Return the friendly-name widget catalog for a screen, built from widget instances."""
    return _SCREEN_WIDGET_CATALOG.get(screen_id) or []


def create_smart_drawer(drawer_id: str = "smart-drawer"):
    return html.Div(
        [
            dcc.Download(id=f"{drawer_id}-download"),
            dcc.Download(id="drawer-kpi-excel-download"),
            dcc.Store(id=f"{drawer_id}-export-data"),
            dcc.Store(id=f"{drawer_id}-theme", data="dark"),
            dcc.Store(id="drawer-kpi-copy-feedback", data=None),
            html.Div(
                id=f"{drawer_id}-placeholder",
                style={"display": "none"},
                children=[dmc.ActionIcon(id=f"{drawer_id}-close", n_clicks=0)],
            ),
            dmc.Drawer(
                id=drawer_id,
                position="right",
                size=_dmc("65%"),
                padding=0,
                withCloseButton=False,
                opened=False,
                zIndex=1200,
                styles={
                    "drawer": {
                        "backgroundColor": "transparent", 
                        "border": "none",
                        "boxShadow": "none",
                    },
                    "body": {
                        "padding": 0,
                        "height": "100%",
                        "display": "flex",
                        "flexDirection": "column",
                        "overflow": "hidden",
                    },
                    "content": {
                        "height": "100%",
                        "display": "flex",
                        "flexDirection": "column",
                        "overflow": "hidden",
                    },
                    "header": {
                        "display": "none",
                    },
                },
                children=[
                    html.Div(
                        id=f"{drawer_id}-content",
                        children=[],
                        style={
                            "height": "100%",
                            "display": "flex",
                            "flexDirection": "column",
                        }
                    )
                ],
            ),
        ]
    )


def _create_drawer_content(drawer_id: str, theme: str, drawer_data: dict):
    is_dark = theme == "dark"

    # Colores base del Design System - solo colores base, sin paletas
    bg_main = DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT
    text_color = DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT
    
    # Tonos dorados en lugar de azules
    brand_gradient = f"linear-gradient(135deg, {DS.NEXA_GOLD} 0%, {DS.NEXA_ORANGE} 100%)"
    icon_color = DS.NEXA_GOLD

    # --- CORRECCIÓN AQUÍ: Claves alineadas con DrawerDataService (tab_...) ---
    tab_defs = [
        ("tab_resumen", "Resumen", "tabler:chart-pie"),
        ("tab_desglose", "Estadísticas", "tabler:chart-histogram"),
        ("tab_datos", "Datos", "tabler:table"),
        ("tab_insights", "Análisis IA", "tabler:brain"),
        ("tab_acciones", "Acciones", "tabler:bolt"),
    ]

    # Seleccionar tab por defecto
    available_tabs = [key for key, _, _ in tab_defs if drawer_data.get(key)]
    default_tab = available_tabs[0] if available_tabs else "tab_resumen"
    single_tab = len(available_tabs) == 1  # Only one tab → render content directly, no tab bar

    # ── Shared header ──────────────────────────────────────────────────────────
    header = dmc.Paper(
        p="lg",
        radius=0,
        style={"backgroundColor": bg_main, "border": "none"},
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
                            color="yellow",
                            style={"color": DS.NEXA_GOLD, "backgroundColor": "rgba(233, 161, 59, 0.15)"},
                            radius="md",
                        ),
                        html.Div([
                            dmc.Text(drawer_data.get("title", "Detalle"), size="xl", fw=_dmc(700), c=_dmc(text_color)),
                            dmc.Text(drawer_data.get("subtitle", ""), size="sm", c=_dmc("dimmed"), mt=4),
                        ]),
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
    )

    # ── Single-tab mode: no tab bar, just scroll the content directly ──────────
    if single_tab:
        content_key = available_tabs[0]
        return html.Div(
            style={
                "display": "flex",
                "flexDirection": "column",
                "height": "100%",
                "width": "100%",
                "backgroundColor": bg_main,
                "overflow": "hidden",
            },
            children=[
                header,
                html.Div(
                    drawer_data[content_key],
                    style={
                        "flex": 1,
                        "overflowY": "auto",
                        "padding": "1.5rem",
                        "backgroundColor": bg_main,
                    },
                ),
            ],
        )

    # ── Multi-tab mode ──────────────────────────────────────────────────────────
    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "height": "100vh",
            "width": "100%",
            "backgroundColor": bg_main,
            "overflow": "hidden",
        },
        children=[
            # --- HEADER ---
            header,
            # --- SCROLLABLE BODY: tabs list sticky, panel content natural height ---
            html.Div(
                style={
                    "flex": 1,
                    "minHeight": 0,
                    "overflowY": "auto",
                    "backgroundColor": bg_main,
                },
                children=[
                    dmc.Tabs(
                        value=default_tab,
                        variant="pills",
                        color="yellow",
                        radius="md",
                        children=[
                            dmc.TabsList(
                                px="md",
                                pt="sm",
                                pb="md",
                                style={
                                    "backgroundColor": bg_main,
                                    "border": "none",
                                    "position": "sticky",
                                    "top": 0,
                                    "zIndex": 10,
                                },
                                children=[
                                    dmc.TabsTab(
                                        dmc.Group(
                                            gap="xs",
                                            children=[
                                                DashIconify(icon=icon, width=16, color="white" if key == "tab_insights" else icon_color),
                                                dmc.Text(label, size="sm", fw=_dmc(600)),
                                            ],
                                        ),
                                        value=key,
                                        style={
                                            "background": brand_gradient if key == "tab_insights" else None,
                                            "color": "white" if key == "tab_insights" else None,
                                            "borderRadius": "8px" if key == "tab_insights" else None,
                                            "marginLeft": "auto" if key == "tab_insights" else None,
                                        } if key == "tab_insights" else {}
                                    ) for key, label, icon in tab_defs if drawer_data.get(key)
                                ],
                            ),
                            # Panels render at natural content height — no forced fill
                            *[
                                dmc.TabsPanel(
                                    drawer_data[key],
                                    value=key,
                                    style={
                                        "padding": "1.5rem",
                                        "backgroundColor": bg_main,
                                    },
                                ) for key, label, icon in tab_defs if drawer_data.get(key)
                            ]
                        ],
                    ),
                ],
            ),
        ],
    )


@callback(
    Output("drawer-llm-output", "children"),
    Input("drawer-generate-insight-btn", "n_clicks"),
    State("drawer-llm-stats", "data"),
    prevent_initial_call=True,
)
def generate_drawer_llm_insight(n_clicks, stats_data):
    """Generates LLM insight on demand when the user clicks the button."""
    if not n_clicks or not stats_data:
        return no_update
    from services.drawer_data_service import _llm_insight
    title = stats_data.get("title", "Indicador")
    stats = stats_data.get("stats", "")
    is_dark = stats_data.get("theme", "dark") == "dark"
    llm_text = _llm_insight(title, stats)
    if not llm_text:
        return dmc.Alert(
            "El modelo no respondió. Verifica que Ollama esté en ejecución.",
            color="yellow",
            icon=DashIconify(icon="tabler:brain", width=18),
        )
    return dmc.Paper(
        p="lg",
        radius="md",
        withBorder=True,
        style={
            "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
            "borderLeft": f"4px solid {DS.NEXA_GOLD}",
        },
        children=[
            dmc.Group(gap="xs", mb="xs", children=[
                DashIconify(icon="tabler:brain", width=16, color=DS.NEXA_GOLD),
                dmc.Text("Análisis de Zamy", size="xs", fw=700, c="dimmed", tt="uppercase"),  # type: ignore
            ]),
            dmc.Text(
                llm_text,
                size="sm",
                style={"whiteSpace": "pre-wrap", "lineHeight": 1.7},
            ),
        ],
    )


@callback(
    Output("drawer-stats-llm-output", "children"),
    Input("drawer-stats-insight-btn", "n_clicks"),
    State("drawer-stats-llm-stats", "data"),
    prevent_initial_call=True,
)
def generate_drawer_stats_insight(n_clicks, stats_data):
    if not n_clicks or not stats_data:
        return no_update
    from services.drawer_data_service import _llm_insight
    title = stats_data.get("title", "Análisis estadístico")
    stats = stats_data.get("stats", "")
    is_dark = stats_data.get("theme", "dark") == "dark"
    llm_text = _llm_insight(title, stats)
    if not llm_text:
        return dmc.Alert(
            "El modelo no respondió. Verifica que Ollama esté en ejecución.",
            color="yellow",
            icon=DashIconify(icon="tabler:brain", width=18),
        )
    return dmc.Paper(
        p="lg",
        radius="md",
        withBorder=True,
        style={
            "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
            "borderLeft": f"4px solid {DS.NEXA_GOLD}",
        },
        children=[
            dmc.Group(gap="xs", mb="xs", children=[
                DashIconify(icon="tabler:brain", width=16, color=DS.NEXA_GOLD),
                dmc.Text("Análisis de Zamy", size="xs", fw=700, c="dimmed", tt="uppercase"),  # type: ignore
            ]),
            dmc.Text(
                llm_text,
                size="sm",
                style={"whiteSpace": "pre-wrap", "lineHeight": 1.7},
            ),
        ],
    )


def register_drawer_callback(drawer_id: str, widget_registry: dict, screen_id: str, filter_ids: list | None = None):
    from services.data_manager import data_manager

    f_ids = filter_ids or []

    # Build friendly-name catalog from the actual widget instances
    catalog = []
    for wid, widget in (widget_registry or {}).items():
        strategy = getattr(widget, "strategy", None)
        title = getattr(strategy, "title", None) or wid.replace("_", " ").title()
        viz_type = "chart" if widget.__class__.__name__ == "ChartWidget" else "kpi"
        catalog.append({"id": wid, "name": title, "type": viz_type})
    _SCREEN_WIDGET_CATALOG[screen_id] = catalog
    #print(f"[DrawerManager] Catalog for '{screen_id}': {[c['name'] for c in catalog]}")

    @callback(
        Output(drawer_id, "opened", allow_duplicate=True),
        Output(f"{drawer_id}-content", "children"),
        [
            Input({"type": "open-smart-drawer", "index": dash.ALL}, "n_clicks"),
            Input(f"{drawer_id}-close", "n_clicks"),
            Input("close-all-drawers", "data"),
        ],
        [
            State(drawer_id, "opened"),
            [State(fid, "value") for fid in f_ids],
        ],
        prevent_initial_call=True,
    )
    def manage_drawer(open_clicks, close_click, close_signal, is_open, filter_values):
        if not dash_ctx.triggered:
            return no_update, no_update

        trigger = dash_ctx.triggered_id

        if trigger == f"{drawer_id}-close" or trigger == "close-all-drawers":
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

            drawer_data = DrawerDataService.get_widget_drawer_data(widget_id=str(widget_id), widget=widget, ctx=ctx, theme=theme)

            content = _create_drawer_content(drawer_id, theme, drawer_data)
            return True, content

        return no_update, no_update

    return manage_drawer