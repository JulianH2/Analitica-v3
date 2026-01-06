import dash_mantine_components as dmc
from dash_iconify import DashIconify

def create_breadcrumbs(items):
    crumbs = []
    for label, href in items:
        crumbs.append(
            dmc.Anchor(label, href=href, size="sm", style={"color": "var(--mantine-color-dimmed)", "textDecoration": "none"})
        )
    
    return dmc.Breadcrumbs(
        separator=DashIconify(icon="tabler:chevron-right", width=14, color="gray"),
        children=crumbs,
        mb="md"
    )