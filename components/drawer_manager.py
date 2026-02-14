import dash
from dash import html, callback, Input, Output, ALL, State, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
from settings.theme import DesignSystem
import pandas as pd


def create_smart_drawer(drawer_id: str = "smart-drawer"):
    return html.Div([
        dcc.Download(id=f"{drawer_id}-download"),
        dcc.Store(id=f"{drawer_id}-export-data"),
        dmc.Drawer(
            id=drawer_id,
            position="right",
            size="70%",
            padding=0,
            withCloseButton=False,
            opened=False,
            styles={
                "body": {"padding": 0, "height": "100%"},
                "content": {"display": "flex", "flexDirection": "column", "height": "100%"}
            },
            children=[
                html.Div(
                    id=f"{drawer_id}-container",
                    style={"display": "flex", "flexDirection": "column", "height": "100%"},
                    children=[
                        _create_drawer_header(drawer_id),
                        
                        dmc.Tabs(
                            value="resumen",
                        variant="pills",
                        color="blue",
                        style={"flex": 1, "display": "flex", "flexDirection": "column", "overflow": "hidden"},
                        children=[
                            dmc.TabsList(
                                px="md",
                                pt="xs",
                                pb="md",
                                style={"borderBottom": f"1px solid {DesignSystem.SLATE[2]}"},
                                children=[
                                    dmc.TabsTab(
                                        dmc.Group(gap="xs", children=[
                                            DashIconify(icon="tabler:chart-line", width=16),
                                            "Resumen"
                                        ]),
                                        value="resumen"
                                    ),
                                    dmc.TabsTab(
                                        dmc.Group(gap="xs", children=[
                                            DashIconify(icon="tabler:layout-grid", width=16),
                                            "Desglose"
                                        ]),
                                        value="desglose"
                                    ),
                                    dmc.TabsTab(
                                        dmc.Group(gap="xs", children=[
                                            DashIconify(icon="tabler:table", width=16),
                                            "Datos"
                                        ]),
                                        value="datos"
                                    ),
                                    dmc.TabsTab(
                                        dmc.Group(gap="xs", children=[
                                            DashIconify(icon="tabler:bulb", width=16),
                                            "Insights IA"
                                        ]),
                                        value="insights",
                                        style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "color": "white"}
                                    ),
                                    dmc.TabsTab(
                                        dmc.Group(gap="xs", children=[
                                            DashIconify(icon="tabler:bolt", width=16),
                                            "Acciones"
                                        ]),
                                        value="acciones"
                                    ),
                                ]
                            ),
                            
                            dmc.TabsPanel(
                                html.Div(id=f"{drawer_id}-tab-resumen"),
                                value="resumen",
                                style={"flex": 1, "overflow": "auto", "padding": "1rem"}
                            ),
                            dmc.TabsPanel(
                                html.Div(id=f"{drawer_id}-tab-desglose"),
                                value="desglose",
                                style={"flex": 1, "overflow": "auto", "padding": "1rem"}
                            ),
                            dmc.TabsPanel(
                                html.Div(id=f"{drawer_id}-tab-datos"),
                                value="datos",
                                style={"flex": 1, "overflow": "auto", "padding": "1rem"}
                            ),
                            dmc.TabsPanel(
                                html.Div(id=f"{drawer_id}-tab-insights"),
                                value="insights",
                                style={"flex": 1, "overflow": "auto", "padding": "1rem"}
                            ),
                            dmc.TabsPanel(
                                html.Div(id=f"{drawer_id}-tab-acciones"),
                                value="acciones",
                                style={"flex": 1, "overflow": "auto", "padding": "1rem"}
                            ),
                        ]
                    )
                ]
            )
        ]
        )
    ])


