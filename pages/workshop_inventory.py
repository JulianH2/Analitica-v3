from flask import session
import dash
from dash import html
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_workshop_filters, get_filter_ids
from strategies.workshop import (
    WorkshopKPIStrategy,
    WorkshopGaugeStrategy,
    WorkshopTrendChartStrategy,
    WorkshopHorizontalBarStrategy,
    WorkshopTableStrategy
)

dash.register_page(__name__, path="/taller-inventory", title="Inventarios Almacén")

SCREEN_ID = "workshop-inventory"

w_ini = SmartWidget(
    "wi_ini",
    WorkshopKPIStrategy(SCREEN_ID, "initial_inventory", "Inventario Inicial", "tabler:database-import", "gray")
)
w_ent = SmartWidget(
    "wi_ent",
    WorkshopKPIStrategy(SCREEN_ID, "entries", "Entradas", "tabler:plus", "green")
)
w_sal = SmartWidget(
    "wi_sal",
    WorkshopKPIStrategy(SCREEN_ID, "outputs", "Salidas", "tabler:minus", "red")
)
w_his = SmartWidget(
    "wi_his",
    WorkshopKPIStrategy(SCREEN_ID, "historical_valuation", "Valorización Histórica", "tabler:history", "blue")
)
w_act = SmartWidget(
    "wi_act",
    WorkshopGaugeStrategy(SCREEN_ID, "current_valuation", "Valorización Actual", "blue", use_needle=False)
)

w_cumpl = SmartWidget(
    "wi_cumpl",
    WorkshopKPIStrategy(SCREEN_ID, "compliance_level", "Cumplimiento", "tabler:checkup-list", "teal")
)
w_reg = SmartWidget(
    "wi_reg",
    WorkshopKPIStrategy(SCREEN_ID, "items_registered", "Insumos Reg.", "tabler:list-numbers", "indigo")
)
w_con = SmartWidget(
    "wi_con",
    WorkshopKPIStrategy(SCREEN_ID, "with_stock", "Con Stock", "tabler:package", "blue")
)
w_sin = SmartWidget(
    "wi_sin",
    WorkshopKPIStrategy(SCREEN_ID, "without_stock", "Sin Stock", "tabler:package-off", "red")
)

chart_trend = ChartWidget(
    "ci_trend",
    WorkshopTrendChartStrategy(SCREEN_ID, "valuation_trends", "Tendencia Histórica Valorización")
)
chart_area = ChartWidget(
    "ci_area",
    WorkshopHorizontalBarStrategy(SCREEN_ID, "valuation_by_area", "Valorización por Área")
)

WIDGET_REGISTRY = {
    "wi_ini": w_ini,
    "wi_ent": w_ent,
    "wi_sal": w_sal,
    "wi_his": w_his,
    "wi_act": w_act,
    "wi_cumpl": w_cumpl,
    "wi_reg": w_reg,
    "wi_con": w_con,
    "wi_sin": w_sin
}

def _render_taller_inventory_body(ctx):
    return html.Div([
        dmc.Paper(
            p="md",
            withBorder=True,
            mb="xl",
            shadow="sm",
            children=[
                dmc.Text("ECUACIÓN DE VALORIZACIÓN", size="xs", fw=700, c="dimmed", mb="sm"), # type: ignore
                dmc.SimpleGrid(
                    cols={"base": 1, "md": 2, "lg": 5}, # type: ignore
                    spacing="xs",
                    children=[
                        w_ini.render(ctx),
                        w_ent.render(ctx),
                        w_sal.render(ctx),
                        w_his.render(ctx),
                        w_act.render(ctx)
                    ]
                )
            ]
        ),
        chart_trend.render(ctx, h=380),
        dmc.Space(h="xl"),
        dmc.SimpleGrid(
            cols={"base": 2, "md": 4}, # type: ignore
            spacing="md",
            mb="xl",
            children=[
                w_cumpl.render(ctx),
                w_reg.render(ctx),
                w_con.render(ctx),
                w_sin.render(ctx)
            ]
        ),
        dmc.Grid(
            gutter="md",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 5}, # type: ignore
                    children=[chart_area.render(ctx, h=450)]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            style={"height": "100%"},
                            children=[
                                dmc.Tabs(
                                    value="fam",
                                    children=[
                                        dmc.TabsList([
                                            dmc.TabsTab("Por Familia", value="fam"),
                                            dmc.TabsTab("Historial Detallado", value="hist")
                                        ]),
                                        dmc.TabsPanel(
                                            dmc.ScrollArea(
                                                h=390,
                                                children=[WorkshopTableStrategy(SCREEN_ID, "valuation_by_family").render(ctx)]
                                            ),
                                            value="fam",
                                            pt="xs"
                                        ),
                                        dmc.TabsPanel(
                                            dmc.ScrollArea(
                                                h=390,
                                                children=[WorkshopTableStrategy(SCREEN_ID, "inventory_history").render(ctx)]
                                            ),
                                            value="hist",
                                            pt="xs"
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
    )
    return dmc.Container(
        fluid=True,
        children=[
            create_smart_modal("inv-modal"),
            *refresh,
            create_workshop_filters(prefix="inv"),
            html.Div(id="taller-inv-body", children=_render_taller_inventory_body(ctx))
        ]
    )

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-inv-body",
    render_body=_render_taller_inventory_body,
    filter_ids=get_filter_ids("inv", 5)
)

register_modal_callback("inv-modal", WIDGET_REGISTRY, SCREEN_ID)
