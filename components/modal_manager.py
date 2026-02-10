import dash
from dash import html, callback, Input, Output, ALL, State, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
from settings.theme import DesignSystem


def create_smart_modal(modal_id: str = "smart-modal"):
    return dmc.Modal(
        id=modal_id,
        size="xl",
        centered=True,
        padding="xl",
        radius="md",
        children=[
            html.Div(
                id=f"{modal_id}-container",
                children=[
                    html.Div(id=f"{modal_id}-header"),
                    html.Div(id=f"{modal_id}-content")
                ]
            )
        ]
    )


def register_modal_callback(modal_id: str, widget_registry: dict, screen_id: str):
    from services.data_manager import data_manager

    @callback(
        Output(modal_id, "opened"),
        Output(modal_id, "title"),
        Output(f"{modal_id}-header", "children"),
        Output(f"{modal_id}-content", "children"),
        Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def handle_modal_interaction(n_clicks):
        if not dash.ctx.triggered or not any(n_clicks):
            return no_update, no_update, no_update, no_update
        widget_id = dash.ctx.triggered_id.get("index")
        if not widget_id:
            return no_update, no_update, no_update, no_update
        widget = widget_registry.get(str(widget_id))
        if not widget:
            return no_update, no_update, no_update, no_update
        ctx = data_manager.get_screen(screen_id, use_cache=True, allow_stale=True)
        try:
            cfg = widget.strategy.get_card_config(ctx)
            title = cfg.get("title", "Detalle")
            icon = cfg.get("icon", "tabler:chart-bar")
            color = cfg.get("color", "blue")
            header = _build_modal_header(cfg, icon, color)
            content = _build_modal_content(widget, ctx, cfg)

            return True, "", header, content

        except Exception as e:
            error_content = dmc.Alert(
                title="Error al cargar detalle",
                color="red",
                icon=DashIconify(icon="tabler:alert-triangle", width=20),
                children=f"No se pudo cargar el contenido: {str(e)}"
            )
            return True, "Error", html.Div(), error_content

    return handle_modal_interaction


def _build_modal_header(cfg, icon, color):
    return dmc.Paper(
        p="md",
        radius="md",
        mb="lg",
        style={
            "background": f"linear-gradient(135deg, {DesignSystem.COLOR_MAP.get(color, DesignSystem.BRAND[5])} 0%, {DesignSystem.COLOR_MAP.get(color, DesignSystem.BRAND[7])} 100%)",
            "color": "white"
        },
        children=dmc.Group(
            justify="space-between",
            children=[
                dmc.Group(
                    gap="md",
                    children=[
                        dmc.ThemeIcon(
                            DashIconify(icon=icon, width=32),
                            size="xl",
                            radius="md",
                            variant="white",
                            color=color
                        ),
                        html.Div([
                            dmc.Text(cfg.get("title", "Detalle"), size="xl", fw=700, c="white"),
                            dmc.Text("Análisis rápido", size="sm", c="white", opacity=0.9)
                        ])
                    ]
                ),
                dmc.Group(
                    gap="xs",
                    children=[
                        dmc.Badge(
                            "Actualizado ahora",
                            variant="white",
                            size="lg",
                            leftSection=DashIconify(icon="tabler:refresh", width=14)
                        )
                    ]
                )
            ]
        )
    )


def _build_modal_content(widget, ctx, cfg):
    main_section = dmc.SimpleGrid(
        cols={"base": 1, "sm": 2, "md": 4},
        spacing="md",
        mb="xl",
        children=[
            _create_metric_card(
                label="Valor Actual",
                value=cfg.get("main_value", "---"),
                icon="tabler:currency-dollar",
                color="blue",
                size="xl"
            ),
            _create_metric_card(
                label="vs Año Anterior",
                value=cfg.get("vs_last_year_formatted", "---"),
                delta=cfg.get("vs_last_year_delta_formatted", ""),
                icon="tabler:calendar",
                color="green"
            ),
            _create_metric_card(
                label="Meta",
                value=cfg.get("target_formatted", "---"),
                delta=cfg.get("target_delta_formatted", ""),
                icon="tabler:target",
                color="orange"
            ),
            _create_metric_card(
                label="YTD",
                value=cfg.get("ytd_formatted", "---"),
                delta=cfg.get("ytd_delta_formatted", ""),
                icon="tabler:calendar-stats",
                color="violet"
            )
        ]
    )
    trend_section = None
    if hasattr(widget.strategy, 'get_figure'):
        try:
            fig = widget.strategy.get_figure(ctx)
            if fig:
                trend_section = dmc.Paper(
                    p="md",
                    radius="md",
                    withBorder=True,
                    mb="lg",
                    children=[
                        dmc.Group(
                            mb="md",
                            children=[
                                DashIconify(icon="tabler:chart-line", width=24, color=DesignSystem.BRAND[5]),
                                dmc.Text("Tendencia Histórica", fw=600, size="lg")
                            ]
                        ),
                        dcc.Graph(
                            figure=fig,
                            config={'displayModeBar': True, 'displaylogo': False},
                            style={"height": "300px"}
                        )
                    ]
                )
        except:
            pass
    insights_section = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        mb="lg",
        children=[
            dmc.Group(
                mb="md",
                children=[
                    DashIconify(icon="tabler:bulb", width=24, color=DesignSystem.BRAND[5]),
                    dmc.Text("Análisis Rápido", fw=600, size="lg")
                ]
            ),
            dmc.Stack(
                gap="sm",
                children=[
                    dmc.Group(
                        gap="sm",
                        children=[
                            dmc.ThemeIcon(
                                DashIconify(icon="tabler:trending-up", width=16),
                                size="md",
                                variant="light",
                                color="green",
                                radius="xl"
                            ),
                            dmc.Text(
                                f"El indicador {cfg.get('title', 'actual')} muestra desempeño {_get_performance_label(cfg)}",
                                size="sm"
                            )
                        ]
                    ),
                    dmc.Group(
                        gap="sm",
                        children=[
                            dmc.ThemeIcon(
                                DashIconify(icon="tabler:calendar-check", width=16),
                                size="md",
                                variant="light",
                                color="blue",
                                radius="xl"
                            ),
                            dmc.Text(
                                _get_comparison_text(cfg),
                                size="sm"
                            )
                        ]
                    ),
                    dmc.Group(
                        gap="sm",
                        children=[
                            dmc.ThemeIcon(
                                DashIconify(icon="tabler:target", width=16),
                                size="md",
                                variant="light",
                                color="orange",
                                radius="xl"
                            ),
                            dmc.Text(
                                _get_target_text(cfg),
                                size="sm"
                            )
                        ]
                    )
                ]
            )
        ]
    )
    actions_section = dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        children=[
            dmc.Group(
                mb="md",
                children=[
                    DashIconify(icon="tabler:bolt", width=24, color=DesignSystem.BRAND[5]),
                    dmc.Text("Acciones Rápidas", fw=600, size="lg")
                ]
            ),
            dmc.Group(
                gap="sm",
                children=[
                    dmc.Button(
                        "Análisis Profundo",
                        leftSection=DashIconify(icon="tabler:zoom-in", width=18),
                        variant="light",
                        color="blue"
                    ),
                    dmc.Button(
                        "Exportar Datos",
                        leftSection=DashIconify(icon="tabler:download", width=18),
                        variant="light",
                        color="green"
                    ),
                    dmc.Button(
                        "Compartir",
                        leftSection=DashIconify(icon="tabler:share", width=18),
                        variant="light",
                        color="gray"
                    ),
                    dmc.Button(
                        "Configurar Alerta",
                        leftSection=DashIconify(icon="tabler:bell", width=18),
                        variant="light",
                        color="orange"
                    )
                ]
            )
        ]
    )
    return dmc.Stack(
        gap="lg",
        children=[
            main_section,
            trend_section if trend_section else html.Div(),
            insights_section,
            actions_section
        ]
    )


