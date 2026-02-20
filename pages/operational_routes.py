from flask import session
import dash
from dash import html, dcc, callback, Input, Output, State, no_update
import dash_mantine_components as dmc
import dash_ag_grid as dag
import plotly.graph_objects as go

from services.data_manager import data_manager
from components.drawer_manager import create_smart_drawer, register_drawer_callback
from components.filter_manager import create_filter_section, register_filter_modal_callback
from strategies.operational import OpsTableStrategy
from components.table_widget import TableWidget
from utils.helpers import safe_get
from design_system import Colors, ComponentSizes, Typography, Space
from dash_iconify import DashIconify

dash.register_page(__name__, path="/operational-routes", title="Análisis de Rutas")

SCREEN_ID = "operational-routes"
PREFIX = "or"

ADDITIONAL_FILTERS = [
    {
        "id": "route-d_viaje__ind_cargado",
        "label": "Vista",
        "type": "segmented",
        "data": [{"label": "Vacíos", "value": "0"}, {"label": "Cargados", "value": "1"}],
        "value": "0",
    },
    {"id": "route-empresa",        "label": "Empresa\\Área",    "type": "select", "data": ["Todas"], "value": "Todas"},
    {"id": "route-clasificacion",  "label": "Clasificación",    "type": "select", "data": ["Todas"], "value": "Todas"},
    {"id": "route-cliente",        "label": "Cliente",          "type": "select", "data": ["Todas"], "value": "Todas"},
    {"id": "route-unidad",         "label": "Unidad",           "type": "select", "data": ["Todas"], "value": "Todas"},
    {"id": "route-operador",       "label": "Operador",         "type": "select", "data": ["Todas"], "value": "Todas"},
    {"id": "route-ruta",           "label": "Ruta",             "type": "select", "data": ["Todas"], "value": "Todas"},
    {"id": "route-origen",         "label": "Origen",           "type": "select", "data": ["Todas"], "value": "Todas"},
    {"id": "route-destino",        "label": "Destino",          "type": "select", "data": ["Todas"], "value": "Todas"},
]

CHECKBOX_FILTERS = [
    {"id": "route-foranea",  "label": "Ruta Foránea"},
    {"id": "route-local",    "label": "Ruta Local"},
    {"id": "route-normal",   "label": "Ruta Normal"},
    {"id": "route-circuito", "label": "Ruta Circuito"},
]

FILTER_IDS = (
    ["route-year", "route-month"]
    + [f["id"] for f in ADDITIONAL_FILTERS]
)

t_main = TableWidget(
    f"{PREFIX}_main",
    OpsTableStrategy(SCREEN_ID, "main_routes", title="Detalle de Rutas")
)

WIDGET_REGISTRY = {
    f"{PREFIX}_main": t_main,
}

COLOR_PALETTE = [
    "#4C6EF5", "#F03E3E", "#12B886", "#F59F00", "#7950F2",
    "#E67700", "#1C7ED6", "#D6336C", "#2F9E44", "#C2255C",
    "#099268", "#C92A2A", "#1864AB", "#5C940D", "#862E9C",
    "#E8590C", "#0B7285", "#A61E4D", "#364FC7", "#087F5B",
]


def _parse_pos(pos_str):
    try:
        parts = str(pos_str or "").split(",")
        if len(parts) == 2:
            lat, lon = float(parts[0].strip()), float(parts[1].strip())
            if -90 <= lat <= 90 and -180 <= lon <= 180 and abs(lat) + abs(lon) > 0.001:
                return lat, lon
    except Exception:
        pass
    return None, None


