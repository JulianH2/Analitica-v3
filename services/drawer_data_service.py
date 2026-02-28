from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash_iconify import DashIconify

import dash_ag_grid as dag
import dash_mantine_components as dmc
from design_system import DesignSystem as DS, dmc as _dmc

# Lazy import to avoid circular; only used inside methods.
def _llm_insight(title: str, stats: str) -> str:
    try:
        from services.ai_chat_service import generate_insight_sync
        return generate_insight_sync(title, stats)
    except Exception:
        return ""


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
            key = getattr(strategy, "key", "")

            if not screen_id or not key:
                raise ValueError("No screen_id or key")

            kpi_data = strategy._resolve_kpi_data(ctx, screen_id, key)

            if not kpi_data:
                raise ValueError("No kpi_data returned")

            value    = kpi_data.get("value") or kpi_data.get("current_value") or kpi_data.get("valor", 0)
            target   = kpi_data.get("target") or kpi_data.get("target_value") or kpi_data.get("meta", 0)
            vs_prev  = kpi_data.get("vs_last_year_value", 0) or 0
            delta    = kpi_data.get("delta") or (float(value or 0) - float(vs_prev or 0))
            delta_pct = kpi_data.get("delta_pct") or kpi_data.get("trend_percent") or kpi_data.get("vs_last_year_delta", 0)

            value     = float(value)     if value     is not None else 0
            target    = float(target)    if target    is not None else 0
            vs_prev   = float(vs_prev)   if vs_prev   is not None else 0
            delta     = float(delta)     if delta     is not None else 0
            delta_pct = float(delta_pct) if delta_pct is not None else 0

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

        has_target = target is not None and float(target) > 0

        ytd_value = kpi_data.get("ytd_value")
        ytd_delta = kpi_data.get("ytd_delta")
        ytd_target = (
            kpi_data.get("ytd_target") or kpi_data.get("target_ytd")
            or kpi_data.get("ytd_meta") or kpi_data.get("meta_ytd")
        )
        if ytd_target is None and ytd_value is not None and ytd_delta is not None:
            try:
                d = float(ytd_delta)
                y = float(ytd_value)
                divisor = 1 + d if abs(d) < 10 else 1 + d / 100
                if abs(divisor) > 0.001:
                    ytd_target = y / divisor
            except Exception:
                pass

        subtitle_parts = []
        if has_target:
            subtitle_parts.append(f"Meta: {DrawerDataService.safe_fmt(target, ',.0f')}")
        if ytd_target and float(ytd_target) > 0:
            subtitle_parts.append(f"Meta YTD: {DrawerDataService.safe_fmt(ytd_target, ',.0f')}")
        subtitle = " · ".join(subtitle_parts) if subtitle_parts else "Sin meta configurada"
        explanation = DrawerDataService._create_kpi_explanation_section(config, theme == "dark")
        resumen_children: List[Any] = [
            DrawerDataService._create_kpi_summary_tab(value, delta, delta_pct, target, config, theme),
        ]

        resumen_children.append(
            DrawerDataService._create_kpi_breakdown_tab(kpi_data, config, theme)
        )
        if explanation is not None:
            resumen_children.append(explanation)
        resumen_children.append(
            DrawerDataService._create_kpi_insights_tab(value, delta, delta_pct, target, kpi_data, config, theme)
        )

        # ── Inline desglose section (raw KPI data table) ──
        resumen_children.append(DrawerDataService._section_header("Datos del indicador", "tabler:table"))
        resumen_children.append(DrawerDataService._create_kpi_data_table(strategy, ctx, theme))

        return {
            "title": config.get("title", "KPI"),
            "subtitle": subtitle,
            "icon": config.get("icon", "tabler:chart-bar"),
            "tab_resumen": dmc.Stack(gap="lg", children=resumen_children),
            "tab_desglose": None,
            "tab_datos": None,
            "tab_insights": None,
            "tab_acciones": DrawerDataService._create_kpi_actions_tab(config, kpi_data, value, target, theme),
        }

    @staticmethod
    def _get_table_drawer_data(widget, ctx, theme) -> Dict[str, Any]:
        strategy = widget.strategy

        try:
            config = strategy.get_card_config(ctx)
        except:
            config = {"title": "Tabla", "icon": "tabler:table"}

        title = config.get("title", "Tabla")

        # Build export rows from the strategy dataframe
        export_rows: List[Dict] = []
        try:
            df = DrawerDataService._load_strategy_dataframe(strategy, ctx)
            if not df.empty:
                export_rows = df.to_dict("records")
        except Exception:
            pass

        chat_prompt = (
            f"@{title}: analiza los datos de esta tabla, señala los valores más relevantes, "
            f"outliers o concentraciones, y sugiere qué acción tomar."
        )

        sh = DrawerDataService._section_header
        unified = dmc.Stack(
            gap="lg",
            children=[
                # ── Summary: stat cards + top-10 grid ──
                DrawerDataService._create_table_summary_tab(strategy, ctx, theme),

                # ── Statistical breakdown ──
                sh("Análisis estadístico", "tabler:chart-bar"),
                DrawerDataService._create_table_breakdown_tab(strategy, ctx, theme),

                # ── Insights + AI ──
                sh("Insights y análisis IA", "tabler:brain"),
                DrawerDataService._create_table_insights_tab(strategy, ctx, theme),
            ],
        )

        try:
            stat_df = DrawerDataService._load_strategy_dataframe(strategy, ctx)
            _stat_label_cols = [stat_df.columns[0]] if not stat_df.empty else []
            engine_result = DrawerDataService._run_statistical_engine(stat_df, label_cols=_stat_label_cols)
        except Exception:
            engine_result = {}

        try:
            full_df = DrawerDataService._load_strategy_dataframe(strategy, ctx)
            full_data_tab = DrawerDataService._create_ag_grid(full_df, theme, show_totals=True) if not full_df.empty else None
        except Exception:
            full_data_tab = None

        return {
            "title": title,
            "subtitle": "Vista detallada completa",
            "icon": config.get("icon", "tabler:table"),
            "tab_resumen": unified,
            "tab_desglose": DrawerDataService._render_estadisticas_tab(engine_result, theme),
            "tab_datos": full_data_tab,
            "tab_insights": None,
            "tab_acciones": DrawerDataService._create_generic_actions_tab(title, chat_prompt, export_rows),
        }

    @staticmethod
    def _get_chart_drawer_data(widget, ctx, theme) -> Dict[str, Any]:
        strategy = widget.strategy

        try:
            config = strategy.get_card_config(ctx)
        except:
            config = {"title": "Gráfica", "icon": "tabler:chart-line"}

        fig = None
        chart_data_table = dmc.Alert("Sin datos", color="gray")
        chart_visual = dmc.Alert("Sin datos", color="gray")
        export_rows: List[Dict] = []

        try:
            fig = strategy.get_figure(ctx, theme=theme)
            chart_data_table = DrawerDataService._extract_chart_data_table(fig, theme)
            chart_visual = DrawerDataService._create_chart_visual(fig, theme)
            # Build export_rows from ALL traces (merged by shared label axis)
            if fig and hasattr(fig, "data") and fig.data:
                export_rows = DrawerDataService._build_multi_trace_export(fig)
        except Exception as e:
            chart_data_table = dmc.Alert(f"Error: {str(e)}", color="red")
            chart_visual = dmc.Alert(f"Error: {str(e)}", color="red")

        title = config.get("title", "Gráfica")
        chat_prompt = (
            f"@{title}: analiza las tendencias, identifica el período con mayor y menor valor, "
            f"y recomienda una acción concreta según los datos del gráfico."
        )

        sh = DrawerDataService._section_header
        unified = dmc.Stack(
            gap="lg",
            children=[
                # ── Main chart visual ──
                chart_visual,

                # ── Period breakdown + stats ──
                sh("Desglose por período", "tabler:chart-bar"),
                DrawerDataService._create_chart_breakdown_tab(fig, theme),  # type: ignore

                # ── Raw data table (all traces) ──
                sh("Datos", "tabler:table"),
                chart_data_table,
            ],
        )

        try:
            fig_df = DrawerDataService._fig_to_dataframe(fig) if fig else pd.DataFrame()
            _fig_label_cols = [fig_df.columns[0]] if not fig_df.empty else []
            engine_result = DrawerDataService._run_statistical_engine(fig_df, label_cols=_fig_label_cols)
        except Exception:
            engine_result = {}

        return {
            "title": title,
            "subtitle": "Datos y tendencias",
            "icon": config.get("icon", "tabler:chart-line"),
            "tab_resumen": unified,
            "tab_desglose": DrawerDataService._render_estadisticas_tab(engine_result, theme),
            "tab_datos": None,
            "tab_insights": DrawerDataService._create_chart_insights_tab(fig, theme),  # type: ignore
            "tab_acciones": DrawerDataService._create_generic_actions_tab(title, chat_prompt, export_rows),
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

    # ── Section header helper (used to visually separate inline sections) ──────

    @staticmethod
    def _section_header(label: str, icon: str = "tabler:chevron-right"):
        """Creates a compact section divider for the unified single-scroll drawer view."""
        return dmc.Group(
            gap="xs",
            mt="xl",
            mb="sm",
            children=[
                DashIconify(icon=icon, width=14, color=DS.NEXA_GOLD),
                dmc.Text(label, size="xs", fw=700, c="dimmed", tt="uppercase"),  # type: ignore
                dmc.Divider(style={"flex": 1}),
            ],
        )

    # ── KPI summary ────────────────────────────────────────────────────────────

    @staticmethod
    def _create_kpi_summary_tab(value, delta, delta_pct, target, config, theme):
        is_dark = theme == "dark"
        has_target = target is not None and float(target) > 0

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


        if has_target:
            is_positive = float(value or 0) >= float(target)
        else:
            is_positive = (delta or 0) >= 0
        trend_color = "#86efac" if is_positive else "#fca5a5"
        trend_icon = "tabler:trending-up" if is_positive else "tabler:trending-down"

        inner_children = [
            dmc.Text(config.get("title", "Valor"), size="sm", c="white", opacity=0.9, fw=600, tt="uppercase"),  # type: ignore
            dmc.Text(val_str, size="56px", fw=700, c="white", style={"lineHeight": 1}),  # type: ignore
            dmc.Group(
                gap="xs",
                justify="center",
                children=[
                    DashIconify(icon=trend_icon, width=24, color=trend_color),
                    dmc.Text(delta_str, size="xl", c=trend_color, fw=700),  # type: ignore
                ],
            ),
        ]

        # Only show progress bar and meta text when a real target exists
        if has_target:
            try:
                progress_pct = min((value / target * 100), 100)
            except Exception:
                progress_pct = 0
            progress_color = "lime" if progress_pct >= 80 else "yellow" if progress_pct >= 50 else "red"
            inner_children += [
                dmc.Progress(
                    value=progress_pct,
                    color=progress_color,
                    h=12,
                    radius="xl",
                    style={"width": "80%", "marginTop": "1rem"},
                    striped=True,
                    animated=True,
                ),
                dmc.Text(f"{progress_pct:.1f}% de la meta ({target_str})", size="xs", c="white", opacity=0.8),  # type: ignore
            ]

        return dmc.Paper(
            p="xl",
            radius="lg",
            withBorder=True,
            style={
                "background": f"linear-gradient(135deg, {DS.CHART_BLUE} 0%, {DS.SLATE[7] if is_dark else DS.SLATE[3]} 100%)",
                "border": "none",
            },
            children=[dmc.Stack(gap="sm", align="center", children=inner_children)],
        )

    @staticmethod
    def _create_kpi_breakdown_tab(kpi_data, config, theme):
        """Show real KPI comparison as a card grid — same style as summary stat cards."""
        title = config.get("title", "").lower()
        is_money   = any(w in title for w in ["ingreso", "costo", "gasto", "pago", "saldo", "balance", "$"])
        is_percent = any(w in title for w in ["porcent", "%", "margen", "disponibilidad"])

        def _fmt(val):
            if val is None or val == 0:
                return "-"
            try:
                v = float(val)
                if is_money:   return DrawerDataService.safe_fmt(v, ",.0f", prefix="$")
                if is_percent: return DrawerDataService.safe_fmt(v, ",.1f", suffix="%")
                return DrawerDataService.safe_fmt(v, ",.2f")
            except Exception:
                return str(val) if val else "-"

        def _fmt_delta(val):
            if val is None or val == 0:
                return "-"
            try:
                v = float(val)
                return DrawerDataService.safe_fmt(v * 100, "+,.1f", suffix="%") if abs(v) < 10 else DrawerDataService.safe_fmt(v, "+,.1f", suffix="%")
            except Exception:
                return str(val) if val else "-"

        value      = kpi_data.get("value")
        target     = kpi_data.get("target")
        vs_prev    = kpi_data.get("vs_last_year_value")
        ytd        = kpi_data.get("ytd_value")
        delta_prev = kpi_data.get("vs_last_year_delta")
        ytd_delta  = kpi_data.get("ytd_delta")

        def _prefmt(key, fallback_val):
            fmtd = kpi_data.get(key + "_formatted")
            return fmtd if fmtd else _fmt(fallback_val)

        has_target = target is not None and float(target or 0) != 0

        ytd_target = (
            kpi_data.get("ytd_target")
            or kpi_data.get("target_ytd")
            or kpi_data.get("ytd_meta")
            or kpi_data.get("meta_ytd")
        )
        if ytd_target is None and ytd is not None and ytd_delta is not None:
            try:
                d = float(ytd_delta)
                y = float(ytd)
                divisor = 1 + d if abs(d) < 10 else 1 + d / 100
                if abs(divisor) > 0.001:
                    ytd_target = y / divisor
            except Exception:
                pass

        has_ytd_target = ytd_target is not None and float(ytd_target or 0) > 0

        # (label, val_str, color, icon, value_color)
        rows: List[tuple] = []
        if value is not None:
            rows.append(("Valor Actual", _prefmt("value", value), "blue", "tabler:circle-filled", None))
        if has_target:
            rows.append(("Meta Mensual", _prefmt("target", target), "yellow", "tabler:target", None))
        if has_ytd_target:
            rows.append(("Meta YTD", _fmt(ytd_target), "orange", "tabler:target-arrow", None))
        if vs_prev is not None and vs_prev != 0:
            rows.append(("Año Anterior", _prefmt("vs_last_year", vs_prev), "gray", "tabler:calendar-stats", None))
        if delta_prev is not None and delta_prev != 0:
            is_pos = float(delta_prev or 0) >= 0
            vc = "green" if is_pos else "red"
            rows.append(("Var. Año Ant.", _fmt_delta(delta_prev), vc, "tabler:trending-up" if is_pos else "tabler:trending-down", vc))
        if ytd is not None and ytd != 0:
            rows.append(("Acum. YTD", _prefmt("ytd", ytd), "indigo", "tabler:calendar-week", None))
        if ytd_delta is not None and ytd_delta != 0:
            is_pos = float(ytd_delta or 0) >= 0
            vc = "green" if is_pos else "red"
            rows.append(("Var. YTD vs Meta", _fmt_delta(ytd_delta), vc, "tabler:chart-bar", vc))

        if not rows:
            return dmc.Alert("No hay datos comparativos disponibles para este KPI.", color="gray")

        return dmc.Stack(
            gap="sm",
            children=[
                dmc.Text("Comparativo", size="xs", fw=700, c="dimmed", tt="uppercase"),  # type: ignore
                dmc.SimpleGrid(
                    cols=3,
                    spacing="sm",
                    children=[
                        DrawerDataService._create_stat_card(label, val_str, color, icon, theme, value_color)
                        for label, val_str, color, icon, value_color in rows
                    ],
                ),
            ],
        )

    @staticmethod
    def _create_kpi_data_table(strategy, ctx, theme):
        try:
            screen_id = getattr(strategy, "screen_id", "")
            key = getattr(strategy, "key", "")
            kpi_data = strategy._resolve_kpi_data(ctx, screen_id, key)

            if not kpi_data:
                return dmc.Alert("No hay datos disponibles", color="gray")

            df = pd.DataFrame([kpi_data])
            return DrawerDataService._create_ag_grid(df, theme, show_totals=False)

        except Exception as e:
            return dmc.Alert(f"Error al cargar datos: {str(e)}", color="red")

    # ── KPI explanation — formula/definition lookup ────────────────────────────

    _KPI_EXPLANATIONS: dict = {
        "ingreso viaje":    ("Ingreso Total ÷ Total de Viajes", "Mide el ingreso promedio generado por cada viaje operado en el período."),
        "ingreso por viaje":("Ingreso Total ÷ Total de Viajes", "Mide el ingreso promedio generado por cada viaje operado en el período."),
        "costo viaje":      ("Costo Total ÷ Total de Viajes", "Costo promedio incurrido por cada viaje operado."),
        "costo por viaje":  ("Costo Total ÷ Total de Viajes", "Costo promedio incurrido por cada viaje operado."),
        "disponibilidad":   ("Unidades Disponibles ÷ Total Unidades × 100", "Porcentaje de la flota lista para operar en el período."),
        "utilizaci":        ("Unidades Activas ÷ Total Unidades × 100", "Porcentaje de uso efectivo de la flota disponible."),
        "cobranza":         ("Σ Montos Cobrados en el período", "Total recuperado de cuentas por cobrar durante el período analizado."),
        "km unidad":        ("Km Totales ÷ Unidades Activas", "Kilómetros promedio recorridos por unidad activa en el período."),
        "km por unidad":    ("Km Totales ÷ Unidades Activas", "Kilómetros promedio recorridos por unidad activa en el período."),
        "facturaci":        ("Σ Facturas Emitidas", "Valor total de las facturas emitidas durante el período."),
    }

    @staticmethod
    def _create_kpi_explanation_section(config: dict, is_dark: bool):
        title_raw = (config.get("title") or "")
        title = title_raw.lower()
        found = None
        for key, (formula, desc) in DrawerDataService._KPI_EXPLANATIONS.items():
            if key in title:
                found = (formula, desc)
                break
        if not found:
            return None
        formula, desc = found
        return dmc.Paper(
            p="md", radius="md", withBorder=True,
            style={
                "backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY,
                "borderLeft": f"4px solid {DS.NEXA_GOLD}",
            },
            children=[dmc.Stack(gap="xs", children=[
                dmc.Group(gap="xs", children=[
                    DashIconify(icon="tabler:calculator", width=14, color=DS.NEXA_GOLD),
                    dmc.Text("Explicación del indicador", size="xs", fw=700, c="dimmed", tt="uppercase"),  # type: ignore
                ]),
                dmc.Text(desc, size="sm"),  # type: ignore
                dmc.Text(f"Fórmula: {formula}", size="xs", c="dimmed", style={"fontFamily": "monospace"}),  # type: ignore
            ])],
        )

    # ── KPI actions tab ────────────────────────────────────────────────────────

    @staticmethod
    def _create_kpi_actions_tab(config: dict, kpi_data: dict, value: float, target: float, theme: str):
        title = config.get("title", "KPI")
        title_lower = title.lower()
        is_money   = any(w in title_lower for w in ["ingreso", "costo", "gasto", "pago", "saldo", "balance", "$"])
        is_percent = any(w in title_lower for w in ["porcent", "%", "margen", "disponibilidad"])

        if is_money:
            val_str = DrawerDataService.safe_fmt(value, ",.0f", prefix="$")
        elif is_percent:
            val_str = DrawerDataService.safe_fmt(value, ",.1f", suffix="%")
        else:
            val_str = DrawerDataService.safe_fmt(value, ",.0f")

        has_target = target is not None and float(target or 0) > 0
        chat_prompt = f"@{title}: {val_str}"
        if has_target:
            if is_money:
                target_str = DrawerDataService.safe_fmt(target, ",.0f", prefix="$")
            elif is_percent:
                target_str = DrawerDataService.safe_fmt(target, ",.1f", suffix="%")
            else:
                target_str = DrawerDataService.safe_fmt(target, ",.0f")
            try:
                pct = min(value / float(target) * 100, 100)
                chat_prompt += f" | Meta: {target_str} ({pct:.1f}%)"
            except Exception:
                chat_prompt += f" | Meta: {target_str}"
        chat_prompt += "\nAnaliza este KPI: ¿qué factores lo impulsan, qué lo frena, y qué acción recomiendas?"

        # Build export rows for download
        export_rows = [{"Indicador": title, "Valor": val_str}]
        for raw_key, label in [("target", "Meta"), ("vs_last_year_value", "Año Anterior"), ("ytd_value", "Acum. YTD")]:
            raw = kpi_data.get(raw_key)
            if raw is not None and raw != 0:
                try:
                    export_rows.append({"Indicador": label, "Valor": DrawerDataService.safe_fmt(float(raw), ",.2f")})
                except (ValueError, TypeError):
                    pass

        return dmc.Stack(
            gap="md",
            children=[
                dcc.Store(id="drawer-kpi-context-store", data={"prompt": chat_prompt, "title": title, "export_rows": export_rows}),

                # ── Primary: Analizar en chat (full width) ──
                dmc.Button(
                    "Analizar en chat con Zamy",
                    id="drawer-analyze-in-chat-btn",
                    leftSection=DashIconify(icon="tabler:message-chatbot", width=16),
                    variant="gradient",
                    gradient={"from": DS.NEXA_GOLD, "to": DS.NEXA_ORANGE},
                    fullWidth=True,
                    size="md",
                    n_clicks=0,
                ),
                dmc.Text(
                    "Envía el KPI al asistente Zamy y abre el chat.",
                    size="xs", c="dimmed",  # type: ignore
                ),

                dmc.Divider(my="xs"),

                # ── Export: Excel izquierda, Copiar derecha ──
                dmc.Text("Exportar", size="xs", fw=700, c="dimmed", tt="uppercase", mb=4),  # type: ignore
                dmc.Group(
                    justify="space-between",
                    children=[
                        dmc.Button(
                            "Descargar Excel",
                            id="drawer-export-excel-btn",
                            leftSection=DashIconify(icon="tabler:file-spreadsheet", width=16),
                            variant="light",
                            color="green",
                            size="sm",
                            n_clicks=0,
                        ),
                        dmc.Button(
                            "Copiar datos",
                            id="drawer-copy-data-btn",
                            rightSection=DashIconify(icon="tabler:copy", width=16),
                            variant="light",
                            color="blue",
                            size="sm",
                            n_clicks=0,
                        ),
                    ],
                ),
            ],
        )

    # ── KPI insights — deterministic analysis with status badge ────────────────

    @staticmethod
    def _create_kpi_insights_tab(value, delta, delta_pct, target, kpi_data: dict, config: dict, theme: str):
        is_dark = theme == "dark"

        try:
            performance = (value / target * 100) if target and target > 0 else None
        except Exception:
            performance = None

        # ── Status badge: EXCELENTE / BUENO / REGULAR / MALO ──
        if performance is not None:
            if performance >= 95:
                status, status_color, status_icon = "EXCELENTE", "lime", "tabler:circle-check-filled"
            elif performance >= 80:
                status, status_color, status_icon = "BUENO", "green", "tabler:thumb-up"
            elif performance >= 60:
                status, status_color, status_icon = "REGULAR", "yellow", "tabler:alert-triangle"
            else:
                status, status_color, status_icon = "MALO", "red", "tabler:alert-circle"
        else:
            status, status_color, status_icon = "SIN META", "gray", "tabler:minus"

        # ── Build insights from actual data ──
        insights: List[Tuple[str, str, str, str]] = []  # (title, text, type, priority)

        # 1. Performance vs meta
        if performance is not None:
            if performance >= 95:
                insights.append((
                    "Cumplimiento de meta",
                    f"Alcanzas el {performance:.1f}% de la meta. Desempeño sobresaliente. Mantén el ritmo.",
                    "success", "High",
                ))
            elif performance >= 80:
                insights.append((
                    "Cerca de la meta",
                    f"Alcanzas el {performance:.1f}% de la meta. Faltan {DrawerDataService.safe_fmt(target - value, ',.0f')} para llegar al objetivo.",
                    "info", "Medium",
                ))
            elif performance >= 60:
                insights.append((
                    "Por debajo de la meta",
                    f"Estás al {performance:.1f}% de la meta. Se necesita un incremento de {DrawerDataService.safe_fmt(target - value, ',.0f')} para alcanzarla.",
                    "warning", "High",
                ))
            else:
                insights.append((
                    "Lejos de la meta",
                    f"Solo alcanzas el {performance:.1f}% de la meta. Revisar estrategia y factores que frenan el avance.",
                    "danger", "High",
                ))

        # 2. Trend vs last year
        if delta_pct != 0:
            delta_pct_display = delta_pct * 100 if abs(delta_pct) < 10 else delta_pct
            if delta_pct_display > 10:
                insights.append((
                    "Mejora vs año anterior",
                    f"Crecimiento del {delta_pct_display:+.1f}% respecto al año anterior. Tendencia positiva.",
                    "success", "Medium",
                ))
            elif delta_pct_display > 0:
                insights.append((
                    "Ligera mejora vs año anterior",
                    f"Incremento del {delta_pct_display:+.1f}% vs año anterior. Progreso moderado.",
                    "info", "Medium",
                ))
            elif delta_pct_display >= -10:
                insights.append((
                    "Caída leve vs año anterior",
                    f"Descenso del {abs(delta_pct_display):.1f}% vs año anterior. Monitorear la tendencia.",
                    "warning", "Medium",
                ))
            else:
                insights.append((
                    "Caída significativa vs año anterior",
                    f"Descenso del {abs(delta_pct_display):.1f}% comparado con el año anterior. Acción requerida.",
                    "danger", "High",
                ))

        # 3. Value = 0 or very low
        if value == 0:
            insights.append((
                "Valor en cero",
                "El indicador está en cero. Verificar si hay datos cargados o si hubo un problema de captura.",
                "danger", "High",
            ))
        elif performance is not None and performance < 10:
            insights.append((
                "Valor muy bajo",
                "El valor está muy por debajo de la meta. Revisar si los datos son correctos.",
                "warning", "High",
            ))

        # 4. YTD insight
        ytd_delta = kpi_data.get("ytd_delta")
        if ytd_delta is not None:
            ytd_pct = ytd_delta * 100 if abs(float(ytd_delta)) < 10 else float(ytd_delta)
            color = "success" if float(ytd_pct) >= 0 else "warning"
            insights.append((
                "Acumulado YTD vs meta",
                f"El acumulado del año a la fecha varía un {float(ytd_pct):+.1f}% respecto a la meta acumulada.",
                color, "Medium",
            ))

        if not insights:
            insights.append(("Sin datos suficientes", "No hay suficiente información para generar análisis.", "info", "Low"))

        # ── Build stats summary for LLM ──
        kpi_title = config.get("title", "KPI")
        vs_prev_val = kpi_data.get("vs_last_year_value")
        stats_parts = [f"KPI: {kpi_title}", f"Estado: {status}"]
        stats_parts.append(f"Valor actual: {DrawerDataService.safe_fmt(value, ',.2f')}")
        if vs_prev_val is not None and vs_prev_val != 0:
            stats_parts.append(f"Año anterior: {DrawerDataService.safe_fmt(float(vs_prev_val), ',.2f')}")
        if target:
            stats_parts.append(f"Meta: {DrawerDataService.safe_fmt(target, ',.2f')}")
        if performance is not None:
            stats_parts.append(f"Cumplimiento vs meta: {performance:.1f}%")
        if delta_pct != 0:
            delta_pct_display = delta_pct * 100 if abs(delta_pct) < 10 else delta_pct
            stats_parts.append(f"Variación vs año anterior: {delta_pct_display:+.1f}%")
        if delta:
            stats_parts.append(f"Delta absoluto: {DrawerDataService.safe_fmt(delta, ',.2f')}")
        ytd_delta_val = kpi_data.get("ytd_delta")
        if ytd_delta_val is not None:
            try:
                ytd_pct_llm = float(ytd_delta_val) * 100 if abs(float(ytd_delta_val)) < 10 else float(ytd_delta_val)
                stats_parts.append(f"YTD vs meta: {ytd_pct_llm:+.1f}%")
            except Exception:
                pass
        stats_summary = "\n".join(stats_parts)

        insight_section_children = [
            dcc.Store(id="drawer-llm-stats", data={"title": kpi_title, "stats": stats_summary, "theme": theme}),
            dmc.Text("Análisis", size="xs", fw=700, c="dimmed", tt="uppercase"),  # type: ignore
        ]

        # Status badge (only when there's a target to compare against)
        if performance is not None:
            insight_section_children.append(
                dmc.Paper(
                    p="md", radius="md", withBorder=True,
                    style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
                    children=[dmc.Group(justify="space-between", children=[
                        dmc.Group(gap="xs", children=[
                            DashIconify(icon=status_icon, width=16, color=DS.COLOR_MAP.get(status_color, DS.CHART_BLUE)),
                            dmc.Text("Estado vs meta", size="sm", fw=600, c="dimmed"),  # type: ignore
                        ]),
                        dmc.Badge(status, color=status_color, size="lg", variant="filled",
                                  leftSection=DashIconify(icon=status_icon, width=12)),
                    ])],
                )
            )

        # Deterministic insight cards (up to 2 key observations)
        insight_section_children += [
            DrawerDataService._create_insight_card(ttl, txt, itype, is_dark, pri)
            for ttl, txt, itype, pri in insights[:2]
        ]

        # AI analysis on demand
        insight_section_children += [
            dmc.Divider(label="Análisis con Zamy", labelPosition="center", my="xs"),
            dmc.Button(
                "Generar análisis",
                id="drawer-generate-insight-btn",
                leftSection=DashIconify(icon="tabler:brain", width=16),
                variant="gradient",
                gradient={"from": "#667eea", "to": "#764ba2"},
                fullWidth=True,
                size="sm",
                n_clicks=0,
            ),
            html.Div(id="drawer-llm-output"),
        ]

        return dmc.Stack(gap="sm", children=insight_section_children)

    # ── Table helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _load_strategy_dataframe(strategy, ctx) -> pd.DataFrame:
        """Load the strategy data into a DataFrame (handles both new and legacy strategies)."""
        if hasattr(strategy, "_get_data"):
            cols_cfg, rows = strategy._get_data(ctx)
            if rows:
                if cols_cfg and isinstance(cols_cfg[0], str):
                    return pd.DataFrame(rows, columns=cols_cfg)
                df = pd.DataFrame(rows)
                if cols_cfg:
                    rename_map = {c["field"]: c["headerName"] for c in cols_cfg if isinstance(c, dict)}
                    df.rename(columns=rename_map, inplace=True)
                return df
        elif hasattr(strategy, "_resolve_chart_data"):
            screen_id = getattr(strategy, "screen_id", "")
            key = getattr(strategy, "key", "")
            if screen_id and key:
                table_data = strategy._resolve_chart_data(ctx, screen_id, key)
                if table_data:
                    data_source = table_data.get("data", table_data)
                    rows = data_source.get("rows", [])
                    if rows:
                        return pd.DataFrame(rows)
        return pd.DataFrame()

    @staticmethod
    def _create_table_summary_tab(strategy, ctx, theme):
        try:
            df = DrawerDataService._load_strategy_dataframe(strategy, ctx)

            if not df.empty:
                num_cols = df.select_dtypes(include="number").columns.tolist()
                integrity = f"{(1 - df.isnull().mean().mean()) * 100:.0f}%"
                return dmc.Stack(
                    gap="lg",
                    children=[
                        dmc.Text("Resumen de Datos", size="xl", fw=700),  # type: ignore
                        dmc.SimpleGrid(
                            cols=3,
                            spacing="md",
                            children=[
                                DrawerDataService._create_stat_card("Total Registros", f"{len(df):,}", "blue", "tabler:database", theme),
                                DrawerDataService._create_stat_card("Columnas", f"{len(df.columns)}", "green", "tabler:columns", theme),
                                DrawerDataService._create_stat_card("Integridad", integrity, "yellow", "tabler:shield-check", theme),
                            ],
                        ),
                        dmc.Text("Vista previa (Top 10):", size="sm", fw=600, c="dimmed", mt="md"),  # type: ignore
                        DrawerDataService._create_ag_grid(df.head(10), theme, show_totals=True),
                    ],
                )

            return dmc.Alert("No se encontraron datos para generar el resumen.", color="gray")

        except Exception as e:
            return dmc.Alert(f"Error al cargar resumen: {str(e)}", color="red")

    @staticmethod
    def _create_table_breakdown_tab(strategy, ctx, theme):
        """Statistical breakdown: numeric stats + top-N contributors per column.
        Different from tab_datos which shows the raw full grid."""
        is_dark = theme == "dark"
        try:
            df = DrawerDataService._load_strategy_dataframe(strategy, ctx)

            if df.empty:
                return dmc.Alert("No hay datos para analizar.", color="gray")

            num_cols = df.select_dtypes(include="number").columns.tolist()
            non_num_cols = [c for c in df.columns if c not in num_cols]

            children = [dmc.Text("Análisis Estadístico", size="xl", fw=700, mb="xs")]  # type: ignore

            # ── Numeric summary per column ──
            if num_cols:
                children.append(dmc.Text("Columnas numéricas", size="sm", fw=600, c="dimmed", mb="sm"))  # type: ignore
                for col in num_cols[:4]:
                    series = pd.to_numeric(df[col], errors="coerce").dropna()
                    if series.empty:
                        continue
                    total = series.sum()
                    avg   = series.mean()
                    mx    = series.max()
                    mn    = series.min()
                    children.append(
                        dmc.Paper(
                            p="md", radius="md", withBorder=True, mb="sm",
                            style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
                            children=[
                                dmc.Text(col, size="sm", fw=700, mb="xs"),  # type: ignore
                                dmc.SimpleGrid(
                                    cols=4,
                                    spacing="xs",
                                    children=[
                                        DrawerDataService._create_stat_card("Total",   DrawerDataService.safe_fmt(total, ",.0f"), "blue",   "tabler:sigma",      theme),
                                        DrawerDataService._create_stat_card("Promedio",DrawerDataService.safe_fmt(avg,   ",.1f"), "green",  "tabler:chart-line", theme),
                                        DrawerDataService._create_stat_card("Máximo",  DrawerDataService.safe_fmt(mx,    ",.0f"), "yellow", "tabler:arrow-up",   theme),
                                        DrawerDataService._create_stat_card("Mínimo",  DrawerDataService.safe_fmt(mn,    ",.0f"), "red",    "tabler:arrow-down", theme),
                                    ],
                                ),
                            ],
                        )
                    )

            # ── Top-N by first non-numeric label + first numeric value ──
            if non_num_cols and num_cols:
                label_col = non_num_cols[0]
                value_col = num_cols[0]
                try:
                    agg = (
                        df.groupby(label_col)[value_col]
                        .sum()
                        .sort_values(ascending=False)
                        .head(8)
                        .reset_index()
                    )
                    agg.columns = [label_col, value_col]
                    total_sum = agg[value_col].sum()
                    children.append(dmc.Text(f"Top por {label_col}", size="sm", fw=600, c="dimmed", mt="md", mb="sm"))  # type: ignore
                    for _, row in agg.iterrows():
                        pct = row[value_col] / total_sum * 100 if total_sum > 0 else 0
                        children.append(
                            dmc.Paper(
                                p="sm", radius="md", withBorder=True, mb="xs",
                                style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
                                children=[
                                    dmc.Group(
                                        justify="space-between",
                                        children=[
                                            dmc.Text(str(row[label_col])[:40], size="sm", fw=600),  # type: ignore
                                            dmc.Group(gap="xs", children=[
                                                dmc.Text(DrawerDataService.safe_fmt(row[value_col], ",.0f"), size="sm", fw=700),  # type: ignore
                                                dmc.Badge(f"{pct:.1f}%", size="sm", variant="light", color="blue"),
                                            ]),
                                        ],
                                    ),
                                    dmc.Progress(value=min(pct, 100), size="xs", color="blue", mt=4),
                                ],
                            )
                        )
                except Exception:
                    pass

            # If nothing was added beyond the header, there are no numeric columns to analyze
            if len(children) <= 1:
                return dmc.Alert(
                    "No hay columnas numéricas disponibles para el análisis estadístico.",
                    color="gray",
                    icon=DashIconify(icon="tabler:chart-off"),
                )

            return dmc.Stack(gap="xs", children=children)

        except Exception as e:
            return dmc.Alert(f"Error en análisis de desglose: {str(e)}", color="red")

    @staticmethod
    def _create_table_insights_tab(strategy, ctx, theme):
        is_dark = theme == "dark"
        df = pd.DataFrame()
        table_title = (getattr(strategy, "key", None) or getattr(strategy, "__class__", None) and strategy.__class__.__name__ or "Tabla")
        try:
            df = DrawerDataService._load_strategy_dataframe(strategy, ctx)
            insights = DrawerDataService._analyze_dataframe_insights(df) if not df.empty else [
                ("Sin datos", "No se encontraron datos para analizar.", "warning", "Low")
            ]
        except Exception as e:
            insights = [("Error de análisis", str(e), "danger", "Low")]

        # ── Build stats text for LLM ──
        stats_parts: List[str] = [f"Tabla: {table_title}"]
        if not df.empty:
            stats_parts.append(f"Registros: {len(df):,} | Columnas: {len(df.columns)}")
            num_cols = df.select_dtypes(include="number").columns.tolist()
            for col in num_cols[:3]:
                series = pd.to_numeric(df[col], errors="coerce").dropna()
                if not series.empty:
                    stats_parts.append(
                        f"{col}: total={series.sum():,.0f}, promedio={series.mean():,.1f}, "
                        f"max={series.max():,.0f}, min={series.min():,.0f}"
                    )
            null_pct = df.isnull().mean().mean() * 100
            if null_pct > 0:
                stats_parts.append(f"Datos nulos: {null_pct:.1f}%")
        for t, tx, _, _ in insights:
            stats_parts.append(f"• {t}: {tx}")
        stats_text = "\n".join(stats_parts)

        # ── Quick numeric summary rows for data-first display ──
        summary_rows: List[Tuple[str, str, str, str]] = []
        if not df.empty:
            num_cols_t = df.select_dtypes(include="number").columns.tolist()
            summary_rows.append(("Total registros", f"{len(df):,}", "blue", "tabler:database"))
            summary_rows.append(("Columnas", f"{len(df.columns)}", "gray", "tabler:columns"))
            for col in num_cols_t[:2]:
                series_t = pd.to_numeric(df[col], errors="coerce").dropna()
                if not series_t.empty:
                    summary_rows.append((f"{col} (total)", DrawerDataService.safe_fmt(series_t.sum(), ",.0f"), "indigo", "tabler:sigma"))
                    summary_rows.append((f"{col} (prom.)", DrawerDataService.safe_fmt(series_t.mean(), ",.1f"), "green", "tabler:chart-line"))

        return dmc.Stack(
            gap="sm",
            children=[
                dcc.Store(id="drawer-llm-stats", data={"title": table_title, "stats": stats_text, "theme": theme}),
                # 1. Data summary first
                dmc.Text("Resumen de datos", size="xs", fw=700, c="dimmed", tt="uppercase", mb=4),  # type: ignore
                *[
                    dmc.Paper(
                        p="md", radius="md", withBorder=True,
                        style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
                        children=[dmc.Group(justify="space-between", children=[
                            dmc.Group(gap="xs", children=[
                                DashIconify(icon=icon, width=14, color=DS.COLOR_MAP.get(color, DS.CHART_BLUE)),
                                dmc.Text(label, size="sm", fw=600, c="dimmed"),  # type: ignore
                            ]),
                            dmc.Text(val_str, size="md", fw=700),  # type: ignore
                        ])],
                    )
                    for label, val_str, color, icon in summary_rows
                ],
                # 2. Deterministic insight cards from data
                *[DrawerDataService._create_insight_card(t, tx, c, is_dark, p) for t, tx, c, p in insights[:3]],
                # 3. AI analysis on demand
                dmc.Divider(label="Análisis con Zamy", labelPosition="center", my="xs"),
                dmc.Button(
                    "Generar análisis",
                    id="drawer-generate-insight-btn",
                    leftSection=DashIconify(icon="tabler:brain", width=16),
                    variant="gradient",
                    gradient={"from": "#667eea", "to": "#764ba2"},
                    fullWidth=True,
                    size="sm",
                    n_clicks=0,
                ),
                html.Div(id="drawer-llm-output"),
            ],
        )

    # ── Chart helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _safe_floats(iterable) -> List[float]:
        """Convert an iterable to floats, silently skipping non-numeric values."""
        result = []
        for v in (iterable or []):
            if v is None:
                continue
            try:
                result.append(float(v))
            except (ValueError, TypeError):
                pass
        return result

    @staticmethod
    def _extract_trace_values(trace) -> List[float]:
        """Return the numeric values from a Plotly trace regardless of orientation or type."""
        sf = DrawerDataService._safe_floats
        # Pie / donut
        if hasattr(trace, "values") and trace.values is not None:
            vals = sf(trace.values)
            if vals:
                return vals
        # Horizontal bar: orientation='h' → x has the numbers, y has the labels
        if getattr(trace, "orientation", None) == "h":
            if hasattr(trace, "x") and trace.x is not None:
                vals = sf(trace.x)
                if vals:
                    return vals
        # Vertical bar, line, scatter: y has the numbers
        if hasattr(trace, "y") and trace.y is not None:
            vals = sf(trace.y)
            if vals:
                return vals
        # Fallback: try x
        if hasattr(trace, "x") and trace.x is not None:
            vals = sf(trace.x)
            if vals:
                return vals
        return []

    @staticmethod
    def _extract_trace_values_raw(trace) -> List:
        """Return values preserving None (no filtering), maintaining original length.
        Used for aligned multi-trace tables so partial current-year data stays aligned."""
        if hasattr(trace, "values") and trace.values is not None:
            return list(trace.values)
        if getattr(trace, "orientation", None) == "h":
            if hasattr(trace, "x") and trace.x is not None:
                return list(trace.x)
        if hasattr(trace, "y") and trace.y is not None:
            return list(trace.y)
        if hasattr(trace, "x") and trace.x is not None:
            return list(trace.x)
        return []

    @staticmethod
    def _extract_trace_labels(trace) -> List[str]:
        """Return the category/label axis from a Plotly trace."""
        # Horizontal bar: y = labels
        if getattr(trace, "orientation", None) == "h":
            if hasattr(trace, "y") and trace.y is not None:
                return [str(v) for v in trace.y if v is not None]
        # Pie
        if hasattr(trace, "labels") and trace.labels is not None:
            return [str(v) for v in trace.labels if v is not None]
        # Vertical bar / line: x = labels
        if hasattr(trace, "x") and trace.x is not None:
            return [str(v) for v in trace.x if v is not None]
        return []

    @staticmethod
    def _create_chart_breakdown_tab(fig, theme):
        """Desglose tab: stats cards + per-period data table with % contribution."""
        is_dark = theme == "dark"
        if not fig or not hasattr(fig, "data") or len(fig.data) == 0:
            return dmc.Alert("No hay datos", color="gray")

        children: List[Any] = [dmc.Text("Desglose por período", size="xl", fw=700, mb="sm")]  # type: ignore

        try:
            trace = fig.data[0]
            values = DrawerDataService._extract_trace_values(trace)
            labels = DrawerDataService._extract_trace_labels(trace)

            if not values:
                return dmc.Alert("No se pudieron calcular estadísticas", color="gray")

            series = pd.Series(values)
            total  = series.sum()
            avg    = series.mean()
            mx     = series.max()
            mn     = series.min()
            std    = series.std()
            cv     = (std / avg * 100) if avg != 0 else 0

            children.append(
                dmc.SimpleGrid(
                    cols=4,
                    spacing="md",
                    mb="lg",
                    children=[
                        DrawerDataService._create_stat_card("Total",      DrawerDataService.safe_fmt(total, ",.0f"), "blue",   "tabler:sigma",      theme),
                        DrawerDataService._create_stat_card("Promedio",   DrawerDataService.safe_fmt(avg,   ",.1f"), "green",  "tabler:chart-line", theme),
                        DrawerDataService._create_stat_card("Máximo",     DrawerDataService.safe_fmt(mx,    ",.0f"), "yellow", "tabler:arrow-up",   theme),
                        DrawerDataService._create_stat_card("Mínimo",     DrawerDataService.safe_fmt(mn,    ",.0f"), "red",    "tabler:arrow-down", theme),
                    ],
                )
            )

            # Per-period contribution table
            if labels and len(labels) == len(values):
                children.append(dmc.Text("Contribución por período", size="sm", fw=600, c="dimmed", mb="xs"))  # type: ignore
                sorted_pairs = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
                for lbl, val in sorted_pairs:
                    pct = (val / total * 100) if total > 0 else 0
                    diff_avg = val - avg
                    diff_color = "green" if diff_avg >= 0 else "red"
                    children.append(
                        dmc.Paper(
                            p="sm", radius="md", withBorder=True, mb="xs",
                            style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
                            children=[
                                dmc.Group(
                                    justify="space-between",
                                    children=[
                                        dmc.Text(str(lbl)[:36], size="sm", fw=600),  # type: ignore
                                        dmc.Group(gap="xs", children=[
                                            dmc.Text(DrawerDataService.safe_fmt(val, ",.0f"), size="sm", fw=700),  # type: ignore
                                            dmc.Badge(f"{pct:.1f}%", size="sm", variant="light", color="blue"),
                                            dmc.Badge(
                                                f"{diff_avg:+,.0f} vs avg",
                                                size="sm", variant="light",
                                                color=diff_color,
                                            ),
                                        ]),
                                    ],
                                ),
                                dmc.Progress(value=min(pct, 100), size="xs", color="blue", mt=4, animated=False),
                            ],
                        )
                    )
        except Exception as e:
            children.append(dmc.Alert(f"Error en desglose: {str(e)}", color="red"))

        return dmc.Stack(gap="xs", children=children)

    @staticmethod
    def _create_chart_insights_tab(fig, theme):
        """Insights tab: pandas stats + LLM natural-language analysis."""
        is_dark = theme == "dark"
        stats_lines: List[str] = []
        insight_cards: list = []

        if fig and hasattr(fig, "data") and fig.data:
            for trace in fig.data[:2]:
                values = DrawerDataService._extract_trace_values(trace)
                if len(values) < 2:
                    continue

                trace_name = (getattr(trace, "name", None) or "Serie").strip() or "Serie"
                series = pd.Series(values)
                avg  = series.mean()
                std  = series.std()
                mx   = series.max()
                mn   = series.min()
                cv   = (std / avg * 100) if avg != 0 else 0
                total = series.sum()

                first_nonzero = next((v for v in values if v != 0), None)
                last_val = values[-1]
                pct_change = ((last_val - first_nonzero) / first_nonzero * 100) if first_nonzero else 0

                drops = [
                    (i, (values[i] - values[i - 1]) / values[i - 1] * 100)
                    for i in range(1, len(values))
                    if values[i - 1] != 0 and (values[i] - values[i - 1]) / values[i - 1] < -0.20
                ]
                zeros = sum(1 for v in values if v == 0)

                stats_lines += [
                    f"Serie: {trace_name}",
                    f"  Total: {total:,.0f} | Promedio: {avg:,.1f}",
                    f"  Máximo: {mx:,.0f} | Mínimo: {mn:,.0f}",
                    f"  Variación período completo: {pct_change:+.1f}%",
                    f"  CV (variabilidad): {cv:.0f}%",
                    f"  Caídas bruscas (>20%): {len(drops)}",
                    f"  Períodos en cero: {zeros}",
                ]

        stats_summary = "\n".join(stats_lines) if stats_lines else "Sin datos numéricos disponibles."
        title = (getattr(fig, "layout", None) and getattr(fig.layout, "title", None) and
                 getattr(fig.layout.title, "text", None)) or "Gráfica"

        return dmc.Stack(
            gap="sm",
            children=[
                dcc.Store(id="drawer-llm-stats", data={"title": title, "stats": stats_summary, "theme": theme}),
                # 1. Calculated stats — data first
                dmc.Paper(
                    p="md",
                    radius="md",
                    withBorder=True,
                    style={"backgroundColor": DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY},
                    children=[
                        dmc.Text("Estadísticas de la serie", size="xs", fw=700, c="dimmed", tt="uppercase", mb="xs"),  # type: ignore
                        dmc.Code(stats_summary, block=True, style={"fontSize": "11px", "backgroundColor": "transparent"}),
                    ],
                ) if stats_lines else dmc.Alert("Sin datos numéricos disponibles.", color="gray"),
                # 2. AI analysis on demand
                dmc.Divider(label="Análisis con Zamy", labelPosition="center", my="xs"),
                dmc.Button(
                    "Generar análisis",
                    id="drawer-generate-insight-btn",
                    leftSection=DashIconify(icon="tabler:brain", width=16),
                    variant="gradient",
                    gradient={"from": "#667eea", "to": "#764ba2"},
                    fullWidth=True,
                    size="sm",
                    n_clicks=0,
                ),
                html.Div(id="drawer-llm-output"),
            ],
        )

    # ── Shared helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _analyze_dataframe_insights(df: pd.DataFrame) -> List[Tuple[str, str, str, str]]:
        """Generate data-driven insights from a DataFrame using pandas."""
        insights: List[Tuple[str, str, str, str]] = []
        n_rows = len(df)

        # Null analysis
        null_pct = df.isnull().mean().mean() * 100
        if null_pct > 10:
            cols_with_nulls = df.columns[df.isnull().any()].tolist()
            insights.append((
                "Datos incompletos",
                f"{null_pct:.1f}% de celdas nulas. Columnas afectadas: {', '.join(cols_with_nulls[:3])}.",
                "warning", "High",
            ))

        num_cols = df.select_dtypes(include="number").columns.tolist()

        for col in num_cols[:3]:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) < 2:
                continue
            avg = series.mean()
            std = series.std()
            total = series.sum()
            mx  = series.max()
            mn  = series.min()
            cv  = (std / avg * 100) if avg != 0 else 0

            # Concentration: top contributor
            top_pct = (mx / total * 100) if total > 0 else 0
            if top_pct > 40:
                insights.append((
                    f"Concentración en {col}",
                    f"El valor máximo representa el {top_pct:.1f}% del total. Alta concentración en un solo registro.",
                    "warning", "High",
                ))

            # High variability
            if cv > 60:
                insights.append((
                    f"Alta variabilidad en {col}",
                    f"CV={cv:.0f}%. Datos muy dispersos. Rango: {DrawerDataService.safe_fmt(mn, ',.0f')} – {DrawerDataService.safe_fmt(mx, ',.0f')}.",
                    "warning", "Medium",
                ))
            elif cv < 10 and len(series) > 3:
                insights.append((
                    f"{col} estable",
                    f"Variabilidad baja (CV={cv:.1f}%). Los valores son consistentes con promedio {DrawerDataService.safe_fmt(avg, ',.1f')}.",
                    "success", "Low",
                ))

        if not insights:
            insights.append((
                "Datos en buen estado",
                f"La tabla tiene {n_rows:,} registros sin anomalías detectadas.",
                "success", "Low",
            ))

        return insights[:4]

    @staticmethod
    def _fig_to_dataframe(fig) -> "pd.DataFrame":
        """Convert Plotly figure traces into a DataFrame for statistical analysis.
        Skips projection traces (name contains 'proy'). Returns empty DF on failure."""
        try:
            shared_labels: List[str] = []
            for trace in fig.data:
                lbl = DrawerDataService._extract_trace_labels(trace)
                if len(lbl) > len(shared_labels):
                    shared_labels = lbl

            if not shared_labels:
                return pd.DataFrame()

            n = len(shared_labels)
            data: Dict[str, Any] = {}
            for i, trace in enumerate(fig.data):
                col_name = (getattr(trace, "name", None) or "").strip() or f"Serie {i + 1}"
                if "proy" in col_name.lower():
                    continue
                vals: List = DrawerDataService._extract_trace_values_raw(trace)
                if vals:
                    if len(vals) < n:
                        vals = list(vals) + [None] * (n - len(vals))
                    elif len(vals) > n:
                        vals = list(vals)[:n]
                    data[col_name] = vals

            if not data:
                return pd.DataFrame()

            df = pd.DataFrame(data)
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            return df
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def _run_statistical_engine(
        df: "pd.DataFrame",
        label_cols: Optional[List[str]] = None,
    ) -> dict:
        """Lightweight statistical engine. Returns structured dict with 5 sections.
        label_cols: column names that are labels/dimensions (never coerced to numeric).
        Designed for speed — no heavy profiling, no blocking."""
        if df is None or df.empty:
            return {}

        df = df.copy()
        _label_set: set = set(label_cols or [])
        for col in df.select_dtypes(include="object").columns:
            if col in _label_set:
                continue
            coerced = pd.to_numeric(
                df[col].astype(str)
                    .str.replace(r"[$,%\s]", "", regex=True)
                    .str.replace(",", "", regex=False)
                    .str.replace("(", "-", regex=False)
                    .str.replace(")", "",  regex=False),
                errors="coerce",
            )
            if coerced.notna().mean() > 0.5:
                is_all_int = (coerced.dropna() % 1 == 0).all()
                if is_all_int:
                    n_valid = max(len(coerced.dropna()), 1)
                    if coerced.dropna().nunique() / n_valid > 0.3:
                        continue
                df[col] = coerced

        num_cols = df.select_dtypes(include="number").columns.tolist()
        n_rows, n_cols = df.shape
        null_pct = df.isnull().mean().mean() * 100
        general = {
            "records": n_rows,
            "columns": n_cols,
            "numeric_cols": len(num_cols),
            "missing_pct": round(null_pct, 1),
        }
        numeric_summary: Dict[str, dict] = {}
        for col in num_cols:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if series.empty:
                continue
            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            missing_count = int(df[col].isnull().sum())
            numeric_summary[col] = {
                "mean":        round(float(series.mean()), 2),
                "median":      round(float(series.median()), 2),
                "std":         round(float(series.std()), 2),
                "min":         round(float(series.min()), 2),
                "max":         round(float(series.max()), 2),
                "q1":          round(q1, 2),
                "q3":          round(q3, 2),
                "count":       int(len(series)),
                "missing":     missing_count,
                "missing_pct": round(missing_count / n_rows * 100, 1),
            }
        correlations: List[dict] = []
        if len(num_cols) >= 2:
            try:
                corr_df = df[num_cols].apply(pd.to_numeric, errors="coerce").corr()
                for i, col_a in enumerate(num_cols):
                    for col_b in num_cols[i + 1:]:
                        r = corr_df.loc[col_a, col_b]
                        if not pd.isna(r):
                            val = float(r)  # type: ignore
                            if abs(val) >= 0.7:
                                correlations.append({
                                    "col_a": col_a,
                                    "col_b": col_b,
                                    "r":     round(val, 3),
                                })
                correlations.sort(key=lambda x: abs(x["r"]), reverse=True)
            except Exception:
                pass
        outliers: Dict[str, dict] = {}
        for col in num_cols:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) < 4:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            count = int(((series < lower) | (series > upper)).sum())
            if count > 0:
                outliers[col] = {
                    "count":       count,
                    "pct":         round(count / len(series) * 100, 1),
                    "lower_bound": round(float(lower), 2),
                    "upper_bound": round(float(upper), 2),
                }

        rankings: Dict[str, dict] = {}
        label_col = next(
            (c for c in df.columns if c not in num_cols and df[c].dtype == object),
            None
        )
        if label_col and num_cols:
            for metric_col in num_cols[:4]: 
                series = pd.to_numeric(df[metric_col], errors="coerce")
                merged = pd.DataFrame({"label": df[label_col].astype(str), "value": series}).dropna()
                if len(merged) < 2:
                    continue
                merged_zero    = merged[merged["value"] == 0]
                merged_nonzero = merged[merged["value"] != 0]
                n_zeros = len(merged_zero)
                zero_labels = merged_zero["label"].astype(str).tolist()
                working = merged_nonzero if len(merged_nonzero) >= 2 else merged
                top_rows    = working.nlargest(3, "value")[["label", "value"]].values.tolist()
                bottom_rows = working.nsmallest(3, "value")[["label", "value"]].values.tolist()
                avg = float(working["value"].mean())
                rankings[metric_col] = {
                    "label_col":   label_col,
                    "top":         [[str(r[0]), round(float(r[1]), 2)] for r in top_rows],
                    "bottom":      [[str(r[0]), round(float(r[1]), 2)] for r in bottom_rows],
                    "avg":         round(avg, 2),
                    "n_zeros":     n_zeros,
                    "n_total":     len(merged),
                    "zero_labels": zero_labels[:6],
                }

        return {
            "general":         general,
            "numeric_summary": numeric_summary,
            "correlations":    correlations,
            "outliers":        outliers,
            "rankings":        rankings,
        }

    @staticmethod
    def _render_estadisticas_tab(engine_result: dict, theme: str):
        is_dark = theme == "dark"
        bg_sec = DS.NEXA_BG_DARK_SECONDARY if is_dark else DS.NEXA_BG_LIGHT_SECONDARY
        sh = DrawerDataService._section_header

        if not engine_result:
            return dmc.Alert(
                "No hay datos numéricos suficientes para generar el análisis estadístico.",
                color="gray",
                icon=DashIconify(icon="tabler:chart-off"),
            )

        general         = engine_result.get("general", {})
        numeric_summary = engine_result.get("numeric_summary", {})
        correlations    = engine_result.get("correlations", [])
        outliers        = engine_result.get("outliers", {})
        rankings        = engine_result.get("rankings", {})

        sections: List[Any] = []
        sections.append(sh("Resumen del dataset", "tabler:database"))
        sections.append(
            dmc.SimpleGrid(
                cols=4,
                spacing="sm",
                children=[
                    DrawerDataService._create_stat_card(
                        "Registros",          f"{general.get('records', 0):,}",          "blue",   "tabler:database",    theme),
                    DrawerDataService._create_stat_card(
                        "Columnas",           f"{general.get('columns', 0)}",             "green",  "tabler:columns",     theme),
                    DrawerDataService._create_stat_card(
                        "Vars. numéricas",    f"{general.get('numeric_cols', 0)}",        "yellow", "tabler:math",        theme),
                    DrawerDataService._create_stat_card(
                        "% Datos faltantes",  f"{general.get('missing_pct', 0):.1f}%",   "red" if general.get("missing_pct", 0) > 10 else "gray",
                        "tabler:alert-triangle" if general.get("missing_pct", 0) > 10 else "tabler:check", theme),
                ],
            )
        )

        if rankings:
            sections.append(sh("Ranking de eficiencia", "tabler:trophy"))
            for metric_col, info in list(rankings.items())[:3]:
                avg = info.get("avg", 0)
                top    = info.get("top", [])
                bottom = info.get("bottom", [])

                medal_colors = ["gold", "silver", "#cd7f32"] 
                medal_icons  = ["tabler:medal", "tabler:medal-2", "tabler:medal-3"]

                top_cards: List[Any] = []
                for rank_i, (label, val) in enumerate(top):
                    pct_above = ((val - avg) / avg * 100) if avg else 0
                    top_cards.append(
                        dmc.Paper(
                            p="sm", radius="md", withBorder=True,
                            style={
                                "backgroundColor": bg_sec,
                                "borderLeft": f"4px solid {medal_colors[rank_i % 3]}",
                            },
                            children=dmc.Group(justify="space-between", children=[
                                dmc.Group(gap="xs", children=[
                                    DashIconify(icon=medal_icons[rank_i % 3], width=16,
                                                color=medal_colors[rank_i % 3]),
                                    dmc.Text(label, size="sm", fw=600),  # type: ignore
                                ]),
                                dmc.Group(gap="xs", children=[
                                    dmc.Text(DrawerDataService.safe_fmt(val, ",.2f"), size="sm", fw=700),  # type: ignore
                                    dmc.Badge(
                                        f"+{pct_above:.0f}% vs prom." if pct_above >= 0 else f"{pct_above:.0f}% vs prom.",
                                        size="xs", variant="light",
                                        color="green" if pct_above >= 0 else "red",
                                    ),
                                ]),
                            ]),
                        )
                    )

                bottom_cards: List[Any] = []
                for label, val in bottom:
                    pct_below = ((val - avg) / avg * 100) if avg else 0
                    bottom_cards.append(
                        dmc.Paper(
                            p="sm", radius="md", withBorder=True,
                            style={
                                "backgroundColor": bg_sec,
                                "borderLeft": f"4px solid {DS.COLOR_MAP.get('red', '#ef4444')}",
                            },
                            children=dmc.Group(justify="space-between", children=[
                                dmc.Group(gap="xs", children=[
                                    DashIconify(icon="tabler:trending-down", width=16,
                                                color=DS.COLOR_MAP.get("red", "#ef4444")),
                                    dmc.Text(label, size="sm", fw=600),  # type: ignore
                                ]),
                                dmc.Group(gap="xs", children=[
                                    dmc.Text(DrawerDataService.safe_fmt(val, ",.2f"), size="sm", fw=700),  # type: ignore
                                    dmc.Badge(
                                        f"{pct_below:.0f}% vs prom." if pct_below < 0 else f"+{pct_below:.0f}% vs prom.",
                                        size="xs", variant="light",
                                        color="red" if pct_below < 0 else "green",
                                    ),
                                ]),
                            ]),
                        )
                    )

                n_zeros     = info.get("n_zeros", 0)
                n_total     = info.get("n_total", 0)
                zero_labels = info.get("zero_labels", [])
                zero_note   = (
                    f"  ·  {n_zeros} de {n_total} con valor cero"
                    if n_zeros > 0 else ""
                )
                zero_cards: List[Any] = []
                for zlabel in zero_labels:
                    zero_cards.append(
                        dmc.Paper(
                            p="xs", radius="md", withBorder=True,
                            style={
                                "backgroundColor": bg_sec,
                                "borderLeft": "3px solid #9ca3af",
                                "opacity": "0.8",
                            },
                            children=dmc.Group(justify="space-between", children=[
                                dmc.Group(gap="xs", children=[
                                    DashIconify(icon="tabler:circle-off", width=14, color="#9ca3af"),
                                    dmc.Text(str(zlabel), size="xs", fw=600),  # type: ignore
                                ]),
                                dmc.Badge("Valor cero", size="xs", variant="outline", color="gray"),
                            ]),
                        )
                    )
                zero_accordion = None
                if zero_cards:
                    zero_accordion = dmc.Accordion(
                        variant="contained",
                        radius="md",
                        style={"marginTop": "4px"},
                        children=[
                            dmc.AccordionItem(
                                value=f"zeros_{metric_col}",
                                children=[
                                    dmc.AccordionControl(
                                        dmc.Group(gap="xs", children=[
                                            DashIconify(icon="tabler:circle-off", width=14, color="#9ca3af"),
                                            dmc.Text(
                                                f"{n_zeros} registro(s) con valor cero — ver detalle",
                                                size="xs", c=_dmc("dimmed"),
                                            ),
                                        ]),
                                    ),
                                    dmc.AccordionPanel(
                                        dmc.Stack(gap="xs", children=zero_cards)
                                    ),
                                ],
                            )
                        ],
                    )

                sections.append(
                    dmc.Stack(
                        gap="xs",
                        children=[
                            dmc.Text(
                                f"Métrica: {metric_col}  ·  Promedio (sin ceros): {DrawerDataService.safe_fmt(avg, ',.2f')}{zero_note}",
                                size="xs", fw=_dmc(600), c=_dmc("dimmed"),
                            ),
                            dmc.SimpleGrid(
                                cols=2, spacing="sm",
                                children=[
                                    dmc.Stack(gap="xs", children=[
                                        dmc.Text("✅ Más eficientes", size="xs", fw=_dmc(700), c=_dmc("green")),
                                        *top_cards,
                                    ]),
                                    dmc.Stack(gap="xs", children=[
                                        dmc.Text("⚠️ Menos eficientes", size="xs", fw=_dmc(700), c=_dmc("red")),
                                        *bottom_cards,
                                    ]),
                                ],
                            ),
                            *([zero_accordion] if zero_accordion else []),
                        ],
                    )
                )
        if numeric_summary:
            sections.append(sh("Estadísticas descriptivas", "tabler:table-options"))

            stat_rows = []
            for col, stats in numeric_summary.items():
                stat_rows.append({
                    "Variable":  col,
                    "Media":     DrawerDataService.safe_fmt(stats["mean"],   ",.2f"),
                    "Mediana":   DrawerDataService.safe_fmt(stats["median"], ",.2f"),
                    "Desv. Std": DrawerDataService.safe_fmt(stats["std"],    ",.2f"),
                    "Mín":       DrawerDataService.safe_fmt(stats["min"],    ",.2f"),
                    "Máx":       DrawerDataService.safe_fmt(stats["max"],    ",.2f"),
                    "Q1":        DrawerDataService.safe_fmt(stats["q1"],     ",.2f"),
                    "Q3":        DrawerDataService.safe_fmt(stats["q3"],     ",.2f"),
                    "Conteo":    f"{stats['count']:,}",
                    "% Nulos":   f"{stats['missing_pct']:.1f}%",
                })

            stats_df = pd.DataFrame(stat_rows)
            sections.append(DrawerDataService._create_ag_grid(stats_df, theme))

        sections.append(sh("Correlaciones fuertes (|r| ≥ 0.70)", "tabler:arrows-exchange"))
        if correlations:
            corr_children: List[Any] = []
            for c in correlations[:6]:
                r = c["r"]
                abs_r = abs(r)
                if abs_r >= 0.9:
                    color, label = "lime",   "Muy fuerte"
                elif abs_r >= 0.8:
                    color, label = "green",  "Fuerte"
                else:
                    color, label = "yellow", "Moderada"
                direction = "positiva" if r > 0 else "negativa"
                corr_children.append(
                    dmc.Paper(
                        p="sm", radius="md", withBorder=True,
                        style={"backgroundColor": bg_sec},
                        children=[
                            dmc.Group(
                                justify="space-between",
                                children=[
                                    dmc.Group(gap="xs", children=[
                                        DashIconify(icon="tabler:arrows-exchange", width=14,
                                                    color=DS.COLOR_MAP.get(color, DS.CHART_BLUE)),
                                        dmc.Text(  # type: ignore
                                            f"{c['col_a']} ↔ {c['col_b']}",
                                            size="sm", fw=600, # type: ignore
                                        ),
                                    ]),
                                    dmc.Group(gap="xs", children=[
                                        dmc.Badge(f"r = {r:+.3f}", size="sm", variant="light",
                                                  color="blue"),
                                        dmc.Badge(f"{label} {direction}", size="sm",
                                                  variant="filled", color=color),
                                    ]),
                                ],
                            ),
                            dmc.Progress(
                                value=abs_r * 100, size="xs", color=color, mt=4, animated=False
                            ),
                        ],
                    )
                )
            sections.append(dmc.Stack(gap="xs", children=corr_children))
        else:
            sections.append(
                dmc.Alert(
                    "No se detectaron correlaciones fuertes entre variables numéricas (umbral |r| ≥ 0.70).",
                    color="gray",
                    icon=DashIconify(icon="tabler:chart-dots"),
                )
            )
        sections.append(sh("Valores extremos (método IQR)", "tabler:alert-triangle"))
        if outliers:
            outlier_children: List[Any] = []
            for col, info in outliers.items():
                severity_color = "red" if info["pct"] > 10 else "orange" if info["pct"] > 5 else "yellow"
                outlier_children.append(
                    dmc.Paper(
                        p="sm", radius="md", withBorder=True,
                        style={
                            "backgroundColor": bg_sec,
                            "borderLeft": f"4px solid {DS.COLOR_MAP.get(severity_color, DS.WARNING[5])}",
                        },
                        children=[
                            dmc.Group(
                                justify="space-between",
                                children=[
                                    dmc.Group(gap="xs", children=[
                                        DashIconify(icon="tabler:alert-triangle", width=14,
                                                    color=DS.COLOR_MAP.get(severity_color, DS.WARNING[5])),
                                        dmc.Text(col, size="sm", fw=600),  # type: ignore
                                    ]),
                                    dmc.Group(gap="xs", children=[
                                        dmc.Badge(f"{info['count']} outliers", size="sm",
                                                  variant="filled", color=severity_color),
                                        dmc.Badge(f"{info['pct']:.1f}%", size="sm",
                                                  variant="light", color=severity_color),
                                    ]),
                                ],
                            ),
                            dmc.Text(  # type: ignore
                                f"Rango esperado: [{DrawerDataService.safe_fmt(info['lower_bound'], ',.2f')} – "
                                f"{DrawerDataService.safe_fmt(info['upper_bound'], ',.2f')}]",
                                size="xs", c="dimmed", mt=4, # type: ignore
                            ),
                        ],
                    )
                )
            sections.append(dmc.Stack(gap="xs", children=outlier_children))
        else:
            sections.append(
                dmc.Alert(
                    "No se detectaron valores extremos (outliers) en las variables numéricas.",
                    color="green",
                    icon=DashIconify(icon="tabler:circle-check"),
                )
            )

        stats_lines: List[str] = []
        if general:
            stats_lines.append(
                f"Dataset: {general.get('records', 0)} registros, "
                f"{general.get('numeric_cols', 0)} variables numéricas, "
                f"{general.get('missing_pct', 0):.1f}% nulos."
            )
        if numeric_summary:
            for col, s in list(numeric_summary.items())[:5]:
                stats_lines.append(
                    f"{col}: media={s['mean']:.2f}, mediana={s['median']:.2f}, "
                    f"std={s['std']:.2f}, min={s['min']:.2f}, max={s['max']:.2f}"
                )
        if correlations:
            for c in correlations[:3]:
                stats_lines.append(f"Correlación {c['col_a']} ↔ {c['col_b']}: r={c['r']:+.3f}")
        if outliers:
            for col, info in list(outliers.items())[:3]:
                stats_lines.append(f"Outliers en {col}: {info['count']} ({info['pct']:.1f}%)")
        stats_text = "\n".join(stats_lines) if stats_lines else "Sin estadísticas calculadas."

        sections.append(dmc.Divider(label="Análisis con Zamy", labelPosition="center", my="xs"))
        sections.append(dcc.Store(
            id="drawer-stats-llm-stats",
            data={"title": "Análisis estadístico del dataset", "stats": stats_text, "theme": theme},
        ))
        sections.append(dmc.Button(
            "Analizar estadísticas con Zamy",
            id="drawer-stats-insight-btn",
            leftSection=DashIconify(icon="tabler:brain", width=16),
            variant="gradient",
            gradient={"from": "#667eea", "to": "#764ba2"},
            fullWidth=True,
            size="sm",
            n_clicks=0,
        ))
        sections.append(html.Div(id="drawer-stats-llm-output"))

        return dmc.Stack(gap="xs", children=sections)

    @staticmethod
    def _create_estadisticas_placeholder():
        """Kept for backward compat — delegates to empty engine render."""
        return DrawerDataService._render_estadisticas_tab({}, "dark")

    @staticmethod
    def _create_actions_tab():
        """Kept for backward compatibility — delegates to generic version."""
        return DrawerDataService._create_generic_actions_tab()

    @staticmethod
    def _create_generic_actions_tab(title: str = "", chat_prompt: str = "", export_rows: Optional[List[Dict]] = None):
        """
        Tab de acciones reutilizable para gráficas, tablas y cualquier widget.
        Expone los mismos botones que el drawer KPI:
          - Analizar en chat (drawer-analyze-in-chat-btn / drawer-kpi-context-store)
          - Descargar Excel (drawer-export-excel-btn)
          - Copiar datos (drawer-copy-data-btn)
        Los callbacks en app.py ya escuchan esos IDs con suppress_callback_exceptions=True.
        """
        if not chat_prompt:
            chat_prompt = f"Analiza el widget '{title}': describe los datos más relevantes, tendencias y posibles acciones." if title else "Analiza los datos de este widget."

        store_data = {
            "prompt": chat_prompt,
            "title": title or "Widget",
            "export_rows": export_rows or [],
        }

        return dmc.Stack(
            gap="md",
            children=[
                dcc.Store(id="drawer-kpi-context-store", data=store_data),

                # ── Analizar en chat ──
                dmc.Button(
                    "Analizar en chat con Zamy",
                    id="drawer-analyze-in-chat-btn",
                    leftSection=DashIconify(icon="tabler:message-chatbot", width=16),
                    variant="gradient",
                    gradient={"from": DS.NEXA_GOLD, "to": DS.NEXA_ORANGE},
                    fullWidth=True,
                    size="md",
                    n_clicks=0,
                ),
                dmc.Text(
                    "Envía el contexto del widget al asistente Zamy y abre el chat.",
                    size="xs", c="dimmed",  # type: ignore
                ),

                dmc.Divider(my="xs"),

                # ── Export ──
                dmc.Text("Exportar", size="xs", fw=700, c="dimmed", tt="uppercase", mb=4),  # type: ignore
                dmc.Group(
                    justify="space-between",
                    children=[
                        dmc.Button(
                            "Descargar Excel",
                            id="drawer-export-excel-btn",
                            leftSection=DashIconify(icon="tabler:file-spreadsheet", width=16),
                            variant="light",
                            color="green",
                            size="sm",
                            n_clicks=0,
                            disabled=not export_rows,
                        ),
                        dmc.Button(
                            "Copiar datos",
                            id="drawer-copy-data-btn",
                            rightSection=DashIconify(icon="tabler:copy", width=16),
                            variant="light",
                            color="blue",
                            size="sm",
                            n_clicks=0,
                            disabled=not export_rows,
                        ),
                    ],
                ),
            ],
        )

    @staticmethod
    def _create_stat_card(label, value, color, icon, theme, value_color=None):
        is_dark = theme == "dark"
        val_text = dmc.Text(str(value), size="xl", fw=700, c=value_color) if value_color else dmc.Text(str(value), size="xl", fw=700)  # type: ignore
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
                                dmc.Text(label, size="xs", c="dimmed", fw=600, tt="uppercase"),  # type: ignore
                            ],
                        ),
                        val_text,
                    ],
                )
            ],
        )

    @staticmethod
    def _create_insight_card(title, text, color, is_dark, priority):
        color_map = {
            "success": DS.SUCCESS[5],
            "info": DS.CHART_BLUE,
            "warning": DS.WARNING[5],
            "danger": DS.DANGER[5],
        }

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
                                dmc.Text(title, size="md", fw=700),  # type: ignore
                                dmc.Badge(priority, color=color if color in ("success", "warning", "info", "danger") else "blue", variant="light"), # type: ignore
                            ],
                        ),
                        dmc.Text(text, size="sm", c="dimmed"),  # type: ignore
                    ],
                )
            ],
        )

    @staticmethod
    def _create_ag_grid(df, theme, show_totals: bool = False):
        if df.empty:
            return dmc.Alert("No hay datos disponibles", color="gray")

        columnDefs = [{"field": col, "sortable": True, "filter": True} for col in df.columns]

        pinned_bottom: List[Dict] = []
        if show_totals:
            total_row: Dict[str, Any] = {}
            non_num_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
            num_cols_all = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            for col in df.columns:
                if col in num_cols_all:
                    try:
                        total_row[col] = pd.to_numeric(df[col], errors="coerce").sum()
                    except Exception:
                        total_row[col] = ""
                elif non_num_cols and col == non_num_cols[0]:
                    total_row[col] = "TOTAL"
                else:
                    total_row[col] = ""
            if total_row:
                pinned_bottom = [total_row]

        return dag.AgGrid(
            rowData=df.to_dict("records"),
            columnDefs=columnDefs,
            defaultColDef={"flex": 1, "minWidth": 100},
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 10,
                "domLayout": "autoHeight",
                "pinnedBottomRowData": pinned_bottom,
            },
        )

    @staticmethod
    def _get_analysis_table(strategy, ctx, theme):
        try:
            table_html = strategy.render(ctx, mode="analysis", theme=theme)
            return html.Div(style={"height": "500px", "overflowY": "auto"}, children=table_html)
        except:
            return dmc.Alert("No se pudo cargar la tabla de análisis", color="red")

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
    def _extract_chart_data_table(fig, theme):
        """Build a merged data table from ALL traces, preserving None for partial current-year data."""
        if not fig or not hasattr(fig, "data") or not fig.data:
            return dmc.Alert("No hay datos disponibles", color="gray")

        try:
            # Use the longest label list as the shared axis
            shared_labels: List[str] = []
            for trace in fig.data:
                lbl = DrawerDataService._extract_trace_labels(trace)
                if len(lbl) > len(shared_labels):
                    shared_labels = lbl

            if shared_labels:
                n = len(shared_labels)
                data_dict: Dict[str, Any] = {"Categoría": shared_labels}
                for i, trace in enumerate(fig.data):
                    col_name = (getattr(trace, "name", None) or "").strip() or f"Serie {i + 1}"
                    # Skip projection traces (they are forecasts, not real data)
                    if "proy" in col_name.lower():
                        continue
                    # Use raw values (None preserved) so partial traces align correctly
                    vals: List = DrawerDataService._extract_trace_values_raw(trace)
                    if vals:
                        if len(vals) < n:
                            vals = list(vals) + [None] * (n - len(vals))
                        elif len(vals) > n:
                            vals = list(vals)[:n]
                        data_dict[col_name] = vals
            else:
                # Fallback: use raw x/y from first trace
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
    def _build_multi_trace_export(fig) -> List[Dict]:
        """Build export_rows merging all traces by shared label axis (None preserved for partial data)."""
        if not fig or not hasattr(fig, "data") or not fig.data:
            return []

        shared_labels: List[str] = []
        for trace in fig.data:
            lbl = DrawerDataService._extract_trace_labels(trace)
            if len(lbl) > len(shared_labels):
                shared_labels = lbl

        if not shared_labels:
            return []

        n = len(shared_labels)
        rows: List[Dict] = [{"Categoría": lbl} for lbl in shared_labels]
        for i, trace in enumerate(fig.data):
            col_name = (getattr(trace, "name", None) or "").strip() or f"Serie {i + 1}"
            # Skip projection traces (they are forecasts, not real data)
            if "proy" in col_name.lower():
                continue
            vals: List = DrawerDataService._extract_trace_values_raw(trace)
            if vals:
                if len(vals) < n:
                    vals = list(vals) + [None] * (n - len(vals))
                elif len(vals) > n:
                    vals = list(vals)[:n]
                for j, val in enumerate(vals):
                    rows[j][col_name] = val

        return rows
