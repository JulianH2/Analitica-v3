from typing import Any, Dict
import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import format_value, safe_get
from dash import dcc

class AdminRichKPIStrategy(KPIStrategy):
    def __init__(self, section, key, title, icon, color, sub_section="indicadores", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon=icon, has_detail=has_detail, layout_config=layout_config)
        self.section, self.key, self.sub_section = section, key, sub_section

    def get_card_config(self, data_context):
        path = f"administracion.{self.section}.{self.sub_section}.{self.key}"
        node = safe_get(data_context, path, {"valor": 0})
        val = node.get('valor', 0) if isinstance(node, dict) else node
        
        is_money = all(x not in self.key.lower() for x in ["dias", "viajes", "disponibilidad"])
        prefix = "$" if is_money else ""
        
        l_mes = node.get("label_mes")
        l_ytd = node.get("label_ytd")
        
        return {
            "title": self.title,
            "value": format_value(val, prefix, format_type=self.layout.get("value_format", "abbreviated")),
            "label_mes": l_mes if l_mes and l_mes not in ["0%", "0", 0] else None,
            "label_ytd": l_ytd if l_ytd and l_ytd not in ["0%", "0", 0] else None,
            "color": self.color,
            "icon": self.icon
        }

    def render_detail(self, data_context):
        return dmc.Text("Detalle de métrica administrativa.", size="sm", c=SemanticColors.TEXT_MUTED)  # type: ignore


