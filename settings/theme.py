import plotly.graph_objects as go
import plotly.io as pio
from typing import Any

class DesignSystem:
    # --- 1. PALETAS DE COLORES MAESTRAS (Tus Hex personalizados) ---
    SLATE = ["#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8", "#64748b", "#475569", "#334155", "#1e293b", "#0f172a"]
    BRAND = ["#eef2ff", "#e0e7ff", "#c7d2fe", "#a5b4fc", "#818cf8", "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81"]
    SUCCESS = ["#f0fdf4", "#dcfce7", "#bbf7d0", "#86efac", "#4ade80", "#22c55e", "#16a34a", "#15803d", "#166534", "#14532d"]
    WARNING = ["#fffbeb", "#fef3c7", "#fde68a", "#fcd34d", "#fbbf24", "#f59e0b", "#d97706", "#b45309", "#92400e", "#78350f"]
    DANGER  = ["#fef2f2", "#fee2e2", "#fecaca", "#fca5a5", "#f87171", "#ef4444", "#dc2626", "#b91c1c", "#991b1b", "#7f1d1d"]
    
    CHART_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]

    # --- 2. CONFIGURACIÓN MANTINE (UI) ---
    @staticmethod
    def get_mantine_theme() -> Any:
        return {
            "fontFamily": "'Inter', sans-serif",
            "primaryColor": "indigo", # Usamos un nombre estándar como primario
            "defaultRadius": "md",
            "colors": {
                # AQUI ESTÁ EL TRUCO: Reemplazamos los estándar con tus HEX
                "indigo": DesignSystem.BRAND,    # "brand" ahora es "indigo"
                "dark": DesignSystem.SLATE,
                "gray": DesignSystem.SLATE,
                "green": DesignSystem.SUCCESS,   # "success" ahora es "green"
                "yellow": DesignSystem.WARNING,  # "warning" ahora es "yellow"
                "red": DesignSystem.DANGER,      # "danger" ahora es "red"
            },
            "components": {
                "Paper": {"defaultProps": {"withBorder": True, "radius": "md", "shadow": "sm"}},
                "AppShell": {"styles": {"main": {"transition": "padding-left 200ms ease"}}}
            }
        }

    # --- 3. CONFIGURACIÓN PLOTLY ---
    # (Esto se queda igual, ya que Plotly usa los hex directos)
    @staticmethod
    def setup_plotly_templates():
        common_layout = {
            "font": {"family": "Inter, sans-serif"},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "colorway": DesignSystem.CHART_COLORS,
            "margin": {"t": 40, "b": 30, "l": 40, "r": 30},
        }
        # Tema Oscuro
        dark = go.layout.Template()
        dark.layout = {
            **common_layout,
            "font": {"color": DesignSystem.SLATE[3]},
            "xaxis": {"gridcolor": DesignSystem.SLATE[7], "linecolor": DesignSystem.SLATE[6], "tickcolor": DesignSystem.SLATE[4]},
            "yaxis": {"gridcolor": DesignSystem.SLATE[7], "linecolor": DesignSystem.SLATE[6], "tickcolor": DesignSystem.SLATE[4]},
        }
        pio.templates["zam_dark"] = dark

        # Tema Claro
        light = go.layout.Template()
        light.layout = {
            **common_layout,
            "font": {"color": DesignSystem.SLATE[6]},
            "xaxis": {"gridcolor": DesignSystem.SLATE[2], "linecolor": DesignSystem.SLATE[3], "tickcolor": DesignSystem.SLATE[5]},
            "yaxis": {"gridcolor": DesignSystem.SLATE[2], "linecolor": DesignSystem.SLATE[3], "tickcolor": DesignSystem.SLATE[5]},
        }
        pio.templates["zam_light"] = light
        pio.templates.default = "zam_dark"

# --- 4. COLORES SEMÁNTICOS (Para lógica interna) ---
class SemanticColors:
    # Ahora mapeamos a los nombres estándar de Mantine
    INGRESO = "green"   # Antes "success"
    EGRESO = "red"      # Antes "danger"
    SALDO = "indigo"    # Antes "brand"
    DEUDA = "indigo"
    
    # Hexadecimales directos para Plotly
    META = DesignSystem.BRAND[5]
    PELIGRO = DesignSystem.WARNING[5]
    CRITICO = DesignSystem.DANGER[5]
    NEUTRO = DesignSystem.SLATE[5]
    
    BRAND_PRIMARY = "indigo"