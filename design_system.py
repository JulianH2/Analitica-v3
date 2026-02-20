from typing import Any, Dict, Final, List, Literal, Optional, TypedDict, Union, Callable, cast
import plotly.graph_objects as go
import plotly.io as pio


def dmc(v: object) -> Any:
    """DMC prop cast — bypasses Pylance false-positives for dash-mantine-components
    props supported at runtime but missing from library type stubs.
    Examples: fw=dmc(700), c=dmc("dimmed"), span=dmc({"base": 12, "lg": 7})."""
    return cast(Any, v)


FontWeight = Literal[400, 500, 600, 700, 800, 900]
FontSize = Union[int, float, Literal["xs", "sm", "md", "lg", "xl"]]
Spacing = Literal["xs", "sm", "md", "lg", "xl"]
Radius = Literal["xs", "sm", "md", "lg", "xl"]

class Breakpoints:
    XS: Final[int] = 0
    SM: Final[int] = 576
    MD: Final[int] = 768
    LG: Final[int] = 992
    XL: Final[int] = 1200
    XXL: Final[int] = 1600
    
    @staticmethod
    def get_cols_config(xs: int = 1, sm: int = 2, md: int = 3, lg: int = 4, xl: Optional[int] = None) -> Dict[str, int]:
        config = {"base": xs, "sm": sm, "md": md, "lg": lg}
        if xl is not None:
            config["xl"] = xl
        return config
    
    @staticmethod
    def get_span_config(xs: int = 12, sm: int = 6, md: int = 4, lg: int = 3, xl: Optional[int] = None) -> Dict[str, int]:
        config = {"base": xs, "sm": sm, "md": md, "lg": lg}
        if xl is not None:
            config["xl"] = xl
        return config


