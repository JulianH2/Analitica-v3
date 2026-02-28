import calendar
import datetime
import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from design_system import (
    DesignSystem as DS,
    Colors,
    Typography,
    ComponentSizes,
    GaugeConfig,
    BadgeConfig,
    ChartColors,
    SemanticColors,
    Space,
    Shadows,
    dmc as _dmc,
)
from components.card_wrapper import make_card
from services.time_service import TimeService
from utils.helpers import format_value
from typing import Any
import math
from flask import session

_ts = TimeService()


COMPACT_HEIGHT_THRESHOLD = 130


class SmartWidget:
    def __init__(self, widget_id: str, strategy: Any, height: int | None = None):
        self.widget_id = widget_id
        self.strategy = strategy
        self._height = height

    def render(self, data_context: Any, mode: str = "auto", theme: str = "dark"):
        try:
            config = self.strategy.get_card_config(data_context)
        except Exception as e:
            print(f"Error rendering widget {self.widget_id}: {e}")
            config = {"title": "Error", "value": "Err"}

        layout = getattr(self.strategy, "layout", {})
        card_height = self._height or layout.get("height", 195)

        is_compact = card_height < COMPACT_HEIGHT_THRESHOLD
        if theme == "auto":
            theme = session.get("theme", "dark")

        figure = None
        if hasattr(self.strategy, "get_figure"):
            try:
                figure = self.strategy.get_figure(data_context, theme=theme)
                if figure and hasattr(figure, "data"):
                    has_data = False
                    for trace in figure.data:
                        for attr in ["x", "y", "values", "value"]:
                            val = getattr(trace, attr, None)
                            if isinstance(val, (list, tuple)) and val:
                                if any(v is not None for v in val):
                                    has_data = True
                                    break
                            elif isinstance(val, (int, float)) and not math.isnan(val):
                                has_data = True
                                break
                        if has_data:
                            break
                    if not has_data:
                        figure = None
            except:
                figure = None

        val = config.get("main_value") or config.get("value")
        is_no_data = not figure and val in (None, "---", "N/A", "")

        if is_compact:
            return self._render_compact(config, card_height, theme)

        if is_no_data and not config.get("is_chart"):
            return self._render_no_data(config, card_height, theme)

        if figure and val and not config.get("is_chart", False):
            return self._render_combined(config, figure, card_height, theme)

        if config.get("is_chart") or (figure and not val):
            return self._render_chart_only(config, figure, card_height, theme)

        return self._render_scalar(config, card_height, theme)

    def _render_chart_only(self, config, figure, height, theme):
        header = self._build_header(config)
        is_dark = theme == "dark"

        if figure is None:
            content = dmc.Center(
                dmc.Stack(
                    gap=5,
                    align="center",
                    children=[
                        DashIconify(icon="tabler:chart-off", width=32, color="gray"),
                        dmc.Text("Sin datos disponibles", size="xs", c=_dmc("dimmed"))
                    ],
                ),
                style={"flex": 1},
            )
        else:
            _bg = Colors.BG_DARK_CARD if is_dark else Colors.BG_LIGHT_CARD
            figure.update_layout(
                template="zam_dark" if is_dark else "zam_light",
                font=dict(color=Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT),
                paper_bgcolor=_bg,
                plot_bgcolor=_bg,
                height=None,
            )

            content = dcc.Graph(
                figure=figure,
                config={"displayModeBar": False, "responsive": True},
                style={"height": "100%", "width": "100%"},
            )

        _HEADER_H = 38
        chart_h = (height - _HEADER_H) if isinstance(height, int) else None
        chart_h_style = f"{chart_h}px" if chart_h else "calc(100% - 38px)"

        return make_card(
            children=dmc.Stack(
                h="100%",
                gap=0,
                children=[
                    header,
                    html.Div(
                        style={
                            "height": chart_h_style,
                            "marginTop": "-5px",
                            "overflow": "hidden",
                        },
                        children=content,
                    ),
                ],
            ),
            height=height,
            is_dark=is_dark,
            p="sm", # type: ignore
        )

    def _render_no_data(self, config, height, theme):
        is_dark = theme == "dark"
        header = self._build_header(config)
        muted = Colors.TEXT_DARK_SECONDARY if is_dark else Colors.TEXT_LIGHT_SECONDARY

        empty = dmc.Center(
            dmc.Stack(
                gap=4,
                align="center",
                children=[
                    DashIconify(icon="tabler:database-off", width=22, color=muted),
                    dmc.Text(
                        "Sin datos",
                        size=_dmc("10px"),
                        fw=_dmc(500),
                        style={"color": muted},
                    ),
                ],
            ),
            style={"flex": 1, "opacity": 0.65},
        )

        return make_card(
            children=dmc.Stack(
                h="100%",
                gap=4,
                children=[header, empty],
            ),
            height=height,
            is_dark=is_dark,
            p="sm",
        )

    def _render_compact(self, config, height, theme="light"):
        main_text_color = Colors.TEXT_DARK if theme == "dark" else Colors.TEXT_LIGHT
        title = config.get("title") or getattr(self.strategy, "title", "")
        icon = config.get("icon") or getattr(self.strategy, "icon", "tabler:chart-bar")
        color = (
            config.get("color")
            or config.get("main_color")
            or getattr(self.strategy, "color", "gray")
        )
        hex_color = DS.COLOR_MAP.get(color, color) if not color.startswith("#") else color
    
        display_val = config.get("main_value") or config.get("value", "---")
        is_inverse = config.get("inverse", False)
    
        delta_info = self._get_primary_delta(config, is_inverse)
        has_detail = getattr(self.strategy, "has_detail", False)
    
        header = dmc.Group(
            justify="space-between",
            align="center",
            w="100%",
            wrap="nowrap",
            gap="xs",
            children=[
                dmc.Text(
                    title,
                    size=_dmc("9px"),
                    c=_dmc("dimmed"),
                    fw=_dmc(600),
                    tt="uppercase",
                    style={
                        "whiteSpace": "nowrap",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "flex": 1,
                    },
                ),
                dmc.ThemeIcon(
                    DashIconify(icon=icon, width=12),
                    variant="light",
                    color=_dmc(hex_color),
                    size="xs",
                    radius="sm",
                ),
            ],
        )
    
        value_section = dmc.Group(
            justify="space-between",
            align="center",
            w="100%",
            wrap="nowrap",
            gap="xs",
            children=[
                dmc.Text(
                    display_val,
                    fw=_dmc(700),
                    fz=_dmc("1rem"),
                    lh=1,
                    c=_dmc(main_text_color),
                    style={
                        "whiteSpace": "nowrap",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "flex": 1,
                    },
                ),
                delta_info if delta_info else html.Div(),
            ],
        )
    
        compact_footer = self._build_compact_footer(config, is_inverse, theme)

        return make_card(
            children=dmc.Stack(
                justify="flex-start",
                h="100%",
                gap=4,
                children=[header, value_section, compact_footer],
            ),
            height=height,
            is_dark=theme == "dark",
            p="xs",
        )

    def _render_scalar(self, config, height, theme):
        main_text_color = Colors.TEXT_DARK if theme == "dark" else Colors.TEXT_LIGHT
        header = self._build_header(config)

        display_val = config.get("main_value") or config.get("value", "---")

        value_section = dmc.Text(
            display_val,
            fw=_dmc(700),
            size=_dmc("1.5rem"),
            lh=1,
            c=_dmc(main_text_color),
            style={
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
        )

        footer = self._build_footer(config, height, theme)

        return make_card(
            children=dmc.Stack(
                justify="flex-start",
                h="100%",
                gap=6,
                children=[header, value_section, footer],
            ),
            height=height,
            is_dark=theme == "dark",
            p="sm",
        )

    def _render_combined(self, config, figure, height, theme):
        is_dark = theme == "dark"
        main_text_color = Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT
        header = self._build_header(config)

        display_val = config.get("main_value") or config.get("value", "---")

        value_section = dmc.Text(
            display_val,
            fw=_dmc(700),
            size=_dmc("1.6rem"),
            lh=1,
            c=_dmc(main_text_color),
            style={
                "whiteSpace": "nowrap",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
        )

        has_needle = any(
            getattr(s, "type", "") == "path"
            for s in (figure.layout.shapes or [])
        )

        figure.update_traces(
            selector=dict(type="indicator"),
            mode="gauge",
        )

        if is_dark and has_needle:
            needle_color = Colors.TEXT_DARK
            hub_color = Colors.BG_DARK
            for shape in (figure.layout.shapes or []):
                if getattr(shape, "type", "") == "path":
                    shape.fillcolor = needle_color
                    shape.line = dict(color=needle_color, width=0)
                elif getattr(shape, "type", "") == "circle":
                    if getattr(shape, "fillcolor", "") == "#1a1a2e":
                        shape.fillcolor = needle_color
                        shape.line = dict(color=hub_color, width=2)

        figure.update_layout(
            template="zam_dark" if is_dark else "zam_light",
            font=dict(color=main_text_color),
        )

        _RESERVED = 200
        gauge_height = max(90, height - _RESERVED)

        figure.update_traces(
            selector=dict(type="indicator"),
            domain={"x": [0.30, 0.70], "y": [0.0, 1.0]},
        )

        _bg = Colors.BG_DARK_CARD if is_dark else Colors.BG_LIGHT_CARD
        figure.update_layout(
            height=gauge_height,
            margin=dict(t=30, b=5, l=5, r=5),
            paper_bgcolor=_bg,
            plot_bgcolor=_bg,
        )

        chart = dcc.Graph(
            id={"type": "interactive-graph", "index": self.widget_id},
            figure=figure,
            config={"displayModeBar": False},
            style={
                "height": f"{gauge_height}px",
                "width": "100%",
                "overflow": "visible",
                "flexShrink": 0,
            },
        )

        footer = self._build_footer(config, height, theme)

        return make_card(
            children=dmc.Stack(
                h="100%",
                gap=3,
                justify="space-between",
                children=[header, value_section, chart, footer],
            ),
            height=height,
            is_dark=is_dark,
            overflow="visible",
            p="md",
        )

    def _build_header(self, config):
        title = config.get("title") or getattr(self.strategy, "title", "")
        icon = config.get("icon") or getattr(self.strategy, "icon", "tabler:chart-bar")
        color = config.get("color") or "gray"
        hex_color = DS.COLOR_MAP.get(color, color) if not color.startswith("#") else color
        has_detail = getattr(self.strategy, "has_detail", False)

        return dmc.Group(
            justify="space-between",
            align="center",
            w="100%",
            mb=8,
            wrap="nowrap",
            children=[
                dmc.Group(
                    gap=8,
                    wrap="nowrap",
                    children=[
                        DashIconify(icon=icon, width=18, color=hex_color),
                        dmc.Text(
                            title,
                            size=_dmc("10px"),
                            c=_dmc("dimmed"),
                            fw=_dmc(700),
                            tt="uppercase",
                            style={"whiteSpace": "nowrap"},
                        ),
                    ],
                ),
                dmc.ActionIcon(
                    DashIconify(icon="tabler:layers-linked", width=14),
                    variant="subtle",
                    color="gray",
                    size="xs",
                    id={"type": "open-smart-drawer", "index": self.widget_id},
                )
                if has_detail
                else html.Div(),
            ],
        )

    def _get_primary_delta(self, config, is_inverse):
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

        if is_inverse and badge_color in (Colors.POSITIVE, Colors.NEGATIVE):
            badge_color = Colors.NEGATIVE if badge_color == Colors.POSITIVE else Colors.POSITIVE

        if badge_text:
            return dmc.Badge(
                badge_text,
                color=_dmc(badge_color),
                variant="light",
                size="xs",
                style={"padding": "0 3px", "height": "16px", "fontSize": "9px"},
            )
        return None

    def _daily_meta_str(self, config) -> str | None:
        """Returns formatted 'meta al día' = target_raw / days_in_month * current_day, or None."""
        raw_node = config.get("raw_data") or {}
        target_raw = raw_node.get("target")
        if not isinstance(target_raw, (int, float)) or target_raw <= 0:
            return None
        today = datetime.date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        daily_meta = target_raw / days_in_month * today.day
        target_fmt = config.get("target_formatted") or ""
        if isinstance(target_fmt, str) and target_fmt.startswith("$"):
            return format_value(daily_meta, "$")
        if isinstance(target_fmt, str) and target_fmt.endswith("%"):
            return f"{daily_meta:.1f}%"
        return f"{int(daily_meta):,}"

    def _build_compact_footer(self, config, is_inverse, theme="dark"):
        label_color = Colors.TEXT_DARK_SECONDARY if theme == "dark" else Colors.TEXT_LIGHT_SECONDARY
        value_color = Colors.TEXT_DARK if theme == "dark" else Colors.TEXT_LIGHT

        label = config.get("label_prev_year", "vs Ant.")
        value = config.get("vs_last_year_formatted")

        if value in (None, "---", "N/A", ""):
            daily = self._daily_meta_str(config)
            if daily:
                label = "Meta al día:"
                value = daily
            elif config.get("target_formatted") and config.get("target_formatted") not in ("---", "N/A"):
                label = "Meta mensual:"
                value = config.get("target_formatted")
            else:
                return html.Div(style={"height": "4px"})

        return dmc.Group(
            gap=3,
            wrap="nowrap",
            children=[
                dmc.Text(label, size=_dmc("8px"), style={"color": label_color}),
                dmc.Text(str(value), size=_dmc("8px"), fw=_dmc(600), style={"color": value_color}),
            ],
        )

    def _safe_to_float(self, val, default=0.0):
        if val is None:
            return default
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            clean = (
                val.replace("%", "")
                .replace("+", "")
                .replace(",", "")
                .replace("$", "")
                .strip()
            )
            try:
                return float(clean)
            except ValueError:
                return default
        return default

    def _safe_format_delta(self, delta, delta_fmt=None):
        if delta is None:
            return None, "gray"

        if delta_fmt and isinstance(delta_fmt, str) and delta_fmt not in ("N/A", "---", ""):
            delta_num = self._safe_to_float(delta_fmt)
            if delta_num > 0:
                return delta_fmt, Colors.POSITIVE
            if delta_num < 0:
                return delta_fmt, Colors.NEGATIVE
            return delta_fmt, "gray"

        delta_num = self._safe_to_float(delta)

        if delta_num == 0:
            return "0%", "gray"

        badge_text = f"{delta_num:+.1f}%"
        badge_color = Colors.POSITIVE if delta_num > 0 else Colors.NEGATIVE

        return badge_text, badge_color

    def _build_footer(self, config, height=200, theme="dark"):
        footer_items = []
        is_inverse = config.get("inverse", False)
        max_items = 3 if height < 180 else 4

        label_color = Colors.TEXT_DARK_SECONDARY if theme == "dark" else Colors.TEXT_LIGHT_SECONDARY
        value_color = Colors.TEXT_DARK if theme == "dark" else Colors.TEXT_LIGHT

        def make_row(label, value, delta=None, delta_fmt=None):
            if value in (None, "---", "N/A", ""):
                return None

            badge = None
            badge_text, badge_color = self._safe_format_delta(delta, delta_fmt)

            if badge_text and badge_text not in ("0%", "N/A"):
                if is_inverse and badge_color in (Colors.POSITIVE, Colors.NEGATIVE):
                    badge_color = (
                        Colors.NEGATIVE if badge_color == Colors.POSITIVE else Colors.POSITIVE
                    )

                badge = dmc.Badge(
                    badge_text,
                    color=_dmc(badge_color),
                    variant="light",
                    size="xs",
                    style={"padding": "0 4px", "height": "16px", "fontSize": "9px"},
                )

            return dmc.Group(
                justify="space-between",
                w="100%",
                wrap="nowrap",
                style={"minHeight": "16px"},
                children=[
                    dmc.Text(label, size=_dmc("9px"), fw=_dmc(500), style={"color": label_color}),
                    dmc.Group(
                        gap=2,
                        wrap="nowrap",
                        children=[
                            dmc.Text(
                                str(value),
                                size=_dmc("9px"),
                                fw=_dmc(600),
                                style={"color": value_color},
                            ),
                            badge if badge else html.Div(),
                        ],
                    ),
                ],
            )

        prev_row = make_row(
            config.get("label_prev_year", f"vs {_ts.previous_year}"),
            config.get("vs_last_year_formatted"),
            config.get("vs_last_year_delta"),
            config.get("vs_last_year_delta_formatted"),
        )
        if prev_row and len(footer_items) < max_items:
            footer_items.append(prev_row)

        meta_row = None
        meta_dia_row = None
        if not config.get("hide_meta", False):
            meta_row = make_row(
                config.get("label_target", "Meta mensual"),
                config.get("target_formatted"),
                config.get("target_delta"),
                config.get("target_delta_formatted"),
            )
            daily = self._daily_meta_str(config)
            if daily:
                meta_dia_row = make_row("Meta al día", daily)
        if meta_row and len(footer_items) < max_items:
            footer_items.append(meta_row)
        if meta_dia_row and len(footer_items) < max_items:
            footer_items.append(meta_dia_row)

        ytd_row = make_row(
            config.get("label_ytd", "YTD"),
            config.get("ytd_formatted"),
            config.get("ytd_delta"),
            config.get("ytd_delta_formatted"),
        )
        if ytd_row and len(footer_items) < max_items:
            footer_items.append(ytd_row)

        if not footer_items:
            return html.Div(style={"height": "4px"})

        return html.Div(
            style={"padding": "4px"},
            children=dmc.Stack(gap=1, w="100%", children=footer_items),
        )