from design_system import dmc as _dmc
import dash_mantine_components as dmc
from utils.helpers import format_value
from .base_strategy import KPIStrategy
from .chart_engine import ChartEngine
from typing import Any, Dict

class ExecutiveKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="", has_detail=True, variant=None, is_pct=False, inverse=False, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)
        self.is_pct = is_pct
        self.inverse = inverse

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)

        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node: Dict[str, Any] = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        if not node:
            return {
                "title": self.title,
                "main_value": "---",
                "icon": self.icon,
                "color": self.color,
                "has_detail": self.has_detail,
                "is_table": False,
                "is_chart": False,
                "raw_data": []
            }

        config: Dict[str, Any] = dict(node)

        val = config.get("value") or config.get("current_value") or config.get("valor", 0)

        if "value_formatted" not in config:
            fmt = self.layout.get("value_format", "abbreviated")
            config["value_formatted"] = (
                f"{val:,.2f}%"
                if self.is_pct
                else format_value(val, "$", format_type=fmt)
            )

        meta = config.get("target") or config.get("target_value") or config.get("meta", 0)
        trend = config.get("trend_percent")

        if trend is None and isinstance(meta, (int, float)) and meta > 0:
            trend = ((val - meta) / meta) * 100
            config["trend"] = trend

        config.update({
            "title": self.title,
            "icon": self.icon,
            "color": self.color,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": False,
            "inverse": self.inverse,
            "value": config.get("value_formatted", "---"),
            "main_value": config.get("value_formatted", "---"),
            "status_color": config.get("status_color") or self.color,
            "raw_data": node,
        })

        return config

    def _render_standard_view(self, ctx, theme):
        return dmc.Text("Detalle no disponible", c=_dmc("dimmed"))
class ExecutiveMiniKPIStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        raw_node = self._resolve_kpi_data(ctx, self.screen_id, self.key)

        if isinstance(raw_node, (int, float, str)) and raw_node is not None:
            node = {"value": raw_node}
        elif raw_node is None:
            node = {}
        else:
            node = raw_node

        if not node:
            return {
                "title": self.title,
                "value": "---",
                "icon": self.icon,
                "color": self.color,
                "has_detail": self.has_detail,
                "is_table": False,
                "is_chart": False,
                "raw_data": {},
            }

        val_raw = node.get("value") or node.get("current_value") or node.get("valor", 0)

        try:
            val = float(val_raw)
        except (TypeError, ValueError):
            val = 0.0

        formatted = node.get("value_formatted") or format_value(val, "$", format_type="abbreviated")

        return {
            "title": self.title,
            "value": formatted,
            "icon": self.icon,
            "color": self.color,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": False,
            "raw_data": node,
        }


class ExecutiveDonutStrategy(KPIStrategy):
    def __init__(self, screen_id, key, title="", color="blue", icon="tabler:chart-pie", has_detail=True, variant=None, layout_config=None):
        super().__init__(screen_id, key, title, color, icon, has_detail, variant, layout_config)

    def get_card_config(self, ctx):
        return {
            "title": self.title,
            "icon": self.icon,
            "has_detail": self.has_detail,
            "is_table": False,
            "is_chart": True,
            "raw_data": {},
        }

    def get_figure(self, ctx, theme="light"):
        node = self._resolve_chart_data(ctx, self.screen_id, self.key)
        fig = ChartEngine.render_donut(node, theme, self.layout)
        if fig is None:
            return self._create_empty_figure(theme=theme)
        return fig