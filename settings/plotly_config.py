"""
Plotly Configuration - Templates Unificados
Basado en los colores EXACTOS de design_system.py y mockups oficiales

UBICACIÓN: settings/plotly_config.py
"""

import plotly.graph_objects as go
import plotly.io as pio


class PlotlyConfig:
    """
    Configuración centralizada de templates de Plotly
    
    Colores sincronizados con design_system.py:
    - AnaliticaZAM-V4.pdf (tema claro)
    - nocturno_AnaliticaZAM-V4.pdf (tema oscuro)
    """
    
    # === COLORES DEL DESIGN SYSTEM ===
    
    # Tema Claro
    BG_LIGHT = "#FFFFFF"
    BG_LIGHT_SECONDARY = "#f2f2f2"
    TEXT_LIGHT = "#1d1d1b"
    TEXT_LIGHT_SECONDARY = "#808080"
    
    # Tema Oscuro (CORREGIDOS - coinciden con PDF)
    BG_DARK = "#62686e"            # ✅ Fondo principal gris del PDF
    BG_DARK_SECONDARY = "#3b4249"
    TEXT_DARK = "#e8eaed"          # Texto principal
    TEXT_DARK_SECONDARY = "#9ca3af" # Texto secundario
    PLOT_GRID_DARK = "#4a5a68"     # Grillas sutiles
    
    # Colores de Gráficas (iguales en ambos temas)
    CHART_BLUE = "#418cdf"
    CHART_BLUE_LIGHT = "#80abd4"
    CHART_GRAY = "#bec4c6"
    CHART_GOLD = "#f9daa0"
    CHART_ORANGE = "#e27f07"
    
    # Semánticos
    POSITIVE = "#4c9f54"
    POSITIVE_LIGHT = "#62c26d"
    POSITIVE_BG = "#b9efbc"
    
    NEUTRAL = "#e9a13b"
    NEUTRAL_BG = "#f9daa0"
    
    NEGATIVE = "#ff0000"
    NEGATIVE_BG = "#fccaca"
    
    # Paleta de colores para series múltiples
    CHART_PALETTE = [
        CHART_BLUE,      # Azul principal
        CHART_GOLD,      # Dorado
        CHART_GRAY,      # Gris
        CHART_ORANGE,    # Naranja
        POSITIVE,        # Verde
        NEGATIVE,        # Rojo
        CHART_BLUE_LIGHT,# Azul claro
        NEUTRAL,         # Dorado oscuro
    ]
    
    # Tipografía
    FONT_FAMILY = "'Nexa', 'Montserrat', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    FONT_SIZE_BASE = 11
    FONT_SIZE_TITLE = 14
    FONT_SIZE_AXIS = 10
    
    @staticmethod
    def setup_templates():
        """
        Configura los templates globales de Plotly
        Llamar UNA VEZ al inicio de la aplicación en app.py
        """
        
        # === TEMPLATE TEMA CLARO ===
        pio.templates["zam_light"] = go.layout.Template(
            layout=go.Layout(
                # Fondos transparentes (el Paper de Mantine maneja el fondo)
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                
                # Tipografía
                font=dict(
                    family=PlotlyConfig.FONT_FAMILY,
                    size=PlotlyConfig.FONT_SIZE_BASE,
                    color=PlotlyConfig.TEXT_LIGHT
                ),
                
                # Título
                title=dict(
                    font=dict(
                        family=PlotlyConfig.FONT_FAMILY,
                        size=PlotlyConfig.FONT_SIZE_TITLE,
                        color=PlotlyConfig.TEXT_LIGHT
                    ),
                    x=0.5,
                    xanchor='center'
                ),
                
                # Ejes X
                xaxis=dict(
                    gridcolor=PlotlyConfig.BG_LIGHT_SECONDARY,  # Grillas sutiles
                    linecolor=PlotlyConfig.TEXT_LIGHT_SECONDARY,
                    tickfont=dict(
                        size=PlotlyConfig.FONT_SIZE_AXIS,
                        color=PlotlyConfig.TEXT_LIGHT_SECONDARY
                    ),
                    title=dict(
                        font=dict(
                            size=PlotlyConfig.FONT_SIZE_BASE,
                            color=PlotlyConfig.TEXT_LIGHT
                        )
                    )
                ),
                
                # Ejes Y
                yaxis=dict(
                    gridcolor=PlotlyConfig.BG_LIGHT_SECONDARY,
                    linecolor=PlotlyConfig.TEXT_LIGHT_SECONDARY,
                    tickfont=dict(
                        size=PlotlyConfig.FONT_SIZE_AXIS,
                        color=PlotlyConfig.TEXT_LIGHT_SECONDARY
                    ),
                    title=dict(
                        font=dict(
                            size=PlotlyConfig.FONT_SIZE_BASE,
                            color=PlotlyConfig.TEXT_LIGHT
                        )
                    )
                ),
                
                # Paleta de colores
                colorway=PlotlyConfig.CHART_PALETTE,
                
                # Hover
                hovermode='closest',
                hoverlabel=dict(
                    bgcolor="white",
                    bordercolor=PlotlyConfig.TEXT_LIGHT_SECONDARY,
                    font=dict(
                        family=PlotlyConfig.FONT_FAMILY,
                        size=PlotlyConfig.FONT_SIZE_BASE,
                        color=PlotlyConfig.TEXT_LIGHT
                    )
                ),
                
                # Leyenda
                legend=dict(
                    font=dict(
                        family=PlotlyConfig.FONT_FAMILY,
                        size=PlotlyConfig.FONT_SIZE_BASE,
                        color=PlotlyConfig.TEXT_LIGHT
                    ),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor=PlotlyConfig.BG_LIGHT_SECONDARY,
                    borderwidth=1
                ),
                
                # Márgenes por defecto
                margin=dict(l=40, r=20, t=30, b=30),
                
                # Responsive
                autosize=True,
            )
        )
        
        # === TEMPLATE TEMA OSCURO ===
        pio.templates["zam_dark"] = go.layout.Template(
            layout=go.Layout(
                # Fondos transparentes
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                
                # Tipografía
                font=dict(
                    family=PlotlyConfig.FONT_FAMILY,
                    size=PlotlyConfig.FONT_SIZE_BASE,
                    color=PlotlyConfig.TEXT_DARK
                ),
                
                # Título
                title=dict(
                    font=dict(
                        family=PlotlyConfig.FONT_FAMILY,
                        size=PlotlyConfig.FONT_SIZE_TITLE,
                        color=PlotlyConfig.TEXT_DARK
                    ),
                    x=0.5,
                    xanchor='center'
                ),
                
                # Ejes X
                xaxis=dict(
                    gridcolor=PlotlyConfig.PLOT_GRID_DARK,  # Grillas del PDF oscuro
                    linecolor=PlotlyConfig.TEXT_DARK_SECONDARY,
                    tickfont=dict(
                        size=PlotlyConfig.FONT_SIZE_AXIS,
                        color=PlotlyConfig.TEXT_DARK_SECONDARY
                    ),
                    title=dict(
                        font=dict(
                            size=PlotlyConfig.FONT_SIZE_BASE,
                            color=PlotlyConfig.TEXT_DARK
                        )
                    ),
                    zerolinecolor=PlotlyConfig.PLOT_GRID_DARK
                ),
                
                # Ejes Y
                yaxis=dict(
                    gridcolor=PlotlyConfig.PLOT_GRID_DARK,
                    linecolor=PlotlyConfig.TEXT_DARK_SECONDARY,
                    tickfont=dict(
                        size=PlotlyConfig.FONT_SIZE_AXIS,
                        color=PlotlyConfig.TEXT_DARK_SECONDARY
                    ),
                    title=dict(
                        font=dict(
                            size=PlotlyConfig.FONT_SIZE_BASE,
                            color=PlotlyConfig.TEXT_DARK
                        )
                    ),
                    zerolinecolor=PlotlyConfig.PLOT_GRID_DARK
                ),
                
                # Paleta de colores (mismos que tema claro)
                colorway=PlotlyConfig.CHART_PALETTE,
                
                # Hover
                hovermode='closest',
                hoverlabel=dict(
                    bgcolor=PlotlyConfig.BG_DARK_SECONDARY,
                    bordercolor=PlotlyConfig.TEXT_DARK_SECONDARY,
                    font=dict(
                        family=PlotlyConfig.FONT_FAMILY,
                        size=PlotlyConfig.FONT_SIZE_BASE,
                        color=PlotlyConfig.TEXT_DARK
                    )
                ),
                
                # Leyenda
                legend=dict(
                    font=dict(
                        family=PlotlyConfig.FONT_FAMILY,
                        size=PlotlyConfig.FONT_SIZE_BASE,
                        color=PlotlyConfig.TEXT_DARK
                    ),
                    bgcolor="rgba(59, 66, 73, 0.8)",  # #3b4249 con 80% opacidad
                    bordercolor=PlotlyConfig.PLOT_GRID_DARK,
                    borderwidth=1
                ),
                
                # Márgenes por defecto
                margin=dict(l=40, r=20, t=30, b=30),
                
                # Responsive
                autosize=True,
            )
        )
        
        # Establecer template por defecto
        pio.templates.default = "zam_light"
        
        print("✅ Templates de Plotly configurados:")
        print(f"   - zam_light (fondo: {PlotlyConfig.BG_LIGHT})")
        print(f"   - zam_dark (fondo: {PlotlyConfig.BG_DARK})")
    
    @staticmethod
    def get_base_layout(theme: str = "light") -> dict:
        """
        Obtiene layout base para una gráfica
        
        Args:
            theme: "light" o "dark"
        
        Returns:
            Dict con configuración base
        """
        template = "zam_dark" if theme == "dark" else "zam_light"
        
        return {
            "template": template,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
        }
    
    @staticmethod
    def apply_theme_to_figure(fig, theme: str = "light"):
        """
        Aplica tema a una figura existente
        
        Args:
            fig: Figura de Plotly
            theme: "light" o "dark"
        
        Returns:
            Figura con tema aplicado
        """
        template = "zam_dark" if theme == "dark" else "zam_light"
        fig.update_layout(template=template)
        return fig


