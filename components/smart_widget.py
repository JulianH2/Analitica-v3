import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
from settings.theme import DesignSystem, SemanticColors
from typing import Any

class SmartWidget:
    def __init__(self, widget_id: str, strategy: Any):
        self.widget_id = widget_id
        self.strategy = strategy

    def _get_delta_info(self, config, is_ytd=False):
        prefix = "ytd_" if is_ytd else "monthly_"
        delta = config.get(f"{prefix}delta") or (config.get("vs_2024") if not is_ytd else None)
        label_text = "vs 2024" if not is_ytd else "vs Meta"
        
        if delta is not None:
            val = float(delta)
            return f"{val:+.1%}", SemanticColors.INGRESO if val >= 0 else SemanticColors.EGRESO, label_text
        
        label_key = "label_ytd" if is_ytd else "label_mes"
        text = str(config.get(label_key, ""))
        if "(" in text:
            try:
                pct = text.split("(")[1].replace(")", "")
                return pct, SemanticColors.EGRESO if "-" in pct else SemanticColors.INGRESO, label_text
            except: pass
        return None, DesignSystem.SLATE[4], label_text

    def render(self, data_context: Any, mode: str = "simple"):
        config = self.strategy.get_card_config(data_context)
        layout = getattr(self.strategy, 'layout', {})
        card_height = layout.get("height", 195)
        
        m_pct, m_col, m_lab = self._get_delta_info(config)
        y_pct, y_col, y_lab = self._get_delta_info(config, is_ytd=True)

        extra_details = dmc.Stack(gap=2, mt=8, children=[
            dmc.Group(justify="space-between", children=[
                dmc.Text("Este Mes:", size="10px", c="dimmed"), # type: ignore
                dmc.Group(gap=4, children=[
                    dmc.Text(str(config.get("monthly_display") or config.get("label_mes", "")).split(" (")[0], size="10px", fw=700, c=SemanticColors.TEXT_MUTED), # type: ignore
                    dmc.Group(gap=2, children=[
                        dmc.Text(m_lab, size="9px", c="dimmed", fs="italic"), # type: ignore
                        dmc.Text(m_pct, size="10px", fw=700, c=m_col) # type: ignore
                    ]) if m_pct else None
                ])
            ]) if config.get("label_mes") or config.get("monthly_display") else None,
            dmc.Group(justify="space-between", children=[
                dmc.Text("Acumulado:", size="10px", c="dimmed"), # type: ignore
                dmc.Group(gap=4, children=[
                    dmc.Text(str(config.get("ytd_display") or config.get("label_ytd", "")).split(" (")[0], size="10px", fw=700, c=SemanticColors.TEXT_MUTED), # type: ignore
                    dmc.Group(gap=2, children=[
                        dmc.Text(y_lab, size="9px", c="dimmed", fs="italic"), # type: ignore
                        dmc.Text(y_pct, size="10px", fw=700, c=y_col) # type: ignore
                    ]) if y_pct else None
                ])
            ]) if config.get("label_ytd") or config.get("ytd_display") else None,
        ])

        if mode == "combined":
            return self._render_combined(config, extra_details, card_height, data_context)
        
        return dmc.Paper(
            p="sm", radius="md", withBorder=True, shadow="xs",
            style={"height": card_height, "backgroundColor": DesignSystem.TRANSPARENT},
            children=dmc.Stack(justify="space-between", h="100%", gap=0, children=[
                self._header(config),
                dmc.Center(style={"flex": 1, "flexDirection": "column"}, children=[
                    dmc.Text(config.get("value", "0"), fw=800, fz="1.6rem", lh="1", ta="center"), # type: ignore
                    extra_details
                ]),
                self._footer(config)
            ])
        )

    def _render_combined(self, config, extra_details, height, ctx):
        figure = self.strategy.get_figure(ctx)
        return dmc.Paper(
            p="sm", radius="md", withBorder=True, shadow="xs",
            style={"height": height, "backgroundColor": DesignSystem.TRANSPARENT},
            children=dmc.Grid(align="stretch", style={"height": "100%"}, gutter=0, children=[
                dmc.GridCol(span=7, children=dmc.Stack(justify="space-between", h="100%", p=4, children=[
                    self._header(config),
                    dmc.Box([
                        dmc.Text(config.get("value", "0"), fw=800, fz="1.5rem", lh="1"), # type: ignore
                    ]),
                    extra_details
                ])),
                dmc.GridCol(span=5, children=dmc.Stack(justify="center", align="center", gap=0, style={"height": "100%"}, children=[
                    dcc.Graph(figure=figure, config={'displayModeBar': False}, style={"height": "140px", "width": "100%"}),
                    dmc.Text(config.get("meta_text", ""), size="10px", c="dimmed", ta="center", mt=-10) # type: ignore
                ]))
            ])
        )

    def _header(self, config):
        return dmc.Group(justify="space-between", align="flex-start", w="100%", children=[
            dmc.Text(config.get("title", self.strategy.title), size="xs", c="dimmed", fw="bold", tt="uppercase"), # type: ignore
            dmc.ThemeIcon(
                DashIconify(icon=config.get("icon", self.strategy.icon), width=18),
                variant="light", color=self.strategy.color, size="md", radius="md"
            )
        ])

    def _footer(self, config):
        return dmc.Group(justify="space-between", align="flex-end", w="100%", children=[
            dmc.Stack(gap=0, children=[
                dmc.Text(config.get("meta_text", ""), size="10px", c="dimmed") if config.get("is_simple") else None # type: ignore
            ]),
            dmc.Button("Detalles", variant="subtle", color="gray", size="compact-xs", w="90px", rightSection=DashIconify(icon="tabler:maximize", width=12)) if getattr(self.strategy, 'has_detail', False) else None
        ])