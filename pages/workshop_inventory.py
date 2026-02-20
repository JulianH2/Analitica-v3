from design_system import dmc as _dmc
from flask import session
import dash
from dash import html, dcc
import dash_mantine_components as dmc

from components.table_widget import TableWidget
from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.skeleton import get_skeleton
from components.filter_manager import create_filter_section, register_filter_modal_callback
from strategies.workshop import WorkshopKPIStrategy, WorkshopGaugeStrategy, WorkshopTrendChartStrategy, WorkshopHorizontalBarStrategy, WorkshopTableStrategy
from services.time_service import TimeService

_ts = TimeService()

def get_dynamic_title(base_title: str) -> str:
    return f"{base_title} {_ts.current_year} vs. {_ts.previous_year}"

dash.register_page(__name__, path="/workshop-inventory", title="Almacén")

SCREEN_ID = "workshop-inventory"
PREFIX = "wi"

w_ini = SmartWidget(f"{PREFIX}_ini", WorkshopKPIStrategy(SCREEN_ID, "initial_inventory", "Inventario Inicial", "tabler:database-import", "gray"))
w_ent = SmartWidget(f"{PREFIX}_ent", WorkshopKPIStrategy(SCREEN_ID, "entries", "Entradas", "tabler:plus", "green"))
w_sal = SmartWidget(f"{PREFIX}_sal", WorkshopKPIStrategy(SCREEN_ID, "outputs", "Salidas", "tabler:minus", "red"))
w_his = SmartWidget(f"{PREFIX}_his", WorkshopKPIStrategy(SCREEN_ID, "historical_valuation", "Valorización Histórica", "tabler:history", "blue"))
w_act = SmartWidget(f"{PREFIX}_act", WorkshopGaugeStrategy(SCREEN_ID, "current_valuation", "Valorización Actual", "blue", use_needle=False, layout_config={"height": 200}))

w_cmp = SmartWidget(f"{PREFIX}_cmp", WorkshopKPIStrategy(SCREEN_ID, "compliance_level", "Nivel Cumplimiento Max Min", "tabler:checkup-list", "teal"))
w_reg = SmartWidget(f"{PREFIX}_reg", WorkshopKPIStrategy(SCREEN_ID, "items_registered", "Insumos Registrados", "tabler:list-numbers", "indigo"))
w_con = SmartWidget(f"{PREFIX}_con", WorkshopKPIStrategy(SCREEN_ID, "with_stock", "Insumos con Existencia", "tabler:package", "blue"))
w_sin = SmartWidget(f"{PREFIX}_sin", WorkshopKPIStrategy(SCREEN_ID, "without_stock", "Insumos sin Existencia", "tabler:package-off", "red"))

class DynamicInvTrendStrategy(WorkshopTrendChartStrategy):
    def __init__(self, screen_id, key, base_title, has_detail=True, layout_config=None):
        self.base_title = base_title
        super().__init__(screen_id, key, get_dynamic_title(base_title), has_detail=has_detail, layout_config=layout_config)
    def get_card_config(self, ctx):
        config = super().get_card_config(ctx)
        config["title"] = get_dynamic_title(self.base_title)
        return config

c_trend = ChartWidget(f"{PREFIX}_trend", DynamicInvTrendStrategy(SCREEN_ID, "valuation_trends", "Valorización Histórica", has_detail=True, layout_config={"height": 380}))
c_area = ChartWidget(f"{PREFIX}_area", WorkshopHorizontalBarStrategy(SCREEN_ID, "valuation_by_area", "Valorización Actual por Área", has_detail=True, layout_config={"height": 450}))

t_fam = TableWidget(f"{SCREEN_ID}-valuation_by_family", WorkshopTableStrategy(SCREEN_ID, "valuation_by_family", title="Valorización Actual por Familia, Subfamilia, Insumo y Medida"))
t_hist = TableWidget(f"{SCREEN_ID}-inventory_history", WorkshopTableStrategy(SCREEN_ID, "inventory_history", title="Historial Detallado"))

