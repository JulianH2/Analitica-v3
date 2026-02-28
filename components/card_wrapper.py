import dash_mantine_components as dmc


def make_card(children, *, height=None, is_dark=False, overflow="hidden", p: "int | str" = 0, extra_style=None):
    style = {
        "display": "flex",
        "flexDirection": "column",
        # CSS vars auto-switch when [data-mantine-color-scheme] changes
        "backgroundColor": "var(--zam-card-bg)",
        "border": "var(--zam-card-border)",
        "boxShadow": "var(--zam-card-shadow)",
        "overflow": overflow,
    }
    if height is not None:
        style["height"] = f"{height}px" if isinstance(height, int) else height
    if extra_style:
        style.update(extra_style)

    return dmc.Paper(
        p=p,  # type: ignore
        radius="md",
        withBorder=False,
        shadow=None,
        style=style,
        children=children,
    )
