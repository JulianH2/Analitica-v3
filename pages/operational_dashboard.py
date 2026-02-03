from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_operational_filters, get_filter_ids
from strategies.operational import (
    OpsKPIStrategy,
    OpsTrendChartStrategy,
    OpsDonutChartStrategy,
    OpsHorizontalBarStrategy,
    OpsTableStrategy
)

# Importar OpsGaugeStrategy solo si existe, sino usar OpsKPIStrategy
try:
    from strategies.operational import OpsGaugeStrategy
except ImportError:
    OpsGaugeStrategy = OpsKPIStrategy
from settings.theme import DesignSystem
from utils.helpers import safe_get

dash.register_page(__name__, path="/ops-dashboard", title="Control Operativo")

SCREEN_ID = "operational-dashboard"

# ==========================================
# SERVICIO DE TIEMPO DINÁMICO
# ==========================================
def get_current_year():
    return datetime.now().year

def get_previous_year():
    return datetime.now().year - 1

def get_dynamic_title(base_title: str) -> str:
    """Genera título dinámico con años actuales"""
    return f"{base_title} {get_current_year()} vs {get_previous_year()}"

# ==========================================
# WIDGETS KPI CON GAUGE DONDE HAY META
# ==========================================

# Los KPIs principales usan OpsGaugeStrategy para mostrar gauge cuando hay meta
w_inc = SmartWidget(
    "go_inc",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="revenue_total",
        title="Ingreso Viaje",
        icon="tabler:cash",
        color="indigo",
        layout_config={"height": 205}
    )
)

w_tri = SmartWidget(
    "go_tri",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_trips",
        title="Viajes",
        icon="tabler:truck",
        color="green",
        layout_config={"height": 205}
    )
)

w_kms = SmartWidget(
    "go_kms",
    OpsGaugeStrategy(
        screen_id=SCREEN_ID,
        kpi_key="total_kilometers",
        title="Kilómetros",
        icon="tabler:route",
        color="yellow",
        layout_config={"height": 205}
    )
)

# KPIs secundarios sin gauge (no tienen meta)
w_avg_trip = SmartWidget(
    "avg_trip",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="revenue_per_trip",
        title="Prom. x Viaje",
        icon="tabler:calculator",
        color="blue"
    )
)

w_avg_unit = SmartWidget(
    "avg_unit",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="revenue_per_unit",
        title="Prom. x Unidad",
        icon="tabler:truck-delivery",
        color="indigo"
    )
)

w_units_qty = SmartWidget(
    "units_qty",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="units_used",
        title="Unidades Uso",
        icon="tabler:packages",
        color="violet"
    )
)

w_customers = SmartWidget(
    "customers",
    OpsKPIStrategy(
        screen_id=SCREEN_ID,
        kpi_key="customers_served",
        title="Clientes",
        icon="tabler:users",
        color="teal"
    )
)

# ==========================================
# WIDGETS DE GRÁFICAS CON TÍTULOS DINÁMICOS
# ==========================================

class DynamicTrendChartStrategy(OpsTrendChartStrategy):
    """Strategy que genera título dinámico basado en el año actual"""
    def __init__(self, screen_id, chart_key, base_title, icon="tabler:chart-line", color="indigo", layout_config=None):
        dynamic_title = get_dynamic_title(base_title)
        super().__init__(screen_id, chart_key, dynamic_title, icon, color, layout_config)
        self.base_title = base_title
    
    def get_card_config(self, data_context):
        config = super().get_card_config(data_context)
        # Actualizar título cada vez que se renderiza
        config["title"] = get_dynamic_title(self.base_title)
        return config

w_inc_comp = ChartWidget(
    "co_inc_comp",
    DynamicTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="revenue_trends",
        base_title="Ingresos",
        icon="tabler:chart-line",
        color="indigo",
        layout_config={"height": 360}
    )
)

w_trips_comp = ChartWidget(
    "co_trips_comp",
    DynamicTrendChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="trips_trends",
        base_title="Viajes",
        icon="tabler:chart-line",
        color="green",
        layout_config={"height": 360}
    )
)

w_mix = ChartWidget(
    "co_mix",
    OpsDonutChartStrategy(
        screen_id=SCREEN_ID,
        chart_key="revenue_by_operation_type",
        title="Ingreso por Tipo Operación",
        layout_config={"height": 400}
    )
)

w_unit_bal = ChartWidget(
    "co_unit_bal",
    OpsHorizontalBarStrategy(
        screen_id=SCREEN_ID,
        chart_key="revenue_by_unit",
        title="Balanceo Ingresos por Unidad",
        layout_config={"height": 360}
    )
)

WIDGET_REGISTRY = {
    "go_inc": w_inc,
    "go_tri": w_tri,
    "go_kms": w_kms,
    "avg_trip": w_avg_trip,
    "avg_unit": w_avg_unit,
    "units_qty": w_units_qty,
    "customers": w_customers
}

# ==========================================
# RENDERIZADO DE COMPONENTES DINÁMICOS
# ==========================================

