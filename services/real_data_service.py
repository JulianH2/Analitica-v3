import pandas as pd

class RealDataService:
    def get_full_dashboard_data(self):
        return {
            "administracion": {
                "facturacion_cobranza": {
                    "indicadores": {
                        "facturado_vs_cobrado": {"valor": 22127664, "meta": 30000000},
                        "prom_dias_cartera": {"valor": 105, "meta": 150}
                    },
                    "acumulado": {
                        "facturado_acumulado": {"valor": 194047842},
                        "notas_credito_acumulado": {"valor": 209371},
                        "notas_cargo": {"valor": 0},
                        "cobrado_acumulado": {"valor": 22127664},
                        "cartera_clientes": {"valor": 171710807}
                    },
                    "mensual": {
                        "facturado_mes": {"valor": 32437705},
                        "credito": {"valor": 52579},
                        "cargo": {"valor": 0},
                        "cobrado": {"valor": 18193148}
                    },
                    "graficas": {
                        "comparativa": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [46.6, 37.3, 103.2, 41.4, 222.9, 117.0, 39.5, 36.3, 40.1, 32.1, 27.2, 25.7],
                            "anterior": [29.4, 0, 62.9, 31.6, 23.0, 33.0, 0, 0, 0, 0, 0, 0]
                        },
                        "mix": {"labels": ['SIN CARTA COBRO', 'POR VENCER', 'VENCIDO'], "values": [56.6, 26.03, 17.37]},
                        "stack": {
                            "clientes": ["MATERIAS PRIMA", "OWENS AMERICA", "VIDRIO PLANO", "PETROLEOS MEX", "VITRO VIDRIO"],
                            "por_vencer": [73, 13, 11, 15, 12],
                            "sin_carta": [0, 11, 0, 0, 0],
                            "vencido": [77, 34, 23, 0, 0]
                        }
                    },
                    "antiguedad": {
                        "h": ["Área", "SIN CARTA", "POR VENCER", "VENCIDO", "Total"],
                        "r": [
                            ["01-TINSA", "$11,598,200", "$28,293,474", "$17,265,373", "$57,157,047"],
                            ["02-TINSA CAD", "$9,063,486", "$5,467,133", "$3,711,020", "$18,241,639"],
                            ["TOTAL", "$97,185,032", "$44,168,641", "$30,357,134", "$171,710,807"]
                        ]
                    }
                },
                "cuentas_por_pagar": {
                    "indicadores": {
                        "cxp_vs_pagado": {"valor": 14000000, "meta": 17000000},
                        "promedio_pago": {"valor": 22, "meta": 30}
                    },
                    "acumulado": {
                        "saldo_inicial": {"valor": 1000000},
                        "cxp": {"valor": 15000000},
                        "notas_cargo": {"valor": 0},
                        "notas_credito": {"valor": 137000},
                        "anticipo": {"valor": 4000},
                        "cxp_total": {"valor": 17000000},
                        "pago_proveedores": {"valor": 14000000},
                        "saldo": {"valor": 3000000}
                    },
                    "graficas": {
                        "comparativa": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [26, 25, 19, 19, 21, 21, 20, 20, 16, 17, 13, 28],
                            "anterior": [17, 15, 14, 17, 18, 15, 13, 14, 15, 13, 14, 13]
                        },
                        "mix": {"labels": ['POR VENCER', 'VENCIDO'], "values": [89.61, 10.39]},
                        "saldo_proveedor": {
                            "prov": ["NEWYO GAS", "INFORMATICA UG", "LLANTAS Y REFAC", "TRACTO REFACCI", "TRACTO IMPORTA"],
                            "por_vencer": [0.70, 0.69, 0.41, 0.11, 0.15],
                            "vencido": [0.30, 0.31, 0.0, 0.0, 0.0]
                        }
                    },
                    "antiguedad": {
                        "h": ["Área", "POR VENCER", "00", "01-08", "09-15", "16-30", "31-45", "46-60", "Total"],
                        "r": [["01-TINSA", "$2,403,183", "$0", "$28,243", "$58,899", "$9,427", "$55,661", "$4,442", "$2,670,638"],
                              ["TOTAL", "$2,585,972", "$0", "$28,243", "$58,899", "$11,377", "$55,661", "$6,182", "$2,885,966"]]
                    }
                },
                "bancos": {
                    "indicadores": {
                        "saldo_inicial": {"valor": 20582298},
                        "ingresos": {"valor": 426484509},
                        "egresos": {"valor": 426092482},
                        "saldo_final": {"valor": 20974325}
                    },
                    "graficas": {
                        "diaria": {
                            "dias": list(range(1, 31)),
                            "ingresos": [10, 11, 12, 11, 10, 8, 9, 11, 12, 13, 14, 28, 15, 14, 13, 12, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22, 24, 26, 28, 30],
                            "egresos": [9, 10, 11, 10, 9, 2, 5, 8, 9, 10, 11, 25, 12, 11, 10, 9, 8, 9, 10, 11, 23, 12, 11, 10, 9, 10, 11, 12, 13, 14]
                        },
                        "donut": {"labels": ["BANREGIO"], "values": [20.97]}
                    },
                    "conceptos": {
                        "h": ["Concepto", "Ingresos Cons.", "Egresos Cons."],
                        "r": [["APERTURA INVERSIONES", "$17,267,707", "$349,976,631"],
                              ["DEPOSITOS CLIENTES", "$18,193,148", "$0"],
                              ["PAGO A PROVEEDORES", "$0", "$3,506,638"]]
                    }
                }
            },
            "operaciones": {
                "dashboard": {
                    "indicadores": {
                        "ingreso_viaje": {
                            "valor": 20900885, 
                            "meta": 23889249, 
                            "label_mes": "$21.8M (-4.4%)", 
                            "label_ytd": "$195.9M (-20%)"
                        },
                        "viajes": {
                            "valor": 716, 
                            "meta": 914, 
                            "label_mes": "835 (-14.2%)", 
                            "label_ytd": "7,194 (-34.6%)"
                        },
                        "kilometros": {
                            "valor": 439098, 
                            "meta": 592357, 
                            "label_mes": "544k (-11.5%)", 
                            "label_ytd": "4.2M (-21.9%)"
                        }
                    },
                    "utilizacion": {"valor": 92},
                    "promedios": {
                        "ingreso_viaje": {"valor": 29191, "meta": 0, "vs_2024": 0.11},
                        "ingreso_unit": {"valor": 254889, "meta": 0, "vs_2024": 0.25},
                        "unidades_utilizadas": {"valor": 82, "meta": 0, "vs_2024": -0.24},
                        "clientes_servidos": {"valor": 15, "meta": 0, "vs_2024": 0.36}
                    },
                    "graficas": {
                        "ingresos_anual": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [25, 22, 24, 25, 22, 24, 22, 18, 20, 14, 19, 22],
                            "anterior": [29, 27, 28, 25, 27, 32, 29, 27, 25, 24, 22, 24],
                            "meta": [27, 24, 25, 24, 24, 28, 27, 24, 22, 22, 20, 22]
                        },
                        "viajes_anual": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [700, 650, 720, 716, 680, 710, 690, 640, 716, 600, 620, 650],
                            "anterior": [850, 800, 820, 835, 810, 840, 830, 800, 835, 780, 790, 810]
                        },
                        "mix_operacion": {
                            "labels": ["REFINADOS", "ARENERA LOCAL", "CONTENEDOR FORÁNEO", "OTROS"],
                            "values": [36.8, 28.5, 7.71, 26.99]
                        },
                        "balanceo_unidades": {
                            "unidades": ["Unidad 144", "Unidad 99", "Unidad 107", "Unidad 143", "Unidad 154"],
                            "montos": [0.65, 0.61, 0.59, 0.58, 0.56]
                        }
                    },
                    "tablas": {
                        "rutas_cargado": {
                            "h": ["No.", "Ruta", "Viajes", "Kms", "Costo x Km", "Costo Viaje Total"],
                            "r": [
                                ["261", "3T-LYCRA", "1", "29", "$193.01", "$5,597"],
                                ["234", "PATIEROS Y GRANEL", "51", "1,785", "$214.10", "$382,173"]
                            ]
                        }
                    }
                },
                "rendimientos": {
                    "indicadores": {
                        "kms_lt": {
                            "valor": 1.86, 
                            "meta": 3.0, 
                            "label_mes": "1.79 (4.27%)", 
                            "label_ytd": "1.85 (-94%)"
                        },
                        "kms_reales": {
                            "valor": 513165, 
                            "meta": 592357, 
                            "label_mes": "579k (-11%)", 
                            "label_ytd": "4.5M (-21%)",
                            "extra_info": ["Kms/Viaje", "716.71"]
                        },
                        "litros": {
                            "valor": 275490, 
                            "meta": 300000, 
                            "label_mes": "324k (-15%)", 
                            "label_ytd": "2.4M (20%)",
                            "extra_info": ["Lts/Viaje", "384.76"]
                        }
                    },
                    "graficas": {
                        "tendencia": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [1.85, 1.82, 1.82, 1.81, 1.74, 1.70, 1.79, 1.78, 1.86, 1.82, 1.83, 1.86],
                            "anterior": [4.46, 1.99, 1.82, 1.87, 1.84, 1.79, 1.90, 1.94, 1.79, 1.88, 1.91, 1.93]
                        },
                        "mix_operacion": {
                            "labels": ["ARENERA LOCAL", "CONTENEDOR FORÁNEO", "PLANA LOCAL", "CONTENEDOR LOCAL", "OTROS"],
                            "values": [15.12, 14.45, 13.29, 12.6, 44.54]
                        }
                    },
                    "tablas": {
                        "unidad": {
                            "h": ["Unidad", "Rend. Real", "Viajes"],
                            "r": [["03", "3.35", "8"], ["148", "2.61", "11"], ["94", "2.61", "12"], ["96", "2.55", "9"]]
                        },
                        "operador": {
                            "h": ["Operador", "Rend. Real", "Viajes", "Kms Real", "Litros Total"],
                            "r": [
                                ["AGUILAR CAZARES GERARDO", "1.95", "7", "8,530", "4,364"],
                                ["AGUILAR YAÑEZ JORGE LUIS", "2.00", "7", "6,967", "3,479"],
                                ["ALANIS ALANIS AMBROCIO", "1.76", "9", "3,726", "2,112"]
                            ]
                        }
                }},
                "rutas": {
                    "mapa": {
                        "puntos": [
                            {"lat": 25.68, "lon": -100.31, "nombre": "Monterrey"},
                            {"lat": 19.43, "lon": -99.13, "nombre": "México DF"}
                        ]
                    },
                    "tablas": {
                        "detalle_rutas": {
                            "h": ["No.", "Ruta", "Cliente", "Cargados", "Vacíos", "Kms Total", "Utilización %"],
                            "r": [
                                ["1", "MTY-MEX", "COCA COLA", "84", "12", "85,400", "87.5%"],
                                ["2", "MEX-GUA", "PEPSI", "76", "15", "54,200", "83.5%"],
                                ["3", "GUA-MTY", "LOGISTICA X", "92", "5", "98,206", "94.8%"]
                            ]
                        }
                    }
        },
                "costos": {
                    "indicadores": {
                        "utilidad_viaje": {
                            "valor": 18.19, 
                            "meta": 25.0, 
                            "label_mes": "17.4% (-68%)", 
                            "label_ytd": "14.2% (-43%)"
                        },
                        "costo_total": {
                            "valor": 17098160, 
                            "meta": 9796576, 
                            "label_mes": "$9.9M (71%)", 
                            "label_ytd": "$111.6M (18%)"
                        }
                    },
                    "graficas": {
                        "mensual_utilidad": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "costo": [11, 11, 13, 10, 11, 28, 22, 17, 11, 10, 11, 9],
                            "utilidad_pct": [51.33, 53.36, 53.65, 0, 52.80, 69.52, 0, 0, 0, 50.25, 53.61, 57.92]
                        },
                        "desglose_conceptos": {
                            "conceptos": ["Combustible", "Percepción Operador", "Sueldo", "Otros", "Estancias"],
                            "montos": [13940407, 3055793, 2269771, 2139090, 648771]
                        },
                        "comparativa_costos": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [11, 10, 12, 12, 11, 28, 12, 12, 17, 11, 11, 9],
                            "anterior": [8, 8, 10, 11, 11, 11, 10, 7, 8, 7, 8, 8]
                        }
                    },
                    "tablas": {
                        "margen_ruta": {
                            "h": ["No.", "Ruta", "Ingreso", "Cant. Viajes", "Combustible", "Sueldo", "Costo Total", "Utilidad"],
                            "r": [
                                ["355", "APAXCO-VITRO", "$1,686,423", "29", "$526,937", "$84,000", "$802,703", "$883,720"],
                                ["1", "CANOITAS-OWENS", "$3,660,979", "170", "$1,025,036", "$154,960", "$1,680,976", "$1,980,003"],
                                ["3", "CANOITAS-VITRO", "$2,250,330", "89", "$571,029", "$84,550", "$889,165", "$1,361,165"]
                            ]
                        }
                    }
                }
            },
            "mantenimiento": {
                "dashboard": {
                    "indicadores": {
                        "costo_interno": {"valor": 603880, "meta": 371948, "vs_2024": 338135, "ytd": 2929400},
                        "costo_externo": {"valor": 197773, "meta": 581033, "vs_2024": 528212, "ytd": 5394052},
                        "costo_llantas": {"valor": 18510, "meta": 1, "vs_2024": 58217, "ytd": 941316},
                        "total_mantenimiento": {"valor": 820164, "meta": 952982, "vs_2024": 924564, "ytd": 9264784},
                        "costo_km": {"valor": 1.32, "meta": 11.0, "vs_2024": 1.31, "ytd": 0.59},
                        "disponibilidad": {"valor": 58, "meta": 100, "vs_2024": 0, "ytd": 0}
                    },
                    "graficas": {
                        "tendencia_anual": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [1.0, 1.0, 2.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                            "anterior": [1.0, 2.0, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0],
                            "meta": [1.5, 1.2, 0.8, 1.8, 2.0, 1.5, 0.8, 1.1, 0.9, 1.6, 1.3, 1.4]
                        },
                        "corrective_preventive": {
                            "labels": ["CORRECTIVO", "PREVENTIVO"],
                            "values": [778167, 41997]
                        },
                        "por_familia": {
                            "labels": ["MOTOR", "SISTEMA DE FRENOS", "REMOLQUES", "GENERAL"],
                            "values": [129253, 111333, 99437, 80982]
                        },
                        "por_flota": {
                            "labels": ["GENERAL", "DEDICADO", "SIN ASIGNAR"],
                            "values": [776817, 35996, 7351]
                        },
                        "por_operacion": {
                            "labels": ["SIN ASIGNAR"],
                            "values": [820164]
                        },
                        "costo_km_unidad": {
                            "labels": ["118", "TV265", "106", "TV224"],
                            "values": [243.19, 33.75, 21.90, 17.62]
                        },
                        "costo_km_marca": {
                            "labels": ["VISUSA", "TYTANK", "CARMEX", "KENWORTH"],
                            "values": [5.23, 2.99, 2.64, 1.79]
                        },
                        "entradas_unidad": {
                            "labels": ["87", "10", "82", "21"],
                            "values": [9, 7, 7, 6]
                        }
                    }
            },
                "almacen": {
                    "indicadores": {
                        "inventario_inicial": {"valor": 12926174, "meta": 0, "vs_2024": 0},
                        "entradas": {"valor": 6128092, "meta": 0, "vs_2024": 0},
                        "salidas": {"valor": 4535675, "meta": 0, "vs_2024": 0},
                        "valorizacion_historica": {"valor": 14561121, "meta": 30384198, "vs_2024": 0},
                        "valorizacion_actual": {"valor": 21111205, "meta": 30384198, "label_mes": "$21.1M (-30%)"},
                        "cumplimiento": {"valor": 47.32, "meta": 100, "vs_2024": 0},
                        "con_existencia": {"valor": 4000, "meta": 0, "vs_2024": 0},
                        "sin_existencia": {"valor": 4000, "meta": 0, "vs_2024": 0},
                        "registrados": {"valor": 8000, "meta": 0, "vs_2024": 0}
                    },
                    "graficas": {
                        "historico_anual": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [18.0, 19.0, 19.3, 24.4, 20.5, 12.9, 14.5, 16.8, 21.9, 19.8, 19.4, 16.5],
                            "anterior": [21.3, 22.6, 25.8, 27.0, 27.1, 27.6, 27.6, 32.2, 0, 45.0, 28.6, 20.3]
                        },
                        "por_area": {
                            "labels": ["01-TINSA", "02-TINSA CAD", "03-MTY MULTIF", "04-MUL CAD", "05-GRANEL"],
                            "values": [9770561, 7458535, 1965866, 1057716, 858527]
                        }
                    },
                    "tablas": {
                        "familia": {
                            "h": ["Familia", "Cantidad", "Valorización Actual", "%TG Valorización", "Estado MinMax"],
                            "r": [
                                ["LLANTAS Y RINES", "5651.00", "$5,356,301", "25.37%", "Dentro del rango"],
                                ["DIESEL", "31794594.58", "$3,227,786", "15.29%", "Dentro del rango"],
                                ["GENERAL", "149851.10", "$3,065,593", "14.52%", "Dentro del rango"]
                            ]
                        },
                        "historico": {
                            "h": ["Período", "Área", "Almacén", "Insumo", "U.M.", "Estado", "C. Inicial", "C. Entradas"],
                            "r": [
                                ["31/07/2025", "01-TINSA", "REFACCIONES TINSA MTY", "0000000056", "PIEZA", "NUEVO", "0.00", "10.00"]
                            ]
                        }
                    }},
                "disponibilidad": {
                    "indicadores": {
                        "pct_disponibilidad": {
                            "valor": 58, 
                            "meta": 100, 
                            "vs_2024": 0, 
                            "ytd": 0, 
                            "label_mes": "58%", 
                            "label_ytd": "N/A"
                        },
                        "entradas_taller": {
                            "valor": 335, 
                            "meta": 300, 
                            "vs_2024": 0, 
                            "ytd": 2450, 
                            "label_mes": "2,450", 
                            "label_ytd": "N/A"
                        }
                    },
                    "graficas": {
                        "disponibilidad_mensual": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [70, 71, 62, 63, 59, 58, 50, 49, 37, 37, 29, 27],
                            "anterior": [78, 69, 73, 64, 59, 52, 48, 50, 46, 43, 55, 0],
                            "meta": [100] * 12
                        },
                        "entradas_vs_kms": {
                            "unidades": ["U-118", "U-106", "U-21", "U-60", "U-46", "U-09"],
                            "entradas": [9, 7, 7, 6, 8, 5],
                            "kms": [14640, 8561, 7195, 7698, 5400, 3200]
                        }
                    },
                    "tablas": {
                        "detalle": {
                            "h": ["Tipo Operación / Unidad", "Días Mes", "Días Taller", "Días Disp.", "Disponibilidad"],
                            "r": [
                                ["SIN ASIGNAR", "4991", "2083", "2908", "58%"],
                                ["CADEREYTA MULTIFLET", "93", "37", "56", "60%"],
                                ["M07", "31", "14", "17", "55%"],
                                ["VMR25", "31", "1", "30", "97%"],
                                ["CADEREYTA TINSA", "1922", "837", "1085", "56%"],
                                ["Total", "4991", "2083", "2908", "58%"]
                            ]
                        }
                    }
        },
                "compras": {
                    "indicadores": {
                        "total": {"valor": 5648478, "vs_2024": 6885581, "ytd": 37665913},
                        "diesel": {"valor": 3923274},
                        "stock": {"valor": 1725204}
                    },
                    "graficas": {
                        "tendencia": {
                            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                            "actual": [3.37, 5.67, 4.21, 4.71, 4.37, 5.85, 5.64, 6.29, 5.20, 7.40, 4.30, 5.71],
                            "anterior": [5.51, 0, 6.88, 8.53, 7.27, 0, 6.88, 0, 6.61, 0, 7.01, 0]
                        },
                        "por_area": {
                            "areas": ["MTY TINSA", "CADEREYTA TINSA", "EL CARMEN G.", "CADEREYTA M.", "MTY MULTIFLET"],
                            "valores": [3.8, 0.6, 0.6, 0.6, 0.1]
                        },
                        "tipo": {
                            "labels": ["DIESEL", "REFACCIONES", "LLANTAS"],
                            "values": [3.92, 1.24, 0.32]
                        }
                    },
                    "tablas": {
                        "proveedores": {
                            "h": ["Proveedor", "Monto", "% Monto"],
                            "r": [
                                ["NEWYO GAS, S.A. DE C.V.", "$3,923,274", "69.46%"],
                                ["TECNOCAM", "$259,200", "4.59%"],
                                ["KENWORTH DE MONTERREY", "$204,437", "3.62%"]
                            ]
                        },
                        "ordenes": {
                            "h": ["Orden", "Fecha", "Proveedor", "Tipo", "Insumo", "Total Compra"],
                            "r": [
                                ["202500556", "01/07/2025", "ACCESORIOS ALLENDE", "REFACCIONES", "STOCK", "$2,987"],
                                ["202500560", "01/07/2025", "GA DIESEL PARTS", "REFACCIONES", "STOCK", "$3,805"]
                            ]
                        },
                        "insumos": {
                            "h": ["Área", "Insumo", "Nombre Insumo", "Almacén", "Precio", "Cantidad", "Subtotal"],
                            "r": [
                                ["05-EL CARMEN", "0116002003", "SOLDADURA 7018", "REFACCIONES GRANEL", "$81", "20", "$1,624"],
                                ["05-EL CARMEN", "0117001001", "DIESEL", "AUTOCONSUMO", "$19", "15,000", "$288,362"]
                            ]
                        }
                    }
                }
            }
        
        }