import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from settings.theme import DesignSystem, SemanticColors
from typing import Any
import math

# Umbral de altura para activar modo compacto
COMPACT_HEIGHT_THRESHOLD = 130

class SmartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def render(self, data_context: Any, mode: str = "auto"):
        try:
            config = self.strategy.get_card_config(data_context)
        except Exception as e:
            print(f"Error rendering widget {self.widget_id}: {e}")
            config = {"title": "Error", "value": "Err"}

        layout = getattr(self.strategy, 'layout', {})
        card_height = layout.get("height", 195)
        
        # Determinar si usar modo compacto
        is_compact = card_height < COMPACT_HEIGHT_THRESHOLD
        
        figure = None
        if hasattr(self.strategy, 'get_figure'):
            try: 
                figure = self.strategy.get_figure(data_context)
                if figure and hasattr(figure, 'data'):
                    has_data = False
                    for trace in figure.data:
                        for attr in ['x', 'y', 'values', 'value']:
                            val = getattr(trace, attr, None)
                            if isinstance(val, (list, tuple)) and len(val) > 0:
                                if any(v is not None for v in val):
                                    has_data = True
                                    break
                            elif isinstance(val, (int, float)) and not math.isnan(val):
                                has_data = True
                                break
                        if has_data: break
                    
                    if not has_data:
                        figure = None
            except: 
                figure = None

        val = config.get("main_value") or config.get("value")

        # Modo compacto: solo scalar, sin graficas
        if is_compact:
            return self._render_compact(config, card_height)

        if figure and val and not config.get("is_chart", False):
            return self._render_combined(config, figure, card_height)
        
        if config.get("is_chart") or (figure and not val):
            return self._render_chart_only(config, figure, card_height)

        return self._render_scalar(config, card_height)

    def _render_compact(self, config, height):
        """Renderizado compacto para cartas pequenas - diseno optimizado y responsivo"""
        title = config.get("title") or getattr(self.strategy, 'title', "")
        icon = config.get("icon") or getattr(self.strategy, 'icon', "tabler:chart-bar")
        color = config.get("color") or config.get("main_color") or getattr(self.strategy, 'color', "gray")
        hex_color = DesignSystem.COLOR_MAP.get(color, color) if not color.startswith("#") else color
        
        display_val = config.get("main_value") or config.get("value", "---")
        is_inverse = config.get("inverse", False)
        
        # Obtener delta para mostrar (solo uno, el mas relevante)
        delta_info = self._get_primary_delta(config, is_inverse)
        
        # Header compacto: titulo + icono en una linea
        header = dmc.Group(
            justify="space-between",
            align="center",
            w="100%",
            wrap="nowrap",
            gap="xs",
            children=[
                dmc.Text(
                    title, 
                    size="9px", 
                    c="dimmed", 
                    fw=600, 
                    tt="uppercase",
                    style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "flex": 1}
                ),
                dmc.ThemeIcon(
                    DashIconify(icon=icon, width=12),
                    variant="light",
                    color=hex_color,
                    size="xs",
                    radius="sm",
                    style={"flexShrink": 0}
                )
            ]
        )
        
        # Valor principal + delta en una linea
        value_section = dmc.Group(
            justify="space-between",
            align="center",
            w="100%",
            wrap="nowrap",
            gap="xs",
            children=[
                dmc.Text(
                    display_val,
                    fw=700,
                    fz="1.1rem",
                    lh="1",
                    c=SemanticColors.TEXT_MAIN,
                    style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "flex": 1}
                ),
                html.Div(delta_info, style={"flexShrink": 0}) if delta_info else html.Div()
            ]
        )
        
        # Footer compacto: solo comparacion ano anterior
        footer = self._build_compact_footer(config, is_inverse)
        
        return dmc.Paper(
            p="xs",
            radius="md",
            withBorder=True,
            shadow="sm",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT, "overflow": "hidden"},
            children=dmc.Stack(
                justify="space-between",
                h="100%",
                gap=2,
                children=[header, value_section, footer]
            )
        )

    def _get_primary_delta(self, config, is_inverse):
        """Obtiene el delta mas relevante para mostrar en modo compacto"""
        # Prioridad: vs ano anterior > meta > ytd
        delta = config.get("vs_last_year_delta")
        delta_fmt = config.get("vs_last_year_delta_formatted")
        
        if delta is None and config.get("target_delta") is not None:
            delta = config.get("target_delta")
            delta_fmt = config.get("target_delta_formatted")
        
        if delta is None and config.get("ytd_delta") is not None:
            delta = config.get("ytd_delta")
            delta_fmt = config.get("ytd_delta_formatted")
        
        if delta is None and config.get("trend") is not None:
            delta = config.get("trend")
            delta_fmt = None
        
        if delta is None:
            return None
        
        badge_text, badge_color = self._safe_format_delta(delta, delta_fmt)
        
        if is_inverse and badge_color in ("green", "red"):
            badge_color = "red" if badge_color == "green" else "green"
        
        if badge_text:
            return dmc.Badge(
                badge_text,
                color=badge_color,
                variant="light",
                size="xs",
                style={"padding": "0 3px", "height": "16px", "fontSize": "9px"}
            )
        return None

    def _build_compact_footer(self, config, is_inverse):
        """Footer compacto: solo una linea de comparacion"""
        label = config.get("label_prev_year", "vs Ant.")
        value = config.get("vs_last_year_formatted")
        
        if value in (None, "---", "N/A", ""):
            # Intentar con meta
            if config.get("target_formatted") and config.get("target_formatted") not in ("---", "N/A"):
                label = "Meta:"
                value = config.get("target_formatted")
            else:
                return html.Div(style={"height": "4px"})
        
        return dmc.Group(
            gap=3,
            wrap="nowrap",
            children=[
                dmc.Text(label, size="8px", c="dimmed"),
                dmc.Text(str(value), size="8px", fw=600, c="dark", style={"whiteSpace": "nowrap"})
            ]
        )

    def _render_scalar(self, config, height):
        """Renderizado estandar para cartas normales/grandes"""
        header = self._build_header(config)
        footer = self._build_footer(config, height)
        
        display_val = config.get("main_value") or config.get("value", "---")
        
        # Ajustar tamano de fuente segun altura
        font_size = "1.5rem" if height < 160 else "1.75rem" if height < 180 else "2rem"

        main_value = dmc.Center(
            style={"flex": 1, "flexDirection": "column", "overflow": "hidden"},
            children=[
                dmc.Text(
                    display_val,
                    fw=800,
                    fz=font_size,
                    lh="1",
                    ta="center",
                    c=SemanticColors.TEXT_MAIN,
                    style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "maxWidth": "100%"}
                ),
            ]
        )

        return dmc.Paper(
            p="sm",
            radius="md",
            withBorder=True,
            shadow="sm",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT, "overflow": "hidden"},
            children=dmc.Stack(
                justify="space-between",
                h="100%",
                gap=0,
                children=[header, main_value, footer]
            )
        )

    def _render_combined(self, config, figure, height):
        """Renderizado combinado: valor + grafica"""
        header = self._build_header(config)
        footer = self._build_footer(config, height)
        display_val = config.get("main_value") or config.get("value", "---")

        if figure:
            figure.update_layout(
                margin=dict(l=0, r=0, t=5, b=0),
                height=height - 80,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

        return dmc.Paper(
            p="sm",
            radius="md",
            withBorder=True,
            shadow="sm",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT, "overflow": "hidden"},
            children=dmc.Grid(
                gutter="xs",
                align="stretch",
                style={"height": "100%"},
                children=[
                    dmc.GridCol(
                        span=5,
                        children=dmc.Stack(
                            justify="space-between",
                            h="100%",
                            gap=0,
                            children=[
                                header,
                                dmc.Text(
                                    display_val, 
                                    fw=800, 
                                    fz="1.3rem", 
                                    lh=1, 
                                    mt=5,
                                    style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis"}
                                ),
                                footer
                            ]
                        )
                    ),
                    dmc.GridCol(
                        span=7,
                        children=html.Div(
                            style={"height": "100%", "width": "100%", "overflow": "hidden"},
                            children=[
                                dcc.Graph(
                                    figure=figure,
                                    config={'displayModeBar': False},
                                    style={"height": "100%", "width": "100%"}
                                )
                            ]
                        )
                    )
                ]
            )
        )

    def _render_chart_only(self, config, figure, height):
        """Renderizado solo grafica"""
        header = self._build_header(config)
        
        content = dmc.Center(
            dmc.Text("Sin datos", size="xs", c="dimmed"),
            style={"height": "100%"}
        )
        if figure:
            figure.update_layout(
                margin=dict(l=5, r=5, t=5, b=5),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            content = dcc.Graph(
                figure=figure,
                config={'displayModeBar': False, 'responsive': True},
                style={"height": "100%", "width": "100%"}
            )

        return dmc.Paper(
            p="sm",
            radius="md",
            withBorder=True,
            shadow="sm",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT, "overflow": "hidden"},
            children=dmc.Stack(
                h="100%",
                gap=0,
                children=[
                    header,
                    html.Div(
                        style={"flex": 1, "marginTop": "-5px", "minHeight": 0, "overflow": "hidden"},
                        children=content
                    )
                ]
            )
        )

    def _build_header(self, config):
        """Header estandar con responsividad"""
        title = config.get("title") or getattr(self.strategy, 'title', "")
        icon = config.get("icon") or getattr(self.strategy, 'icon', "tabler:chart-bar")
        color = config.get("color") or config.get("main_color") or getattr(self.strategy, 'color', "gray")
        hex_color = DesignSystem.COLOR_MAP.get(color, color) if not color.startswith("#") else color

        return dmc.Group(
            justify="space-between",
            align="flex-start",
            w="100%",
            mb=0,
            wrap="nowrap",
            gap="xs",
            children=[
                dmc.Text(
                    title, 
                    size="xs", 
                    c="dimmed", 
                    fw="bold", 
                    tt="uppercase",
                    style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "flex": 1}
                ),
                dmc.ThemeIcon(
                    DashIconify(icon=icon, width=16),
                    variant="light",
                    color=hex_color,
                    size="sm",
                    radius="md",
                    style={"flexShrink": 0}
                )
            ]
        )

    def _safe_to_float(self, val, default=0.0):
        """Convierte cualquier valor a float de forma segura"""
        if val is None:
            return default
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            clean = val.replace('%', '').replace('+', '').replace(',', '').replace('$', '').strip()
            try:
                return float(clean)
            except ValueError:
                return default
        return default

    def _safe_format_delta(self, delta, delta_fmt=None):
        """Formatea un delta de forma segura, manejando strings y numeros"""
        if delta is None:
            return None, "gray"
        
        if delta_fmt and isinstance(delta_fmt, str) and delta_fmt not in ("N/A", "---", ""):
            delta_num = self._safe_to_float(delta_fmt)
            if delta_num > 0:
                return delta_fmt, "green"
            elif delta_num < 0:
                return delta_fmt, "red"
            return delta_fmt, "gray"
        
        delta_num = self._safe_to_float(delta)
        
        if delta_num == 0:
            return "0%", "gray"
        
        badge_text = f"{delta_num:+.1f}%"
        badge_color = "green" if delta_num > 0 else "red"
        
        return badge_text, badge_color

    def _build_footer(self, config, height=200):
        """Footer adaptativo segun altura"""
        if config.get("extra_rows"):
            rows = []
            for item in config.get("extra_rows"):
                color = item.get("color", "dimmed")
                if color == "green": color = "green"
                elif color == "red": color = "red"
                elif color == "blue": color = "blue"
                rows.append(dmc.Group(
                    justify="space-between",
                    w="100%",
                    wrap="nowrap",
                    children=[
                        dmc.Text(item.get("label"), size="9px", c="dimmed", fw=500),
                        dmc.Text(item.get("value"), size="9px", fw=700, c=color)
                    ]
                ))
            return dmc.Card(
                p=4,
                radius="sm",
                bg="gray.0",
                children=dmc.Stack(gap=1, w="100%", children=rows)
            )
    
        footer_items = []
        is_inverse = config.get("inverse", False)
        
        # Para cartas medianas (140-180px), limitar a 2 items
        max_items = 2 if height < 180 else 3
        
        def make_row(label, value, delta=None, delta_fmt=None, is_inverse=False):
            if value in (None, "---", "N/A", ""):
                return None

            badge = None
            badge_text, badge_color = self._safe_format_delta(delta, delta_fmt)
            
            if is_inverse and badge_color in ("green", "red"):
                badge_color = "red" if badge_color == "green" else "green"

            if badge_text:
                badge = dmc.Badge(
                    badge_text,
                    color=badge_color,
                    variant="light",
                    size="xs",
                    style={"padding": "0 3px", "height": "14px", "fontSize": "8px"},
                )

            return dmc.Group(
                justify="space-between",
                w="100%",
                wrap="nowrap",
                gap="xs",
                children=[
                    dmc.Group(
                        gap=3,
                        wrap="nowrap",
                        style={"flex": 1, "overflow": "hidden"},
                        children=[
                            dmc.Text(label, size="9px", c="dimmed"),
                            dmc.Text(str(value), size="9px", fw=600, c="dark", style={"whiteSpace": "nowrap"}),
                        ]
                    ),
                    html.Div(badge, style={"flexShrink": 0}) if badge else html.Div(),
                ],
            )
        
        # Ano anterior
        prev_row = make_row(
            config.get("label_prev_year", "vs Ant:"), 
            config.get("vs_last_year_formatted"), 
            config.get("vs_last_year_delta"), 
            config.get("vs_last_year_delta_formatted"),
            is_inverse
        )
        if prev_row and len(footer_items) < max_items: 
            footer_items.append(prev_row)

        # Meta
        if config.get("target_formatted") and config.get("target_formatted") not in ("---", "N/A"):
            meta_row = make_row(
                "Meta:", 
                config.get("target_formatted"), 
                config.get("target_delta"),
                config.get("target_delta_formatted"),
                is_inverse
            )
            if meta_row and len(footer_items) < max_items: 
                footer_items.append(meta_row)

        # YTD
        ytd_row = make_row(
            "YTD:", 
            config.get("ytd_formatted"), 
            config.get("ytd_delta"), 
            config.get("ytd_delta_formatted"),
            is_inverse
        )
        if ytd_row and len(footer_items) < max_items: 
            footer_items.append(ytd_row)

        if not footer_items and config.get("trend") is not None:
            trend = config.get("trend")
            trend_txt = config.get("trend_text") or "vs Ant."
            
            badge_text, badge_color = self._safe_format_delta(trend)
            
            if is_inverse and badge_color in ("green", "red"):
                badge_color = "red" if badge_color == "green" else "green"

            return dmc.Group(
                gap=3,
                mt=8,
                children=[
                    dmc.Badge(badge_text, color=badge_color, variant="light", size="xs"),
                    dmc.Text(trend_txt, size="9px", c="dimmed")
                ]
            )

        if not footer_items: 
            return html.Div(style={"height": "8px"})

        return dmc.Stack(gap=2, w="100%", mt=4, children=footer_items)