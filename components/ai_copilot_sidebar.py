import dash_mantine_components as dmc
from dash import html, dcc
from dash_iconify import DashIconify
import dash_draggable
from design_system import DesignSystem as DS
import time


def get_ai_toggle_button():
    return dmc.Affix(
        position={"bottom": 30, "right": 30},
        zIndex=1000, # type: ignore
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
                    )
                ],
            ),
            dmc.Text(
                message.get("timestamp", ""),
                size="xs",
                c="dimmed", # type: ignore
                mt=4,
                style={"fontSize": "10px"},
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
                                    fw=700, # type: ignore
                                    c=DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT, # type: ignore
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
                                        dmc.Text("En línea", size="xs", c="dimmed"), # type: ignore
                                    ],
                                ),
                            ]),
                        ],
                    ),
                    dmc.Group(
                        gap=4,
                        children=[
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
                                label="Limpiar conversación",
                                children=dmc.ActionIcon(
                                    id={"type": "chat-control", "action": "clear"},
                                    children=DashIconify(icon="tabler:trash", width=18),
                                    variant="subtle",
                                    color="red",
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
                            )

                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def create_chat_content(messages: list, quick_actions: list, is_dark: bool):
    return html.Div(
        style={
            "flex": 1,
            "display": "flex",
            "flexDirection": "column",
            "overflow": "hidden",
        },
        children=[
            html.Div(
                id="chat-messages-container",
                style={
                    "flex": 1,
                    "overflowY": "auto",
                    "padding": "20px",
                    "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                },
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "height": "100%",
                            "textAlign": "center",
                            "padding": "40px 20px",
                        } if not messages else {"display": "none"},
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
                                fw=700, # type: ignore
                                c=DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT, # type: ignore
                                mb="xs",
                            ),
                            dmc.Text(
                                "Tu asistente de analítica inteligente",
                                size="sm",
                                c="dimmed", # type: ignore
                                mb="xl",
                            ),
                        ],
                    ) if not messages else None,
                    html.Div(
                        children=[
                            create_message_bubble(msg, is_dark)
                            for msg in messages
                        ],
                    ),
                ] if not messages else [
                    html.Div(
                        children=[
                            create_message_bubble(msg, is_dark)
                            for msg in messages
                        ],
                    ),
                ],
            ),
            html.Div(
                style={
                    "padding": "16px 20px",
                    "borderTop": f"1px solid {'rgba(255,255,255,0.08)' if is_dark else '#e5e7eb'}",
                    "backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT,
                    "display": "none" if messages else "block",
                },
                children=[
                    dmc.Text(
                        "Acciones rápidas:",
                        size="xs",
                        c="dimmed", # type: ignore
                        mb="sm",
                        fw=600, # type: ignore
                    ),
                    dmc.Stack(
                        gap="xs",
                        children=[
                            create_quick_action_button(action, is_dark)
                            for action in quick_actions
                        ],
                    ),
                ] if quick_actions else [],
            ),
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
                            dmc.TextInput(
                                id="chat-input",
                                placeholder="Escribe tu pregunta...",
                                radius="xl",
                                size="md",
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
                                children=DashIconify(icon="tabler:send", width=20),
                                variant="filled",
                                color="yellow",
                                size="lg",
                                radius="xl",
                                style={
                                    "background": f"linear-gradient(135deg, {DS.NEXA_GOLD} 0%, {DS.NEXA_ORANGE} 100%)",
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

def render_ai_copilot(is_open=False, theme="light", mode="drawer", messages=None, quick_actions=None):
    is_dark = theme == "dark"
    messages = messages or []
    quick_actions = quick_actions or []

    chat_content = html.Div(
        style={"display": "flex", "flexDirection": "column", "height": "100%"},
        children=[
            create_chat_header(mode, is_dark),
            create_chat_content(messages, quick_actions, is_dark),
        ],
    )

    if mode == "drawer":
        return dmc.Drawer(
            id="ai-copilot-container",
            opened=is_open,
            position="right",
            size="450px", # type: ignore
            padding=0,
            zIndex=1100,
            withCloseButton=False,
            styles={
                "content": {"backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT},
                "body": {"padding": 0, "height": "100%", "display": "flex", "flexDirection": "column"},
            },
            children=chat_content,
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
            children=chat_content,
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
                    style={"flex": 1, "display": "flex", "flexDirection": "column"},
                    children=chat_content,
                ),
            ],
        )


    return dmc.Drawer(
        id="ai-copilot-container",
        opened=is_open,
        position="right",
        size="450px", # type: ignore
        padding=0,
        zIndex=1100,
        withCloseButton=False,
        styles={
            "content": {"backgroundColor": DS.NEXA_BG_DARK if is_dark else DS.NEXA_BG_LIGHT},
            "body": {"padding": 0, "height": "100%", "display": "flex", "flexDirection": "column"},
        },
        children=chat_content,
    )

def create_chat_stores():
    return html.Div([
        dcc.Store(id="chat-messages-store", data=[]),
        dcc.Store(id="chat-mode-store", data="drawer"),
        dcc.Store(id="chat-open-store", data=False),
        dcc.Store(id="chat-sidebar-active", data=False),
    ])
