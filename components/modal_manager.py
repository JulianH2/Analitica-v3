import dash
from dash import html, callback, Input, Output, ALL, no_update
import dash_mantine_components as dmc

def create_smart_modal(modal_id: str = "smart-modal"):
    return dmc.Modal(
        id=modal_id,
        size="xl",
        centered=True,
        children=[html.Div(id=f"{modal_id}-content")]
    )

def register_modal_callback(modal_id: str, widget_registry: dict, screen_id: str):
    from services.data_manager import data_manager

    @callback(
        Output(modal_id, "opened"),
        Output(modal_id, "title"),
        Output(f"{modal_id}-content", "children"),
        Input({"type": "open-smart-detail", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def handle_modal_click(n_clicks):
        if not dash.ctx.triggered or not any(n_clicks):
            return no_update, no_update, no_update

        if not dash.ctx.triggered_id:
            return no_update, no_update, no_update

        widget_id = dash.ctx.triggered_id.get("index")
        if not widget_id:
            return no_update, no_update, no_update

        widget = widget_registry.get(str(widget_id))
        if not widget:
            return no_update, no_update, no_update

        ctx = data_manager.get_screen(screen_id, use_cache=True, allow_stale=True)

        try:
            cfg = widget.strategy.get_card_config(ctx)
            title = cfg.get("title", "Detalle")
            detail = widget.strategy.render_detail(ctx)
            return True, title, detail
        except Exception as e:
            return True, "Error", dmc.Text(f"Error al cargar detalle: {str(e)}", c="red")

    return handle_modal_click
