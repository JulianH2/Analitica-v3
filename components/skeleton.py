"""
Skeleton components para eliminar flickering durante carga de datos.
Renderiza inmediatamente estructuras animadas que se reemplazan por datos reales.
"""

from dash import html

# =============================================================================
# SKELETON BASE
# =============================================================================

def skeleton_box(height="20px", width="100%", class_name=""):
    """Caja skeleton base con animación shimmer."""
    return html.Div(
        className=f"skeleton-box {class_name}".strip(),
        style={"height": height, "width": width}
    )

# =============================================================================
# SKELETON KPI
# =============================================================================

def skeleton_kpi():
    """Skeleton para una tarjeta KPI individual."""
    return html.Div(
        className="skeleton-kpi",
        children=[
            skeleton_box("14px", "60%", "skeleton-kpi-title"),
            skeleton_box("32px", "80%", "skeleton-kpi-value"),
            skeleton_box("12px", "50%", "skeleton-kpi-delta"),
        ]
    )

def skeleton_kpi_row(count=4):
    """Fila de KPIs skeleton."""
    return html.Div(
        className="skeleton-kpi-row",
        children=[skeleton_kpi() for _ in range(count)]
    )

# =============================================================================
# SKELETON CHART
# =============================================================================

def skeleton_chart(height="300px"):
    """Skeleton para una gráfica."""
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
    """Fila de gráficas skeleton."""
    return html.Div(
        className="skeleton-chart-row",
        children=[skeleton_chart(height) for _ in range(count)]
    )

# =============================================================================
# SKELETON TABLE
# =============================================================================

def skeleton_table(rows=5, cols=4):
    """Skeleton para una tabla."""
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

# =============================================================================
# SKELETON GAUGE
# =============================================================================

def skeleton_gauge():
    """Skeleton para un gauge/indicador circular."""
    return html.Div(
        className="skeleton-gauge",
        children=[
            html.Div(className="skeleton-gauge-circle"),
            skeleton_box("14px", "60%", "skeleton-gauge-label"),
        ]
    )

def skeleton_gauge_row(count=3):
    """Fila de gauges skeleton."""
    return html.Div(
        className="skeleton-gauge-row",
        children=[skeleton_gauge() for _ in range(count)]
    )

# =============================================================================
# SKELETON LAYOUTS POR TIPO DE PÁGINA
# =============================================================================

def skeleton_dashboard_standard():
    """Layout skeleton estándar: KPIs + 2 charts + tabla."""
    return html.Div(
        className="skeleton-layout skeleton-dashboard",
        children=[
            skeleton_kpi_row(4),
            skeleton_chart_row(2, "280px"),
            skeleton_table(5, 5),
        ]
    )

def skeleton_dashboard_with_gauges():
    """Layout skeleton con gauges: KPIs + gauges + chart."""
    return html.Div(
        className="skeleton-layout skeleton-dashboard-gauges",
        children=[
            skeleton_kpi_row(4),
            skeleton_gauge_row(3),
            skeleton_chart("300px"),
        ]
    )

def skeleton_dashboard_operational():
    """Layout skeleton para dashboards operativos."""
    return html.Div(
        className="skeleton-layout skeleton-operational",
        children=[
            # 3 KPIs principales
            html.Div(
                className="skeleton-kpi-row-3",
                children=[skeleton_kpi() for _ in range(3)]
            ),
            # 4 KPIs secundarios
            html.Div(
                className="skeleton-kpi-row",
                children=[skeleton_kpi() for _ in range(4)]
            ),
            # 2 charts de tendencia
            skeleton_chart_row(2, "340px"),
            # Fleet + Routes
            html.Div(
                className="skeleton-ops-fleet-routes",
                children=[
                    skeleton_gauge(),
                    skeleton_table(5, 4),
                ]
            ),
            # Mix + Balance
            skeleton_chart_row(2, "380px"),
        ]
    )

def skeleton_dashboard_table_focus():
    """Layout skeleton centrado en tabla: KPIs mínimos + tabla grande."""
    return html.Div(
        className="skeleton-layout skeleton-table-focus",
        children=[
            skeleton_kpi_row(3),
            skeleton_table(8, 6),
        ]
    )

def skeleton_home():
    """Layout skeleton para home: replica estructura real del dashboard."""
    return html.Div(
        className="skeleton-layout skeleton-home",
        children=[
            # Top KPIs (4) - altura 180px
            html.Div(
                className="skeleton-kpi-row",
                children=[skeleton_kpi() for _ in range(4)]
            ),

            # Main chart (400px) + side KPIs (8 cards × 92px aprox)
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

            # Maintenance section (4 KPIs)
            html.Div(
                className="skeleton-kpi-row",
                children=[skeleton_kpi() for _ in range(4)]
            ),

            # Bottom: truck (280px) + 2 donuts (280px)
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

# =============================================================================
# MAPEO DE SCREEN_ID A SKELETON
# =============================================================================

SKELETON_MAP = {
    # Home
    "home": skeleton_home,
    
    # Operational (con guiones como en las páginas)
    "operational-dashboard": skeleton_dashboard_operational,
    "operational-costs": skeleton_dashboard_standard,
    "operational-performance": skeleton_dashboard_standard,
    "operational-routes": skeleton_dashboard_table_focus,
    
    # Workshop (con guiones como en las páginas)
    "workshop-dashboard": skeleton_dashboard_with_gauges,
    "workshop-inventory": skeleton_dashboard_table_focus,
    "workshop-availability": skeleton_dashboard_standard,
    "workshop-purchases": skeleton_dashboard_table_focus,
    
    # Administration (con guiones como en las páginas)
    "administration-banks": skeleton_dashboard_standard,
    "administration-receivables": skeleton_dashboard_table_focus,  # collection usa este SCREEN_ID
    "administration-payables": skeleton_dashboard_table_focus,
}

def get_skeleton(screen_id: str):
    """
    Retorna el skeleton apropiado para una pantalla.
    Si no hay mapeo específico, retorna el estándar.
    """
    skeleton_fn = SKELETON_MAP.get(screen_id, skeleton_dashboard_standard)
    return skeleton_fn()