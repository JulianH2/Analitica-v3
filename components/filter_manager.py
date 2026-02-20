import dash_mantine_components as dmc
from dash import html, Output, Input, State, callback
from dash_iconify import DashIconify
from design_system import Colors, Typography
from datetime import datetime


MONTHS_FULL = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
MONTHS_ABBR = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _get_current_month() -> str:
    return MONTHS_FULL[datetime.now().month - 1]


def _get_current_year() -> str:
    return str(datetime.now().year)


def _month_abbr(month_lower: str) -> str:
    try:
        return MONTHS_ABBR[MONTHS_FULL.index(month_lower.lower())]
    except ValueError:
        return "Ene"


def _build_date_modal_content(year_id, month_id, year_options, default_year, default_month):
    return dmc.Group(
        gap="sm",
        wrap="nowrap",
        align="flex-end",
        children=[
            html.Div(children=[
                html.Label("Año", className="zam-filter-label"),
                dmc.Select(
                    id=year_id,
                    data=year_options,
                    value=default_year,
                    allowDeselect=False,
                    size="sm",
                    radius="md",
                    w=110,
                    styles={"input": {
                        "fontWeight": 700,
                        "border": f"2px solid {Colors.CHART_BLUE}",
                    }},
                ),
            ]),
            html.Div(children=[
                html.Label("Mes", className="zam-filter-label"),
                dmc.Select(
                    id=month_id,
                    data=MONTHS_FULL,
                    value=default_month.lower(),
                    allowDeselect=False,
                    size="sm",
                    radius="md",
                    w=90,
                ),
            ]),
        ],
    )


def _build_filters_modal_content(additional_filters, checkbox_filters):
    extra = []
    if additional_filters:
        for f in additional_filters:
            f_type = f.get("type", "select")
            if f_type == "select":
                extra.append(html.Div(
                    style={"marginBottom": "14px"},
                    children=[
                        html.Label(f.get("label", ""), className="zam-filter-label"),
                        dmc.Select(
                            id=f["id"],
                            data=f.get("data", []),
                            value=f.get("value", f["data"][0] if f.get("data") else None),
                            size="sm",
                            radius="md",
                            clearable=True,
                            comboboxProps={"zIndex": 9999},
                        ),
                    ]
                ))
            elif f_type == "segmented":
                extra.append(html.Div(
                    style={"marginBottom": "14px"},
                    children=[
                        html.Label(f.get("label", ""), className="zam-filter-label"),
                        dmc.SegmentedControl(
                            id=f["id"],
                            data=f.get("data", []),
                            value=f.get("value"),
                            size="xs",
                            radius="md",
                            fullWidth=True,
                            color="blue",
                        ),
                    ]
                ))

    checks = []
    if checkbox_filters:
        checks = [
            dmc.Divider(my="md"),
            dmc.Stack(
                gap="sm",
                children=[
                    dmc.Checkbox(
                        label=cb["label"], id=cb["id"],
                        color="blue", size="sm", radius="sm",
                    )
                    for cb in checkbox_filters
                ],
            )
        ]

    return html.Div(children=extra + checks)



