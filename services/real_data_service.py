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
            "workshop": { "dashboard": { "kpis": {}, "charts": {} } }
        }
    
    def _inject_main_data(self, data):
        main = data["main"]["dashboard"]
        
        main["kpis"]["trip_revenue"] = KPICalculator.calculate_kpi(
            title="Ingresos por Viaje",
            current_value=209005,
            previous_value=209005,
            target_value=2090000,
            current_ytd_value=1959056,
            previous_ytd_value=56346456,
            kpi_type="currency",
            unit="MXN"
        )
        
        main["kpis"]["trip_costs"] = KPICalculator.calculate_kpi(
            title="Costos Totales",
            current_value=9716281,
            previous_value=8009507,
            target_value=9500000,
            current_ytd_value=131046917,
            previous_ytd_value=120000000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        main["kpis"]["net_profit"] = KPICalculator.calculate_kpi(
            title="Utilidad Neta",
            current_value=435345,
            previous_value=345435,
            target_value=14389249,
            kpi_type="currency",
            unit="MXN",
            inverse=False
        )
        
        main["kpis"]["profit_margin"] = KPICalculator.calculate_kpi(
            title="Margen %",
            current_value=20900885,
            previous_value=21868572,
            target_value=0.60,
            kpi_type="percent",
            inverse=False
        )
        
        main["kpis"]["trips"] = KPICalculator.calculate_kpi(
            title="Viajes",
            current_value=671,
            previous_value=773,
            target_value=848,
            current_ytd_value=8523,
            previous_ytd_value=8100,
            kpi_type="number",
            unit="viajes",
            inverse=False
        )
        
        main["kpis"]["units_used"] = KPICalculator.calculate_kpi(
            title="Unidades Activas",
            current_value=82,
            previous_value=99,
            target_value=95,
            kpi_type="number",
            unit="uds",
            inverse=False
        )
        
        main["kpis"]["customers_served"] = KPICalculator.calculate_kpi(
            title="Clientes Atendidos",
            current_value=13,
            previous_value=12,
            target_value=15,
            kpi_type="number",
            unit="cli",
            inverse=False
        )
        
        main["kpis"]["bank_balance"] = {
            "title": "Bancos M.N.",
            "value": 18933620,
            "value_formatted": "$18,933,620",
            "status_color": "teal",
            "trend_direction": "up",
            "trend_percentage": 4.7,
            "trend_formatted": "+4.7%",
            "metadata": {
                "type": "currency",
                "unit": "MXN",
                "category": "financial",
                "last_updated": "2025-09-30T23:59:59"
            },
            "extra_rows": [
                {"label": "Saldo Inicial", "value": "$18,076,634", "color": "dimmed"},
                {"label": "Ingresos", "value": "$472,111,604", "color": "green"},
                {"label": "Egresos", "value": "$471,254,617", "color": "red"},
                {"label": "Neto Mes", "value": "$856,987", "color": "blue"}
            ]
        }
        
        main["kpis"]["units_availability"] = KPICalculator.calculate_kpi(
            title="Disponibilidad",
            current_value=0.888,
            previous_value=0.85,
            target_value=0.95,
            kpi_type="percent",
            inverse=False
        )
        
        main["kpis"]["maintenance_cost_per_km"] = KPICalculator.calculate_kpi(
            title="Costo Mtto/Km",
            current_value=2.45,
            previous_value=2.10,
            target_value=2.30,
            current_ytd_value=2.40,
            kpi_type="currency",
            unit="MXN/km",
            inverse=True
        )
        
        main["kpis"]["total_maintenance"] = KPICalculator.calculate_kpi(
            title="Gasto Mtto",
            current_value=820164,
            previous_value=920000,
            target_value=800000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        main["kpis"]["fuel_yield"] = { "value": 1.91, "value_formatted": "1.91 km/l", "trend_percent": 2.5 }
        main["kpis"]["total_km"] = { "value": 509537, "value_formatted": "509,537", "trend_percent": 5.1 }
        main["kpis"]["total_liters"] = { "value": 266159, "value_formatted": "266,159", "trend_percent": 3.0 }
        main["kpis"]["revenue_per_km"] = { "value": 21.39, "value_formatted": "$21.39", "title": "Ingreso x Km" }
        
        main["kpis"]["mtto_interno"] = { "value": 820200, "value_formatted": "$820.2k", "title": "Interno" }
        main["kpis"]["mtto_externo"] = { "value": 650100, "value_formatted": "$650.1k", "title": "Externo" }
        main["kpis"]["mtto_llantas"] = { "value": 320100, "value_formatted": "$320.1k", "title": "Llantas" }
        
        main["charts"]["main_indicators"] = {
            "type": "line_chart",
            "title": "Tendencia de Ingresos Mensual",
            "description": "Comparativa de ingresos: Actual vs Anterior vs Meta",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [19.0, 20.5, 21.8, 21.2, 22.5, 23.2, 22.9, 23.5, 20.9, None, None, None],
                        "color": "#2E86AB"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [18.5, 19.2, 20.1, 19.8, 21.5, 22.0, 21.8, 22.2, 21.0, 20.5, 19.8, 19.2],
                        "color": "#A3BAC3"
                    },
                    {
                        "name": "Meta 2025",
                        "data": [20.0, 21.0, 21.5, 21.5, 22.0, 22.5, 22.5, 23.0, 22.5, 22.0, 21.5, 21.0],
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
            "description": "Distribución de la cartera total: $171,710,807 MXN",
            "data": {
                "labels": ["SIN CARTA COBRO", "POR VENCER", "VENCIDO"],
                "values": [97185032, 44168641, 30357134],
                "colors": ["#7BC950", "#FFD166", "#EF476F"],
                "total_formatted": "$171.7M"
            }
        }
        
        main["charts"]["supplier_balance"] = {
            "type": "donut_chart",
            "title": "Saldo por Proveedor",
            "description": "Distribución de saldo CxP: $2,885,966 MXN",
            "data": {
                "labels": ["POR VENCER", "VENCIDO"],
                "values": [2585972, 299994],
                "colors": ["#118AB2", "#06D6A0"],
                "total_formatted": "$2.9M"
            }
        }
        
        main["charts"]["kpi_summary"] = {
            "type": "table",
            "title": "Resumen Ejecutivo",
            "headers": ["KPI", "Actual", "Meta", "Desviación", "Estatus"],
            "rows": [
                ["Ingresos por Viaje", "$20.9M", "$23.9M", "-12.5%", "⚠️"],
                ["Costos Totales", "$9.7M", "$9.5M", "+2.3%", "⚠️"],
                ["Utilidad Neta", "$11.2M", "$14.4M", "-22.2%", "🔴"],
                ["Margen %", "53.6%", "60.0%", "-6.4%", "🟡"],
                ["Viajes", "671", "848", "-20.9%", "🔴"],
                ["Disponibilidad", "88.8%", "95.0%", "-6.2%", "🟡"]
            ]
        }
        
        main["charts"]["executive_summary"] = {
            "type": "table",
            "title": "Resumen Ejecutivo Detallado",
            "headers": ["KPI", "Valor Actual", "Mes Anterior", "Meta", "Variación", "YTD", "Estatus"],
            "rows": [
                ["Ingresos por Viajes", "$20,946,909", "$21,868,572", "$23,889,249", "-4.21%", "$195,904,545", "⚠️"],
                ["Costos Totales", "$9,716,281", "$9,976,187", "$9,500,000", "-2.61%", "$131,046,917", "⚠️"],
                ["Utilidad Neta", "$11,230,628", "$11,892,385", "$14,389,249", "-5.56%", "$64,857,628", "🔴"],
                ["Margen %", "53.61%", "54.39%", "60.0%", "-1.44%", "33.11%", "🟡"],
                ["Viajes", "671", "773", "848", "-13.20%", "8,523", "🔴"],
                ["Unidades Activas", "82", "99", "95", "-17.17%", "85.2", "🔴"],
                ["Clientes Atendidos", "13", "12", "15", "+8.33%", "125", "🟢"],
                ["Bancos M.N.", "$18,933,620", "$18,076,634", "$20,000,000", "+4.74%", "-", "🟢"],
                ["Disponibilidad", "28.88%", "27.00%", "40.0%", "+6.96%", "29.54%", "🔴"],
                ["Costo Mtto/Km", "$0.93", "$0.84", "$0.85", "+10.71%", "$0.90", "🔴"]
            ]
        }

        main["kpis"]["load_status"] = {
            "title": "Estado de Carga",
            "value": 0.93,
            "value_formatted": "93%",
            "details": {
                "cargado": 93,
                "vacio": 7
            },
            "metadata": {
                "type": "percent",
                "category": "operational"
            }
        }

        return data
    
    def _inject_operational_data(self, data):
        operational = data["operational"]["dashboard"]
        
        operational["kpis"]["trip_revenue"] = KPICalculator.calculate_kpi(
            title="Ingreso por Viaje",
            current_value=20900885,
            previous_value=21868572,
            target_value=23889249,
            current_ytd_value=195904545,
            previous_ytd_value=180000000,
            kpi_type="currency",
            unit="MXN",
            inverse=False
        )
        
        operational["kpis"]["trips"] = KPICalculator.calculate_kpi(
            title="Viajes",
            current_value=716,
            previous_value=835,
            target_value=914,
            current_ytd_value=7194,
            previous_ytd_value=6500,
            kpi_type="number",
            unit="viajes",
            inverse=False
        )
        
        operational["kpis"]["kilometers"] = KPICalculator.calculate_kpi(
            title="Kilómetros",
            current_value=439098,
            previous_value=500000,
            target_value=592357,
            current_ytd_value=4267963,
            kpi_type="number",
            unit="km",
            inverse=False
        )
        
        operational["kpis"]["units_used"] = KPICalculator.calculate_kpi(
            title="Unidades Utilizadas",
            current_value=82,
            previous_value=108,
            target_value=95,
            kpi_type="number",
            unit="unidades",
            inverse=False
        )
        
        operational["kpis"]["customers_served"] = KPICalculator.calculate_kpi(
            title="Clientes Servidos",
            current_value=15,
            previous_value=11,
            target_value=20,
            kpi_type="number",
            unit="clientes",
            inverse=False
        )
        
        operational["kpis"]["fuel_efficiency"] = KPICalculator.calculate_kpi(
            title="Rendimiento Km/Lt",
            current_value=1.86,
            previous_value=1.79,
            target_value=3.0,
            current_ytd_value=1.85,
            previous_ytd_value=1.90,
            kpi_type="number",
            unit="km/lt",
            inverse=False
        )
        
        operational["kpis"]["real_kilometers"] = KPICalculator.calculate_kpi(
            title="Kilómetros Reales",
            current_value=513165,
            previous_value=579799,
            target_value=592357,
            current_ytd_value=4561615,
            kpi_type="number",
            unit="km",
            inverse=False
        )
        
        operational["kpis"]["fuel_consumption"] = KPICalculator.calculate_kpi(
            title="Consumo Combustible",
            current_value=275490,
            previous_value=324556,
            target_value=300000,
            current_ytd_value=2462572,
            kpi_type="number",
            unit="litros",
            inverse=True
        )
        
        operational["kpis"]["total_trip_cost"] = KPICalculator.calculate_kpi(
            title="Costo Total Viaje",
            current_value=17098160,
            previous_value=9971878,
            target_value=9796576,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        operational["kpis"]["profit_margin"] = KPICalculator.calculate_kpi(
            title="Margen de Utilidad",
            current_value=18.19,
            previous_value=17.0,
            target_value=25.0,
            kpi_type="percent",
            inverse=False
        )
        
        operational["kpis"]["avg_revenue_per_trip"] = KPICalculator.calculate_kpi(
            title="Ingreso Promedio x Viaje",
            current_value=29191,
            previous_value=26190,
            target_value=32000,
            kpi_type="currency",
            unit="MXN/viaje",
            inverse=False
        )
        
        operational["kpis"]["avg_revenue_per_unit"] = KPICalculator.calculate_kpi(
            title="Ingreso Promedio x Unidad",
            current_value=254889,
            previous_value=202487,
            target_value=280000,
            kpi_type="currency",
            unit="MXN/unidad",
            inverse=False
        )
        
        operational["charts"]["revenue_trend"] = {
            "type": "line_chart",
            "title": "Tendencia de Ingresos Anual",
            "description": "Comparativa mensual: 2025 vs 2024 vs Meta",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [25.0, 22.0, 24.0, 25.0, 22.0, 24.0, 22.0, 18.0, 20.9, 14.0, 19.0, 22.0],
                        "color": "#2E86AB"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [29.0, 27.0, 28.0, 25.0, 27.0, 32.0, 29.0, 27.0, 25.0, 24.0, 22.0, 24.0],
                        "color": "#A3BAC3"
                    },
                    {
                        "name": "Meta 2025",
                        "data": [27.0, 24.0, 25.0, 24.0, 24.0, 28.0, 27.0, 24.0, 22.0, 22.0, 20.0, 22.0],
                        "color": "#F24236",
                        "dashed": True
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        operational["charts"]["trips_trend"] = {
            "type": "line_chart",
            "title": "Tendencia de Viajes Mensual",
            "description": "Cantidad de viajes: 2025 vs 2024",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [959, 955, 815, 783, 709, 750, 535, 658, 716, 671, 573, 716],
                        "color": "#118AB2"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [1069, 894, 987, 1319, 1359, 1320, 1179, 930, 835, 848, 773, 800],
                        "color": "#06D6A0"
                    }
                ],
                "y_axis_label": "Cantidad de Viajes",
                "x_axis_label": "Meses"
            }
        }
        
        operational["charts"]["operation_type_distribution"] = {
            "type": "donut_chart",
            "title": "Distribución por Tipo de Operación",
            "description": "Ingresos por categoría operativa",
            "data": {
                "labels": [
                    "REFINADOS",
                    "ARENERA LOCAL (TRAMO)", 
                    "CONTENEDOR FORÁNEO",
                    "CONTENEDOR LOCAL",
                    "ARENERA FORÁNEA",
                    "VOLTEO FORÁNEO",
                    "PLANA LOCAL",
                    "SIN ASIGNAR"
                ],
                "values": [7700000, 5956903, 1611000, 800000, 500000, 450000, 400000, 300000],
                "colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#073B4C", "#7209B7", "#F3722C", "#A3BAC3"],
                "percentages": [36.8, 28.5, 7.7, 3.8, 2.4, 2.2, 1.9, 1.4]
            }
        }
        
        operational["charts"]["cost_breakdown"] = {
            "type": "bar_chart",
            "title": "Desglose de Costos Operativos",
            "description": "Distribución del costo total por concepto",
            "data": {
                "categories": ["Combustible", "Percepción Operador", "Sueldo", "Otros", "Estancias"],
                "series": [
                    {
                        "name": "Costo Mensual",
                        "data": [13.94, 3.06, 2.27, 2.14, 0.65],
                        "color": "#EF476F"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Conceptos"
            }
        }
        
        operational["charts"]["operator_performance"] = {
            "type": "table",
            "title": "Rendimiento por Operador",
            "headers": ["Operador", "Rendimiento (Km/Lt)", "Viajes", "Kms Real", "Litros Total"],
            "rows": [
                ["AGUILAR CAZARES GERARDO", "1.95", "7", "8,530", "4,364"],
                ["AGUILAR YAÑEZ JORGE LUIS", "2.00", "7", "6,967", "3,479"],
                ["ALANIS ALANIS AMBROCIO", "1.76", "9", "3,726", "2,112"],
                ["ALMANZA CASTELLANOS MARTIN", "1.82", "12", "15,430", "8,473"],
                ["AREVALO CASTILLO JULIO", "1.81", "8", "9,850", "5,441"]
            ]
        }
        
        operational["charts"]["main_routes"] = {
            "type": "table",
            "title": "Rutas con Mayor Tráfico",
            "headers": ["Ruta", "Cliente", "Viajes Cargados", "Viajes Vacíos", "Kms Total", "Utilización %"],
            "rows": [
                ["MTY-MEX", "COCA COLA", "84", "12", "85,400", "87.5%"],
                ["MEX-GUA", "PEPSI", "76", "15", "54,200", "83.5%"],
                ["GUA-MTY", "LOGISTICA X", "92", "5", "98,206", "94.8%"],
                ["MTY-GDL", "FEMSA", "68", "18", "72,300", "79.1%"],
                ["MTY-NL", "CEMEX", "55", "8", "48,500", "87.3%"]
            ]
        }
        
        operational["charts"]["routes_map"] = {
            "type": "map_chart",
            "title": "Mapa de Rutas Activas",
            "description": "Ubicación de viajes recientes",
            "data": {
                "center": {"lat": 23.6345, "lon": -102.5528},
                "zoom": 5,
                "points": [
                    {"lat": 25.68, "lon": -100.31, "nombre": "Monterrey", "type": "origin", "count": 45},
                    {"lat": 19.43, "lon": -99.13, "nombre": "México DF", "type": "destination", "count": 32},
                    {"lat": 20.67, "lon": -103.35, "nombre": "Guadalajara", "type": "destination", "count": 28},
                    {"lat": 32.53, "lon": -117.03, "nombre": "Tijuana", "type": "destination", "count": 15},
                    {"lat": 21.16, "lon": -86.85, "nombre": "Cancún", "type": "destination", "count": 8}
                ],
                "routes": [
                    {"from": "Monterrey", "to": "México DF", "frequency": 28},
                    {"from": "Monterrey", "to": "Guadalajara", "frequency": 22},
                    {"from": "Monterrey", "to": "Tijuana", "frequency": 12}
                ]
            }
        }
        
        operational["kpis"]["profit_per_trip"] = KPICalculator.calculate_kpi(
            title="Utilidad por Viaje",
            current_value=0.1819,
            previous_value=0.1700,
            target_value=0.2500,
            kpi_type="percent",
            inverse=False
        )

        operational["kpis"]["total_trip_cost"] = KPICalculator.calculate_kpi(
            title="Costo Total Viaje",
            current_value=17098160,
            previous_value=9971878,
            target_value=9796576,
            current_ytd_value=150000000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )

        operational["kpis"]["real_yield"] = KPICalculator.calculate_kpi(
            title="Rendimiento Real (Km/Lt)",
            current_value=1.86,
            previous_value=1.79,
            target_value=3.0,
            kpi_type="number",
            unit="km/lt",
            inverse=False
        )

        operational["kpis"]["real_kilometers"] = KPICalculator.calculate_kpi(
            title="Kilómetros Reales",
            current_value=513165,
            previous_value=579799,
            target_value=592357,
            current_ytd_value=4561615,
            kpi_type="number",
            unit="km",
            inverse=False
        )

        operational["kpis"]["liters_consumed"] = KPICalculator.calculate_kpi(
            title="Litros Consumidos",
            current_value=275490,
            previous_value=324556,
            target_value=300000,
            kpi_type="number",
            unit="litros",
            inverse=True
        )
        
        operational["kpis"]["km_per_trip"] = {
            "title": "Kms por Viaje",
            "value": 716.71,
            "value_formatted": "716.71 km",
            "type": "number",
            "unit": "km/viaje"
        }

        operational["kpis"]["liters_per_trip"] = {
            "title": "Litros por Viaje",
            "value": 384.76,
            "value_formatted": "384.76 lt",
            "type": "number",
            "unit": "lt/viaje"
        }

        operational["charts"]["cost_and_profit_trends"] = {
            "type": "bar_chart",
            "chart_type": "stacked",
            "title": "Costo Viaje Total y Monto Utilidad",
            "description": "Desglose mensual del costo total vs utilidad",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "Costo Total",
                        "data": [15.5, 16.2, 15.8, 16.5, 17.0, 17.5, 17.1, 17.0, 17.1, 16.8, 16.5, 16.0],
                        "color": "#EF476F"
                    },
                    {
                        "name": "Utilidad",
                        "data": [3.8, 4.1, 4.0, 4.2, 4.3, 4.5, 4.2, 4.0, 3.8, 3.7, 3.6, 3.5],
                        "color": "#06D6A0"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }

        operational["charts"]["cost_by_concept"] = {
            "type": "horizontal_bar_chart",
            "title": "Costo Viaje Total por Concepto",
            "description": "Distribución del costo total por concepto operativo",
            "data": {
                "categories": ["Combustible", "Sueldo Operador", "Estancias", "Percepción Operador", "Otros"],
                "series": [
                    {
                        "name": "Costo Mensual",
                        "data": [13.94, 2.27, 0.65, 3.06, 2.14],
                        "color": "#118AB2"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Conceptos"
            }
        }

        operational["charts"]["yield_trends"] = {
            "type": "line_chart",
            "title": "Rendimiento Real 2025 vs 2024",
            "description": "Comparativa del rendimiento Km/Lt por mes",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [1.85, 1.83, 1.87, 1.89, 1.88, 1.86, 1.84, 1.82, 1.86, 1.87, 1.85, 1.83],
                        "color": "#06D6A0"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [1.80, 1.82, 1.85, 1.83, 1.87, 1.89, 1.86, 1.84, 1.81, 1.82, 1.83, 1.81],
                        "color": "#A3BAC3"
                    }
                ],
                "y_axis_label": "Km/Lt",
                "x_axis_label": "Meses"
            }
        }

        operational["charts"]["yield_by_operation"] = {
            "type": "donut_chart",
            "title": "Rendimiento Real por Tipo Operación",
            "description": "Rendimiento promedio por categoría operativa",
            "data": {
                "labels": ["REFINADOS", "ARENERA LOCAL", "CONTENEDOR FORÁNEO", "CONTENEDOR LOCAL", "VOLTEO FORÁNEO"],
                "values": [2.10, 1.95, 1.88, 1.92, 1.85],
                "colors": ["#EF476F", "#FFD166", "#06D6A0", "#118AB2", "#7209B7"],
                "percentages": [25.3, 23.5, 18.7, 16.2, 16.3]
            }
        }

        operational["charts"]["trip_details"] = {
            "type": "table",
            "title": "Detalle de Viajes y Guías",
            "headers": ["No. Viaje", "Fecha", "Unidad", "Operador", "Ruta", "Cliente", "Kms", "Flete", "Estatus"],
            "rows": [
                ["9590", "16/09/2025", "UTI-T", "SALAZAR GONZALEZ LUIS", "CANOITAS-OWENS MTY", "OWENS AMERICA", "680", "$28,750", "COMPLETADO"],
                ["9591", "16/09/2025", "U-118", "JUAN PEREZ", "MTY-MEX", "COCA COLA", "845", "$32,500", "COMPLETADO"],
                ["9592", "17/09/2025", "U-106", "MARIO LOPEZ", "MEX-GUA", "PEPSI", "720", "$28,150", "COMPLETADO"],
                ["9593", "17/09/2025", "U-21", "CARLOS GARCIA", "GUA-MTY", "LOGISTICA X", "890", "$34,200", "EN CURSO"],
                ["9594", "18/09/2025", "U-60", "LUIS RAMIREZ", "MTY-GDL", "FEMSA", "650", "$25,800", "COMPLETADO"]
            ],
            "summary": {
                "total_trips": 716,
                "total_km": 439098,
                "total_revenue": "$20,900,885",
                "avg_revenue_per_trip": "$29,191"
            }
        }

        operational["charts"]["guide_details"] = {
            "type": "table",
            "title": "Listado de Guías",
            "headers": ["No. Guía", "Área", "Fecha", "Factura", "Cliente", "Flete", "Estatus"],
            "rows": [
                ["CPMC-004362", "CADEREYTA MULTIFLET", "12/08/2025", "FMC-4459", "MATERIAS PRIMAS MONTERREY", "$13,226", "CONFIRMADA"],
                ["CPMC-004363", "MTY TINSA", "13/08/2025", "FMC-4460", "OWENS AMERICA", "$28,750", "FACTURADA"],
                ["CPMC-004364", "MTY MULTIFLET", "14/08/2025", "FMC-4461", "VITRO VIDRIO", "$15,420", "PENDIENTE"],
                ["CPMC-004365", "CADEREYTA TINSA", "15/08/2025", "FMC-4462", "PETROLEOS MEX", "$22,180", "CONFIRMADA"],
                ["CPMC-004366", "EL CARMEN GRANEL", "16/08/2025", "FMC-4463", "CEMEX", "$18,350", "FACTURADA"]
            ],
            "summary": {
                "total_guides": 850,
                "total_flete": "$19,832,222",
                "pending": 45,
                "confirmed": 620,
                "invoiced": 185
            }
        }

        operational["charts"]["liquidation_summary"] = {
            "type": "table",
            "title": "Resumen de Liquidaciones",
            "headers": ["No. Liquidación", "Fecha", "Operador", "Anticipo", "Costos", "Total", "Estatus"],
            "rows": [
                ["512", "09/09/2025", "SALAZAR GONZALEZ LUIS", "$9,400", "$4,600", "$14,000", "PAGADA"],
                ["513", "10/09/2025", "JUAN PEREZ", "$8,200", "$5,100", "$13,300", "PAGADA"],
                ["514", "11/09/2025", "MARIO LOPEZ", "$7,500", "$6,200", "$13,700", "PENDIENTE"],
                ["515", "12/09/2025", "CARLOS GARCIA", "$6,800", "$4,900", "$11,700", "PAGADA"],
                ["516", "13/09/2025", "LUIS RAMIREZ", "$5,900", "$5,500", "$11,400", "PENDIENTE"]
            ],
            "summary": {
                "total_liquidations": 250,
                "total_advance": "$450,000",
                "total_costs": "$3,148,982",
                "total_amount": "$3,598,982",
                "paid": 220,
                "pending": 30
            }
        }

        operational["charts"]["income_by_unit_report"] = {
            "type": "table",
            "title": "Reporte Ingresos y Viajes x Unidad",
            "headers": ["Unidad", "Viajes", "Kms Total", "Ingresos", "Costo Total", "Utilidad", "Utilidad/Km"],
            "rows": [
                ["U-118", "45", "36,540", "$1,147,500", "$892,650", "$254,850", "$6.97"],
                ["U-106", "42", "32,880", "$1,029,600", "$803,088", "$226,512", "$6.89"],
                ["U-21", "38", "30,020", "$941,600", "$734,448", "$207,152", "$6.90"],
                ["U-60", "35", "26,950", "$845,250", "$659,295", "$185,955", "$6.90"],
                ["U-46", "32", "24,640", "$772,800", "$602,784", "$170,016", "$6.90"]
            ]
        }

        operational["charts"]["income_by_operator_report"] = {
            "type": "table",
            "title": "Reporte Ingresos y Viajes x Operador",
            "headers": ["Operador", "Viajes", "Kms Total", "Ingresos", "Rendimiento (Km/Lt)", "Calificación"],
            "rows": [
                ["AGUILAR CAZARES GERARDO", "7", "8,530", "$267,050", "1.95", "4.8"],
                ["AGUILAR YAÑEZ JORGE LUIS", "7", "6,967", "$218,050", "2.00", "4.9"],
                ["ALANIS ALANIS AMBROCIO", "9", "3,726", "$116,650", "1.76", "4.2"],
                ["ALMANZA CASTELLANOS MARTIN", "12", "15,430", "$483,050", "1.82", "4.5"],
                ["AREVALO CASTILLO JULIO", "8", "9,850", "$308,400", "1.81", "4.4"]
            ]
        }

        operational["charts"]["margin_by_route"] = {
            "type": "table",
            "title": "Margen por Ruta",
            "headers": ["Ruta", "Viajes", "Ingreso Total", "Costo Total", "Utilidad", "Margen %", "Rendimiento (Km/Lt)"],
            "rows": [
                ["MTY-MEX", "84", "$2,730,000", "$2,129,400", "$600,600", "22.0%", "1.88"],
                ["MEX-GUA", "76", "$2,470,000", "$1,926,600", "$543,400", "22.0%", "1.85"],
                ["GUA-MTY", "92", "$2,990,000", "$2,332,200", "$657,800", "22.0%", "1.90"],
                ["MTY-GDL", "68", "$2,210,000", "$1,723,800", "$486,200", "22.0%", "1.87"],
                ["MTY-NL", "55", "$1,787,500", "$1,394,250", "$393,250", "22.0%", "1.84"]
            ]
        }

        return data
    
    def _inject_administration_data(self, data):
        administration = data["administration"]["dashboard"]
        
        administration["kpis"]["billed_vs_collected"] = KPICalculator.calculate_kpi(
            title="Facturado vs Cobrado",
            current_value=22127664,
            previous_value=23300000,
            target_value=30000000,
            kpi_type="currency",
            unit="MXN",
            inverse=False
        )
        
        administration["kpis"]["avg_collection_days"] = KPICalculator.calculate_kpi(
            title="Promedio Días Cartera",
            current_value=45,
            previous_value=40,
            target_value=30,
            kpi_type="number",
            unit="días",
            inverse=True
        )
        
        administration["kpis"]["client_portfolio"] = KPICalculator.calculate_kpi(
            title="Cartera de Clientes",
            current_value=171710807,
            previous_value=165000000,
            target_value=160000000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        administration["kpis"]["accumulated_billed"] = {
            "title": "Facturado Acumulado",
            "value": 194047842,
            "value_formatted": "$194,047,842",
            "status_color": "teal",
            "trend_direction": "up",
            "trend_percentage": 15.2,
            "trend_formatted": "+15.2%",
            "metadata": {
                "type": "currency",
                "unit": "MXN",
                "category": "billing",
                "description": "Total facturado año actual"
            },
            "extra_rows": [
                {"label": "Facturado Mes", "value": "$32,437,705", "color": "blue"},
                {"label": "Cobrado Acumulado", "value": "$22,127,664", "color": "green"},
                {"label": "Notas Crédito", "value": "$209,371", "color": "orange"}
            ]
        }
        
        administration["kpis"]["ap_vs_paid"] = KPICalculator.calculate_kpi(
            title="CxP vs Pagado",
            current_value=14000000,
            previous_value=13500000,
            target_value=17000000,
            kpi_type="currency",
            unit="MXN",
            inverse=False
        )
        
        administration["kpis"]["avg_payment_days"] = KPICalculator.calculate_kpi(
            title="Promedio Días Pago",
            current_value=22,
            previous_value=25,
            target_value=30,
            kpi_type="number",
            unit="días",
            inverse=False
        )
        
        administration["kpis"]["ap_balance"] = KPICalculator.calculate_kpi(
            title="Saldo CxP",
            current_value=3000000,
            previous_value=2800000,
            target_value=2500000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        administration["kpis"]["bank_availability"] = KPICalculator.calculate_kpi(
            title="Disponibilidad Bancaria",
            current_value=15400000,
            previous_value=15000000,
            target_value=20000000,
            kpi_type="currency",
            unit="MXN",
            inverse=False
        )
        
        administration["kpis"]["credit_line_usage"] = KPICalculator.calculate_kpi(
            title="Uso Líneas Crédito",
            current_value=0.85,
            previous_value=0.82,
            target_value=0.75,
            kpi_type="percent",
            inverse=True
        )
        
        administration["kpis"]["banregio_balance"] = {
            "title": "Banregio",
            "value": 15400000,
            "value_formatted": "$15,400,000",
            "status_color": "green",
            "metadata": {
                "type": "currency",
                "unit": "MXN",
                "category": "banking",
                "description": "Saldo en cuenta Banregio"
            },
            "extra_rows": [
                {"label": "% Total Disponibilidad", "value": "100%", "color": "dimmed"},
                {"label": "Línea Crédito", "value": "$10,000,000", "color": "blue"},
                {"label": "Uso", "value": "85%", "color": "orange"}
            ]
        }
        
        administration["charts"]["monthly_billing_comparison"] = {
            "type": "line_chart",
            "title": "Facturación Mensual 2025 vs 2024",
            "description": "Comparativa en millones de pesos",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [46.6, 37.3, 103.2, 41.4, 222.9, 117.0, 39.5, 36.3, 40.1, 32.1, 27.2, 25.7],
                        "color": "#2E86AB"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [29.4, 0, 62.9, 31.6, 23.0, 33.0, 0, 0, 0, 0, 0, 0],
                        "color": "#A3BAC3"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        administration["charts"]["portfolio_distribution"] = {
            "type": "donut_chart",
            "title": "Distribución de Cartera",
            "description": "Estado de la cartera: $171,710,807 MXN",
            "data": {
                "labels": ["SIN CARTA COBRO", "POR VENCER", "VENCIDO"],
                "values": [97185032, 44168641, 30357134],
                "colors": ["#7BC950", "#FFD166", "#EF476F"],
                "percentages": [56.6, 25.7, 17.7],
                "total_formatted": "$171.7M"
            }
        }
        
        administration["charts"]["portfolio_by_client"] = {
            "type": "bar_chart",
            "chart_type": "stacked",
            "title": "Cartera por Cliente",
            "description": "Desglose por cliente y estatus",
            "data": {
                "categories": ["MATERIAS PRIMA", "OWENS AMERICA", "VIDRIO PLANO", "PETROLEOS MEX", "VITRO VIDRIO"],
                "series": [
                    {
                        "name": "SIN CARTA COBRO",
                        "data": [0, 11, 0, 0, 0],
                        "color": "#7BC950"
                    },
                    {
                        "name": "POR VENCER",
                        "data": [73, 13, 11, 15, 12],
                        "color": "#FFD166"
                    },
                    {
                        "name": "VENCIDO",
                        "data": [77, 34, 23, 0, 0],
                        "color": "#EF476F"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Clientes"
            }
        }
        
        administration["charts"]["monthly_ap_comparison"] = {
            "type": "line_chart",
            "title": "Cuentas por Pagar Mensual 2025 vs 2024",
            "description": "Promedio días de pago",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [26, 25, 19, 19, 21, 21, 20, 20, 16, 17, 13, 28],
                        "color": "#EF476F"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [17, 15, 14, 17, 18, 15, 13, 14, 15, 13, 14, 13],
                        "color": "#A3BAC3"
                    }
                ],
                "y_axis_label": "Días Promedio",
                "x_axis_label": "Meses"
            }
        }
        
        administration["charts"]["balance_by_supplier"] = {
            "type": "bar_chart",
            "chart_type": "stacked",
            "title": "Saldo por Proveedor",
            "description": "Desglose por proveedor y estatus",
            "data": {
                "categories": ["NEWYO GAS", "INFORMATICA UG", "LLANTAS Y REFAC", "TRACTO REFACCI", "TRACTO IMPORTA"],
                "series": [
                    {
                        "name": "POR VENCER",
                        "data": [0.70, 0.69, 0.41, 0.11, 0.15],
                        "color": "#FFD166"
                    },
                    {
                        "name": "VENCIDO",
                        "data": [0.30, 0.31, 0.0, 0.0, 0.0],
                        "color": "#EF476F"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Proveedores"
            }
        }
        
        administration["charts"]["daily_bank_flow"] = {
            "type": "area_chart",
            "title": "Flujo Diario Bancario - Septiembre",
            "description": "Ingresos vs Egresos diarios",
            "data": {
                "days": list(range(1, 31)),
                "series": [
                    {
                        "name": "Ingresos",
                        "data": [10, 11, 12, 11, 10, 8, 9, 11, 12, 13, 14, 28, 15, 14, 13, 12, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22, 24, 26, 28, 30],
                        "color": "#06D6A0",
                        "fill": True
                    },
                    {
                        "name": "Egresos",
                        "data": [9, 10, 11, 10, 9, 2, 5, 8, 9, 10, 11, 25, 12, 11, 10, 9, 8, 9, 10, 11, 23, 12, 11, 10, 9, 10, 11, 12, 13, 14],
                        "color": "#EF476F",
                        "fill": True
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Días del Mes"
            }
        }
        
        administration["charts"]["billing_summary"] = {
            "type": "table",
            "title": "Resumen Facturación y Cobranza",
            "headers": ["Concepto", "Acumulado", "Mes Actual", "Variación"],
            "rows": [
                ["Facturado Total", "$194,047,842", "$32,437,705", "+15.2%"],
                ["Cobrado Total", "$22,127,664", "$18,193,148", "-5.0%"],
                ["Cartera Clientes", "$171,710,807", "-", "+4.1%"],
                ["Notas Crédito", "$209,371", "$52,579", "-12.3%"],
                ["Notas Cargo", "$0", "$0", "0.0%"]
            ]
        }
        
        administration["charts"]["ap_summary"] = {
            "type": "table",
            "title": "Resumen Cuentas por Pagar",
            "headers": ["Concepto", "Monto", "Meta", "Desviación"],
            "rows": [
                ["Saldo Inicial", "$1,000,000", "$800,000", "+25.0%"],
                ["CxP Generado", "$15,000,000", "$14,000,000", "+7.1%"],
                ["Pagos Realizados", "$14,000,000", "$13,000,000", "+7.7%"],
                ["Saldo Actual", "$3,000,000", "$2,500,000", "+20.0%"],
                ["Días Promedio Pago", "22 días", "30 días", "-26.7%"]
            ]
        }
        
        administration["charts"]["bank_distribution"] = {
            "type": "donut_chart",
            "title": "Distribución por Institución Bancaria",
            "description": "Saldo final consolidado",
            "data": {
                "labels": ["BANREGIO"],
                "values": [15400000],
                "colors": ["#118AB2"],
                "percentages": [100.0],
                "total_formatted": "$15.4M"
            }
        }
        
        administration["charts"]["aging_portfolio"] = {
            "type": "table",
            "title": "Antigüedad de Saldos - Cartera de Clientes",
            "headers": ["Cliente", "SIN CARTA COBRO", "POR VENCER", "1-30 Días", "31-60 Días", "61-90 Días", "+90 Días", "Total"],
            "rows": [
                ["MATERIAS PRIMA", "$0", "$73M", "$530,764", "$1,023,308", "$1,513,372", "$15,430,407", "$91M"],
                ["OWENS AMERICA", "$11M", "$13M", "$0", "$0", "$0", "$0", "$24M"],
                ["VIDRIO PLANO", "$0", "$11M", "$0", "$0", "$0", "$23M", "$34M"],
                ["PETROLEOS MEX", "$0", "$15M", "$0", "$0", "$0", "$0", "$15M"],
                ["VITRO VIDRIO", "$0", "$12M", "$0", "$0", "$0", "$0", "$12M"]
            ],
            "total_row": ["TOTAL", "$11M", "$124M", "$531K", "$1,023K", "$1,513K", "$39M", "$176M"],
            "color_coding": {
                "1-30 Días": "yellow",
                "31-60 Días": "orange", 
                "61-90 Días": "red",
                "+90 Días": "dark_red"
            }
        }

        administration["charts"]["aging_payables"] = {
            "type": "table",
            "title": "Antigüedad de Saldos - Cuentas por Pagar",
            "headers": ["Proveedor", "POR VENCER", "1-30 Días", "31-60 Días", "61-90 Días", "+90 Días", "Total"],
            "rows": [
                ["NEWYO GAS", "$700K", "$28,243", "$58,899", "$9,427", "$263,631", "$1,060K"],
                ["INFORMATICA UG", "$690K", "$0", "$0", "$0", "$214,224", "$904K"],
                ["LLANTAS Y REFAC", "$410K", "$0", "$0", "$1,950", "$0", "$412K"],
                ["TRACTO REFACCI", "$110K", "$0", "$0", "$0", "$0", "$110K"],
                ["TRACTO IMPORTA", "$150K", "$0", "$0", "$0", "$0", "$150K"]
            ],
            "total_row": ["TOTAL", "$2,060K", "$28K", "$59K", "$11K", "$478K", "$2,636K"]
        }

        administration["charts"]["invoice_month_detail"] = {
            "type": "table",
            "title": "Detalle Facturas del Mes",
            "headers": ["Factura", "Fecha", "Cliente", "RFC", "Subtotal", "IVA", "Total", "Estatus"],
            "rows": [
                ["FMC-4459", "12/08/2025", "MATERIAS PRIMAS MONTERREY", "MPM250605123", "$11,224", "$1,796", "$13,020", "COBRADA"],
                ["FMC-4460", "13/08/2025", "OWENS AMERICA", "OAI800101A34", "$24,364", "$3,898", "$28,262", "PENDIENTE"],
                ["FMC-4461", "14/08/2025", "VITRO VIDRIO", "VVI750210A56", "$13,068", "$2,091", "$15,159", "COBRADA"],
                ["FMC-4462", "15/08/2025", "PETROLEOS MEX", "PEM681022B78", "$18,796", "$3,007", "$21,803", "PENDIENTE"],
                ["FMC-4463", "16/08/2025", "CEMEX", "CEM850304C90", "$15,551", "$2,488", "$18,039", "COBRADA"]
            ],
            "summary": {
                "total_invoices": 120,
                "total_subtotal": "$27,448,278",
                "total_iva": "$4,391,724",
                "total_amount": "$31,840,002",
                "collected": "$18,193,148",
                "pending": "$13,646,854"
            }
        }

        administration["charts"]["bank_movements_by_concept"] = {
            "type": "table",
            "title": "Ingresos y Egresos Por Concepto",
            "headers": ["Concepto", "Ingresos", "Egresos", "Neto"],
            "rows": [
                ["DEPÓSITOS CLIENTES", "$18,193,148", "$0", "+$18,193,148"],
                ["PAGO A PROVEEDORES", "$0", "$2,973,856", "-$2,973,856"],
                ["NÓMINA EMPLEADOS", "$0", "$1,039,662", "-$1,039,662"],
                ["GASTOS OPERADORES", "$0", "$1,046,528", "-$1,046,528"],
                ["IMPUESTOS FEDERALES", "$0", "$1,015,117", "-$1,015,117"],
                ["COMISIONES BANCARIAS", "$0", "$1,804", "-$1,804"],
                ["OTROS INGRESOS", "$39,707", "$0", "+$39,707"]
            ],
            "total_row": ["TOTAL", "$18,232,855", "$6,076,967", "+$12,155,888"]
        }

        administration["charts"]["payments_detail"] = {
            "type": "table",
            "title": "Detalle de Pagos del Mes",
            "headers": ["Fecha", "Proveedor", "Concepto", "Referencia", "Monto", "Método Pago"],
            "rows": [
                ["01/09/2025", "NEWYO GAS", "COMBUSTIBLE SEPTIEMBRE", "PAGO-789012", "$1,250,000", "TRANSFERENCIA"],
                ["05/09/2025", "INFORMATICA UG", "LICENCIAMIENTO SOFTWARE", "PAGO-789013", "$85,000", "TRANSFERENCIA"],
                ["10/09/2025", "LLANTAS Y REFAC", "LLANTAS UNIDAD 118", "PAGO-789014", "$127,992", "CHEQUE"],
                ["15/09/2025", "TRACTOCAMIONES KENWORTH", "REFACCIONES MOTOR", "PAGO-789015", "$204,437", "TRANSFERENCIA"],
                ["20/09/2025", "TRACTO REFACCIONES ALLENDE", "REFACCIONES FRENOS", "PAGO-789016", "$167,192", "TRANSFERENCIA"]
            ],
            "summary": {
                "total_payments": 45,
                "total_amount": "$14,000,000",
                "transfers": 32,
                "checks": 13
            }
        }

        return data
   
    def _inject_workshop_data(self, data):
        workshop = data["workshop"]["dashboard"]
        
        workshop["kpis"]["internal_cost"] = KPICalculator.calculate_kpi(
            title="Costo Taller Interno",
            current_value=603880,
            previous_value=560000,
            target_value=371948,
            current_ytd_value=2900000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["external_cost"] = KPICalculator.calculate_kpi(
            title="Costo Taller Externo",
            current_value=197773,
            previous_value=232000,
            target_value=581033,
            current_ytd_value=5300000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["tire_cost"] = KPICalculator.calculate_kpi(
            title="Costo Llantas",
            current_value=18510,
            previous_value=17600,
            target_value=15000,
            current_ytd_value=941000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["total_maintenance_cost"] = KPICalculator.calculate_kpi(
            title="Costo Total workshop",
            current_value=820164,
            previous_value=920000,
            target_value=952982,
            current_ytd_value=9200000,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["cost_per_km"] = KPICalculator.calculate_kpi(
            title="Costo por Km",
            current_value=1.32,
            previous_value=1.31,
            target_value=1.10,
            current_ytd_value=0.59,
            kpi_type="currency",
            unit="MXN/km",
            inverse=True
        )
        
        workshop["kpis"]["units_availability"] = KPICalculator.calculate_kpi(
            title="Disponibilidad Unidades",
            current_value=0.58,
            previous_value=0.68,
            target_value=1.00,
            kpi_type="percent",
            inverse=False
        )
        
        workshop["kpis"]["inventory_valuation"] = KPICalculator.calculate_kpi(
            title="Valorización Inventario",
            current_value=21111205,
            previous_value=30100000,
            target_value=30384198,
            kpi_type="currency",
            unit="MXN",
            inverse=False
        )
        
        workshop["kpis"]["inventory_compliance"] = KPICalculator.calculate_kpi(
            title="Cumplimiento Inventario",
            current_value=47.32,
            previous_value=50.0,
            target_value=100.0,
            kpi_type="percent",
            inverse=False
        )
        
        workshop["kpis"]["total_purchases"] = KPICalculator.calculate_kpi(
            title="Total Compras",
            current_value=5648478,
            previous_value=6885581,
            target_value=6000000,
            current_ytd_value=37665913,
            kpi_type="currency",
            unit="MXN",
            inverse=True
        )
        
        workshop["kpis"]["workshop_entries"] = {
            "title": "Entradas a Taller",
            "value": 335,
            "value_formatted": "335",
            "status_color": "orange",
            "trend_direction": "up",
            "trend_percentage": 5.0,
            "trend_formatted": "+5.0%",
            "metadata": {
                "type": "number",
                "unit": "entradas",
                "category": "workshop",
                "description": "Entradas a taller mensuales"
            },
            "extra_rows": [
                {"label": "Meta Mensual", "value": "300", "color": "dimmed"},
                {"label": "% Cumplimiento", "value": "111.6%", "color": "orange"},
                {"label": "Promedio x Unidad", "value": "4.1", "color": "blue"}
            ]
        }
        
        workshop["charts"]["maintenance_cost_trend"] = {
            "type": "line_chart",
            "title": "Costo Total workshop 2025 vs 2024",
            "description": "Comparativa mensual en millones de pesos",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 0.82, 1.0, 1.0, 1.0],
                        "color": "#EF476F"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [1.0, 2.0, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0],
                        "color": "#A3BAC3"
                    },
                    {
                        "name": "Meta 2025",
                        "data": [1.5, 1.2, 0.8, 1.8, 2.0, 1.5, 0.8, 1.1, 0.9, 1.6, 1.3, 1.4],
                        "color": "#06D6A0",
                        "dashed": True
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        workshop["charts"]["maintenance_cost_distribution"] = {
            "type": "donut_chart",
            "title": "Distribución de Costos de workshop",
            "description": "Total: $820,164 MXN",
            "data": {
                "labels": ["Taller Interno", "Taller Externo", "Llantas"],
                "values": [603880, 197773, 18510],
                "colors": ["#EF476F", "#FFD166", "#118AB2"],
                "percentages": [73.6, 24.1, 2.3],
                "total_formatted": "$820,164"
            }
        }
        
        workshop["charts"]["corrective_preventive"] = {
            "type": "bar_chart",
            "title": "workshop Correctivo vs Preventivo",
            "description": "Distribución por tipo de workshop",
            "data": {
                "categories": ["CORRECTIVO", "PREVENTIVO"],
                "series": [
                    {
                        "name": "Costo",
                        "data": [778.167, 41.997],
                        "color": "#EF476F"
                    }
                ],
                "y_axis_label": "Miles MXN",
                "x_axis_label": "Tipo de workshop"
            }
        }
        
        workshop["charts"]["costs_by_family"] = {
            "type": "horizontal_bar_chart",
            "title": "Costos por Familia de Reparación",
            "description": "Desglose por categoría técnica",
            "data": {
                "categories": ["MOTOR", "SISTEMA DE FRENOS", "REMOLQUES", "GENERAL", "SUSPENSION"],
                "series": [
                    {
                        "name": "Costo",
                        "data": [129.253, 111.333, 99.437, 80.982, 65.210],
                        "color": "#118AB2"
                    }
                ],
                "x_axis_label": "Miles MXN",
                "y_axis_label": "Familia"
            }
        }
        
        workshop["charts"]["monthly_availability"] = {
            "type": "line_chart",
            "title": "% Disponibilidad Mensual 2025 vs 2024",
            "description": "Porcentaje de unidades disponibles",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [70, 71, 62, 63, 59, 58, 50, 49, 37, 37, 29, 27],
                        "color": "#06D6A0"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [78, 69, 73, 64, 59, 52, 48, 50, 46, 43, 55, 0],
                        "color": "#A3BAC3"
                    },
                    {
                        "name": "Meta",
                        "data": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
                        "color": "#EF476F",
                        "dashed": True
                    }
                ],
                "y_axis_label": "% Disponibilidad",
                "x_axis_label": "Meses"
            }
        }
        
        workshop["charts"]["entries_vs_kilometers"] = {
            "type": "scatter_chart",
            "title": "Entradas a Taller vs Kilómetros Recorridos",
            "description": "Relación entre uso y workshop por unidad",
            "data": {
                "points": [
                    {"x": 14640, "y": 9, "label": "U-118", "color": "#EF476F", "size": 12},
                    {"x": 8561, "y": 7, "label": "U-106", "color": "#FFD166", "size": 10},
                    {"x": 7195, "y": 7, "label": "U-21", "color": "#06D6A0", "size": 10},
                    {"x": 7698, "y": 6, "label": "U-60", "color": "#118AB2", "size": 9},
                    {"x": 5400, "y": 8, "label": "U-46", "color": "#7209B7", "size": 11},
                    {"x": 3200, "y": 5, "label": "U-09", "color": "#073B4C", "size": 8}
                ],
                "x_axis_label": "Kilómetros Recorridos",
                "y_axis_label": "Entradas a Taller",
                "trend_line": True
            }
        }
        
        workshop["charts"]["monthly_purchases"] = {
            "type": "line_chart",
            "title": "Compras Mensuales 2025 vs 2024",
            "description": "Total compras en millones de pesos",
            "data": {
                "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "series": [
                    {
                        "name": "2025 (Actual)",
                        "data": [3.37, 5.67, 4.21, 4.71, 4.37, 5.85, 5.64, 6.29, 5.20, 7.40, 4.30, 5.71],
                        "color": "#118AB2"
                    },
                    {
                        "name": "2024 (Anterior)",
                        "data": [5.51, 0, 6.88, 8.53, 7.27, 0, 6.88, 0, 6.61, 0, 7.01, 0],
                        "color": "#A3BAC3"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Meses"
            }
        }
        
        workshop["charts"]["purchases_by_type"] = {
            "type": "donut_chart",
            "title": "Compras por Tipo",
            "description": "Distribución del total: $5,648,478 MXN",
            "data": {
                "labels": ["DIESEL", "REFACCIONES", "LLANTAS"],
                "values": [3923274, 1242447, 329592],
                "colors": ["#EF476F", "#FFD166", "#118AB2"],
                "percentages": [69.5, 22.0, 5.8],
                "total_formatted": "$5.65M"
            }
        }
        
        workshop["charts"]["inventory_by_area"] = {
            "type": "horizontal_bar_chart",
            "title": "Valorización de Inventario por Área",
            "description": "Valor actual por ubicación",
            "data": {
                "categories": ["01-TINSA", "02-TINSA CAD", "03-MTY MULTIF", "04-MUL CAD", "05-GRANEL"],
                "series": [
                    {
                        "name": "Valor Actual",
                        "data": [9.77, 7.46, 1.97, 1.06, 0.86],
                        "color": "#06D6A0"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Área"
            }
        }
        
        workshop["charts"]["availability_detail"] = {
            "type": "table",
            "title": "Detalle de Disponibilidad por Área",
            "headers": ["Área / Unidad", "Días Mes", "Días Taller", "Días Disp.", "Disponibilidad"],
            "rows": [
                ["SIN ASIGNAR", "4991", "2083", "2908", "58%"],
                ["CADEREYTA MULTIFLET", "93", "37", "56", "60%"],
                ["M07", "31", "14", "17", "55%"],
                ["VMR25", "31", "1", "30", "97%"],
                ["CADEREYTA TINSA", "1922", "837", "1085", "56%"],
                ["TOTAL GENERAL", "4991", "2083", "2908", "58%"]
            ]
        }
        
        workshop["kpis"]["total_purchases"] = KPICalculator.calculate_kpi(
            title="Compras Total",
            current_value=5648478,
            previous_value=6885581,
            target_value=6000000,
            current_ytd_value=37665913,
            kpi_type="currency",
            unit="MXN"
        )

        workshop["kpis"]["fuel_purchases"] = {
            "title": "Combustible",
            "value": 3923274,
            "value_formatted": "$3,923,274",
            "percentage_of_total": 69.46
        }

        workshop["kpis"]["parts_purchases"] = {
            "title": "Refacciones",
            "value": 1242447,
            "value_formatted": "$1,242,447",
            "percentage_of_total": 22.0
        }

        workshop["kpis"]["tire_purchases"] = {
            "title": "Llantas",
            "value": 329592,
            "value_formatted": "$329,592",
            "percentage_of_total": 5.84
        }

        workshop["kpis"]["initial_inventory"] = {
            "title": "Inventario Inicial",
            "value": 12926174,
            "value_formatted": "$12,926,174",
            "type": "currency",
            "unit": "MXN"
        }

        workshop["kpis"]["current_valuation"] = KPICalculator.calculate_kpi(
            title="Valorización Actual",
            current_value=21111205,
            previous_value=30384198,
            target_value=30384198,
            kpi_type="currency",
            unit="MXN"
        )

        workshop["kpis"]["compliance_level"] = {
            "title": "Nivel Cumplimiento",
            "value": 47.32,
            "value_formatted": "47.32%",
            "type": "percent",
            "status": "warning"
        }

        workshop["charts"]["purchases_by_area"] = {
            "type": "horizontal_bar_chart",
            "title": "Total Compra por Área",
            "description": "Distribución de compras por ubicación",
            "data": {
                "categories": ["MTY TINSA", "CADEREYTA TINSA", "EL CARMEN GRANEL", "CADEREYTA MULTIFLET", "MTY MULTIFLET"],
                "series": [
                    {
                        "name": "Compras",
                        "data": [3.8, 0.6, 0.6, 0.6, 0.1],
                        "color": "#06D6A0"
                    }
                ],
                "x_axis_label": "Millones MXN",
                "y_axis_label": "Área"
            }
        }

        workshop["charts"]["top_suppliers_chart"] = {
            "type": "bar_chart",
            "title": "Top 10 Proveedores",
            "description": "Principales proveedores por monto de compras",
            "data": {
                "categories": ["NEWYO GAS", "TECNOCAM", "TRACTOCAMIONES KENWORTH", "TRACTO REFACCI", "IM MOTRIZ", "LLANTAS Y REFAC", "ACCESORIOS ALLENDE", "PROVEEDORA DE LONAS", "CR3 SUPPLY", "TRACTO IMPORTACIONES"],
                "series": [
                    {
                        "name": "Monto",
                        "data": [3.92, 0.26, 0.20, 0.17, 0.15, 0.13, 0.07, 0.06, 0.06, 0.05],
                        "color": "#118AB2"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Proveedores"
            }
        }

        workshop["charts"]["valuation_by_area"] = {
            "type": "bar_chart",
            "title": "Valorización Actual por Área",
            "description": "Distribución del inventario por ubicación",
            "data": {
                "categories": ["01-TINSA", "02-TINSA CAD", "03-MTY MULTIF", "04-MUL CAD", "05-GRANEL"],
                "series": [
                    {
                        "name": "Valor Actual",
                        "data": [9.77, 7.46, 1.97, 1.06, 0.86],
                        "color": "#118AB2"
                    }
                ],
                "y_axis_label": "Millones MXN",
                "x_axis_label": "Área"
            }
        }

        workshop["charts"]["maintenance_costs_by_unit"] = {
            "type": "table",
            "title": "Detalle Gastos x Unidad",
            "headers": ["Unidad", "Costo Interno", "Costo Externo", "Costo Llantas", "Costo Total", "Entradas Taller"],
            "rows": [
                ["02", "$6,971", "$0", "$225", "$7,196", "3"],
                ["03", "$3,850", "$0", "$9,270", "$13,120", "2"],
                ["106", "$17,132", "$16,391", "$0", "$33,523", "7"],
                ["118", "$45,280", "$28,450", "$3,150", "$76,880", "9"],
                ["21", "$12,850", "$8,920", "$1,980", "$23,750", "5"]
            ],
            "total_row": ["TOTAL", "$603,880", "$197,773", "$18,510", "$820,164", "335"]
        }

        workshop["charts"]["service_orders_detail"] = {
            "type": "table",
            "title": "Detalle Órdenes de Servicio",
            "headers": ["Orden", "Unidad", "Tipo Reparación", "Razón", "Costo Total", "Fecha Cierre", "Status"],
            "rows": [
                ["2307", "03", "CORRECTIVO", "CORRECTIVO TRACTOCAMION", "$9,266", "22/07/2025", "CERRADA"],
                ["2300", "07", "CORRECTIVO", "CORRECTIVO TRACTOCAMION", "$10,351", "21/07/2025", "CERRADA"],
                ["2299", "21", "PREVENTIVO", "workshop PREVENTIVO", "$3,850", "20/07/2025", "CERRADA"],
                ["2298", "118", "CORRECTIVO", "REPARACIÓN MOTOR", "$15,280", "19/07/2025", "CERRADA"],
                ["2297", "106", "CORRECTIVO", "REPARACIÓN FRENOS", "$8,920", "18/07/2025", "CERRADA"]
            ],
            "summary": {
                "total_orders": 339,
                "total_corrective": 278,
                "total_preventive": 61,
                "total_amount": "$820,164",
                "closed": 327,
                "open": 12
            }
        }
        
        workshop["charts"]["valuation_by_family"] = {
            "type": "table",
            "title": "Valorización por Familia",
            "headers": ["Familia", "Valorización", "% Total", "Cantidad Items", "Estado"],
            "rows": [
                ["LLANTAS Y RINES", "$5,368,019", "25.43%", "5,651", "OK"],
                ["DIESEL", "$3,171,020", "15.02%", "31,791,503", "OK"],
                ["GENERAL", "$3,069,709", "14.54%", "149,811", "OK"],
                ["MOTOR", "$2,567,111", "12.16%", "11,762", "OK"],
                ["SUSPENSION", "$1,277,804", "6.05%", "2,383", "OK"]
            ],
            "total_row": ["TOTAL", "$21,111,205", "100.00%", "31,979,669", ""]
        }

        workshop["charts"]["open_orders"] = {
            "type": "table",
            "title": "Órdenes No Cerradas",
            "headers": ["Orden", "Unidad", "Tipo Reparación", "Fecha Inicio", "Días Abierta", "Responsable"],
            "rows": [
                ["104", "118", "CORRECTIVO", "29/05/2024", "250", "TÉCNICO 1"],
                ["406", "M-32", "PREVENTIVO", "26/12/2025", "10", "TÉCNICO 2"],
                ["407", "U-21", "CORRECTIVO", "15/01/2025", "8", "TÉCNICO 3"],
                ["408", "U-60", "CORRECTIVO", "20/01/2025", "3", "TÉCNICO 1"],
                ["409", "U-46", "PREVENTIVO", "22/01/2025", "1", "TÉCNICO 2"]
            ],
            "summary": {
                "total_open": 12,
                "avg_days_open": 45,
                "corrective": 9,
                "preventive": 3
            }
        }

        return data