from flask import session
import dash
from dash import html
import dash_mantine_components as dmc

from services.data_manager import data_manager
from components.visual_widget import ChartWidget
from components.smart_widget import SmartWidget
from components.modal_manager import create_smart_modal, register_modal_callback
from components.filter_manager import create_filter_section
from strategies.administration import (
    AdminKPIStrategy, AdminTrendChartStrategy,
    AdminDonutChartStrategy, AdminTableStrategy
)

dash.register_page(__name__, path="/admin-banks", title="Bancos")

SCREEN_ID = "administration-banks"

# Títulos por variante: Consolidado, Pesos (MXN), Dólares (USD)
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
                variant=variant
            )
        ),
        "chart_donut": ChartWidget(
            f"cb_donut_{variant}",
            AdminDonutChartStrategy(
                screen_id=SCREEN_ID,
                chart_key="balance_by_bank",
                title=f"Saldo por Institución Bancaria {suffix}",
                icon="tabler:chart-pie",
                variant=variant
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
    """Devuelve el diccionario de widgets preconstruidos para la variante."""
    if variant == "consolidado":
        return _widgets_consolidado
    if variant == "pesos":
        return _widgets_pesos
    return _widgets_dolares


def _banks_tab_content(ctx, variant):
    """Contenido de cada tab por variante (Consolidado, Pesos, Dólares)."""
    widgets = _widgets_by_variant(variant)
    table_title = "INGRESOS Y EGRESOS POR CONCEPTO (Consolidado)" if variant == "consolidado" else (
        "INGRESOS Y EGRESOS POR CONCEPTO (MXN)" if variant == "pesos" else "INGRESOS Y EGRESOS POR CONCEPTO (USD)"
    )
    return [
        dmc.SimpleGrid(
            cols={"base": 1, "sm": 2, "lg": 4}, # type: ignore
            spacing="md",
            mb="xl",
            children=[
                widgets["kpi_initial"].render(ctx),
                widgets["kpi_incomes"].render(ctx),
                widgets["kpi_expenses"].render(ctx),
                widgets["kpi_final"].render(ctx)
            ]
        ),
        dmc.Paper(
            p="md",
            withBorder=True,
            mb="xl",
            shadow="sm",
            children=[widgets["chart_daily"].render(ctx, h=380)]
        ),
        dmc.Grid(
            gutter="lg",
            children=[
                dmc.GridCol(
                    span={"base": 12, "md": 5}, # type: ignore
                    children=[widgets["chart_donut"].render(ctx, h=400)]
                ),
                dmc.GridCol(
                    span={"base": 12, "md": 7}, # type: ignore
                    children=[
                        dmc.Paper(
                            p="md",
                            withBorder=True,
                            shadow="sm",
                            children=[
                                dmc.Text(
                                    table_title,
                                    fw="bold",
                                    size="xs",
                                    c="dimmed", # type: ignore
                                    mb="md"
                                ),
                                dmc.ScrollArea(
                                    h=360,
                                    children=[
                                        AdminTableStrategy(
                                            SCREEN_ID,
                                            "income_expense_concepts",
                                            variant=variant
                                        ).render(ctx)
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
                    html.Div(_banks_tab_content(ctx, "consolidado"), style={"paddingTop": "1rem"}),
                    value="consolidado"
                ),
                dmc.TabsPanel(
                    html.Div(_banks_tab_content(ctx, "pesos"), style={"paddingTop": "1rem"}),
                    value="pesos"
                ),
                dmc.TabsPanel(
                    html.Div(_banks_tab_content(ctx, "dolares"), style={"paddingTop": "1rem"}),
                    value="dolares"
                )
            ]
        ),
        dmc.Space(h=50)
    ])

def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    
    ctx = data_manager.get_screen(SCREEN_ID, use_cache=True, allow_stale=True)
    refresh_components, _ = data_manager.dash_refresh_components(
        SCREEN_ID,
        interval_ms=800,
        max_intervals=1
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
        p="md",
        children=[
            create_smart_modal("bank-modal"),
            *refresh_components,
            filters,
            html.Div(id="admin-banks-body", children=_render_admin_banks_body(ctx))
        ]
    )

FILTER_IDS = ["bank-year", "bank-month", "bank-empresa", "bank-institucion"]

data_manager.register_dash_refresh_callbacks(
    screen_id=SCREEN_ID,
    body_output_id="admin-banks-body",
    render_body=_render_admin_banks_body,
    filter_ids=FILTER_IDS
)

register_modal_callback("bank-modal", WIDGET_REGISTRY, SCREEN_ID)