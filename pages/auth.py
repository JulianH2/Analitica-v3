import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html
from settings.theme import DesignSystem

def get_login_layout():
    return dmc.MantineProvider(
        forceColorScheme="light",
        theme=DesignSystem.get_mantine_theme(), # type: ignore
        children=dmc.Box(
            style={"backgroundColor": "#f8fafc", "minHeight": "100vh"},
            children=[
                dmc.Center(
                    style={"height": "100vh"},
                    children=[
                        dmc.Paper(
                            shadow="xl", radius="lg", withBorder=True, p="xl", w=420,
                            children=dmc.Stack(
                                children=[
                                    dmc.Stack(gap=0, align="center", children=[
                                        dmc.ThemeIcon(
                                            size=60, radius=100, variant="light", color="indigo",
                                            children=DashIconify(icon="tabler:hexagon-letter-a", width=35)
                                        ),
                                        dmc.Text("Bienvenido", size="lg", fw="bold", mt="sm"),
                                        dmc.Text("Selecciona tu método de acceso", size="sm", c="gray"), 
                                    ]),

                                    dmc.Divider(label="Acceso Corporativo", labelPosition="center"),
                                    dmc.Anchor(
                                        dmc.Button(
                                            "Continuar con Microsoft",
                                            leftSection=DashIconify(icon="logos:microsoft-icon"),
                                            variant="outline", 
                                            color="dark", 
                                            size="lg", 
                                            fullWidth=True,
                                        ),
                                        href="/login/azure",
                                        refresh=True,
                                        underline="never"
                                    ),

                                    dmc.Divider(label="O con tu correo y contraseña", labelPosition="center"),
                                    html.Form(action="/login/local", method="post", children=[
                                        dmc.Stack(gap="md", children=[
                                            dmc.TextInput(
                                                label="Correo Electrónico", 
                                                name="email", 
                                                placeholder="tu@empresa.com", 
                                                required=True,
                                                leftSection=DashIconify(icon="tabler:mail")
                                            ),
                                            dmc.PasswordInput(
                                                label="Contraseña", 
                                                name="password", 
                                                placeholder="••••••••", 
                                                required=True,
                                                leftSection=DashIconify(icon="tabler:lock")
                                            ),
                                            html.Button(
                                                "Iniciar Sesión", 
                                                type="submit",
                                                style={
                                                    "backgroundColor": DesignSystem.BRAND[5],
                                                    "color": "white",
                                                    "border": "none",
                                                    "padding": "10px",
                                                    "borderRadius": "4px",
                                                    "cursor": "pointer",
                                                    "width": "100%",
                                                    "fontWeight": "600",
                                                    "fontSize": "14px",
                                                    "marginTop": "10px"
                                                },
                                                className="mantine-Button-root"
                                            )
                                        ])
                                    ]),
                                    
                                    dmc.Group(gap="xs", justify="center", mt="lg", children=[
                                        DashIconify(icon="tabler:shield-check", color=DesignSystem.SUCCESS[5], width=14),
                                        dmc.Text("Sistema seguro y monitoreado", size="xs", c="gray")
                                    ])
                                ]
                            )
                        )
                    ]
                )
            ]
        )
    )

def get_error_layout(error_message="Ocurrió un error inesperado."):
    return dmc.MantineProvider(
        forceColorScheme="light",
        theme=DesignSystem.get_mantine_theme(), # type: ignore
        children=dmc.Container(
            style={"height": "100vh", "display": "flex", "alignItems": "center", "justifyContent": "center"},
            children=dmc.Paper(
                shadow="xl", p="xl", radius="md", withBorder=True, w=500,
                children=dmc.Stack(
                    align="center",
                    children=[
                        DashIconify(icon="tabler:alert-triangle", width=60, color=DesignSystem.DANGER[5]),
                        dmc.Text("Error de Autenticación", size="lg", fw="bold", c="red"),
                        dmc.Text(error_message, ta="center", c="gray"),
                        dmc.Anchor(
                            dmc.Button("Intentar de nuevo", variant="light", color="gray"),
                            href="/logout", refresh=True
                        )
                    ]
                )
            )
        )
    )