class CollectionGaugeStrategy(KPIStrategy):
    def __init__(self, title, val_key, color, prefix="$", section="facturacion_cobranza", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon="tabler:wallet", has_detail=has_detail, layout_config=layout_config)
        self.val_key = val_key
        self.prefix = prefix
        self.section = section
        self.gauge_params = {
            "range_max_mult": 1.15,
            "threshold_width": 5,
            "threshold_color": "#f59e0b",
            "exceed_color": "#228be6",
            "bg_color": "rgba(0,0,0,0.05)",
            "font_size": 18
        }

    def get_card_config(self, data_context):
        path = f"administracion.{self.section}.indicadores.{self.val_key}"
        node = safe_get(data_context, path, {})
        val = node.get("valor", 0)
        
        return {
            "title": self.title,
            "value": format_value(val, self.prefix),
            "monthly_display": node.get("monthly_display"),
            "monthly_delta": node.get("monthly_delta"),
            "label_mes": node.get("label_mes"),
            "meta_text": f"Meta: {format_value(node.get('meta', 0), self.prefix)}" if node.get("meta") else ""
        }

    def get_figure(self, data_context):
        path = f"administracion.{self.section}.indicadores.{self.val_key}"
        node = safe_get(data_context, path, {})
        
        val_pct = node.get("valor_porcentaje", 0)
        meta_pct = node.get("meta_porcentaje", 100)
        exceeds = val_pct > meta_pct
        
        bar_color = self.gauge_params["exceed_color"] if exceeds else self.hex_color
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", 
            value=val_pct,
            number={
                'suffix': "%", 
                'font': {'size': self.gauge_params["font_size"], 'weight': 'bold'},
                'valueformat': '.1f'
            },
            gauge={
                'axis': {'range': [0, max(val_pct, meta_pct) * self.gauge_params["range_max_mult"]], 'visible': False},
                'bar': {'color': bar_color, 'thickness': 0.8},
                'bgcolor': self.gauge_params["bg_color"],
                'threshold': {
                    'line': {'color': self.gauge_params["threshold_color"], 'width': self.gauge_params["threshold_width"]}, 
                    'thickness': 0.75, 
                    'value': meta_pct
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        
        if exceeds:
            fig.add_annotation(
                x=0.5, y=1.05, 
                text="★ META SUPERADA", 
                showarrow=False, 
                font=dict(color=bar_color, size=9, weight="bold")
            )

        fig.update_layout(
            height=150,
            margin=dict(l=5, r=5, t=0, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': "Inter, sans-serif"}
        )
        return fig

    def render_detail(self, data_context): 
        return dmc.Text("Análisis de eficiencia operativa de cobranza.", size="sm", c=SemanticColors.TEXT_MUTED)   # type: ignore


class CollectionComparisonStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Comparativo de Facturación Anual", color="indigo", layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.facturacion_cobranza.graficas.comparativa"
        ds = safe_get(data_context, path, {"meses": [], "actual": [], "anterior": []})
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3], opacity=0.5))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=self.hex_color))
        
        fig.add_trace(go.Scatter(
            x=ds["meses"], y=[18.5] * len(ds["meses"]),
            name="Presupuesto", mode="lines", 
            line=dict(color=DesignSystem.WARNING[5], width=3, dash="dot")
        ))
        
        fig.update_layout(
            barmode='group', height=400, bargap=0.15,
            margin=dict(t=50, b=40, l=20, r=20),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None


class CollectionMixStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Distribución de Cartera", color="indigo", layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.facturacion_cobranza.graficas.mix"
        ds = safe_get(data_context, path, {"labels": [], "values": []})
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], values=ds["values"], hole=0.5,
            marker=dict(colors=[SemanticColors.INGRESO, DesignSystem.WARNING[5], SemanticColors.EGRESO])
        )])
        fig.update_layout(
            showlegend=True, 
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig
    def render_detail(self, data_context): return None

class DebtorsStackedStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Saldo por Cliente", color="indigo", layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.facturacion_cobranza.graficas.stack"
        ds = safe_get(data_context, path, {"clientes": [], "por_vencer": [], "sin_carta": [], "vencido": []})
        fig = go.Figure()
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["por_vencer"], name="Vigente", orientation='h', marker_color=SemanticColors.INGRESO))
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["sin_carta"], name="Pendiente", orientation='h', marker_color=DesignSystem.WARNING[5]))
        fig.add_trace(go.Bar(y=ds["clientes"], x=ds["vencido"], name="Vencido", orientation='h', marker_color=SemanticColors.EGRESO))
        
        fig.update_layout(
            barmode='stack', 
            bargap=0.15,
            height=500, 
            margin=dict(l=10, r=20, t=10, b=10), 
            yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle.", size="sm", c=SemanticColors.TEXT_MUTED) # type: ignore
    
class CollectionAgingTableStrategy:
    def render(self, data_context):
        path = "administracion.facturacion_cobranza.antiguedad"
        ds = safe_get(data_context, path, {"h": [], "r": []})
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(x, fz=DesignSystem.FONT_TABLE, c=SemanticColors.TEXT_MUTED, fw=DesignSystem.FW_NORMAL)   # type: ignore
                for x in ds["h"]
            ])),
            dmc.TableTbody([dmc.TableTr([
                dmc.TableTd(str(c), fz=DesignSystem.FONT_TABLE) 
                for c in r
            ]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True, highlightOnHover=True)


class BankDailyEvolutionStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Flujo Diario de Caja", color="green", icon="tabler:timeline", layout_config=layout_config)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.bancos.graficas.diaria"
        ds = safe_get(data_context, path, {"dias": [], "ingresos": [], "egresos": []})
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ds["dias"], y=ds["ingresos"], name="Ingresos",
            line=dict(color=SemanticColors.INGRESO, width=4, shape='spline'),
            fill='tozeroy', fillcolor='rgba(34, 197, 94, 0.05)'
        ))
        fig.add_trace(go.Scatter(
            x=ds["dias"], y=ds["egresos"], name="Egresos",
            line=dict(color=SemanticColors.EGRESO, width=4, shape='spline'),
            fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.05)'
        ))
        
        fig.update_layout(
            height=400, hovermode="x unified",
            margin=dict(t=50, b=20, l=10, r=10),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None


class BankDonutStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Saldo por Institución", color="orange", icon="tabler:building-bank", layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.bancos.graficas.donut"
        ds = safe_get(data_context, path, {"labels": [], "values": []})
        
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], values=ds["values"], 
            hole=0.45, 
            marker=dict(colors=DesignSystem.CHART_COLORS)
        )])
        fig.update_layout(
            height=380, showlegend=True, 
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"),
            margin=dict(t=30, b=50, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None


class BankConceptsStrategy:
    def render(self, data_context, title=None):
        path = "administracion.bancos.conceptos"
        ds = safe_get(data_context, path, {"h": [], "r": []})
        
        return dmc.Stack(gap="xs", children=[
            dmc.Text(title, fw=DesignSystem.FW_BOLD, size="xs", c=SemanticColors.TEXT_MUTED, tt="uppercase") if title else None,  # type: ignore
            dmc.Table([
                dmc.TableThead(dmc.TableTr([
                    dmc.TableTh(x, fz=DesignSystem.FONT_TABLE, c=SemanticColors.TEXT_MUTED, fw=DesignSystem.FW_NORMAL)   # type: ignore
                    for x in ds["h"]
                ])),
                dmc.TableTbody([dmc.TableTr([
                    dmc.TableTd(str(c), fz=DesignSystem.FONT_TABLE) 
                    for c in r
                ]) for r in ds["r"]])
            ], striped="odd", withTableBorder=True, highlightOnHover=True)
        ])

class PayablesGaugeStrategy(KPIStrategy):
    def __init__(self, title, val_key, color="red", prefix="$", section="cuentas_por_pagar", has_detail=True):
        super().__init__(title=title, color=color, icon="tabler:receipt-refund", has_detail=has_detail)
        self.val_key, self.prefix, self.section = val_key, prefix, section

    def get_card_config(self, data_context):
        path = f"administracion.{self.section}.indicadores.{self.val_key}"
        node = safe_get(data_context, path, {})
        val = node.get("valor", 0)
        config = {
            "title": self.title,
            "value": format_value(val, self.prefix),
            "icon": self.icon,
            "meta_text": f"Meta: {format_value(node.get('meta', 0), self.prefix)}" if node.get("meta") else ""
        }
        config.update(node)
        return config

    def get_figure(self, data_context):
        path = f"administracion.{self.section}.indicadores.{self.val_key}"
        node = safe_get(data_context, path, {})
        val, meta = node.get("valor", 0), node.get("meta", 0)
        t_vals = node.get("tickvals", [0, val, meta])
        t_text = node.get("ticktext", [f"{self.prefix}0", format_value(val, self.prefix), format_value(meta, self.prefix)])
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={'valueformat': '$,.0f' if self.prefix=="$" else '.1f', 'font': {'size': 18, 'weight': 'bold'}},
            gauge={
                'axis': {'range': [0, max(t_vals)*1.1], 'tickvals': t_vals, 'ticktext': t_text, 'visible': True, 'tickfont': {'size': 10}},
                'bar': {'color': self.hex_color, 'thickness': 0.8},
                'bgcolor': "rgba(0,0,0,0.05)",
                'threshold': {'line': {'color': "#f59e0b", 'width': 4}, 'value': meta}
            }
        ))
        fig.update_layout(height=150, margin=dict(l=5, r=5, t=0, b=30), paper_bgcolor='rgba(0,0,0,0)')
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Análisis de cumplimiento de pagos.")
    
