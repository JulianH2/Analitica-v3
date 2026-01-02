import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

def render_sidebar(collapsed=False):
    """
    Renders the application sidebar.
    
    Args:
        collapsed (bool): Whether the sidebar is in mini mode.
    """
    
    def nav_link(icon, label, href, is_sub=False):
        return dmc.NavLink(
            leftSection=DashIconify(icon=icon, width=20),
            label="" if collapsed else label,
            href=href,
            variant="filled" if not is_sub else "subtle",
            color="indigo",
            active=False, # Logic for active state can be added via callback or pathname matching
            style={
                "borderRadius": "8px", 
                "marginBottom": "4px",
                "paddingLeft": "20px" if is_sub and not collapsed else "12px",
                "height": "42px",
                "justifyContent": "center" if collapsed else "flex-start",
            }
        )
    
    def section_header(text):
        return dmc.Text(
            text, 
            size="xs", 
            c="dimmed", 
            fw=700, 
            mt="lg", 
            mb="xs",
            tt="uppercase",
            style={"display": "none" if collapsed else "block"}
        )

    return dmc.Stack(
        justify="space-between",
        h="100%",
        p="xs",
        children=[
            # Top Section: Navigation
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"flex": 1},
                children=dmc.Stack(gap=0, children=[
                    # Dashboard
                    nav_link("tabler:layout-dashboard", "Executive Summary", "/"),
                    
                    # Operations Section
                    section_header("Operations"),
                    nav_link("tabler:truck", "General Overview", "/ops-dashboard"),
                    nav_link("tabler:chart-arrows", "Performance & Yield", "/ops-performance", is_sub=True),
                    nav_link("tabler:calculator", "Costs & Margins", "/ops-costs", is_sub=True),
                    
                    # Maintenance Section
                    section_header("Maintenance"),
                    nav_link("tabler:tool", "Workshop Dashboard", "/taller-dashboard"),
                    nav_link("tabler:calendar-time", "Availability", "/taller-availability", is_sub=True),
                    nav_link("tabler:box", "Inventory", "/taller-inventory", is_sub=True),
                    
                    # Admin Section
                    section_header("Administration"),
                    nav_link("tabler:file-invoice", "Billing & Collection", "/admin-collection"),
                    nav_link("tabler:file-dollar", "Accounts Payable", "/admin-payables"),
                    nav_link("tabler:building-bank", "Treasury", "/admin-banks"),
                ])
            ),

            # Bottom Section: User & Toggle
            dmc.Stack(gap="xs", children=[
                dmc.Divider(),
                # Collapse Button
                dmc.ActionIcon(
                    DashIconify(icon="tabler:chevrons-right" if collapsed else "tabler:chevrons-left", width=18),
                    id="btn-sidebar-toggle",
                    variant="light", 
                    color="gray", 
                    size="lg", 
                    style={"alignSelf": "center" if collapsed else "flex-end"}
                ),
                # User Profile Placeholder
                dmc.Group(
                    gap="xs", 
                    justify="center" if collapsed else "flex-start",
                    children=[
                        dmc.Avatar("AD", radius="xl", color="indigo"),
                        html.Div([
                            dmc.Text("Admin User", size="sm", fw=500),
                            dmc.Text("Administrator", size="xs", c="dimmed")
                        ], style={"display": "none" if collapsed else "block"}),
                    ]
                )
            ])
        ]
    )