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
            "operaciones": { "dashboard": { "kpis": {}, "charts": {}, "tables": {} } },
            "administracion": { "dashboard": { "kpis": {}, "charts": {} } },
            "mantenimiento": { "dashboard": { "kpis": {}, "charts": {} } }
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
        
        return data
    
    def _inject_operational_data(self, data):
        operational = data["operaciones"]["dashboard"]
        
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
        
        return data
    
    def _inject_administration_data(self, data):
        administration = data["administracion"]["dashboard"]
        
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
        
        return data
   
    def _inject_workshop_data(self, data):
        workshop = data["mantenimiento"]["dashboard"]
        
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
            title="Costo Total Mantenimiento",
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
            "title": "Costo Total Mantenimiento 2025 vs 2024",
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
            "title": "Distribución de Costos de Mantenimiento",
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
            "title": "Mantenimiento Correctivo vs Preventivo",
            "description": "Distribución por tipo de mantenimiento",
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
                "x_axis_label": "Tipo de Mantenimiento"
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
            "description": "Relación entre uso y mantenimiento por unidad",
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
        
        return data