def _create_drawer_header(drawer_id):
    return dmc.Paper(
        p="md",
        radius=0,
        shadow="sm",
        style={"borderBottom": f"2px solid {DesignSystem.SLATE[2]}"},
        children=dmc.Group(
            justify="space-between",
            children=[
                dmc.Group(
                    gap="sm",
                    children=[
                        dmc.ThemeIcon(
                            id=f"{drawer_id}-header-icon",
                            children=DashIconify(icon="tabler:chart-bar", width=24),
                            size="lg",
                            variant="light",
                            color="blue"
                        ),
                        html.Div([
                            dmc.Text(
                                id=f"{drawer_id}-header-title",
                                children="Análisis Detallado",
                                size="lg",
                                fw=700
                            ),
                            dmc.Text(
                                id=f"{drawer_id}-header-subtitle",
                                children="Exploración profunda de métricas",
                                size="xs",
                                c="dimmed"
                            )
                        ])
                    ]
                ),
                dmc.Group(
                    gap="xs",
                    children=[
                        dmc.Tooltip(
                            label="Exportar datos",
                            children=dmc.ActionIcon(
                                children=DashIconify(icon="tabler:download", width=18),
                                variant="subtle",
                                color="gray",
                                size="lg"
                            )
                        ),
                        dmc.Tooltip(
                            label="Compartir análisis",
                            children=dmc.ActionIcon(
                                children=DashIconify(icon="tabler:share", width=18),
                                variant="subtle",
                                color="gray",
                                size="lg"
                            )
                        ),
                        dmc.Tooltip(
                            label="Cerrar",
                            children=dmc.ActionIcon(
                                id=f"{drawer_id}-close",
                                children=DashIconify(icon="tabler:x", width=18),
                                variant="subtle",
                                color="gray",
                                size="lg"
                            )
                        )
                    ]
                )
            ]
        )
    )


def register_drawer_callback(drawer_id: str, widget_registry: dict, screen_id: str):
    from services.data_manager import data_manager

    _no = no_update

    @callback(
        Output(drawer_id, "opened"),
        Output(f"{drawer_id}-header-title", "children"),
        Output(f"{drawer_id}-header-subtitle", "children"),
        Output(f"{drawer_id}-header-icon", "children"),
        Output(f"{drawer_id}-tab-resumen", "children"),
        Output(f"{drawer_id}-tab-desglose", "children"),
        Output(f"{drawer_id}-tab-datos", "children"),
        Output(f"{drawer_id}-tab-insights", "children"),
        Output(f"{drawer_id}-tab-acciones", "children"),
        Output(f"{drawer_id}-export-data", "data"),
        Input({"type": "open-smart-drawer", "index": ALL}, "n_clicks"),
        Input(f"{drawer_id}-close", "n_clicks"),
        State(drawer_id, "opened"),
        prevent_initial_call=True
    )
    def handle_drawer_interaction(open_clicks, close_click, is_open):
        
        if not dash.ctx.triggered:
            return _no, _no, _no, _no, _no, _no, _no, _no, _no, _no
        
        trigger_id = dash.ctx.triggered_id
        
        if trigger_id == f"{drawer_id}-close":
            return False, _no, _no, _no, _no, _no, _no, _no, _no, _no
        
        if not any(open_clicks):
            return _no, _no, _no, _no, _no, _no, _no, _no, _no, _no
        
        widget_id = trigger_id.get("index")
        if not widget_id:
            return _no, _no, _no, _no, _no, _no, _no, _no, _no, _no
        
        widget = widget_registry.get(str(widget_id))
        if not widget:
            return _no, _no, _no, _no, _no, _no, _no, _no, _no, _no
        
        try:
            ctx = data_manager.get_screen(screen_id, use_cache=True, allow_stale=True)
            cfg = widget.strategy.get_card_config(ctx)
        except Exception as e:
            print(f"⚠️ Error en drawer para {widget_id}: {e}")
            cfg = {}

        title = str(cfg.get("title", "Análisis Detallado")) if cfg else "Sin Datos"
        subtitle = "Exploración profunda de métricas" if cfg else "Información no disponible"
        icon_name = str(cfg.get("icon", "tabler:alert-circle")) if cfg else "tabler:alert-circle"
        export_data = cfg.get("raw_data", []) if cfg else []
        
        try:
            tab_resumen = _build_resumen_tab(widget, ctx, cfg)
            tab_desglose = _build_desglose_tab(widget, ctx, cfg)
            tab_datos = _build_datos_tab(widget, ctx, cfg)
            tab_insights = _build_insights_tab(widget, ctx, cfg)
            tab_acciones = _build_acciones_tab(widget, ctx, cfg)
            
            return (
                True,
                title,
                subtitle,
                DashIconify(icon=icon_name, width=24),
                tab_resumen,
                tab_desglose,
                tab_datos,
                tab_insights,
                tab_acciones,
                export_data
            )
        except Exception as e:
            print(f"⚠️ Error construyendo tabs: {e}")
            error_content = dmc.Alert(
                title="Error al cargar análisis",
                color="red",
                children=f"No se pudo cargar el contenido: {str(e)}"
            )
            return True, title, "Error al cargar", DashIconify(icon="tabler:alert-triangle", width=24), error_content, error_content, error_content, error_content, error_content, []
    
    return handle_drawer_interaction
    @callback(
        Output(f"{drawer_id}-download", "data"),
        Input("drawer-export-csv", "n_clicks"),
        Input("drawer-export-excel", "n_clicks"),
        State(f"{drawer_id}-export-data", "data"),
        prevent_initial_call=True
    )
    def handle_drawer_export(n_csv, n_excel, stored_data):
        if not stored_data:
            return no_update
        
        trigger = dash.ctx.triggered_id
        
        try:
            df = pd.DataFrame(stored_data)
            if df.empty:
                return no_update
            
            if trigger == "drawer-export-csv":
                return dcc.send_data_frame(df.to_csv, "datos_exportados.csv", index=False)
            elif trigger == "drawer-export-excel":
                return dcc.send_data_frame(df.to_excel, "datos_exportados.xlsx", index=False, engine="openpyxl")
        except Exception as e:
            print(f"⚠️ Error en export: {e}")
            return no_update


