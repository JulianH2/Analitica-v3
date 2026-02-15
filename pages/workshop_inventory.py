from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
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

w_ini = SmartWidget("wi_ini", WorkshopKPIStrategy(SCREEN_ID, "initial_inventory", "Inventario Inicial", "tabler:database-import", "gray"))
w_ent = SmartWidget("wi_ent", WorkshopKPIStrategy(SCREEN_ID, "entries", "Entradas", "tabler:plus", "green"))
w_sal = SmartWidget("wi_sal", WorkshopKPIStrategy(SCREEN_ID, "outputs", "Salidas", "tabler:minus", "red"))
w_his = SmartWidget("wi_his", WorkshopKPIStrategy(SCREEN_ID, "historical_valuation", "Valorización Histórica", "tabler:history", "blue"))
w_act = SmartWidget("wi_act", WorkshopGaugeStrategy(SCREEN_ID, "current_valuation", "Valorización Actual", "blue", use_needle=False, layout_config={"height": 200}))

w_cumpl = SmartWidget("wi_cumpl", WorkshopKPIStrategy(SCREEN_ID, "compliance_level", "Cumplimiento", "tabler:checkup-list", "teal"))
w_reg = SmartWidget("wi_reg", WorkshopKPIStrategy(SCREEN_ID, "items_registered", "Insumos Reg.", "tabler:list-numbers", "indigo"))
w_con = SmartWidget("wi_con", WorkshopKPIStrategy(SCREEN_ID, "with_stock", "Con Stock", "tabler:package", "blue"))
w_sin = SmartWidget("wi_sin", WorkshopKPIStrategy(SCREEN_ID, "without_stock", "Sin Stock", "tabler:package-off", "red"))

chart_trend = ChartWidget("ci_trend", WorkshopTrendChartStrategy(SCREEN_ID, "valuation_trends", "Tendencia Histórica Valorización"))
chart_area = ChartWidget("ci_area", WorkshopHorizontalBarStrategy(SCREEN_ID, "valuation_by_area", "Valorización por Área"))

WIDGET_REGISTRY = {
    "wi_ini": w_ini, "wi_ent": w_ent, "wi_sal": w_sal, "wi_his": w_his, "wi_act": w_act,
    "wi_cumpl": w_cumpl, "wi_reg": w_reg, "wi_con": w_con, "wi_sin": w_sin
}

def _render_taller_inventory_body(ctx):
    theme = session.get("theme", "dark")
    
    def _card(widget_content, h=None):
        style = {"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}
        return dmc.Paper(
            p="xs", radius="md", withBorder=True, shadow=None,
            style=style, children=widget_content
        )
    
    return html.Div([

        dmc.Paper(
            p="md",
            withBorder=True,
            mb="xl",
            shadow="sm",
            style={"backgroundColor": "transparent"},
            children=[
                dmc.Text("ECUACIÓN DE VALORIZACIÓN", size="xs", fw=700, c="dimmed", mb="sm"), # type: ignore
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                        "gap": "0.6rem"
                    },
                    children=[
                        w_ini.render(ctx, theme=theme),
                        w_ent.render(ctx, theme=theme),
                        w_sal.render(ctx, theme=theme),
                        w_his.render(ctx, theme=theme),
                        w_act.render(ctx, theme=theme)
                    ]
                )
            ]
        ),
        

        _card(chart_trend.render(ctx, h=380, theme=theme)),
        
        dmc.Space(h="xl"),
        

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "0.6rem",
                "marginBottom": "1.5rem"
            },
            children=[
                _card(w_cumpl.render(ctx, theme=theme)),
                _card(w_reg.render(ctx, theme=theme)),
                _card(w_con.render(ctx, theme=theme)),
                _card(w_sin.render(ctx, theme=theme))
            ]
        ),
        

        dmc.Grid(
            gutter="md",
            children=[
                dmc.GridCol(
                    span={"base": 12, "lg": 5}, # type: ignore
                    children=[_card(chart_area.render(ctx, h=450, theme=theme))]
                ),
                dmc.GridCol(
                    span={"base": 12, "lg": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            style={"height": "100%", "backgroundColor": "transparent"},
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
                                                children=[WorkshopTableStrategy(SCREEN_ID, "valuation_by_family").render(ctx, theme=theme)]
                                            ),
                                            value="fam",
                                            pt="xs"
                                        ),
                                        dmc.TabsPanel(
                                            dmc.ScrollArea(
                                                h=390,
                                                children=[WorkshopTableStrategy(SCREEN_ID, "inventory_history").render(ctx, theme=theme)]
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

WIDGET_REGISTRY = {
    "wi_ini": w_ini, 
    "wi_ent": w_ent, 
    "wi_sal": w_sal, 
    "wi_his": w_his, 
    "wi_act": w_act,
    "wi_cumpl": w_cumpl, 
    "wi_reg": w_reg, 
    "wi_con": w_con, 
    "wi_sin": w_sin,
    "ci_trend": chart_trend,
    "ci_area": chart_area,
    "workshop-inventory-valuation_by_family": TableWidget(
        "workshop-inventory-valuation_by_family", 
        WorkshopTableStrategy(SCREEN_ID, "valuation_by_family")
    ),
    "workshop-inventory-inventory_history": TableWidget(
        "workshop-inventory-inventory_history", 
        WorkshopTableStrategy(SCREEN_ID, "inventory_history")
    )
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    refresh, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=60 * 60 * 1000,
        max_intervals=-1
    )
    
    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="inv-load-trigger", data={"loaded": True}),
            *refresh,
            create_smart_drawer("inv-drawer"),
            create_workshop_filters(prefix="inv"),
            html.Div(id="taller-inv-body", children=get_skeleton(SCREEN_ID))
        ]
    )

FILTER_IDS = ["inv-year", "inv-month"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="taller-inv-body",
    render_body=_render_taller_inventory_body,
    filter_ids=FILTER_IDS
)

register_drawer_callback(
    drawer_id="inv-drawer", 
    widget_registry=WIDGET_REGISTRY, 
    screen_id=SCREEN_ID, 
    filter_ids=FILTER_IDS
)