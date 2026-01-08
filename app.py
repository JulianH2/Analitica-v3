import logging
import dash
from dash import Input, Output, State
from flask import Flask, redirect, request, session, url_for
from flask_session import Session
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from config import Config
from components.layout.sidebar import render_sidebar
from pages.auth import get_error_layout, get_login_layout
from services.auth_service import auth_service
from settings.theme import DesignSystem

server = Flask(__name__)
server.config.from_object(Config)
Session(server)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_service.init_app(server)

app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Enterprise Analytics",
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
    ]
)

@server.route("/login/local", methods=["POST"])
def login_local_route():
    email = request.form.get("email")
    password = request.form.get("password")
    result = auth_service.login_local(email, password)
    
    if result is True:
        return redirect("/")
    else:
        session["auth_error"] = result
        return redirect("/")

@server.route("/login/<provider>")
def login_social_route(provider):
    return auth_service.login_social(provider)

@server.route("/getAToken")
def azure_callback_compatibility():
    try:
        result = auth_service.handle_social_callback('azure')
        
        if result is True:
            return redirect("/")
        
        session["auth_error"] = result
    except Exception as e:
        session["auth_error"] = f"Error crítico: {str(e)}"
    
    return redirect("/")

@server.route("/auth/<provider>/callback")
def auth_callback(provider):
    try:
        result = auth_service.handle_social_callback(provider)
        if result is True:
            return redirect("/")
        session["auth_error"] = result
    except Exception as e:
        session["auth_error"] = f"Error callback {provider}: {str(e)}"
    
    return redirect("/")

@server.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@server.before_request
def check_authentication():
    if request.path.startswith("/assets") or request.path.startswith("/_dash-component"):
        return None
    if not Config.ENABLE_LOGIN:
        return None
    pass

def get_app_shell():
    return dmc.MantineProvider(
        forceColorScheme="dark",
        theme=DesignSystem.get_mantine_theme(),
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
                dmc.AppShellNavbar(id="navbar", children=render_sidebar(collapsed=False)),
                dmc.AppShellMain(children=dash.page_container)
            ]
        )
    )

def serve_layout():
    if session.get("auth_error"):
        error_msg = session.pop("auth_error")
        return get_error_layout(error_msg)
    
    if Config.ENABLE_LOGIN and not session.get("user"):
        return get_login_layout()
    
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