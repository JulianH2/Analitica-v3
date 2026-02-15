from flask import session
import dash
from dash import html, dcc, callback, Input, Output, no_update
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.filter_manager import create_filter_section
from strategies.administration import (
    AdminKPIStrategy, AdminTrendChartStrategy,
    AdminDonutChartStrategy, AdminTableStrategy
)

dash.register_page(__name__, path="/admin-banks", title="Bancos")

SCREEN_ID = "administration-banks"

def skeleton_admin_banks():
    
    from components.skeleton import skeleton_kpi, skeleton_chart, skeleton_table, skeleton_box
    
    def tab_content():
        return html.Div(
            style={"paddingTop": "1rem"},
            children=[
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                        "gap": "0.8rem",
                        "marginBottom": "1.5rem"
                    },
                    children=[skeleton_kpi() for _ in range(4)]
                ),
                html.Div(
                    style={"marginBottom": "1.5rem"},
                    children=[skeleton_chart("380px")]
                ),
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "5fr 7fr",
                        "gap": "1rem"
                    },
                    children=[
                        skeleton_chart("400px"),
                        skeleton_table(8, 4)
                    ]
                )
            ]
        )
    
    return html.Div(
        className="skeleton-layout",
        children=[
            skeleton_box("24px", "200px", "skeleton-title"),
            html.Div(
                style={"marginTop": "1.5rem"},
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "0.5rem",
                            "marginBottom": "1rem",
                            "borderBottom": "1px solid rgba(255,255,255,0.1)"
                        },
                        children=[skeleton_box("32px", "100px") for _ in range(3)]
                    ),
                    tab_content()
                ]
            )
        ]
    )

def _bank_widgets(variant):
    suffix = "Consolidado" if variant == "consolidado" else ("MXN" if variant == "pesos" else "USD")
    return {
        "kpi_initial": SmartWidget(
            f"kb_initial_{variant}",
            AdminKPIStrategy(
                screen_id=SCREEN_ID,
                kpi_key="initial_balance",
                title=f"Saldo Inicial {suffix}",
                icon="tabler:wallet",
                color="gray",
                variant=variant
            )
        ),
        "kpi_incomes": SmartWidget(
            f"kb_incomes_{variant}",
            AdminKPIStrategy(
                screen_id=SCREEN_ID,
                kpi_key="total_income",
                title=f"Ingresos {suffix}",
                icon="tabler:trending-up",
                color="green",
                variant=variant
            )
        ),
        "kpi_expenses": SmartWidget(
            f"kb_expenses_{variant}",
            AdminKPIStrategy(
                screen_id=SCREEN_ID,
                kpi_key="total_expenses",
                title=f"Egresos {suffix}",
                icon="tabler:trending-down",
                color="red",
                variant=variant
            )
        ),
        "kpi_final": SmartWidget(
            f"kb_final_{variant}",
            AdminKPIStrategy(
                screen_id=SCREEN_ID,
                kpi_key="final_balance",
                title=f"Saldo Final {suffix}",
                icon="tabler:cash",
                color="indigo",
                variant=variant
            )
        ),
        "chart_daily": ChartWidget(
            f"cb_daily_{variant}",
            AdminTrendChartStrategy(
                screen_id=SCREEN_ID,
                chart_key="daily_cash_flow",
                title=f"Evolución Diaria de Flujo {suffix}",
                icon="tabler:chart-line",
                variant=variant,
                layout_config={"height": 380}
            )
        ),
        "chart_donut": ChartWidget(
            f"cb_donut_{variant}",
            AdminDonutChartStrategy(
                screen_id=SCREEN_ID,
                chart_key="balance_by_bank",
                title=f"Saldo por Institución Bancaria {suffix}",
                icon="tabler:chart-pie",
                variant=variant,
                layout_config={"height": 400}
            )
        ),
    }

_widgets_consolidado = _bank_widgets("consolidado")
_widgets_pesos = _bank_widgets("pesos")
_widgets_dolares = _bank_widgets("dolares")

WIDGET_REGISTRY = {
    **{w.widget_id: w for w in _widgets_consolidado.values()},
    **{w.widget_id: w for w in _widgets_pesos.values()},
    **{w.widget_id: w for w in _widgets_dolares.values()},
}

def _widgets_by_variant(variant):
    if variant == "consolidado":
        return _widgets_consolidado
    if variant == "pesos":
        return _widgets_pesos
    return _widgets_dolares

