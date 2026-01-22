from typing import Any, Dict, Final, List, Literal, TypedDict
import plotly.graph_objects as go
import plotly.io as pio

# --- 1. DEFINICIONES DE TIPO ---
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

    SLATE: Final[List[str]] = ["#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8", "#64748b", "#475569", "#334155", "#1e293b", "#0f172a"]
    BRAND: Final[List[str]] = ["#eef2ff", "#e0e7ff", "#c7d2fe", "#a5b4fc", "#818cf8", "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81"]
    SUCCESS: Final[List[str]] = ["#f0fdf4", "#dcfce7", "#bbf7d0", "#86efac", "#4ade80", "#22c55e", "#16a34a", "#15803d", "#166534", "#14532d"]
    WARNING: Final[List[str]] = ["#fffbeb", "#fef3c7", "#fde68a", "#fcd34d", "#fbbf24", "#f59e0b", "#d97706", "#b45309", "#92400e", "#78350f"]
    DANGER: Final[List[str]] = ["#fef2f2", "#fee2e2", "#fecaca", "#fca5a5", "#f87171", "#ef4444", "#dc2626", "#b91c1c", "#991b1b", "#7f1d1d"]
    INFO: Final[List[str]] = ["#f0f9ff", "#e0f2fe", "#bae6fd", "#7dd3fc", "#38bdf8", "#0ea5e9", "#0284c7", "#0369a1", "#075985", "#0c4a6e"]

    TRANSPARENT: Final[str] = "rgba(0,0,0,0)"
    WHITE: Final[str] = "#ffffff"

    COLOR_MAP: Final[Dict[str, str]] = {
        "indigo": BRAND[5],
        "blue": INFO[5],
        "green": SUCCESS[5],
        "emerald": SUCCESS[5],
        "yellow": WARNING[5],
        "amber": WARNING[5],
        "orange": "#f97316",
        "red": DANGER[5],
        "rose": "#f43f5e",
        "slate": SLATE[5],
        "gray": SLATE[5],
        "dark": SLATE[8],
        "black": SLATE[9],
        "cyan": "#06b6d4",
        "teal": "#14b8a6",
        "violet": "#8b5cf6",
        "grape": "#be4bdb",
        "pink": "#ec4899",
        "lime": "#84cc16",
    }

    CHART_COLORS: Final[List[str]] = [
        BRAND[5], SUCCESS[5], WARNING[5], "#ec4899", "#8b5cf6", "#06b6d4"
    ]

    TYPOGRAPHY: Final[TypographyConfig] = {
        "family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "weights": {
            "normal": 400, 
            "medium": 500, 
            "bold": 700, 
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
            "bg_color": "rgba(0,0,0,0)"
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
            "primaryColor": "indigo",
            "defaultRadius": DesignSystem.LAYOUT["card_radius"],
            "white": "#ffffff",
            "black": DesignSystem.SLATE[9],
            "colors": {
                "indigo": DesignSystem.BRAND, 
                "dark": DesignSystem.SLATE, 
                "gray": DesignSystem.SLATE,
                "green": DesignSystem.SUCCESS, 
                "yellow": DesignSystem.WARNING, 
                "red": DesignSystem.DANGER, 
                "blue": DesignSystem.INFO
            },
            "components": {
                "Button": {"defaultProps": {"size": "sm", "fw": 500}},
                "Paper": {"defaultProps": {"withBorder": True, "shadow": "sm"}},
                "Card": {"defaultProps": {"withBorder": True, "shadow": "sm", "radius": "md"}}
            }
        }

    @staticmethod
    def setup_plotly_templates():
        base_layout = dict(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(t=30, b=10, l=10, r=10),
            colorway=DesignSystem.CHART_COLORS,
            font=dict(
                family=DesignSystem.TYPOGRAPHY["family"],
                color=DesignSystem.SLATE[7]
            ),
            xaxis=dict(
                showgrid=False, 
                zeroline=False,
                tickfont=dict(size=10, color=DesignSystem.SLATE[5])
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor=DesignSystem.SLATE[2],
                zeroline=False,
                tickfont=dict(size=10, color=DesignSystem.SLATE[5])
            ),
        )
        clean_theme = go.layout.Template(layout=base_layout)
        pio.templates["zam_clean"] = clean_theme
        pio.templates.default = "zam_clean"

class SemanticColors:
    INGRESO: Final[str] = DesignSystem.SUCCESS[6] 
    EGRESO: Final[str] = DesignSystem.DANGER[5]
    PROFIT: Final[str] = DesignSystem.BRAND[6]
    
    TEXT_MAIN: Final[str] = DesignSystem.SLATE[8]
    TEXT_MUTED: Final[str] = DesignSystem.SLATE[5]
    BORDER: Final[str] = DesignSystem.SLATE[2]

DesignSystem.setup_plotly_templates()