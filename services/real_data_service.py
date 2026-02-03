import pandas as pd
from services.kpi_calculator import KPICalculator

class RealDataService:
    def get_full_dashboard_data(self):
        data = self.get_base_structure()
        self._inject_main_data(data)
        self._inject_operational_data(data)
        self._inject_administration_data(data)
        self._inject_workshop_data(data)
        return data

    def get_base_structure(self):
        return {
            "main": { "dashboard": { "kpis": {}, "charts": {}, "tables": {} } },
            "operational": { "dashboard": { "kpis": {}, "charts": {}, "tables": {} } },
            "administration": { "dashboard": { "kpis": {}, "charts": {} } },
            "workshop": { "dashboard": { "kpis": {}, "charts": {}, "tables": {} } }
        }
    
    def _inject_main_data(self, data):
        main = data["main"]["dashboard"]
        
        main["kpis"]["trip_revenue"] = KPICalculator.calculate_kpi(
            title="Ingresos por Viaje",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        main["kpis"]["trip_costs"] = KPICalculator.calculate_kpi(
            title="Costos Totales",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        main["kpis"]["net_profit"] = KPICalculator.calculate_kpi(
            title="Utilidad Neta",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=False
        )
        
        main["kpis"]["profit_margin"] = KPICalculator.calculate_kpi(
            title="Margen %",
            current_value=0.1,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="percent",
            inverse=False
        )
        
        main["kpis"]["trips"] = KPICalculator.calculate_kpi(
            title="Viajes",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="number",
            unit="viajes",
            inverse=False
        )
        
        main["kpis"]["units_used"] = KPICalculator.calculate_kpi(
            title="Unidades Activas",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="uds",
            inverse=False
        )
        
        main["kpis"]["customers_served"] = KPICalculator.calculate_kpi(
            title="Clientes Atendidos",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="cli",
            inverse=False
        )
        
        main["kpis"]["bank_balance"] = KPICalculator.calculate_kpi(
            title="Bancos M.N.",
            current_value=1,
            kpi_type="currency",
            unit="MXN",
            metadata={
                "type": "currency",
                "unit": "MXN",
                "category": "financial",
                "last_updated": "2025-09-30T23:59:59",
                "extra_rows": [
                    {"label": "Ingresos", "value": "$1", "color": "green"},
                    {"label": "Egresos", "value": "$1", "color": "red"},
                    {"label": "Neto Mes", "value": "$1", "color": "blue"}
                ]
            }
        )
        
        main["kpis"]["units_availability"] = KPICalculator.calculate_kpi(
            title="Disponibilidad",
            current_value=0.1,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="percent",
            inverse=False
        )
        
        main["kpis"]["maintenance_cost_per_km"] = KPICalculator.calculate_kpi(
            title="Costo Mtto/Km",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            kpi_type="currency",
            unit="MXN/km",
            inverse=True
        )
        
        main["kpis"]["total_maintenance"] = KPICalculator.calculate_kpi(
            title="Gasto Mtto",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        main["kpis"]["fuel_yield"] = KPICalculator.calculate_kpi(
            title="Rendimiento Combustible",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="km/l"
        )
        
        main["kpis"]["total_km"] = KPICalculator.calculate_kpi(
            title="Kilómetros Totales",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="km"
        )
        
        main["kpis"]["total_liters"] = KPICalculator.calculate_kpi(
            title="Litros Totales",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="l"
        )
        
        main["kpis"]["revenue_per_km"] = KPICalculator.calculate_kpi(
            title="Ingreso x Km",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN/km"
        )
        
        main["kpis"]["mtto_interno"] = KPICalculator.calculate_kpi(
            title="Interno",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        main["kpis"]["mtto_externo"] = KPICalculator.calculate_kpi(
            title="Externo",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        main["kpis"]["mtto_llantas"] = KPICalculator.calculate_kpi(
            title="Llantas",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        main["charts"]["main_indicators"] = {
            "type": "line_chart",
            "title": "Tendencia de Ingresos Mensual",
            "description": "Comparativa de ingresos: Actual vs Anterior vs Meta",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, None, None, None],
                        "color": "#2E86AB"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#A3BAC3"
                    },
                    {
                        "name": "Meta 2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#F24236",
                        "dashed": True
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        main["charts"]["client_portfolio"] = {
            "type": "donut_chart",
            "title": "Cartera por Estatus",
            "description": "Distribución de la cartera total: $1 MXN",
            "data": {
                "labels": ["SIN CARTA COBRO", "POR VENCER", "VENCIDO"],
                "values": [0.3, 0.3, 0.3],
                "colors": ["#7BC950", "#FFD166", "#EF476F"],
                "total_formatted": "$1"
            }
        }
        
        main["charts"]["costs_by_category"] = {
            "type": "horizontal_bar_chart",
            "title": "Costos por Categoría",
            "description": "Distribución de costos operativos",
            "data": {
                "categories": ["Combustible", "Mantenimiento", "Operadores", "Casetas", "Otros"],
                "series": [
                    {
                        "name": "Costos",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Categoría"
            }
        }
        
        main["tables"]["top_clients"] = {
            "type": "table",
            "title": "Top 10 Clientes por Ingreso",
            "headers": ["Cliente", "Ingresos", "Viajes", "% Total"],
            "rows": [
                ["CLIENTE A", "$1", "1", "0.1%"],
                ["CLIENTE B", "$1", "1", "0.1%"],
                ["CLIENTE C", "$1", "1", "0.1%"],
                ["CLIENTE D", "$1", "1", "0.1%"],
                ["CLIENTE E", "$1", "1", "0.1%"]
            ]
        }
        
        main["tables"]["top_routes"] = {
            "type": "table",
            "title": "Top Rutas por Volumen",
            "headers": ["Ruta", "Viajes", "Kms", "Ingresos"],
            "rows": [
                ["RUTA A", "1", "1", "$1"],
                ["RUTA B", "1", "1", "$1"],
                ["RUTA C", "1", "1", "$1"],
                ["RUTA D", "1", "1", "$1"],
                ["RUTA E", "1", "1", "$1"]
            ]
        }

    def _inject_operational_data(self, data):
        operational = data["operational"]["dashboard"]
        
        operational["kpis"]["revenue_total"] = KPICalculator.calculate_kpi(
            title="Ingreso Viaje",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        operational["kpis"]["revenue_previous"] = KPICalculator.calculate_kpi(
            title="Ingreso Año Anterior",
            current_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        operational["kpis"]["revenue_variance"] = KPICalculator.calculate_kpi(
            title="Var vs Anterior",
            current_value=0.1,
            kpi_type="percent"
        )
        
        operational["kpis"]["total_trips"] = KPICalculator.calculate_kpi(
            title="Viajes",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="number",
            unit="viajes",
            inverse=False
        )

        operational["kpis"]["trips_previous"] = KPICalculator.calculate_kpi(
            title="Viajes Año Ant.",
            current_value=1,
            kpi_type="number",
            unit="viajes"
        )
        
        operational["kpis"]["trips_variance"] = KPICalculator.calculate_kpi(
            title="Var Viajes",
            current_value=0.1,
            kpi_type="percent"
        )
        
        operational["kpis"]["total_kilometers"] = KPICalculator.calculate_kpi(
            title="Kilómetros",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="number",
            unit="km",
            inverse=False
        )

        operational["kpis"]["kilometers_previous"] = KPICalculator.calculate_kpi(
            title="Kms Año Ant.",
            current_value=1,
            kpi_type="number",
            unit="km"
        )
        
        operational["kpis"]["kilometers_variance"] = KPICalculator.calculate_kpi(
            title="Var Kms",
            current_value=0.1,
            kpi_type="percent"
        )
        
        operational["kpis"]["revenue_per_trip"] = KPICalculator.calculate_kpi(
            title="Ingreso x Viaje",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        operational["kpis"]["revenue_per_unit"] = KPICalculator.calculate_kpi(
            title="Ingreso x Unidad",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            previous_ytd_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        operational["kpis"]["units_used"] = KPICalculator.calculate_kpi(
            title="Unidades Usadas",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="uds",
            inverse=False
        )
        
        operational["kpis"]["customers_served"] = KPICalculator.calculate_kpi(
            title="Clientes Atendidos",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="cli",
            inverse=False
        )

        operational["kpis"]["load_status"] = KPICalculator.calculate_kpi(
            title="% Carga",
            current_value=0.1,
            kpi_type="percent"
        )
        
        operational["kpis"]["profit_per_trip"] = KPICalculator.calculate_kpi(
            title="Utilidad x Viaje",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        operational["kpis"]["total_trip_cost"] = KPICalculator.calculate_kpi(
            title="Costo Total Viaje",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        operational["kpis"]["real_yield"] = KPICalculator.calculate_kpi(
            title="Rendimiento Real",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="km/l"
        )
        
        operational["kpis"]["real_kilometers"] = KPICalculator.calculate_kpi(
            title="Kilómetros Reales",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="km"
        )
        
        operational["kpis"]["liters_consumed"] = KPICalculator.calculate_kpi(
            title="Litros Consumidos",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="l",
            inverse=True
        )
        
        operational["kpis"]["km_per_trip"] = KPICalculator.calculate_kpi(
            title="Km x Viaje",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="km"
        )
        
        operational["kpis"]["liters_per_trip"] = KPICalculator.calculate_kpi(
            title="Litros x Viaje",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="l",
            inverse=True
        )
        
        # --- Gráficas y Tablas (Tus datos originales intactos) ---
        operational["charts"]["revenue_trends"] = {
            "type": "line_chart",
            "title": "Tendencia Ingresos 2025 vs 2024",
            "description": "Comparativa mensual de ingresos totales",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"],
                "series": [
                    {
                        "name": "2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#2E86AB"
                    },
                    {
                        "name": "2024",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#A3BAC3"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        operational["charts"]["trips_trends"] = {
            "type": "line_chart",
            "title": "Tendencia Viajes 2025 vs 2024",
            "description": "Evolución mensual del número de viajes",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"],
                "series": [
                    {
                        "name": "2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#06D6A0"
                    },
                    {
                        "name": "2024",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#CCCCCC"
                    }
                ],
                "y_axis_label": "Número de Viajes",
                "x_axis_label": "Meses"
            }
        }
        
        operational["charts"]["revenue_by_operation_type"] = {
            "type": "donut_chart",
            "title": "Distribución Ingresos por Tipo Operación",
            "description": "Segmentación de ingresos totales por tipo de operación",
            "data": {
                "labels": ["Dedicado", "General", "Sin Asignar"],
                "values": [0.3, 0.3, 0.3],
                "colors": ["#118AB2", "#06D6A0", "#FFD166"],
                "total_formatted": "$1"
            }
        }
        
        operational["charts"]["cost_breakdown"] = {
            "type": "donut_chart",
            "title": "Desglose Costos por Concepto",
            "description": "Distribución porcentual de costos operacionales",
            "data": {
                "labels": ["Combustible", "Mantenimiento", "Operadores", "Casetas", "Otros"],
                "values": [0.2, 0.2, 0.2, 0.2, 0.2],
                "colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#8338EC"],
                "total_formatted": "$1"
            }
        }
        
        operational["charts"]["operator_performance"] = {
            "type": "bar_chart",
            "title": "Rendimiento por Operador (Top 10)",
            "description": "Comparativa de rendimiento de combustible",
            "data": {
                "categories": ["Op-001", "Op-002", "Op-003", "Op-004", "Op-005", "Op-006", "Op-007", "Op-008", "Op-009", "Op-010"],
                "series": [
                    {
                        "name": "Rendimiento km/l",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#06D6A0"
                    }
                ],
                "y_axis_label": "km/l",
                "x_axis_label": "Operador"
            }
        }
        
        operational["charts"]["main_routes"] = {
            "type": "horizontal_bar_chart",
            "title": "Principales Rutas por Viajes",
            "description": "Top 10 rutas más transitadas",
            "data": {
                "categories": ["RUTA A", "RUTA B", "RUTA C", "RUTA D", "RUTA E", "RUTA F", "RUTA G", "RUTA H", "RUTA I", "RUTA J"],
                "series": [
                    {
                        "name": "Viajes",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    }
                ],
                "x_axis_label": "Número de Viajes",
                "y_axis_label": "Ruta"
            }
        }
        
        operational["charts"]["routes_map"] = {
            "type": "map",
            "title": "Mapa de Rutas Principales",
            "description": "Visualización geográfica de rutas activas",
            "data": {
                "routes": [
                    {
                        "origin": {"lat": 0.1, "lng": 0.1, "name": "Origen A"},
                        "destination": {"lat": 0.1, "lng": 0.1, "name": "Destino A"},
                        "trips": 1,
                        "revenue": 1
                    },
                    {
                        "origin": {"lat": 0.1, "lng": 0.1, "name": "Origen B"},
                        "destination": {"lat": 0.1, "lng": 0.1, "name": "Destino B"},
                        "trips": 1,
                        "revenue": 1
                    }
                ],
                "center": {"lat": 0.1, "lng": 0.1},
                "zoom": 1
            }
        }
        
        operational["charts"]["cost_and_profit_trends"] = {
            "type": "line_chart",
            "title": "Tendencia Costos y Utilidad",
            "description": "Evolución mensual de costos totales vs utilidad neta",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"],
                "series": [
                    {
                        "name": "Costos",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F"
                    },
                    {
                        "name": "Utilidad",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#06D6A0"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        operational["charts"]["cost_by_concept"] = {
            "type": "horizontal_bar_chart",
            "title": "Costos por Concepto",
            "description": "Distribución detallada de costos operacionales",
            "data": {
                "categories": ["Combustible", "Mantenimiento", "Salarios Operadores", "Casetas", "Seguros", "Otros"],
                "series": [
                    {
                        "name": "Costo",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Concepto"
            }
        }
        
        operational["charts"]["yield_trends"] = {
            "type": "line_chart",
            "title": "Tendencia Rendimiento Combustible",
            "description": "Evolución del rendimiento promedio mensual",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"],
                "series": [
                    {
                        "name": "Rendimiento Real",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    },
                    {
                        "name": "Meta",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#F24236",
                        "dashed": True
                    }
                ],
                "y_axis_label": "km/l",
                "x_axis_label": "Meses"
            }
        }
        
        operational["charts"]["yield_by_operation"] = {
            "type": "bar_chart",
            "title": "Rendimiento por Tipo Operación",
            "description": "Comparativa de rendimiento por categoría operacional",
            "data": {
                "categories": ["Dedicado", "General", "Sin Asignar"],
                "series": [
                    {
                        "name": "Rendimiento",
                        "data": [0.1, 0.1, 0.1],
                        "color": "#06D6A0"
                    }
                ],
                "y_axis_label": "km/l",
                "x_axis_label": "Tipo Operación"
            }
        }
        
        operational["charts"]["revenue_by_unit"] = {
            "type": "horizontal_bar_chart",
            "title": "Balanceo Ingresos por Unidad",
            "description": "Distribución de ingresos generados por cada unidad",
            "data": {
                "categories": ["Unidad 001", "Unidad 002", "Unidad 003", "Unidad 004", "Unidad 005"],
                "series": [
                    {
                        "name": "Ingresos",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Unidad"
            }
        }
        
        operational["tables"]["trip_details"] = {
            "type": "table",
            "title": "Detalle de Viajes",
            "headers": ["Folio", "Fecha", "Unidad", "Operador", "Ruta", "Kms", "Litros", "Ingreso", "Costo"],
            "rows": [
                ["V-00001", "01/01/2025", "001", "Op-001", "RUTA A", "1", "1", "$1", "$1"],
                ["V-00002", "01/01/2025", "002", "Op-002", "RUTA B", "1", "1", "$1", "$1"],
                ["V-00003", "02/01/2025", "003", "Op-003", "RUTA C", "1", "1", "$1", "$1"],
                ["V-00004", "02/01/2025", "004", "Op-004", "RUTA D", "1", "1", "$1", "$1"],
                ["V-00005", "03/01/2025", "005", "Op-005", "RUTA E", "1", "1", "$1", "$1"]
            ],
            "summary": {
                "total_trips": 1,
                "total_km": 1,
                "total_liters": 1,
                "total_revenue": "$1",
                "total_cost": "$1"
            }
        }
        
        operational["tables"]["guide_details"] = {
            "type": "table",
            "title": "Detalle Guías",
            "headers": ["Guía", "Fecha", "Cliente", "Origen", "Destino", "Producto", "Toneladas", "Ingreso"],
            "rows": [
                ["G-00001", "01/01/2025", "CLIENTE A", "ORIGEN A", "DESTINO A", "PRODUCTO A", "1", "$1"],
                ["G-00002", "01/01/2025", "CLIENTE B", "ORIGEN B", "DESTINO B", "PRODUCTO B", "1", "$1"],
                ["G-00003", "02/01/2025", "CLIENTE C", "ORIGEN C", "DESTINO C", "PRODUCTO C", "1", "$1"],
                ["G-00004", "02/01/2025", "CLIENTE D", "ORIGEN D", "DESTINO D", "PRODUCTO D", "1", "$1"],
                ["G-00005", "03/01/2025", "CLIENTE E", "ORIGEN E", "DESTINO E", "PRODUCTO E", "1", "$1"]
            ],
            "summary": {
                "total_guides": 1,
                "total_tons": 1,
                "total_revenue": "$1"
            }
        }
        
        operational["tables"]["liquidation_summary"] = {
            "type": "table",
            "title": "Resumen Liquidación",
            "headers": ["Período", "Operador", "Viajes", "Kms", "Ingreso", "Bonos", "Descuentos", "Neto"],
            "rows": [
                ["Ene-2025", "Op-001", "1", "1", "$1", "$1", "$1", "$1"],
                ["Ene-2025", "Op-002", "1", "1", "$1", "$1", "$1", "$1"],
                ["Ene-2025", "Op-003", "1", "1", "$1", "$1", "$1", "$1"],
                ["Ene-2025", "Op-004", "1", "1", "$1", "$1", "$1", "$1"],
                ["Ene-2025", "Op-005", "1", "1", "$1", "$1", "$1", "$1"]
            ],
            "summary": {
                "total_trips": 1,
                "total_km": 1,
                "total_revenue": "$1",
                "total_bonuses": "$1",
                "total_deductions": "$1",
                "total_net": "$1"
            }
        }
        
        operational["tables"]["income_by_unit_report"] = {
            "type": "table",
            "title": "Reporte Ingreso por Unidad",
            "headers": ["Unidad", "Modelo", "Tipo", "Viajes", "Kms", "Ingreso", "Costo", "Utilidad", "Margen %"],
            "rows": [
                ["001", "MODELO A", "Tractocamión", "1", "1", "$1", "$1", "$1", "0.1%"],
                ["002", "MODELO B", "Tractocamión", "1", "1", "$1", "$1", "$1", "0.1%"],
                ["003", "MODELO C", "Tractocamión", "1", "1", "$1", "$1", "$1", "0.1%"],
                ["004", "MODELO D", "Tractocamión", "1", "1", "$1", "$1", "$1", "0.1%"],
                ["005", "MODELO E", "Tractocamión", "1", "1", "$1", "$1", "$1", "0.1%"]
            ],
            "summary": {
                "total_units": 1,
                "total_trips": 1,
                "total_km": 1,
                "total_revenue": "$1",
                "total_cost": "$1",
                "total_profit": "$1",
                "avg_margin": "0.1%"
            }
        }
        
        operational["tables"]["income_by_operator_report"] = {
            "type": "table",
            "title": "Reporte Ingreso por Operador",
            "headers": ["Operador", "Viajes", "Kms", "Rendimiento", "Ingreso", "Eficiencia %"],
            "rows": [
                ["Op-001", "1", "1", "0.1", "$1", "0.1%"],
                ["Op-002", "1", "1", "0.1", "$1", "0.1%"],
                ["Op-003", "1", "1", "0.1", "$1", "0.1%"],
                ["Op-004", "1", "1", "0.1", "$1", "0.1%"],
                ["Op-005", "1", "1", "0.1", "$1", "0.1%"]
            ],
            "summary": {
                "total_operators": 1,
                "total_trips": 1,
                "total_km": 1,
                "avg_yield": "0.1",
                "total_revenue": "$1"
            }
        }
        
        operational["tables"]["margin_by_route"] = {
            "type": "table",
            "title": "Margen por Ruta",
            "headers": ["Ruta", "Viajes", "Ingreso", "Costo", "Utilidad", "Margen %"],
            "rows": [
                ["RUTA A", "1", "$1", "$1", "$1", "0.1%"],
                ["RUTA B", "1", "$1", "$1", "$1", "0.1%"],
                ["RUTA C", "1", "$1", "$1", "$1", "0.1%"],
                ["RUTA D", "1", "$1", "$1", "$1", "0.1%"],
                ["RUTA E", "1", "$1", "$1", "$1", "0.1%"]
            ],
            "summary": {
                "total_routes": 1,
                "total_trips": 1,
                "total_revenue": "$1",
                "total_cost": "$1",
                "total_profit": "$1",
                "avg_margin": "0.1%"
            }
        }
        
        operational["tables"]["top_routes"] = {
            "type": "table",
            "title": "Rutas",
            "headers": ["No.", "Ruta", "Viajes", "Kms Viaje", "Costo x Km", "Costo Viaje Total", "% Costo Total"],
            "rows": [
                ["1", "RUTA A", "1", "1", "$1", "$1", "0.1%"],
                ["2", "RUTA B", "1", "1", "$1", "$1", "0.1%"],
                ["3", "RUTA C", "1", "1", "$1", "$1", "0.1%"],
                ["4", "RUTA D", "1", "1", "$1", "$1", "0.1%"],
                ["5", "RUTA E", "1", "1", "$1", "$1", "0.1%"]
            ],
            "summary": {
                "total_trips": 1,
                "total_km": 1,
                "total_cost": "$1"
            }
        }
        
        operational["tables"]["top_clients"] = {
            "type": "table",
            "title": "Ingreso Cliente",
            "headers": ["No.", "Cliente", "Flete", "Otros", "Ingreso Viaje", "% Ingreso", "Kms Viaje"],
            "rows": [
                ["1", "CLIENTE A", "$1", "$1", "$1", "0.1%", "1"],
                ["2", "CLIENTE B", "$1", "$1", "$1", "0.1%", "1"],
                ["3", "CLIENTE C", "$1", "$1", "$1", "0.1%", "1"],
                ["4", "CLIENTE D", "$1", "$1", "$1", "0.1%", "1"],
                ["5", "CLIENTE E", "$1", "$1", "$1", "0.1%", "1"]
            ],
            "summary": {
                "total_revenue": "$1",
                "total_clients": 1,
                "total_km": 1
            }
        }

    def _inject_administration_data(self, data):
        administration = data["administration"]["dashboard"]
        
        administration["kpis"]["accounts_receivable"] = KPICalculator.calculate_kpi(
            title="Cartera Total",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        administration["kpis"]["overdue"] = KPICalculator.calculate_kpi(
            title="Vencido",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        administration["kpis"]["due_soon"] = KPICalculator.calculate_kpi(
            title="Por Vencer",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        administration["kpis"]["no_bill"] = KPICalculator.calculate_kpi(
            title="Sin Carta Cobro",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        administration["kpis"]["accounts_payable"] = KPICalculator.calculate_kpi(
            title="Cuentas por Pagar",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        administration["kpis"]["payable_overdue"] = KPICalculator.calculate_kpi(
            title="CP Vencidas",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        administration["kpis"]["bank_balance_admin"] = KPICalculator.calculate_kpi(
            title="Bancos",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        administration["kpis"]["bank_balance_usd"] = KPICalculator.calculate_kpi(
            title="Bancos USD",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="USD"
        )
        
        administration["kpis"]["cash_flow"] = KPICalculator.calculate_kpi(
            title="Flujo de Efectivo",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        administration["kpis"]["income_month"] = KPICalculator.calculate_kpi(
            title="Ingresos Mes",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        administration["kpis"]["expenses_month"] = KPICalculator.calculate_kpi(
            title="Egresos Mes",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        administration["kpis"]["collection_efficiency"] = KPICalculator.calculate_kpi(
            title="Eficiencia Cobranza",
            current_value=0.1,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="percent"
        )
        
        administration["kpis"]["avg_collection_days"] = KPICalculator.calculate_kpi(
            title="Días Promedio Cobro",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="días",
            inverse=True
        )
        
        administration["kpis"]["working_capital"] = KPICalculator.calculate_kpi(
            title="Capital de Trabajo",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )
        
        administration["kpis"]["liquidity_ratio"] = KPICalculator.calculate_kpi(
            title="Razón de Liquidez",
            current_value=0.1,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="number",
            unit="ratio"
        )
        
        administration["kpis"]["debt_ratio"] = KPICalculator.calculate_kpi(
            title="Razón de Endeudamiento",
            current_value=0.1,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="percent",
            inverse=True
        )
        
        administration["kpis"]["roe"] = KPICalculator.calculate_kpi(
            title="ROE",
            current_value=0.1,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="percent"
        )
        
        administration["kpis"]["roa"] = KPICalculator.calculate_kpi(
            title="ROA",
            current_value=0.1,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="percent"
        )
        
        administration["charts"]["receivables_by_status"] = {
            "type": "donut_chart",
            "title": "Cartera por Estatus",
            "description": "Distribución de la cartera total por estado de cobranza",
            "data": {
                "labels": ["Sin Carta Cobro", "Por Vencer", "Vencido"],
                "values": [0.3, 0.3, 0.3],
                "colors": ["#7BC950", "#FFD166", "#EF476F"],
                "total_formatted": "$1"
            }
        }
        
        administration["charts"]["receivables_trends"] = {
            "type": "line_chart",
            "title": "Tendencia Cartera 2025 vs 2024",
            "description": "Evolución mensual de la cartera total",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"],
                "series": [
                    {
                        "name": "2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#2E86AB"
                    },
                    {
                        "name": "2024",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#A3BAC3"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        administration["charts"]["top_debtors"] = {
            "type": "horizontal_bar_chart",
            "title": "Top 10 Clientes con Mayor Saldo",
            "description": "Principales deudores por monto pendiente",
            "data": {
                "categories": ["CLIENTE A", "CLIENTE B", "CLIENTE C", "CLIENTE D", "CLIENTE E", "CLIENTE F", "CLIENTE G", "CLIENTE H", "CLIENTE I", "CLIENTE J"],
                "series": [
                    {
                        "name": "Saldo",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Cliente"
            }
        }
        
        administration["charts"]["payables_by_supplier"] = {
            "type": "horizontal_bar_chart",
            "title": "Top Proveedores Cuentas por Pagar",
            "description": "Principales proveedores por monto adeudado",
            "data": {
                "categories": ["PROVEEDOR A", "PROVEEDOR B", "PROVEEDOR C", "PROVEEDOR D", "PROVEEDOR E", "PROVEEDOR F", "PROVEEDOR G", "PROVEEDOR H", "PROVEEDOR I", "PROVEEDOR J"],
                "series": [
                    {
                        "name": "Monto",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#FFD166"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Proveedor"
            }
        }
        
        administration["charts"]["cash_flow_trends"] = {
            "type": "bar_chart",
            "title": "Flujo de Efectivo Mensual",
            "description": "Ingresos vs Egresos mensuales",
            "data": {
                "categories": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"],
                "series": [
                    {
                        "name": "Ingresos",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#06D6A0"
                    },
                    {
                        "name": "Egresos",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        administration["charts"]["financial_ratios"] = {
            "type": "line_chart",
            "title": "Indicadores Financieros",
            "description": "Evolución de razones financieras clave",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep"],
                "series": [
                    {
                        "name": "Liquidez",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    },
                    {
                        "name": "Endeudamiento",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F"
                    }
                ],
                "y_axis_label": "Ratio",
                "x_axis_label": "Meses"
            }
        }

    def _inject_workshop_data(self, data):
        workshop = data["workshop"]["dashboard"]
        
        workshop["kpis"]["internal_cost"] = KPICalculator.calculate_kpi(
            title="Costo Interno",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["external_cost"] = KPICalculator.calculate_kpi(
            title="Costo Externo",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["tire_cost"] = KPICalculator.calculate_kpi(
            title="Costo Llantas",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["total_maintenance"] = KPICalculator.calculate_kpi(
            title="Total Mantenimiento",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["cost_per_km"] = KPICalculator.calculate_kpi(
            title="Costo por Km",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            kpi_type="currency",
            unit="MXN/km",
            inverse=True
        )
        
        workshop["kpis"]["availability_percent"] = KPICalculator.calculate_kpi(
            title="% Disponibilidad",
            current_value=0.58,
            previous_value=0.1,
            target_value=0.95,
            kpi_type="percent",
            metadata={
                "gauge_config": {
                    "min": 0,
                    "max": 100,
                    "warning_threshold": 70,
                    "critical_threshold": 50
                }
            }
        )
        
        workshop["kpis"]["workshop_entries"] = KPICalculator.calculate_kpi(
            title="Entradas a Taller",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="entradas",
            inverse=True
        )
        
        workshop["kpis"]["corrective_cost"] = KPICalculator.calculate_kpi(
            title="Costo Correctivo",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            metadata={
                "percentage_of_total": 0.1
            }
        )
        
        workshop["kpis"]["preventive_cost"] = KPICalculator.calculate_kpi(
            title="Costo Preventivo",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            metadata={
                "percentage_of_total": 0.1
            }
        )
        
        workshop["kpis"]["avg_repair_time"] = KPICalculator.calculate_kpi(
            title="Tiempo Promedio Reparación",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="días",
            inverse=True
        )
        
        workshop["kpis"]["units_in_workshop"] = KPICalculator.calculate_kpi(
            title="Unidades en Taller",
            current_value=18,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="uds"
        )
        
        workshop["kpis"]["pending_orders"] = KPICalculator.calculate_kpi(
            title="Órdenes Pendientes",
            current_value=12,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="órdenes"
        )
        
        workshop["kpis"]["total_purchases"] = KPICalculator.calculate_kpi(
            title="Compras Total",
            current_value=1,
            previous_value=1,
            target_value=1,
            current_ytd_value=1,
            kpi_type="currency",
            unit="MXN"
        )

        workshop["kpis"]["fuel_purchases"] = KPICalculator.calculate_kpi(
            title="Combustible",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            metadata={
                "percentage_of_total": 0.1
            }
        )

        workshop["kpis"]["parts_purchases"] = KPICalculator.calculate_kpi(
            title="Refacciones",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            metadata={
                "percentage_of_total": 0.1
            }
        )

        workshop["kpis"]["tire_purchases"] = KPICalculator.calculate_kpi(
            title="Llantas",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN",
            metadata={
                "percentage_of_total": 0.1
            }
        )

        workshop["kpis"]["initial_inventory"] = KPICalculator.calculate_kpi(
            title="Inventario Inicial",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )

        workshop["kpis"]["current_valuation"] = KPICalculator.calculate_kpi(
            title="Valorización Actual",
            current_value=1,
            previous_value=1,
            target_value=1,
            kpi_type="currency",
            unit="MXN"
        )

        workshop["kpis"]["compliance_level"] = KPICalculator.calculate_kpi(
            title="Nivel Cumplimiento",
            current_value=0.47,
            previous_value=0.1,
            target_value=0.1,
            kpi_type="percent"
        )

        workshop["kpis"]["items_with_stock"] = KPICalculator.calculate_kpi(
            title="Insumos con Existencia",
            current_value=4000,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="insumos"
        )

        workshop["kpis"]["items_without_stock"] = KPICalculator.calculate_kpi(
            title="Insumos sin Existencia",
            current_value=4000,
            previous_value=1,
            target_value=1,
            kpi_type="number",
            unit="insumos"
        )
        
        workshop["charts"]["maintenance_costs_trend"] = {
            "type": "bar_chart",
            "title": "Costo Total Mantenimiento 2025 vs. 2024",
            "description": "Comparativa mensual de costos de mantenimiento",
            "data": {
                "categories": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "Actual 2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    },
                    {
                        "name": "Anterior 2024",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#CCCCCC"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        workshop["charts"]["maintenance_by_type"] = {
            "type": "donut_chart",
            "title": "Costo por Tipo de Reparación",
            "description": "Distribución entre mantenimiento Correctivo y Preventivo",
            "data": {
                "labels": ["CORRECTIVO", "PREVENTIVO"],
                "values": [0.5, 0.5],
                "colors": ["#EF476F", "#06D6A0"],
                "total_formatted": "$1"
            }
        }
        
        workshop["charts"]["maintenance_by_family"] = {
            "type": "horizontal_bar_chart",
            "title": "Costo Total Mantenimiento por Familia y Subfamilia",
            "description": "Distribución del costo por familia de componentes",
            "data": {
                "categories": ["MOTOR", "SISTEMA DE FRENOS", "REMOLQUES", "GENERAL", "SISTEMA ELÉCTRICO"],
                "series": [
                    {
                        "name": "Costo",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    }
                ],
                "x_axis_label": "Miles MXN",
                "y_axis_label": "Familia"
            }
        }
        
        workshop["charts"]["maintenance_by_fleet"] = {
            "type": "horizontal_bar_chart",
            "title": "Costo Total Mantenimiento por Flota/Marca/Modelo",
            "description": "Distribución del costo por tipo de flota",
            "data": {
                "categories": ["GENERAL", "DEDICADO", "SIN ASIGNAR"],
                "series": [
                    {
                        "name": "Costo",
                        "data": [0.1, 0.1, 0.1],
                        "color": "#FFD166"
                    }
                ],
                "x_axis_label": "Miles MXN",
                "y_axis_label": "Flota"
            }
        }
        
        workshop["charts"]["maintenance_by_operation"] = {
            "type": "donut_chart",
            "title": "Costo por Tipo de Operación",
            "description": "Distribución del costo por área operativa",
            "data": {
                "labels": ["SIN ASIGNAR"],
                "values": [1],
                "colors": ["#8338EC"],
                "total_formatted": "$1"
            }
        }
        
        workshop["charts"]["cost_per_km_by_unit"] = {
            "type": "horizontal_bar_chart",
            "title": "Costo por Kilómetro por Unidad y Modelo",
            "description": "Ranking de unidades con mayor costo por km",
            "data": {
                "categories": ["UNIDAD 001", "UNIDAD 002", "UNIDAD 003", "UNIDAD 004", "UNIDAD 005"],
                "series": [
                    {
                        "name": "Costo/km",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F"
                    }
                ],
                "x_axis_label": "MXN/km",
                "y_axis_label": "Unidad"
            }
        }
        
        workshop["charts"]["cost_per_km_by_brand"] = {
            "type": "horizontal_bar_chart",
            "title": "Costo por Kilómetro por Marca, Modelo y Unidad",
            "description": "Comparativa de costos por marca",
            "data": {
                "categories": ["MARCA A", "MARCA B", "MARCA C", "MARCA D", "MARCA E"],
                "series": [
                    {
                        "name": "Costo/km",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    }
                ],
                "x_axis_label": "MXN/km",
                "y_axis_label": "Marca"
            }
        }
        
        workshop["charts"]["workshop_entries_by_unit"] = {
            "type": "horizontal_bar_chart",
            "title": "Entradas a Taller por Unidad",
            "description": "Frecuencia de entradas al taller por unidad",
            "data": {
                "categories": ["UNIDAD 001", "UNIDAD 002", "UNIDAD 003", "UNIDAD 004", "UNIDAD 005"],
                "series": [
                    {
                        "name": "Entradas",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#FFD166"
                    }
                ],
                "x_axis_label": "Número de Entradas",
                "y_axis_label": "Unidad"
            }
        }
        
        workshop["charts"]["availability_trends"] = {
            "type": "bar_chart",
            "title": "% Disponibilidad Unidades 2025 vs. 2024",
            "description": "Comparativa mensual de disponibilidad de unidades",
            "data": {
                "categories": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "Actual 2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#06D6A0"
                    },
                    {
                        "name": "Anterior 2024",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, None],
                        "color": "#CCCCCC"
                    },
                    {
                        "name": "Meta",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#F24236",
                        "dashed": True
                    }
                ],
                "y_axis_label": "Porcentaje %",
                "x_axis_label": "Meses"
            }
        }
        
        workshop["charts"]["entries_and_km_by_unit"] = {
            "type": "combo_chart",
            "title": "Entradas a Taller y Kms Recorridos por Unidad",
            "description": "Relación entre entradas al taller y kilómetros recorridos",
            "data": {
                "categories": ["U-001", "U-002", "U-003", "U-004", "U-005", "U-006", "U-007", "U-008"],
                "series": [
                    {
                        "name": "Entradas a Taller",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#EF476F",
                        "type": "bar"
                    },
                    {
                        "name": "Kms Unidad",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2",
                        "type": "line"
                    }
                ],
                "y_axis_left_label": "Entradas",
                "y_axis_right_label": "Kilómetros",
                "x_axis_label": "Unidad"
            }
        }
        
        workshop["charts"]["purchases_trend"] = {
            "type": "bar_chart",
            "title": "Compras 2025 vs. 2024",
            "description": "Comparativa mensual de compras totales",
            "data": {
                "categories": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "Actual 2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    },
                    {
                        "name": "Anterior 2024",
                        "data": [0.1, None, 0.1, 0.1, 0.1, None, 0.1, None, 0.1, None, 0.1, None],
                        "color": "#CCCCCC"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }

        workshop["charts"]["purchases_by_area"] = {
            "type": "horizontal_bar_chart",
            "title": "Total Compra por Área",
            "description": "Distribución de compras por ubicación",
            "data": {
                "categories": ["ÁREA A", "ÁREA B", "ÁREA C", "ÁREA D", "ÁREA E"],
                "series": [
                    {
                        "name": "Compras",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#06D6A0"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Área"
            }
        }

        workshop["charts"]["purchases_by_type"] = {
            "type": "donut_chart",
            "title": "Compras por Tipo",
            "description": "Distribución de compras por categoría",
            "data": {
                "labels": ["DIESEL", "REFACCIONES", "LLANTAS", "OTROS"],
                "values": [0.25, 0.25, 0.25, 0.25],
                "colors": ["#EF476F", "#FFD166", "#06D6A0", "#8338EC"],
                "total_formatted": "$1"
            }
        }

        workshop["charts"]["top_suppliers_chart"] = {
            "type": "horizontal_bar_chart",
            "title": "Top 10 Proveedores",
            "description": "Principales proveedores por monto de compras",
            "data": {
                "categories": ["PROVEEDOR A", "PROVEEDOR B", "PROVEEDOR C", "PROVEEDOR D", "PROVEEDOR E", "PROVEEDOR F", "PROVEEDOR G", "PROVEEDOR H", "PROVEEDOR I", "PROVEEDOR J"],
                "series": [
                    {
                        "name": "Monto",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Proveedores"
            }
        }

        workshop["charts"]["valuation_trends"] = {
            "type": "line_chart",
            "title": "Valorización Histórica 2025 vs. 2024",
            "description": "Evolución mensual del valor del inventario",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "Actual 2025",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    },
                    {
                        "name": "Anterior 2024",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, None, 0.1, 0.1, 0.1],
                        "color": "#CCCCCC"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }

        workshop["charts"]["valuation_by_area"] = {
            "type": "bar_chart",
            "title": "Valorización Actual por Área",
            "description": "Distribución del inventario por ubicación",
            "data": {
                "categories": ["ÁREA 01", "ÁREA 02", "ÁREA 03", "ÁREA 04", "ÁREA 05"],
                "series": [
                    {
                        "name": "Valor Actual",
                        "data": [0.1, 0.1, 0.1, 0.1, 0.1],
                        "color": "#118AB2"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Área"
            }
        }

        workshop["tables"]["availability_detail"] = {
            "type": "table",
            "title": "Detalle de Disponibilidad por Área/Tipo Operación/Unidad",
            "headers": ["Tipo Operación", "Días del Mes", "Días en Taller", "Días Disponibles", "Disponibilidad"],
            "rows": [
                ["SIN ASIGNAR", "4991", "2083", "2908", "58%"],
                ["CADEREYTA MULTIFLET", "93", "37", "56", "60%"],
                ["M07", "31", "14", "17", "55%"],
                ["M10", "31", "22", "9", "29%"],
                ["VMR25", "31", "1", "30", "97%"],
                ["CADEREYTA TINSA", "1922", "837", "1085", "56%"],
                ["05", "31", "31", "0", "0%"],
                ["09", "31", "31", "0", "0%"],
                ["103", "31", "31", "0", "0%"],
                ["106", "31", "31", "0", "0%"],
                ["144", "31", "1", "30", "97%"]
            ],
            "summary": {
                "total_days": "4991",
                "total_workshop_days": "2083",
                "total_available_days": "2908",
                "overall_availability": "58%"
            }
        }
        
        workshop["tables"]["expenses_by_unit"] = {
            "type": "table",
            "title": "Detalle Gastos x Unidad",
            "headers": ["Unidad", "Costo Mtto x Km", "Gasto Llantas Nuevas", "Gasto Llantas Renovadas", "Gasto Mano de Obra", "Gasto Refacciones", "Gasto Taller Externo", "Costo de Mantenimiento", "Costo Total"],
            "rows": [
                ["02", "$1", "", "", "$1", "$1", "", "$1", "$1"],
                ["03", "$1", "$1", "", "$1", "$1", "", "$1", "$1"],
                ["05", "$1", "", "", "$1", "$1", "", "$1", "$1"],
                ["07", "$1", "$1", "", "$1", "$1", "", "$1", "$1"],
                ["09", "$1", "", "", "", "$1", "$1", "$1", "$1"],
                ["106", "$1", "", "", "$1", "$1", "$1", "$1", "$1"],
                ["118", "$1", "", "", "$1", "$1", "", "$1", "$1"],
                ["21", "$1", "", "", "$1", "$1", "$1", "$1", "$1"]
            ],
            "total_row": ["TOTAL", "$1", "$1", "$1", "$1", "$1", "$1", "$1", "$1"]
        }
        
        workshop["tables"]["service_orders_detail"] = {
            "type": "table",
            "title": "Detalle Órdenes de Servicio",
            "headers": ["Área", "Orden", "Fecha Inicio", "Unidad", "Tipo Operación", "Costo Mtto Interno", "Costo Mtto Externo", "Costo Llantas", "Subtotal", "Fecha Cierre", "Tipo Reparación"],
            "rows": [
                ["ÁREA A", "2307", "22/07/2025", "03", "SIN ASIGNAR", "$1", "", "$1", "$1", "22/07/2025", "CORRECTIVO"],
                ["ÁREA A", "2300", "21/07/2025", "07", "SIN ASIGNAR", "$1", "", "$1", "$1", "21/07/2025", "CORRECTIVO"],
                ["ÁREA A", "2140", "01/07/2025", "02", "SIN ASIGNAR", "$1", "", "", "$1", "01/07/2025", "CORRECTIVO"],
                ["ÁREA A", "2148", "02/07/2025", "02", "SIN ASIGNAR", "$1", "", "", "$1", "02/07/2025", "CORRECTIVO"],
                ["ÁREA B", "2353", "09/07/2025", "05", "SIN ASIGNAR", "$1", "", "", "$1", "09/07/2025", "CORRECTIVO"],
                ["ÁREA B", "2403", "26/06/2025", "09", "SIN ASIGNAR", "", "$1", "", "$1", "03/07/2025", "CORRECTIVO"]
            ],
            "summary": {
                "total_orders": 1,
                "total_internal_cost": "$1",
                "total_external_cost": "$1",
                "total_tire_cost": "$1",
                "total_cost": "$1"
            }
        }
        
        workshop["tables"]["components_by_order"] = {
            "type": "table",
            "title": "Detalle de Componentes por Orden",
            "headers": ["Área", "Orden", "Familia", "Subfamilia", "Componente", "Costo Mtto Interno", "Costo Mtto Externo", "Costo"],
            "rows": [
                ["ÁREA A", "284", "GENERAL", "ACCESORIOS", "COMPONENTE A", "", "$1", "$1"],
                ["ÁREA A", "287", "GENERAL", "ACCESORIOS", "COMPONENTE B", "$1", "", "$1"],
                ["ÁREA A", "288", "SISTEMA ELECTRICO", "SISTEMA DE LUCES", "COMPONENTE C", "$1", "", "$1"],
                ["ÁREA B", "2313", "CHASIS Y CARROCERIA", "CARROCERIA", "COMPONENTE D", "$1", "", "$1"],
                ["ÁREA B", "2313", "GENERAL", "EQUIPO DE SEGURIDAD", "COMPONENTE E", "$1", "", "$1"],
                ["ÁREA B", "2317", "SISTEMA DE AIRE", "VALVULAS", "COMPONENTE F", "$1", "", "$1"]
            ],
            "summary": {
                "total_components": 1,
                "total_internal": "$1",
                "total_external": "$1",
                "total": "$1"
            }
        }
        
        workshop["tables"]["open_orders"] = {
            "type": "table",
            "title": "Órdenes No Cerradas",
            "headers": ["#", "Orden", "Estatus", "Fecha", "Unidad", "Tipo Reparación", "Días Abierta"],
            "rows": [
                ["1", "104", "ABIERTAS", "29/05/2024", "118", "CORRECTIVO", "1"],
                ["2", "406", "ABIERTAS", "26/12/2025", "M-32", "PREVENTIVO", "1"],
                ["3", "767", "ABIERTAS", "26/12/2025", "U-45", "CORRECTIVO", "1"],
                ["4", "3089", "ABIERTAS", "07/10/2025", "U-67", "CORRECTIVO", "1"],
                ["5", "3107", "ABIERTAS", "26/12/2025", "U-89", "PREVENTIVO", "1"],
                ["6", "118", "LIBERADAS", "05/06/2024", "U-23", "CORRECTIVO", "1"],
                ["7", "125", "LIBERADAS", "04/07/2024", "U-56", "PREVENTIVO", "1"],
                ["8", "165", "LIBERADAS", "13/12/2023", "U-78", "CORRECTIVO", "1"]
            ],
            "summary": {
                "total_open": 1,
                "total_released": 1,
                "avg_days_open": 1
            }
        }

        workshop["tables"]["valuation_by_family"] = {
            "type": "table",
            "title": "Valorización Actual por Familia, Subfamilia, Insumo y Medida",
            "headers": ["Familia", "Cantidad", "Valorización Actual", "% TG Valorización", "Estado MinMax"],
            "rows": [
                ["FAMILIA A", "1", "$1", "0.1%", "Dentro del rango"],
                ["FAMILIA B", "1", "$1", "0.1%", "Dentro del rango"],
                ["FAMILIA C", "1", "$1", "0.1%", "Dentro del rango"],
                ["FAMILIA D", "1", "$1", "0.1%", "Dentro del rango"],
                ["FAMILIA E", "1", "$1", "0.1%", "Dentro del rango"],
                ["FAMILIA F", "1", "$1", "0.1%", "Dentro del rango"],
                ["FAMILIA G", "1", "$1", "0.1%", "Dentro del rango"],
                ["FAMILIA H", "1", "$1", "0.1%", "Dentro del rango"]
            ],
            "total_row": ["TOTAL", "1", "$1", "100.00%", ""]
        }

        workshop["tables"]["purchase_orders_detail"] = {
            "type": "table",
            "title": "Detalle de Órdenes de Compra",
            "headers": ["Área", "Orden Compra", "Fecha", "Proveedor", "RFC", "Tipo", "Subtotal", "Total Compra"],
            "rows": [
                ["ÁREA 01", "202500556", "01/07/2025", "PROVEEDOR A", "RFC001", "REFACCIONES", "$1", "$1"],
                ["ÁREA 01", "202500560", "01/07/2025", "PROVEEDOR B", "RFC002", "REFACCIONES", "$1", "$1"],
                ["ÁREA 01", "202500572", "04/07/2025", "PROVEEDOR C", "RFC003", "UREA", "$1", "$1"],
                ["ÁREA 01", "202500574", "05/07/2025", "PROVEEDOR D", "RFC004", "REFACCIONES", "$1", "$1"],
                ["ÁREA 05", "202500015", "01/01/2025", "PROVEEDOR E", "RFC005", "SOLDADURA", "$1", "$1"],
                ["ÁREA 04", "202500114", "15/01/2025", "PROVEEDOR F", "RFC006", "REFACCIONES", "$1", "$1"]
            ],
            "summary": {
                "total_orders": 1,
                "total_amount": "$1"
            }
        }

        workshop["tables"]["inventory_detail"] = {
            "type": "table",
            "title": "Detalle Insumos de Almacén",
            "headers": ["Área", "Almacén", "Insumo", "Unidad", "Nombre", "Familia", "Cantidad", "Costo Uni"],
            "rows": [
                ["ÁREA 02", "REFACCIONES", "0107001023", "LITROS", "INSUMO A", "LUBRICANTES", "1.00", "$1"],
                ["ÁREA 01", "REFACCIONES", "0107001004", "LITROS", "INSUMO B", "LUBRICANTES", "1.00", "$1"],
                ["ÁREA 01", "REFACCIONES", "0107001002", "LITROS", "INSUMO C", "LUBRICANTES", "1.00", "$1"],
                ["ÁREA 02", "REFACCIONES", "0117001008", "LITROS", "INSUMO D", "DIESEL", "1.00", "$1"],
                ["ÁREA 01", "ACEITES", "0117001006", "LITROS", "INSUMO E", "DIESEL", "1.00", "$1"]
            ],
            "summary": {
                "total_items": 1,
                "total_with_stock": 1,
                "total_without_stock": 1
            }
        }

        return data