"""
Skeleton components para eliminar flickering durante carga de datos.
Renderiza inmediatamente estructuras animadas que se reemplazan por datos reales.
"""

from dash import html





def skeleton_box(height="20px", width="100%", class_name=""):
    
    return html.Div(
        className=f"skeleton-box {class_name}".strip(),
        style={"height": height, "width": width}
    )





def skeleton_kpi():
    
    return html.Div(
        className="skeleton-kpi",
        children=[
            skeleton_box("14px", "60%", "skeleton-kpi-title"),
            skeleton_box("32px", "80%", "skeleton-kpi-value"),
            skeleton_box("12px", "50%", "skeleton-kpi-delta"),
        ]
    )

def skeleton_kpi_row(count=4):
    
    return html.Div(
        className="skeleton-kpi-row",
        children=[skeleton_kpi() for _ in range(count)]
    )





def skeleton_chart(height="300px"):
    
    return html.Div(
        className="skeleton-chart",
        style={"height": height},
        children=[
            skeleton_box("16px", "40%", "skeleton-chart-title"),
            html.Div(
                className="skeleton-chart-area",
                children=[
                    html.Div(className="skeleton-chart-bar", style={"height": "60%"}),
                    html.Div(className="skeleton-chart-bar", style={"height": "80%"}),
                    html.Div(className="skeleton-chart-bar", style={"height": "45%"}),
                    html.Div(className="skeleton-chart-bar", style={"height": "90%"}),
                    html.Div(className="skeleton-chart-bar", style={"height": "70%"}),
                    html.Div(className="skeleton-chart-bar", style={"height": "55%"}),
                ]
            )
        ]
    )

def skeleton_chart_row(count=2, height="300px"):
    
    return html.Div(
        className="skeleton-chart-row",
        children=[skeleton_chart(height) for _ in range(count)]
    )





def skeleton_table(rows=5, cols=4):
    
    header_row = html.Div(
        className="skeleton-table-header",
        children=[skeleton_box("16px", "100%") for _ in range(cols)]
    )
    
    body_rows = [
        html.Div(
            className="skeleton-table-row",
            children=[skeleton_box("14px", f"{70 + (i * 5) % 30}%") for _ in range(cols)]
        )
        for i in range(rows)
    ]
    
    return html.Div(
        className="skeleton-table",
        children=[header_row] + body_rows
    )





def skeleton_gauge():
    
    return html.Div(
        className="skeleton-gauge",
        children=[
            html.Div(className="skeleton-gauge-circle"),
            skeleton_box("14px", "60%", "skeleton-gauge-label"),
        ]
    )

def skeleton_gauge_row(count=3):
    
    return html.Div(
        className="skeleton-gauge-row",
        children=[skeleton_gauge() for _ in range(count)]
    )





def skeleton_dashboard_standard():
    
    return html.Div(
        className="skeleton-layout skeleton-dashboard",
        children=[
            skeleton_kpi_row(4),
            skeleton_chart_row(2, "280px"),
            skeleton_table(5, 5),
        ]
    )

def skeleton_dashboard_with_gauges():
    
    return html.Div(
        className="skeleton-layout skeleton-dashboard-gauges",
        children=[
            skeleton_kpi_row(4),
            skeleton_gauge_row(3),
            skeleton_chart("300px"),
        ]
    )

def skeleton_dashboard_operational():
    
    return html.Div(
        className="skeleton-layout skeleton-operational",
        children=[

            html.Div(
                className="skeleton-kpi-row-3",
                children=[skeleton_kpi() for _ in range(3)]
            ),

            html.Div(
                className="skeleton-kpi-row",
                children=[skeleton_kpi() for _ in range(4)]
            ),

            skeleton_chart_row(2, "340px"),

            html.Div(
                className="skeleton-ops-fleet-routes",
                children=[
                    skeleton_gauge(),
                    skeleton_table(5, 4),
                ]
            ),

            skeleton_chart_row(2, "380px"),
        ]
    )

def skeleton_dashboard_table_focus():
    
    return html.Div(
        className="skeleton-layout skeleton-table-focus",
        children=[
            skeleton_kpi_row(3),
            skeleton_table(8, 6),
        ]
    )

def skeleton_home():
    
    return html.Div(
        className="skeleton-layout skeleton-home",
        children=[

            html.Div(
                className="skeleton-kpi-row",
                children=[skeleton_kpi() for _ in range(4)]
            ),


            html.Div(
                className="skeleton-home-main",
                children=[
                    skeleton_chart("400px"),
                    html.Div(
                        className="skeleton-home-side",
                        children=[
                            html.Div(className="skeleton-kpi-row-2", children=[skeleton_kpi(), skeleton_kpi()]),
                            html.Div(className="skeleton-kpi-row-2", children=[skeleton_kpi(), skeleton_kpi()]),
                            html.Div(className="skeleton-kpi-row-2", children=[skeleton_kpi(), skeleton_kpi()]),
                            html.Div(className="skeleton-kpi-row-2", children=[skeleton_kpi(), skeleton_kpi()]),
                        ]
                    )
                ]
            ),


            html.Div(
                className="skeleton-kpi-row",
                children=[skeleton_kpi() for _ in range(4)]
            ),


            html.Div(
                className="skeleton-home-bottom",
                children=[
                    skeleton_gauge(),
                    skeleton_chart("280px"),
                    skeleton_chart("280px"),
                ]
            )
        ]
    )





SKELETON_MAP = {

    "home": skeleton_home,
    

    "operational-dashboard": skeleton_dashboard_operational,
    "operational-costs": skeleton_dashboard_standard,
    "operational-performance": skeleton_dashboard_standard,
    "operational-routes": skeleton_dashboard_table_focus,
    

    "workshop-dashboard": skeleton_dashboard_with_gauges,
    "workshop-inventory": skeleton_dashboard_table_focus,
    "workshop-availability": skeleton_dashboard_standard,
    "workshop-purchases": skeleton_dashboard_table_focus,
    

    "administration-banks": skeleton_dashboard_standard,
    "administration-receivables": skeleton_dashboard_table_focus,
    "administration-payables": skeleton_dashboard_table_focus,
}

def get_skeleton(screen_id: str):
    """
    Retorna el skeleton apropiado para una pantalla.
    Si no hay mapeo específico, retorna el estándar.
    """
    skeleton_fn = SKELETON_MAP.get(screen_id, skeleton_dashboard_standard)
    return skeleton_fn()