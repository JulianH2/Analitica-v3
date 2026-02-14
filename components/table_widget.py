"""
Table Widget - Actualizado con Design System
Widget para tablas con estilos según mockups
"""

import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import Colors, DesignSystem as DS, Typography, ComponentSizes, Space

class TableWidget:
    def __init__(self, widget_id, strategy):
        self.widget_id = widget_id
        self.strategy = strategy
    
    def render(self, ctx, theme="dark"):
        return self.strategy.render(ctx, mode="dashboard", theme=theme)