def _render_fleet_status(ctx):
    """Renderiza el estado de carga de flota con datos reales"""
    # Obtener valor real del contexto
    load_data = safe_get(ctx, ["operational", "dashboard", "kpis", "load_status"], {})
    
    if isinstance(load_data, dict):
        val = load_data.get("value", 0)
        val_formatted = load_data.get("value_formatted", f"{val:.1f}%")
    else:
        val = float(load_data) if load_data else 0
        val_formatted = f"{val:.1f}%"
    
    # Convertir a porcentaje si viene como decimal
    if val < 1:
        val = val * 100
    
    # Determinar color según nivel
    if val >= 80:
        color = "green"
        icon_color = DesignSystem.SUCCESS[5]
    elif val >= 60:
        color = "yellow"
        icon_color = DesignSystem.WARNING[5]
    else:
        color = "red"
        icon_color = DesignSystem.DANGER[5]
    
    return dmc.Paper(
        p="md",
        withBorder=True,
        radius="md",
        style={"height": "420px"},
        children=[
            dmc.Stack(
                justify="center",
                align="center",
                style={"height": "100%"},
                children=[
                    dmc.Text("Estado de Carga de Flota", fw="bold", size="xs", c="dimmed", tt="uppercase"), # type: ignore
                    DashIconify(icon="tabler:truck-loading", width=60, color=icon_color),
                    dmc.Text(f"{val:.1f}%", fw="bold", size="2rem", c=color), # type: ignore
                    dmc.Text("Cargado", size="sm", c="dimmed"), # type: ignore
                    dmc.Progress(value=min(val, 100), color=color, h=22, radius="xl", style={"width": "100%"})
                ]
            )
        ]
    )

def _render_routes_tabs(ctx):
    """Renderiza tabs de rutas - vacío y cargado separadas"""
    return dmc.Paper(
        p="md",
        withBorder=True,
        radius="md",
        style={"height": "420px"},
        children=[
            dmc.Tabs(
                value="rutas_cargado",
                children=[
                    dmc.TabsList([
                        dmc.TabsTab("Rutas Vacío", value="rutas_vacio", leftSection=DashIconify(icon="tabler:map-pin-off")),
                        dmc.TabsTab("Rutas Cargado", value="rutas_cargado", leftSection=DashIconify(icon="tabler:map-pin"))
                    ]),
                    dmc.TabsPanel(
                        dmc.ScrollArea(h=350, pt="xs", children=[OpsTableStrategy(SCREEN_ID, "routes_empty").render(ctx)]),
                        value="rutas_vacio"
                    ),
                    dmc.TabsPanel(
                        dmc.ScrollArea(h=350, pt="xs", children=[OpsTableStrategy(SCREEN_ID, "routes_loaded").render(ctx)]),
                        value="rutas_cargado"
                    )
                ]
            )
        ]
    )

def _render_income_tabs(ctx):
    return dmc.Paper(
        p="md",
        withBorder=True,
        children=[
            dmc.Tabs(
                value="ingreso_cliente",
                children=[
                    dmc.TabsList([
                        dmc.TabsTab("Ingreso Cliente", value="ingreso_cliente"),
                        dmc.TabsTab("Ingreso Operador", value="ingreso_operador"),
                        dmc.TabsTab("Ingreso Unidad", value="ingreso_unidad")
                    ]),
                    dmc.TabsPanel(
                        dmc.ScrollArea(h=400, pt="md", type="auto", children=[OpsTableStrategy(SCREEN_ID, "top_clients").render(ctx)]),
                        value="ingreso_cliente"
                    ),
                    dmc.TabsPanel(
                        dmc.ScrollArea(h=400, pt="md", type="auto", children=[OpsTableStrategy(SCREEN_ID, "income_by_operator_report").render(ctx)]),
                        value="ingreso_operador"
                    ),
                    dmc.TabsPanel(
                        dmc.ScrollArea(h=400, pt="md", type="auto", children=[OpsTableStrategy(SCREEN_ID, "income_by_unit_report").render(ctx)]),
                        value="ingreso_unidad"
                    )
                ]
            )
        ]
    )

def _render_body(ctx):
    return html.Div([
        dmc.SimpleGrid(
            cols={"base": 1, "lg": 3}, # type: ignore
            spacing="md",
            mb="md",
            children=[
                w_inc.render(ctx),
                w_tri.render(ctx),
                w_kms.render(ctx)
            ]
        ),
        dmc.SimpleGrid(
            cols={"base": 2, "sm": 2, "lg": 4}, # type: ignore
            spacing="sm",
            mb="xl",
            children=[
                w_avg_trip.render(ctx),
                w_avg_unit.render(ctx),
                w_units_qty.render(ctx),
                w_customers.render(ctx)
            ]
        ),
        dmc.SimpleGrid(
            cols={"base": 1, "md": 2}, # type: ignore
            spacing="md",
            mb="xl",
            children=[
                w_inc_comp.render(ctx),
                w_trips_comp.render(ctx)
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "lg": 4}, children=[_render_fleet_status(ctx)]), # type: ignore
                dmc.GridCol(span={"base": 12, "lg": 8}, children=[_render_routes_tabs(ctx)]) # type: ignore
            ]
        ),
        dmc.Grid(
            gutter="md",
            mb="xl",
            children=[
                dmc.GridCol(span={"base": 12, "md": 5}, children=[w_mix.render(ctx)]), # type: ignore
                dmc.GridCol(
                    span={"base": 12, "md": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            children=[
                                dmc.Text("Balanceo de Ingresos por Unidad", fw=600, size="sm", mb="sm", c="dimmed"), # type: ignore
                                dmc.ScrollArea(h=360, children=[w_unit_bal.render(ctx)])
                            ]
                        )
                    ]
                )
            ]
        ),
        _render_income_tabs(ctx),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
        
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID, 
        interval_ms=60 * 60 * 1000, 
        max_intervals=-1
    )
    
    return dmc.Container(
        fluid=True,
        px="xs",
        children=[
            create_smart_modal("ops-modal"),
            *refresh_components,
            create_operational_filters(prefix="ops"),
            
            dcc.Loading(
                id="loading-ops",
                type="circle",
                color=DesignSystem.BRAND[5],
                children=html.Div(id="ops-body", children=_render_body(ctx))
            )
        ]
    )

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="ops-body",
    render_body=_render_body,
    filter_ids=get_filter_ids("ops", 5)
)

register_modal_callback("ops-modal", WIDGET_REGISTRY, SCREEN_ID)