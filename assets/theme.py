import plotly.graph_objects as go
import plotly.io as pio

# --- 1. CONFIGURACIÓN SEMÁNTICA (NEGOCIO) ---
class SemanticColors:
    """
    Fuente de verdad para los colores del negocio.
    Las estrategias usan ESTOS nombres, no hex.
    """
    # Flujos Financieros
    INGRESO = "teal"        # Dinero entrando
    EGRESO = "red"          # Dinero saliendo
    SALDO = "blue"          # Estado actual
    DEUDA = "indigo"        # CxP / CxC
    
    # Estados
    META = "cyan"
    PELIGRO = "orange"
    CRITICO = "red"
    NEUTRO = "gray"
    
    # Marca
    BRAND_PRIMARY = "indigo"
    BRAND_SECONDARY = "violet"

# --- 2. SISTEMA DE DISEÑO (VISUAL) ---
class DesignSystem:
    # Escala de Grises (Slate)
    SLATE = [
        "#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#94a3b8",
        "#64748b", "#475569", "#334155", "#1e293b", "#0f172a"
    ]
    
    # Paleta para Gráficas (Plotly Colorway)
    CHART_COLORS = [
        "#3b82f6", # Blue 500
        "#10b981", # Emerald 500
        "#f59e0b", # Amber 500
        "#ef4444", # Red 500
        "#8b5cf6", # Violet 500
        "#ec4899"  # Pink 500
    ]

    @staticmethod
    def setup_plotly_templates():
        """Configura los temas de Plotly para toda la app"""
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
            "font": {"color": "#cbd5e1"},
            "xaxis": {"gridcolor": "#334155", "linecolor": "#475569", "tickcolor": "#94a3b8"},
            "yaxis": {"gridcolor": "#334155", "linecolor": "#475569", "tickcolor": "#94a3b8"},
        }
        pio.templates["zam_dark"] = dark

        # Tema Claro
        light = go.layout.Template()
        light.layout = {
            **common_layout,
            "font": {"color": "#1e293b"},
            "xaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1", "tickcolor": "#64748b"},
            "yaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1", "tickcolor": "#64748b"},
        }
        pio.templates["zam_light"] = light
        
        # Default
        pio.templates.default = "zam_light"