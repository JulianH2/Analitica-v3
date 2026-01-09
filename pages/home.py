from flask import session
import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from services.data_manager import DataManager
from components.smart_widget import SmartWidget
from components.visual_widget import ChartWidget
from strategies.executive import ExecutiveKPIStrategy, ExecutiveMiniKPIStrategy, ExecutiveDonutStrategy
from strategies.charts import MainTrendChartStrategy
from strategies.operational import FleetEfficiencyStrategy

dash.register_page(__name__, path='/', title='Dashboard Principal')
data_manager = DataManager()

# --- DEFINICIÓN DE WIDGETS ---
# 1. Financieros Principales
w_income = SmartWidget("h_inc", ExecutiveKPIStrategy("operaciones", "dashboard", "ingreso_viaje", "Ingresos por Viajes", "tabler:coin", "blue"))
w_costs = SmartWidget("h_cost", ExecutiveKPIStrategy("operaciones", "costos", "costo_total", "Costos por Viajes", "tabler:wallet", "red"))
w_margin = SmartWidget("h_marg", ExecutiveKPIStrategy("operaciones", "costos", "utilidad_viaje", "% Margen por Viaje", "tabler:chart-pie", "green", is_pct=True))

# 2. Operativos
w_viajes = SmartWidget("h_via", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "viajes", "Viajes", "blue", "tabler:steering-wheel"))
w_units = SmartWidget("h_uni", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "unidades_utilizadas", "Unidades Utilizadas", "cyan", "tabler:bus"))
w_clients = SmartWidget("h_cli", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "clientes_servidos", "Clientes Servidos", "indigo", "tabler:users"))

