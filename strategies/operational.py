import plotly.graph_objects as go
import dash_mantine_components as dmc
from .base_strategy import KPIStrategy
from settings.theme import DesignSystem, SemanticColors
from utils.helpers import format_value, safe_get

class FleetEfficiencyStrategy(KPIStrategy):
    def __init__(self, color="green", has_detail=True, layout_config=None):
        super().__init__(
            title="Eficiencia de Flota",
            color=color,
            icon="tabler:truck-delivery",
            has_detail=has_detail,
            layout_config=layout_config
        )

    def get_card_config(self, data_context):
        try:
            val = data_context["operaciones"]["dashboard"]["utilizacion"].get("valor", 0)
        except (KeyError, TypeError):
            val = 0
        return {"title": self.title, "value": f"{val:,.1f}%"}

    def get_figure(self, data_context):
        try:
            val = data_context["operaciones"]["dashboard"]["utilizacion"]["valor"]
        except (KeyError, TypeError):
            val = 0

        hex_color = DesignSystem.COLOR_MAP.get(self.color, DesignSystem.SUCCESS[5])

        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={'suffix': "%", 'font': {'size': 20, 'weight': 'bold', 'color': SemanticColors.TEXT_MAIN}},
            gauge={
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': hex_color, 'thickness': 0.8},
                'bgcolor': DesignSystem.SLATE[1]
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(
            height=DesignSystem.GAUGE_HEIGHT,
            margin=dict(l=15, r=15, t=35, b=10),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de indicador...", c=SemanticColors.TEXT_MUTED, size="sm")   # type: ignore


class OpsGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="$", section="dashboard", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon="tabler:gauge", has_detail=has_detail, layout_config=layout_config)
        self.key, self.prefix, self.section = key, prefix, section
        self.gauge_params = {
            "range_max_mult": 1.15,
            "threshold_width": 5,
            "threshold_color": DesignSystem.WARNING[5],
            "exceed_color": DesignSystem.INFO[5], # type: ignore
            "bg_color": DesignSystem.SLATE[1],
            "font_size": 18
        }

    def get_card_config(self, data_context):
        node = safe_get(data_context, f"operaciones.{self.section}.indicadores.{self.key}")
        if not node:
             node = safe_get(data_context, f"operaciones.{self.section}.promedios.{self.key}", {})

        val = node.get("valor", 0)
        fmt = self.layout.get("value_format", "abbreviated")
        
        return {
            "title": self.title,
            "value": f"{val:,.2f}%" if self.prefix == "%" else format_value(val, self.prefix, format_type=fmt),
            "monthly_display": node.get("monthly_display"),
            "monthly_delta": node.get("monthly_delta"),
            "ytd_display": node.get("ytd_display"),
            "ytd_delta": node.get("ytd_delta"),
            "label_mes": node.get("label_mes"),
            "label_ytd": node.get("label_ytd"),
            "vs_2024": node.get("vs_2024"),
            "meta_text": f"Meta: {format_value(node.get('meta', 0), self.prefix)}" if node.get("meta") else ""
        }

    def get_figure(self, data_context):
        node = safe_get(data_context, f"operaciones.{self.section}.indicadores.{self.key}")
        if not node:
             node = safe_get(data_context, f"operaciones.{self.section}.promedios.{self.key}", {})
        
        val_pct = node.get("valor_porcentaje", 0)
        meta_pct = node.get("meta_porcentaje", 100)
        exceeds = val_pct > meta_pct
        
        bar_color = self.gauge_params["exceed_color"] if exceeds else self.hex_color
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val_pct,
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
            margin=dict(l=5, r=5, t=25, b=5),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            font={'family': "Inter, sans-serif"}
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de indicador...", c=SemanticColors.TEXT_MUTED, size="sm") # type: ignore


class OpsComparisonStrategy(KPIStrategy):
    def __init__(self, title, data_key, color, section="dashboard", has_detail=True, layout_config=None, indicator_key_for_meta=None):
        super().__init__(title=title, color=color, icon="tabler:arrows-diff", has_detail=has_detail, layout_config=layout_config)
        self.data_key, self.section = data_key, section
        self.indicator_key_for_meta = indicator_key_for_meta

    def get_card_config(self, data_context):
        return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, f"operaciones.{self.section}.graficas.{self.data_key}", {"meses": [], "actual": [], "anterior": []})
        fig = go.Figure()

        fig.add_trace(go.Bar(x=ds["meses"], y=ds["anterior"], name="Anterior", marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.add_trace(go.Bar(x=ds["meses"], y=ds["actual"], name="Actual", marker_color=self.hex_color))

        meta_data = ds.get("meta")
        if not meta_data:
            target_key = self.indicator_key_for_meta
            if not target_key:
                target_key = self.data_key.replace("comparativa_", "").replace("_anual", "")

            meta_val = safe_get(data_context, f"operaciones.{self.section}.indicadores.{target_key}.meta", 0)

            if meta_val > 0:
                val_scaled = meta_val
                if ds["actual"] and ds["actual"][0] < 1000 and meta_val > 1_000_000:
                    val_scaled = meta_val / 1_000_000

                meta_data = [val_scaled] * len(ds["meses"])

        if meta_data:
            fig.add_trace(go.Scatter(
                x=ds["meses"], y=meta_data, name="Meta", mode="lines+markers+text",
                line=dict(color=DesignSystem.WARNING[5], width=3, dash="dot"),
                text=[f"{v:,.1f}" if v < 100 else f"{v:,.0f}" for v in meta_data],
                textposition="top center", textfont=dict(size=9, color=DesignSystem.WARNING[5], weight="bold")
            ))

        fig.update_layout(
            barmode='group', margin=dict(t=40, b=50, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(automargin=True), 
            paper_bgcolor=DesignSystem.TRANSPARENT, 
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de indicador...", c=SemanticColors.TEXT_MUTED, size="sm")  # type: ignore


class PerformanceGaugeStrategy(KPIStrategy):
    def __init__(self, title, key, color, prefix="", section="rendimientos", has_detail=True, layout_config=None):
        super().__init__(title=title, color=color, icon="tabler:chart-candle", has_detail=has_detail, layout_config=layout_config)
        self.key, self.prefix, self.section = key, prefix, section

    def get_card_config(self, data_context):
        node = safe_get(data_context, f"operaciones.{self.section}.indicadores.{self.key}", {})
        val = node.get("valor", 0)
        return {
            "title": self.title,
            "value": format_value(val, self.prefix),
            "monthly_display": node.get("monthly_display"),
            "monthly_delta": node.get("monthly_delta"),
            "ytd_display": node.get("ytd_display"),
            "ytd_delta": node.get("ytd_delta"),
            "label_mes": node.get("label_mes"),
            "label_ytd": node.get("label_ytd"),
            "meta_text": f"Meta: {node.get('meta', 0):,.2f}" if node.get('meta') else ""
        }

    def get_figure(self, data_context):
        node = safe_get(data_context, f"operaciones.{self.section}.indicadores.{self.key}", {})
        val, meta = node.get("valor", 0), node.get("meta", 1.0)
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            number={'font': {'size': 20, 'weight': 'bold'}, 'valueformat': '.2f'},
            gauge={
                'axis': {'range': [0, max(val, meta) * 1.2], 'visible': False},
                'bar': {'color': self.hex_color},
                'bgcolor': "rgba(0,0,0,0.1)",
                'threshold': {'line': {'color': "#f59e0b", 'width': 4}, 'thickness': 0.75, 'value': meta}
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(height=150, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de indicador...", c=SemanticColors.TEXT_MUTED, size="sm")  # type: ignore


class OpsPieStrategy(KPIStrategy):
    def __init__(self, has_detail=True, layout_config=None):
        super().__init__(title="Ingreso por Operación", icon="tabler:chart-pie", color="indigo", has_detail=has_detail, layout_config=layout_config)
    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        ds = safe_get(data_context, "operaciones.dashboard.graficas.mix_operacion", {"labels": [], "values": []})
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], 
            values=ds["values"], 
            hole=.6, 
            textinfo='percent',
            marker=dict(colors=DesignSystem.CHART_COLORS)
        )])
        fig.update_layout(
            showlegend=True, 
            legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"), 
            margin=dict(t=20, b=40, l=10, r=10), 
            height=340,
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig
    def render_detail(self, data_context): return None


class BalanceUnitStrategy(KPIStrategy):
    def __init__(self, has_detail=True, layout_config=None):
        super().__init__(title="Balanceo por Unidad", icon="tabler:scale", color="blue", has_detail=has_detail, layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "operaciones.dashboard.graficas.balanceo_unidades", {"unidades": [], "montos": []})
        target_val = safe_get(data_context, "operaciones.dashboard.promedios.ingreso_unit.valor", 254889)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=ds["unidades"], x=ds["montos"], orientation='h',
            marker_color=self.hex_color,
            text=[f"${v:,.2f}M" for v in ds["montos"]], textposition="auto"
        ))

        fig.add_vline(x=target_val/1e6 if target_val > 1000 else target_val,
                      line_width=4, line_dash="solid", line_color=DesignSystem.WARNING[5])

        fig.add_annotation(x=target_val/1e6 if target_val > 1000 else target_val, y=-0.5,
                           text=f"${target_val:,.0f}", showarrow=False,
                           font=dict(color=DesignSystem.WARNING[5], size=10, weight="bold"), yref="paper")

        fig.update_layout(
            yaxis=dict(autorange="reversed", automargin=True), 
            margin=dict(t=30, b=40, l=10, r=30), 
            height=340,
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig
    def render_detail(self, data_context): return None


class CostUtilityStackedStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Costo Viaje Total y Monto Utilidad", color="red", layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title, "is_simple": True}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "operaciones.costos.graficas.mensual_utilidad", {"meses": [], "costo": [], "utilidad_pct": []})
        costos, pcts = ds.get("costo", []), ds.get("utilidad_pct", [])
        utilidades = [(c * p / (100 - p)) if (100-p) > 0 else 0 for c, p in zip(costos, pcts)]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=ds["meses"], y=utilidades, name="Utilidad", marker_color=DesignSystem.SUCCESS[5],
                             text=[f"{p}%" for p in pcts], textposition="inside"))
        fig.add_trace(go.Bar(x=ds["meses"], y=costos, name="Costo Total", marker_color=DesignSystem.DANGER[5]))
        fig.update_layout(
            barmode='stack', margin=dict(t=30, b=40, l=10, r=10), 
            legend=dict(orientation="h", y=1.1, x=1, xanchor="right"),
            paper_bgcolor=DesignSystem.TRANSPARENT, 
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de indicador...", c=SemanticColors.TEXT_MUTED, size="sm")  # type: ignore


class OpsTableStrategy:
    def render_rutas(self, data_context):
        try: ds = data_context["operaciones"]["dashboard"]["tablas"]["rutas_cargado"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c=SemanticColors.TEXT_MUTED)  # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(h, fz=DesignSystem.FONT_TABLE, c=SemanticColors.TEXT_MUTED, fw=DesignSystem.FW_NORMAL)   # type: ignore
                for h in ds["h"]
            ])),
            dmc.TableTbody([dmc.TableTr([
                dmc.TableTd(str(c), fz=DesignSystem.FONT_TABLE) 
                for c in r
            ]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

    def render_tabbed_table(self, data_context, tab_key): 
        return dmc.Text(f"Cargando {tab_key}...", size="sm", py="xl", ta="center", c=SemanticColors.TEXT_MUTED)  # type: ignore


class CostBreakdownStrategy(KPIStrategy):
    def __init__(self, layout_config=None):
        super().__init__(title="Costo por Clasificación", color="blue", layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title, "is_simple": True}

    def get_figure(self, data_context):
        ds = safe_get(data_context, "operaciones.costos.graficas.desglose_conceptos", {"conceptos": [], "montos": []})
        fig = go.Figure(go.Bar(
            y=ds["conceptos"], x=ds["montos"], orientation='h', 
            marker_color=DesignSystem.BRAND[5],
            text=[format_value(v, "$") for v in ds["montos"]], textposition="auto"
        ))
        fig.update_layout(
            yaxis=dict(autorange="reversed", automargin=True), margin=dict(t=20, b=20, l=10, r=20),
            paper_bgcolor=DesignSystem.TRANSPARENT, 
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context):
        return dmc.Text("Detalle de indicador...", c=SemanticColors.TEXT_MUTED, size="sm")  # type: ignore


class CostTableStrategy:
    def render_margen_ruta(self, data_context):
        try: ds = data_context["operaciones"]["costos"]["tablas"]["margen_ruta"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c=SemanticColors.TEXT_MUTED)  # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(h, fz=DesignSystem.FONT_TABLE, c=SemanticColors.TEXT_MUTED, fw=DesignSystem.FW_NORMAL)   # type: ignore
                for h in ds["h"]
            ])),
            dmc.TableTbody([dmc.TableTr([
                dmc.TableTd(str(c), fz=DesignSystem.FONT_TABLE) 
                for c in r
            ]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)


class PerformanceTrendStrategy(KPIStrategy):
    def __init__(self, has_detail=True, layout_config=None):
        super().__init__(title="Tendencia Rendimiento Real (Kms/Lt)", icon="tabler:timeline", color="indigo", has_detail=has_detail, layout_config=layout_config)
    def get_card_config(self, data_context): return {"title": self.title}
    def get_figure(self, data_context):
        ds = safe_get(data_context, "operaciones.rendimientos.graficas.tendencia", {})
        fig = go.Figure()

        fig.add_trace(go.Bar(x=ds.get("meses"), y=ds.get("anterior"), name="Anterior", marker_color=DesignSystem.SLATE[3], opacity=0.6))
        fig.add_trace(go.Bar(x=ds.get("meses"), y=ds.get("actual"), name="Actual", marker_color=DesignSystem.BRAND[5]))

        meta_val = 3.0
        fig.add_trace(go.Scatter(
            x=ds.get("meses"), y=[meta_val]*len(ds.get("meses", [])),
            name="Meta", mode="lines+markers+text",
            line=dict(color=DesignSystem.WARNING[5], width=3, dash="dot"),
            text=[f"{meta_val:.2f}"]*len(ds.get("meses", [])),
            textposition="top center",
            textfont=dict(size=9, color=DesignSystem.WARNING[5])
        ))

        fig.update_layout(
            barmode='group',
            margin=dict(t=40, b=50, l=10, r=10),
            legend=dict(orientation="h", y=1.1, x=1, xanchor="right"),
            xaxis=dict(automargin=True),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig
    def render_detail(self, data_context): return None


class PerformanceMixStrategy(KPIStrategy):
    def __init__(self, has_detail=True, layout_config=None):
        super().__init__(title="Distribución de Rendimiento por Operación", icon="tabler:chart-pie-2", color="indigo", has_detail=has_detail,layout_config=layout_config)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["rendimientos"]["graficas"]["mix_operacion"]
        except: ds = {"labels": [], "values": []}
        fig = go.Figure(data=[go.Pie(
            labels=ds["labels"], 
            values=ds["values"], 
            hole=.6, 
            marker=dict(colors=DesignSystem.CHART_COLORS)
        )])
        fig.update_layout(
            showlegend=True, 
            legend=dict(orientation="h", y=-0.2), 
            margin=dict(t=30, b=40),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None


class PerformanceTableStrategy:
    def render_unit(self, data_context):
        try: ds = data_context["operaciones"]["rendimientos"]["tablas"]["unidad"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c=SemanticColors.TEXT_MUTED)  # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(h, fz=DesignSystem.FONT_TABLE, c=SemanticColors.TEXT_MUTED, fw=DesignSystem.FW_NORMAL)   # type: ignore
                for h in ds["h"]
            ])),
            dmc.TableTbody([dmc.TableTr([
                dmc.TableTd(str(c), fz=DesignSystem.FONT_TABLE) 
                for c in r
            ]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)

    def render_operador(self, data_context):
        try: ds = data_context["operaciones"]["rendimientos"]["tablas"]["operador"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c=SemanticColors.TEXT_MUTED)  # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(h, fz=DesignSystem.FONT_TABLE, c=SemanticColors.TEXT_MUTED, fw=DesignSystem.FW_NORMAL)   # type: ignore
                for h in ds["h"]
            ])),
            dmc.TableTbody([dmc.TableTr([
                dmc.TableTd(str(c), fz=DesignSystem.FONT_TABLE) 
                for c in r
            ]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True)


class RouteMapStrategy(KPIStrategy):
    def __init__(self, has_detail=True):
        super().__init__(title="Mapa de Rutas Activas", icon="tabler:map-2", color="indigo", has_detail=has_detail)

    def get_card_config(self, data_context): return {"title": self.title}

    def get_figure(self, data_context):
        try: ds = data_context["operaciones"]["rutas"]["mapa"]["puntos"]
        except: ds = []
        lats, lons, nombres = [p["lat"] for p in ds], [p["lon"] for p in ds], [p["nombre"] for p in ds]
        fig = go.Figure(go.Scattermapbox(lat=lats, lon=lons, mode='markers+lines', marker=dict(size=12, color=self.hex_color), text=nombres))
        fig.update_layout(
            mapbox_style="carto-positron", 
            mapbox_zoom=4, 
            mapbox_center={"lat": 23.6, "lon": -102.5}, 
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor=DesignSystem.TRANSPARENT,
            plot_bgcolor=DesignSystem.TRANSPARENT
        )
        return fig

    def render_detail(self, data_context): return None


class RouteDetailTableStrategy:
    def render_tabla_rutas(self, data_context):
        try: ds = data_context["operaciones"]["rutas"]["tablas"]["detalle_rutas"]
        except: return dmc.Text("Sin datos", ta="center", py="xl", c=SemanticColors.TEXT_MUTED)  # type: ignore
        return dmc.Table([
            dmc.TableThead(dmc.TableTr([
                dmc.TableTh(h, fz=DesignSystem.FONT_TABLE, c=SemanticColors.TEXT_MUTED, fw=DesignSystem.FW_NORMAL)   # type: ignore
                for h in ds["h"]
            ])),
            dmc.TableTbody([dmc.TableTr([
                dmc.TableTd(str(c), fz=DesignSystem.FONT_TABLE) 
                for c in r
            ]) for r in ds["r"]])
        ], striped="odd", withTableBorder=True, highlightOnHover=True)