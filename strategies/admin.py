from typing import Any, Dict
import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import format_value, safe_get

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
    def __init__(self, title, val_key, target_key, color, prefix="$", layout_config=None):
        super().__init__(title=title, color=color, icon="tabler:rebound", layout_config=layout_config)
        self.val_key, self.target_key, self.prefix = val_key, target_key, prefix

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.facturacion_cobranza.indicadores"
        node = safe_get(data_context, path, {})
        val = node.get(self.val_key, {}).get("valor", 0)
        target = node.get(self.target_key, {}).get("valor", 100)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={
                'prefix': self.prefix, 
                'font': {'size': 28, 'weight': 'bold', 'color': SemanticColors.TEXT_MAIN}, 
                'valueformat': '~s' if val >= 1000 else ',.2f'
            },
            gauge={
                'axis': {'range': [None, target * 1.15 if target > 0 else 100], 'visible': False}, 
                'bar': {'color': self.hex_color, 'thickness': 0.85}, 
                'bgcolor': DesignSystem.SLATE[1]
            },
            domain={'x': [0, 1], 'y': [0.2, 1]}
        ))
        
        fig.add_annotation(
            x=0.5, y=0.05, showarrow=False,
            text=f"META: {format_value(target, self.prefix)}",
            font=dict(size=DesignSystem.FONT_TABLE, color=SemanticColors.TEXT_MUTED, weight="bold")
        )
        
        fig.update_layout(
            height=180, 
            margin=dict(l=30, r=30, t=40, b=10), 
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
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
            labels=ds["labels"], values=ds["values"], hole=0.45,
            marker=dict(colors=[SemanticColors.INGRESO, DesignSystem.WARNING[5], SemanticColors.EGRESO])
        )])
        fig.update_layout(
            height=320, showlegend=True, 
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(t=40, b=60, l=20, r=20),
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
            barmode='stack', bargap=0.1, height=550, 
            margin=dict(l=10, r=20, t=30, b=10), 
            yaxis=dict(autorange="reversed"),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de facturación y saldos por cliente.", size="sm", c=SemanticColors.TEXT_MUTED)  # type: ignore


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
    def __init__(self, title, val_key, target_key, color, prefix="$", layout_config=None):
        super().__init__(title=title, color=color, icon="tabler:wallet", layout_config=layout_config)
        self.val_key, self.target_key, self.prefix = val_key, target_key, prefix

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        path = "administracion.cuentas_por_pagar.indicadores"
        node = safe_get(data_context, path, {})
        val = node.get(self.val_key, {}).get("valor", 0)
        target = node.get(self.target_key, {}).get("valor", 100)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={
                'prefix': self.prefix, 'font': {'size': 28, 'weight': 'bold', 'color': SemanticColors.TEXT_MAIN},
                'valueformat': '~s' if val >= 1000 else ',.2f'
            },
            gauge={
                'axis': {'range': [None, target * 1.15 if target > 0 else 100], 'visible': False},
                'bar': {'color': self.hex_color, 'thickness': 0.85},
                'bgcolor': DesignSystem.SLATE[1]
            },
            domain={'x': [0, 1], 'y': [0.2, 1]}
        ))
        
        fig.add_annotation(
            x=0.5, y=0.05, showarrow=False,
            text=f"META: {format_value(target, self.prefix)}",
            font=dict(size=DesignSystem.FONT_TABLE, color=SemanticColors.TEXT_MUTED, weight="bold")
        )
        fig.update_layout(
            height=300, margin=dict(l=30, r=30, t=40, b=10),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): 
        return dmc.Text("Análisis de cumplimiento de obligaciones financieras.", size="sm", c=SemanticColors.TEXT_MUTED)  # type: ignore


class PayablesComparisonStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Cuentas x Pagar 2025 vs. 2024", color="red", icon="tabler:scale", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["comparativa"]
        except:
            ds = {"meses": [], "actual": [], "anterior": []}
        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="2025", marker_color=self.hex_color))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="2024", marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.update_layout(
            barmode='group', margin=dict(t=40, b=20),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return None


class PayablesMixStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Saldo por Clasificación", color="red", icon="tabler:chart-pie-2", has_detail=has_detail)

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        try:
            ds = data_context["administracion"]["cuentas_por_pagar"]["graficas"]["mix"]
        except:
            ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], 
            values=ds["values"], 
            hole=.6, 
            marker=dict(colors=[SemanticColors.INGRESO, SemanticColors.EGRESO])
        )])
        fig.update_layout(
            showlegend=True, legend=dict(orientation="h", y=-0.1), margin=dict(t=30, b=40),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return None


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


class PayablesAgingTableStrategy:
    def render(self, data_context):
        path = "administracion.cuentas_por_pagar.antiguedad"
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