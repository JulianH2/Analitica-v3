import os
import django
import logging
import time
from flask import Flask, redirect, request, session
from werkzeug.middleware.proxy_fix import ProxyFix

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Analitica.settings")
django.setup()

import json
import dash
from dash import Input, Output, State, dcc, callback_context, ALL, MATCH, ClientsideFunction
import dash_mantine_components as dmc
from dash import html

from typing import Any, Dict, cast

from config import Config
from services.dashboard_context_mapping import PATH_SCREEN_TOKEN, DEFAULT_TIMEZONE
from services.ai_chat_service import DashboardContext
from components.layout.sidebar import render_sidebar
from components.ai_copilot_sidebar import (
    render_ai_copilot,
    get_ai_toggle_button,
    create_chat_stores
)
from pages.auth import get_login_layout
from services.auth_service import auth_service
from services.ai_chat_service import ai_chat_service
from services.chat_history_service import (
    list_conversations,
    get_conversation_with_messages,
    create_conversation,
    add_message as chat_history_add_message,
    delete_conversation,
)
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
            dcc.Store(id="selected-db-store", storage_type="session"),
            dcc.Store(id="global-date-filter", storage_type="local", data={}),
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
        if db_value == current_db:
            return dash.no_update, dash.no_update, dash.no_update

        from dashboard_core.db_helper import reset_db_failures, validate_db_quick, get_db_status
        
        db_status = get_db_status(db_value)
        if db_status["blocked"]:
            return dash.no_update, dash.no_update, dash.no_update

        if not validate_db_quick(db_value):
            return dash.no_update, dash.no_update, dash.no_update

        reset_engine()
        reset_db_failures(db_value)
        data_manager.cache.clear()
        
        databases = session.get("databases", [])
        selected_info = next((d for d in databases if d.get("base_de_datos") == db_value), None)
        
        session["current_db"] = db_value

        print("session['current_db']", session["current_db"])
        
        session["current_client_logo"] = selected_info.get("url_logo") if selected_info else None
        session.modified = True
        
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
    # Guard: only act when the triggering button was genuinely clicked (n_clicks > 0).
    trigger_value = callback_context.triggered[0].get("value") if callback_context.triggered else None
    if not trigger_value:
        return dash.no_update
    triggered = callback_context.triggered_id
    if isinstance(triggered, dict) and triggered.get("action") == "close":
        return False
    if triggered == "ai-copilot-toggle":
        return not is_open
    return dash.no_update

@app.callback(
    Output("ai-copilot-affix", "style"),
    Input("chat-open-store", "data"),
    Input("chat-mode-store", "data"),
)
def toggle_affix_visibility(is_open, mode):
    """Hide the floating toggle button when the chat is already visible (sidebar/float modes)."""
    if is_open and mode in ("sidebar", "float"):
        return {"display": "none"}
    return {}


