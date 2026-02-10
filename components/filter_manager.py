import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

def create_filter_section(
    year_id: str,
    month_id: str,
    year_options=None,
    default_year="2026",
    default_month="enero",
    additional_filters=None
):
    if year_options is None:
        year_options = ["2026", "2025", "2024"]

    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    year_month_grid = dmc.Grid(
        align="center",
        gutter="sm",
        mb="xs" if additional_filters else 0,
        children=[
            dmc.GridCol(
                span="content",
                children=[
                    dmc.Select(
                        id=year_id,
                        data=year_options,
                        value=default_year,
                        variant="filled",
                        style={"width": "100px"},
                        allowDeselect=False,
                        size="sm"
                    )
                ]
            ),
            dmc.GridCol(
                span="auto",
                children=[
                    dmc.ScrollArea(
                        w="100%",
                        type="scroll",
                        scrollbarSize=6,
                        offsetScrollbars=True, # type: ignore
                        children=[
                            dmc.SegmentedControl(
                                id=month_id,
                                value=default_month.lower(),
                                color="blue",
                                radius="md",
                                size="sm",
                                fullWidth=True,
                                style={"minWidth": "800px"},
                                data=[{"label": m, "value": m.lower()} for m in months] # type: ignore
                            )
                        ]
                    )
                ]
            )
        ]
    )

    additional_grid = None
    if additional_filters:
        num_filters = len(additional_filters)
        if num_filters <= 3:
            cols = {"base": 2, "md": num_filters}
        elif num_filters <= 6:
            cols = {"base": 2, "md": 3, "lg": num_filters}
        else:
            cols = {"base": 2, "md": 4, "lg": 6}

        filter_selects = [
            dmc.Select(
                id=f["id"],
                label=f["label"],
                data=f["data"],
                value=f.get("value", f["data"][0] if f["data"] else None),
                size=f.get("size", "xs")
            )
            for f in additional_filters
        ]

        additional_grid = dmc.SimpleGrid(
            cols=cols, # type: ignore
            spacing="xs",
            children=filter_selects
        )

    filter_content = html.Div([year_month_grid, additional_grid])

    return dmc.Accordion(
        value="filtros",
        variant="contained",
        radius="md",
        mb="lg",
        children=[
            dmc.AccordionItem(
                value="filtros",
                children=[
                    dmc.AccordionControl(
                        dmc.Group([
                            DashIconify(icon="tabler:filter"),
                            dmc.Text("Filtros y Controles")
                        ]),
                        h=40
                    ),
                    dmc.AccordionPanel(filter_content)
                ]
            )
        ]
    )

def create_operational_filters(prefix="ops"):
    return create_filter_section(
        year_id=f"{prefix}-year",
        month_id=f"{prefix}-month",
        default_month="enero",
        additional_filters=[
            {"id": f"{prefix}-empresa", "label": "Empresa Área", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-clasificacion", "label": "Clasificación", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-cliente", "label": "Cliente", "data": ["Todos"], "value": "Todos"},
            {"id": f"{prefix}-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-operador", "label": "Operador", "data": ["Todas"], "value": "Todas"}
        ]
    )

def create_administration_filters(prefix="admin", num_filters=4):
    filters = [
        {"id": f"{prefix}-empresa", "label": "Empresa Área", "data": ["Todas"], "value": "Todas"}
    ]

    if num_filters >= 2:
        filters.append({"id": f"{prefix}-tipo", "label": "Tipo Operación", "data": ["Todas"], "value": "Todas"})
    if num_filters >= 3:
        filters.append({"id": f"{prefix}-cliente", "label": "Cliente", "data": ["Todas"], "value": "Todas"})
    if num_filters >= 4:
        filters.append({"id": f"{prefix}-status", "label": "Estatus", "data": ["Todas"], "value": "Todas"})

    return create_filter_section(
        year_id=f"{prefix}-year",
        month_id=f"{prefix}-month",
        additional_filters=filters
    )

def create_workshop_filters(prefix="workshop"):
    return create_filter_section(
        year_id=f"{prefix}-year",
        month_id=f"{prefix}-month",
        year_options=["2025"],
        default_month="julio",
        additional_filters=[
            {"id": f"{prefix}-empresa", "label": "Empresa/Área", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-unidad", "label": "Unidad", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-tipo-op", "label": "Tipo Operación", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-clasificacion", "label": "Clasificación", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-razon", "label": "Razón Reparación", "data": ["Todas"], "value": "Todas"},
            {"id": f"{prefix}-motor", "label": "Tipo Motor", "data": ["Todas"], "value": "Todas"}
        ]
    )

def get_filter_ids(prefix, additional_count=5):
    ids = [f"{prefix}-year", f"{prefix}-month"]
    
    if prefix in ["workshop", "avail", "pur", "inv"]:
        workshop_filters = ["empresa", "unidad", "tipo-op", "clasificacion", "razon", "motor"]
        for f in workshop_filters:
            ids.append(f"{prefix}-{f}")
    else:
        common_additional = ["empresa", "clasificacion", "cliente", "unidad", "operador"]
        for i in range(min(additional_count, len(common_additional))):
            ids.append(f"{prefix}-{common_additional[i]}")
            
    return ids