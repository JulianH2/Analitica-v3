class RealDataService:
    def get_full_dashboard_data(self):
        data = self.get_base_structure()

        # MOCK TEMPORAL (solo para demo / desarrollo)
        self._inject_operational_data(data)
        self._inject_financial_data(data)
        self._inject_maintenance_data(data)

        return data


    
    def get_base_structure(self):
        return {
            "operational": {
                "dashboard": {
                    "kpis": {},
                    "charts": {}
                }
            },
            "financial": {
                "dashboard": {
                    "kpis": {}
                }
            },
            "maintenance": {
                "dashboard": {
                    "kpis": {}
                }
            }
        }

    def _inject_operational_data(self, data):
        operational = data["operational"]["dashboard"]
        operational["kpis"]["trip_revenue"] = {
            "value": 1,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        operational["kpis"]["trips"] = {
            "value": 1,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        operational["kpis"]["kilometers"] = {
            "value": 1,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        operational["kpis"]["utilization"] = {
            "value": 0
        }
        operational["kpis"]["average_trip_revenue"] = {
            "value": 1,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        operational["kpis"]["average_unit_revenue"] = {
            "value": 1,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        operational["kpis"]["units_used"] = {
            "value": 1,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        operational["kpis"]["customers_served"] = {
            "value": 1,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        operational["kpis"]["km_per_liter"] = {
            "value": 1.86,
            "target": 3.0,
            "delta": 0.0427,
            "ytd": -0.94
        }
        operational["kpis"]["real_kilometers"] = {
            "value": 513165,
            "target": 592357,
            "delta": -0.11,
            "ytd": -0.21
        }
        operational["kpis"]["liters"] = {
            "value": 275490,
            "target": 300000,
            "delta": -0.15,
            "ytd": 0.20
        }
        operational["kpis"]["trip_profit"] = {
            "value": 18.19,
            "target": 25.0,
            "delta": -0.68,
            "ytd": -0.43
        }
        operational["kpis"]["total_cost"] = {
            "value": 17098160,
            "target": 9796576,
            "delta": 0.71,
            "ytd": 0.18
        }
        operational["charts"]["annual_revenue"] = {
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "actual": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "previous": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "target": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        operational["charts"]["annual_trips"] = {
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "actual": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "previous": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        operational["charts"]["operation_mix"] = {
            "labels": ["", "", "", ""],
            "values": [0, 0, 0, 0]
        }
        operational["charts"]["unit_balancing"] = {
            "labels": ["", "", "", "", ""],
            "values": [0, 0, 0, 0, 0]
        }
        operational["charts"]["trend"] = {
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "actual": [1.85, 1.82, 1.82, 1.81, 1.74, 1.70, 1.79, 1.78, 1.86, 1.82, 1.83, 1.86],
            "previous": [4.46, 1.99, 1.82, 1.87, 1.84, 1.79, 1.90, 1.94, 1.79, 1.88, 1.91, 1.93]
        }
        operational["charts"]["operation_mix_rend"] = {
            "labels": ["ARENERA LOCAL", "CONTENEDOR FORÁNEO", "PLANA LOCAL", "CONTENEDOR LOCAL", "OTROS"],
            "values": [15.12, 14.45, 13.29, 12.6, 44.54]
        }
        operational["charts"]["monthly_profit"] = {
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "cost": [11, 11, 13, 10, 11, 28, 22, 17, 11, 10, 11, 9],
            "profit_pct": [51.33, 53.36, 53.65, 0, 52.80, 69.52, 0, 0, 0, 50.25, 53.61, 57.92]
        }
        operational["charts"]["cost_breakdown"] = {
            "concepts": ["Combustible", "Percepción Operador", "Sueldo", "Otros", "Estancias"],
            "amounts": [13940407, 3055793, 2269771, 2139090, 648771]
        }
        operational["charts"]["cost_comparison"] = {
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "actual": [11, 10, 12, 12, 11, 28, 12, 12, 17, 11, 11, 9],
            "previous": [8, 8, 10, 11, 11, 11, 10, 7, 8, 7, 8, 8]
        }
        operational["charts"]["map_points"] = [
            {"lat": 25.68, "lon": -100.31, "name": "Monterrey"},
            {"lat": 19.43, "lon": -99.13, "name": "México DF"}
        ]
        operational["charts"]["loaded_routes_table"] = {
            "headers": ["No.", "Ruta", "Viajes", "Kms", "Costo x Km", "Costo Viaje Total"],
            "rows": [
                ["261", "3T-LYCRA", "1", "29", "$193.01", "$5,597"],
                ["234", "PATIEROS Y GRANEL", "51", "1,785", "$214.10", "$382,173"]
            ]
        }
        operational["charts"]["unit_table"] = {
            "headers": ["Unidad", "Rend. Real", "Viajes"],
            "rows": [["03", "3.35", "8"], ["148", "2.61", "11"], ["94", "2.61", "12"], ["96", "2.55", "9"]]
        }
        operational["charts"]["operator_table"] = {
            "headers": ["Operador", "Rend. Real", "Viajes", "Kms Real", "Litros Total"],
            "rows": [
                ["AGUILAR CAZARES GERARDO", "1.95", "7", "8,530", "4,364"],
                ["AGUILAR YAÑEZ JORGE LUIS", "2.00", "7", "6,967", "3,479"],
                ["ALANIS ALANIS AMBROCIO", "1.76", "9", "3,726", "2,112"]
            ]
        }
        operational["charts"]["route_detail_table"] = {
            "headers": ["No.", "Ruta", "Cliente", "Cargados", "Vacíos", "Kms Total", "Utilización %"],
            "rows": [
                ["1", "MTY-MEX", "COCA COLA", "84", "12", "85,400", "87.5%"],
                ["2", "MEX-GUA", "PEPSI", "76", "15", "54,200", "83.5%"],
                ["3", "GUA-MTY", "LOGISTICA X", "92", "5", "98,206", "94.8%"]
            ]
        }
        operational["charts"]["route_margin_table"] = {
            "headers": ["No.", "Ruta", "Ingreso", "Cant. Viajes", "Combustible", "Sueldo", "Costo Total", "Utilidad"],
            "rows": [
                ["355", "APAXCO-VITRO", "$1,686,423", "29", "$526,937", "$84,000", "$802,703", "$883,720"],
                ["1", "CANOITAS-OWENS", "$3,660,979", "170", "$1,025,036", "$154,960", "$1,680,976", "$1,980,003"],
                ["3", "CANOITAS-VITRO", "$2,250,330", "89", "$571,029", "$84,550", "$889,165", "$1,361,165"]
            ]
        }
        
    def _inject_financial_data(self, data):
        financial = data["financial"]["dashboard"]
        financial.setdefault("charts", {})
        financial["kpis"]["billed_vs_collected"] = {
            "value": 22127664,
            "target": 30000000,
            "delta": -0.05,
            "ytd": 73.7
        }
        financial["kpis"]["average_payment_days"] = {
            "value": 45,
            "target": 30,
            "delta": 0.12,
            "ytd": 150.0
        }
        financial["kpis"]["accounts_payable_vs_paid"] = {
            "value": 14000000,
            "target": 17000000,
            "delta": 0.0,
            "ytd": 82.4
        }
        financial["kpis"]["average_payment_days_payable"] = {
            "value": 22,
            "target": 30,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["total_availability"] = {
            "value": 15400000,
            "target": 20000000,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["credit_line_usage"] = {
            "value": 8500000,
            "target": 10000000,
            "delta": 0.0,
            "ytd": 85.0
        }
        financial["kpis"]["accumulated_billed"] = {
            "value": 194047842,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["accumulated_credit_notes"] = {
            "value": 209371,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["accumulated_debit_notes"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["accumulated_collected"] = {
            "value": 22127664,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["customer_portfolio"] = {
            "value": 171710807,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["monthly_billed"] = {
            "value": 32437705,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["monthly_credit"] = {
            "value": 52579,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["monthly_debit"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["monthly_collected"] = {
            "value": 18193148,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["initial_balance"] = {
            "value": 1000000,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["accounts_payable"] = {
            "value": 15000000,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["debit_notes_payable"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["credit_notes_payable"] = {
            "value": 137000,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["advance_payment"] = {
            "value": 4000,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["total_accounts_payable"] = {
            "value": 17000000,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["supplier_payments"] = {
            "value": 14000000,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["kpis"]["final_balance"] = {
            "value": 3000000,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        financial["charts"]["comparison"] = {
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "actual": [46.6, 37.3, 103.2, 41.4, 222.9, 117.0, 39.5, 36.3, 40.1, 32.1, 27.2, 25.7],
            "previous": [29.4, 0, 62.9, 31.6, 23.0, 33.0, 0, 0, 0, 0, 0, 0]
        }
        financial["charts"]["mix"] = {
            "labels": ['SIN CARTA COBRO', 'POR VENCER', 'VENCIDO'],
            "values": [56.6, 26.03, 17.37]
        }
        financial["charts"]["stack"] = {
            "clients": ["MATERIAS PRIMA", "OWENS AMERICA", "VIDRIO PLANO", "PETROLEOS MEX", "VITRO VIDRIO"],
            "to_expire": [73, 13, 11, 15, 12],
            "without_letter": [0, 11, 0, 0, 0],
            "expired": [77, 34, 23, 0, 0]
        }
        financial["charts"]["aging_table"] = {
            "headers": ["Área", "SIN CARTA", "POR VENCER", "VENCIDO"],
            "rows": [
                ["MATERIAS PRIMA", "0", "73", "77"],
                ["OWENS AMERICA", "11", "13", "34"],
                ["VIDRIO PLANO", "0", "11", "23"],
                ["PETROLEOS MEX", "0", "15", "0"],
                ["VITRO VIDRIO", "0", "12", "0"]
            ]
        }
        financial["charts"]["billing_table"] = {
            "headers": ["Cliente", "Facturado", "Notas Crédito", "Notas Débito", "Cobrado", "Saldo"],
            "rows": [
                ["MATERIAS PRIMA", "73,000,000", "0", "0", "50,000,000", "23,000,000"],
                ["OWENS AMERICA", "45,000,000", "200,000", "0", "30,000,000", "15,000,000"],
                ["VIDRIO PLANO", "38,000,000", "0", "0", "25,000,000", "13,000,000"]
            ]
        }
        financial["charts"]["cash_flow"] = {
            "months": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "inflow": [46.6, 37.3, 103.2, 41.4, 222.9, 117.0, 39.5, 36.3, 40.1, 32.1, 27.2, 25.7],
            "outflow": [29.4, 0, 62.9, 31.6, 23.0, 33.0, 0, 0, 0, 0, 0, 0]
        }
        # 1. Gráfica de Dona: Saldo por Institución
        financial["charts"]["bank_balances"] = {
            "labels": ["BBVA Operativo", "Banamex Nómina", "Santander USD", "Caja Chica"],
            "values": [1500000, 850000, 450000, 50000]
        }

        # 2. Tabla: Desglose por Conceptos
        financial.setdefault("tables", {})
        financial["tables"]["bank_concepts"] = {
            "h": ["Concepto", "Ingresos", "Egresos", "Balance"],
            "r": [
                ["Cobranza Clientes", "$18,500,000", "$0", "$18,500,000"],
                ["Pago Proveedores", "$0", "$12,400,000", "-$12,400,000"],
                ["Nómina", "$0", "$2,100,000", "-$2,100,000"],
                ["Impuestos", "$0", "$850,000", "-$850,000"],
                ["Préstamos", "$1,000,000", "$200,000", "$800,000"]
            ]
        }

        # =========================================================
        # NUEVOS DATOS SIMULADOS PARA CUENTAS POR PAGAR (Admin-Payables)
        # =========================================================

        # 1. Gráfica Comparativa Anual (2025 vs 2024)
        financial["charts"]["payables_comparison"] = {
            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
            "actual": [12.5, 11.8, 13.2, 12.0, 14.5, 13.8, 12.2, 0, 0, 0, 0, 0], # Millones
            "anterior": [10.5, 11.0, 11.5, 11.2, 11.8, 12.0, 12.5, 11.8, 12.2, 12.5, 13.0, 12.8]
        }

        # 2. Dona: Saldo por Clasificación
        financial["charts"]["payables_mix"] = {
            "labels": ["Proveedores MP", "Fletes", "Servicios", "Mantenimiento"],
            "values": [45, 25, 20, 10]
        }

        # 3. Stacked Bar: Saldo por Proveedor (Vigente vs Vencido)
        financial["charts"]["supplier_balance"] = {
            "prov": ["COMBUSTIBLES S.A.", "LLANTAS Y REF.", "SEGUROS MONTERREY", "MANTENIMIENTO EXPRESS", "REFACCIONES DEL NORTE"],
            "por_vencer": [2500000, 1200000, 800000, 450000, 300000], # Vigente
            "vencido": [0, 150000, 0, 50000, 120000] # Vencido
        }

        # 4. Tabla: Antigüedad de Saldos
        financial["tables"]["payables_aging"] = {
            "h": ["Proveedor", "Corriente", "1-30 Días", "31-60 Días", "+60 Días", "Total"],
            "r": [
                ["COMBUSTIBLES S.A.", "$2.5M", "$0", "$0", "$0", "$2.5M"],
                ["LLANTAS Y REF.", "$1.2M", "$150k", "$0", "$0", "$1.35M"],
                ["SEGUROS MONTERREY", "$800k", "$0", "$0", "$0", "$800k"],
                ["MANTENIMIENTO EXPRESS", "$450k", "$50k", "$0", "$0", "$500k"],
                ["REFACCIONES DEL NORTE", "$300k", "$20k", "$100k", "$0", "$420k"]
            ]
        }
    
    def _inject_maintenance_data(self, data):
        # 1. Asegurar que la ruta base existe
        if "maintenance" not in data:
            data["maintenance"] = {}
        
        if "dashboard" not in data["maintenance"]:
            data["maintenance"]["dashboard"] = {}

        # 2. Obtener referencia al nodo dashboard
        # NOTA: En tu código, esta variable se llama 'maintenance' según el traceback
        maintenance = data["maintenance"]["dashboard"]

        # 3. INICIALIZAR LOS CONTENEDORES (Esto es lo que te falta) 
        if "kpis" not in maintenance: maintenance["kpis"] = {}
        if "charts" not in maintenance: maintenance["charts"] = {}  # <--- Esto arregla tu error
        if "tables" not in maintenance: maintenance["tables"] = {}
        maintenance["kpis"]["total_units"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["units_in_service"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["units_in_maintenance"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["units_in_repair"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["units_in_standby"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["maintenance_cost"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["repair_cost"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["preventive_maintenance_compliance"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["corrective_maintenance_incidents"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["mean_time_between_failures"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["mean_time_to_repair"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["fuel_efficiency"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["tire_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["brake_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["engine_oil_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["transmission_oil_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["coolant_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["battery_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["air_filter_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["cabin_filter_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["wiper_blade_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["light_bulb_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["belt_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["hose_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["clutch_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["brake_pad_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["brake_rotor_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["shock_absorber_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["strut_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["wheel_bearing_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["cv_joint_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["exhaust_system_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["catalytic_converter_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["oxygen_sensor_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["mass_airflow_sensor_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["throttle_body_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["fuel_injector_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["fuel_pump_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["ignition_coil_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["spark_plug_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["alternator_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["starter_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["battery_cable_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["fuse_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["relay_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["switch_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["sensor_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["actuator_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["control_module_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["wiring_harness_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["connector_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["ground_strap_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["fuse_box_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["relay_box_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["junction_box_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["terminal_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["crimp_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["solder_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["heat_shrink_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["electrical_tape_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["wire_loom_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["cable_tie_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["grommet_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["bushing_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["mount_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["bracket_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["clip_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["fastener_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["adhesive_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["sealant_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["gasket_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["o_ring_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["seal_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["bearing_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["coupling_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["universal_joint_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["drive_shaft_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["axle_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["differential_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["transfer_case_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        }
        maintenance["kpis"]["transmission_life"] = {
            "value": 0,
            "target": 0,
            "delta": 0.0,
            "ytd": 0.0
        },

        maintenance["kpis"]["internal_labour_cost"] = {"value": 450000, "target": 400000, "delta": 12.5}
        maintenance["kpis"]["external_labour_cost"] = {"value": 320000, "target": 300000, "delta": 6.6}
        maintenance["kpis"]["tire_cost"] = {"value": 180000, "target": 200000, "delta": -10.0}
        maintenance["kpis"]["total_maintenance_cost"] = {"value": 950000, "target": 900000, "delta": 5.5}
        maintenance["kpis"]["availability_pct"] = {"value": 92.5, "target": 95.0, "delta": -2.5}
        maintenance["kpis"]["cost_per_km"] = {"value": 2.45, "target": 2.20, "delta": 11.3}

        maintenance["charts"]["cost_trend_annual"] = {
            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            "anterior": [850, 870, 860, 890, 880, 900],
            "actual": [880, 890, 920, 910, 940, 950]
        }
        maintenance["charts"]["corrective_preventive"] = {"values": [35, 65]} # %
        maintenance["charts"]["cost_by_family"] = {
            "labels": ["Tractos", "Remolques", "Dollys", "Utilitarios"], 
            "values": [550000, 250000, 100000, 50000]
        }
        maintenance["charts"]["cost_by_fleet"] = {
            "labels": ["Flota A", "Flota B", "Flota C"], 
            "values": [400000, 350000, 200000]
        }
        maintenance["charts"]["cost_by_operation"] = {
            "labels": ["Local", "Foráneo", "Patio"], 
            "values": [30, 60, 10]
        }
        maintenance["charts"]["cost_per_km_unit"] = {
            "labels": ["U-101", "U-102", "U-103", "U-104", "U-105"], 
            "values": [3.2, 2.8, 2.5, 2.1, 1.9]
        }
        maintenance["charts"]["cost_per_km_brand"] = {
            "labels": ["Kenworth", "Freightliner", "International"], 
            "values": [2.6, 2.4, 2.3]
        }
        maintenance["charts"]["entries_per_unit"] = {
            "labels": ["U-101", "U-205", "U-304"], 
            "values": [5, 4, 3]
        }

        # --- INVENTARIOS ---
        maintenance["kpis"]["initial_inventory"] = {"value": 2500000}
        maintenance["kpis"]["inventory_entries"] = {"value": 450000}
        maintenance["kpis"]["inventory_exits"] = {"value": 380000}
        maintenance["kpis"]["historical_valuation_kpi"] = {"value": 2570000}
        maintenance["kpis"]["current_inventory_value"] = {"value": 2570000, "target": 2500000}
        
        maintenance["kpis"]["min_max_compliance"] = {"value": 94} # %
        maintenance["kpis"]["registered_skus"] = {"value": 1250}
        maintenance["kpis"]["skus_in_stock"] = {"value": 1100}
        maintenance["kpis"]["skus_out_of_stock"] = {"value": 150}

        maintenance["charts"]["inventory_history"] = {
            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            "anterior": [2.4, 2.45, 2.5, 2.4, 2.35, 2.4],
            "actual": [2.42, 2.48, 2.55, 2.52, 2.58, 2.57] # Millones
        }
        maintenance["charts"]["inventory_by_area"] = {
            "labels": ["Refacciones", "Llantas", "Lubricantes", "Filtros"],
            "values": [1200000, 800000, 400000, 170000]
        }
        maintenance["tables"]["family"] = {
            "h": ["Familia", "Valor", "% Total"],
            "r": [["Motor", "$800k", "31%"], ["Suspensión", "$500k", "19%"], ["Frenos", "$300k", "11%"]]
        }
        maintenance["tables"]["history"] = {
            "h": ["Mes", "Valor Inicial", "Entradas", "Salidas", "Final"],
            "r": [["Junio", "$2.55M", "$400k", "$380k", "$2.57M"]]
        }

        # --- COMPRAS ---
        maintenance["kpis"]["total_purchase"] = {"value": 1200000, "target": 1100000}
        maintenance["kpis"]["diesel_purchase"] = {"value": 800000, "target": 750000}
        maintenance["kpis"]["stock_purchase"] = {"value": 400000, "target": 350000}

        maintenance["charts"]["purchases_trend"] = {
            "meses": ["Ene", "Feb", "Mar", "Abr"],
            "anterior": [1.0, 1.1, 1.05, 1.15],
            "actual": [1.1, 1.15, 1.2, 1.18]
        }
        maintenance["charts"]["purchases_by_area"] = {
            "areas": ["Taller Central", "Patio Norte", "Ruta"],
            "valores": [700000, 300000, 200000]
        }
        maintenance["charts"]["purchases_by_type"] = {
            "labels": ["Crédito", "Contado"], "values": [80, 20]
        }
        maintenance["tables"]["suppliers"] = {
            "h": ["Proveedor", "Monto", "Part."],
            "r": [["Mobil Oil", "$300k", "25%"], ["Llantas Michelin", "$200k", "16%"]]
        }
        maintenance["tables"]["orders"] = {
            "h": ["OC", "Proveedor", "Fecha", "Monto", "Estatus"],
            "r": [["OC-1001", "Mobil", "15-Jul", "$50,000", "Recibido"]]
        }
        maintenance["tables"]["supplies"] = {
            "h": ["Código", "Descripción", "Cant", "Costo Unit"],
            "r": [["ACE-15W40", "Aceite Motor Tambo", "10", "$15,000"]]
        }

        # --- DISPONIBILIDAD ---
        maintenance["kpis"]["workshop_entries_count"] = {"value": 45}
        
        maintenance["charts"]["availability_monthly"] = {
            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            "anterior": [94, 93, 95, 94, 93, 94],
            "actual": [95, 94, 93, 92, 92, 93],
            "target": [95, 95, 95, 95, 95, 95]
        }
        maintenance["charts"]["entries_vs_kms"] = {
            "unidades": ["U-001", "U-002", "U-003", "U-004", "U-005"],
            "entradas": [2, 1, 3, 0, 1],
            "kms": [12000, 15000, 8000, 18000, 14000]
        }
        maintenance["tables"]["availability_detail"] = {
            "h": ["Unidad", "Estatus", "Días Taller", "Falla"],
            "r": [["U-003", "En Reparación", "3", "Motor"], ["U-001", "Mantenimiento", "1", "Preventivo"]]
        }
    