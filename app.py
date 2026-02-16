import os
import django
import logging
from flask import Flask, redirect, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Analitica.settings")
django.setup()

import dash
from dash import Input, Output, State, dcc, callback_context, ALL, ClientsideFunction
import dash_mantine_components as dmc
from dash import html

from typing import Any, Dict, cast

from config import Config
from components.layout.sidebar import render_sidebar
from components.ai_copilot_sidebar import (
    render_ai_copilot,
    get_ai_toggle_button,
    create_chat_stores
)
from pages.auth import get_login_layout
from services.auth_service import auth_service
from services.ai_chat_service import ai_chat_service
from design_system import DesignSystem
from settings.plotly_config import PlotlyConfig
from services.global_db import reset_engine
from services.data_manager import data_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
PlotlyConfig.setup_templates()

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
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
        "/assets/style.css"
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
    theme = cast(Any, DesignSystem.get_mantine_theme())
    header_config = cast(Any, {"height": {"base": 60, "sm": 0}})
    navbar_config = cast(Any, {"width": 260, "breakpoint": "sm", "collapsed": {"mobile": True}})
    pt_config = cast(Any, {"base": 80, "sm": "md"})

    return dmc.MantineProvider(
        id="mantine-provider",
        theme=theme,
        children=[
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="theme-store", storage_type="local"),
            dcc.Store(id="sidebar-store", storage_type="local"),
            dcc.Store(id="selected-db-store", storage_type="local", data="db_1"),
            create_chat_stores(),
            dmc.AppShell(
                id="app-shell",
                header=header_config,
                navbar=navbar_config,
                padding="md",
                children=[
                    dmc.AppShellHeader(
                        px="md",
                        hiddenFrom="sm",
                        children=dmc.Group(
                            justify="space-between",
                            h="100%",
                            children=[
                                dmc.Burger(id="mobile-burger", size="sm"),
                                dmc.Text("Analitica Mobile", size="md", fw="bold"),
                            ],
                        ),
                    ),
                    dmc.AppShellNavbar(id="navbar", children=[]),
                    dmc.AppShellMain(
                        id="app-shell-main",
                        children=dash.page_container,
                        pt=pt_config,
                    ),
                    get_ai_toggle_button(),
                    dmc.Box(
                        id="ai-copilot-wrapper",
                        children=render_ai_copilot(
                            is_open=False,
                            theme="dark",
                            mode="drawer",
                            messages=[],
                            quick_actions=ai_chat_service.get_quick_actions(),
                        ),
                    ),
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
        session["theme"] = new_theme
        return new_theme, dash.no_update, dash.no_update
    if trigger_id == "btn-sidebar-toggle":
        return dash.no_update, not is_collapsed, dash.no_update
    if trigger_id == "db-selector" and db_value:
        from dashboard_core.db_helper import reset_db_failures, validate_db_quick, get_db_status
        
        previous_db = session.get("current_db")
        databases = session.get("databases", [])
        selected_db_info = next((d for d in databases if d.get("base_de_datos") == db_value), None)
        client_name = selected_db_info.get("nombre_cliente") if selected_db_info else "Desconocido"
        user_email = session.get("user", {}).get("email", "Desconocido")
        
        db_status = get_db_status(db_value)
        if db_status["blocked"]:
            logger.warning(
                f"⚠️ Usuario {user_email} intentó cambiar a BD bloqueada: {db_value}. "
                f"Manteniendo BD actual: {previous_db}"
            )
            return dash.no_update, dash.no_update, dash.no_update
        logger.info(f"🔍 Validando acceso a BD: {db_value}")
        is_valid = validate_db_quick(db_value)
        
        if not is_valid:
            logger.error(
                f"❌ Validación falló para {db_value}. Usuario {user_email} "
                f"permanecerá en: {previous_db}"
            )
            return dash.no_update, dash.no_update, dash.no_update
        logger.info(
            f"✅ Validación exitosa. Cambio de BD | "
            f"usuario={user_email} anterior={previous_db} nueva={db_value} cliente={client_name}"
        )
        reset_db_failures(previous_db) # type: ignore
        reset_db_failures(db_value)
        reset_engine()
        data_manager.cache.clear()
        session["current_db"] = db_value
        session["current_client_logo"] = (selected_db_info.get("url_logo") if selected_db_info else None)
        
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
    navbar_config = cast(Dict[str, Any], {"width": 80 if collapsed else 260, "breakpoint": "sm", "collapsed": {"mobile": True}})
    sidebar_ui = render_sidebar(collapsed=collapsed, current_theme=theme, current_db=selected_db, active_path=pathname)
    return theme, navbar_config, sidebar_ui

@app.callback(
    Output("chat-open-store", "data"),
    Input("ai-copilot-toggle", "n_clicks"),
    Input({"type": "chat-control", "action": ALL}, "n_clicks"),
    State("chat-open-store", "data"),
    prevent_initial_call=True,
)
def toggle_chat(toggle_clicks, actions, is_open):
    triggered = callback_context.triggered_id
    if isinstance(triggered, dict) and triggered.get("action") == "close":
        return False
    if triggered == "ai-copilot-toggle":
        return not is_open
    return dash.no_update

@app.callback(
    Output("chat-mode-store", "data"),
    Output("chat-sidebar-active", "data"),
    Input("chat-mode-drawer", "n_clicks"),
    Input("chat-mode-sidebar", "n_clicks"),
    Input("chat-mode-float", "n_clicks"),
    State("chat-open-store", "data"),
    prevent_initial_call=True,
)
def change_chat_mode(drawer_clicks, sidebar_clicks, float_clicks, is_open):
    triggered = callback_context.triggered_id
    mode_map = {
        "chat-mode-drawer": "drawer",
        "chat-mode-sidebar": "sidebar",
        "chat-mode-float": "float",
    }
    new_mode = mode_map.get(triggered, "drawer") # type: ignore
    sidebar_active = (new_mode == "sidebar" and is_open)
    return new_mode, sidebar_active

@app.callback(
    Output("app-shell-main", "style"),
    Input("chat-sidebar-active", "data"),
)
def adjust_main_padding(sidebar_active):
    if sidebar_active:
        return {"marginRight": "450px", "transition": "margin-right 0.3s ease"}
    return {"marginRight": "0px", "transition": "margin-right 0.3s ease"}

@app.callback(
    Output("chat-sidebar-active", "data", allow_duplicate=True),
    Input("chat-open-store", "data"),
    Input("chat-mode-store", "data"),
    prevent_initial_call=True,
)
def update_sidebar_active(is_open, mode):
    return (mode == "sidebar" and is_open)

@app.callback(
    Output("chat-messages-store", "data"),
    Input("chat-send", "n_clicks"),
    Input("chat-input", "n_submit"),
    Input({"type": "quick-action", "action": ALL}, "n_clicks"),
    State("chat-input", "value"),
    State("chat-messages-store", "data"),
    prevent_initial_call=True,
)
def send_message(send_clicks, submit, quick_clicks, input_value, messages):
    triggered = callback_context.triggered_id
    user_message = None
    if triggered in ["chat-send", "chat-input"]:
        if input_value and input_value.strip():
            user_message = input_value.strip()
    elif isinstance(triggered, dict) and triggered.get("type") == "quick-action":
        if any(quick_clicks):
            user_message = triggered.get("action")
    if not user_message:
        return dash.no_update
    response, timestamp = ai_chat_service.get_response(user_message)
    messages = messages or []
    messages.append({"role": "user", "content": user_message, "timestamp": timestamp})
    messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
    return messages

@app.callback(
    Output("chat-input", "value"),
    Input("chat-messages-store", "data"),
    prevent_initial_call=True,
)
def clear_input_after_send(messages):
    return ""

@app.callback(
    Output("chat-messages-store", "data", allow_duplicate=True),
    Input({"type": "chat-control", "action": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def clear_conversation(actions):
    triggered = callback_context.triggered_id
    if isinstance(triggered, dict) and triggered.get("action") == "clear":
        ai_chat_service.clear_history()
        return []
    return dash.no_update


@app.callback(
    Output("ai-copilot-wrapper", "children"),
    Input("chat-open-store", "data"),
    Input("chat-mode-store", "data"),
    Input("chat-messages-store", "data"),
    Input("theme-store", "data"),
)
def render_chat_ui(is_open, mode, messages, theme):
    theme = theme or "dark"
    messages = messages or []
    mode = mode or "drawer"
    quick_actions = ai_chat_service.get_quick_actions() if not messages else []
    return render_ai_copilot(
        is_open=is_open,
        theme=theme,
        mode=mode,
        messages=messages,
        quick_actions=quick_actions,
    )

@app.callback(
    Output("app-shell", "navbar", allow_duplicate=True),
    Input("mobile-burger", "opened"),
    State("sidebar-store", "data"),
    prevent_initial_call=True,
)
def toggle_mobile_navbar(opened, collapsed):
    collapsed = collapsed if collapsed is not None else False
    return cast(Dict[str, Any], {"width": 80 if collapsed else 260, "breakpoint": "sm", "collapsed": {"mobile": not opened if opened is not None else True}})

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="switch_graph_theme"),
    Output({"type": "interactive-graph", "index": ALL}, "figure"),
    Input("theme-store", "data"),
    Input({"type": "interactive-graph", "index": ALL}, "id"),
    State({"type": "interactive-graph", "index": ALL}, "figure"),
)

app.clientside_callback(
    """
    function(searchValues, currentOptions) {
        if (!searchValues) return window.dash_clientside.no_update;
        return searchValues.map(function(val, i) {
            var opts = Object.assign({}, (currentOptions && currentOptions[i]) || {});
            opts.quickFilterText = val || "";
            return opts;
        });
    }
    """,
    Output({"type": "ag-grid-dashboard", "index": ALL}, "dashGridOptions"),
    Input({"type": "ag-quick-search", "index": ALL}, "value"),
    State({"type": "ag-grid-dashboard", "index": ALL}, "dashGridOptions"),
    prevent_initial_call=True,
)

app.clientside_callback(
    """
    function(messages) {
        if (!messages || messages.length === 0) {
            return window.dash_clientside.no_update;
        }
        setTimeout(function() {
            const container = document.getElementById('chat-messages-container');
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }, 100);
        return window.dash_clientside.no_update;
    }
    """,
    Output("chat-input", "placeholder"),
    Input("chat-messages-store", "data"),
    prevent_initial_call=True,
)

if __name__ == "__main__":
    logger.info("Iniciando aplicacion Analitica en puerto 8000")
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True,
        dev_tools_ui=True,
        dev_tools_props_check=True,
        use_reloader=False
    )