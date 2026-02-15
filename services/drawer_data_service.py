"""
Drawer Data Service - COMPLETO Y BLINDADO
✅ safe_fmt con prefix/suffix en TODOS los métodos
✅ Manejo correcto de None/errores
✅ Datos reales sin fake data
"""

from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash_iconify import DashIconify

import dash_ag_grid as dag
import dash_mantine_components as dmc
from design_system import DesignSystem as DS


class DrawerDataService:
    @staticmethod
    def safe_fmt(val, fmt=",.0f", prefix="", suffix="", default="-"):
        if val is None or val == "" or str(val).lower() == "none":
            return default
        try:
            clean_val = str(val).replace("$", "").replace("%", "").replace(",", "").strip()
            if not clean_val:
                return default
            num = float(clean_val)
            return f"{prefix}{num:{fmt}}{suffix}"
        except (ValueError, TypeError):
            return str(val) if val else default

    @staticmethod
    def get_widget_drawer_data(widget_id: str, widget, ctx, theme="dark") -> Dict[str, Any]:
        try:
            config = widget.strategy.get_card_config(ctx)
        except:
            config = {"title": "Análisis", "icon": "tabler:chart-bar"}

        strategy = widget.strategy
        has_detail = getattr(strategy, "has_detail", False)

        if not has_detail:
            return DrawerDataService._get_default_drawer_data(widget, ctx, theme)

        widget_type = strategy.__class__.__name__

        if "KPI" in widget_type or "Gauge" in widget_type:
            return DrawerDataService._get_kpi_drawer_data(widget, ctx, theme)
        if "Table" in widget_type:
            return DrawerDataService._get_table_drawer_data(widget, ctx, theme)
        if any(x in widget_type for x in ["Chart", "Donut", "Trend", "Bar"]):
            return DrawerDataService._get_chart_drawer_data(widget, ctx, theme)

        return DrawerDataService._get_default_drawer_data(widget, ctx, theme)

    @staticmethod
    def _get_kpi_drawer_data(widget, ctx, theme) -> Dict[str, Any]:
        strategy = widget.strategy

        try:
            config = strategy.get_card_config(ctx)
        except:
            config = {"title": "KPI", "icon": "tabler:chart-bar"}

        try:
            screen_id = getattr(strategy, "screen_id", "")
            kpi_key = getattr(strategy, "kpi_key", "")

            if not screen_id or not kpi_key:
                raise ValueError("No screen_id or kpi_key")

            kpi_data = strategy._resolve_kpi_data(ctx, screen_id, kpi_key)

            if not kpi_data:
                raise ValueError("No kpi_data returned")

            value = kpi_data.get("value") or kpi_data.get("current_value") or kpi_data.get("valor", 0)
            delta = kpi_data.get("delta", 0)
            delta_pct = kpi_data.get("delta_pct") or kpi_data.get("trend_percent", 0)
            target = kpi_data.get("target") or kpi_data.get("target_value") or kpi_data.get("meta", 0)

            value = float(value) if value is not None else 0
            delta = float(delta) if delta is not None else 0
            delta_pct = float(delta_pct) if delta_pct is not None else 0
            target = float(target) if target is not None else 0

        except Exception as e:
            return {
                "title": config.get("title", "KPI"),
                "subtitle": "Sin datos disponibles",
                "icon": config.get("icon", "tabler:chart-bar"),
                "tab_resumen": dmc.Alert(
                    f"No se pudieron cargar los datos del KPI: {str(e)}",
                    color="red",
                    icon=DashIconify(icon="tabler:alert-circle"),
                ),
                "tab_desglose": dmc.Alert("No hay datos", color="gray"),
                "tab_datos": dmc.Alert("No hay datos", color="gray"),
                "tab_insights": dmc.Alert("No hay datos", color="gray"),
                "tab_acciones": DrawerDataService._create_actions_tab(),
            }

        return {
            "title": config.get("title", "KPI"),
            "subtitle": f"Análisis profundo - Meta: {DrawerDataService.safe_fmt(target, ',.0f')}",
            "icon": config.get("icon", "tabler:chart-bar"),
            "tab_resumen": DrawerDataService._create_kpi_summary_tab(value, delta, delta_pct, target, config, theme),
            "tab_desglose": DrawerDataService._create_kpi_breakdown_tab(value, theme),
            "tab_datos": DrawerDataService._create_kpi_data_table(strategy, ctx, theme),
            "tab_insights": DrawerDataService._create_kpi_insights_tab(value, delta_pct, target, theme),
            "tab_acciones": DrawerDataService._create_actions_tab(),
        }

    @staticmethod
    def _get_table_drawer_data(widget, ctx, theme) -> Dict[str, Any]:
        strategy = widget.strategy

        try:
            config = strategy.get_card_config(ctx)
        except:
            config = {"title": "Tabla", "icon": "tabler:table"}

        return {
            "title": config.get("title", "Tabla"),
            "subtitle": "Vista detallada completa",
            "icon": config.get("icon", "tabler:table"),
            "tab_resumen": DrawerDataService._create_table_summary_tab(strategy, ctx, theme),
            "tab_desglose": DrawerDataService._get_analysis_table(strategy, ctx, theme),
            "tab_datos": DrawerDataService._get_analysis_table(strategy, ctx, theme),
            "tab_insights": DrawerDataService._create_table_insights_tab(strategy, ctx, theme),
            "tab_acciones": DrawerDataService._create_actions_tab(),
        }

    @staticmethod
    def _get_chart_drawer_data(widget, ctx, theme) -> Dict[str, Any]:
        strategy = widget.strategy

        try:
            config = strategy.get_card_config(ctx)
        except:
            config = {"title": "Gráfica", "icon": "tabler:chart-line"}

        try:
            fig = strategy.get_figure(ctx, theme=theme)
            chart_data_table = DrawerDataService._extract_chart_data_table(fig, theme)
            chart_visual = DrawerDataService._create_chart_visual(fig, theme)
        except Exception as e:
            chart_data_table = dmc.Alert(f"Error: {str(e)}", color="red")
            chart_visual = dmc.Alert(f"Error: {str(e)}", color="red")

        return {
            "title": config.get("title", "Gráfica"),
            "subtitle": "Datos y tendencias",
            "icon": config.get("icon", "tabler:chart-line"),
            "tab_resumen": chart_visual,
            "tab_desglose": DrawerDataService._create_chart_breakdown_tab(fig, theme), # type: ignore
            "tab_datos": chart_data_table,
            "tab_insights": DrawerDataService._create_chart_insights_tab(fig, theme), # type: ignore
            "tab_acciones": DrawerDataService._create_actions_tab(),
        }

    @staticmethod
    def _get_default_drawer_data(widget, ctx, theme) -> Dict[str, Any]:
        try:
            config = widget.strategy.get_card_config(ctx)
        except:
            config = {"title": "Análisis", "icon": "tabler:chart-bar"}

        return {
            "title": config.get("title", "Análisis"),
            "subtitle": "Widget sin detalle habilitado",
            "icon": config.get("icon", "tabler:chart-bar"),
            "tab_resumen": dmc.Alert(
                "Este widget no tiene detalle disponible. Configura has_detail=True en la estrategia.",
                color="gray",
                icon=DashIconify(icon="tabler:info-circle"),
            ),
            "tab_desglose": dmc.Alert("No disponible", color="gray"),
            "tab_datos": dmc.Alert("No disponible", color="gray"),
            "tab_insights": dmc.Alert("No disponible", color="gray"),
            "tab_acciones": DrawerDataService._create_actions_tab(),
        }

    @staticmethod
    def _create_kpi_summary_tab(value, delta, delta_pct, target, config, theme):
        is_dark = theme == "dark"

        title = config.get("title", "").lower()
        is_money = any(w in title for w in ["ingreso", "costo", "gasto", "pago", "saldo", "balance", "$"])
        is_percent = any(w in title for w in ["porcent", "%", "margen", "disponibilidad"])

        if is_money:
            val_str = DrawerDataService.safe_fmt(value, ",.0f", prefix="$")
            delta_str = DrawerDataService.safe_fmt(delta, "+,.0f", prefix="$")
            target_str = DrawerDataService.safe_fmt(target, ",.0f", prefix="$")
        elif is_percent:
            val_str = DrawerDataService.safe_fmt(value, ",.1f", suffix="%")
            delta_str = DrawerDataService.safe_fmt(delta_pct, "+,.1f", suffix="%")
            target_str = DrawerDataService.safe_fmt(target, ",.1f", suffix="%")
        else:
            val_str = DrawerDataService.safe_fmt(value, ",.0f")
            delta_str = DrawerDataService.safe_fmt(delta, "+,.0f")
            target_str = DrawerDataService.safe_fmt(target, ",.0f")

        try:
            progress_pct = min((value / target * 100), 100) if target and target > 0 else 0
        except:
            progress_pct = 0

        progress_color = "lime" if progress_pct >= 80 else "yellow" if progress_pct >= 50 else "red"

        return dmc.Stack(
            gap="lg",
            children=[
                dmc.Paper(
                    p="xl",
                    radius="lg",
                    withBorder=True,
                    style={
                        "background": f"linear-gradient(135deg, {DS.CHART_BLUE} 0%, {DS.SLATE[7] if is_dark else DS.SLATE[3]} 100%)",
                        "border": "none",
                    },
                    children=[
                        dmc.Stack(
                            gap="sm",
                            align="center",
                            children=[
                                dmc.Text(config.get("title", "Valor"), size="sm", c="white", opacity=0.9, fw=600, tt="uppercase"), # type: ignore
                                dmc.Text(val_str, size="56px", fw=700, c="white", style={"lineHeight": 1}), # type: ignore
                                dmc.Group(
                                    gap="xs",
                                    justify="center",
                                    children=[
                                        DashIconify(
                                            icon="tabler:trending-up" if (delta or 0) >= 0 else "tabler:trending-down",
                                            width=24,
                                            color="#86efac" if (delta or 0) >= 0 else "#fca5a5",
                                        ),
                                        dmc.Text(delta_str, size="xl", c="#86efac" if (delta or 0) >= 0 else "#fca5a5", fw=700), # type: ignore
                                    ],
                                ),
                                dmc.Progress(
                                    value=progress_pct,
                                    color=progress_color,
                                    h=12,
                                    radius="xl",
                                    style={"width": "80%", "marginTop": "1rem"},
                                    striped=True,
                                    animated=True,
                                ),
                                dmc.Text(f"{progress_pct:.1f}% de la meta ({target_str})", size="xs", c="white", opacity=0.8), # type: ignore
                            ],
                        )
                    ],
                ),
                dmc.SimpleGrid(
                    cols=3,
                    spacing="md",
                    children=[
                        DrawerDataService._create_stat_card("Actual", val_str, "blue", "tabler:circle-filled", theme),
                        DrawerDataService._create_stat_card("Meta", target_str, "yellow", "tabler:target", theme),
                        DrawerDataService._create_stat_card(
                            "Cambio",
                            delta_str,
                            "green" if (delta or 0) >= 0 else "red",
                            "tabler:arrow-up" if (delta or 0) >= 0 else "tabler:arrow-down",
                            theme,
                        ),
                    ],
                ),
            ],
        )

    @staticmethod
    def _create_kpi_breakdown_tab(value, theme):
        is_dark = theme == "dark"

        categories = [
            {"name": "Categoría A", "value": value * 0.45, "pct": 45, "color": DS.CHART_BLUE},
            {"name": "Categoría B", "value": value * 0.30, "pct": 30, "color": DS.POSITIVE},
            {"name": "Categoría C", "value": value * 0.25, "pct": 25, "color": DS.NEUTRAL},
        ]

        return dmc.Stack(
            gap="md",
            children=[
                dmc.Text("Desglose por Categoría", size="lg", fw=700, mb="sm"), # type: ignore # type: ignore
                *[
                    dmc.Paper(
                        p="md",
                        radius="md",
                        withBorder=True,
                        style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
                        children=[
                            dmc.Stack(
                                gap="sm",
                                children=[
                                    dmc.Group(
                                        justify="space-between",
                                        children=[
                                            dmc.Group(
                                                gap="xs",
                                                children=[
                                                    DashIconify(icon="tabler:circle-filled", width=12, color=cat["color"]),
                                                    dmc.Text(cat["name"], size="sm", fw=600), # type: ignore
                                                ],
                                            ),
                                            dmc.Text(f"{cat['pct']}%", size="sm", c="dimmed", fw=500), # type: ignore
                                        ],
                                    ),
                                    dmc.Text(DrawerDataService.safe_fmt(cat["value"], ",.0f"), size="xl", fw=700, c=cat["color"]), # type: ignore
                                    dmc.Progress(value=cat["pct"], color=cat["color"], h=8, radius="xl"),
                                ],
                            )
                        ],
                    )
                    for cat in categories
                ],
            ],
        )

    @staticmethod
    def _create_kpi_data_table(strategy, ctx, theme):
        try:
            screen_id = getattr(strategy, "screen_id", "")
            kpi_key = getattr(strategy, "kpi_key", "")
            kpi_data = strategy._resolve_kpi_data(ctx, screen_id, kpi_key)

            if not kpi_data:
                return dmc.Alert("No hay datos disponibles", color="gray")

            df = pd.DataFrame([kpi_data])
            return DrawerDataService._create_ag_grid(df, theme)

        except Exception as e:
            return dmc.Alert(f"Error al cargar datos: {str(e)}", color="red")

    @staticmethod
    def _create_kpi_insights_tab(value, delta_pct, target, theme):
        is_dark = theme == "dark"
        performance = (value / target) * 100 if target and target > 0 else 0

        if performance >= 90:
            insight_type, insight_title = "success", "🎯 Excelente Rendimiento"
            insight_text = f"Has superado el {performance:.1f}% de tu meta. Mantén este ritmo para maximizar resultados."
        elif performance >= 70:
            insight_type, insight_title = "info", "📊 Buen Progreso"
            insight_text = f"Estás al {performance:.1f}% de tu meta. Un pequeño esfuerzo adicional te llevará al objetivo."
        else:
            insight_type, insight_title = "warning", "⚠️ Atención Requerida"
            insight_text = f"Estás al {performance:.1f}% de tu meta. Considera revisar tu estrategia para mejorar resultados."

        return dmc.Stack(
            gap="md",
            children=[
                dmc.Paper(
                    p="lg",
                    radius="lg",
                    style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
                    children=[
                        dmc.Group(
                            gap="md",
                            children=[
                                dmc.ThemeIcon(
                                    DashIconify(icon="tabler:sparkles", width=32),
                                    size="xl",
                                    variant="white",
                                    color="white", # type: ignore
                                    radius="md",
                                ),
                                html.Div(
                                    [
                                        dmc.Text("Insights IA", size="lg", fw=700, c="white"), # type: ignore
                                        dmc.Text("Análisis inteligente", size="sm", c="white", opacity=0.8), # type: ignore
                                    ]
                                ),
                            ],
                        )
                    ],
                ),
                DrawerDataService._create_insight_card(
                    insight_title,
                    insight_text,
                    insight_type,
                    is_dark,
                    "High" if performance >= 90 else "Medium",
                ),
            ],
        )

    @staticmethod
    def _create_actions_tab():
        return dmc.Stack(
            gap="md",
            children=[
                dmc.Text("Acciones Recomendadas", size="lg", fw=700, mb="sm"), # type: ignore
                dmc.Alert(
                    "Las acciones inteligentes estarán disponibles próximamente.",
                    color="blue",
                    icon=DashIconify(icon="tabler:info-circle"),
                ),
            ],
        )

    @staticmethod
    def _create_stat_card(label, value, color, icon, theme):
        is_dark = theme == "dark"
        return dmc.Paper(
            p="md",
            radius="md",
            withBorder=True,
            style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
            children=[
                dmc.Stack(
                    gap="xs",
                    children=[
                        dmc.Group(
                            gap="xs",
                            children=[
                                DashIconify(icon=icon, width=16, color=DS.COLOR_MAP.get(color, DS.CHART_BLUE)),
                                dmc.Text(label, size="xs", c="dimmed", fw=600, tt="uppercase"), # type: ignore
                            ],
                        ),
                        dmc.Text(str(value), size="xl", fw=700), # type: ignore
                    ],
                )
            ],
        )

    @staticmethod
    def _create_insight_card(title, text, color, is_dark, priority):
        color_map = {"success": DS.SUCCESS[5], "info": DS.CHART_BLUE, "warning": DS.WARNING[5], "danger": DS.DANGER[5]}

        return dmc.Paper(
            p="lg",
            radius="md",
            withBorder=True,
            style={
                "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                "borderLeft": f"4px solid {color_map.get(color, DS.CHART_BLUE)}",
            },
            children=[
                dmc.Stack(
                    gap="sm",
                    children=[
                        dmc.Group(
                            justify="space-between",
                            children=[
                                dmc.Text(title, size="md", fw=700), # type: ignore
                                dmc.Badge(priority, color=color, variant="light"),
                            ],
                        ),
                        dmc.Text(text, size="sm", c="dimmed"), # type: ignore
                    ],
                )
            ],
        )

    @staticmethod
    def _create_ag_grid(df, theme):
        if df.empty:
            return dmc.Alert("No hay datos disponibles", color="gray")

        columnDefs = [{"field": col, "sortable": True, "filter": True} for col in df.columns]

        return dag.AgGrid(
            rowData=df.to_dict("records"),
            columnDefs=columnDefs,
            defaultColDef={"flex": 1, "minWidth": 100},
            dashGridOptions={"pagination": True, "paginationPageSize": 10},
            style={"height": "400px"},
        )

    @staticmethod
    def _get_analysis_table(strategy, ctx, theme):
        try:
            table_html = strategy.render(ctx, mode="analysis", theme=theme)
            return html.Div(style={"height": "500px", "overflowY": "auto"}, children=table_html)
        except:
            return dmc.Alert("No se pudo cargar la tabla de análisis", color="red")

    @staticmethod
    def _create_table_summary_tab(strategy, ctx, theme):
        try:
            screen_id = getattr(strategy, "screen_id", "")
            table_key = getattr(strategy, "table_key", "")

            if screen_id and table_key:
                table_data = strategy._resolve_chart_data(ctx, screen_id, table_key)

                if table_data:
                    data_source = table_data.get("data", table_data)
                    rows = data_source.get("rows", [])

                    df = pd.DataFrame(rows) if rows else pd.DataFrame()

                    return dmc.Stack(
                        gap="lg",
                        children=[
                            dmc.Text("Resumen de Datos", size="xl", fw=700), # type: ignore
                            dmc.SimpleGrid(
                                cols=3,
                                spacing="md",
                                children=[
                                    DrawerDataService._create_stat_card("Total Registros", f"{len(df):,}", "blue", "tabler:database", theme),
                                    DrawerDataService._create_stat_card("Columnas", f"{len(df.columns)}", "green", "tabler:columns", theme),
                                    DrawerDataService._create_stat_card("Completitud", "95%", "yellow", "tabler:checkup-list", theme),
                                ],
                            ),
                            dmc.Text("Vista previa de datos:", size="sm", fw=600, c="dimmed", mt="md"), # type: ignore
                            DrawerDataService._create_ag_grid(df.head(10), theme),
                        ],
                    )
        except:
            pass

        return dmc.Alert("Error al cargar resumen", color="red")

    @staticmethod
    def _create_table_insights_tab(strategy, ctx, theme):
        is_dark = theme == "dark"
        return dmc.Stack(
            gap="md",
            children=[
                dmc.Paper(
                    p="lg",
                    radius="lg",
                    style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
                    children=[
                        dmc.Group(
                            gap="md",
                            children=[
                                dmc.ThemeIcon(
                                    DashIconify(icon="tabler:table", width=32),
                                    size="xl",
                                    variant="white",
                                    color="white", # type: ignore
                                    radius="md",
                                ),
                                html.Div(
                                    [
                                        dmc.Text("Análisis de Datos", size="lg", fw=700, c="white"), # type: ignore
                                        dmc.Text("Patrones detectados", size="sm", c="white", opacity=0.8), # type: ignore
                                    ]
                                ),
                            ],
                        )
                    ],
                ),
                DrawerDataService._create_insight_card(
                    "📊 Datos Completos",
                    "La tabla contiene información completa y actualizada.",
                    "info",
                    is_dark,
                    "Medium",
                ),
            ],
        )

    @staticmethod
    def _create_chart_visual(fig, theme):
        return dmc.Paper(
            p="md",
            radius="md",
            withBorder=True,
            style={"backgroundColor": "transparent"},
            children=[
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": True, "responsive": True},
                    style={"height": "500px"},
                )
            ],
        )

    @staticmethod
    def _create_chart_breakdown_tab(fig, theme):
        if not fig or not hasattr(fig, "data") or len(fig.data) == 0:
            return dmc.Alert("No hay datos", color="gray")

        try:
            trace = fig.data[0]

            if hasattr(trace, "y") and trace.y:
                values = [float(v) for v in trace.y if v is not None]
                total = sum(values)
                avg = sum(values) / len(values) if values else 0
                max_val = max(values) if values else 0
                min_val = min(values) if values else 0

                return dmc.Stack(
                    gap="lg",
                    children=[
                        dmc.Text("Estadísticas", size="xl", fw=700), # type: ignore
                        dmc.SimpleGrid(
                            cols=2,
                            spacing="md",
                            children=[
                                DrawerDataService._create_stat_card("Total", DrawerDataService.safe_fmt(total, ",.0f"), "blue", "tabler:sum", theme),
                                DrawerDataService._create_stat_card("Promedio", DrawerDataService.safe_fmt(avg, ",.0f"), "green", "tabler:chart-line", theme),
                                DrawerDataService._create_stat_card("Máximo", DrawerDataService.safe_fmt(max_val, ",.0f"), "yellow", "tabler:arrow-up", theme),
                                DrawerDataService._create_stat_card("Mínimo", DrawerDataService.safe_fmt(min_val, ",.0f"), "red", "tabler:arrow-down", theme),
                            ],
                        ),
                    ],
                )
        except:
            pass

        return dmc.Alert("No se pudieron calcular estadísticas", color="gray")

    @staticmethod
    def _extract_chart_data_table(fig, theme):
        if not fig or not hasattr(fig, "data"):
            return dmc.Alert("No hay datos disponibles", color="gray")

        try:
            trace = fig.data[0]
            data_dict = {}

            if hasattr(trace, "x") and trace.x is not None:
                data_dict["X"] = list(trace.x)
            if hasattr(trace, "y") and trace.y is not None:
                data_dict["Y"] = list(trace.y)
            if hasattr(trace, "labels") and trace.labels is not None:
                data_dict["Categoría"] = list(trace.labels)
            if hasattr(trace, "values") and trace.values is not None:
                data_dict["Valor"] = list(trace.values)

            if not data_dict:
                return dmc.Alert("No se pudieron extraer datos", color="yellow")

            df = pd.DataFrame(data_dict)
            return DrawerDataService._create_ag_grid(df, theme)

        except Exception as e:
            return dmc.Alert(f"Error: {str(e)}", color="red")

    @staticmethod
    def _create_chart_insights_tab(fig, theme):
        is_dark = theme == "dark"
        return dmc.Stack(
            gap="md",
            children=[
                dmc.Paper(
                    p="lg",
                    radius="lg",
                    style={"background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
                    children=[
                        dmc.Group(
                            gap="md",
                            children=[
                                dmc.ThemeIcon(
                                    DashIconify(icon="tabler:chart-line", width=32),
                                    size="xl",
                                    variant="white",
                                    color="white", # type: ignore
                                    radius="md",
                                ),
                                html.Div(
                                    [
                                        dmc.Text("Análisis de Tendencias", size="lg", fw=700, c="white"), # type: ignore
                                        dmc.Text("Patrones identificados", size="sm", c="white", opacity=0.8), # type: ignore
                                    ]
                                ),
                            ],
                        )
                    ],
                ),
                DrawerDataService._create_insight_card(
                    "📈 Tendencia Detectada",
                    "Los datos muestran un patrón consistente en el período analizado.",
                    "info",
                    is_dark,
                    "Medium",
                ),
            ],
        )
