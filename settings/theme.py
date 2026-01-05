import plotly.graph_objects as go
import plotly.io as pio

class DesignSystem:
    # 1. PALETA "SLATE" (Base Enterprise)
    SLATE = [
        "#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8",
        "#64748b", "#475569", "#334155", "#1e293b", "#0f172a"
    ]
    
    # 2. BRAND "INDIGO" (Primario)
    BRAND = [
        "#eef2ff", "#e0e7ff", "#c7d2fe", "#a5b4fc", "#818cf8",
        "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81"
    ]

    # 3. SEMÁFOROS (Ajustados para no chillar en modo oscuro)
    SUCCESS = ["#f0fdf4", "#dcfce7", "#bbf7d0", "#86efac", "#4ade80", "#22c55e", "#16a34a", "#15803d", "#166534", "#14532d"]
    WARNING = ["#fffbeb", "#fef3c7", "#fde68a", "#fcd34d", "#fbbf24", "#f59e0b", "#d97706", "#b45309", "#92400e", "#78350f"]
    DANGER =  ["#fef2f2", "#fee2e2", "#fecaca", "#fca5a5", "#f87171", "#ef4444", "#dc2626", "#b91c1c", "#991b1b", "#7f1d1d"]

    # 4. CHART COLORS (Plotly)
    CHART_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]

    @staticmethod
    def get_mantine_theme():
        return {
            "colorScheme": "dark",
            "fontFamily": "'Inter', sans-serif",
            "primaryColor": "brand",
            "defaultRadius": "md",
            "colors": {
                "brand": DesignSystem.BRAND,
                "dark": DesignSystem.SLATE, 
                "gray": DesignSystem.SLATE, 
                "success": DesignSystem.SUCCESS,
                "warning": DesignSystem.WARNING,
                "danger": DesignSystem.DANGER,
            },
            "components": {
                "Paper": {
                    "defaultProps": {"withBorder": True, "radius": "md", "shadow": "sm"}
                },
                "Card": {
                    "defaultProps": {"withBorder": True, "radius": "md", "shadow": "sm"}
                },
                "Text": {
                    "defaultProps": {"c": "dimmed"} 
                },
                "Title": {
                    "defaultProps": {"order": 3} 
                },
                "AppShell": {
                    "styles": {
                        "main": {"backgroundColor": "var(--mantine-color-body)"}
                    }
                }
            }
        }

    @staticmethod
    def setup_plotly_templates():
        common_layout = {
            "font": {"family": "Inter, sans-serif"},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "colorway": DesignSystem.CHART_COLORS,
            "margin": {"t": 40, "b": 30, "l": 40, "r": 30},
        }

        dark = go.layout.Template()
        dark.layout = {
            **common_layout,
            "font": {"color": "#cbd5e1"},
            "xaxis": {"gridcolor": "#334155", "linecolor": "#475569", "tickcolor": "#94a3b8"}, # Slate 7/6/4
            "yaxis": {"gridcolor": "#334155", "linecolor": "#475569", "tickcolor": "#94a3b8"},
        }
        pio.templates["zam_dark"] = dark

        light = go.layout.Template()
        light.layout = {
            **common_layout,
            "font": {"color": "#475569"},
            "xaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1", "tickcolor": "#64748b"}, # Slate 2/3/5
            "yaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1", "tickcolor": "#64748b"},
        }
        pio.templates["zam_light"] = light
        
        pio.templates.default = "zam_dark"