class PayablesDynamicChartStrategy:
    def render(self, data_context, view="comparativa", height=400):
        path = f"administracion.cuentas_por_pagar.graficas.{view}"
        ds = safe_get(data_context, path, {})
        fig = go.Figure()

        if view == "comparativa":
            fig.add_trace(go.Scatter(x=ds.get("meses"), y=ds.get("actual"), name="2025", mode="lines+markers", line=dict(color=DesignSystem.BRAND[6], width=3)))
            fig.add_trace(go.Scatter(x=ds.get("meses"), y=ds.get("anterior"), name="2024", mode="lines", line=dict(color=DesignSystem.SLATE[4], dash="dash")))
        
        elif view == "mix":
            fig = go.Figure(go.Pie(labels=ds.get("labels"), values=ds.get("values"), hole=.5, marker=dict(colors=[DesignSystem.BRAND[6], DesignSystem.SLATE[4]])))
        
        elif view == "saldo_proveedor":
            fig.add_trace(go.Bar(y=ds.get("prov"), x=ds.get("por_vencer"), name="Vigente", orientation='h', marker_color=SemanticColors.INGRESO))
            fig.add_trace(go.Bar(y=ds.get("prov"), x=ds.get("vencido"), name="Vencido", orientation='h', marker_color=SemanticColors.EGRESO))
            fig.update_layout(barmode='stack', yaxis=dict(autorange="reversed"))

        fig.update_layout(height=height, margin=dict(l=15, r=1, t=0, b=35), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return dcc.Graph(figure=fig, config={'displayModeBar': False})

class PayablesAgingTableStrategy:
    def render(self, data_context, view="aging"):
        map_paths = {
            "aging": "administracion.cuentas_por_pagar.antiguedad",
            "area": "administracion.cuentas_por_pagar.antiguedad_area",
            "prov": "administracion.cuentas_por_pagar.antiguedad_proveedor"
        }
        ds = safe_get(data_context, map_paths.get(view, "aging"), {"h": [], "r": []})
        if not ds.get("r"): return dmc.Text("Sin datos", c="dimmed", ta="center", py="xl") # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([dmc.TableTh(x, style={"fontSize": "11px"}) for x in ds["h"]])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(c), style={"fontSize": "11px"}) for c in row]) for row in ds["r"]])
        ], striped="odd", withTableBorder=True, withColumnBorders=True)

class PayablesComparisonStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Cuentas x Pagar 2025 vs. 2024", color="red", icon="tabler:scale", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context, view="monthly"):
        try:
            ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["comparativa"]
        except:
            ds = {"meses": [], "actual": [], "anterior": []}
        
        fig = go.Figure()
        
        if view == "monthly":
            fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=self.hex_color))
            fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3], opacity=0.6))
            fig.update_layout(barmode='group')
        
        elif view == "cumulative":
            import pandas as pd
            actual_cum = pd.Series(ds["actual"]).cumsum()
            anterior_cum = pd.Series(ds["anterior"]).cumsum()
            fig.add_trace(go.Scatter(x=ds["meses"], y=actual_cum, name="2025 (Acum)", fill='tozeroy', line=dict(color=self.hex_color)))
            fig.add_trace(go.Scatter(x=ds["meses"], y=anterior_cum, name="2024 (Acum)", line=dict(color=DesignSystem.SLATE[4], dash='dash')))

        elif view == "comparison":
            diff = [a - b for a, b in zip(ds["actual"], ds["anterior"])]
            fig.add_trace(go.Bar(x=ds["meses"], y=diff, name="Diferencia", marker_color=DesignSystem.BRAND[5]))

        fig.update_layout(
            margin=dict(t=10, b=20, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT,
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
        )
        return fig

    def get_figure_by_view(self, data_context, view="monthly"):
        fig = self.get_figure(data_context, view=view)
        return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={"height": "400px"})

    def render_detail(self, data_context):
        return None

class PayablesMixStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Saldo por Clasificación", color="red", icon="tabler:chart-pie-2", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["mix"]
        except: ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], values=ds["values"], hole=.5, 
            marker=dict(colors=[SemanticColors.INGRESO, SemanticColors.EGRESO])
        )])
        fig.update_layout(
            showlegend=True, legend=dict(orientation="h", y=-0.1), 
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None
    
class SupplierSaldoStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Saldo por Proveedor", color="red", icon="tabler:truck-loading", layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.cuentas_por_pagar.graficas.saldo_proveedor"
        ds = safe_get(data_context, path, {"prov": [], "por_vencer": [], "vencido": []})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(y=ds["prov"], x=ds["por_vencer"], name="Vigente", orientation='h', marker_color=SemanticColors.INGRESO))
        fig.add_trace(go.Bar(y=ds["prov"], x=ds["vencido"], name="Vencido", orientation='h', marker_color=SemanticColors.EGRESO))
        
        fig.update_layout(
            barmode='stack', bargap=0.1, height=550, 
            margin=dict(l=10, r=20, t=30, b=10), yaxis=dict(autorange="reversed"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): 
        return dmc.Text("Desglose de deuda vigente vs. vencida por proveedor.", size="sm", c=SemanticColors.TEXT_MUTED)  # type: ignore