import dash_mantine_components as dmc
from dash import html, dcc
from dash_iconify import DashIconify
from design_system import DesignSystem


def render_ai_copilot_sidebar(is_open=False, current_theme="dark"):
    header = dmc.Paper(
        p="md",
        radius=0,
        style={
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "borderBottom": "2px solid rgba(255,255,255,0.1)"
        },
        children=dmc.Group(
            justify="space-between",
            children=[
                dmc.Group(
                    gap="sm",
                    children=[
                        dmc.ThemeIcon(
                            id="ai-copilot-header-icon",
                            children=DashIconify(icon="tabler:brain", width=28),
                            size="xl",
                            radius="md",
                            variant="white",
                            color="violet"
                        ),
                        html.Div(
                            children=[
                                dmc.Text(
                                    children="AI Analyst",
                                    size="xl",
                                    fw=700,
                                    c="white"
                                ),
                                dmc.Text(
                                    children="Tu asistente inteligente",
                                    size="xs",
                                    c="white",
                                    opacity=0.9
                                )
                            ]
                        )
                    ]
                ),
                dmc.ActionIcon(
                    id="ai-copilot-close",
                    children=DashIconify(icon="tabler:x", width=20),
                    variant="subtle",
                    color="white",
                    size="lg"
                )
            ]
        )
    )
    auto_summary = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        mb="md",
        children=[
            dmc.Group(
                mb="sm",
                children=[
                    DashIconify(icon="tabler:sparkles", width=20, color=DesignSystem.BRAND[5]),
                    dmc.Text("Resumen Inteligente", fw=600, size="sm")
                ]
            ),
            dmc.Stack(
                gap="xs",
                children=[
                    dmc.Alert(
                        children=[
                            dmc.Text("📈 Tus ingresos crecieron 18.5% vs mes anterior", size="sm", fw=500),
                            dmc.Text("El mejor desempeño en 6 meses", size="xs", c="dimmed", mt=4)
                        ],
                        color="green",
                        variant="light",
                        radius="md"
                    ),
                    dmc.Alert(
                        children=[
                            dmc.Text("⚠️ Costos de mantenimiento +12% sobre meta", size="sm", fw=500),
                            dmc.Text("Revisar contratos de proveedores externos", size="xs", c="dimmed", mt=4)
                        ],
                        color="yellow",
                        variant="light",
                        radius="md"
                    ),
                    dmc.Alert(
                        children=[
                            dmc.Text("💡 Oportunidad: optimizar rutas puede ahorrar 8%", size="sm", fw=500),
                            dmc.Text("Basado en análisis de kilometraje", size="xs", c="dimmed", mt=4)
                        ],
                        color="blue",
                        variant="light",
                        radius="md"
                    )
                ]
            )
        ]
    )
    quick_suggestions = [
        {
            "icon": "tabler:chart-line",
            "label": "Analizar tendencias",
            "desc": "¿Cuáles son los patrones en los últimos 3 meses?",
            "color": "blue"
        },
        {
            "icon": "tabler:alert-circle",
            "label": "Revisar alertas",
            "desc": "¿Qué KPIs están fuera de rango?",
            "color": "red"
        },
        {
            "icon": "tabler:coin",
            "label": "Optimizar costos",
            "desc": "¿Dónde puedo reducir gastos?",
            "color": "green"
        },
        {
            "icon": "tabler:chart-arrows",
            "label": "Proyecciones",
            "desc": "¿Cómo voy vs mi meta anual?",
            "color": "violet"
        },
        {
            "icon": "tabler:users",
            "label": "Análisis de clientes",
            "desc": "¿Qué clientes generan más valor?",
            "color": "orange"
        },
        {
            "icon": "tabler:route",
            "label": "Eficiencia operativa",
            "desc": "¿Cómo mejorar rendimiento de rutas?",
            "color": "cyan"
        }
    ]
    
    suggestion_cards = dmc.Stack(
        gap="xs",
        children=[
            dmc.Paper(
                p="sm",
                radius="md",
                withBorder=True,
                style={"cursor": "pointer", "transition": "all 0.2s"},
                className="suggestion-card-hover",
                children=dmc.Group(
                    gap="sm",
                    wrap="nowrap",
                    children=[
                        dmc.ThemeIcon(
                            DashIconify(icon=s["icon"], width=18),
                            size="md",
                            variant="light",
                            color=s["color"],
                            radius="md"
                        ),
                        html.Div(
                            style={"flex": 1, "minWidth": 0},
                            children=[
                                dmc.Text(s["label"], size="sm", fw=600, style={"lineHeight": 1.2}),
                                dmc.Text(
                                    s["desc"],
                                    size="xs",
                                    c="dimmed",
                                    style={
                                        "lineHeight": 1.3,
                                        "overflow": "hidden",
                                        "textOverflow": "ellipsis",
                                        "whiteSpace": "nowrap"
                                    }
                                )
                            ]
                        ),
                        DashIconify(icon="tabler:chevron-right", width=16, color="gray", style={"flexShrink": 0})
                    ]
                )
            )
            for s in quick_suggestions
        ]
    )
    chat_messages = [
        {
            "role": "assistant",
            "content": "👋 ¡Hola! Soy tu asistente de IA. Puedo ayudarte a:",
            "bullets": [
                "Analizar tendencias y patrones en tus datos",
                "Identificar oportunidades de mejora",
                "Responder preguntas sobre tus métricas",
                "Generar reportes personalizados"
            ]
        }
    ]
    
    chat_area = dmc.Stack(
        gap="sm",
        style={
            "flex": 1,
            "overflowY": "auto",
            "minHeight": 0,
            "padding": "0.5rem"
        },
        children=[
            dmc.Paper(
                p="md",
                radius="md",
                style={"background": DesignSystem.SLATE[1]},
                children=[
                    dmc.Group(
                        mb="xs",
                        children=[
                            dmc.Avatar(
                                DashIconify(icon="tabler:robot", width=20),
                                size="sm",
                                radius="xl",
                                color="violet",
                                variant="light"
                            ),
                            dmc.Text("AI Analyst", size="sm", fw=600)
                        ]
                    ),
                    dmc.Text(chat_messages[0]["content"], size="sm", mb="xs"),
                    dmc.List(
                        size="sm",
                        spacing="xs",
                        icon=dmc.ThemeIcon(
                            DashIconify(icon="tabler:point-filled", width=8),
                            size="xs",
                            color="violet",
                            variant="transparent"
                        ),
                        children=[
                            dmc.ListItem(dmc.Text(item, size="sm", c="dimmed"))
                            for item in chat_messages[0]["bullets"]
                        ]
                    )
                ]
            ),
            dmc.Paper(
                p="md",
                radius="md",
                ml="xl",
                style={"background": DesignSystem.BRAND[5], "color": "white"},
                children=dmc.Text("¿Cómo van mis ingresos este mes?", size="sm")
            ),
            dmc.Paper(
                p="md",
                radius="md",
                mr="xl",
                style={"background": DesignSystem.SLATE[1]},
                children=[
                    dmc.Group(
                        mb="xs",
                        children=[
                            dmc.Avatar(
                                DashIconify(icon="tabler:robot", width=20),
                                size="sm",
                                radius="xl",
                                color="violet",
                                variant="light"
                            ),
                            dmc.Badge("Analizando...", size="xs", variant="dot", color="violet")
                        ]
                    ),
                    dmc.Text(
                        "Tus ingresos de febrero van excelente:",
                        size="sm",
                        fw=500,
                        mb="xs"
                    ),
                    dmc.Stack(
                        gap="xs",
                        children=[
                            dmc.Group(
                                gap="xs",
                                children=[
                                    dmc.Text("•", c="green", fw=700),
                                    dmc.Text("$175,900 acumulado (+18.5% vs mes anterior)", size="sm")
                                ]
                            ),
                            dmc.Group(
                                gap="xs",
                                children=[
                                    dmc.Text("•", c="green", fw=700),
                                    dmc.Text("17.3% por encima de la meta ($150,000)", size="sm")
                                ]
                            ),
                            dmc.Group(
                                gap="xs",
                                children=[
                                    dmc.Text("•", c="blue", fw=700),
                                    dmc.Text("Proyección: $185,000 al cierre de mes", size="sm")
                                ]
                            )
                        ]
                    ),
                    dmc.Divider(my="xs"),
                    dmc.Text("¿Quieres que analice algo más específico?", size="xs", c="dimmed", style={"fontStyle": "italic"})
                ]
            ),
            html.Div(style={"flex": 1})
        ]
    )
    input_section = dmc.Stack(
        gap="xs",
        p="md",
        style={
            "borderTop": f"1px solid {DesignSystem.SLATE[2]}",
            "background": DesignSystem.SLATE[0]
        },
        children=[
            dmc.Group(
                gap="xs",
                mb="xs",
                children=[
                    dmc.Badge(
                        "¿Tendencias?",
                        size="sm",
                        variant="light",
                        style={"cursor": "pointer"}
                    ),
                    dmc.Badge(
                        "¿Top clientes?",
                        size="sm",
                        variant="light",
                        style={"cursor": "pointer"}
                    ),
                    dmc.Badge(
                        "¿Proyecciones?",
                        size="sm",
                        variant="light",
                        style={"cursor": "pointer"}
                    )
                ]
            ),
            dmc.Group(
                gap="xs",
                align="flex-end",
                children=[
                    dmc.Textarea(
                        id="ai-copilot-input",
                        placeholder="Pregunta sobre tus datos... (Ej: ¿Cómo optimizo costos?)",
                        autosize=True,
                        minRows=1,
                        maxRows=4,
                        radius="md",
                        style={"flex": 1}
                    ),
                    dmc.Stack(
                        gap="xs",
                        children=[
                            dmc.Tooltip(
                                label="Adjuntar archivo",
                                children=dmc.ActionIcon(
                                    DashIconify(icon="tabler:paperclip", width=18),
                                    variant="subtle",
                                    color="gray",
                                    size="md"
                                )
                            ),
                            dmc.Tooltip(
                                label="Enviar mensaje",
                                children=dmc.ActionIcon(
                                    DashIconify(icon="tabler:send", width=20),
                                    id="ai-copilot-send",
                                    variant="filled",
                                    size="xl",
                                    radius="md",
                                    style={
                                        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                                    }
                                )
                            )
                        ]
                    )
                ]
            ),
            dmc.Text(
                "💡 Tip: Sé específico en tus preguntas para obtener mejores respuestas",
                size="xs",
                c="dimmed",
                ta="center",
                mt="xs"
            )
        ]
    )
    sidebar_content = dmc.Stack(
        gap=0,
        style={"height": "100%", "display": "flex", "flexDirection": "column"},
        children=[
            header,
            html.Div(
                style={
                    "flex": 1,
                    "overflowY": "auto",
                    "padding": "1rem",
                    "minHeight": 0
                },
                children=dmc.Stack(
                    gap="md",
                    children=[
                        auto_summary,
                        dmc.Divider(
                            label="Preguntas Rápidas",
                            labelPosition="center",
                            size="sm"
                        ),
                        suggestion_cards,
                        dmc.Divider(
                            label="Conversación",
                            labelPosition="center",
                            size="sm"
                        ),
                        chat_area
                    ]
                )
            ),
            input_section
        ]
    )
    return html.Div(
        id="ai-copilot-sidebar-container",
        className="ai-copilot-sidebar" + (" ai-copilot-sidebar-open" if is_open else ""),
        children=[
            dmc.Paper(
                shadow="xl",
                radius=0,
                style={
                    "height": "100vh",
                    "display": "flex",
                    "flexDirection": "column",
                    "overflow": "hidden"
                },
                children=sidebar_content
            )
        ],
        style={
    "position": "fixed",
    "top": 0,
    "right": 0,
    "width": "450px",
    "height": "100vh",
    "zIndex": 1100,
    "transition": "transform 0.3s ease-in-out",
}

    )


