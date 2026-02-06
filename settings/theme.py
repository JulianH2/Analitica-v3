from typing import Any, Dict, Final, List, TypedDict
import plotly.graph_objects as go
import plotly.io as pio

class TypographyConfig(TypedDict):
    family: str
    weights: Dict[str, int]
    sizes: Dict[str, int]
    line_heights: Dict[str, str]
    transforms: Dict[str, str]

class LayoutConfig(TypedDict):
    breakpoints: Dict[str, int]
    spacing: Dict[str, str]
    card_radius: str
    shadows: Dict[str, str]
    grid_columns: int
    default_span: int

class DesignSystem:
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

    NEXA_BG_LIGHT: Final[str] = "#f8f6f3"
    NEXA_BG_DARK: Final[str] = "#1d1d1b"
    TEXT_DARK: Final[str] = "#f2f2f2"

    SLATE: Final[List[str]] = ["#f8fafc", "#f2f2f2", "#e2e8f0", "#cbd5e1", "#94a3b8", "#808080", "#475569", "#334155", "#1d1d1b", "#0f172a"]
    BRAND: Final[List[str]] = ["#e8f4fd", "#d1e9fb", "#a3d3f7", "#75bdf3", "#47a7ef", "#418cdf", "#3570b3", "#295487", "#1d385b", "#111c2f"]
    SUCCESS: Final[List[str]] = ["#edf7ee", "#d4edd6", "#a9dbb0", "#7ec98a", "#53b764", "#4c9f54", "#3d7f43", "#2e5f32", "#1f3f21", "#101f10"]
    WARNING: Final[List[str]] = ["#fef6e8", "#fdecd1", "#fbd9a3", "#f9c675", "#f7b347", "#e9a13b", "#ba812f", "#8c6123", "#5d4017", "#2f200b"]
    DANGER: Final[List[str]] = ["#fff2f2", "#ffe6e6", "#ffcccc", "#ffb3b3", "#ff9999", "#ff0000", "#cc0000", "#990000", "#660000", "#330000"]
    INFO: Final[List[str]] = ["#e8f4fd", "#d1e9fb", "#a3d3f7", "#75bdf3", "#47a7ef", "#418cdf", "#3570b3", "#295487", "#1d385b", "#111c2f"]
    ORANGE: Final[List[str]] = ["#fef3e8", "#fde7d1", "#fbcfa3", "#f9b775", "#f79f47", "#e27f08", "#b56606", "#884d05", "#5b3403", "#2d1a01"]

    TRANSPARENT: Final[str] = "rgba(0,0,0,0)"
    WHITE: Final[str] = "#ffffff"

    COLOR_MAP: Final[Dict[str, str]] = {
        "indigo": BRAND[5],
        "blue": NEXA_BLUE,
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
    }

    CHART_COLORS: Final[List[str]] = [
        NEXA_BLUE,
        NEXA_ORANGE,
        NEXA_GREEN,
        NEXA_GOLD,
        "#808080",
        NEXA_RED,
    ]

    CHART_YEAR_COLORS: Final[Dict[str, str]] = {
        "current": NEXA_BLUE,
        "previous": NEXA_ORANGE,
        "target": NEXA_GREEN,
        "meta": "#808080",
    }

    CHART_DONUT_COLORS: Final[List[str]] = [
        NEXA_BLUE,
        NEXA_ORANGE,
        NEXA_GREEN,
        NEXA_GOLD,
        "#808080",
        NEXA_CREAM,
        NEXA_PINK_LIGHT,
    ]

    TYPOGRAPHY: Final[TypographyConfig] = {
        "family": "'Nexa', 'Montserrat', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "weights": {
            "normal": 400,
            "medium": 600,
            "bold": 800,
            "black": 900
        },
        "sizes": {
            "xs_tiny": 9,
            "xs": 10,
            "table": 11,
            "sm": 12,
            "md": 14,
            "lg": 18,
            "xl": 24,
            "xxl": 32
        },
        "line_heights": {
            "tight": "1",
            "normal": "1.5",
            "relaxed": "1.75"
        },
        "transforms": {
            "upper": "uppercase",
            "cap": "capitalize"
        }
    }

    LAYOUT: Final[LayoutConfig] = {
        "grid_columns": 12,
        "default_span": 4,
        "card_radius": "md",
        "breakpoints": {
            "xs": 0, "sm": 576, "md": 768, "lg": 992, "xl": 1200
        },
        "spacing": {
            "xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"
        },
        "shadows": {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
        }
    }

    COMPONENTS: Final[Dict[str, Any]] = {
        "kpi_card": {
            "height": 160,
            "header_icon_size": 18,
            "detail_btn_width": "100%"
        },
        "gauge": {
            "height": 220,
            "inner_radius": "75%",
        },
        "charts": {
            "height_default": 320,
            "height_sm": 250,
            "height_lg": 450,
            "bg_color": "rgba(0,0,0,0)",
            "bar_width": 0.6,
            "bar_gap": 0.15,
        }
    }

    FONT_TABLE: Final[int] = TYPOGRAPHY["sizes"]["table"]
    FONT_XS: Final[int] = TYPOGRAPHY["sizes"]["xs"]
    FONT_SM: Final[int] = TYPOGRAPHY["sizes"]["sm"]
    FONT_MD: Final[int] = TYPOGRAPHY["sizes"]["md"]

    FW_NORMAL: Final[int] = TYPOGRAPHY["weights"]["normal"]
    FW_BOLD: Final[int] = TYPOGRAPHY["weights"]["bold"]
    FW_MEDIUM: Final[int] = TYPOGRAPHY["weights"]["medium"]

    @staticmethod
    def get_mantine_theme() -> Dict[str, Any]:
        return {
            "colorScheme": "light",
            "fontFamily": DesignSystem.TYPOGRAPHY["family"],
            "primaryColor": "blue",
            "defaultRadius": DesignSystem.LAYOUT["card_radius"],
            "white": DesignSystem.NEXA_BG_LIGHT,
            "black": DesignSystem.NEXA_BLACK,
            "colors": {
                "indigo": DesignSystem.BRAND,
                "dark": DesignSystem.SLATE,
                "gray": DesignSystem.SLATE,
                "green": DesignSystem.SUCCESS,
                "yellow": DesignSystem.WARNING,
                "red": DesignSystem.DANGER,
                "blue": DesignSystem.INFO,
                "orange": DesignSystem.ORANGE,
            },
            "components": {
                "Button": {"defaultProps": {"size": "sm", "fw": 600, "radius": "md"}},
                "Paper": {"defaultProps": {"withBorder": True, "shadow": "md"}},
                "Card": {"defaultProps": {"withBorder": True, "shadow": "md", "radius": "lg"}}
            }
        }

    @staticmethod
    def get_mantine_theme_dark() -> Dict[str, Any]:
        theme = DesignSystem.get_mantine_theme()
        theme["colorScheme"] = "dark"
        theme["white"] = DesignSystem.NEXA_BG_DARK
        theme["black"] = DesignSystem.TEXT_DARK
        return theme

    @staticmethod
    def setup_plotly_templates():
        base_layout = dict(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(t=35, b=35, l=45, r=20),
            colorway=DesignSystem.CHART_COLORS,
            font=dict(
                family=DesignSystem.TYPOGRAPHY["family"],
                color=DesignSystem.NEXA_BLACK,
                size=11
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=DesignSystem.SLATE[2],
                gridwidth=1,
                zeroline=False,
                tickfont=dict(size=10, color=DesignSystem.NEXA_GRAY)
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            bargap=0.18,
            bargroupgap=0.12,
        )
        pio.templates["zam_clean"] = go.layout.Template(layout=base_layout)
        pio.templates.default = "zam_clean"

class SemanticColors:
    INGRESO: Final[str] = DesignSystem.NEXA_GREEN
    EGRESO: Final[str] = DesignSystem.NEXA_RED
    PROFIT: Final[str] = DesignSystem.NEXA_BLUE
    TEXT_MAIN: Final[str] = DesignSystem.NEXA_BLACK
    TEXT_MUTED: Final[str] = DesignSystem.NEXA_GRAY
    BORDER: Final[str] = DesignSystem.SLATE[2]

DesignSystem.setup_plotly_templates()