def _banks_tab_content(ctx, variant, theme):
    
    widgets = _widgets_by_variant(variant)
    table_title = (
        "INGRESOS Y EGRESOS POR CONCEPTO (Consolidado)" if variant == "consolidado" else
        "INGRESOS Y EGRESOS POR CONCEPTO (MXN)" if variant == "pesos" else
        "INGRESOS Y EGRESOS POR CONCEPTO (USD)"
    )
    
    def _card(widget_content, h=None):
        style = {"overflow": "hidden", "height": h or "100%", "backgroundColor": "transparent"}
        return dmc.Paper(
            p="xs", radius="md", withBorder=True, shadow=None,
            style=style, children=widget_content
        )
    
    return [

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "0.8rem",
                "marginBottom": "1.5rem"
            },
            children=[
                _card(widgets["kpi_initial"].render(ctx, theme=theme)),
                _card(widgets["kpi_incomes"].render(ctx, theme=theme)),
                _card(widgets["kpi_expenses"].render(ctx, theme=theme)),
                _card(widgets["kpi_final"].render(ctx, theme=theme))
            ]
        ),
        

        _card(widgets["chart_daily"].render(ctx, h=380, theme=theme)),
        
        dmc.Space(h="md"),
        

        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(
                    span={"base": 12, "md": 5}, # type: ignore
                    children=[_card(widgets["chart_donut"].render(ctx, h=400, theme=theme))]
                ),
                dmc.GridCol(
                    span={"base": 12, "md": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            shadow="sm",
                            style={"backgroundColor": "transparent"},
                            children=[
                                dmc.Text(table_title, fw="bold", size="xs", c="dimmed", mb="md"), # type: ignore
                                dmc.ScrollArea(
                                    h=360,
                                    children=[
                                        AdminTableStrategy(
                                            SCREEN_ID,
                                            "income_expense_concepts",
                                            variant=variant
                                        ).render(ctx, theme=theme)
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]

def _render_admin_banks_body(ctx):
    theme = session.get("theme", "dark")
    
    return html.Div([
        dmc.Title("Administración - Bancos", order=3, mb="lg", c="dimmed"), # type: ignore
        dmc.Tabs(
            value="consolidado",
            children=[
                dmc.TabsList([
                    dmc.TabsTab("Consolidado", value="consolidado"),
                    dmc.TabsTab("Pesos", value="pesos"),
                    dmc.TabsTab("Dólares", value="dolares")
                ]),
                dmc.TabsPanel(
                    html.Div(_banks_tab_content(ctx, "consolidado", theme), style={"paddingTop": "1rem"}),
                    value="consolidado"
                ),
                dmc.TabsPanel(
                    html.Div(_banks_tab_content(ctx, "pesos", theme), style={"paddingTop": "1rem"}),
                    value="pesos"
                ),
                dmc.TabsPanel(
                    html.Div(_banks_tab_content(ctx, "dolares", theme), style={"paddingTop": "1rem"}),
                    value="dolares"
                )
            ]
        ),
        dmc.Space(h=50)
    ])
    
def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=60 * 60 * 1000,
        max_intervals=-1
    )
    
    filters = create_filter_section(
        year_id="bank-year",
        month_id="bank-month",
        default_month="enero",
        additional_filters=[
            {"id": "bank-empresa", "label": "Empresa Área", "data": ["Todas"], "value": "Todas"},
            {"id": "bank-institucion", "label": "Institución Bancaria", "data": ["Todas"], "value": "Todas"}
        ]
    )
    
    return dmc.Container(
        fluid=True,
        px="md",
        children=[
            dcc.Store(id="bank-load-trigger", data={"loaded": True}),
            *refresh_components,
            create_smart_drawer("bank-drawer"),
            filters,
            html.Div(id="admin-banks-body", children=skeleton_admin_banks())
        ]
    )

FILTER_IDS = ["bank-year", "bank-month", "bank-empresa", "bank-institucion"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="admin-banks-body",
    render_body=_render_admin_banks_body,
    filter_ids=FILTER_IDS
)

register_drawer_callback(
    drawer_id="bank-drawer", 
    widget_registry=WIDGET_REGISTRY, 
    screen_id=SCREEN_ID, 
    filter_ids=FILTER_IDS
)