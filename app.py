import os
import django
import logging
from datetime import datetime
from flask import Flask, redirect, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Analitica.settings")
django.setup()

import dash
from dash import Input, Output, State, dcc, callback_context, ALL, ClientsideFunction
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from config import Config
from components.layout.sidebar import render_sidebar
from pages.auth import get_login_layout
from services.auth_service import auth_service
from settings.theme import DesignSystem

DesignSystem.setup_plotly_templates()

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
    auth_service.handle_social_callback("azure")
    return redirect("/")

@server.route("/auth/<provider>/callback")
def auth_callback(provider):
    auth_service.handle_social_callback(provider)
    return redirect("/")

@server.route("/logout")
def logout():
    session.clear()
    return redirect("/")

def get_app_shell():
    return dmc.MantineProvider(
        id="mantine-provider",
        theme=DesignSystem.get_mantine_theme(), # type: ignore
        children=[
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="theme-store", storage_type="local"),
            dcc.Store(id="sidebar-store", storage_type="local"),
            dcc.Store(id="selected-db-store", storage_type="local", data="db_1"),
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
                                DashIconify(icon="tabler:hexagon-letter-a", width=35, color=DesignSystem.BRAND[5]),
                                dmc.Text("Analitica", size="xl", fw="bold"),
                            ],
                            h="100%",
                        ),
                    ),
                    dmc.AppShellNavbar(id="navbar", children=[]),
                    dmc.AppShellMain(
                        children=dcc.Loading(
                            id="loading-overlay",
                            type="circle",
                            color=DesignSystem.BRAND[5],
                            children=dash.page_container
                        )
                    ),
                ],
            ),
        ],
    )

app.layout = lambda: (
    get_login_layout() if Config.ENABLE_LOGIN and not session.get("user") else get_app_shell()
)

@app.callback(
    Output("theme-store", "data"),
    Output("sidebar-store", "data"),
    Output("selected-db-store", "data"),
    Input("theme-toggle", "n_clicks"),
    Input("btn-sidebar-toggle", "n_clicks"),
    Input("db-selector", "value"),
    State("theme-store", "data"),
    State("sidebar-store", "data"),
    State("selected-db-store", "data"),
    prevent_initial_call=True,
)
def update_stores(n_theme, n_sidebar, db_value, current_theme, is_collapsed, current_db):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "theme-toggle":
        new_theme = "light" if (current_theme or "dark") == "dark" else "dark"
        return new_theme, dash.no_update, dash.no_update

    if trigger_id == "btn-sidebar-toggle":
        return dash.no_update, not is_collapsed, dash.no_update

    if trigger_id == "db-selector" and db_value:
        previous_db = session.get("current_db")
        databases = session.get("databases", [])
        selected_db_info = next((d for d in databases if d.get("base_de_datos") == db_value), None)

        client_name = selected_db_info.get("nombre_cliente") if selected_db_info else "Desconocido"
        user_email = session.get("user", {}).get("email", "Desconocido")

        logger.info(
            "Cambio de base de datos | usuario=%s anterior=%s nueva=%s cliente=%s",
            user_email,
            previous_db,
            db_value,
            client_name
        )

        session["current_db"] = db_value
        session["current_client_logo"] = (
            selected_db_info.get("url_logo") if selected_db_info else None
        )

        return dash.no_update, dash.no_update, db_value

    return dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output("mantine-provider", "forceColorScheme"),
    Output("app-shell", "navbar"),
    Output("navbar", "children"),
    Input("theme-store", "data"),
    Input("sidebar-store", "data"),
    Input("selected-db-store", "data"),
    Input("url", "pathname"),
)
def render_interface(theme, collapsed, selected_db, pathname):
    theme = theme or "dark"
    collapsed = collapsed if collapsed is not None else False
    selected_db = selected_db or "db_1"

    navbar_config = {
        "width": 80 if collapsed else 260,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    }

    sidebar_ui = render_sidebar(
        collapsed=collapsed,
        current_theme=theme,
        current_db=selected_db,
        active_path=pathname
    )

    return theme, navbar_config, sidebar_ui

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="switch_graph_theme"),
    Output({"type": "interactive-graph", "index": ALL}, "figure"),
    Input("theme-store", "data"),
    Input({"type": "interactive-graph", "index": ALL}, "id"),
    State({"type": "interactive-graph", "index": ALL}, "figure"),
)

@app.callback(
    Output("loading-overlay", "children"),
    Input("selected-db-store", "data"),
    Input("url", "pathname"),
)
def refresh_content_on_db_change(selected_db, pathname):
    return dash.page_container

if __name__ == "__main__":
    logger.info("Iniciando aplicacion Analitica")
    app.run(port=8000, debug=True)
