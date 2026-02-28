import dash_mantine_components as dmc
from dash import html, dcc
from dash_iconify import DashIconify
from design_system import DesignSystem as DS, dmc as _dmc


def get_ai_toggle_button():
    return dmc.Affix(
        id="ai-copilot-affix",
        position={"bottom": 30, "right": 30},
        zIndex=_dmc(1000),
        children=dmc.ActionIcon(
            id="ai-copilot-toggle",
            radius="xl",
            size=60,
            variant="filled",
            style={
                "boxShadow": DS.LAYOUT["shadows"]["lg"],
                "transition": "all 0.3s ease",
                "backgroundColor": DS.NEXA_GOLD,
                "background": f"linear-gradient(135deg, {DS.NEXA_GOLD} 0%, {DS.NEXA_ORANGE} 100%)",
            },
            children=DashIconify(icon="tabler:message-chatbot", width=32, color="white"),
        ),
    )


def create_message_bubble(message: dict, is_dark: bool):
    is_user = message["role"] == "user"

    return html.Div(
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "flex-end" if is_user else "flex-start",
            "marginBottom": "12px",
        },
        children=[
            html.Div(
                style={
                    "maxWidth": "75%",
                    "padding": "12px 16px",
                    "borderRadius": "16px",
                    "backgroundColor": DS.NEXA_GOLD if is_user else (
                        DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY
                    ),
                    "color": "white" if is_user else (DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT),
                    "boxShadow": DS.LAYOUT["shadows"]["sm"],
                },
                children=[
                    dmc.Text(
                        message["content"],
                        size="sm",
                        style={"whiteSpace": "pre-wrap", "wordBreak": "break-word"},
                    ) if is_user else dcc.Markdown(
                        message["content"],
                        style={
                            "fontSize": "14px",
                            "lineHeight": "1.6",
                            "wordBreak": "break-word",
                            "margin": 0,
                        },
                        className="zamy-markdown",
                    )
                ],
            ),
            dmc.Text(
                message.get("timestamp", ""),
                size="xs",
                c=_dmc("dimmed"),
                mt=4,
                style={"fontSize": "10px"},
            ),
        ],
    )


def create_typing_indicator(is_dark: bool):
    """Burbuja animada que indica que Zamy está procesando la respuesta."""
    return html.Div(
        id="zamy-typing-indicator",
        style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "flex-start",
            "marginBottom": "12px",
        },
        children=[
            html.Div(
                style={
                    "padding": "12px 18px",
                    "borderRadius": "16px",
                    "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                    "boxShadow": DS.LAYOUT["shadows"]["sm"],
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "6px",
                },
                children=[
                    html.Span(style={
                        "width": "7px", "height": "7px", "borderRadius": "50%",
                        "backgroundColor": DS.NEXA_GOLD,
                        "animation": "zamyDot 1.2s infinite",
                        "animationDelay": "0s",
                    }),
                    html.Span(style={
                        "width": "7px", "height": "7px", "borderRadius": "50%",
                        "backgroundColor": DS.NEXA_GOLD,
                        "animation": "zamyDot 1.2s infinite",
                        "animationDelay": "0.3s",
                    }),
                    html.Span(style={
                        "width": "7px", "height": "7px", "borderRadius": "50%",
                        "backgroundColor": DS.NEXA_GOLD,
                        "animation": "zamyDot 1.2s infinite",
                        "animationDelay": "0.6s",
                    }),
                    dmc.Text("Zamy está pensando…", size="xs", c=_dmc("dimmed"), ml=4),
                ],
            ),
        ],
    )


def create_quick_action_button(action: dict, is_dark: bool):
    return dmc.Button(
        action["label"],
        id={"type": "quick-action", "action": action["action"]},
        variant="light",
        color="yellow",
        size="sm",
        leftSection=DashIconify(icon=action["icon"], width=16),
        fullWidth=True,
        styles={
            "root": {
                "backgroundColor": DS.NEXA_GOLD + "20",
                "color": DS.NEXA_GOLD,
                "border": f"1px solid {DS.NEXA_GOLD}40",
            }
        },
    )


