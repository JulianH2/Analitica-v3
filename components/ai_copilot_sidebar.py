"""
AI Copilot Sidebar - Actualizado con Design System
Sidebar de chat "Zamy" con colores y estilos según mockups
"""

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import DesignSystem as DS, ComponentSizes, Typography, Space, BorderRadius


def get_ai_toggle_button():
    """
    Botón flotante para abrir/cerrar el AI Copilot
    Usa colores y tamaños del design system
    """
    return dmc.Affix(
        position={"bottom": 30, "right": 30},
        zIndex=1000,  # DS.ZIndex.AI_TOGGLE
        children=dmc.ActionIcon(
            id="ai-copilot-toggle",
            radius="xl",
            size=60,
            variant="filled",
            color="blue",
            style={
                "boxShadow": DS.LAYOUT['shadows']['lg'],
                "transition": "transform 0.2s ease",
                "backgroundColor": DS.CHART_BLUE  # Azul consistente
            },
            children=DashIconify(icon="tabler:message-chatbot", width=32)
        )
    )


def render_ai_copilot_sidebar(is_open=False, theme="light"):
    """
    Renderiza el sidebar de AI Copilot (Zamy)
    Adaptado a los colores del mockup
    
    Args:
        is_open: Si el drawer está abierto
        theme: "light" o "dark"
    """
    is_dark = theme == "dark"
    
    # Contenido visual (Logo Zamy, textos, input)
    content = dmc.Stack(
        gap="xl",
        h="100%",
        children=[
            # Sección Superior (Logo/RingProgress con +)
            dmc.Paper(
                radius="30px",
                style={
                    "backgroundColor": DS.NEXA_BG_LIGHT_SECONDARY if not is_dark else DS.NEXA_BG_DARK_SECONDARY,
                    "height": "300px",
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "position": "relative",
                },
                children=[
                    # RingProgress con los 4 colores del mockup
                    dmc.RingProgress(
                        size=120,
                        thickness=12,
                        roundCaps=False,
                        sections=[
                            {"value": 25, "color": DS.CHART_BLUE},      # Azul
                            {"value": 25, "color": DS.NEGATIVE},        # Rojo
                            {"value": 25, "color": DS.POSITIVE},        # Verde
                            {"value": 25, "color": DS.NEUTRAL},         # Naranja/Dorado
                        ],
                        label=dmc.Center(
                            DashIconify(
                                icon="tabler:plus", 
                                width=50, 
                                color=DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK,
                                style={"strokeWidth": "4px"}
                            )
                        )
                    ),
                    
                    # "Habla con Zamy" badge en la parte inferior
                    dmc.Group(
                        gap=5,
                        mt="xl",
                        style={"position": "absolute", "bottom": "30px"},
                        children=[
                            DashIconify(
                                icon="tabler:microphone", 
                                width=16, 
                                color=DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK
                            ),
                            dmc.Text(
                                "Habla con Zamy", 
                                size="xs", 
                                fw=700, 
                                c=DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK
                            )
                        ]
                    )
                ]
            ),
            
            # Textos principales (como en el mockup)
            dmc.Stack(
                gap=0,
                children=[
                    dmc.Title(
                        "Chatea", 
                        order=1, 
                        style={
                            "fontSize": f"{Typography.XXXL}px",  # 48px
                            "color": DS.NEXA_GRAY,
                            "fontWeight": Typography.WEIGHT_BOLD,
                            "lineHeight": Typography.LH_TIGHT
                        }
                    ),
                    dmc.Title(
                        "con Zamy,", 
                        order=1, 
                        style={
                            "fontSize": f"{Typography.XXXL}px",
                            "color": DS.NEXA_GRAY,
                            "fontWeight": Typography.WEIGHT_BOLD,
                            "lineHeight": Typography.LH_TIGHT
                        }
                    ),
                    dmc.Text(
                        "nuestra inteligencia artificial.", 
                        size="xl", 
                        c=DS.TEXT_LIGHT_SECONDARY if not is_dark else DS.TEXT_DARK_SECONDARY,
                        mt="sm"
                    ),
                    dmc.Text(
                        "Te ayudará a encontrar lo que necesites.",
                        size="md",
                        c=DS.TEXT_LIGHT_SECONDARY if not is_dark else DS.TEXT_DARK_SECONDARY,
                        mt="xs"
                    )
                ]
            ),

            html.Div(style={"flex": 1}),  # Espaciador flexible

            # Input de búsqueda (estilo mockup)
            dmc.TextInput(
                placeholder="Pregunta lo que quieras",
                radius="xl",
                size="lg",
                styles={
                    "input": {
                        "border": f"3px solid {DS.NEUTRAL_BG}",  # Borde dorado claro
                        "backgroundColor": DS.NEXA_BG_LIGHT if not is_dark else DS.NEXA_BG_DARK_CARD,
                        "color": DS.TEXT_LIGHT if not is_dark else DS.TEXT_DARK,
                        "textAlign": "center",
                        "fontSize": f"{Typography.MD}px",
                        "height": f"{ComponentSizes.INPUT_HEIGHT}px"
                    }
                }
            )
        ]
    )

    # Drawer con ancho según mockup (380px)
    return dmc.Drawer(
        id="ai-copilot-drawer",
        opened=is_open,
        position="right",
        size=f"{ComponentSizes.CHAT_SIDEBAR_WIDTH}px",  # 380px
        padding="md",
        zIndex=1100,  # DS.ZIndex.AI_SIDEBAR
        withCloseButton=True,
        styles={
            "content": {
                "backgroundColor": DS.NEXA_BG_LIGHT if not is_dark else DS.NEXA_BG_DARK
            }
        },
        children=content
    )