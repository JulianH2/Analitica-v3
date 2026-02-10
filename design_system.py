from typing import Any, Dict, Final, List, Literal, TypedDict, Union
import plotly.graph_objects as go
import plotly.io as pio

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
    def get_cols_config(xs: int = 1, sm: int = 2, md: int = 3, lg: int = 4, xl: int = None) -> Dict[str, int]: # type: ignore
        config = {"base": xs, "sm": sm, "md": md, "lg": lg}
        if xl is not None:
            config["xl"] = xl
        return config
    
    @staticmethod
    def get_span_config(xs: int = 12, sm: int = 6, md: int = 4, lg: int = 3, xl: int = None) -> Dict[str, int]: # type: ignore
        config = {"base": xs, "sm": sm, "md": md, "lg": lg}
        if xl is not None:
            config["xl"] = xl
        return config

class Colors:
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
    BG_LIGHT: Final[str] = "#f8f6f3"
    BG_DARK: Final[str] = "#1d1d1b"
    TEXT_DARK: Final[str] = "#f2f2f2"
    
    SLATE: Final[List[str]] = [
        "#f8fafc", "#f2f2f2", "#e2e8f0", "#cbd5e1", 
        "#94a3b8", "#808080", "#475569", "#334155", 
        "#1d1d1b", "#0f172a"
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
        "slate": SLATE[5],
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
    TABLE: Final[int] = 11
    SM: Final[int] = 12
    MD: Final[int] = 14
    BASE: Final[int] = 16
    LG: Final[int] = 18
    XL: Final[int] = 24
    XXL: Final[int] = 32
    XXXL: Final[int] = 48
    
    LH_TIGHT: Final[str] = "1"
    LH_NORMAL: Final[str] = "1.5"
    LH_RELAXED: Final[str] = "1.75"

class Space:
    XXS: Final[int] = 2
    XS: Final[int] = 4
    SM: Final[int] = 8
    MD: Final[int] = 16
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
    MD: Final[str] = "8px"
    LG: Final[str] = "12px"
    XL: Final[str] = "16px"
    FULL: Final[str] = "9999px"

class Shadows:
    SM: Final[str] = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    MD: Final[str] = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    LG: Final[str] = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    XL: Final[str] = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

class ComponentSizes:
    KPI_HEIGHT_COMPACT: Final[int] = 110
    KPI_HEIGHT_NORMAL: Final[int] = 160
    KPI_HEIGHT_LARGE: Final[int] = 195
    CHART_HEIGHT_SM: Final[int] = 250
    CHART_HEIGHT_MD: Final[int] = 320
    CHART_HEIGHT_LG: Final[int] = 450
    GAUGE_HEIGHT: Final[int] = 220
    GAUGE_INNER_RADIUS: Final[str] = "75%"
    ICON_XS: Final[int] = 12
    ICON_SM: Final[int] = 14
    ICON_MD: Final[int] = 16
    ICON_LG: Final[int] = 20
    ICON_XL: Final[int] = 24
    ICON_XXL: Final[int] = 32

class SemanticColors:
    INGRESO: Final[str] = Colors.NEXA_GREEN
    EGRESO: Final[str] = Colors.NEXA_RED
    PROFIT: Final[str] = Colors.NEXA_BLUE
    TEXT_MAIN: Final[str] = Colors.NEXA_BLACK
    TEXT_MUTED: Final[str] = Colors.NEXA_GRAY
    TEXT_DIMMED: Final[str] = Colors.SLATE[5]
    BORDER: Final[str] = Colors.SLATE[2]
    BORDER_MUTED: Final[str] = Colors.SLATE[1]
    SUCCESS: Final[str] = Colors.NEXA_GREEN
    WARNING: Final[str] = Colors.NEXA_GOLD
    ERROR: Final[str] = Colors.NEXA_RED
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
    
    YEAR_COMPARISON: Final[Dict[str, str]] = {
        "current": Colors.NEXA_BLUE,
        "previous": Colors.NEXA_ORANGE,
        "target": Colors.NEXA_GREEN,
        "meta": Colors.NEXA_GRAY,
    }
    
    DONUT: Final[List[str]] = [
        Colors.NEXA_BLUE,
        Colors.NEXA_ORANGE,
        Colors.NEXA_GREEN,
        Colors.NEXA_GOLD,
        Colors.NEXA_GRAY,
        Colors.NEXA_CREAM,
        Colors.NEXA_PINK_LIGHT,
    ]

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
    def get_base_layout() -> Dict[str, Any]:
        return dict(
            paper_bgcolor=Colors.TRANSPARENT,
            plot_bgcolor=Colors.TRANSPARENT,
            margin=dict(t=35, b=35, l=45, r=20),
            colorway=ChartColors.DEFAULT,
            font=dict(
                family=Typography.FAMILY,
                color=Colors.NEXA_BLACK,
                size=Typography.TABLE
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=Typography.XS, color=Colors.NEXA_GRAY)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=Colors.SLATE[2],
                gridwidth=1,
                zeroline=False,
                tickfont=dict(size=Typography.XS, color=Colors.NEXA_GRAY)
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
    def get_display_config() -> Dict[str, Any]:
        return {
            'displayModeBar': 'hover',
            'responsive': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'zoom2d']
        }
    
    @staticmethod
    def setup_templates() -> None:
        pio.templates["zam_clean"] = go.layout.Template(
            layout=PlotlyConfig.get_base_layout()
        )
        pio.templates.default = "zam_clean"

class MantineTheme:
    @staticmethod
    def get_light_theme() -> Dict[str, Any]:
        return {
            "colorScheme": "light",
            "fontFamily": Typography.FAMILY,
            "primaryColor": "blue",
            "defaultRadius": "md",
            "white": Colors.BG_LIGHT,
            "black": Colors.NEXA_BLACK,
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
                        "shadow": "sm"
                    }
                },
                "Card": {
                    "defaultProps": {
                        "withBorder": True,
                        "shadow": "sm",
                        "radius": "md"
                    }
                }
            }
        }
    
    @staticmethod
    def get_dark_theme() -> Dict[str, Any]:
        theme = MantineTheme.get_light_theme()
        theme["colorScheme"] = "dark"
        theme["white"] = Colors.BG_DARK
        theme["black"] = Colors.TEXT_DARK
        return theme