class Colors:

    CHART_CURRENT: Final[str] = "#f9daa0"
    CHART_PREVIOUS: Final[str] = "#bec4c6"
    CHART_TARGET: Final[str] = "#418cdf"
    CHART_COLORS: Final[str] = "#c9c4b8"


    NEXA_ORANGE: Final[str] = "#e27f08"
    NEXA_BLUE: Final[str] = "#418cdf"
    NEXA_GREEN: Final[str] = "#4c9f54"
    NEXA_RED: Final[str] = "#ff0000"
    NEXA_BLACK: Final[str] = "#1d1d1b"
    NEXA_GOLD: Final[str] = "#e9a13b"
    NEXA_GRAY_LIGHT: Final[str] = "#f2f2f2"
    NEXA_GRAY: Final[str] = "#808080"
    NEXA_CREAM: Final[str] = "#f9daa0"
    NEXA_PINK_LIGHT: Final[str] = "#fccaca"


    BG_LIGHT: Final[str] = "#F8FAFC"
    BG_LIGHT_SECONDARY: Final[str] = "#FFFFFF"
    BG_LIGHT_CARD: Final[str] = "#FFFFFF"


    BG_DARK: Final[str] = "#1d1d1b"       
    

    BG_DARK_SECONDARY: Final[str] = "#2c2e33" 
    

    BG_DARK_CARD: Final[str] = "#62686e"      


    PLOT_BG_DARK: Final[str] = "rgba(0,0,0,0)"
    PLOT_GRID_DARK: Final[str] = "#4a4a4a"
    
    PLOT_BG_LIGHT: Final[str] = "rgba(0,0,0,0)"
    PLOT_GRID_LIGHT: Final[str] = "#e2e8f0"


    TEXT_LIGHT: Final[str] = "#1d1d1b"
    TEXT_LIGHT_SECONDARY: Final[str] = "#64748b"
    TEXT_DARK: Final[str] = "#f2f2f2"
    TEXT_DARK_SECONDARY: Final[str] = "#bec4c6"


    POSITIVE: Final[str] = "#4c9f54"
    POSITIVE_LIGHT: Final[str] = "#62c26d"
    POSITIVE_BG: Final[str] = "rgba(76, 159, 84, 0.15)"

    NEUTRAL: Final[str] = "#e9a13b"
    NEUTRAL_BG: Final[str] = "rgba(233, 161, 59, 0.15)"

    NEGATIVE: Final[str] = "#ff0000"
    NEGATIVE_LIGHT: Final[str] = "#fccaca"
    NEGATIVE_BG: Final[str] = "rgba(255, 0, 0, 0.15)"


    CHART_BLUE: Final[str] = "#418cdf"
    CHART_BLUE_LIGHT: Final[str] = "#80abd4"
    CHART_GRAY: Final[str] = "#bec4c6"
    CHART_GOLD: Final[str] = "#f9daa0"
    CHART_ORANGE: Final[str] = "#e27f07"

    BAR_GOLD: Final[str] = "#e9a13b"
    BAR_GRAY: Final[str] = "#7a8895"
    BAR_BLUE: Final[str] = "#418cdf"


    SLATE: Final[List[str]] = [
        "#f8fafc", "#f2f2f2", "#e2e8f0", "#cbd5e1", 
        "#94a3b8", "#808080", "#757575F9", 
        "#62686e",
        "#1d1d1b",
        "#0f172a"  
    ]
    
    BRAND: Final[List[str]] = [
        "#e8f4fd", "#d1e9fb", "#a3d3f7", "#75bdf3",
        "#47a7ef", "#418cdf", "#3570b3", "#295487",
        "#1d385b", "#111c2f"
    ]
    
    SUCCESS: Final[List[str]] = [
        "#edf7ee", "#d4edd6", "#a9dbb0", "#7ec98a",
        "#53b764", "#4c9f54", "#3d7f43", "#2e5f32",
        "#1f3f21", "#101f10"
    ]
    
    WARNING: Final[List[str]] = [
        "#fef6e8", "#fdecd1", "#fbd9a3", "#f9c675",
        "#f7b347", "#e9a13b", "#ba812f", "#8c6123",
        "#5d4017", "#2f200b"
    ]
    
    DANGER: Final[List[str]] = [
        "#fff2f2", "#ffe6e6", "#ffcccc", "#ffb3b3",
        "#ff9999", "#ff0000", "#cc0000", "#990000",
        "#660000", "#330000"
    ]
    
    ORANGE: Final[List[str]] = [
        "#fef3e8", "#fde7d1", "#fbcfa3", "#f9b775",
        "#f79f47", "#e27f08", "#b56606", "#884d05",
        "#5b3403", "#2d1a01"
    ]
    TRANSPARENT: Final[str] = "rgba(0,0,0,0)"
    WHITE: Final[str] = "#ffffff"
    
    CARD_BORDER_LIGHT: Final[str] = "1px solid #e5e7eb"
    CARD_BORDER_DARK: Final[str] = "1px solid rgba(255,255,255,0.08)"
    
    COLOR_MAP: Final[Dict[str, str]] = {
        "blue": NEXA_BLUE,
        "indigo": BRAND[5],
        "green": NEXA_GREEN,
        "emerald": SUCCESS[5],
        "yellow": NEXA_GOLD,
        "amber": WARNING[5],
        "orange": NEXA_ORANGE,
        "red": NEXA_RED,
        "rose": "#f43f5e",
        "slate": SLATE[7],
        "gray": NEXA_GRAY,
        "dark": NEXA_BLACK,
        "black": NEXA_BLACK,
        "cyan": "#06b6d4",
        "teal": "#14b8a6",
        "violet": "#8b5cf6",
        "grape": "#be4bdb",
        "pink": NEXA_PINK_LIGHT,
        "lime": "#84cc16",
        "gold": NEXA_GOLD,
        "cream": NEXA_CREAM,
        "white": WHITE,
    }
    