def _build_resumen_tab(widget, ctx, cfg):
    
    fig = None
    if hasattr(widget.strategy, 'get_figure'):
        try:
            fig = widget.strategy.get_figure(ctx)
        except:
            pass
    
    if fig:
        graph = dcc.Graph(
            figure=fig,
            config={'displayModeBar': True, 'displaylogo': False},
            style={"height": "400px", "marginBottom": "1.5rem"}
        )
    else:
        graph = dmc.Alert(
            "No hay visualización disponible para este widget",
            color="gray",
            icon=DashIconify(icon="tabler:chart-off", width=20)
        )
    
    kpis = dmc.SimpleGrid(
        cols={"base": 1, "sm": 2, "md": 4},
        spacing="md",
        mb="lg",
        children=[
            _create_stat_card("Valor Actual", cfg.get("main_value", "---"), "blue", "tabler:currency-dollar"),
            _create_stat_card("vs Año Anterior", cfg.get("vs_last_year_delta_formatted", "---"), "green", "tabler:trending-up"),
            _create_stat_card("vs Meta", cfg.get("target_delta_formatted", "---"), "orange", "tabler:target"),
            _create_stat_card("YTD", cfg.get("ytd_formatted", "---"), "violet", "tabler:calendar-stats"),
        ]
    )
    
    summary_text = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        children=[
            dmc.Group(mb="sm", children=[
                DashIconify(icon="tabler:file-text", width=20, color=DesignSystem.BRAND[5]),
                dmc.Text("Resumen Ejecutivo", fw=600, size="sm")
            ]),
            dmc.Text(
                f"El indicador {cfg.get('title', 'actual')} presenta un valor de {cfg.get('main_value', '---')}. "
                f"Comparado con el período anterior, muestra una variación de {cfg.get('vs_last_year_delta_formatted', 'N/A')}. "
                f"La métrica se encuentra actualmente {'por encima' if (cfg.get('target_delta') or 0) > 0 else 'por debajo'} de la meta establecida.",
                size="sm",
                c="dimmed"
            )
        ]
    )
    
    return dmc.Stack(
        gap="md",
        children=[kpis, graph, summary_text]
    )


