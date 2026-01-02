import pandas as pd

class RealDataService:
    def __init__(self):
        self.meses_labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    def get_full_dashboard_data(self):
        return {
            "main_dashboard": {
                "fecha": {"año": 2025, "mes": "noviembre"},
                "indicadores_principales": {
                    "ingresos_por_viajes": {"valor": 20946909, "meta": 19599920, "vs_2024": 17888058, "ytd": 236403764},
                    "costos_por_viajes": {"valor": 9716281, "meta": 7711638, "vs_2024": 8009507, "ytd": 131046917},
                    "margen_por_viaje": {"valor": 53.61, "meta": 11888282, "vs_2024": 9878551, "ytd": 105356847}
                },
                "metricas_operativas": {
                    "viajes": {"valor": 671, "meta": 848, "vs_2024": 773, "ytd": 8523},
                    "unidades_utilizadas": {"valor": 82, "vs_2024": 99},
                    "clientes_servidos": {"valor": 13, "vs_2024": 12},
                    "costo_viaje_km": 21.39,
                    "costo_mtto_km": 0.93
                },
                "mantenimiento": {
                    "total": {"valor": 818932, "meta": 1447628},
                    "taller_interno": 564513,
                    "taller_externo": 254419,
                    "costo_llantas": 0
                },
                "rendimiento": {
                    "rendimiento_kms_lts": 1.91,
                    "kilometros": 509537,
                    "litros_total": 266159,
                    "estado_carga": 93
                },
                "resumenes": {
                    "bancos_mn": {
                        "saldo": 18933620,
                        "saldo_inicial": 18076634,
                        "ingresos": 472111604,
                        "egresos": 471254617
                    },
                    "disponibilidad_unidades": 28.88,
                    "cartera_clientes_mn": {
                        "total": 32658208,
                        "composicion": {"por_vencer": 20.8, "sin_carta_cobro": 33.38, "vencido": 45.83}
                    },
                    "saldo_proveedores_mn": {
                        "total": 926023,
                        "composicion": {"por_vencer": 65.62, "vencido": 34.38}
                    }
                }
            },
            "administracion": {
                "facturacion_cobranza": {
                    "filtros": {"año": 2025, "mes": "09-Sep"},
                    "indicadores_clave": {"facturado_vs_cobrado": 22127664, "prom_dias_cartera": 105},
                    "acumulado": {
                        "facturado": 194047842,
                        "notas_credito": 209371,
                        "notas_cargo": 0,
                        "cobrado": 22127664,
                        "cartera_clientes": 171710807
                    },
                    "mensual": {
                        "facturado": 32437705,
                        "credito": 52579,
                        "cargo": 0,
                        "cobrado": 18193148
                    },
                    "cartera_clasificacion": {
                        "total": 171710807,
                        "sin_carta_cobro": 56.6,
                        "por_vencer": 26.03,
                        "vencido": 17.37
                    },
                    "cartera_cliente": [
                        {"cliente": "MATERIAS PRIMA...", "por_vencer": 73000000, "sin_carta_cobro": 0, "vencido": 77000000},
                        {"cliente": "OWENS AMERICA", "por_vencer": 13000000, "sin_carta_cobro": 11000000, "vencido": 34000000},
                        {"cliente": "VIDRIO PLANO D...", "por_vencer": 11000000, "sin_carta_cobro": 0, "vencido": 23000000},
                        {"cliente": "PETROLEOS MEXI...", "por_vencer": 15000000, "sin_carta_cobro": 0, "vencido": 0},
                        {"cliente": "VITRO VIDRIO AU...", "por_vencer": 12000000, "sin_carta_cobro": 0, "vencido": 0},
                        {"cliente": "INDUSTRIA DEL A...", "por_vencer": 4000000, "sin_carta_cobro": 0, "vencido": 0},
                        {"cliente": "CONCRETOS Y TR...", "por_vencer": 2000000, "sin_carta_cobro": 0, "vencido": 0},
                        {"cliente": "HELLMANN WOR...", "por_vencer": 2000000, "sin_carta_cobro": 0, "vencido": 0}
                    ],
                    "antiguedad_saldos": {
                        "total": {"sin_carta_cobro": 97185032, "por_vencer": 44168641, "00": 530764, "01-08": 4622047, "09-15": 3728334, "16-30": 3707702, "31-45": 168695, "46-60": 496169, "61-90": 0, "91-120": 213712, ">120": 14232078}
                    }
                }
            },
            "operaciones": {
                "dashboard_operaciones": {
                    "filtros": {"año": 2025, "mes": "septiembre"},
                    "indicadores_principales": {
                        "ingreso_viaje": {"valor": 20900885, "meta": 23889249, "vs_2024": 21868572, "ytd": 195904545},
                        "viajes": {"valor": 716, "meta": 914, "vs_2024": 835, "ytd": 7194},
                        "kilometros": {"valor": 439098, "meta": 592357, "vs_2024": 544286, "ytd": 4267963}
                    }
                }
            },
            "taller": {
                "mantenimiento": {
                    "filtros": {"año": 2025, "mes": "07-Jul"},
                    "indicadores_clave": {
                        "costo_interno": {"valor": 603880, "meta": 371948, "vs_2024": 338135, "ytd": 2929400},
                        "costo_externo": {"valor": 197773, "meta": 581033, "vs_2024": 528212, "ytd": 5394052},
                        "costo_llantas": {"valor": 18510, "meta": 1, "vs_2024": 58217, "ytd": 941316},
                        "total_mantenimiento": {"valor": 820164, "meta": 952982, "vs_2024": 924564, "ytd": 9264784},
                        "costo_por_km": {"valor": 1.32, "meta": 11.00, "vs_2024": 1.31, "ytd": 0.59},
                        "disponibilidad": 58
                    }
                }
            }
        }

    def get_main_trend_chart(self):
        data = {
            "mes": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
            "ingresos_actual": [25000000, 22000000, 24000000, 25000000, 22000000, 24000000, 22000000, 0, 20000000, 0, 20946909, 0],
            "ingresos_anterior": [29000000, 27000000, 28000000, 25000000, 27000000, 32000000, 29000000, 0, 25000000, 0, 17888058, 0],
            "meta": [27000000, 24000000, 25000000, 24000000, 24000000, 28000000, 0, 0, 22000000, 0, 19599920, 0]
        }
        return pd.DataFrame(data)

    def get_main_dashboard_table(self):
        data = {
            "Indicador": ["Ingresos por Viajes", "Costos por Viajes", "% Margen por Viaje", "Viajes", "Unidades Utilizadas", "Clientes Servidos", "Costo Viaje x Km", "Costo Mtto x Km", "Total Mantenimiento", "Rendimiento (kms/lts)", "Kilómetros", "Litros Total", "Estado de Carga", "Saldo Bancos M.N.", "% Disponibilidad Unidades", "Cartera Clientes M.N.", "Saldo Proveedores M.N."],
            "Valor Actual": [20946909, 9716281, "53.61%", 671, 82, 13, "$21.39", "$0.93", 818932, 1.91, 509537, 266159, "93%", 18933620, "28.88%", 32658208, 926023],
            "Meta": [19599920, 7711638, "$11,888,282", 848, "-", "-", "-", "-", 1447628, "-", "-", "-", "-", "-", "-", "-", "-"],
            "vs. 2024": [17888058, 8009507, "$9,878,551", 773, 99, 12, "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            "YTD/Variación": [236403764, 131046917, "$105,356,847", 8523, "-17.17%", "8.33%", "-", "-", "-43.43%", "-", "-", "-", "-", "-", "-", "-", "-"]
        }
        return pd.DataFrame(data)

    def get_admin_data(self):
        return {
            "facturacion_cobranza": {
                "filtros": {
                    "año": 2025,
                    "mes": "09-Sep",
                    "empresa_area": "Todas",
                    "tipo_operacion": "Todas",
                    "cliente": "Todas",
                    "estatus_cliente": "Todas",
                    "factura": "Todas",
                    "serie_factura": "Todas",
                    "estatus_serie": "Todas"
                },
                "indicadores_clave": {
                    "facturado_vs_cobrado": 22127664,
                    "prom_dias_cartera": 105
                },
                "acumulado": {
                    "facturado_acumulado": 194047842,
                    "notas_credito_acumulado": 209371,
                    "notas_cargo": 0,
                    "cobrado_acumulado": 22127664,
                    "cartera_clientes": 171710807
                },
                "mensual": {
                    "facturado_mes": 32437705,
                    "credito": 52579,
                    "cargo": 0,
                    "cobrado": 18193148
                },
                "graficas": {
                    "cartera_clasificacion": {
                        "tipo": "donut",
                        "total": 171710807,
                        "datos": [
                            {"clasificacion": "SIN CARTA COBRO", "monto": 97000000, "porcentaje": 56.6},
                            {"clasificacion": "POR VENCER", "monto": 45000000, "porcentaje": 26.03},
                            {"clasificacion": "VENCIDO", "monto": 30000000, "porcentaje": 17.37}
                        ]
                    },
                    "cartera_cliente": {
                        "tipo": "barra_horizontal_apilada",
                        "datos": [
                            {"cliente": "MATERIAS PRIMA...", "por_vencer": 73000000, "sin_carta_cobro": 0, "vencido": 77000000},
                            {"cliente": "OWENS AMERICA", "por_vencer": 13000000, "sin_carta_cobro": 11000000, "vencido": 34000000},
                            {"cliente": "VIDRIO PLANO D...", "por_vencer": 11000000, "sin_carta_cobro": 0, "vencido": 23000000},
                            {"cliente": "PETROLEOS MEXI...", "por_vencer": 15000000, "sin_carta_cobro": 0, "vencido": 0},
                            {"cliente": "VITRO VIDRIO AU...", "por_vencer": 12000000, "sin_carta_cobro": 0, "vencido": 0},
                            {"cliente": "INDUSTRIA DEL A...", "por_vencer": 4000000, "sin_carta_cobro": 0, "vencido": 0},
                            {"cliente": "CONCRETOS Y TR...", "por_vencer": 2000000, "sin_carta_cobro": 0, "vencido": 0},
                            {"cliente": "HELLMANN WOR...", "por_vencer": 2000000, "sin_carta_cobro": 0, "vencido": 0}
                        ]
                    }
                },
                "antiguedad_saldos": {
                    "columnas": ["area", "sin_carta_cobro", "por_vencer", "00", "01-08", "09-15", "16-30", "31-45", "46-60", "61-90", "91-120", "> 120", "total"],
                    "datos": [
                        {"area": "01-TINSA", "sin_carta_cobro": 11598200, "por_vencer": 28293474, "00": 530764, "01-08": 1023308, "09-15": 1513372, "16-30": 3050958, "31-45": 0, "46-60": 0, "61-90": 0, "91-120": 93872, "> 120": 11588577, "total": 57},
                        {"area": "02-TINSA CAD", "sin_carta_cobro": 9063486, "por_vencer": 5467133, "00": 0, "01-08": 2033689, "09-15": 0, "16-30": 0, "31-45": 0, "46-60": 59255, "61-90": 0, "91-120": 0, "> 120": 1711020, "total": 18},
                        {"area": "03-MTY MULTIF", "sin_carta_cobro": 602287, "por_vencer": 1830560, "00": 0, "01-08": 541323, "09-15": 134960, "16-30": 23520, "31-45": 111655, "46-60": 422547, "61-90": 0, "91-120": 0, "> 120": 2808858, "total": 6},
                        {"area": "04-MUL CAD", "sin_carta_cobro": 75921059, "por_vencer": 6853502, "00": 0, "01-08": 1023559, "09-15": 1077067, "16-30": 221300, "31-45": 57040, "46-60": 14367, "61-90": 0, "91-120": 119840, "> 120": 820423, "total": 86},
                        {"area": "05-GRANEL", "sin_carta_cobro": 0, "por_vencer": 1723972, "00": 0, "01-08": 0, "09-15": 942935, "16-30": 432924, "31-45": 0, "46-60": 0, "61-90": 0, "91-120": 0, "> 120": 0, "total": 3}
                    ]
                }
            }
        }

    def get_admin_payables_data(self):
        return {
            "cuentas_por_pagar": {
                "indicadores_clave": {
                    "saldo_total_proveedores": 926023
                },
                "graficas": {
                    "saldo_proveedores_clasificacion": {
                        "tipo": "donut",
                        "total": 926023,
                        "datos": [
                            {"clasificacion": "POR VENCER", "monto": 608000, "porcentaje": 65.62},
                            {"clasificacion": "VENCIDO", "monto": 318000, "porcentaje": 34.38}
                        ]
                    }
                }
            }
        }

    def get_admin_banks_data(self):
        return {
            "tesoreria_bancos": {
                "indicadores_clave": {
                    "saldo_actual": 18933620
                },
                "movimientos": {
                    "saldo_inicial": 18076634,
                    "ingresos": 472111604,
                    "egresos": 471254617
                }
            }
        }

    def get_ops_income_data(self):
        return {
            "kpis": {
                "ingresos_por_viajes": 20946909,
                "viajes": 671,
                "kilometros": 509537,
                "unidades_utilizadas": 82,
                "clientes_servidos": 13,
                "rendimiento_kms_lts": 1.91,
                "litros_total": 266159,
                "estado_carga": 93
            },
            "promedios": {
                "ingreso_por_viaje": 31217.45,
                "km_por_viaje": 759.37,
                "ingreso_por_km": 41.11
            },
            "tablas": {
                "rutas": [
                    {"ruta": "3T-LYCRA", "viajes": 29},
                    {"ruta": "ALCALI-ALCALI", "viajes": 5},
                    {"ruta": "ALCALI-SASIL", "viajes": 52},
                    {"ruta": "CANOITAS-DALTILE", "viajes": 314},
                    {"ruta": "CANOITAS-FEVISA", "viajes": 1150}
                ],
                "unidades": [
                    {"unidad": "01", "kms_vacios": 0, "kms_cargados": 2871, "kms_totales": 2871},
                    {"unidad": "02", "kms_vacios": 0, "kms_cargados": 1020, "kms_totales": 1020},
                    {"unidad": "03", "kms_vacios": 75, "kms_cargados": 3090, "kms_totales": 3165},
                    {"unidad": "05", "kms_vacios": 0, "kms_cargados": 0, "kms_totales": 0}
                ],
                "clientes": [
                    {"cliente": "MATERIAS PRIMA...", "viajes": 0, "kms": 0},
                    {"cliente": "OWENS AMERICA", "viajes": 0, "kms": 0},
                    {"cliente": "VIDRIO PLANO D...", "viajes": 0, "kms": 0},
                    {"cliente": "PETROLEOS MEXI...", "viajes": 0, "kms": 0},
                    {"cliente": "VITRO VIDRIO AU...", "viajes": 0, "kms": 0},
                    {"cliente": "INDUSTRIA DEL A...", "viajes": 0, "kms": 0},
                    {"cliente": "CONCRETOS Y TR...", "viajes": 0, "kms": 0},
                    {"cliente": "HELLMANN WOR...", "viajes": 0, "kms": 0}
                ]
            }
        }

    def get_ops_costs_data(self):
        return {
            "costos_totales": {
                "costos_por_viajes": 9716281,
                "total_mantenimiento": 818932,
                "costo_viaje_por_km": 21.39,
                "costo_mtto_por_km": 0.93
            },
            "utilidad": {
                "margen_por_viaje_porcentaje": 53.61,
                "margen_por_viaje_monto": 11225228,
                "utilidad_neta": 105356847
            },
            "desglose_gastos": {
                "mantenimiento": {
                    "taller_interno": 564513,
                    "taller_externo": 254419,
                    "costo_llantas": 0,
                    "correctivo": 778167,
                    "preventivo": 41997
                },
                "por_familia": {
                    "motor": 129253,
                    "sistema_de_frenos": 111333,
                    "remolques": 99437,
                    "general": 80982
                },
                "por_flota": {
                    "general": 776817,
                    "dedicado": 35996,
                    "sin_asignar": 7351
                }
            }
        }

    def get_ops_performance_data(self):
        """
        Devuelve datos de rendimiento operativo, principalmente de combustible.
        """
        data = {
            "rendimiento_combustible": {
                "valor_actual": 1.91,
                "unidad": "km/lt",
                "meta": None,
                "vs_anterior": None,
                "ytd": None
            },
            "kilometros_mes": 509537,
            "litros_total_mes": 266159,
            "estado_carga": 0.93,
            "viajes_mes": 671,
            "unidades_utilizadas": 82,
            "clientes_servidos": 13,
            "costo_viaje_km": 21.39,
            "costo_mtto_km": 0.93
        }
        return data

    def get_mantenimiento_data(self):
        """
        Devuelve datos de mantenimiento, KPIs, disponibilidad y principales fallas.
        """
        data = {
            "kpis_taller": {
                "costo_interno": {
                    "valor": 603880,
                    "meta": 371948,
                    "vs_2024": 0.7859,
                    "ytd": -0.3102
                },
                "costo_externo": {
                    "valor": 197773,
                    "meta": 581033,
                    "vs_2024": -0.6256,
                    "ytd": -0.1940
                },
                "costo_llantas": {
                    "valor": 18510,
                    "meta": 1,
                    "vs_2024": -0.6820,
                    "ytd": 134.47
                },
                "total_mantenimiento": {
                    "valor": 820164,
                    "meta": 952982,
                    "vs_2024": -0.1129,
                    "ytd": None
                },
                "costo_por_km": {
                    "valor": 1.32,
                    "meta": 11.00,
                    "vs_2024": 0.0114,
                    "ytd": -0.9882
                }
            },
            "disponibilidad": 0.58,
            "top_fallas": [
                {"familia": "MOTOR", "costo": 129253},
                {"familia": "SISTEMA DE FRENOS", "costo": 111333},
                {"familia": "REMOLQUES", "costo": 99437},
                {"familia": "GENERAL", "costo": 80982}
            ],
            "distribucion_tipo_mantenimiento": {
                "CORRECTIVO": 0.5361,
                "PREVENTIVO": 0.3446
            }
        }
        return data