def create_filter_section(
    year_id: str,
    month_id: str,
    year_options=None,
    default_year=None,
    default_month=None,
    additional_filters=None,
    checkbox_filters=None,
    theme="dark",
    minimal=False,
):
    if default_year is None:
        default_year = _get_current_year()
    if default_month is None:
        default_month = _get_current_month()

    if year_options is None:
        cy = _get_current_year()
        year_options = [cy, str(int(cy) - 1), str(int(cy) - 2)]
    elif default_year not in year_options:
        year_options = [default_year] + list(year_options)

    date_modal_id   = f"{year_id}-date-modal"
    filter_modal_id = f"{year_id}-filter-modal"
    btn_mes_id      = f"{year_id}-btn-mes"
    btn_filtro_id   = f"{year_id}-btn-filtro"
    date_label_id   = f"{year_id}-date-label"

    n_extra = len(additional_filters) if additional_filters else 0
    date_label_init = f"{_month_abbr(default_month)} · {default_year}"

    _btn_styles = {
        "root": {
            "height": "34px",
            "padding": "0 12px",
            "fontWeight": 600,
            "fontSize": "13px",
            "fontFamily": Typography.FAMILY,
            "borderRadius": "6px",
            "cursor": "pointer",
        }
    }

    toolbar = dmc.Group(
        justify="flex-end",
        gap="xs",
        mb="lg",
        children=[
            html.Div(
                className="zam-pill",
                children=[
                    DashIconify(icon="tabler:calendar", width=13, color=Colors.CHART_BLUE),
                    html.Span(date_label_init, id=date_label_id),
                ],
            ),
            html.Div(className="zam-pill-divider"),
            dmc.Button(
                id=btn_mes_id,
                variant="subtle",
                size="xs",
                radius="md",
                className="zam-pill zam-pill-btn",
                styles=_btn_styles,
                children=dmc.Group(
                    gap=5,
                    wrap="nowrap",
                    children=[
                        html.Span("Mes"),
                        DashIconify(icon="tabler:chevron-down", width=13),
                    ],
                ),
            ),
            html.Div(className="zam-pill-divider"),
            dmc.Button(
                id=btn_filtro_id,
                variant="subtle",
                size="xs",
                radius="md",
                className=f"zam-pill zam-pill-btn {'zam-pill-active' if n_extra > 0 else ''}",
                styles=_btn_styles,
                children=dmc.Group(
                    gap=6,
                    wrap="nowrap",
                    children=[
                        DashIconify(icon="tabler:adjustments-horizontal", width=14),
                        html.Span("Filtro"),
                        dmc.Badge(
                            str(n_extra), size="xs", color="blue", variant="filled",
                        ) if n_extra > 0 else None,
                    ],
                ),
            ),
        ],
    )

    date_modal = dmc.Modal(
        id=date_modal_id,
        title=dmc.Group(
            gap="xs",
            children=[
                DashIconify(icon="tabler:calendar", width=18, color=Colors.CHART_BLUE),
                dmc.Text("Período", fw=700, size="sm"), # type: ignore
            ]
        ),
        centered=True,
        size="xs",
        padding="xl",
        radius="lg",
        children=_build_date_modal_content(
            year_id=year_id,
            month_id=month_id,
            year_options=year_options,
            default_year=default_year,
            default_month=default_month,
        ),
    )

    filter_modal = dmc.Modal(
        id=filter_modal_id,
        title=dmc.Group(
            gap="xs",
            children=[
                DashIconify(icon="tabler:adjustments-horizontal", width=18, color=Colors.CHART_BLUE),
                dmc.Text("Filtros", fw=700, size="sm"), # type: ignore
            ]
        ),
        centered=True,
        size="sm",
        padding="xl",
        radius="lg",
        children=_build_filters_modal_content(
            additional_filters=additional_filters,
            checkbox_filters=checkbox_filters,
        ),
    )

    return html.Div([toolbar, date_modal, filter_modal])


def create_operational_filters(prefix="ops", theme="dark", minimal=False):
    return create_filter_section(
        year_id=f"{prefix}-year",
        month_id=f"{prefix}-month",
        theme=theme,
        minimal=minimal,
        additional_filters=[
            {"id": f"{prefix}-empresa",        "label": "Empresa / Área",    "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-tipo-unidad",    "label": "Tipo Unidad",       "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-no-viaje",       "label": "No. Viaje",         "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-tipo-operacion", "label": "Tipo Operación",    "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-clasificacion",  "label": "Clasificación",     "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-cliente",        "label": "Cliente",           "data": ["Todos"], "value": "Todos"},
            {"id": f"{prefix}-unidad",         "label": "Unidad",            "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-operador",       "label": "Operador",          "data": ["Todas"], "value": "Todas"},
        ],
    )


def create_workshop_filters(prefix="workshop", theme="dark", minimal=False):
    return create_filter_section(
        year_id=f"{prefix}-year",
        month_id=f"{prefix}-month",
        theme=theme,
        minimal=minimal,
        additional_filters=[
            {"id": f"{prefix}-empresa",       "label": "Empresa / Área",              "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-unidad",        "label": "Unidad",                      "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-tipo-op",       "label": "Tipo Operación",              "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-clasificacion", "label": "Clasificación / Tipo Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-razon",         "label": "Tipo / Razón Reparación",     "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-motor",         "label": "Tipo Motor",                  "data": ["Todos"], "value": "Todos"},
        ],
    )


def get_filter_ids(year_id, month_id, additional_filters=None):
    ids = [year_id, month_id]
    if additional_filters:
        ids += [f["id"] for f in additional_filters]
    return ids


def register_filter_modal_callback(year_id: str):
    month_id        = year_id.replace("-year", "-month")
    date_modal_id   = f"{year_id}-date-modal"
    filter_modal_id = f"{year_id}-filter-modal"
    btn_mes_id      = f"{year_id}-btn-mes"
    btn_filtro_id   = f"{year_id}-btn-filtro"
    date_label_id   = f"{year_id}-date-label"

    @callback(
        Output(date_modal_id, "opened"),
        Input(btn_mes_id, "n_clicks"),
        State(date_modal_id, "opened"),
        prevent_initial_call=True,
    )
    def _toggle_date_modal(n, is_open):
        return True

    @callback(
        Output(filter_modal_id, "opened"),
        Input(btn_filtro_id, "n_clicks"),
        State(filter_modal_id, "opened"),
        prevent_initial_call=True,
    )
    def _toggle_filter_modal(n, is_open):
        return True

    @callback(
        Output(date_label_id, "children"),
        Input(year_id, "value"),
        Input(month_id, "value"),
        prevent_initial_call=False,
    )
    def _update_label(year_val, month_val):
        abbr = _month_abbr(month_val or _get_current_month())
        yr   = year_val or _get_current_year()
        return f"{abbr} · {yr}"