def _create_metric_card(label, value, icon, color, delta=None, size="md"):
    return dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        children=dmc.Stack(
            gap="xs",
            children=[
                dmc.Group(
                    justify="space-between",
                    children=[
                        dmc.Text(label, size="xs", c="dimmed", fw=600, tt="uppercase"),
                        DashIconify(
                            icon=icon,
                            width=20,
                            color=DesignSystem.COLOR_MAP.get(color, color)
                        )
                    ]
                ),
                dmc.Text(
                    str(value),
                    size=size,
                    fw=700,
                    c=color,
                    style={"lineHeight": 1.2}
                ),
                html.Div(
                    dmc.Badge(
                        delta,
                        variant="light",
                        color=_get_delta_color(delta),
                        size="sm"
                    ) if delta and delta not in ("", "---", "N/A") else html.Div(style={"height": "20px"})
                )
            ]
        )
    )


def _get_delta_color(delta_str):
    if not delta_str or delta_str in ("", "---", "N/A"):
        return "gray"
    clean = str(delta_str).replace('%', '').replace('+', '').replace(',', '').strip()
    try:
        val = float(clean)
        return "green" if val > 0 else "red" if val < 0 else "gray"
    except:
        return "gray"


def _get_performance_label(cfg):
    delta = cfg.get("vs_last_year_delta", 0)
    try:
        delta_num = float(delta) if delta else 0
        if delta_num > 15:
            return "excepcional (+{:.1f}%)".format(delta_num)
        elif delta_num > 5:
            return "muy positivo (+{:.1f}%)".format(delta_num)
        elif delta_num > 0:
            return "positivo (+{:.1f}%)".format(delta_num)
        elif delta_num > -5:
            return "estable ({:.1f}%)".format(delta_num)
        else:
            return "por debajo de expectativas ({:.1f}%)".format(delta_num)
    except:
        return "estable"


def _get_comparison_text(cfg):
    prev_value = cfg.get("vs_last_year_formatted", "N/A")
    delta = cfg.get("vs_last_year_delta_formatted", "N/A")
    
    if prev_value != "N/A" and delta != "N/A":
        return f"Año anterior: {prev_value} (variación: {delta})"
    return "Comparación con año anterior no disponible"


def _get_target_text(cfg):
    target = cfg.get("target_formatted", "N/A")
    delta = cfg.get("target_delta_formatted", "N/A")
    
    if target != "N/A" and delta != "N/A":
        try:
            delta_clean = str(delta).replace('%', '').replace('+', '').strip()
            delta_num = float(delta_clean)
            if delta_num > 0:
                return f"Meta: {target} - Superada en {delta}"
            elif delta_num < 0:
                return f"Meta: {target} - Faltante: {delta}"
            else:
                return f"Meta: {target} - Cumplida exactamente"
        except:
            return f"Meta establecida: {target}"
    return "Meta no definida para este período"