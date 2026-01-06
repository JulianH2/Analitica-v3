import dash
from dash import html, dcc, Input, Output, State, no_update, _dash_renderer
from flask import Flask, request, redirect, url_for, session
from flask_session import Session
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from config import Config
from components.layout.sidebar import render_sidebar
from services.auth_service import auth_service

_dash_renderer._set_react_version("18.2.0")

server = Flask(__name__)
server.config.from_object(Config)
Session(server)

app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Enterprise Analytics",
    external_stylesheets=[
        "https://unpkg.com/@mantine/core@7.10.0/styles.css",
        "https://unpkg.com/@mantine/dates@7.10.0/styles.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
    ]
)

# --- RUTAS DE AUTENTICACIÓN ---
@server.route("/login")
def login():
    return auth_service.login()

@server.route("/getAToken")
def get_token():
    return auth_service.get_token(app) 

@server.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@server.before_request
def check_authentication():
    if not Config.ENABLE_LOGIN:
        return None
    pass

def get_app_shell():
    return dmc.MantineProvider(
        theme={
            "primaryColor": "indigo",
            "fontFamily": "'Inter', sans-serif",
            "components": {
                "Paper": {"defaultProps": {"radius": "md", "withBorder": True, "shadow": "sm"}},
                "Button": {"defaultProps": {"radius": "md"}}
            }
        },
        children=dmc.AppShell(
            id="app-shell",
            header={"height": 60},
            navbar={
                "width": 260,
                "breakpoint": "sm",
                "collapsed": {"mobile": True}
            },
            padding="md",
            style={"backgroundColor": "var(--mantine-color-gray-0)"}, 
            children=[
                dmc.AppShellHeader(
                    px="md",
                    children=dmc.Group(
                        justify="space-between", 
                        h="100%",
                        children=[
                            dmc.Group([
                                dmc.Burger(id="btn-mobile-menu", hiddenFrom="sm", size="sm"),
                                DashIconify(icon="tabler:hexagon-letter-a", width=35, color="#4c6ef5"),
                                dmc.Text("Analitica ", size="xl", fw="bold", style={"letterSpacing": "-0.5px"})
                            ]),
                            dmc.Group([
                                dmc.ActionIcon(DashIconify(icon="tabler:bell"), variant="subtle", color="gray"),
                                dmc.ActionIcon(DashIconify(icon="tabler:settings"), variant="subtle", color="gray"),
                            ])
                        ]
                    )
                ),
                
                dmc.AppShellNavbar(
                    id="navbar",
                    children=render_sidebar(collapsed=False)
                ),
                
                dmc.AppShellMain(children=dash.page_container)
            ]
        )
    )

def serve_layout():
    # Si el login está habilitado y no hay usuario en sesión, redirigir
    if Config.ENABLE_LOGIN and not session.get("user"):
        return dmc.MantineProvider(
            children=dmc.Container(
                style={"height": "100vh", "display": "flex", "alignItems": "center", "justifyContent": "center"},
                children=dmc.Stack(
                    align="center",
                    children=[
                        DashIconify(icon="tabler:lock", width=50, color="indigo"),
                        dmc.Text("Tu sesión ha expirado o no has iniciado sesión.", size="lg", fw="normal"),
                        dmc.Anchor(
                            dmc.Button(
                                "Iniciar sesión con Microsoft",
                                leftSection=DashIconify(icon="logos:microsoft-icon"),
                                variant="outline",
                                size="lg",
                                fullWidth=True
                            ),
                            href="/login",
                            refresh=True,
                            underline="never"
                        ),
                    ]
                )
            )
        )
    
    # Si hay sesión o el login está desactivado, mostrar la App normal
    return get_app_shell()

app.layout = serve_layout

@app.callback(
    Output("app-shell", "navbar"),    
    Output("navbar", "children"),     
    Input("btn-sidebar-toggle", "n_clicks"),
    State("app-shell", "navbar"),     
    prevent_initial_call=True
)
def toggle_sidebar(n, navbar_config):
    current_width = navbar_config.get("width", 260)
    
    is_currently_collapsed = current_width == 80
    
    new_width = 260 if is_currently_collapsed else 80
    new_collapsed_state = not is_currently_collapsed 
    
    navbar_config["width"] = new_width
    
    return navbar_config, render_sidebar(collapsed=new_collapsed_state)

@app.callback(
    Output("app-shell", "navbar", allow_duplicate=True), 
    Input("btn-mobile-menu", "opened"),
    State("app-shell", "navbar"),
    prevent_initial_call=True
)
def toggle_mobile(opened, navbar_prop):
    navbar_prop["collapsed"] = {"mobile": not opened}
    return navbar_prop

if __name__ == "__main__":
    app.run(debug=True, port=8000)