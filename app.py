import dash
from dash import Input, Output, State, dcc, html, callback_context
from flask import Flask, redirect, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from config import Config
from components.layout.sidebar import render_sidebar
from pages.auth import get_error_layout, get_login_layout
from services.auth_service import auth_service
from settings.theme import DesignSystem

server = Flask(__name__)
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)
server.config.from_object(Config)
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
    session["auth_error"] = result
    return redirect("/")

@server.route("/login/<provider>")
def login_social_route(provider):
    return auth_service.login_social(provider)

@server.route("/getAToken")
def azure_callback_compatibility():
    result = auth_service.handle_social_callback("azure")
    if result is True:
        return redirect("/")
    session["auth_error"] = result
    return redirect("/")

@server.route("/auth/<provider>/callback")
def auth_callback(provider):
    result = auth_service.handle_social_callback(provider)
    if result is True:
        return redirect("/")
    session["auth_error"] = result
    return redirect("/")

@server.route("/logout")
def logout():
    session.clear()
    return redirect("/")

def get_app_shell():
    return dmc.MantineProvider(
        id="mantine-provider",
        forceColorScheme="dark",
        theme=DesignSystem.get_mantine_theme(),
        children=[
            dcc.Store(id="theme-store", storage_type="local", data="dark"),
            dcc.Store(id="sidebar-store", storage_type="local", data=False),
            dmc.AppShell(
                id="app-shell",
                header={"height": 60},
                navbar={"width": 260, "breakpoint": "sm", "collapsed": {"mobile": True}},
                padding="md",
                children=[
                    dmc.AppShellHeader(
                        px="md",
                        children=dmc.Group(
                            [
                                DashIconify(
                                    icon="tabler:hexagon-letter-a",
                                    width=35,
                                    color=DesignSystem.BRAND[5],
                                ),
                                dmc.Text(
                                    "Analítica ",
                                    size="xl",
                                    fw="bold",
                                    style={"letterSpacing": "-0.5px"},
                                ),
                            ],
                            h="100%",
                        ),
                    ),
                    dmc.AppShellNavbar(id="navbar", children=[], style={"zIndex": 100}),
                    dmc.AppShellMain(children=dash.page_container),
                ],
            ),
        ],
    )

app.layout = lambda: (
    get_login_layout()
    if Config.ENABLE_LOGIN and not session.get("user")
    else get_app_shell()
)

@app.callback(
    Output("theme-store", "data"),
    Output("sidebar-store", "data"),
    Input("theme-toggle", "n_clicks"),
    Input("btn-sidebar-toggle", "n_clicks"),
    State("theme-store", "data"),
    State("sidebar-store", "data"),
    prevent_initial_call=True,
)
def update_stores(btn_theme, btn_sidebar, current_theme, is_collapsed):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    current_theme = current_theme or "dark"
    is_collapsed = is_collapsed if is_collapsed is not None else False
    if trigger_id == "theme-toggle":
        current_theme = "light" if current_theme == "dark" else "dark"
    elif trigger_id == "btn-sidebar-toggle":
        is_collapsed = not is_collapsed
    return current_theme, is_collapsed

@app.callback(
    Output("mantine-provider", "forceColorScheme"),
    Output("app-shell", "navbar"),
    Output("navbar", "children"),
    Input("theme-store", "data"),
    Input("sidebar-store", "data"),
)
def render_interface(theme, collapsed):
    theme = theme or "dark"
    collapsed = collapsed if collapsed is not None else False
    navbar_config = {
        "width": 80 if collapsed else 260,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    }
    sidebar_ui = render_sidebar(collapsed=collapsed, current_theme=theme)
    return theme, navbar_config, sidebar_ui

if __name__ == "__main__":
    app.run(port=8000)