@app.callback(
    Output("chat-mode-store", "data"),
    Output("chat-sidebar-active", "data"),
    Input("chat-mode-drawer", "n_clicks"),
    Input("chat-mode-sidebar", "n_clicks"),
    Input("chat-mode-float", "n_clicks"),
    State("chat-mode-store", "data"),
    State("chat-open-store", "data"),
    prevent_initial_call=True,
)
def change_chat_mode(drawer_clicks, sidebar_clicks, float_clicks, current_mode, is_open):
    triggered = callback_context.triggered_id
    # Guard: only act when the specific button was genuinely clicked (n_clicks > 0).
    # Prevents spurious triggers when render_chat_ui re-renders the buttons.
    clicks_map = {
        "chat-mode-drawer": drawer_clicks,
        "chat-mode-sidebar": sidebar_clicks,
        "chat-mode-float": float_clicks,
    }
    if not triggered or not clicks_map.get(str(triggered)):
        return dash.no_update, dash.no_update

    mode_map = {
        "chat-mode-drawer": "drawer",
        "chat-mode-sidebar": "sidebar",
        "chat-mode-float": "float",
    }
    new_mode = mode_map.get(str(triggered), current_mode or "drawer")
    # If already in this mode, don't re-trigger (idempotent click)
    if new_mode == (current_mode or "drawer"):
        return dash.no_update, dash.no_update
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
    Output("dashboard-context-store", "data"),
    Input("url", "pathname"),
    Input("current-page-token-store", "data"),
)
def sync_dashboard_context(pathname, token_data):
    pathname = pathname or "/"
    logger.debug("sync_dashboard_context pathname=%s token_data type=%s", pathname, type(token_data).__name__ if token_data is not None else "None")
    for path, screen_id, _ in PATH_SCREEN_TOKEN:
        if path == pathname:
            filters = {}
            if token_data:
                try:
                    filters = json.loads(token_data) if isinstance(token_data, str) else (token_data if isinstance(token_data, dict) else {})
                except Exception as ex:
                    logger.warning("sync_dashboard_context failed to parse token_data: %s", ex)
            date_range = {}
            if filters.get("year"):
                date_range["year"] = str(filters["year"])
            if filters.get("month"):
                date_range["month"] = str(filters["month"])
            out = {
                "screen_id": screen_id,
                "widget_id": None,
                "filters": filters,
                "date_range": date_range or None,
                "timezone": DEFAULT_TIMEZONE,
            }
            logger.info("sync_dashboard_context -> screen_id=%s filters=%s", screen_id, filters)
            return out
    return {"screen_id": None, "widget_id": None, "filters": None, "date_range": None, "timezone": DEFAULT_TIMEZONE}


@app.callback(
    Output("chat-messages-store", "data"),
    Output("chat-pending-store", "data"),
    Output("chat-loading", "data"),
    Output("chat-input", "value"),
    Input("chat-send", "n_clicks"),
    Input("chat-input", "n_submit"),
    Input({"type": "quick-action", "action": ALL}, "n_clicks"),
    State("chat-input", "value"),
    State("chat-messages-store", "data"),
    prevent_initial_call=True,
)
def on_user_send(send_clicks, submit, quick_clicks, input_value, messages):
    """Stage 1: immediately show the user message and set loading state."""
    triggered = callback_context.triggered_id
    user_message = None
    if triggered in ["chat-send", "chat-input"]:
        if input_value and input_value.strip():
            user_message = input_value.strip()
    elif isinstance(triggered, dict) and triggered.get("type") == "quick-action":
        if any(quick_clicks):
            user_message = triggered.get("action")
    if not user_message:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    timestamp = time.strftime("%H:%M")
    messages = list(messages or [])
    messages.append({"role": "user", "content": user_message, "timestamp": timestamp})
    return messages, user_message, True, ""


@app.callback(
    Output("chat-messages-store", "data", allow_duplicate=True),
    Output("chat-pending-store", "data", allow_duplicate=True),
    Output("chat-loading", "data", allow_duplicate=True),
    Output("current-conversation-id", "data", allow_duplicate=True),
    Input("chat-pending-store", "data"),
    State("chat-messages-store", "data"),
    State("current-conversation-id", "data"),
    State("dashboard-context-store", "data"),
    prevent_initial_call=True,
)
def on_ai_respond(pending_message, messages, current_conv_id, context_data):
    """Stage 2: call the AI model and append its response."""
    if not pending_message:
        return dash.no_update, dash.no_update, False, dash.no_update
    user = session.get("user") or {}
    ctx = None
    if context_data and isinstance(context_data, dict):
        logger.info(
            "chat context_data: screen_id=%s filters=%s date_range=%s",
            context_data.get("screen_id"),
            context_data.get("filters"),
            context_data.get("date_range"),
        )
        ctx = DashboardContext(
            screen_id=context_data.get("screen_id"),
            widget_id=context_data.get("widget_id"),
            filters=context_data.get("filters"),
            date_range=context_data.get("date_range"),
            timezone=context_data.get("timezone") or DEFAULT_TIMEZONE,
            user_id=user.get("id_licencia"),
            role_id=user.get("role_id"),
            current_db=session.get("current_db"),
        )
        logger.info("chat DashboardContext: screen_id=%s filters=%s", ctx.screen_id, ctx.filters)
    else:
        logger.warning("chat: no context_data, type=%s", type(context_data).__name__ if context_data is not None else "None")
    response, timestamp = ai_chat_service.get_response(pending_message, dashboard_context=ctx)
    messages = list(messages or [])
    messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
    # Persistir en Azure SQL
    empresa = session.get("current_db") or ""
    id_licencia = user.get("id_licencia")
    updated_conv_id = current_conv_id
    if id_licencia and empresa:
        if current_conv_id is None:
            new_id = create_conversation(int(id_licencia), empresa, title=pending_message[:256])
            if new_id is not None:
                chat_history_add_message(new_id, "user", pending_message)
                chat_history_add_message(new_id, "assistant", response)
                updated_conv_id = new_id
        else:
            chat_history_add_message(current_conv_id, "user", pending_message)
            chat_history_add_message(current_conv_id, "assistant", response)
    # Reset pending to None so this callback doesn't fire again for the same message
    return messages, None, False, updated_conv_id