PlotlyConfig.setup_templates()

class DesignSystem:
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
    NEXA_BG_DARK = Colors.BG_DARK
    TEXT_DARK = Colors.TEXT_DARK
    SLATE = Colors.SLATE
    BRAND = Colors.BRAND
    SUCCESS = Colors.SUCCESS
    WARNING = Colors.WARNING
    DANGER = Colors.DANGER
    INFO = Colors.BRAND
    ORANGE = Colors.ORANGE
    TRANSPARENT = Colors.TRANSPARENT
    WHITE = Colors.WHITE
    COLOR_MAP = Colors.COLOR_MAP
    CHART_COLORS = ChartColors.DEFAULT
    CHART_YEAR_COLORS = ChartColors.YEAR_COMPARISON
    CHART_DONUT_COLORS = ChartColors.DONUT
    TYPOGRAPHY = {
        "family": Typography.FAMILY,
        "weights": {
            "normal": Typography.WEIGHT_NORMAL,
            "medium": Typography.WEIGHT_MEDIUM,
            "bold": Typography.WEIGHT_BOLD,
            "black": Typography.WEIGHT_BLACK
        },
        "sizes": {
            "xs_tiny": Typography.XS_TINY,
            "xs": Typography.XS,
            "table": Typography.TABLE,
            "sm": Typography.SM,
            "md": Typography.MD,
            "lg": Typography.LG,
            "xl": Typography.XL,
            "xxl": Typography.XXL
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
    FW_NORMAL = Typography.WEIGHT_NORMAL
    FW_BOLD = Typography.WEIGHT_BOLD
    FW_MEDIUM = Typography.WEIGHT_MEDIUM
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
            "xs": f"{Space.XS}px",
            "sm": f"{Space.SM}px",
            "md": f"{Space.MD}px",
            "lg": f"{Space.LG}px",
            "xl": f"{Space.XL}px"
        },
        "shadows": {
            "sm": Shadows.SM,
            "md": Shadows.MD,
            "lg": Shadows.LG
        }
    }
    COMPONENTS = {
        "kpi_card": {
            "height": ComponentSizes.KPI_HEIGHT_NORMAL,
            "header_icon_size": ComponentSizes.ICON_LG,
        },
        "gauge": {
            "height": ComponentSizes.GAUGE_HEIGHT,
            "inner_radius": ComponentSizes.GAUGE_INNER_RADIUS,
        },
        "charts": {
            "height_default": ComponentSizes.CHART_HEIGHT_MD,
            "height_sm": ComponentSizes.CHART_HEIGHT_SM,
            "height_lg": ComponentSizes.CHART_HEIGHT_LG,
        }
    }
    @staticmethod
    def get_mantine_theme() -> Dict[str, Any]:
        return MantineTheme.get_light_theme()
    @staticmethod
    def get_mantine_theme_dark() -> Dict[str, Any]:
        return MantineTheme.get_dark_theme()
    @staticmethod
    def setup_plotly_templates() -> None:
        PlotlyConfig.setup_templates()