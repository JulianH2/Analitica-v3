import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, Any
from .base_strategy import KPIStrategy
from services.data_manager import DataManager

data_manager = DataManager()

class TripsStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]:
        val = 716
        meta = 720
        trend = -0.5
        return {"title": "Viajes Totales", "value": str(val), "meta_text": f"Meta: {meta}", "trend": trend, "icon": "tabler:truck", "color": "orange"}
    
    def render_detail(self, data_context):
        return dmc.Stack([dmc.Alert("Volumen de tráfico vs periodo anterior.", color="orange", variant="light")])

class FleetEfficiencyStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]:
        val = 1.91
        return {"title": "Rendimiento", "value": f"{val} km/L", "meta_text": "Meta: 2.1 km/L", "trend": -9.0, "icon": "tabler:gas-station", "color": "cyan"}
    
    def render_detail(self, data_context):
        return dmc.Text("Detalle de eficiencia de combustible.")

class UnitCostStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]:
        val = 12.50
        return {"title": "Costo por Km", "value": f"${val:.2f}", "meta_text": "Costo Viaje / Km", "trend": 0, "icon": "tabler:calculator", "color": "indigo", "reverse_trend": True}
    def render_detail(self, data_context): return dmc.Text("Desglose de costos...")

class UnitUtilizationStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]:
        return {"title": "Unidades Activas", "value": "85", "meta_text": "En operación", "trend": 0, "icon": "tabler:bus", "color": "teal"}
    def render_detail(self, data_context): return dmc.Text("Lista de unidades...")

class ClientImpactStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]:
        return {"title": "Clientes Activos", "value": "12", "meta_text": "Periodo actual", "trend": 0, "icon": "tabler:users", "color": "violet"}
    def render_detail(self, data_context): return dmc.Text("Lista de clientes...")

class GaugeKPIStrategy(KPIStrategy):
    def __init__(self, kpi_key, title, color):
        self.kpi_key = kpi_key
        self.title = title
        self.color = color

    def get_card_config(self, data_context) -> Dict[str, Any]:
        return {"title": self.title}

    def get_figure(self, data_context):
        val = 75 
        meta = 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=val,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': meta, 'increasing': {'color': "green"}},
            number={'prefix': ""},
            title={'text': ""},
            gauge={
                'axis': {'range': [None, meta * 1.2], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': self.color},
                'bgcolor': "white",
                'borderwidth': 0,
                'steps': [{'range': [0, meta], 'color': "#f8f9fa"}],
            }
        ))
        
        fig.update_layout(
            height=160, 
            margin=dict(l=25, r=25, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "darkblue", 'family': "Inter, sans-serif"}
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text(f"Detalle histórico de {self.title}")

class MonthlyComparisonStrategy(KPIStrategy):
    def __init__(self, metric_name, color):
        self.metric_name = metric_name
        self.color = color

    def get_card_config(self, data_context) -> Dict[str, Any]:
        return {"title": f"{self.metric_name} vs Anterior"}

    def get_figure(self, data_context):
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        actual = [25, 22, 24, 25, 22, 24, 14, 28, 22, 24, 18, 19]
        anterior = [19, 20, 22, 20, 20, 21, 25, 20, 18, 20, 15, 16]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='24', x=meses, y=anterior, marker_color='#adb5bd'))
        fig.add_trace(go.Bar(name='25', x=meses, y=actual, marker_color=self.color))

        fig.update_layout(
            barmode='group', height=200, margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True, legend=dict(orientation="h", y=1.1, x=1),
            title=dict(text=f"<b>{self.metric_name} comparativo</b>", font=dict(size=12))
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Alert(f"Análisis mensual de {self.metric_name}", color="blue", variant="light")

class OpsPieStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]: return {"title": "Mix Operativo"}
    def get_figure(self, data_context):
        fig = go.Figure(data=[go.Pie(labels=['Full', 'Sencillo', 'Refrig.'], values=[35, 40, 25], hole=.6, marker_colors=["#228be6", "#40c057", "#fab005"])])
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), showlegend=True, legend=dict(orientation="h", y=-0.1))
        return fig
    def render_detail(self, data_context): return None

class BalanceUnitStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]: return {"title": "Top Ingreso Unidad"}
    def get_figure(self, data_context):
        fig = go.Figure(go.Bar(x=[144, 99, 107, 143, 154], y=['U-101', 'U-102', 'U-103', 'U-104', 'U-105'], orientation='h', marker_color="#228be6"))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        return fig
    def render_detail(self, data_context): return None