def _build_desglose_tab(widget, ctx, cfg):
    
    months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    current_year = [120, 135, 150, 145, 160, 175, 180, 190, 185, 200, 210, 220]
    previous_year = [100, 110, 130, 125, 140, 150, 155, 165, 160, 175, 180, 190]
    
    fig_comparison = go.Figure()
    fig_comparison.add_trace(go.Bar(
        x=months,
        y=current_year,
        name="2026",
        marker_color=DesignSystem.BRAND[5]
    ))
    fig_comparison.add_trace(go.Bar(
        x=months,
        y=previous_year,
        name="2025",
        marker_color=DesignSystem.SLATE[4]
    ))
    
    fig_comparison.update_layout(
        title="Comparativo Mensual",
        barmode='group',
        height=350,
        margin=dict(t=40, b=30, l=40, r=20),
        paper_bgcolor=DesignSystem.TRANSPARENT,
        plot_bgcolor=DesignSystem.TRANSPARENT,
        font=dict(size=11)
    )
    
    breakdown_cards = dmc.SimpleGrid(
        cols={"base": 1, "sm": 2, "md": 3},
        spacing="md",
        mb="lg",
        children=[
            _create_breakdown_card("Por Cliente", "42%", DesignSystem.BRAND[5], "tabler:users"),
            _create_breakdown_card("Por Región", "28%", DesignSystem.SUCCESS[5], "tabler:map-pin"),
            _create_breakdown_card("Por Producto", "30%", DesignSystem.WARNING[5], "tabler:package"),
        ]
    )
    
    return dmc.Stack(
        gap="lg",
        children=[
            breakdown_cards,
            dcc.Graph(figure=fig_comparison, config={'displaylogo': False}),
            dmc.Paper(
                p="md",
                radius="md",
                withBorder=True,
                children=[
                    dmc.Text("Análisis Dimensional", fw=600, mb="sm"),
                    dmc.Text(
                        "El desglose muestra que el mayor contribuyente es el segmento de clientes corporativos "
                        "con un 42% del total. La región norte ha mostrado el crecimiento más significativo "
                        "con un incremento del 18% respecto al año anterior.",
                        size="sm",
                        c="dimmed"
                    )
                ]
            )
        ]
    )


def _build_datos_tab(widget, ctx, cfg):
    import dash_ag_grid as dag
    
    raw_data = cfg.get("raw_data", [])
    
    if not raw_data or not isinstance(raw_data, list):
        return dmc.Alert(
            "No hay datos detallados disponibles para este indicador",
            color="blue",
            icon=DashIconify(icon="tabler:info-circle", width=20)
        )
    
    try:
        df = pd.DataFrame(raw_data)
        
        if df.empty:
            return dmc.Alert(
                "El conjunto de datos está vacío",
                color="yellow",
                icon=DashIconify(icon="tabler:alert-triangle", width=20)
            )
        
        row_data = df.to_dict("records")
        headers = list(df.columns)
        
        def _detect_type(col):
            for val in df[col].dropna().head(10):
                if isinstance(val, (int, float)):
                    return "agNumberColumnFilter"
                if isinstance(val, str):
                    clean = val.replace("$", "").replace(",", "").replace("%", "").strip()
                    try:
                        float(clean)
                        return "agNumberColumnFilter"
                    except (ValueError, TypeError):
                        pass
            return "agTextColumnFilter"
        
        column_defs = []
        for i, h in enumerate(headers):
            col_def = {
                "field": h,
                "headerName": h,
                "sortable": True,
                "filter": _detect_type(h),
                "resizable": True,
                "floatingFilter": True,
                "minWidth": 110,
                "flex": 1,
            }
            if i == 0:
                col_def["pinned"] = "left"
                col_def["flex"] = 0
                col_def["minWidth"] = 150
            column_defs.append(col_def)
        
        grid = dag.AgGrid(
            id="drawer-analyst-grid",
            rowData=row_data,
            columnDefs=column_defs,
            defaultColDef={
                "sortable": True,
                "filter": True,
                "resizable": True,
                "floatingFilter": True,
            },
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 50,
                "paginationPageSizeSelector": [25, 50, 100],
                "animateRows": True,
                "rowSelection": "single",
                "enableCellTextSelection": True,
                "domLayout": "normal",
            },
            style={"height": "100%", "width": "100%"},
            className="ag-theme-alpine",
        )
        
        stats_cards = dmc.SimpleGrid(
            cols={"base": 2, "md": 4},
            spacing="sm",
            mb="md",
            children=[
                _create_stat_card("Total Registros", len(df), "blue", "tabler:database"),
                _create_stat_card("Columnas", len(df.columns), "green", "tabler:columns"),
                _create_stat_card("Valores Únicos", int(df.nunique().sum()), "orange", "tabler:filter"),
                _create_stat_card("Registros Nulos", int(df.isnull().sum().sum()), "red", "tabler:alert-circle"),
            ]
        )
        
        return dmc.Stack(
            gap="md",
            children=[
                stats_cards,
                dmc.Group(
                    justify="space-between",
                    mb="xs",
                    children=[
                        dmc.Text("Datos Detallados", fw=600),
                        dmc.Badge(f"{len(df)} registros · Modo Analista", variant="light", color="violet")
                    ]
                ),
                html.Div(style={"height": "480px"}, children=grid)
            ]
        )
    
    except Exception as e:
        return dmc.Alert(
            f"Error al procesar datos: {str(e)}",
            color="red",
            icon=DashIconify(icon="tabler:alert-triangle", width=20)
        )


