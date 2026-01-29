import os
import django
from django.conf import settings

# 1. Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Analitica.settings")
django.setup()

import dash
from dash import Input, Output, State, dcc, html, callback_context, ALL, ClientsideFunction
from flask import Flask, redirect, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
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

# --- Rutas de Autenticación ---
@server.route("/login/local", methods=["POST"])
def login_local_route():
    email = request.form.get("email")
    password = request.form.get("password")
    result = auth_service.login_local(email, password)
    if result is True: return redirect("/")
    session["auth_error"] = result
    return redirect("/")

@server.route("/login/<provider>")
def login_social_route(provider): return auth_service.login_social(provider)

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

# --- LAYOUT PRINCIPAL ---
def get_app_shell():
    return dmc.MantineProvider(
        id="mantine-provider",
        # El theme base es estático. El color scheme lo controla el callback maestro.
        theme=DesignSystem.get_mantine_theme(),
        children=[
            dcc.Location(id="url", refresh=False),
            
            # --- STORES (LA MEMORIA) ---
            # storage_type="local" asegura persistencia al recargar.
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
                                dmc.Text("Analítica", size="xl", fw="bold", style={"letterSpacing": "-0.5px"}),
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
    get_login_layout() if Config.ENABLE_LOGIN and not session.get("user") else get_app_shell()
)

# --- CALLBACK 1: GESTIÓN DE ESTADO (INPUTS) ---
# Este callback solo ESCRIBE en los stores. No renderiza nada.
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

    if trigger_id == "db-selector":
        if db_value:
            session["current_db"] = db_value
            return dash.no_update, dash.no_update, db_value
        
    return dash.no_update, dash.no_update, dash.no_update
# --- CALLBACK 2: RENDERIZADO MAESTRO (OUTPUTS) ---
# Este es el "Render Atómico". Calcula tema y UI en el mismo ciclo.
@app.callback(
    Output("mantine-provider", "forceColorScheme"), # <--- LA FUENTE DE LA VERDAD
    Output("app-shell", "navbar"),
    Output("navbar", "children"),
    Input("theme-store", "data"),
    Input("sidebar-store", "data"),
    Input("selected-db-store", "data"),
    Input("url", "pathname"),
)
def render_interface(theme, collapsed, selected_db, pathname):
    # 1. Normalización de datos
    theme = theme or "dark" # Fallback por defecto si el store está vacío
    collapsed = collapsed if collapsed is not None else False
    selected_db = selected_db or "db_1"
    
    # 2. Configuración del Navbar (Responsive)
    navbar_config = {
        "width": 80 if collapsed else 260,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    }
    
    # 3. Generación del Sidebar
    # Pasamos los datos limpios. Sidebar.py solo pinta, no piensa.
    sidebar_ui = render_sidebar(
        collapsed=collapsed, 
        current_theme=theme, 
        current_db=selected_db,
        active_path=pathname
    )
    
    # 4. Retorno Atómico: Tema + Configuración + UI
    return theme, navbar_config, sidebar_ui

# --- Clientside: Gráficas (Solo cosmético) ---
app.clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='switch_graph_theme'),
    Output({"type": "interactive-graph", "index": ALL}, "figure"),
    Input("theme-store", "data"), 
    Input({"type": "interactive-graph", "index": ALL}, "id"), 
    State({"type": "interactive-graph", "index": ALL}, "figure"),
)

if __name__ == "__main__":
    app.run(port=8000)