def create_chat_header(mode: str, is_dark: bool):
    return html.Div(
        style={
            "padding": "16px",
            "borderBottom": f"1px solid {'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'}",
            "backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT,
        },
        children=[
            dmc.Group(
                justify="space-between",
                children=[
                    dmc.Group(
                        gap="xs",
                        children=[
                            dmc.ThemeIcon(
                                children=DashIconify(icon="tabler:message-chatbot", width=24),
                                size="lg",
                                variant="light",
                                color="yellow",
                                style={
                                    "background": f"linear-gradient(135deg, {DS.NEXA_GOLD} 0%, {DS.NEXA_ORANGE} 100%)",
                                },
                            ),
                            html.Div([
                                dmc.Text(
                                    "Zamy AI",
                                    size="lg",
                                    fw=_dmc(700),
                                    c=_dmc(DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT),
                                ),
                                dmc.Group(
                                    gap=4,
                                    children=[
                                        html.Div(
                                            style={
                                                "width": "8px",
                                                "height": "8px",
                                                "borderRadius": "50%",
                                                "backgroundColor": DS.POSITIVE,
                                            }
                                        ),
                                        dmc.Text("En línea", size="xs", c=_dmc("dimmed")),
                                    ],
                                ),
                            ]),
                        ],
                    ),
                    dmc.Group(
                        gap=4,
                        children=[
                            dmc.Tooltip(
                                label="Historial de chats",
                                children=dmc.ActionIcon(
                                    id="chat-history-btn",
                                    children=DashIconify(icon="tabler:history", width=18),
                                    variant="subtle",
                                    color="gray",
                                    size="md",
                                ),
                            ),
                            dmc.Tooltip(
                                label="Drawer lateral",
                                children=dmc.ActionIcon(
                                    id="chat-mode-drawer",
                                    children=DashIconify(icon="tabler:layout-sidebar-right", width=18),
                                    variant="light" if mode == "drawer" else "subtle",
                                    color="yellow" if mode == "drawer" else "gray",
                                    size="md",
                                ),
                            ),
                            dmc.Tooltip(
                                label="Sidebar fijo",
                                children=dmc.ActionIcon(
                                    id="chat-mode-sidebar",
                                    children=DashIconify(icon="tabler:layout-navbar", width=18),
                                    variant="light" if mode == "sidebar" else "subtle",
                                    color="yellow" if mode == "sidebar" else "gray",
                                    size="md",
                                ),
                            ),
                            dmc.Tooltip(
                                label="Flotante",
                                children=dmc.ActionIcon(
                                    id="chat-mode-float",
                                    children=DashIconify(icon="tabler:float-center", width=18),
                                    variant="light" if mode == "float" else "subtle",
                                    color="yellow" if mode == "float" else "gray",
                                    size="md",
                                ),
                            ),
                            dmc.Tooltip(
                                label="Nueva conversación",
                                children=dmc.ActionIcon(
                                    id={"type": "chat-control", "action": "new"},
                                    children=DashIconify(icon="tabler:plus", width=18),
                                    variant="subtle",
                                    color="green",
                                    size="md",
                                ),
                            ),
                            dmc.Tooltip(
                                label="Cerrar",
                                children=dmc.ActionIcon(
                                    id={"type": "chat-control", "action": "close"},
                                    children=DashIconify(icon="tabler:x", width=18),
                                    variant="subtle",
                                    color="gray",
                                    size="md",
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def create_chat_content(messages: list, quick_actions: list, is_dark: bool, is_loading: bool = False, kpi_catalog: list | None = None):
    # Build the list of message bubbles
    bubbles = [create_message_bubble(msg, is_dark) for msg in (messages or [])]

    # Typing indicator when waiting for AI
    if is_loading:
        bubbles.append(create_typing_indicator(is_dark))

    has_messages = bool(messages)

    return html.Div(
        style={
            "flex": 1,
            "display": "flex",
            "flexDirection": "column",
            "overflow": "hidden",
        },
        children=[
            # Messages area
            html.Div(
                id="chat-messages-container",
                style={
                    "flex": 1,
                    "overflowY": "auto",
                    "padding": "20px",
                    "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                },
                children=[
                    # Empty state
                    html.Div(
                        style={
                            "display": "flex" if not has_messages else "none",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "height": "100%",
                            "textAlign": "center",
                            "padding": "40px 20px",
                        },
                        children=[
                            dmc.ThemeIcon(
                                children=DashIconify(icon="tabler:sparkles", width=48),
                                size=80,
                                radius="xl",
                                variant="light",
                                color="yellow",
                                style={
                                    "background": f"linear-gradient(135deg, {DS.NEXA_GOLD}20 0%, {DS.NEXA_ORANGE}20 100%)",
                                    "marginBottom": "20px",
                                },
                            ),
                            dmc.Text(
                                "¡Hola! Soy Zamy",
                                size="xl",
                                fw=_dmc(700),
                                c=_dmc(DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT),
                                mb="xs",
                            ),
                            dmc.Text(
                                "Tu asistente inteligente de negocio",
                                size="sm",
                                c=_dmc("dimmed"),
                                mb="xl",
                            ),
                        ],
                    ),
                    # Message bubbles
                    html.Div(children=bubbles),
                ],
            ),
            # Quick actions (only when chat is empty)
            html.Div(
                style={
                    "padding": "16px 20px",
                    "borderTop": f"1px solid {'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'}",
                    "backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT,
                    "display": "block" if (not has_messages and quick_actions) else "none",
                },
                children=[
                    dmc.Text(
                        "Acciones rápidas:",
                        size="xs",
                        c=_dmc("dimmed"),
                        mb="sm",
                        fw=_dmc(600),
                    ),
                    dmc.Stack(
                        gap="xs",
                        children=[
                            create_quick_action_button(action, is_dark)
                            for action in (quick_actions or [])
                        ],
                    ),
                ],
            ),
            # Input area
            html.Div(
                style={
                    "padding": "16px 20px",
                    "borderTop": f"1px solid {'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'}",
                    "backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT,
                },
                children=[
                    dmc.Group(
                        gap="xs",
                        children=[
                            # @ mention popover
                            dmc.Popover(
                                id="kpi-mention-popover",
                                position="top-start",
                                withArrow=True,
                                shadow="md",
                                zIndex=2000,
                                children=[
                                    dmc.PopoverTarget(
                                        dmc.Tooltip(
                                            label="Mencionar KPI (@)",
                                            children=dmc.ActionIcon(
                                                id="chat-at-btn",
                                                children=DashIconify(icon="tabler:at", width=18),
                                                variant="light",
                                                color="yellow",
                                                size="lg",
                                                radius="xl",
                                            ),
                                        )
                                    ),
                                    dmc.PopoverDropdown(
                                        style={
                                            "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                                            "border": f"1px solid {'rgba(255,255,255,0.1)' if is_dark else '#e5e7eb'}",
                                            "padding": "8px",
                                            "minWidth": "220px",
                                        },
                                        children=[
                                            dmc.Text(
                                                "Mencionar widget (@{…})",
                                                size="xs",
                                                fw=600,  # type: ignore
                                                c="dimmed",  # type: ignore
                                                mb="xs",
                                                tt="uppercase",  # type: ignore
                                            ),
                                            dmc.ScrollArea(
                                                h=220,
                                                children=dmc.Stack(
                                                    gap=4,
                                                    children=(
                                                        [
                                                            dmc.Group(
                                                                gap="xs",
                                                                wrap="nowrap",
                                                                children=[
                                                                    dmc.Button(
                                                                        item["name"],
                                                                        id={"type": "kpi-mention-item", "index": f"{item['id']}::{item['name']}"},
                                                                        variant="subtle",
                                                                        color="yellow",
                                                                        size="xs",
                                                                        style={"flex": 1, "minWidth": 0, "textAlign": "left"},
                                                                        justify="left",
                                                                        leftSection=DashIconify(
                                                                            icon=(
                                                                                "tabler:chart-bar" if item.get("type") == "chart"
                                                                                else "tabler:table" if item.get("type") == "table"
                                                                                else "tabler:hash"
                                                                            ),
                                                                            width=14,
                                                                        ),
                                                                    ),
                                                                    dmc.Badge(
                                                                        (
                                                                            "Gráfica" if item.get("type") == "chart"
                                                                            else "Tabla" if item.get("type") == "table"
                                                                            else "KPI"
                                                                        ),
                                                                        size="xs",
                                                                        variant="light",
                                                                        color=(
                                                                            "blue" if item.get("type") == "chart"
                                                                            else "green" if item.get("type") == "table"
                                                                            else "yellow"
                                                                        ),
                                                                        style={"flexShrink": 0},
                                                                    ),
                                                                ],
                                                            )
                                                            for item in (kpi_catalog or [])
                                                        ] if kpi_catalog else [
                                                            dmc.Text(
                                                                "No hay widgets disponibles",
                                                                size="sm",
                                                                c="dimmed",  # type: ignore
                                                                ta="center",  # type: ignore
                                                            )
                                                        ]
                                                    ),
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.TextInput(
                                id="chat-input",
                                placeholder="Escribe tu pregunta… usa @ para mencionar KPIs",
                                radius="xl",
                                size="md",
                                disabled=is_loading,
                                style={"flex": 1},
                                styles={
                                    "input": {
                                        "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                                        "color": DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT,
                                        "border": f"1px solid {'rgba(255,255,255,0.1)' if is_dark else '#e5e7eb'}",
                                    }
                                },
                            ),
                            dmc.ActionIcon(
                                id="chat-send",
                                children=DashIconify(
                                    icon="tabler:loader-2" if is_loading else "tabler:send",
                                    width=20,
                                ),
                                variant="filled",
                                color="yellow",
                                size="lg",
                                radius="xl",
                                disabled=is_loading,
                                loading=is_loading,
                                style={
                                    "background": f"linear-gradient(135deg, {DS.NEXA_GOLD} 0%, {DS.NEXA_ORANGE} 100%)",
                                    "opacity": "0.6" if is_loading else "1",
                                },
                            ),
                            dmc.ActionIcon(
                                id="chat-voice",
                                children=DashIconify(icon="tabler:microphone", width=20),
                                variant="light",
                                color="yellow",
                                size="lg",
                                radius="xl",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def create_history_panel(history_list: list, is_dark: bool):
    """Panel inline de historial de conversaciones (reemplaza el modal)."""
    items = []
    for conv in (history_list or []):
        conv_id = conv.get("id")
        title = (conv.get("title") or "Sin título")[:60]
        updated = conv.get("updated_at") or conv.get("created_at") or ""
        if isinstance(updated, str) and len(updated) > 16:
            updated = updated[:16].replace("T", " ")
        items.append(
            dmc.Paper(
                p="sm",
                radius="md",
                mb="xs",
                style={
                    "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                    "border": f"1px solid {'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'}",
                    "transition": "border-color 0.15s",
                },
                children=dmc.Group(
                    justify="space-between",
                    wrap="nowrap",
                    gap="xs",
                    children=[
                        # Clickable area to load the conversation
                        dmc.UnstyledButton(
                            id={"type": "history-item", "index": conv_id},
                            style={"flex": 1, "textAlign": "left", "minWidth": 0},
                            children=[
                                dmc.Group(gap="xs", mb=2, wrap="nowrap", children=[
                                    DashIconify(icon="tabler:message", width=14, color=DS.NEXA_GOLD),
                                    dmc.Text(
                                        title,
                                        size="sm",
                                        fw=_dmc(600),
                                        style={"color": DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT, "flex": 1, "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"},
                                    ),
                                ]),
                                dmc.Text(updated, size="xs", c=_dmc("dimmed")),
                            ],
                        ),
                        # Delete button
                        dmc.Tooltip(
                            label="Eliminar conversación",
                            children=dmc.ActionIcon(
                                id={"type": "history-delete", "index": conv_id},
                                children=DashIconify(icon="tabler:trash", width=14),
                                variant="subtle",
                                color="red",
                                size="sm",
                            ),
                        ),
                    ],
                ),
            )
        )

    return html.Div(
        style={"display": "flex", "flexDirection": "column", "height": "100%", "overflow": "hidden"},
        children=[
            # Sub-header del panel de historial
            html.Div(
                style={
                    "padding": "12px 16px",
                    "borderBottom": f"1px solid {'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'}",
                    "backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT,
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                },
                children=[
                    dmc.ActionIcon(
                        id={"type": "chat-nav", "action": "back"},
                        children=DashIconify(icon="tabler:arrow-left", width=18),
                        variant="subtle",
                        color="gray",
                        size="md",
                    ),
                    dmc.Text(
                        "Conversaciones anteriores",
                        size="sm",
                        fw=_dmc(600),
                        c=_dmc(DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT),
                    ),
                ],
            ),
            # Lista scrollable
            html.Div(
                style={
                    "flex": 1,
                    "overflowY": "auto",
                    "padding": "12px 16px",
                    "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                },
                children=items if items else [
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "paddingTop": "60px",
                            "gap": "12px",
                        },
                        children=[
                            DashIconify(icon="tabler:history-off", width=40, color=DS.NEXA_GOLD + "60"),
                            dmc.Text("No hay conversaciones guardadas.", size="sm", c=_dmc("dimmed")),
                        ],
                    )
                ],
            ),
        ],
    )


def render_ai_copilot(
    is_open=False,
    theme="light",
    mode="drawer",
    messages=None,
    quick_actions=None,
    view="chat",
    history_list=None,
    is_loading=False,
    kpi_catalog=None,
):
    is_dark = theme == "dark"
    messages = messages or []
    quick_actions = quick_actions or []
    history_list = history_list or []
    kpi_catalog = kpi_catalog or []

    # Inner body: history panel OR normal chat
    if view == "history":
        body = html.Div(
            style={"display": "flex", "flexDirection": "column", "height": "100%"},
            children=[
                create_chat_header(mode, is_dark),
                create_history_panel(history_list, is_dark),
            ],
        )
    else:
        body = html.Div(
            style={"display": "flex", "flexDirection": "column", "height": "100%"},
            children=[
                create_chat_header(mode, is_dark),
                create_chat_content(messages, quick_actions, is_dark, is_loading=is_loading, kpi_catalog=kpi_catalog),
            ],
        )

    if mode == "drawer":
        return dmc.Drawer(
            id="ai-copilot-container",
            opened=is_open,
            position="right",
            size=_dmc("450px"),
            padding=0,
            zIndex=1100,
            withCloseButton=False,
            styles={
                "content": {"backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT},
                "body": {"padding": 0, "height": "100%", "display": "flex", "flexDirection": "column"},
            },
            children=body,
        )

    if mode == "sidebar":
        return html.Div(
            id="ai-copilot-container",
            style={
                "position": "fixed",
                "right": 0,
                "top": 0,
                "bottom": 0,
                "width": "450px",
                "zIndex": 900,
                "backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT,
                "boxShadow": DS.LAYOUT["shadows"]["xl"],
                "transform": "translateX(0)" if is_open else "translateX(100%)",
                "transition": "transform 0.3s ease",
            },
            children=body,
        )

    if mode == "float":
        if not is_open:
            return html.Div(style={"display": "none"})

        return html.Div(
            id="ai-copilot-float-window",
            style={
                "position": "fixed",
                "bottom": "90px",
                "right": "30px",
                "width": "420px",
                "height": "650px",
                "zIndex": 5000,
                "borderRadius": "18px",
                "overflow": "hidden",
                "boxShadow": DS.LAYOUT["shadows"]["xl"],
                "backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT,
                "border": f"1px solid {'rgba(255,255,255,0.12)' if is_dark else '#e5e7eb'}",
                "display": "flex",
                "flexDirection": "column",
            },
            children=[
                html.Div(
                    id="float-drag-handle",
                    style={
                        "height": "38px",
                        "cursor": "move",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "borderBottom": f"1px solid {'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'}",
                        "background": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                        "userSelect": "none",
                    },
                    children=[
                        html.Div(
                            style={
                                "width": "44px",
                                "height": "5px",
                                "borderRadius": "10px",
                                "backgroundColor": DS.NEXA_GOLD,
                            }
                        )
                    ],
                ),
                html.Div(
                    style={"flex": 1, "display": "flex", "flexDirection": "column", "overflow": "hidden"},
                    children=body,
                ),
            ],
        )

    # Fallback: drawer
    return dmc.Drawer(
        id="ai-copilot-container",
        opened=is_open,
        position="right",
        size=_dmc("450px"),
        padding=0,
        zIndex=1100,
        withCloseButton=False,
        styles={
            "content": {"backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT},
            "body": {"padding": 0, "height": "100%", "display": "flex", "flexDirection": "column"},
        },
        children=body,
    )


def create_chat_stores():
    return html.Div([
        dcc.Store(id="chat-messages-store", storage_type="session", data=[]),
        # localStorage so the mode survives navigation / page reload
        dcc.Store(id="chat-mode-store", storage_type="local", data="drawer"),
        dcc.Store(id="chat-open-store", storage_type="session", data=False),
        dcc.Store(id="chat-sidebar-active", data=False),
        dcc.Store(id="current-conversation-id", storage_type="session", data=None),
        dcc.Store(id="chat-history-list-store", data=[]),
        # "chat" | "history" — drives which panel is shown inside the copilot
        dcc.Store(id="chat-view-store", data="chat"),
        dcc.Store(id="current-page-token-store", data=None),
        # Two-stage send: pending message text + loading flag
        dcc.Store(id="chat-pending-store", data=None),
        dcc.Store(id="chat-loading", data=False),
        # @mention catalog: list of {id, name, type} for current screen's widgets
        dcc.Store(id="kpi-mention-catalog", data=[]),
        # Signal to close any active drawer (incremented by analyze_kpi_in_chat)
        dcc.Store(id="close-all-drawers", data=0),
        dcc.Store(
            id="dashboard-context-store",
            data={
                "screen_id": None,
                "widget_id": None,
                "filters": None,
                "date_range": None,
                "timezone": "America/Mexico_City",
            },
        ),
    ])