# 3. Costos Unitarios (Añadí placeholders para estructura)
w_cost_viaje_km = SmartWidget("h_cvkm", ExecutiveMiniKPIStrategy("operaciones", "dashboard", "ingreso_viaje", "Costo Viaje x Km", "orange", "tabler:ruler-2", prefix="$")) # Reutilizado por demo
w_cost_mtto_km = SmartWidget("h_cmkm", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_km", "Costo Mtto x Km", "red", "tabler:tool", prefix="$"))

# 4. Mantenimiento
w_m_total = SmartWidget("h_mt", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "total_mantenimiento", "Total Mantenimiento", "green", "tabler:tool", prefix="$"))
w_m_int = SmartWidget("h_mi", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_interno", "Taller Interno", "teal", "tabler:building-factory", prefix="$"))
w_m_ext = SmartWidget("h_me", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_externo", "Taller Externo", "lime", "tabler:building-store", prefix="$"))
w_m_llantas = SmartWidget("h_ml", ExecutiveMiniKPIStrategy("mantenimiento", "dashboard", "costo_llantas", "Costo Llantas", "gray", "tabler:circle", prefix="$"))

# Visuales
w_main_chart = ChartWidget("h_chart", MainTrendChartStrategy())
w_yield = SmartWidget("h_yield", FleetEfficiencyStrategy())
w_portfolio = ChartWidget("h_port", ExecutiveDonutStrategy("Cartera Clientes M.N.", "administracion", "facturacion_cobranza", {"SIN CARTA COBRO": "blue", "POR VENCER": "yellow", "VENCIDO": "red"}))
w_suppliers = ChartWidget("h_supp", ExecutiveDonutStrategy("Saldo Proveedores M.N.", "administracion", "cuentas_por_pagar", {"POR VENCER": "blue", "VENCIDO": "red"}))

WIDGET_REGISTRY = {
    "h_inc": w_income, "h_cost": w_costs, "h_marg": w_margin, "h_yield": w_yield
}

def layout():
    if not session.get("user"): return dmc.Text("No autorizado...")
    ctx = data_manager.get_data()

    def truck_visual():
        val = ctx["operaciones"]["dashboard"]["utilizacion"]["valor"]
        return dmc.Paper(p="md", withBorder=True, shadow="sm", radius="md", h="100%", children=[
            dmc.Text("Estado Carga Flota", size="xs", c="dimmed", fw="bold"), # type: ignore
            dmc.Center(h=100, children=DashIconify(icon="tabler:truck", width=60, color="green")),
            dmc.Progress(value=val, color="green", size="lg"),
            dmc.Text(f"{val}% Cargado", size="xs", ta="center", mt=5, fw=500) # type: ignore
        ])

    return dmc.Container(fluid=True, children=[
        dmc.Modal(id="home-smart-modal", size="xl", centered=True, children=[html.Div(id="home-modal-content")]),
        
        # --- ENCABEZADO Y FILTROS ---
        dmc.Group(justify="space-between", mb="lg", children=[
            dmc.Title("Resultado Financiero Mensual", order=3),
            dmc.Badge("Noviembre 2025", size="lg", variant="light", color="blue")
        ]),

        # --- SECCIÓN 1: INDICADORES PRINCIPALES ---
        dmc.Divider(label="Indicadores Financieros Principales", labelPosition="left", mb="sm"),
        dmc.SimpleGrid(cols={"base": 1, "md": 3}, spacing="lg", mb="lg", children=[ # type: ignore
            w_income.render(ctx), w_costs.render(ctx), w_margin.render(ctx)
        ]),

        # --- SECCIÓN 2: GRÁFICA TENDENCIA ---
        dmc.Paper(p="md", withBorder=True, mb="xl", children=[
            w_main_chart.render(ctx)
        ]),

        # --- SECCIÓN 3: MÉTRICAS OPERATIVAS Y COSTOS ---
        dmc.Divider(label="Métricas Operativas y de Costos", labelPosition="left", mb="sm"),
        dmc.Grid(gutter="md", mb="lg", children=[
            # Columna Izquierda: Métricas Operativas (3)
            dmc.GridCol(span={"base": 12, "md": 8}, children=[ # type: ignore
                dmc.SimpleGrid(cols=3, spacing="sm", children=[
                    w_viajes.render(ctx), w_units.render(ctx), w_clients.render(ctx)
                ])
            ]),
            # Columna Derecha: Costos Unitarios (2)
            dmc.GridCol(span={"base": 12, "md": 4}, children=[ # type: ignore
                dmc.SimpleGrid(cols=2, spacing="sm", children=[
                    w_cost_viaje_km.render(ctx), w_cost_mtto_km.render(ctx)
                ])
            ])
        ]),

        # --- SECCIÓN 4: MANTENIMIENTO ---
        dmc.Divider(label="Detalle de Mantenimiento", labelPosition="left", mb="sm"),
        dmc.SimpleGrid(cols={"base": 2, "md": 4}, spacing="sm", mb="xl", children=[ # type: ignore
            w_m_total.render(ctx), w_m_int.render(ctx), w_m_ext.render(ctx), w_m_llantas.render(ctx)
        ]),

        # --- SECCIÓN 5: RESÚMENES FINANCIEROS Y FLOTA ---
        dmc.Divider(label="Resúmenes Financieros y de Flota", labelPosition="left", mb="sm"),
        dmc.SimpleGrid(cols={"base": 1, "sm": 2, "lg": 4}, spacing="lg", children=[ # type: ignore
            # 1. Disponibilidad (Gauge)
            w_yield.render(ctx), 
            # 2. Carga (Camión)
            truck_visual(), 
            # 3. Cartera (Dona)
            w_portfolio.render(ctx), 
            # 4. Proveedores (Dona)
            w_suppliers.render(ctx)
        ]),
        
        dmc.Space(h=50)
    ])

@callback(
    Output("home-smart-modal", "opened"), Output("home-smart-modal", "title"), Output("home-modal-content", "children"),
    Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"), prevent_initial_call=True
)
def handle_home_click(n_clicks):
    if not dash.ctx.triggered or not any(n_clicks): return no_update, no_update, no_update
    w_id = dash.ctx.triggered_id["index"] # type: ignore
    widget = WIDGET_REGISTRY.get(w_id)
    if widget:
        ctx = data_manager.get_data()
        cfg = widget.strategy.get_card_config(ctx)
        return True, cfg.get("title"), widget.strategy.render_detail(ctx)
    return no_update, no_update, no_update