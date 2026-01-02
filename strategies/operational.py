import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .base_strategy import KPIStrategy

class TripsStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        metrics = data_context.get("main_dashboard", {}).get("metricas_operativas", {})
        kpi = metrics.get("viajes", {})
        val = kpi.get("valor", 0)
        meta = kpi.get("meta", 0)
        trend = ((val - meta) / meta) * 100 if meta != 0 else 0

        return {
            "title": "Total Trips",
            "value": str(val),
            "meta_text": f"Target: {meta}",
            "trend": trend,
            "icon": "tabler:truck",
            "color": "orange"
        }

    def render_detail(self, data_context):
        metrics = data_context.get("main_dashboard", {}).get("metricas_operativas", {})
        ytd = metrics.get('viajes', {}).get('ytd', 0)
        
        return dmc.Stack([
            dmc.Alert("Traffic volume compared to previous period.", color="orange", variant="light"),
            dmc.SimpleGrid(cols=2, children=[
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("Daily Average", size="xs", c="dimmed"),
                    dmc.Text(f"{int(metrics.get('viajes', {}).get('valor', 0)/30)} trips", fw=700, size="xl")
                ]),
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("YTD Cumulative", size="xs", c="dimmed"),
                    dmc.Text(f"{ytd:,}", fw=700, size="xl", c="dark")
                ])
            ])
        ])

class FleetEfficiencyStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        rend = data_context.get("main_dashboard", {}).get("rendimiento", {})
        val = rend.get("rendimiento_kms_lts", 0)
        meta = 2.10 
        trend = ((val - meta) / meta) * 100

        return {
            "title": "Fuel Efficiency",
            "value": f"{val} km/L",
            "meta_text": f"Target: {meta} km/L",
            "trend": trend,
            "icon": "tabler:gas-station",
            "color": "cyan"
        }

    def render_detail(self, data_context):
        rend = data_context.get("main_dashboard", {}).get("rendimiento", {})
        liters = rend.get("litros_total", 0)
        kms = rend.get("kilometros", 0)
        load_pct = rend.get("estado_carga", 0)

        return dmc.Stack([
            dmc.Text("Consumption & Efficiency KPIs", fw=700, mb="md"),
            
            dmc.SimpleGrid(cols=2, children=[
                dmc.Paper(p="xs", withBorder=True, bg="gray.0", children=[
                    dmc.Group([
                        DashIconify(icon="tabler:droplet", width=24, color="gray"),
                        dmc.Stack(gap=0, children=[
                            dmc.Text("Liters Consumed", size="xs", c="dimmed"),
                            dmc.Text(f"{liters:,.0f}", fw=700, size="lg")
                        ])
                    ])
                ]),
                dmc.Paper(p="xs", withBorder=True, bg="gray.0", children=[
                    dmc.Group([
                        DashIconify(icon="tabler:road", width=24, color="gray"),
                        dmc.Stack(gap=0, children=[
                            dmc.Text("Total Kms", size="xs", c="dimmed"),
                            dmc.Text(f"{kms:,.0f}", fw=700, size="lg")
                        ])
                    ])
                ]),
            ]),

            dmc.Divider(label="Load Efficiency", mt="sm"),
            
            dmc.Box([
                dmc.Group(justify="space-between", mb=5, children=[
                    dmc.Text("Load Status", fw=500, size="sm"),
                    dmc.Badge(f"{load_pct}% Loaded", color="cyan")
                ]),
                dmc.ProgressRoot(size="xl", children=[
                    dmc.ProgressSection(
                        value=load_pct, 
                        color="cyan",
                        children=[dmc.ProgressLabel(f"{load_pct}%")]
                    ),
                    dmc.ProgressSection(
                        value=100-load_pct, 
                        color="gray", 
                        children=[dmc.ProgressLabel("Empty")]
                    )
                ])
            ])
        ])

class UnitCostStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        ops = data_context.get("main_dashboard", {}).get("metricas_operativas", {})
        val = ops.get("costo_viaje_km", 0)
        
        return {
            "title": "Cost per Km",
            "value": f"${val:.2f}",
            "meta_text": "Trip Cost / Km",
            "trend": 0, 
            "icon": "tabler:calculator",
            "color": "indigo",
            "reverse_trend": True
        }

    def render_detail(self, data_context):
        ops = data_context.get("main_dashboard", {}).get("metricas_operativas", {})
        mtto = data_context.get("main_dashboard", {}).get("mantenimiento", {})
        trip_cost = ops.get("costo_viaje_km", 0)
        mtto_cost = mtto.get("costo_km", 0)

        return dmc.Stack([
            dmc.Alert("Unit breakdown per kilometer driven.", color="indigo", variant="light"),
            dmc.Group(grow=True, children=[
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("Trip Cost / Km", c="dimmed", size="xs"),
                    dmc.Text(f"${trip_cost}", fw=700, size="xl", c="blue")
                ]),
                dmc.Paper(p="md", withBorder=True, children=[
                    dmc.Text("Maint Cost / Km", c="dimmed", size="xs"),
                    dmc.Text(f"${mtto_cost}", fw=700, size="xl", c="orange")
                ])
            ])
        ])

class UnitUtilizationStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        ops = data_context.get("main_dashboard", {}).get("metricas_operativas", {})
        kpi = ops.get("unidades_utilizadas", {})
        val = kpi.get("valor", 0)
        prev = kpi.get("vs_2024", 0)
        
        trend = ((val - prev) / prev) * 100 if prev != 0 else 0

        return {
            "title": "Active Units",
            "value": str(val),
            "meta_text": f"Previous Year: {prev}",
            "trend": trend,
            "icon": "tabler:bus",
            "color": "teal"
        }

    def render_detail(self, data_context):
        res = data_context.get("main_dashboard", {}).get("resumenes", {})
        disp = res.get("disponibilidad_unidades", 0)
        
        return dmc.Stack([
            dmc.Alert("Units with at least one trip in the period.", color="teal", variant="light"),
            dmc.Paper(p="md", withBorder=True, children=[
                dmc.Text("Fleet Availability", fw=700),
                dmc.Center(
                    dmc.RingProgress(
                        sections=[{"value": disp, "color": "teal"}],
                        label=dmc.Center(dmc.Text(f"{disp}%", fw=700)),
                        size=140
                    )
                )
            ])
        ])

class ClientImpactStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        ops = data_context.get("main_dashboard", {}).get("metricas_operativas", {})
        kpi = ops.get("clientes_servidos", {})
        val = kpi.get("valor", 0)
        prev = kpi.get("vs_2024", 0)
        trend = val - prev 

        return {
            "title": "Active Clients",
            "value": str(val),
            "meta_text": f"Previous Year: {prev}",
            "trend": trend,
            "icon": "tabler:users",
            "color": "violet"
        }

    def render_detail(self, data_context):
        return dmc.Text("Client details available in Revenue Report.")