def _build_map_figure(ctx, theme, selected_rk=None, show_legend=True):
    node = safe_get(ctx, ["operational", "dashboard", "tables", "main_routes"])
    if not node:
        return _empty_map(theme)

    headers = node.get("headers", [])
    rows = node.get("rows", [])
    if not headers or not rows:
        return _empty_map(theme)

    hmap = {h: i for i, h in enumerate(headers)}
    idx_ruta = hmap.get("Ruta")
    idx_origen = hmap.get("Origen")
    idx_dest = hmap.get("Destino")
    idx_po = hmap.get("Pos. Origen")
    idx_pd = hmap.get("Pos. Destino")

    if idx_po is None or idx_pd is None:
        return _empty_map(theme)

    def _g(row, idx):
        return row[idx] if idx is not None and idx < len(row) else ""

    fig = go.Figure()
    all_lats, all_lons = [], []
    sel_lats, sel_lons = [], []

    for i, row in enumerate(rows):
        lat_o, lon_o = _parse_pos(_g(row, idx_po))
        lat_d, lon_d = _parse_pos(_g(row, idx_pd))
        if not (lat_o and lon_o and lat_d and lon_d):
            continue

        ruta = str(_g(row, idx_ruta) or f"Ruta {i+1}").strip()
        origen = str(_g(row, idx_origen)).strip()
        dest = str(_g(row, idx_dest)).strip()
        color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
        is_sel = (selected_rk is not None and i == selected_rk)

        all_lats += [lat_o, lat_d]
        all_lons += [lon_o, lon_d]
        if is_sel:
            sel_lats += [lat_o, lat_d]
            sel_lons += [lon_o, lon_d]

        fig.add_trace(go.Scattermapbox(
            lat=[lat_o, lat_d], lon=[lon_o, lon_d],
            mode="lines+markers", name=ruta,
            customdata=[[origen, dest, ruta], [origen, dest, ruta]],
            hovertemplate="<b>%{customdata[2]}</b><br>%{customdata[0]} → %{customdata[1]}<extra></extra>",
            line=dict(width=5 if is_sel else 2.5, color="#FFD700" if is_sel else color),
            marker=dict(size=12 if is_sel else 8, color="#FFD700" if is_sel else color),
            opacity=1.0 if is_sel else (0.35 if selected_rk is not None else 1.0),
        ))

    if not all_lats:
        return _empty_map(theme)

    if sel_lats:
        c_lat = (min(sel_lats) + max(sel_lats)) / 2
        c_lon = (min(sel_lons) + max(sel_lons)) / 2
        rng = max(max(sel_lats) - min(sel_lats), max(sel_lons) - min(sel_lons))
        zoom = 5 if rng > 5 else 8 if rng > 1 else 11
    else:
        c_lat = (min(all_lats) + max(all_lats)) / 2
        c_lon = (min(all_lons) + max(all_lons)) / 2
        rng = max(max(all_lats) - min(all_lats), max(all_lons) - min(all_lons))
        zoom = 5 if rng > 5 else 7 if rng > 2 else 9

    is_dark = theme == "dark"
    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=c_lat, lon=c_lon), zoom=zoom),
        margin=dict(l=0, r=0, t=0, b=0), height=620, autosize=True,
        paper_bgcolor="rgba(0,0,0,0)", showlegend=show_legend,
        legend=dict(
            bgcolor="rgba(25,25,25,0.88)" if is_dark else "rgba(255,255,255,0.92)",
            font=dict(color="#fff" if is_dark else "#1A1B1E", size=10),
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            itemwidth=30, borderwidth=1,
            bordercolor="rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)",
        ),
    )
    return fig


def _empty_map(theme):
    fig = go.Figure()
    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=23.63, lon=-102.55), zoom=4),
        margin=dict(l=0, r=0, t=0, b=0), height=620,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text="Sin datos de coordenadas", x=0.5, y=0.5,
                          xref="paper", yref="paper", showarrow=False,
                          font=dict(size=16, color="gray"))],
    )
    return fig