def get_ai_toggle_button():
    return html.Div(
        style={
            "position": "fixed",
            "bottom": "24px",
            "right": "24px",
            "zIndex": 1000
        },
        children=[
            dmc.Badge(
                "3",
                size="sm",
                color="red",
                variant="filled",
                circle=True,
                style={
                    "position": "absolute",
                    "top": "-4px",
                    "right": "-4px",
                    "zIndex": 1,
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.2)"
                }
            ),
            dmc.Tooltip(
                label="Abrir AI Analyst",
                position="left",
                withArrow=True,
                children=dmc.ActionIcon(
                    DashIconify(icon="tabler:robot", width=28),
                    id="ai-copilot-toggle",
                    size="xl",
                    radius="xl",
                    style={
                        "width": "64px",
                        "height": "64px",
                        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        "boxShadow": "0 8px 24px rgba(102, 126, 234, 0.4), 0 4px 8px rgba(0,0,0,0.1)",
                        "transition": "all 0.3s ease",
                        "cursor": "pointer",
                        "animation": "pulse 2s ease-in-out infinite"
                    },
                    className="ai-toggle-btn"
                )
            )
        ]
    )


def get_ai_copilot_styles():
    return """
    <style>
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4), 0 4px 8px rgba(0,0,0,0.1);
            }
            50% {
                transform: scale(1.05);
                box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6), 0 6px 12px rgba(0,0,0,0.15);
            }
        }
        
        .ai-toggle-btn:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6), 0 6px 12px rgba(0,0,0,0.2) !important;
        }
        
        .suggestion-card-hover:hover {
            transform: translateX(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: var(--mantine-color-blue-5);
        }
        
        .ai-copilot-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 450px;
            height: 100vh;
            z-index: 1100;
        }
    </style>
    """