def _build_insights_tab(widget, ctx, cfg):
    
    insights = [
        {
            "type": "positive",
            "icon": "tabler:trending-up",
            "color": "green",
            "title": "Tendencia Positiva",
            "description": f"El indicador {cfg.get('title', 'actual')} muestra una tendencia alcista sostenida durante los últimos 3 meses con un crecimiento promedio del 8.5%."
        },
        {
            "type": "warning",
            "icon": "tabler:alert-triangle",
            "color": "orange",
            "title": "Área de Oportunidad",
            "description": "Se detecta volatilidad en el segmento de clientes pequeños. Considere estrategias de retención y fidelización para estabilizar este canal."
        },
        {
            "type": "neutral",
            "icon": "tabler:bulb",
            "color": "blue",
            "title": "Recomendación Estratégica",
            "description": "Basado en el patrón estacional identificado, se sugiere incrementar recursos en el Q4 para maximizar el aprovechamiento del pico de demanda."
        },
        {
            "type": "info",
            "icon": "tabler:chart-dots",
            "color": "violet",
            "title": "Patrón Detectado",
            "description": "Los datos muestran una correlación del 87% con las variables macroeconómicas del sector. Monitorear indicadores externos puede mejorar la precisión de proyecciones."
        }
    ]
    
    insight_cards = [
        dmc.Paper(
            p="md",
            radius="md",
            withBorder=True,
            mb="md",
            children=dmc.Stack(
                gap="sm",
                children=[
                    dmc.Group(
                        children=[
                            dmc.ThemeIcon(
                                DashIconify(icon=insight["icon"], width=20),
                                size="lg",
                                variant="light",
                                color=insight["color"],
                                radius="xl"
                            ),
                            dmc.Text(insight["title"], fw=600, size="sm")
                        ]
                    ),
                    dmc.Text(insight["description"], size="sm", c="dimmed")
                ]
            )
        )
        for insight in insights
    ]
    
    ai_banner = dmc.Paper(
        p="lg",
        radius="md",
        mb="lg",
        style={
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "color": "white"
        },
        children=dmc.Stack(
            gap="sm",
            children=[
                dmc.Group(
                    children=[
                        DashIconify(icon="tabler:robot", width=32),
                        dmc.Text("Análisis con IA", size="lg", fw=700, c="white")
                    ]
                ),
                dmc.Text(
                    "Estos insights han sido generados automáticamente mediante modelos de machine learning "
                    "entrenados con históricos de 3 años. La precisión actual del modelo es del 94.2%.",
                    size="sm",
                    c="white",
                    opacity=0.95
                ),
                dmc.Button(
                    "Solicitar Análisis Profundo",
                    leftSection=DashIconify(icon="tabler:sparkles", width=18),
                    variant="white",
                    color="dark",
                    size="sm",
                    mt="xs"
                )
            ]
        )
    )
    
    return dmc.Stack(
        gap="md",
        children=[ai_banner] + insight_cards
    )