class Typography:
    
    
    FAMILY: Final[str] = (
        "'Nexa', 'Montserrat', 'Inter', "
        "-apple-system, BlinkMacSystemFont, "
        "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    )
    

    WEIGHT_NORMAL: Final[FontWeight] = 400
    WEIGHT_MEDIUM: Final[FontWeight] = 500
    WEIGHT_SEMIBOLD: Final[FontWeight] = 600
    WEIGHT_BOLD: Final[FontWeight] = 700
    WEIGHT_EXTRABOLD: Final[FontWeight] = 800
    WEIGHT_BLACK: Final[FontWeight] = 900
    

    XS_TINY: Final[int] = 9
    XS: Final[int] = 10
    BADGE: Final[int] = 11
    TABLE: Final[int] = 11
    TABLE_HEADER: Final[int] = 12
    METRIC_SMALL: Final[int] = 12
    SM: Final[int] = 13
    LABEL: Final[int] = 14
    MD: Final[int] = 14
    BASE: Final[int] = 16
    KPI_SMALL: Final[int] = 16
    LG: Final[int] = 18
    SUBTITLE: Final[int] = 18
    XL: Final[int] = 24
    SECTION_TITLE: Final[int] = 24
    KPI_MEDIUM: Final[int] = 24
    XXL: Final[int] = 32
    KPI_LARGE: Final[int] = 32
    XXXL: Final[int] = 48
    

    LH_TIGHT: Final[str] = "1"
    LH_NORMAL: Final[str] = "1.5"
    LH_RELAXED: Final[str] = "1.75"


class Space:
    
    
    XXS: Final[int] = 2
    XS: Final[int] = 4
    SM: Final[int] = 8
    MD: Final[int] = 12
    BASE: Final[int] = 16
    LG: Final[int] = 24
    XL: Final[int] = 32
    XXL: Final[int] = 48
    XXXL: Final[int] = 64
    
    @staticmethod
    def get(size: Spacing) -> int:
        mapping: Dict[Spacing, int] = {
            "xs": Space.XS,
            "sm": Space.SM,
            "md": Space.MD,
            "lg": Space.LG,
            "xl": Space.XL,
        }
        return mapping.get(size, Space.MD)


class BorderRadius:
    
    
    XS: Final[str] = "2px"
    SM: Final[str] = "4px"
    MD: Final[str] = "6px"
    BASE: Final[str] = "8px"
    LG: Final[str] = "12px"
    XL: Final[str] = "16px"
    PILL: Final[str] = "24px"
    FULL: Final[str] = "9999px"


class Shadows:
    
    
    SM: Final[str] = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    MD: Final[str] = "0 1px 3px 0 rgba(0, 0, 0, 0.08)"
    LG: Final[str] = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    XL: Final[str] = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    

    SM_DARK: Final[str] = "0 2px 4px 0 rgba(0, 0, 0, 0.25)"
    MD_DARK: Final[str] = "0 2px 6px 0 rgba(0, 0, 0, 0.3)"
    LG_DARK: Final[str] = "0 12px 18px -4px rgba(0, 0, 0, 0.4), 0 6px 8px -3px rgba(0, 0, 0, 0.3)"
    XL_DARK: Final[str] = "0 24px 30px -6px rgba(0, 0, 0, 0.5), 0 12px 12px -6px rgba(0, 0, 0, 0.4)"


class ComponentSizes:
    
    
    KPI_HEIGHT_COMPACT: Final[int] = 110
    KPI_HEIGHT_NORMAL: Final[int] = 160
    KPI_HEIGHT_GAUGE: Final[int] = 195
    

    CHART_HEIGHT_SM: Final[int] = 240
    CHART_HEIGHT_MD: Final[int] = 340
    CHART_HEIGHT_BASE: Final[int] = 420
    CHART_HEIGHT_LG: Final[int] = 520
    

    GAUGE_HEIGHT: Final[int] = 195
    GAUGE_SIZE: Final[int] = 120
    GAUGE_THICKNESS: Final[int] = 18
    GAUGE_INNER_RADIUS: Final[str] = "75%"
    

    BUTTON_HEIGHT_SM: Final[int] = 32
    BUTTON_HEIGHT_MD: Final[int] = 36
    BUTTON_HEIGHT_LG: Final[int] = 44
    

    BADGE_HEIGHT: Final[int] = 20
    

    ICON_XS: Final[int] = 12
    ICON_SM: Final[int] = 14
    ICON_MD: Final[int] = 16
    ICON_LG: Final[int] = 20
    ICON_XL: Final[int] = 24
    ICON_XXL: Final[int] = 32
    ICON_XXXL: Final[int] = 48
    

    TABLE_HEADER_HEIGHT: Final[int] = 40
    TABLE_ROW_HEIGHT: Final[int] = 44
    

    CHAT_SIDEBAR_WIDTH: Final[int] = 380
    FILTER_MODAL_WIDTH: Final[int] = 400
    INPUT_HEIGHT: Final[int] = 48


class SemanticColors:
    
    
    INGRESO: Final[str] = Colors.NEXA_GREEN
    EGRESO: Final[str] = Colors.NEXA_RED
    PROFIT: Final[str] = Colors.NEXA_BLUE
    

    TEXT_MAIN: Final[str] = Colors.NEXA_BLACK
    TEXT_MUTED: Final[str] = Colors.NEXA_GRAY
    TEXT_DIMMED: Final[str] = Colors.SLATE[5]
    

    BORDER: Final[str] = Colors.SLATE[2]
    BORDER_MUTED: Final[str] = Colors.SLATE[1]
    

    SUCCESS: Final[str] = Colors.POSITIVE
    SUCCESS_BG: Final[str] = Colors.POSITIVE_BG
    WARNING: Final[str] = Colors.NEUTRAL
    WARNING_BG: Final[str] = Colors.NEUTRAL_BG
    ERROR: Final[str] = Colors.NEGATIVE
    ERROR_BG: Final[str] = Colors.NEGATIVE_BG
    INFO: Final[str] = Colors.NEXA_BLUE


class ChartColors:
    
    
    DEFAULT: Final[List[str]] = [
        Colors.NEXA_BLUE,
        Colors.NEXA_ORANGE,
        Colors.NEXA_GREEN,
        Colors.NEXA_GOLD,
        Colors.NEXA_GRAY,
        Colors.NEXA_RED,
    ]
    
    CHART_COLORS: Final[List[str]] = ["#f9daa0", "#bec4c6", "#418cdf", "#e9a13b"]
    

    YEAR_COMPARISON: Final[Dict[str, str]] = {
        "meta": Colors.CHART_BLUE,
        "2025": Colors.CHART_GRAY,
        "2026": Colors.CHART_GOLD,
        "current": Colors.CHART_GOLD,
        "previous": Colors.CHART_GRAY,
        "target": Colors.CHART_BLUE,
    }
    

    LINE_TRENDS: Final[List[str]] = [
        Colors.CHART_BLUE_LIGHT,
        Colors.CHART_GOLD,
    ]
    

    HORIZONTAL_BARS: Final[str] = Colors.CHART_GOLD
    
    DONUT: Final[List[str]] = [
        Colors.NEXA_BLUE,
        Colors.NEXA_ORANGE,
        Colors.NEXA_GREEN,
        Colors.NEXA_GOLD,
        Colors.NEXA_GRAY,
        Colors.NEXA_CREAM,
        Colors.NEXA_PINK_LIGHT,
    ]


class BadgeConfig:
    
    
    @staticmethod
    def get_positive_badge() -> Dict[str, str]:
        
        return {
            "background": Colors.POSITIVE_BG,
            "text": Colors.POSITIVE,
            "icon": "↑"
        }
    
    @staticmethod
    def get_negative_badge() -> Dict[str, str]:
        
        return {
            "background": Colors.NEGATIVE_BG,
            "text": Colors.NEGATIVE,
            "icon": "↓"
        }
    
    @staticmethod
    def get_neutral_badge() -> Dict[str, str]:
        
        return {
            "background": Colors.NEUTRAL_BG,
            "text": Colors.NEUTRAL,
            "icon": "~"
        }
    
    @staticmethod
    def get_comparison_badge(diff_percentage: float) -> Dict[str, str]:
        if diff_percentage > 0:
            return {
                **BadgeConfig.get_positive_badge(),
                "label": f"+{diff_percentage:.1f}%"
            }
        elif diff_percentage < 0:
            return {
                **BadgeConfig.get_negative_badge(),
                "label": f"{diff_percentage:.1f}%"
            }
        else:
            return {
                **BadgeConfig.get_neutral_badge(),
                "label": "0.0%"
            }


class GaugeConfig:
    
    
    @staticmethod
    def get_gauge_color(percentage: float) -> str:
        if percentage >= 80:
            return Colors.POSITIVE
        elif percentage >= 60:
            return Colors.NEUTRAL
        else:
            return Colors.NEGATIVE
    
    @staticmethod
    def get_gauge_colors(percentage: float) -> Dict[str, str]:
        gauge_color = GaugeConfig.get_gauge_color(percentage)
        
        if percentage >= 80:
            bg_color = Colors.POSITIVE_BG
        elif percentage >= 60:
            bg_color = Colors.NEUTRAL_BG
        else:
            bg_color = Colors.NEGATIVE_BG
        
        return {
            "gauge_color": gauge_color,
            "background": bg_color,
            "text": gauge_color
        }


class TableStatusConfig:
    
    
    @staticmethod
    def get_status_badge(status: str) -> Dict[str, str]:
        status_map = {
            "dentro_del_rango": {
                "background": Colors.POSITIVE_BG,
                "text": Colors.POSITIVE,
                "label": "Dentro del rango"
            },
            "atencion": {
                "background": Colors.NEUTRAL_BG,
                "text": Colors.NEUTRAL,
                "label": "Atención"
            },
            "fuera_del_rango": {
                "background": Colors.NEGATIVE_BG,
                "text": Colors.NEGATIVE,
                "label": "Fuera del rango"
            }
        }
        return status_map.get(status, status_map["atencion"])
    
    @staticmethod
    def determine_status(current: float, min_val: float, max_val: float) -> str:
        if min_val <= current <= max_val:
            return "dentro_del_rango"
        elif current > max_val * 1.2 or current < min_val * 0.8:
            return "fuera_del_rango"
        else:
            return "atencion"


class ZIndex:
    
    
    BASE: Final[int] = 0
    DROPDOWN: Final[int] = 100
    STICKY: Final[int] = 200
    FIXED: Final[int] = 300
    MODAL_BACKDROP: Final[int] = 400
    MODAL: Final[int] = 500
    POPOVER: Final[int] = 600
    TOOLTIP: Final[int] = 700
    DRAWER: Final[int] = 1100
    AI_SIDEBAR: Final[int] = 1100
    NOTIFICATION: Final[int] = 1200
    AI_TOGGLE: Final[int] = 1000


class PlotlyConfig:
    
    
    @staticmethod
    def get_base_layout(theme: str = "light") -> Dict[str, Any]:
        is_dark = theme == "dark"
        
        return dict(
            paper_bgcolor=Colors.TRANSPARENT,
            plot_bgcolor=Colors.TRANSPARENT,
            margin=dict(t=35, b=45, l=50, r=20),
            colorway=ChartColors.DEFAULT,
            font=dict(
                family=Typography.FAMILY,
                color=Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT,
                size=Typography.METRIC_SMALL
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(
                    size=Typography.XS, 
                    color=Colors.TEXT_DARK_SECONDARY if is_dark else Colors.TEXT_LIGHT_SECONDARY
                )
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=Colors.BG_DARK_SECONDARY if is_dark else Colors.BG_LIGHT_SECONDARY,
                gridwidth=1,
                zeroline=False,
                tickfont=dict(
                    size=Typography.XS, 
                    color=Colors.TEXT_DARK_SECONDARY if is_dark else Colors.TEXT_LIGHT_SECONDARY
                )
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=Typography.XS)
            ),
            bargap=0.18,
            bargroupgap=0.12,
        )
    
    @staticmethod
    def get_bar_chart_config(theme: str = "light") -> Dict[str, Any]:
        
        return {
            "colors": ChartColors.YEAR_COMPARISON,
            "bar_width": 0.6,
            "bar_gap": 0.18,
            "bar_group_gap": 0.12,
            "height": ComponentSizes.CHART_HEIGHT_BASE,
            "x_labels": ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", 
                        "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        }
    
    @staticmethod
    def get_line_chart_config(theme: str = "light") -> Dict[str, Any]:
        
        return {
            "colors": ChartColors.LINE_TRENDS,
            "line_width": 2,
            "line_smooth": True,
            "fill_opacity": 0.15,
            "height": ComponentSizes.CHART_HEIGHT_MD
        }
    
    @staticmethod
    def get_horizontal_bar_config(theme: str = "light") -> Dict[str, Any]:
        
        return {
            "bar_color": ChartColors.HORIZONTAL_BARS,
            "bar_height": 0.5,
            "height": ComponentSizes.CHART_HEIGHT_SM,
            "value_labels": {
                "show": True,
                "position": "inside",
                "font_size": Typography.BADGE,
                "font_color": Colors.TEXT_LIGHT,
                "font_weight": Typography.WEIGHT_SEMIBOLD
            }
        }
    
    @staticmethod
    def get_display_config() -> Dict[str, Any]:
        
        return {
            'displayModeBar': 'hover',
            'responsive': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'zoom2d']
        }
    
    @staticmethod
    def setup_templates() -> None:
        

        pio.templates["zam_light"] = go.layout.Template(
            layout=PlotlyConfig.get_base_layout("light")
        )
        

        pio.templates["zam_dark"] = go.layout.Template(
            layout=PlotlyConfig.get_base_layout("dark")
        )
        
        pio.templates.default = "zam_light"


