import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import DesignSystem as DS, ComponentSizes, Typography, Space, BorderRadius


def get_ai_toggle_button():
    return dmc.Affix(
        position={"bottom": 30, "right": 30},
        zIndex=1000, # type: ignore
        children=dmc.ActionIcon(
            id="ai-copilot-toggle",
            radius="xl",
            size=60,
            variant="filled",
            color="blue",
            style={
                "boxShadow": DS.LAYOUT["shadows"]["lg"],
                "transition": "transform 0.2s ease",
                "backgroundColor": DS.CHART_BLUE,
            },
            children=DashIconify(icon="tabler:message-chatbot", width=32),
        ),
    )


def render_ai_copilot_sidebar(is_open=False, theme="light"):
    is_dark = theme == "dark"

    content = dmc.Stack(
        gap="xl",
        h="100%",
        children=[
            dmc.Paper(
                radius="30px", # type: ignore
                style={
                    "backgroundColor": DS.NEXA_BG_LIGHT_SECONDARY
                    if not is_dark
                    else DS.NEXA_BG_DARK_SECONDARY,
                    "height": "300px",
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "position": "relative",
                },
                children=[
                    dmc.RingProgress(
                        size=120,
                        thickness=12,
                        roundCaps=False,
                        sections=[
                            {"value": 25, "color": DS.CHART_BLUE},
                            {"value": 25, "color": DS.NEGATIVE},
                            {"value": 25, "color": DS.POSITIVE},
                            {"value": 25, "color": DS.NEUTRAL},
                        ], # type: ignore
                        label=dmc.Center(
                            DashIconify(
                                icon="tabler:plus",
                                width=50,
                                color=DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK,
                                style={"strokeWidth": "4px"},
                            )
                        ),
                    ),
                    dmc.Group(
                        gap=5,
                        mt="xl",
                        style={"position": "absolute", "bottom": "30px"},
                        children=[
                            DashIconify(
                                icon="tabler:microphone",
                                width=16,
                                color=DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK,
                            ),
                            dmc.Text(
                                "Habla con Zamy",
                                size="xs",
                                fw=700, # type: ignore
                                c=DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK, # type: ignore
                            ),
                        ],
                    ),
                ],
            ),
            dmc.Stack(
                gap=0,
                children=[
                    dmc.Title(
                        "Chatea",
                        order=1,
                        style={
                            "fontSize": f"{Typography.XXXL}px",
                            "color": DS.NEXA_GRAY,
                            "fontWeight": Typography.WEIGHT_BOLD,
                            "lineHeight": Typography.LH_TIGHT,
                        },
                    ),
                    dmc.Title(
                        "con Zamy,",
                        order=1,
                        style={
                            "fontSize": f"{Typography.XXXL}px",
                            "color": DS.NEXA_GRAY,
                            "fontWeight": Typography.WEIGHT_BOLD,
                            "lineHeight": Typography.LH_TIGHT,
                        },
                    ),
                    dmc.Text(
                        "nuestra inteligencia artificial.",
                        size="xl",
                        c=DS.TEXT_LIGHT_SECONDARY
                        if not is_dark
                        else DS.TEXT_DARK_SECONDARY, # pyright: ignore[reportArgumentType]
                        mt="sm",
                    ),
                    dmc.Text(
                        "Te ayudará a encontrar lo que necesites.",
                        size="md",
                        c=DS.TEXT_LIGHT_SECONDARY
                        if not is_dark
                        else DS.TEXT_DARK_SECONDARY, # type: ignore
                        mt="xs",
                    ),
                ],
            ),
            html.Div(style={"flex": 1}),
            dmc.TextInput(
                placeholder="Pregunta lo que quieras",
                radius="xl",
                size="lg",
                styles={
                    "input": {
                        "border": f"3px solid {DS.NEUTRAL_BG}",
                        "backgroundColor": DS.NEXA_BG_LIGHT
                        if not is_dark
                        else DS.NEXA_BG_DARK_SECONDARY,
                        "color": DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK,
                        "textAlign": "center",
                        "fontSize": f"{Typography.MD}px",
                        "height": f"{ComponentSizes.INPUT_HEIGHT}px",
                    }
                },
            ),
        ],
    )

    return dmc.Drawer(
        id="ai-copilot-drawer",
        opened=is_open,
        position="right",
        size=f"{ComponentSizes.CHAT_SIDEBAR_WIDTH}px", # type: ignore
        padding="md",
        zIndex=1100,
        withCloseButton=True,
        styles={
            "content": {
                "backgroundColor": DS.NEXA_BG_LIGHT if not is_dark else DS.NEXA_BG_DARK
            }
        },
        children=content,
    )
