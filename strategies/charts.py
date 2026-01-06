import plotly.graph_objects as go
from services.data_manager import DataManager
from .base_strategy import KPIStrategy
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px

data_manager = DataManager()

class MainTrendChartStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Tendencia Financiera Anual", "icon": "tabler:chart-area-line"}

    def render_detail(self, data_context):
        return None 

    def get_figure(self, data_context):
        df = data_manager.service.get_main_trend_chart()
        meses = [str(m)[:3].title() for m in df["mes"]] if "mes" in df.columns else []
        
        fig = go.Figure()
        
        if "ingresos_anterior" in df.columns:
            fig.add_trace(go.Bar(
                x=meses, y=df["ingresos_anterior"], name="2024", 
                marker_color="#f1f3f5", hoverinfo="y"
            ))
        
        y_actual = df.get("ingresos_actual", [])
        fig.add_trace(go.Bar(
            x=meses, y=y_actual, name="2025", 
            marker_color="#228be6"
        ))
        
        y_meta = df.get("meta", [])
        fig.add_trace(go.Scatter(
            x=meses, y=y_meta, name="Meta", 
            mode='lines', line=dict(color="#fab005", width=3, dash='dot')
        ))

        fig.update_layout(
            title=dict(text="<b>Evolución de Ingresos vs Meta</b>", font=dict(size=14, family="Inter")),
            template="plotly_white",
            height=320,  
            margin=dict(t=40, b=30, l=0, r=0), 
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family="Inter, sans-serif", color="#495057", size=11),
            yaxis=dict(showgrid=True, gridcolor="#f8f9fa", zeroline=False),
            xaxis=dict(showgrid=False)
        )
        return fig
    
class OpsFleetStatusStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Fleet Status", "icon": "tabler:chart-pie"}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        res = data_context.get("main_dashboard", {}).get("resumenes", {})
        disp = res.get("disponibilidad_unidades", 0)
        mtto = max(0, 100 - disp)
        
        fig = go.Figure(data=[go.Pie(
            labels=['Available', 'Maintenance'],
            values=[disp, mtto],
            hole=.7,
            marker_colors=["#40c057", "#fa5252"], 
            textinfo='none',
            hoverinfo='label+percent'
        )])

        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text=f'<b>{disp}%</b><br>Avail', x=0.5, y=0.5, font_size=20, showarrow=False, font_family="Inter")]
        )
        return fig

class OpsUnitPerformanceStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Unit Efficiency (Top 5)", "icon": "tabler:chart-bar"}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        ops_data = data_manager.service.get_ops_income_data()
        units = ops_data.get("tablas", {}).get("unidades", [])[:5]
        
        ids = [u.get("unidad", "?") for u in units]
        total = [u.get("kms_totales", 0) for u in units]
        loaded = [u.get("kms_cargados", 0) for u in units]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=ids, y=total, name="Total Kms",
            marker_color="#e9ecef", marker_cornerradius=4
        ))
        
        fig.add_trace(go.Bar(
            x=ids, y=loaded, name="Loaded Kms",
            marker_color="#15aabf", marker_cornerradius=4
        ))

        fig.update_layout(
            template="plotly_white",
            margin=dict(t=30, b=30, l=40, r=20),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='overlay',
            font=dict(family="Inter, sans-serif", color="#495057")
        )
        return fig

class OpsRoutesChartStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Top Routes by Volume", "icon": "tabler:route"}

    def render_detail(self, data_context):
        return None

    def get_figure(self, data_context):
        ops_data = data_manager.service.get_ops_income_data()
        rutas = ops_data.get("tablas", {}).get("rutas", [])
        
        rutas_sorted = sorted(rutas, key=lambda x: x['viajes'], reverse=False)
        
        labels = [r["ruta"] for r in rutas_sorted]
        values = [r["viajes"] for r in rutas_sorted]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=labels,
            x=values,
            orientation='h',
            marker=dict(color="#fd7e14", cornerradius=4),
            text=values,
            textposition='auto'
        ))

        fig.update_layout(
            template="plotly_white",
            margin=dict(t=10, b=20, l=10, r=20),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor="#f1f3f5"),
            font=dict(family="Inter, sans-serif", color="#495057")
        )
        return fig
    
class OpsMapStrategy(KPIStrategy):
    def get_card_config(self, data_context):
        return {"title": "Monitoreo Geoespacial", "icon": "tabler:map-pin"}

    def render_detail(self, data_context):
        return dmc.Text("Detalle de coordenadas y paradas en modal...")

    def get_figure(self, data_context):
        df_map = pd.DataFrame({
            "Unidad": ["Unidad 01", "Unidad 05", "Unidad 12", "Unidad 88"],
            "lat": [25.6866, 19.4326, 20.6597, 21.1619], 
            "lon": [-100.3161, -99.1332, -103.3496, -101.6866],
            "Estado": ["En Ruta", "Cargando", "Mantenimiento", "En Ruta"],
            "Color": ["blue", "green", "red", "blue"]
        })

        fig = px.scatter_mapbox(
            df_map, lat="lat", lon="lon", hover_name="Unidad",
            color="Estado", zoom=4, height=350,
            color_discrete_map={"En Ruta": "#228be6", "Cargando": "#40c057", "Mantenimiento": "#fa5252"}
        )
        
        fig.update_layout(
            mapbox_style="carto-positron", 
            margin=dict(r=0, t=0, l=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=0.02, xanchor="left", x=0.02)
        )
        return fig