class MantineTheme:
    
    
    @staticmethod
    def get_light_theme() -> Dict[str, Any]:
        return {
            "colorScheme": "light",
            "fontFamily": Typography.FAMILY,
            "primaryColor": "blue",
            "defaultRadius": "md",
            "white": Colors.BG_LIGHT,
            "black": Colors.TEXT_LIGHT,
            "colors": {
                "indigo": Colors.BRAND,
                "dark": Colors.SLATE,
                "gray": Colors.SLATE,
                "green": Colors.SUCCESS,
                "yellow": Colors.WARNING,
                "red": Colors.DANGER,
                "blue": Colors.BRAND,
                "orange": Colors.ORANGE,
            },
            "components": {
                "Button": {
                    "defaultProps": {
                        "size": "sm",
                        "fw": Typography.WEIGHT_SEMIBOLD,
                        "radius": "md"
                    }
                },
                "Paper": {
                    "defaultProps": {
                        "withBorder": True,
                        "shadow": "sm",
                        "radius": "base"
                    },
                    "styles": {
                        "root": {
                            "borderColor": Colors.BG_LIGHT_SECONDARY
                        }
                    }
                },
                "Card": {
                    "defaultProps": {
                        "withBorder": True,
                        "shadow": "sm",
                        "radius": "base",
                        "padding": "md"
                    }
                },
                "Badge": {
                    "defaultProps": {
                        "size": "sm",
                        "radius": "pill"
                    }
                },
                "Table": {
                    "styles": {
                        "thead": {
                            "backgroundColor": Colors.BG_LIGHT_SECONDARY,
                            "fontWeight": Typography.WEIGHT_SEMIBOLD
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def get_dark_theme() -> Dict[str, Any]:
        theme = MantineTheme.get_light_theme()
        theme.update({
            "colorScheme": "dark",
            "white": Colors.BG_DARK,
            "black": Colors.TEXT_DARK,
        })
        

        if "components" in theme:
            theme["components"]["Paper"]["styles"] = {
                "root": {
                    "backgroundColor": Colors.BG_DARK_CARD,
                    "borderColor": Colors.BG_DARK_SECONDARY
                }
            }
            theme["components"]["Table"]["styles"]["thead"]["backgroundColor"] = Colors.BG_DARK_SECONDARY
        
        return theme


PlotlyConfig.setup_templates()

class DesignSystem:
    

    TEXT_LIGHT = Colors.TEXT_LIGHT
    TEXT_LIGHT_SECONDARY = Colors.TEXT_LIGHT_SECONDARY
    TEXT_DARK = Colors.TEXT_DARK
    TEXT_DARK_SECONDARY = Colors.TEXT_DARK_SECONDARY
    

    NEXA_ORANGE = Colors.NEXA_ORANGE
    NEXA_BLUE = Colors.NEXA_BLUE
    NEXA_GREEN = Colors.NEXA_GREEN
    NEXA_RED = Colors.NEXA_RED
    NEXA_BLACK = Colors.NEXA_BLACK
    NEXA_GOLD = Colors.NEXA_GOLD
    NEXA_GRAY_LIGHT = Colors.NEXA_GRAY_LIGHT
    NEXA_GRAY = Colors.NEXA_GRAY
    NEXA_CREAM = Colors.NEXA_CREAM
    NEXA_PINK_LIGHT = Colors.NEXA_PINK_LIGHT
    

    NEXA_BG_LIGHT = Colors.BG_LIGHT
    NEXA_BG_LIGHT_SECONDARY = Colors.BG_LIGHT_SECONDARY
    NEXA_BG_DARK = Colors.BG_DARK
    NEXA_BG_DARK_SECONDARY = Colors.BG_DARK_SECONDARY
    

    TEXT_LIGHT = Colors.TEXT_LIGHT
    TEXT_DARK = Colors.TEXT_DARK
    

    POSITIVE = Colors.POSITIVE
    POSITIVE_LIGHT = Colors.POSITIVE_LIGHT
    POSITIVE_BG = Colors.POSITIVE_BG
    NEUTRAL = Colors.NEUTRAL
    NEUTRAL_BG = Colors.NEUTRAL_BG
    NEGATIVE = Colors.NEGATIVE
    NEGATIVE_BG = Colors.NEGATIVE_BG
    

    CHART_BLUE = Colors.CHART_BLUE
    CHART_BLUE_LIGHT = Colors.CHART_BLUE_LIGHT
    CHART_GRAY = Colors.CHART_GRAY
    CHART_GOLD = Colors.CHART_GOLD
    CHART_ORANGE = Colors.CHART_ORANGE
    

    SLATE = Colors.SLATE
    BRAND = Colors.BRAND
    SUCCESS = Colors.SUCCESS
    WARNING = Colors.WARNING
    DANGER = Colors.DANGER
    INFO = Colors.BRAND
    ORANGE = Colors.ORANGE
    TRANSPARENT = Colors.TRANSPARENT
    WHITE = Colors.WHITE
    CARD_BORDER_LIGHT = Colors.CARD_BORDER_LIGHT
    CARD_BORDER_DARK = Colors.CARD_BORDER_DARK
    COLOR_MAP = Colors.COLOR_MAP
    

    CHART_COLORS = ChartColors.CHART_COLORS
    CHART_YEAR_COLORS = ChartColors.YEAR_COMPARISON
    CHART_LINE_COLORS = ChartColors.LINE_TRENDS
    CHART_DONUT_COLORS = ChartColors.DONUT
    

    TYPOGRAPHY = {
        "family": Typography.FAMILY,
        "weights": {
            "normal": Typography.WEIGHT_NORMAL,
            "medium": Typography.WEIGHT_MEDIUM,
            "semibold": Typography.WEIGHT_SEMIBOLD,
            "bold": Typography.WEIGHT_BOLD,
            "extrabold": Typography.WEIGHT_EXTRABOLD,
            "black": Typography.WEIGHT_BLACK
        },
        "sizes": {
            "xs_tiny": Typography.XS_TINY,
            "xs": Typography.XS,
            "badge": Typography.BADGE,
            "table": Typography.TABLE,
            "table_header": Typography.TABLE_HEADER,
            "sm": Typography.SM,
            "label": Typography.LABEL,
            "md": Typography.MD,
            "base": Typography.BASE,
            "lg": Typography.LG,
            "xl": Typography.XL,
            "xxl": Typography.XXL,
            "kpi_large": Typography.KPI_LARGE
        },
        "line_heights": {
            "tight": Typography.LH_TIGHT,
            "normal": Typography.LH_NORMAL,
            "relaxed": Typography.LH_RELAXED
        }
    }
    

    FONT_TABLE = Typography.TABLE
    FONT_XS = Typography.XS
    FONT_SM = Typography.SM
    FONT_MD = Typography.MD
    FONT_BADGE = Typography.BADGE
    FW_NORMAL = Typography.WEIGHT_NORMAL
    FW_MEDIUM = Typography.WEIGHT_MEDIUM
    FW_SEMIBOLD = Typography.WEIGHT_SEMIBOLD
    FW_BOLD = Typography.WEIGHT_BOLD
    

    LAYOUT = {
        "grid_columns": 12,
        "breakpoints": {
            "xs": Breakpoints.XS,
            "sm": Breakpoints.SM,
            "md": Breakpoints.MD,
            "lg": Breakpoints.LG,
            "xl": Breakpoints.XL
        },
        "spacing": {
            "xxs": f"{Space.XXS}px",
            "xs": f"{Space.XS}px",
            "sm": f"{Space.SM}px",
            "md": f"{Space.MD}px",
            "base": f"{Space.BASE}px",
            "lg": f"{Space.LG}px",
            "xl": f"{Space.XL}px",
            "xxl": f"{Space.XXL}px"
        },
        "radius": {
            "xs": BorderRadius.XS,
            "sm": BorderRadius.SM,
            "md": BorderRadius.MD,
            "base": BorderRadius.BASE,
            "lg": BorderRadius.LG,
            "xl": BorderRadius.XL,
            "pill": BorderRadius.PILL,
            "full": BorderRadius.FULL
        },
        "shadows": {
            "sm": Shadows.SM,
            "md": Shadows.MD,
            "lg": Shadows.LG,
            "xl": Shadows.XL,
            "sm_dark": Shadows.SM_DARK,
            "md_dark": Shadows.MD_DARK,
            "lg_dark": Shadows.LG_DARK,
            "xl_dark": Shadows.XL_DARK
        }
    }
    

    COMPONENTS = {
        "kpi_card": {
            "height_compact": ComponentSizes.KPI_HEIGHT_COMPACT,
            "height_normal": ComponentSizes.KPI_HEIGHT_NORMAL,
            "height_gauge": ComponentSizes.KPI_HEIGHT_GAUGE,
            "padding": Space.BASE,
            "border_radius": BorderRadius.BASE,
        },
        "gauge": {
            "height": ComponentSizes.GAUGE_HEIGHT,
            "size": ComponentSizes.GAUGE_SIZE,
            "thickness": ComponentSizes.GAUGE_THICKNESS,
            "inner_radius": ComponentSizes.GAUGE_INNER_RADIUS,
        },
        "charts": {
            "height_sm": ComponentSizes.CHART_HEIGHT_SM,
            "height_md": ComponentSizes.CHART_HEIGHT_MD,
            "height_default": ComponentSizes.CHART_HEIGHT_BASE,
            "height_lg": ComponentSizes.CHART_HEIGHT_LG,
        },
        "button": {
            "height_sm": ComponentSizes.BUTTON_HEIGHT_SM,
            "height_md": ComponentSizes.BUTTON_HEIGHT_MD,
            "height_lg": ComponentSizes.BUTTON_HEIGHT_LG,
            "padding": f"{Space.SM}px {Space.BASE}px",
            "border_radius": BorderRadius.MD,
            "font_size": Typography.SM,
            "font_weight": Typography.WEIGHT_SEMIBOLD
        },
        "badge": {
            "height": ComponentSizes.BADGE_HEIGHT,
            "padding": f"{Space.XXS}px {Space.SM}px",
            "border_radius": BorderRadius.PILL,
            "font_size": Typography.BADGE,
            "font_weight": Typography.WEIGHT_SEMIBOLD
        },
        "table": {
            "header_height": ComponentSizes.TABLE_HEADER_HEIGHT,
            "row_height": ComponentSizes.TABLE_ROW_HEIGHT,
            "font_size_header": Typography.TABLE_HEADER,
            "font_size_body": Typography.TABLE,
            "padding": f"{Space.SM}px {Space.MD}px"
        }
    }
    

    @staticmethod
    def get_mantine_theme(scheme: str = "light") -> Dict[str, Any]:
        
        if scheme == "dark":
            return MantineTheme.get_dark_theme()
        return MantineTheme.get_light_theme()
    
    @staticmethod
    def get_mantine_theme_dark() -> Dict[str, Any]:
        
        return MantineTheme.get_dark_theme()
    
    @staticmethod
    def setup_plotly_templates() -> None:
        
        PlotlyConfig.setup_templates()
    
    @staticmethod
    def get_plotly_layout(theme: str = "light") -> Dict[str, Any]:
        
        return PlotlyConfig.get_base_layout(theme)
    
    @staticmethod
    def get_badge_config(diff_percentage: float) -> Dict[str, str]:
        
        return BadgeConfig.get_comparison_badge(diff_percentage)
    
    @staticmethod
    def get_gauge_color(percentage: float) -> str:
        
        return GaugeConfig.get_gauge_color(percentage)
    
    @staticmethod
    def get_status_badge(status: str) -> Dict[str, str]:
        
        return TableStatusConfig.get_status_badge(status)
    
    @staticmethod
    def determine_status(current: float, min_val: float, max_val: float) -> str:
        
        return TableStatusConfig.determine_status(current, min_val, max_val)