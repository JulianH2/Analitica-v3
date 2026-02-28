import dash_mantine_components as dmc
from dash import html, Output, Input, State, callback, no_update
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


def _build_filters_modal_content(additional_filters, checkbox_filters, apply_btn_id=None):
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
                        color="blue", size="sm",
                    )
                    for cb in checkbox_filters
                ],
            )
        ]

    apply_btn = []
    if apply_btn_id:
        apply_btn = [
            dmc.Divider(my="md"),
            dmc.Button(
                id=apply_btn_id,
                children=dmc.Group(gap=6, wrap="nowrap", children=[
                    DashIconify(icon="tabler:search", width=15),
                    html.Span("Aplicar filtros"),
                ]),
                fullWidth=True,
                size="sm",
                radius="md",
                color="blue",
                variant="filled",
            ),
        ]

    return html.Div(children=extra + checks + apply_btn)


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

    filter_modal_id = f"{year_id}-filter-modal"
    btn_filtro_id   = f"{year_id}-btn-filtro"

    n_extra      = len(additional_filters) if additional_filters else 0
    apply_btn_id = f"{year_id}-apply-btn"

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

    # Inline select styles — unstyled so they blend into the pill container
    _inline_input = {
        "fontWeight": 700,
        "fontSize": "13px",
        "cursor": "pointer",
        "padding": "0 2px",
        "height": "22px",
        "minHeight": "22px",
        "border": "none",
        "background": "transparent",
        "fontFamily": Typography.FAMILY,
    }

    toolbar = dmc.Group(
        justify="flex-end",
        gap="xs",
        mb="lg",
        children=[
            # Date pill with inline year + month selects
            html.Div(
                className="zam-pill",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "4px",
                    "padding": "0 8px 0 10px",
                },
                children=[
                    DashIconify(icon="tabler:calendar", width=13, color=Colors.CHART_BLUE),
                    dmc.Select(
                        id=year_id,
                        data=year_options,
                        value=default_year,
                        allowDeselect=False,
                        size="xs",
                        w=62,
                        variant="unstyled",
                        comboboxProps={"zIndex": 9999},
                        styles={"input": _inline_input},
                    ),
                    html.Span("·", style={"color": "#888", "fontSize": "12px", "userSelect": "none"}),
                    dmc.Select(
                        id=month_id,
                        data=MONTHS_FULL,
                        value=default_month.lower(),
                        allowDeselect=False,
                        size="xs",
                        w=88,
                        variant="unstyled",
                        comboboxProps={"zIndex": 9999},
                        styles={"input": {**_inline_input, "textTransform": "capitalize"}},
                    ),
                ],
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

    filter_modal = dmc.Modal(
        id=filter_modal_id,
        title=dmc.Group(
            gap="xs",
            children=[
                DashIconify(icon="tabler:adjustments-horizontal", width=18, color=Colors.CHART_BLUE),
                dmc.Text("Filtros", fw=700, size="sm"),  # type: ignore
            ]
        ),
        centered=True,
        size="sm",
        padding="xl",
        radius="lg",
        children=_build_filters_modal_content(
            additional_filters=additional_filters,
            checkbox_filters=checkbox_filters,
            apply_btn_id=apply_btn_id,
        ),
    )

    return html.Div([toolbar, filter_modal])


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
    filter_modal_id = f"{year_id}-filter-modal"
    btn_filtro_id   = f"{year_id}-btn-filtro"
    apply_btn_id    = f"{year_id}-apply-btn"

    @callback(
        Output(filter_modal_id, "opened"),
        Input(btn_filtro_id, "n_clicks"),
        Input(apply_btn_id, "n_clicks"),
        State(filter_modal_id, "opened"),
        prevent_initial_call=True,
    )
    def _toggle_filter_modal(n_open, n_apply, is_open):
        from dash import ctx as dash_ctx
        if dash_ctx.triggered_id == apply_btn_id:
            return False
        return True

    @callback(
        Output("global-date-filter", "data", allow_duplicate=True),
        Input(year_id, "value"),
        Input(month_id, "value"),
        prevent_initial_call=True,
    )
    def _save_date(year_val, month_val):
        if year_val or month_val:
            return {
                "year": year_val or _get_current_year(),
                "month": month_val or _get_current_month(),
            }
        return no_update

    @callback(
        Output(year_id, "value"),
        Output(month_id, "value"),
        Input("url", "pathname"),
        State("global-date-filter", "data"),
        prevent_initial_call=True,
    )
    def _restore_date(pathname, store_data):
        if store_data and store_data.get("year") and store_data.get("month"):
            return store_data["year"], store_data["month"]
        return _get_current_year(), _get_current_month()
