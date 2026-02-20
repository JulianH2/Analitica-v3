import dash
from dash import html, callback, Input, Output, ALL, State, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
from design_system import DesignSystem as DS, Typography, ComponentSizes, Space, BadgeConfig, dmc as _dmc


def create_smart_modal(modal_id: str = "smart-modal"):
    return dmc.Modal(
        id=modal_id,
        size="xl",
        centered=True,
        padding="xl",
        radius="md",
        styles={"content": {"backgroundColor": "var(--mantine-color-body)"}},
        children=[
            html.Div(
                id=f"{modal_id}-container",
                children=[
                    html.Div(id=f"{modal_id}-header"),
                    html.Div(id=f"{modal_id}-content"),
                ],
            )
        ],
    )


def register_modal_callback(modal_id: str, widget_registry: dict, screen_id: str):
    from services.data_manager import data_manager

    @callback(
        Output(modal_id, "opened"),
        Output(modal_id, "title"),
        Output(f"{modal_id}-header", "children"),
        Output(f"{modal_id}-content", "children"),
        Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_modal_interaction(n_clicks):
        if not dash.ctx.triggered or not any(n_clicks):
            return no_update, no_update, no_update, no_update

        triggered = dash.ctx.triggered_id
        widget_id = triggered.get("index") if isinstance(triggered, dict) else None
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
                children=f"No se pudo cargar el contenido: {str(e)}",
            )
            return True, "Error", html.Div(), error_content

    return handle_modal_interaction


def _build_modal_header(cfg, icon, color):
    color_hex = DS.COLOR_MAP.get(color, DS.CHART_BLUE)
    gradient_start = color_hex
    gradient_end = _darken_color(color_hex, 20)

    return dmc.Paper(
        p="md",
        radius="md",
        mb="lg",
        style={
            "background": f"linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%)",
            "color": "white",
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
                            color=color,
                        ),
                        html.Div(
                            [
                                dmc.Text(
                                    cfg.get("title", "Detalle"),
                                    size="xl",
                                    fw=_dmc(Typography.WEIGHT_BOLD),
                                    c=_dmc("white"),
                                ),
                                dmc.Text(
                                    "Análisis rápido",
                                    size="sm",
                                    c=_dmc("white"),
                                    opacity=_dmc(0.9),
                                ),
                            ]
                        ),
                    ],
                ),
                dmc.Group(
                    gap="xs",
                    children=[
                        dmc.Badge(
                            "Actualizado ahora",
                            variant="white",
                            size="lg",
                            leftSection=DashIconify(icon="tabler:refresh", width=14),
                            styles={"root": {"fontSize": f"{Typography.XS}px"}},
                        )
                    ],
                ),
            ],
        ),
    )


def _build_modal_content(widget, ctx, cfg):
    main_section = dmc.SimpleGrid(
        cols=_dmc({"base": 1, "sm": 2, "md": 4}),
        spacing="md",
        mb="xl",
        children=[
            _create_metric_card(
                label="Valor Actual",
                value=cfg.get("main_value", "---"),
                icon="tabler:currency-dollar",
                color="blue",
                size="xl",
            ),
            _create_metric_card(
                label="vs Año Anterior",
                value=cfg.get("vs_last_year_formatted", "---"),
                delta=cfg.get("vs_last_year_delta_formatted", ""),
                icon="tabler:calendar",
                color="green",
            ),
            _create_metric_card(
                label="Meta",
                value=cfg.get("target_formatted", "---"),
                delta=cfg.get("target_delta_formatted", ""),
                icon="tabler:target",
                color="orange",
            ),
            _create_metric_card(
                label="YTD",
                value=cfg.get("ytd_formatted", "---"),
                delta=cfg.get("ytd_delta_formatted", ""),
                icon="tabler:calendar-stats",
                color="violet",
            ),
        ],
    )

    trend_section = None
    if hasattr(widget.strategy, "get_figure"):
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
                                DashIconify(
                                    icon="tabler:chart-line",
                                    width=24,
                                    color=DS.CHART_BLUE,
                                ),
                                dmc.Text(
                                    "Tendencia Histórica",
                                    fw=_dmc(Typography.WEIGHT_SEMIBOLD),
                                    size="lg",
                                ),
                            ],
                        ),
                        dcc.Graph(
                            figure=fig,
                            config={"displayModeBar": True, "displaylogo": False},
                            style={"height": "300px"},
                        ),
                    ],
                )
        except:
            pass

    insights_section = _build_insights_section(cfg)
    actions_section = _build_actions_section()

    return dmc.Stack(
        gap="lg",
        children=[
            main_section,
            trend_section if trend_section else html.Div(),
            insights_section,
            actions_section,
        ],
    )


