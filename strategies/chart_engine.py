import datetime
import math
import plotly.graph_objects as go
from design_system import ChartColors, Colors, ComponentSizes, GaugeConfig, Typography
from services.time_service import TimeService


def safe_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            clean = val.replace("%", "").replace("$", "").replace(",", "").strip()
            return float(clean) if clean else default
        except:
            return default
    return default


def safe_max(*args):
    valid = [safe_float(v) for v in args if v is not None]
    return max(valid) if valid else 0.0


def clean_series(x_data, y_data):
    x_clean, y_clean = [], []
    for x, y in zip(x_data or [], y_data or []):
        y_val = safe_float(y)
        if not math.isnan(y_val):
            x_clean.append(x)
            y_clean.append(y_val)
        else:
            x_clean.append(x)
            y_clean.append(0)
    return x_clean, y_clean


class ChartEngine:
    @staticmethod
    def render_donut(node, theme="dark", layout_config=None):
        is_dark = theme == "dark"
        layout_config = layout_config or {}

        data_source = node.get("data", node) if isinstance(node, dict) else {}
        labels = data_source.get("labels", [])
        values = data_source.get("values", [])
        colors = data_source.get("colors", [])
        total = data_source.get("total_formatted", "")

        if not labels or not values:
            return None

        if not colors:
            colors = [ChartColors.DONUT[i % len(ChartColors.DONUT)] for i in range(len(labels))]

        fig_height = layout_config.get("height", 260)
        max_index = max(range(len(values)), key=lambda i: values[i])

        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.65,
                marker=dict(
                    colors=colors,
                    line=dict(color=Colors.BG_DARK_CARD if is_dark else Colors.BG_LIGHT, width=2),
                ),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
                pull=[0.05 if i == max_index else 0 for i in range(len(values))],
            )
        ])

        if total:
            fig.add_annotation(
                text=f"<b>Total</b><br>{total}",
                x=0.30,
                y=0.5,
                showarrow=False,
                font=dict(
                    size=Typography.MD,
                    color=Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT,
                    family=Typography.FAMILY,
                ),
                xref="paper",
                yref="paper",
            )

        fig.update_traces(domain=dict(x=[0.0, 0.60], y=[0.0, 1.0]))

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=fig_height,
            margin=dict(t=30, b=20, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.65, itemsizing="constant"),
        )
        return fig

    @staticmethod
    def render_trend(node, theme="dark", layout_config=None):
        layout_config = layout_config or {}
        ts = TimeService()

        if not node:
            return None

        curr_year = str(ts.current_year)
        prev_year = str(ts.previous_year)
        curr_month = datetime.date.today().month

        data_source = node.get("data", node)
        categories = data_source.get("categories") or data_source.get("months") or []
        series_list = data_source.get("series", [])

        if not categories or not series_list:
            return None

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_name = s.get("name", "")
            s_data = s.get("data", [])

            if "Meta" in s_name or "Objetivo" in s_name:
                base_color = Colors.CHART_TARGET
            elif curr_year in s_name or "Actual" in s_name:
                base_color = Colors.CHART_CURRENT
            elif prev_year in s_name or "Anterior" in s_name:
                base_color = Colors.CHART_PREVIOUS
            else:
                base_color = ChartColors.CHART_COLORS[idx % len(ChartColors.CHART_COLORS)]

            past_y = [safe_float(y) if i < curr_month else None for i, y in enumerate(s_data)]
            future_y = [safe_float(y) if i >= curr_month - 1 else None for i, y in enumerate(s_data)]

            if "Meta" in s_name:
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name="Meta",
                    mode="lines+markers",
                    line=dict(color=base_color, width=2, dash="dot"),
                    marker=dict(size=6),
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories,
                    y=past_y,
                    name=s_name.replace(curr_year, "Actual").replace(prev_year, "Anterior"),
                    marker=dict(color=base_color, cornerradius=6),
                    width=0.38,
                    offsetgroup=str(idx),
                ))

                fig.add_trace(go.Bar(
                    x=categories,
                    y=future_y,
                    name=f"{s_name} (proy.)",
                    marker=dict(color=base_color, opacity=0.45, cornerradius=6),
                    width=0.38,
                    offsetgroup=str(idx),
                    showlegend=False,
                ))

        h_val = layout_config.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            barmode="group",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig

    @staticmethod
    def render_gauge(raw_node, theme="dark", layout_config=None, hex_color=None):
        layout_config = layout_config or {}
        ts = TimeService()

        if not raw_node or not isinstance(raw_node, dict):
            return None

        prev_year = str(ts.previous_year)

        current = safe_float(raw_node.get("value", 0))
        target = safe_float(raw_node.get("target")) if raw_node.get("target") else None
        vs_last_year = safe_float(raw_node.get("vs_last_year")) if raw_node.get("vs_last_year") else None

        percentage = (current / target * 100) if target and target > 0 else 0
        gauge_color = GaugeConfig.get_gauge_color(percentage) if target else (hex_color or Colors.BAR_BLUE)

        max_val = safe_max(current, target or 0, vs_last_year or 0, 100)

        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=current,
            number={"font": {"size": Typography.KPI_MEDIUM, "family": Typography.FAMILY}, "valueformat": ",.0f"},
            gauge={
                "axis": {"range": [0, max_val * 1.1], "tickwidth": 1},
                "bar": {"color": gauge_color},
                "bgcolor": Colors.TRANSPARENT,
                "borderwidth": 0,
                "threshold": {
                    "line": {"color": Colors.CHART_TARGET, "width": 4},
                    "thickness": 0.8,
                    "value": target if target else max_val,
                },
            },
        ))

        if target:
            fig.add_annotation(
                x=0.5,
                y=-0.15,
                text=f"<b>META:</b> {target:,.0f}",
                showarrow=False,
                font=dict(size=Typography.BADGE, color=Colors.CHART_TARGET, family=Typography.FAMILY),
                xref="paper",
                yref="paper",
            )

        if vs_last_year:
            fig.add_annotation(
                x=0.5,
                y=-0.30,
                text=f"Año {prev_year}: {vs_last_year:,.0f}",
                showarrow=False,
                font=dict(size=Typography.XS, color=Colors.CHART_PREVIOUS, family=Typography.FAMILY),
                xref="paper",
                yref="paper",
            )

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=layout_config.get("height", ComponentSizes.KPI_HEIGHT_NORMAL),
            margin=dict(l=25, r=25, t=30, b=50),
            hovermode=False,
        )
        return fig

    @staticmethod
    def render_horizontal_bar(node, theme="dark", layout_config=None):
        layout_config = layout_config or {}

        if not node:
            return None

        data_source = node.get("data", node)
        categories = [str(c) for c in (data_source.get("categories") or data_source.get("labels") or [])]
        values = [safe_float(v) for v in data_source.get("values", [])]
        target_val = safe_float(data_source.get("target") or data_source.get("goal"))

        if not categories:
            return None

        num_bars = len(categories)
        calculated_height = max(layout_config.get("height", 340), num_bars * 50 + 100)
        avg_value = sum(values) / len(values) if values else 0

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=values,
            y=categories,
            orientation="h",
            marker=dict(color=Colors.CHART_GOLD, cornerradius=6),
            width=0.80,
            text=[
                f"${v/1e6:.1f}M" if v >= 1e6 else f"${v/1e3:.1f}k" if v >= 1000 else f"${v:.0f}"
                for v in values
            ],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Valor: $%{x:,.2f}<extra></extra>",
        ))

        if target_val > 0 or avg_value > 0:
            ref_val = target_val if target_val > 0 else avg_value
            fig.add_vline(
                x=ref_val,
                line_width=2,
                line_dash="dot",
                line_color=Colors.CHART_TARGET,
                annotation_text=f"META: ${ref_val:,.0f}",
                annotation_position="top",
                annotation_font=dict(size=Typography.XS, color=Colors.CHART_TARGET, family=Typography.FAMILY),
            )

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=calculated_height,
            margin=dict(t=50, b=40, l=120, r=80),
            showlegend=False,
            xaxis=dict(showgrid=True, zeroline=False, tickformat="$,.0f", side="top"),
            yaxis=dict(type="category", autorange="reversed", automargin=True),
            bargap=0.8,
        )
        return fig

    @staticmethod
    def render_line_chart(node, theme="dark", layout_config=None, current_month_only=False):
        layout_config = layout_config or {}
    
        if not node:
            return None
    
        data_source = node.get("data", node)
        all_categories = data_source.get("categories") or data_source.get("months") or []
        series_list = data_source.get("series", [])
    
        if not all_categories or not series_list:
            return None
    
        curr_month = len(all_categories)
    
        if current_month_only:
            curr_month = datetime.date.today().month
            categories = all_categories[:curr_month]
        else:
            categories = all_categories
    
        fig = go.Figure()
    
        for idx, s in enumerate(series_list):
            s_type = s.get("type", "bar")
            s_name = s.get("name", f"Serie {idx}")
            s_data = s.get("data", [])
    
            if current_month_only:
                s_data = s_data[:curr_month]
    
            s_color = s.get("color", ChartColors.DEFAULT[idx % len(ChartColors.DEFAULT)])
    
            if s_type == "line" or "Meta" in s_name:
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    mode="lines+markers",
                    line=dict(color=s_color, width=3, dash="dot" if "Meta" in s_name else "solid"),
                    marker=dict(size=6),
                ))
            else:
                fig.add_trace(go.Bar(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    marker_color=s_color
                ))
    
        height_val = layout_config.get("height", 350)
        plotly_height = height_val if isinstance(height_val, int) else None
    
        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            margin=dict(t=30, b=40, l=50, r=30),
            height=plotly_height,
            autosize=True,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11),
            ),
            barmode="group",
            hovermode="x unified",
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10)),
        )
    
        return fig
    
    @staticmethod
    def render_stacked_bar(node, theme="dark", layout_config=None):
        layout_config = layout_config or {}

        if not node:
            return None

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])

        if not categories or not series_list:
            return None

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_name = s.get("name", "")
            s_data = s.get("data", [])
            base_color = ChartColors.CHART_COLORS[idx % len(ChartColors.CHART_COLORS)]

            fig.add_trace(go.Bar(
                x=categories,
                y=s_data,
                name=s_name,
                marker=dict(color=base_color, cornerradius=6),
            ))

        h_val = layout_config.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            barmode="stack",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig

    @staticmethod
    def render_cash_flow(node, theme="dark", layout_config=None):
        layout_config = layout_config or {}

        if not node:
            return None

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        ingresos = data_source.get("ingresos", [])
        egresos = data_source.get("egresos", [])

        if not categories:
            return None

        fig = go.Figure()
        fig.add_trace(go.Bar(x=categories, y=ingresos, name="Ingresos", marker=dict(color=Colors.POSITIVE, cornerradius=6)))
        fig.add_trace(go.Bar(x=categories, y=[-e for e in egresos], name="Egresos", marker=dict(color=Colors.NEGATIVE, cornerradius=6)))

        h_val = layout_config.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            barmode="relative",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig

    @staticmethod
    def render_multi_line(node, theme="dark", layout_config=None, forecast_mode=False):
        layout_config = layout_config or {}

        if not node:
            return None

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])

        if not categories or not series_list:
            return None

        fig = go.Figure()

        for idx, s in enumerate(series_list):
            s_name = s.get("name", "")
            s_data = s.get("data", [])
            is_forecast = forecast_mode and ("Forecast" in s_name or "Proyección" in s_name)
            base_color = ChartColors.LINE_TRENDS[idx % len(ChartColors.LINE_TRENDS)]

            fig.add_trace(go.Scatter(
                x=categories,
                y=s_data,
                name=s_name,
                mode="lines+markers",
                line=dict(color=base_color, width=2, dash="dash" if is_forecast else "solid"),
                marker=dict(size=5 if is_forecast else 6),
            ))

        h_val = layout_config.get("height")
        plot_height = h_val if isinstance(h_val, (int, float)) else ComponentSizes.CHART_HEIGHT_BASE

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=plot_height,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        )
        return fig

    @staticmethod
    def render_bar_chart(node, theme="dark", layout_config=None):
        layout_config = layout_config or {}

        if not node:
            return None

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])

        if not categories:
            return None

        fig = go.Figure()

        for serie in series_list:
            s_name = serie.get("name", "Valor")
            s_data = serie.get("data", [])
            s_color = serie.get("color", ChartColors.CHART_COLORS[0])
            fig.add_trace(go.Bar(x=categories, y=s_data, name=s_name, marker_color=s_color))

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=layout_config.get("height", 350),
            margin=dict(t=30, b=40, l=40, r=20),
            showlegend=len(series_list) > 1,
        )
        return fig

    @staticmethod
    def render_combo_chart(node, theme="dark", layout_config=None):
        layout_config = layout_config or {}

        if not node:
            return None

        data_source = node.get("data", node)
        categories = data_source.get("categories", [])
        series_list = data_source.get("series", [])

        if not categories or not series_list:
            return None

        fig = go.Figure()

        for serie in series_list:
            s_name = serie.get("name", "")
            s_data = serie.get("data", [])
            s_color = serie.get("color", ChartColors.CHART_COLORS[0])
            s_type = serie.get("type", "bar")

            if s_type == "line":
                fig.add_trace(go.Scatter(
                    x=categories,
                    y=s_data,
                    name=s_name,
                    mode="lines+markers",
                    line=dict(color=s_color, width=3),
                    marker=dict(size=6),
                    yaxis="y2",
                ))
            else:
                fig.add_trace(go.Bar(x=categories, y=s_data, name=s_name, marker_color=s_color))

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            height=layout_config.get("height", 350),
            margin=dict(t=30, b=40, l=40, r=40),
            legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
            hovermode="x unified",
            yaxis=dict(title=""),
            yaxis2=dict(title="", overlaying="y", side="right"),
        )
        return fig

    @staticmethod
    def render_map(node, theme="dark", layout_config=None):
        layout_config = layout_config or {}
        is_dark = theme == "dark"

        if not node:
            return None

        data_source = node.get("data", node)
        routes = data_source.get("routes", [])

        if not routes:
            return None

        fig = go.Figure()

        for route in routes:
            lats = route.get("lat", [])
            lons = route.get("lon", [])
            name = route.get("name", "Ruta")
            color = route.get("color", Colors.CHART_BLUE)

            if lats and lons:
                fig.add_trace(go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode="lines+markers",
                    name=name,
                    line=dict(width=3, color=color),
                    marker=dict(size=8, color=color),
                ))

        center_lat, center_lon = 20.5937, -100.3897
        all_lats = [lat for r in routes for lat in (r.get("lat", []) or [])]
        all_lons = [lon for r in routes for lon in (r.get("lon", []) or [])]

        if all_lats and all_lons:
            center_lat = sum(all_lats) / len(all_lats)
            center_lon = sum(all_lons) / len(all_lons)

        legend_bg = "rgba(98,104,110,0.9)" if is_dark else "rgba(255,255,255,0.9)"

        fig.update_layout(
            mapbox=dict(style="open-street-map", center=dict(lat=center_lat, lon=center_lon), zoom=10),
            margin=dict(l=0, r=0, t=0, b=0),
            height=layout_config.get("height", ComponentSizes.CHART_HEIGHT_LG),
            showlegend=True,
            font=dict(family=Typography.FAMILY, size=Typography.SM, color=Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor=legend_bg, font=dict(size=Typography.XS, family=Typography.FAMILY)),
        )
        return fig

    @staticmethod
    def render_table(node, theme="dark"):
        is_dark = theme == "dark"

        if not node:
            return None

        data_source = node.get("data", node)
        headers = data_source.get("headers", [])
        rows = data_source.get("rows", [])

        if not headers:
            return None

        cols = list(map(list, zip(*rows))) if rows else [[] for _ in headers]

        header_bg = Colors.BG_DARK_CARD if is_dark else Colors.SLATE[1]
        header_color = Colors.TEXT_DARK if is_dark else Colors.SLATE[7]
        cell_bg = Colors.BG_DARK if is_dark else "white"
        cell_color = Colors.TEXT_DARK if is_dark else Colors.SLATE[6]
        line_color = Colors.SLATE[5] if is_dark else Colors.SLATE[2]

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f"<b>{h}</b>" for h in headers],
                fill_color=header_bg,
                align="left",
                font=dict(color=header_color, size=Typography.TABLE_HEADER),
                height=30,
            ),
            cells=dict(
                values=cols,
                fill_color=cell_bg,
                align="left",
                font=dict(color=cell_color, size=Typography.TABLE),
                height=25,
                line_color=line_color,
            ),
        )])

        fig.update_layout(
            template="plotly_dark" if theme == "dark" else "plotly",
            margin=dict(t=10, b=10, l=10, r=10),
            height=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig