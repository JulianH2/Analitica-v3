PBI_MAPPING = {
    'financial': {
        'kpis': {
            'monthly_billed': 'h_factura_saldo[Facturado Mes]',
            'accumulated_billed': 'h_factura_saldo[Facturado Acumulado]',
            'monthly_collected': 'h_factura_saldo[m_cobrado_mes_mx]',
            'billed_vs_collected': 'h_factura_saldo[% Facturación Cobrada]',
            'average_payment_days': 'h_factura_saldo[Promedio Días Cartera]',
            'customer_portfolio': 'h_factura_saldo[Cartera Vencida]',
            'monthly_credit': 'h_factura_saldo[m_ncred_mes_mx]',
            'monthly_debit': 'h_factura_saldo[m_ncargo_mes_mx]',
            'accounts_payable': 'h_proveedores[Cuentas x Pagar]',
            'total_accounts_payable': 'h_proveedores[Saldo CxP]',
            'initial_balance': 'h_proveedores[Saldo Inicial CxP]',
            'supplier_payments': 'h_proveedores[Pago Proveedor]',
            'average_payment_days_payable': 'h_proveedores[Promedio Días Pago]',
            'accounts_payable_vs_paid': 'h_proveedores[RotacionCuentasPorPagar]'
        },
        'charts': {}
    },
    'operational': {
        'kpis': {
            'trip_revenue': 'h_viaje[Ingreso Viaje]',
            'total_cost': 'd_viaje[Costo Viaje Total]',
            'trip_profit': 'd_viaje[Monto Utilidad]',
            'trips': 'h_viaje[Viajes]',
            'units_used': 'd_unidad[Unidades Cantidad]',
            'customers_served': 'h_relacion_viaje_cp[Clientes Servidos]',
            'kilometers': 'd_unidad_kilometros[Kms Unidad]',
            'liters': 'd_viaje[Litros Real]',
            'cost_per_km': 'd_viaje[Costo Viaje x Km]',
            'utilization': 'h_viaje[Unidades Utilizadas]',
            'km_per_liter': 'd_viaje[Rendimiento Real]',
            'real_kilometers': 'd_viaje[Kms Real]',
            'average_trip_revenue': 'h_viaje[Ingreso x Viaje]',
            'average_unit_revenue': 'h_viaje[Ingreso x Unidad]'
        },
        'charts': {}
    },
    'maintenance': {
        'kpis': {
            'total_maintenance_cost': 'd_orden_servicio[Costo de Mantenimiento]',
            'internal_labour_cost': 'd_mo_orden[Costo Mano de Obra Interno]',
            'external_labour_cost': 'h_taller_gasto_taller_externo[Costo Mano de Obra Externo]',
            'tire_cost': 'h_llantas_nueva[Costo Llantas Nuevas]',
            'availability_pct': 'h_unidad_indicadores_mes_diario[% Disponibilidad]',
            'cost_per_km': 'd_unidad_kilometros_diarios[Costo Mtto x Km]',
            'workshop_entries_count': 'd_orden_servicio[Entradas a Taller]',
            'preventive_maintenance_compliance': 'h_inventario_almacen[Nivel Cumplimiento MaxMin]',
            'initial_inventory': 'h_inventario_cierre_mes[Inventario Inicial]',
            'inventory_entries': 'h_inventario_cierre_mes[Entradas]',
            'registered_skus': 'h_inventario_almacen[Insumos Registrados]',
            'skus_in_stock': 'h_inventario_almacen[Insumos con Existencia]',
            'skus_out_of_stock': 'h_inventario_almacen[Insumos sin Existencia]',
            'inventory_exits': 'h_inventario_cierre_mes[Salidas]',
            'current_inventory_value': 'h_inventario_almacen[Valorización Actual]',
            'total_purchase': 'h_orden_compra[Compras]',
            'diesel_purchase': 'h_orden_compra[Compras Combustibles]',
            'stock_purchase': 'h_orden_compra[Compras Stock y No Stock]'
        },
        'charts': {}
    }
}