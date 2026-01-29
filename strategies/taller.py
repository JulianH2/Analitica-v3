import plotly.graph_objects as go
import dash_mantine_components as dmc
import math
from utils.helpers import format_value, safe_get 
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors

class TallerMiniGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="$", suffix="", section="dashboard", layout_config=None):
        super().__init__(title=title, color=color, layout_config=layout_config)
        self.key, self.prefix, self.suffix = key, prefix, suffix

    def get_card_config(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {"value": 0, "target": 1})
        return {"title": self.title, "node": node}

    def get_figure(self, data_context):
        cfg = self.get_card_config(data_context)
        node = cfg["node"]
        val = node.get('value', 0)
        meta = node.get('target', 1)
        
        pct = (val / meta * 100) if meta > 0 else 0
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=pct, 
            number={'suffix': "%", 'font': {'size': 14, 'weight': 'bold'}},
            gauge={
                'shape': "angular", 
                'axis': {'range': [0, 100], 'visible': False}, 
                'bar': {'color': hex_color, 'thickness': 1},
                'bgcolor': "rgba(148, 163, 184, 0.08)"
            }, 
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(
            height=70, 
            margin=dict(l=0, r=0, t=5, b=5),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def render_detail(self, data_context): return None

class TallerGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="$", suffix="", section="dashboard", has_detail=True, layout_config=None):
        super().__init__(
            title=title, color=color, icon="tabler:gauge", 
            has_detail=has_detail, layout_config=layout_config 
        )
        self.key, self.prefix, self.suffix = key, prefix, suffix

    def get_card_config(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        val = node.get("value", 0)
        
        config = {
            "title": self.title,
            "value": f"{format_value(val, self.prefix)}{self.suffix}",
            "icon": self.icon,
            "is_simple": True
        }
        
        config.update(node)

        if "delta" in node:
            config["monthly_display"] = format_value(val, self.prefix)
        if "ytd" in node:
            config["ytd_display"] = format_value(node.get("ytd", 0), self.prefix)

        return config

    def get_figure(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        
        val = node.get("value", 0)
        meta = node.get("target", 1)
        val_pct = (val / meta * 100) if meta > 0 else 0
        meta_pct = 100.0
        
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val_pct, 
            number={'suffix': "%", 'font': {'size': 18, 'weight': 'bold'}},
            gauge={
                'shape': "angular", 
                'axis': {'range': [0, 100], 'visible': False}, 
                'bar': {'color': hex_color, 'thickness': 0.8}, 
                'bgcolor': "rgba(148, 163, 184, 0.05)",
                'threshold': {'line': {'color': "#f59e0b", 'width': 4}, 'value': meta_pct}
            }, 
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Cargando detalle técnico...", c="dimmed") # type: ignore

class TallerNeedleGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, section="dashboard", has_detail=True):
        super().__init__(title=title, color="gray", icon="tabler:clock-hour-4", has_detail=has_detail)
        self.key = key

    def get_card_config(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        val = node.get("value", 0)
        
        return {
            "title": self.title,
            "value": f"{val}%",
            "monthly_display": f"{val}%",
            "monthly_delta": node.get("delta", 0),
            "label_mes": "Actual",
            "meta_text": f"Meta: {node.get('target', 0)}%"
        }

    def get_figure(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        value = node.get("value", 0) 
        
        fig = go.Figure(go.Indicator(
            mode="gauge",
            value=value,
            gauge={
                'axis': {'range': [0, 100], 'visible': True, 'tickwidth': 1, 'tickcolor': "gray"},
                'bar': {'color': "rgba(0,0,0,0)"},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 85], 'color': "#fa5252"},
                    {'range': [85, 95], 'color': "#fcc419"},
                    {'range': [95, 100], 'color': "#228be6"}
                ],
            }
        ))

        theta = 180 - (value * 1.8)
        r = 0.45 
        x_pivote, y_pivote = 0.5, 0.25
        x_punta = x_pivote + r * math.cos(math.radians(theta))
        y_punta = y_pivote + r * math.sin(math.radians(theta))

        fig.add_shape(type="line", x0=x_pivote, y0=y_pivote, x1=x_punta, y1=y_punta, line=dict(color="black", width=4), xref="paper", yref="paper")
        fig.add_shape(type="circle", x0=x_pivote-0.02, y0=y_pivote-0.02, x1=x_pivote+0.02, y1=y_pivote+0.02, fillcolor="black", line_color="black", xref="paper", yref="paper")

        fig.update_layout(
            height=160,
            margin=dict(l=25, r=25, t=40, b=5),
            paper_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(x=0.5, y=0.45, text=f"{value}%", showarrow=False, font=dict(size=18, weight="bold"))]
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de disponibilidad")

class AvailabilityMonthlyStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="% Disponibilidad Unidades 2025 vs. 2024", color="indigo", icon="tabler:calendar-stats", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.availability_monthly", {"meses": [], "anterior": [], "actual": [], "target": []})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds.get("meses",[]), y=ds.get("anterior",[]), marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.add_trace(go.Bar(name='2025', x=ds.get("meses",[]), y=ds.get("actual",[]), marker_color=self.hex_color))
        fig.add_trace(go.Scatter(name='Meta', x=ds.get("meses",[]), y=ds.get("target",[]), mode='lines', line=dict(color=DesignSystem.SUCCESS[5], width=2, dash='dot')))
        fig.update_layout(barmode='group', yaxis=dict(ticksuffix="%"), margin=dict(t=40, b=20), paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT)
        return fig

    def render_detail(self, data_context): return None

class AvailabilityKmEntriesStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Entradas a Taller y Kms Recorridos", color="red", icon="tabler:tool", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.entries_vs_kms", {"unidades": [], "entradas": [], "kms": []})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds.get("unidades",[]), y=ds.get("entradas",[]), name="Entradas", yaxis='y', marker_color=DesignSystem.DANGER[5]))
        fig.add_trace(go.Scatter(x=ds.get("unidades",[]), y=ds.get("kms",[]), name="Kilómetros", yaxis='y2', mode='lines+markers', line=dict(color=self.hex_color, width=3)))
        fig.update_layout(
            yaxis2=dict(overlaying='y', side='right', showgrid=False),
            margin=dict(t=40, b=20), hovermode="x unified",
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class AvailabilityTableStrategy:
    def render(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.tables.availability_detail", 
                      safe_get(data_context, "maintenance.dashboard.charts.availability_detail", {"h": [], "r": []}))
        
        if not ds.get("h"): return dmc.Text("Sin datos disponibles", c="dimmed", ta="center", py="xl") # type: ignore
        
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(h, style={"fontSize": "11px"}, c=SemanticColors.TEXT_MUTED) for h in ds.get("h",[])])), # type: ignore
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), fw=700 if str(row[0]) in ["Total", "SIN ASIGNAR"] else 400, style={"fontSize": "11px"}) for c in row]) for row in ds.get("r",[])]) # type: ignore
        ], striped="odd", withTableBorder=True, highlightOnHover=True)

class TallerTrendStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Evolución de Costos de Mantenimiento", color="indigo", icon="tabler:trending-up", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.cost_trend_annual", {"meses": [], "anterior": [], "actual": []})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds.get("meses"), y=ds.get("anterior"), marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.add_trace(go.Bar(name='2025', x=ds.get("meses"), y=ds.get("actual"), marker_color=self.hex_color))
        
        fig.update_layout(
            barmode='group', bargap=0.15, height=320,
            margin=dict(t=40, b=20, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class TallerMaintenanceTypeStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Distribución por Tipo de Mantenimiento", color="indigo", icon="tabler:chart-bar-stacked", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.corrective_preventive", {"values": [0,0]})
        
        fig = go.Figure()
        vals = ds.get("values", [0,0])
        fig.add_trace(go.Bar(name='Correctivo', x=['CORRECTIVO'], y=[vals[0]], marker_color=DesignSystem.DANGER[5], width=0.5))
        fig.add_trace(go.Bar(name='Preventivo', x=['PREVENTIVO'], y=[vals[1]], marker_color=DesignSystem.SUCCESS[5], width=0.5))
        
        fig.update_layout(
            barmode='stack', height=320,
            margin=dict(t=40, b=20, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class TallerHorizontalBarStrategy(KPIStrategy):
    def __init__(self, title, key, color="indigo", has_detail=True):
        super().__init__(title=title, color=color, icon="tabler:list-details", has_detail=has_detail)
        self.key = key

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = f"maintenance.dashboard.charts.{self.key}"
        ds = safe_get(data_context, path, {"values": [], "labels": []})
        
        fig = go.Figure(go.Bar(
            x=ds.get("values"), y=ds.get("labels"), orientation='h', 
            marker_color=self.hex_color,
            text=[f"{v:,.0f}" for v in ds.get("values",[])], textposition="auto"
        ))
        
        fig.update_layout(
            yaxis=dict(autorange="reversed", automargin=True),
            margin=dict(t=30, b=20, l=10, r=20),
            height=350, bargap=0.1,
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class TallerDonutStrategy(KPIStrategy):
    def __init__(self, title, key, has_detail=True):
        super().__init__(title=title, icon="tabler:chart-pie", has_detail=has_detail)
        self.key = key

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = f"maintenance.dashboard.charts.{self.key}"
        ds = safe_get(data_context, path, {"labels": [], "values": []})
        
        fig = go.Figure(data=[go.Pie(
            labels=ds.get("labels"), values=ds.get("values"), 
            hole=.6, marker=dict(colors=DesignSystem.CHART_COLORS)
        )])
        fig.update_layout(
            showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=30, b=40),
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class PurchasesTrendStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Compras 2025 vs. 2024", color="indigo", icon="tabler:shopping-cart", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.purchases_trend", {"meses": [], "anterior": [], "actual": []})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='2024', x=ds.get("meses"), y=ds.get("anterior"), marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.add_trace(go.Bar(name='2025', x=ds.get("meses"), y=ds.get("actual"), marker_color=self.hex_color))
        
        fig.update_layout(
            barmode='group', bargap=0.15, height=320,
            margin=dict(t=40, b=20, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class PurchasesAreaBarStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Total Compra por Área", color="green", icon="tabler:category", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.purchases_by_area", {"valores": [], "areas": []})
        
        fig = go.Figure(go.Bar(
            x=ds.get("valores"), y=ds.get("areas"), orientation='h', 
            marker_color=self.hex_color, 
            text=[f"${v/1000000:,.1f}M" for v in ds.get("valores", [])], textposition="auto"
        ))
        
        fig.update_layout(
            yaxis=dict(autorange="reversed", automargin=True),
            margin=dict(t=30, b=20, l=10, r=20),
            height=350, bargap=0.1, 
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class PurchasesTypeDonutStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Compras por Tipo Compra", icon="tabler:chart-donut", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.purchases_by_type", {"labels": [], "values": []})
        
        fig = go.Figure(data=[go.Pie(
            labels=ds.get("labels"), values=ds.get("values"), 
            hole=.6, 
            marker=dict(colors=[DesignSystem.DANGER[5], DesignSystem.BRAND[5], DesignSystem.WARNING[5]])
        )])
        fig.update_layout(
            showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(t=30, b=40),
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class WorkshopPurchasesTableStrategy:
    def _build(self, h, r):
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}, c=SemanticColors.TEXT_MUTED) for x in h])), # type: ignore
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in r])
        ], striped="odd", withTableBorder=True, highlightOnHover=True)

    def render_proveedor(self, data_context): 
        d = safe_get(data_context, "maintenance.dashboard.tables.suppliers", {"h": [], "r": []})
        return self._build(d.get("h", []), d.get("r", []))

    def render_ordenes(self, data_context): 
        d = safe_get(data_context, "maintenance.dashboard.tables.orders", {"h": [], "r": []})
        return self._build(d.get("h", []), d.get("r", []))

    def render_insumos(self, data_context): 
        d = safe_get(data_context, "maintenance.dashboard.tables.supplies", {"h": [], "r": []})
        return self._build(d.get("h", []), d.get("r", []))

class InventoryGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, section="kpis", has_detail=True):
        super().__init__(title=title, color=color, icon="tabler:building-warehouse", has_detail=has_detail)
        self.key = key

    def get_card_config(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        val = node.get("value", 0)
        return {
            "title": self.title,
            "value": format_value(val, "$"),
            "monthly_display": node.get("monthly_display"),
            "monthly_delta": node.get("delta"),
            "label_mes": node.get("label_mes"),
            "meta_text": f"Meta: {format_value(node.get('target', 0), '$')}" if node.get("target") else ""
        }

    def get_figure(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {})
        
        val = node.get("value", 0)
        meta = node.get("target", 1)
        val_pct = (val / meta * 100) if meta > 0 else 0
        meta_pct = 100.0
        
        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.BRAND[5])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val_pct,
            number={'suffix': "%", 'font': {'size': 20, 'weight': 'bold'}},
            gauge={
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': hex_color, 'thickness': 1},
                'bgcolor': "rgba(0,0,0,0.05)",
                'threshold': {'line': {'color': "#f59e0b", 'width': 4}, 'value': meta_pct}
            }
        ))
        fig.update_layout(height=150, margin=dict(l=15, r=15, t=25, b=5), paper_bgcolor='rgba(0,0,0,0)')
        return fig

    def render_detail(self, data_context): return None
    
class InventoryHistoricalTrendStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(
            title="Valorización Histórica 2025 vs. 2024", 
            color="indigo", icon="tabler:history", has_detail=has_detail
        )

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.inventory_history", {"meses": [], "anterior": [], "actual": []})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='2025', x=ds.get("meses"), y=ds.get("actual"), 
            marker_color=self.hex_color, opacity=0.8
        ))
        fig.add_trace(go.Scatter(
            name='2024', x=ds.get("meses"), y=ds.get("anterior"), 
            mode='lines+markers', line=dict(color=DesignSystem.SLATE[4], width=3, shape='spline')
        ))

        fig.update_layout(
            margin=dict(t=40, b=20, l=40, r=10),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(title="Valorización", tickformat="$,.0f", gridcolor="rgba(0,0,0,0.05)"),
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class InventoryAreaDistributionStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Valorización Actual por Área", color="indigo", icon="tabler:section", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "maintenance.dashboard.charts.inventory_by_area", {"labels": [], "values": []})
        
        fig = go.Figure(go.Bar(
            x=ds.get("labels"), y=ds.get("values"), 
            marker_color=self.hex_color, 
            text=[f"${v/1e6:.1f}M" for v in ds.get("values",[])], textposition="auto"
        ))
        fig.update_layout(
            margin=dict(t=40, b=20),
            paper_bgcolor=DesignSystem.TRANSPARENT, plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None

class InventoryDetailedTableStrategy:
    def _build(self, h, r):
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}, c=SemanticColors.TEXT_MUTED) for x in h])), # type: ignore
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in r])
        ], striped="odd", withTableBorder=True)

    def render_family(self, data_context):
        d = safe_get(data_context, "maintenance.dashboard.tables.family", {"h": [], "r": []})
        return self._build(d.get("h", []), d.get("r", []))

    def render_history(self, data_context):
        d = safe_get(data_context, "maintenance.dashboard.tables.history", {"h": [], "r": []})
        return self._build(d.get("h", []), d.get("r", []))

class TallerRichKPIStrategy(KPIStrategy):
    def __init__(self, key, title, icon, color, has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.key = key

    def get_card_config(self, data_context):
        path = f"maintenance.dashboard.kpis.{self.key}"
        node = safe_get(data_context, path, {"value": 0})
        
        val = node.get('value', 0) if isinstance(node, dict) else node
        
        is_money = all(x not in self.key.lower() for x in ["days", "dias", "count", "percent", "cumplimiento", "registrados"])
        prefix = "$" if is_money else ""
        
        l_mes = node.get("label_mes") if isinstance(node, dict) else None
        
        return {
            "title": self.title,
            "value": format_value(val, prefix, format_type="abbreviated"),
            "label_mes": l_mes,
            "color": self.color,
            "icon": self.icon
        }

    def render_detail(self, data_context):
        return dmc.Text("Detalle de indicador de almacén.", size="sm", c=SemanticColors.TEXT_MUTED)