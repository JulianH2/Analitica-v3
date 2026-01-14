import plotly.graph_objects as go
import plotly.io as pio
from typing import Any, Dict

class DesignSystem:
    SLATE = ["#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8", "#64748b", "#475569", "#334155", "#1e293b", "#0f172a"]
    BRAND = ["#eef2ff", "#e0e7ff", "#c7d2fe", "#a5b4fc", "#818cf8", "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81"]
    SUCCESS = ["#f0fdf4", "#dcfce7", "#bbf7d0", "#86efac", "#4ade80", "#22c55e", "#16a34a", "#15803d", "#166534", "#14532d"]
    WARNING = ["#fffbeb", "#fef3c7", "#fde68a", "#fcd34d", "#fbbf24", "#f59e0b", "#d97706", "#b45309", "#92400e", "#78350f"]
    DANGER = ["#fef2f2", "#fee2e2", "#fecaca", "#fca5a5", "#f87171", "#ef4444", "#dc2626", "#b91c1c", "#991b1b", "#7f1d1d"]

    CHART_COLORS = [BRAND[5], SUCCESS[5], WARNING[5], DANGER[5], "#8b5cf6", "#ec4899", "#06b6d4"]

    GAUGE_HEIGHT = 250  
    STANDARD_CHART_HEIGHT = 420

    COLOR_MAP: Dict[str, str] = {
        "indigo": BRAND[5], "blue": BRAND[5], "green": SUCCESS[5], "teal": SUCCESS[5],
        "red": DANGER[5], "yellow": WARNING[5], "orange": WARNING[5], "gray": SLATE[5]
    }

    @staticmethod
    def get_mantine_theme() -> Dict[str, Any]:
        return {
            "fontFamily": "'Inter', sans-serif",
            "primaryColor": "indigo",
            "defaultRadius": "md",
            "colors": {
                "indigo": DesignSystem.BRAND, "dark": DesignSystem.SLATE, "gray": DesignSystem.SLATE,
                "green": DesignSystem.SUCCESS, "yellow": DesignSystem.WARNING, "red": DesignSystem.DANGER,
            }
        }

    @staticmethod
    def setup_plotly_templates():
        base_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=40, b=20, l=10, r=10),
            colorway=DesignSystem.CHART_COLORS,
        )
        dark_layout = dict(
            **base_layout,
            font=dict(family="Inter, sans-serif", size=12, color="#ffffff"),
            xaxis=dict(gridcolor="#334155", tickfont=dict(color="#cbd5e1"), showgrid=True, zeroline=False),
            yaxis=dict(gridcolor="#334155", tickfont=dict(color="#cbd5e1"), showgrid=True, zeroline=False),
            legend=dict(font=dict(color="#ffffff"), orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
        )
        light_layout = dict(
            **base_layout,
            font=dict(family="Inter, sans-serif", size=12, color="#1e293b"),
            xaxis=dict(gridcolor="#e2e8f0", tickfont=dict(color="#475569"), showgrid=True, zeroline=False),
            yaxis=dict(gridcolor="#e2e8f0", tickfont=dict(color="#475569"), showgrid=True, zeroline=False),
            legend=dict(font=dict(color="#1e293b"), orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
        )
        pio.templates["zam_dark"] = go.layout.Template(layout=dark_layout)
        pio.templates["zam_light"] = go.layout.Template(layout=light_layout)
        pio.templates.default = "zam_dark"

class SemanticColors:
    INGRESO = DesignSystem.SUCCESS[5]
    EGRESO = DesignSystem.DANGER[5]
    META = DesignSystem.WARNING[5]
    NEUTRO = DesignSystem.SLATE[4]