# === HELPERS PARA GRÁFICAS ESPECÍFICAS ===

class ChartStyles:
    """Estilos específicos para diferentes tipos de gráficas"""
    
    @staticmethod
    def get_bar_config(theme: str = "light") -> dict:
        """Configuración para gráficas de barras"""
        return {
            **PlotlyConfig.get_base_layout(theme),
            "barmode": "group",
            "bargap": 0.15,
            "bargroupgap": 0.1,
        }
    
    @staticmethod
    def get_line_config(theme: str = "light") -> dict:
        """Configuración para gráficas de líneas"""
        return {
            **PlotlyConfig.get_base_layout(theme),
            "hovermode": "x unified",
        }
    
    @staticmethod
    def get_pie_config(theme: str = "light") -> dict:
        """Configuración para gráficas de pastel/donut"""
        return {
            **PlotlyConfig.get_base_layout(theme),
            "showlegend": True,
        }


def get_semantic_color(value: float, threshold_positive: float = 0, 
                       threshold_negative: float = 0, inverse: bool = False) -> str:
    """
    Obtiene color semántico basado en valor
    
    Args:
        value: Valor numérico
        threshold_positive: Umbral para positivo
        threshold_negative: Umbral para negativo
        inverse: Invertir lógica (para métricas donde menos es mejor)
    
    Returns:
        Color hex
    """
    if inverse:
        if value < threshold_negative:
            return PlotlyConfig.POSITIVE
        elif value > threshold_positive:
            return PlotlyConfig.NEGATIVE
        else:
            return PlotlyConfig.NEUTRAL
    else:
        if value > threshold_positive:
            return PlotlyConfig.POSITIVE
        elif value < threshold_negative:
            return PlotlyConfig.NEGATIVE
        else:
            return PlotlyConfig.NEUTRAL