def _build_table(ctx, theme):
    node = safe_get(ctx, ["operational", "dashboard", "tables", "main_routes"])
    if not node:
        return dmc.Center(style={"height": 400}, children=[dmc.Text("Sin datos disponibles", size="sm", c="dimmed")]) # type: ignore

    headers = node.get("headers", [])
    rows = node.get("rows", [])
    if not headers or not rows:
        return dmc.Center(style={"height": 400}, children=[dmc.Text("Sin rutas para los filtros seleccionados", size="sm", c="dimmed")]) # type: ignore

    is_dark = theme == "dark"
    column_defs = []
    for i, h in enumerate(headers):
        col_def = {"field": f"col_{i}", "headerName": h, "sortable": True, "resizable": True, "suppressMenu": True, "tooltipField": f"col_{i}"}
        if h == "No.":
            col_def.update({"width": 65, "flex": 0, "pinned": "left"})
        elif h == "Ruta":
            col_def.update({"minWidth": 200, "flex": 2})
        elif h in ("Pos. Origen", "Pos. Destino"):
            col_def.update({"minWidth": 240, "flex": 1})
        else:
            col_def.update({"minWidth": 110, "flex": 1})
        column_defs.append(col_def)

    row_data = []
    for i, row in enumerate(rows):
        d = {"_row_index": int(i)}
        for j, val in enumerate(row):
            d[f"col_{j}"] = val if val is not None else "" # type: ignore
        row_data.append(d)

    grid = dag.AgGrid(
        id="routes-ag-grid", rowData=row_data, columnDefs=column_defs,
        defaultColDef={"sortable": True, "resizable": True, "filter": False},
        dashGridOptions={"pagination": True, "paginationPageSize": 20,
                         "rowHeight": ComponentSizes.TABLE_ROW_HEIGHT,
                         "headerHeight": ComponentSizes.TABLE_HEADER_HEIGHT,
                         "suppressFieldDotNotation": True, "rowSelection": "single", "animateRows": True},
        style={"height": "520px", "width": "100%"},
        className="ag-theme-alpine-dark" if is_dark else "ag-theme-alpine",
        selectedRows=[],
    )

    search_bar = dmc.Group(justify="space-between", mt=Space.SM, children=[
        dmc.TextInput(id="routes-quick-search", placeholder="Buscar ruta...", size="xs", radius="xl",
                      style={"width": "240px"},
                      styles={"input": {"backgroundColor": "rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.03)",
                                        "color": Colors.TEXT_DARK if is_dark else Colors.TEXT_LIGHT}}),
        dmc.Text(f"{len(row_data)} rutas", size="xs", c="dimmed"), # type: ignore
    ])
    return html.Div([grid, search_bar])


def skeleton_ops_routes():
    from components.skeleton import skeleton_chart, skeleton_table, skeleton_box
    return html.Div(children=[
        skeleton_box("24px", "200px", "mb-sm"),
        dmc.Paper(p="md", withBorder=True, mb="xl", children=[skeleton_chart("640px")]),
        dmc.Paper(p="md", withBorder=True, children=[skeleton_table(12, 6)]),
    ])


def _render_ops_routes_body(ctx):
    theme = session.get("theme", "dark")
    return html.Div([
        dmc.Paper(
            p="md", withBorder=True, mb="xl",
            style={"backgroundColor": "transparent", "position": "relative"},
            children=[
                dmc.Group(justify="space-between", mb="xs", children=[
                    dmc.Text("MAPA ANÁLISIS DE RUTAS", fw="bold", size="xs", c="gray"),
                    dmc.Tooltip(label="Mostrar / ocultar leyenda", position="left", children=[
                        dmc.ActionIcon(id="routes-legend-toggle", children=DashIconify(icon="tabler:list", width=16),
                                       variant="light", color="blue", size="sm", radius="md"),
                    ]),
                ]),
                dcc.Graph(id="routes-map-graph", figure=_build_map_figure(ctx, theme, show_legend=True),
                          style={"height": "620px", "width": "100%"},
                          config={"displayModeBar": True, "responsive": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}),
            ],
        ),
        dmc.Paper(
            p="md", withBorder=True, style={"backgroundColor": "transparent"},
            children=[
                dmc.Group(justify="space-between", mb="xs", children=[
                    dmc.Text("DETALLE DE RUTAS Y UTILIZACIÓN", fw="bold", size="xs", c="gray"),
                    dmc.Text("Clic en una fila → zoom en mapa", size="xs", c="dimmed", fs="italic"), # type: ignore
                ]),
                _build_table(ctx, theme),
            ],
        ),
        dmc.Space(h=50),
        dcc.Store(id="routes-ctx-store", data=ctx),
        dcc.Store(id="routes-legend-store", data=True),
    ])


