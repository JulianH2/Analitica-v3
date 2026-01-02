import dash
from dash import html, dcc, Input, Output, State, no_update, _dash_renderer
from flask import Flask, request, redirect
from flask_session import Session
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from config import Config
from components.layout.sidebar import render_sidebar

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
            bg="gray.0", 
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
                                dmc.Text("Analytics Pro", size="xl", fw=700, style={"letterSpacing": "-0.5px"})
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

app.layout = get_app_shell

@app.callback(
    Output("navbar", "width"),
    Output("navbar", "children"),
    Input("btn-sidebar-toggle", "n_clicks"),
    State("navbar", "width"),
    prevent_initial_call=True
)
def toggle_sidebar(n, current_width):
    width_val = current_width if isinstance(current_width, int) else 260
    is_collapsed = width_val == 80
    
    new_width = 260 if is_collapsed else 80
    new_collapsed_state = not is_collapsed
    
    return new_width, render_sidebar(collapsed=new_collapsed_state)

@app.callback(
    Output("app-shell", "navbar"),
    Input("btn-mobile-menu", "opened"),
    State("app-shell", "navbar"),
    prevent_initial_call=True
)
def toggle_mobile(opened, navbar_prop):
    navbar_prop["collapsed"] = {"mobile": not opened}
    return navbar_prop

if __name__ == "__main__":
    app.run(debug=True, port=8050)