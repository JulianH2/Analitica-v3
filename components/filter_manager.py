import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify
from design_system import DesignSystem as DS, Typography, BorderRadius

def create_filter_section(
    year_id: str,
    month_id: str,
    year_options=None,
    default_year="2026",
    default_month="enero",
    additional_filters=None,
    checkbox_filters=None,
    theme="dark",
    minimal=False,
):
    if year_options is None:
        year_options = ["2026", "2025", "2024"]

    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]

    is_dark = theme == "dark"
    bg_input = DS.TRANSPARENT
    border_color = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"
    text_main = DS.TEXT_DARK if is_dark else DS.TEXT_LIGHT

    year_month_grid = dmc.Group(
        gap="md",
        mb="md" if (additional_filters or checkbox_filters) else 0,
        wrap="nowrap",
        children=[
            dmc.Group(
                gap="xs",
                wrap="nowrap",
                children=[
                    DashIconify(icon="tabler:calendar", width=16, color=DS.CHART_BLUE),
                    dmc.Select(
                        id=year_id,
                        data=year_options,
                        value=default_year,
                        variant="filled",
                        w=100,
                        allowDeselect=False,
                        size="xs",
                        radius="md",
                        styles={
                            "input": {
                                "backgroundColor": bg_input,
                                "color": text_main,
                                "fontWeight": DS.TYPOGRAPHY["weights"]["bold"],
                                "fontSize": f"{DS.TYPOGRAPHY['sizes']['sm']}px",
                                "border": f"1px solid {border_color}",
                                "backdropFilter": "none",
                            }
                        },
                    ),
                ],
            ),
            dmc.ScrollArea(
                style={"flex": 1},
                type="scroll",
                scrollbarSize=6,
                offsetScrollbars=True, # type: ignore
                children=[
                    dmc.SegmentedControl(
                        id=month_id,
                        value=default_month.lower(),
                        color="blue",
                        radius="md",
                        size="xs",
                        fullWidth=True,
                        style={"minWidth": "800px"},
                        data=[{"label": m, "value": m.lower()} for m in months], # type: ignore
                        styles={
                            "root": {
                                "backgroundColor": bg_input,
                                "padding": "3px",
                                "border": f"1px solid {border_color}",
                                "backdropFilter": "none",
                            },
                            "label": {
                                "fontSize": f"{DS.TYPOGRAPHY['sizes']['xs']}px",
                                "fontWeight": DS.TYPOGRAPHY["weights"]["semibold"],
                                "padding": "6px 10px",
                            },
                            "indicator": {
                                "backgroundColor": DS.CHART_BLUE,
                                "boxShadow": "0 2px 8px rgba(59, 130, 246, 0.3)",
                            },
                        },
                    )
                ],
            ),
        ],
    )

    additional_section = None
    if additional_filters:
        num_filters = len(additional_filters)
        if num_filters <= 3:
            cols = {"base": 1, "sm": 2, "md": num_filters}
        elif num_filters <= 6:
            cols = {"base": 1, "sm": 2, "md": 3, "lg": num_filters}
        else:
            cols = {"base": 1, "sm": 2, "md": 3, "lg": 6}

        filter_controls = []
        for f in additional_filters:
            f_type = f.get("type", "select")

            if f_type == "segmented":
                filter_controls.append(
                    dmc.SegmentedControl(
                        id=f["id"],
                        data=f.get("data", []),
                        value=f.get("value"),
                        size="xs",
                        radius="md",
                        fullWidth=True,
                        styles={
                            "root": {
                                "backgroundColor": bg_input,
                                "border": f"1px solid {border_color}",
                                "backdropFilter": "none",
                                "padding": "3px",
                            },
                            "indicator": {"backgroundColor": DS.CHART_BLUE},
                            "label": {
                                "fontSize": f"{DS.TYPOGRAPHY['sizes']['xs']}px",
                                "fontWeight": DS.TYPOGRAPHY["weights"]["semibold"],
                            },
                        },
                    )
                )

            elif f_type == "select":
                filter_controls.append(
                    dmc.Select(
                        id=f["id"],
                        label=f.get("label", ""),
                        data=f.get("data", []),
                        value=f.get("value", f["data"][0] if f.get("data") else None),
                        size="xs",
                        radius="md",
                        styles={
                            "label": {
                                "fontSize": f"{DS.TYPOGRAPHY['sizes']['xs']}px",
                                "fontWeight": DS.TYPOGRAPHY["weights"]["semibold"],
                                "color": text_main,
                                "marginBottom": "6px",
                            },
                            "input": {
                                "fontSize": f"{DS.TYPOGRAPHY['sizes']['xs']}px",
                                "backgroundColor": bg_input,
                                "borderColor": border_color,
                                "borderRadius": f"{BorderRadius.MD}",
                                "backdropFilter": "none",
                            },
                        },
                    )
                )

        additional_section = dmc.SimpleGrid(cols=cols, spacing="sm", children=filter_controls) # type: ignore

    checkbox_section = None
    if checkbox_filters:
        checkbox_section = dmc.Group(
            gap="md",
            mt="sm",
            children=[
                dmc.Checkbox(
                    label=cb["label"],
                    id=cb["id"],
                    color="blue",
                    size="xs",
                    radius="sm",
                )
                for cb in checkbox_filters
            ],
        )

    filter_content = html.Div([year_month_grid, additional_section, checkbox_section])

    if minimal:
        return dmc.Paper(
            p="sm",
            radius="md",
            mb="md",
            style={
                "backgroundColor": DS.TRANSPARENT,
                "border": f"1px solid {border_color}",
                "backdropFilter": "none",
            },
            children=filter_content,
        )

    return dmc.Accordion(
        value="filtros",
        variant="contained",
        radius="md",
        mb="lg",
        styles={
            "root": {
                "backgroundColor": DS.TRANSPARENT,
                "border": f"1px solid {border_color}",
                "backdropFilter": "none",
            },
            "control": {
                "height": "48px",
                "fontSize": f"{DS.TYPOGRAPHY['sizes']['sm']}px",
                "fontWeight": DS.TYPOGRAPHY["weights"]["bold"],
                "backgroundColor": DS.TRANSPARENT,
                "borderRadius": f"{BorderRadius.MD}",
                "&:hover": {"backgroundColor": "rgba(59, 130, 246, 0.1)"},
            },
            "item": {"borderRadius": f"{BorderRadius.MD}", "border": "none", "backgroundColor": DS.TRANSPARENT},
            "panel": {"padding": "16px", "paddingTop": "20px", "backgroundColor": DS.TRANSPARENT},
        },
        children=[
            dmc.AccordionItem(
                value="filtros",
                children=[
                    dmc.AccordionControl(
                        dmc.Group(
                            gap="sm",
                            children=[
                                DashIconify(
                                    icon="tabler:adjustments-horizontal",
                                    width=18,
                                    color=DS.CHART_BLUE,
                                ),
                                dmc.Text("Filtros", fw="bold", size="sm"),
                            ],
                        )
                    ),
                    dmc.AccordionPanel(filter_content),
                ],
            )
        ],
    )

def create_operational_filters(prefix="ops", theme="dark", minimal=False):
    return create_filter_section(
        year_id=f"{prefix}-year",
        month_id=f"{prefix}-month",
        default_month="enero",
        theme=theme,
        minimal=minimal,
        additional_filters=[
            {"id": f"{prefix}-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-clasificacion", "label": "Clasificación", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-cliente", "label": "Cliente", "data": ["Todos"], "value": "Todos"},
            {"id": f"{prefix}-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"},
        ],
    )

def create_workshop_filters(prefix="workshop", theme="dark", minimal=False):
    return create_filter_section(
        year_id=f"{prefix}-year",
        month_id=f"{prefix}-month",
        year_options=["2025"],
        default_month="julio",
        theme=theme,
        minimal=minimal,
        additional_filters=[
            {"id": f"{prefix}-empresa", "label": "Empresa", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-tipo-op", "label": "Tipo Op.", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-clasificacion", "label": "Clasificación", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-razon", "label": "Razón", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-motor", "label": "Motor", "data": ["Todos"], "value": "Todos"},
        ],
    )

def get_filter_ids(year_id, month_id, additional_filters=None):
    ids = [year_id, month_id]
    if additional_filters:
        ids += [f["id"] for f in additional_filters]
    return ids