def layout():
    if not session.get("user"):
        return dmc.Text("No autorizado...")
    refresh_components, _ = data_manager.dash_refresh_components(SCREEN_ID, interval_ms=800, max_intervals=1)
    filters = create_filter_section(year_id="route-year", month_id="route-month",
                                    additional_filters=ADDITIONAL_FILTERS, checkbox_filters=CHECKBOX_FILTERS)
    return dmc.Container(fluid=True, px="md", children=[
        dcc.Store(id="route-load-trigger", data={"loaded": True}),
        *refresh_components,
        create_smart_drawer("route-drawer"),
        filters,
        html.Div(id="ops-routes-body", children=skeleton_ops_routes()),
    ])


data_manager.register_dash_refresh_callbacks(screen_id=SCREEN_ID, body_output_id="ops-routes-body",
                                             render_body=_render_ops_routes_body, filter_ids=FILTER_IDS)


@callback(Output("routes-map-graph", "figure"), Output("routes-legend-store", "data"),
          Input("routes-legend-toggle", "n_clicks"), State("routes-legend-store", "data"),
          State("routes-ctx-store", "data"), State("routes-map-graph", "figure"), prevent_initial_call=True)
def _toggle_legend(n_clicks, legend_visible, ctx, current_fig):
    theme = session.get("theme", "dark")
    if not n_clicks:
        return no_update, no_update
    new_visible = not legend_visible
    if ctx:
        return _build_map_figure(ctx, theme, show_legend=new_visible), new_visible
    if current_fig:
        import copy
        fig_copy = copy.deepcopy(current_fig)
        fig_copy["layout"]["showlegend"] = new_visible
        return fig_copy, new_visible
    return no_update, new_visible


@callback(Output("routes-map-graph", "figure", allow_duplicate=True), Input("routes-ag-grid", "selectedRows"),
          State("routes-ctx-store", "data"), State("routes-legend-store", "data"), prevent_initial_call=True)
def _on_row_selected(selected_rows, ctx, legend_visible):
    theme = session.get("theme", "dark")
    if not ctx:
        return no_update
    show_legend = legend_visible if legend_visible is not None else True
    if not selected_rows:
        return _build_map_figure(ctx, theme, selected_rk=None, show_legend=show_legend)
    row_index = selected_rows[0].get("_row_index")
    if row_index is None:
        return no_update
    return _build_map_figure(ctx, theme, selected_rk=row_index, show_legend=show_legend)


@callback(Output("routes-ag-grid", "dashGridOptions"), Input("routes-quick-search", "value"), prevent_initial_call=True)
def _on_search(search_val):
    return {"quickFilterText": search_val or ""}


for _cb in CHECKBOX_FILTERS:
    @callback(Output(_cb["id"], "variant"), Output(_cb["id"], "color"),
              Input(_cb["id"], "n_clicks"), prevent_initial_call=True)
    def _toggle_btn(n_clicks):
        is_active = (n_clicks or 0) % 2 == 1
        return ("filled", "blue") if is_active else ("default", "gray")


register_drawer_callback(drawer_id="route-drawer", widget_registry=WIDGET_REGISTRY,
                         screen_id=SCREEN_ID, filter_ids=FILTER_IDS)

register_filter_modal_callback("route-year")