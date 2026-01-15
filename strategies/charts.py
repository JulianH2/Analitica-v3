import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem

class MainTrendChartStrategy(KPIStrategy):
    """Gráfica de tendencia principal que consume datos del contexto unificado"""
    def get_card_config(self, data_context):
        return {"title": "Tendencia Financiera Anual", "icon": "tabler:chart-area-line"}

    def render_detail(self, data_context):
        return dmc.Text("Análisis detallado de la evolución de ingresos mensuales.", c="dimmed") # type: ignore

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["dashboard"]["graficas"]["ingresos_anual"]
        meses = ds["meses"]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=meses, y=ds["meta"], name="Meta", 
            mode='lines', line=dict(color=DesignSystem.WARNING[5], width=3, dash='dot')
        ))

        fig.add_trace(go.Bar(
            x=meses, y=ds["anterior"], name="2024", 
            marker_color=DesignSystem.SLATE[3] 
        ))
        
        fig.add_trace(go.Bar(
            x=meses, y=ds["actual"], name="2025", 
            marker_color=DesignSystem.BRAND[5]
        ))

        fig.update_layout(
            height=320,  
            margin=dict(t=40, b=50, l=10, r=10), 
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT, 
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=1,
                font=dict(size=10)
            ),
            barmode='group',
            yaxis=dict(showgrid=True, gridcolor=DesignSystem.SLATE[2], zeroline=False),
            xaxis=dict(
                showgrid=False, 
                automargin=True,
                tickfont=dict(size=10)
            ),
        )
        return fig
    
class OpsFleetStatusStrategy(KPIStrategy):
    """Estado de flota consumiendo indicadores de disponibilidad"""
    def get_card_config(self, data_context):
        return {"title": "Estado de Flota", "icon": "tabler:chart-pie"}

    def render_detail(self, data_context): return None

    def get_figure(self, data_context):
        disp = data_context["mantenimiento"]["disponibilidad"]["indicadores"]["pct_disponibilidad"]["valor"]
        mtto = 100 - disp
        
        fig = go.Figure(data=[go.Pie(
            labels=['Disponible', 'Mantenimiento'],
            values=[disp, mtto],
            hole=.7,
            marker_colors=[DesignSystem.SUCCESS[5], DesignSystem.DANGER[5]], 
            textinfo='none'
        )])

        fig.update_layout(
            showlegend=True,
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            annotations=[dict(text=f'<b>{disp}%</b><br>Disp.', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        return fig

class OpsRoutesChartStrategy(KPIStrategy):
    """Rutas principales basadas en la tabla de rutas del Dashboard"""
    def get_card_config(self, data_context):
        return {"title": "Top Rutas por Volumen", "icon": "tabler:route"}

    def get_figure(self, data_context):
        ds = data_context["operaciones"]["dashboard"]["tablas"]["rutas_cargado"]
        labels = [r[1] for r in ds["r"]]
        values = [int(r[2]) for r in ds["r"]]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=labels, x=values, orientation='h',
            marker=dict(color=DesignSystem.WARNING[6]),
            text=values, textposition='auto'
        ))

        fig.update_layout(
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            margin=dict(t=10, b=20, l=10, r=20),
            height=300,
            yaxis=dict(autorange="reversed")
        )
        return fig