def _create_metric_card(label, value, icon, color, delta=None, size="md"):
    color_hex = DS.COLOR_MAP.get(color, color)
    badge_component = html.Div(style={"height": "20px"})

    if delta and delta not in ("", "---", "N/A"):
        try:
            clean = str(delta).replace("%", "").replace("+", "").replace(",", "").strip()
            delta_num = float(clean)
            badge_config = BadgeConfig.get_comparison_badge(delta_num)

            badge_component = dmc.Badge(
                badge_config["label"],
                variant="light",
                size="sm",
                styles={
                    "root": {
                        "backgroundColor": badge_config["background"],
                        "color": badge_config["text"],
                        "fontSize": f"{Typography.BADGE}px",
                        "fontWeight": Typography.WEIGHT_SEMIBOLD,
                    }
                },
            )
        except:
            pass

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
                        dmc.Text(
                            label,
                            size="xs",
                            c=_dmc("dimmed"),
                            fw=_dmc(Typography.WEIGHT_SEMIBOLD),
                            tt="uppercase",
                            style={"fontSize": f"{Typography.XS}px"},
                        ),
                        DashIconify(
                            icon=icon,
                            width=ComponentSizes.ICON_LG,
                            color=color_hex,
                        ),
                    ],
                ),
                dmc.Text(
                    str(value),
                    size=_dmc(size),
                    fw=_dmc(Typography.WEIGHT_BOLD),
                    c=color,
                    style={
                        "lineHeight": Typography.LH_TIGHT,
                        "fontSize": f"{Typography.KPI_LARGE if size == 'xl' else Typography.KPI_MEDIUM}px",
                    },
                ),
                badge_component,
            ],
        ),
    )


def _build_insights_section(cfg):
    return dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        mb="lg",
        children=[
            dmc.Group(
                mb="md",
                children=[
                    DashIconify(icon="tabler:bulb", width=24, color=DS.CHART_BLUE),
                    dmc.Text(
                        "Análisis Rápido",
                        fw=_dmc(Typography.WEIGHT_SEMIBOLD),
                        size="lg",
                    ),
                ],
            ),
            dmc.Stack(
                gap="sm",
                children=[
                    _create_insight_item(
                        icon="tabler:trending-up",
                        color="green",
                        text=f"El indicador {cfg.get('title', 'actual')} muestra desempeño {_get_performance_label(cfg)}",
                    ),
                    _create_insight_item(
                        icon="tabler:calendar-check",
                        color="blue",
                        text=_get_comparison_text(cfg),
                    ),
                    _create_insight_item(
                        icon="tabler:target",
                        color="orange",
                        text=_get_target_text(cfg),
                    ),
                ],
            ),
        ],
    )


def _create_insight_item(icon, color, text):
    return dmc.Group(
        gap="sm",
        children=[
            dmc.ThemeIcon(
                DashIconify(icon=icon, width=16),
                size="md",
                variant="light",
                color=color,
                radius="xl",
            ),
            dmc.Text(text, size="sm", style={"fontSize": f"{Typography.SM}px"}),
        ],
    )


def _build_actions_section():
    return dmc.Paper(
        p="md",
        radius="md",
        withBorder=True,
        children=[
            dmc.Group(
                mb="md",
                children=[
                    DashIconify(icon="tabler:bolt", width=24, color=DS.CHART_BLUE),
                    dmc.Text(
                        "Acciones Rápidas",
                        fw=_dmc(Typography.WEIGHT_SEMIBOLD),
                        size="lg",
                    ),
                ],
            ),
            dmc.Group(
                gap="sm",
                children=[
                    dmc.Button(
                        "Análisis Profundo",
                        leftSection=DashIconify(icon="tabler:zoom-in", width=18),
                        variant="light",
                        color="blue",
                        size="sm",
                    ),
                    dmc.Button(
                        "Exportar Datos",
                        leftSection=DashIconify(icon="tabler:download", width=18),
                        variant="light",
                        color="green",
                        size="sm",
                    ),
                    dmc.Button(
                        "Compartir",
                        leftSection=DashIconify(icon="tabler:share", width=18),
                        variant="light",
                        color="gray",
                        size="sm",
                    ),
                    dmc.Button(
                        "Configurar Alerta",
                        leftSection=DashIconify(icon="tabler:bell", width=18),
                        variant="light",
                        color="orange",
                        size="sm",
                    ),
                ],
            ),
        ],
    )


def _darken_color(hex_color: str, percent: int) -> str:
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    factor = (100 - percent) / 100
    darkened = tuple(int(c * factor) for c in rgb)
    return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


def _get_performance_label(cfg):
    delta = cfg.get("vs_last_year_delta", 0)
    try:
        delta_num = float(delta) if delta else 0
        if delta_num > 15:
            return "excepcional (+{:.1f}%)".format(delta_num)
        if delta_num > 5:
            return "muy positivo (+{:.1f}%)".format(delta_num)
        if delta_num > 0:
            return "positivo (+{:.1f}%)".format(delta_num)
        if delta_num > -5:
            return "estable ({:.1f}%)".format(delta_num)
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
            delta_clean = str(delta).replace("%", "").replace("+", "").strip()
            delta_num = float(delta_clean)
            if delta_num > 0:
                return f"Meta: {target} - Superada en {delta}"
            if delta_num < 0:
                return f"Meta: {target} - Faltante: {delta}"
            return f"Meta: {target} - Cumplida exactamente"
        except:
            return f"Meta establecida: {target}"
    return "Meta no definida para este período"