def _build_acciones_tab(widget, ctx, cfg):
    
    export_section = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        children=[
            dmc.Group(mb="md", children=[
                DashIconify(icon="tabler:download", width=24, color=DesignSystem.BRAND[5]),
                dmc.Text("Exportar Datos", fw=600)
            ]),
            dmc.SimpleGrid(
                cols={"base": 1, "sm": 2},
                spacing="sm",
                children=[
                    dmc.Button(
                        "Descargar CSV",
                        id="drawer-export-csv",
                        leftSection=DashIconify(icon="tabler:file-type-csv", width=18),
                        variant="light",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Descargar Excel",
                        id="drawer-export-excel",
                        leftSection=DashIconify(icon="tabler:file-spreadsheet", width=18),
                        variant="light",
                        color="green",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Exportar PDF",
                        leftSection=DashIconify(icon="tabler:file-type-pdf", width=18),
                        variant="light",
                        color="red",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Copiar datos",
                        leftSection=DashIconify(icon="tabler:copy", width=18),
                        variant="light",
                        color="gray",
                        fullWidth=True
                    )
                ]
            )
        ]
    )
    
    share_section = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        mt="md",
        children=[
            dmc.Group(mb="md", children=[
                DashIconify(icon="tabler:share", width=24, color=DesignSystem.BRAND[5]),
                dmc.Text("Compartir Análisis", fw=600)
            ]),
            dmc.Stack(
                gap="sm",
                children=[
                    dmc.Button(
                        "Enviar por email",
                        leftSection=DashIconify(icon="tabler:mail", width=18),
                        variant="light",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Generar enlace compartible",
                        leftSection=DashIconify(icon="tabler:link", width=18),
                        variant="light",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Programar reporte",
                        leftSection=DashIconify(icon="tabler:calendar", width=18),
                        variant="light",
                        fullWidth=True
                    )
                ]
            )
        ]
    )
    
    alerts_section = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        mt="md",
        children=[
            dmc.Group(mb="md", children=[
                DashIconify(icon="tabler:bell", width=24, color=DesignSystem.BRAND[5]),
                dmc.Text("Configurar Alertas", fw=600)
            ]),
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        justify="space-between",
                        children=[
                            html.Div([
                                dmc.Text("Alerta si supera meta", size="sm", fw=500),
                                dmc.Text("Notificar cuando el valor exceda +10%", size="xs", c="dimmed")
                            ]),
                            dmc.Switch(checked=True, color="green")
                        ]
                    ),
                    dmc.Group(
                        justify="space-between",
                        children=[
                            html.Div([
                                dmc.Text("Alerta de caída", size="sm", fw=500),
                                dmc.Text("Notificar si disminuye más de 5%", size="xs", c="dimmed")
                            ]),
                            dmc.Switch(checked=False, color="red")
                        ]
                    ),
                    dmc.Group(
                        justify="space-between",
                        children=[
                            html.Div([
                                dmc.Text("Reporte semanal", size="sm", fw=500),
                                dmc.Text("Enviar resumen cada lunes", size="xs", c="dimmed")
                            ]),
                            dmc.Switch(checked=True, color="blue")
                        ]
                    )
                ]
            )
        ]
    )
    
    quick_actions = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        mt="md",
        children=[
            dmc.Group(mb="md", children=[
                DashIconify(icon="tabler:bolt", width=24, color=DesignSystem.BRAND[5]),
                dmc.Text("Acciones Rápidas", fw=600)
            ]),
            dmc.Stack(
                gap="sm",
                children=[
                    dmc.Button(
                        "Abrir análisis profundo en IA",
                        leftSection=DashIconify(icon="tabler:robot", width=18),
                        variant="gradient",
                        gradient={"from": "blue", "to": "purple"},
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Comparar con otros períodos",
                        leftSection=DashIconify(icon="tabler:calendar-stats", width=18),
                        variant="light",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Ver desglose detallado",
                        leftSection=DashIconify(icon="tabler:zoom-in", width=18),
                        variant="light",
                        fullWidth=True
                    )
                ]
            )
        ]
    )
    
    return dmc.Stack(
        gap="md",
        children=[export_section, share_section, alerts_section, quick_actions]
    )


def _create_stat_card(label, value, color, icon):
    return dmc.Paper(
        p="sm",
        radius="md",
        withBorder=True,
        children=dmc.Stack(
            gap="xs",
            children=[
                dmc.Group(
                    justify="space-between",
                    children=[
                        dmc.Text(label, size="xs", c="dimmed", fw=500),
                        DashIconify(icon=icon, width=16, color=DesignSystem.COLOR_MAP.get(color, color))
                    ]
                ),
                dmc.Text(str(value), size="lg", fw=700, c=color)
            ]
        )
    )


def _create_breakdown_card(label, percentage, color, icon):
    return dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        children=dmc.Stack(
            gap="sm",
            children=[
                dmc.Group(
                    justify="space-between",
                    children=[
                        dmc.Text(label, size="sm", fw=600),
                        DashIconify(icon=icon, width=20, color=color)
                    ]
                ),
                dmc.Text(percentage, size="xl", fw=700, c=color),
                dmc.Progress(value=float(percentage.replace('%', '')), color=color, h=8, radius="xl")
            ]
        )
    )