@app.callback(
    Output("chat-view-store", "data"),
    Output("chat-history-list-store", "data"),
    Input("chat-history-btn", "n_clicks"),
    State("chat-view-store", "data"),
    prevent_initial_call=True,
)
def toggle_history_view(history_clicks, current_view):
    # Guard: only fire when the button was actually clicked (n_clicks > 0).
    # Prevents spurious triggers when Dash re-renders and the component reappears.
    if not history_clicks:
        return dash.no_update, dash.no_update
    # If already showing history, don't toggle back — the back arrow handles return.
    if (current_view or "chat") == "history":
        return dash.no_update, dash.no_update
    user = session.get("user") or {}
    empresa = session.get("current_db") or ""
    id_licencia = user.get("id_licencia")
    if not id_licencia or not empresa:
        return "history", []
    lst = list_conversations(int(id_licencia), empresa)
    return "history", lst


@app.callback(
    Output("chat-view-store", "data", allow_duplicate=True),
    Input({"type": "chat-nav", "action": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def handle_chat_nav(nav_clicks):
    """Handles back/forward navigation inside the chat panel (e.g., back from history)."""
    if not any(c for c in (nav_clicks or []) if c):
        return dash.no_update
    triggered = callback_context.triggered_id
    if isinstance(triggered, dict) and triggered.get("action") == "back":
        return "chat"
    return dash.no_update


@app.callback(
    Output("chat-messages-store", "data", allow_duplicate=True),
    Output("current-conversation-id", "data", allow_duplicate=True),
    Output("chat-view-store", "data", allow_duplicate=True),
    Input({"type": "history-item", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def load_conversation_from_history(clicks):
    triggered = callback_context.triggered_id
    if not isinstance(triggered, dict) or triggered.get("type") != "history-item":
        return dash.no_update, dash.no_update, dash.no_update
    conv_id = triggered.get("index")
    if conv_id is None:
        return dash.no_update, dash.no_update, dash.no_update
    conv = get_conversation_with_messages(conv_id)
    if not conv or not conv.get("messages"):
        return dash.no_update, dash.no_update, "chat"
    user = session.get("user") or {}
    if conv.get("id_licencia") != user.get("id_licencia"):
        return dash.no_update, dash.no_update, "chat"
    # Restore conversation history; reset Pydantic AI run result so context
    # doesn't bleed from a previous (unrelated) agent session.
    ai_chat_service.conversation_history = list(conv["messages"])
    ai_chat_service._last_run_result = None
    return conv["messages"], conv_id, "chat"


@app.callback(
    Output("chat-history-list-store", "data", allow_duplicate=True),
    Output("current-conversation-id", "data", allow_duplicate=True),
    Output("chat-messages-store", "data", allow_duplicate=True),
    Output("chat-view-store", "data", allow_duplicate=True),
    Input({"type": "history-delete", "index": ALL}, "n_clicks"),
    State("current-conversation-id", "data"),
    prevent_initial_call=True,
)
def delete_conversation_from_history(clicks, current_conv_id):
    """Delete a conversation from the history panel and refresh the list."""
    trigger_value = callback_context.triggered[0].get("value") if callback_context.triggered else None
    if not trigger_value:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    triggered = callback_context.triggered_id
    if not isinstance(triggered, dict) or triggered.get("type") != "history-delete":
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    conv_id = triggered.get("index")
    if not conv_id:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    delete_conversation(conv_id)
    # Refresh the history list
    user = session.get("user") or {}
    empresa = session.get("current_db") or ""
    id_licencia = user.get("id_licencia")
    new_list = list_conversations(int(id_licencia), empresa) if id_licencia and empresa else []
    # Always stay in history view. If deleted the active conversation, clear its UI.
    if str(current_conv_id) == str(conv_id):
        ai_chat_service.clear_history()
        return new_list, None, [], "history"
    return new_list, dash.no_update, dash.no_update, "history"


@app.callback(
    Output("chat-messages-store", "data", allow_duplicate=True),
    Output("current-conversation-id", "data", allow_duplicate=True),
    Output("chat-view-store", "data", allow_duplicate=True),
    Input({"type": "chat-control", "action": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def clear_conversation(actions):
    # Guard: only act when a chat-control button was genuinely clicked (n_clicks > 0).
    trigger_value = callback_context.triggered[0].get("value") if callback_context.triggered else None
    if not trigger_value:
        return dash.no_update, dash.no_update, dash.no_update
    triggered = callback_context.triggered_id
    # "new" action: start a new conversation (clear UI but keep previous conv in DB)
    if isinstance(triggered, dict) and triggered.get("action") == "new":
        ai_chat_service.clear_history()
        return [], None, "chat"
    return dash.no_update, dash.no_update, dash.no_update


@app.callback(
    Output("kpi-mention-catalog", "data"),
    Input("dashboard-context-store", "data"),
)
def update_kpi_mention_catalog(ctx_data):
    """Populate the @mention KPI list for the current screen."""
    screen_id = (ctx_data or {}).get("screen_id")
    if not screen_id:
        return []
    try:
        from components.drawer_manager import get_screen_widget_catalog
        catalog = get_screen_widget_catalog(screen_id)
        if catalog:
            #print(f"[Catalog] Screen '{screen_id}' → {len(catalog)} widgets: {[c['name'] for c in catalog]}")
            return catalog
        from services.widget_catalog_service import list_widgets_by_screen
        widgets = list_widgets_by_screen(screen_id)
        result = [{"id": w.widget_id, "name": w.widget_id.replace("_", " ").title(), "type": w.viz_type}
                  for w in widgets]
        print(f"[Catalog] Fallback for '{screen_id}' → {[r['name'] for r in result]}")
        return result
    except Exception:
        return []


@app.callback(
    Output("ai-copilot-wrapper", "children"),
    Input("chat-open-store", "data"),
    Input("chat-mode-store", "data"),
    Input("chat-messages-store", "data"),
    Input("theme-store", "data"),
    Input("chat-view-store", "data"),
    Input("chat-history-list-store", "data"),
    Input("chat-loading", "data"),
    Input("kpi-mention-catalog", "data"),
)
def render_chat_ui(is_open, mode, messages, theme, view, history_list, is_loading, kpi_catalog):
    theme = theme or "dark"
    messages = messages or []
    mode = mode or "drawer"
    view = view or "chat"
    quick_actions = ai_chat_service.get_quick_actions() if not messages else []
    return render_ai_copilot(
        is_open=is_open,
        theme=theme,
        mode=mode,
        messages=messages,
        quick_actions=quick_actions,
        view=view,
        history_list=history_list or [],
        is_loading=is_loading or False,
        kpi_catalog=kpi_catalog or [],
    )

@app.callback(
    Output("chat-input", "value", allow_duplicate=True),
    Output("chat-open-store", "data", allow_duplicate=True),
    Output("close-all-drawers", "data", allow_duplicate=True),
    Input("drawer-analyze-in-chat-btn", "n_clicks"),
    State("drawer-kpi-context-store", "data"),
    State("close-all-drawers", "data"),
    prevent_initial_call=True,
)
def analyze_kpi_in_chat(n_clicks, kpi_context, close_counter):
    """Pre-fill chat with KPI context, open the chat, and signal all drawers to close."""
    if not n_clicks or not kpi_context:
        return dash.no_update, dash.no_update, dash.no_update
    prompt = kpi_context.get("prompt", "")
    return prompt, True, (close_counter or 0) + 1


@app.callback(
    Output("drawer-kpi-excel-download", "data"),
    Input("drawer-export-excel-btn", "n_clicks"),
    State("drawer-kpi-context-store", "data"),
    prevent_initial_call=True,
)
def download_kpi_excel(n_clicks, kpi_context):
    """Generate a CSV download from the KPI export rows."""
    import pandas as pd
    if not n_clicks or not kpi_context:
        return dash.no_update
    title = kpi_context.get("title", "KPI")
    rows = kpi_context.get("export_rows", [])
    if not rows:
        return dash.no_update
    df = pd.DataFrame(rows)
    csv_string = df.to_csv(index=False, encoding="utf-8-sig")
    filename = f"{title.replace(' ', '_')}.csv"
    return dict(content=csv_string, filename=filename)


app.clientside_callback(
    """
    function(n, kpi_ctx) {
        if (!n || !kpi_ctx) return window.dash_clientside.no_update;
        var rows = kpi_ctx.export_rows || [];
        var lines = [(kpi_ctx.title || 'KPI')].concat(
            rows.map(function(r) { return r['Indicador'] + ': ' + r['Valor']; })
        );
        try { navigator.clipboard.writeText(lines.join('\\n')); } catch(e) {}
        return null;
    }
    """,
    Output("drawer-kpi-copy-feedback", "data"),
    Input("drawer-copy-data-btn", "n_clicks"),
    State("drawer-kpi-context-store", "data"),
    prevent_initial_call=True,
)


@app.callback(
    Output("chat-input", "value", allow_duplicate=True),
    Output("kpi-mention-popover", "opened", allow_duplicate=True),
    Input({"type": "kpi-mention-item", "index": ALL}, "n_clicks"),
    State("chat-input", "value"),
    prevent_initial_call=True,
)
def insert_kpi_mention(clicks, current_value):
    import re
    if not any(c for c in (clicks or []) if c):
        return dash.no_update, dash.no_update
    triggered = callback_context.triggered_id
    if not isinstance(triggered, dict):
        return dash.no_update, dash.no_update
    raw_index = str(triggered.get("index", "KPI"))
    name = raw_index.split("::")[-1] if "::" in raw_index else raw_index
    text = current_value or ""
    token = f"@{{{name}}}"
    new_text = re.sub(r'@\{?[^}]*$', token, text)
    if new_text == text:
        new_text = f"{text.rstrip()} {token}".lstrip()
    return new_text, False


@app.callback(
    Output("kpi-mention-popover", "opened", allow_duplicate=True),
    Input("chat-input", "value"),
    prevent_initial_call=True,
)
def auto_open_mention_popover(value):
    """Open the KPI mention popover when the user types @ (with or without opening brace)."""
    import re
    if value and re.search(r'@\{?[^}]*$', value):
        return True
    return False


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
    ClientsideFunction(namespace="clientside", function_name="search_table"),
    Output({"type": "ag-grid-dashboard", "index": MATCH}, "dashGridOptions"),
    Input({"type": "ag-quick-search", "index": MATCH}, "value"),
    State({"type": "ag-grid-dashboard", "index": MATCH}, "dashGridOptions"),
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