class PerformanceGaugeStrategy(KPIStrategy):
    def __init__(self, title, value, meta, suffix=""):
        self.title = title
        self.value = value
        self.meta = meta
        self.suffix = suffix

    def get_card_config(self, data_context) -> Dict[str, Any]: return {"title": self.title}
    
    def get_figure(self, data_context):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = self.value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            delta = {'reference': self.meta, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}, "position": "bottom"},
            number = {'suffix': self.suffix, 'font': {'size': 24, 'color': "#228be6"}},
            gauge = {
                'axis': {'range': [None, self.meta*1.5], 'visible': False},
                'bar': {'color': "#228be6"}, 
                'bgcolor': "white", 
                'borderwidth': 0,
                'steps': [{'range': [0, self.meta], 'color': "#e7f5ff"}],
            }
        ))
        fig.update_layout(height=140, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)')
        return fig
    def render_detail(self, data_context): return dmc.Text(f"Detalle de {self.title}")

class PerformanceTrendStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]: return {"title": "Rendimiento Real 2025 vs 2024"}
    def get_figure(self, data_context):
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        real = [2.8, 1.9, 1.95, 2.0, 1.98, 2.05, 2.1, 2.0, 1.95, 2.0, 1.9, 1.95]
        meta = [1.95] * 12
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses, y=real, name="Real", marker_color="#228be6"))
        fig.add_trace(go.Scatter(x=meses, y=meta, name="Meta", mode='lines+markers', line=dict(color='#fd7e14', width=2)))
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", y=1.1), title=dict(text="<b>Rendimiento Real vs Meta</b>", font=dict(size=12)))
        return fig
    def render_detail(self, data_context): return None

class PerformanceMixStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]: return {"title": "Rend. por Tipo Op."}
    def get_figure(self, data_context):
        fig = go.Figure(data=[go.Pie(labels=['Foráneo', 'Local', 'Patio'], values=[60, 30, 10], hole=.6, marker_colors=["#228be6", "#fab005", "#e9ecef"], textinfo='percent')])
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=20, b=10), showlegend=True)
        return fig
    def render_detail(self, data_context): return None

class CostConceptStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]: return {"title": "Costo por Clasificación"}
    def get_figure(self, data_context):
        concepts = ["Combustible", "Sueldos", "Llantas", "Mtto", "Peajes"]
        values = [8.5, 4.2, 1.5, 1.2, 0.8]
        fig = go.Figure(go.Bar(x=values, y=concepts, orientation='h', marker_color="#228be6", text=[f"${v}M" for v in values], textposition="auto"))
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(autorange="reversed"))
        return fig
    def render_detail(self, data_context): return None

class CostTrendVerticalStrategy(KPIStrategy):
    def get_card_config(self, data_context) -> Dict[str, Any]: return {"title": "Costo Total 2025 vs 2024"}
    def get_figure(self, data_context):
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
        actual = [1.5, 1.6, 1.55, 1.7, 1.8, 1.6]
        anterior = [1.4, 1.5, 1.5, 1.6, 1.6, 1.5]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses, y=anterior, name="2024", marker_color="#adb5bd"))
        fig.add_trace(go.Bar(x=meses, y=actual, name="2025", marker_color="#228be6"))
        fig.update_layout(barmode='group', height=250, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=1.1))
        return fig
    def render_detail(self, data_context): return None

class TableDataStrategy:
    def get_routes_data(self): return [["261", "3T-LYCRA", "1", "29", "$5.5k"], ["355", "APAXCO", "1", "854", "$0"], ["1", "CANOITAS", "1", "680", "$0"]]
    def get_income_data(self): return [["32", "LITECRETE", "$200k", "0.9%"], ["35", "CONCRETOS", "$662k", "3.1%"], ["12", "VITRO", "$3.9M", "18%"]]
    def get_perf_unit_data(self): return [["U-105", "2.4", "5"], ["U-33", "2.35", "7"], ["U-12", "2.3", "5"], ["U-99", "2.28", "8"]]
    def get_perf_op_data(self): return [["Juan Perez", "2.4", "5"], ["Luis G.", "2.35", "7"], ["Carlos R.", "2.3", "5"]]

class SimpleTextStrategy(KPIStrategy):
    def __init__(self, key, title, prefix="", suffix="", color="gray", icon="tabler:circle"):
        self.key = key
        self.title = title
        self.prefix = prefix
        self.suffix = suffix
        self.color = color
        self.icon = icon

    def get_card_config(self, data_context) -> Dict[str, Any]:
        val = 1234 
        return {"title": self.title, "value": f"{self.prefix}{val}{self.suffix}", "color": self.color, "icon": self.icon, "is_simple": True}
    
    def render_detail(self, data_context): return dmc.Text(f"Detalle de {self.title}")