def _render_taller_inventory_body(ctx):
    theme = session.get("theme", "dark")

    return html.Div([
        dmc.Paper(
            p="md",
            withBorder=True,
            mb="xl",
            shadow="sm",
            style={"backgroundColor": "transparent"},
            children=[
                dmc.Text("ECUACIÓN DE VALORIZACIÓN", size="xs", fw=_dmc(700), c=_dmc("dimmed"), mb="sm"),
                html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))", "gap": "0.6rem"}, children=[
                    w_ini.render(ctx, theme=theme),
                    w_ent.render(ctx, theme=theme),
                    w_sal.render(ctx, theme=theme),
                    w_his.render(ctx, theme=theme),
                    w_act.render(ctx, theme=theme)
                ])
            ]
        ),
        c_trend.render(ctx, h=420, theme=theme),
        dmc.Space(h="xl"),
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))", "gap": "0.6rem", "marginBottom": "1.5rem"}, children=[
            w_cmp.render(ctx, theme=theme),
            w_reg.render(ctx, theme=theme),
            w_con.render(ctx, theme=theme),
            w_sin.render(ctx, theme=theme)
        ]),
        dmc.Grid(gutter="md", children=[
            dmc.GridCol(span=_dmc({"base": 12, "lg": 5}), children=[c_area.render(ctx, h=480, theme=theme)]),
            dmc.GridCol(span=_dmc({"base": 12, "lg": 7}), children=[dmc.Paper(
                p="md",
                withBorder=True,
                style={"height": "100%", "backgroundColor": "transparent"},
                children=[dmc.Tabs(value="fam", children=[
                    dmc.TabsList([
                        dmc.TabsTab("Por Familia", value="fam"),
                        dmc.TabsTab("Historial Detallado", value="hist")
                    ]),
                    dmc.TabsPanel(dmc.ScrollArea(h=390, children=[t_fam.render(ctx, theme=theme)]), value="fam", pt="xs"),
                    dmc.TabsPanel(dmc.ScrollArea(h=390, children=[t_hist.render(ctx, theme=theme)]), value="hist", pt="xs"),
                ])]
            )]),
        ]),
        dmc.Space(h=50),
    ])

WIDGET_REGISTRY = {
    f"{PREFIX}_ini": w_ini, f"{PREFIX}_ent": w_ent, f"{PREFIX}_sal": w_sal, f"{PREFIX}_his": w_his, f"{PREFIX}_act": w_act,
    f"{PREFIX}_cmp": w_cmp, f"{PREFIX}_reg": w_reg, f"{PREFIX}_con": w_con, f"{PREFIX}_sin": w_sin,
    f"{PREFIX}_trend": c_trend, f"{PREFIX}_area": c_area,
    f"{SCREEN_ID}-valuation_by_family": t_fam, f"{SCREEN_ID}-inventory_history": t_hist,
}

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    refresh, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=60 * 60 * 1000, max_intervals=-1)

    filters = create_filter_section(
        year_id="inv-year",
        month_id="inv-month",
        additional_filters=[
            {"id": "inv-empresa", "label": "Empresa\\Área", "data": ["Todas"], "value": "Todas"},
            {"id": "inv-almacen", "label": "Almacén", "data": ["Todas"], "value": "Todas"},
            {"id": "inv-familia", "label": "Familia\\SubFamilia", "data": ["Todas"], "value": "Todas"},
            {"id": "inv-insumo", "label": "Insumo", "data": ["Todas"], "value": "Todas"},
            {"id": "inv-estado", "label": "Estado", "data": ["Todas"], "value": "Todas"},
            {"id": "inv-unidad-medida", "label": "Unidad Medida", "data": ["Todas"], "value": "Todas"},
        ],
    )

    return dmc.Container(fluid=True, px="md", children=[
        dcc.Store(id="inv-load-trigger", data={"loaded": True}),
        *refresh,
        create_smart_drawer("inv-drawer"),
        filters,
        html.Div(id="taller-inv-body", children=get_skeleton(SCREEN_ID))
    ])

FILTER_IDS = ["inv-year", "inv-month", "inv-empresa", "inv-almacen", "inv-familia", "inv-insumo", "inv-estado", "inv-unidad-medida"]

data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="taller-inv-body", render_body=_render_taller_inventory_body, filter_ids=FILTER_IDS)

register_drawer_callback(drawer_id="inv-drawer", widget_registry=WIDGET_REGISTRY, screen_id=SCREEN_ID, filter_ids=FILTER_IDS)

register_filter_modal_callback("inv-year")