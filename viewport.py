"""Which part of the layout is on screen.

The alternate screen has no scrollback: when the layout is taller than the
terminal, the program scrolls itself by drawing layout row VIEW_Y at screen
row 0. Region origins stay in layout coordinates; render/ converts them.
"""
import globals


def layout_height() -> int:
    """Rows taken by every region stacked together."""
    return max(
        (r.origin[1] + r.height for r in globals.REGIONS.values()), default=0
    )


def clamp_view() -> None:
    """Keeps VIEW_Y between the top and the last full screen of the layout
    (the layout may have shrunk, e.g. after a theme change)."""
    max_y = max(0, layout_height() - globals.TERMINAL_SIZE.lines)
    globals.VIEW_Y = min(max(globals.VIEW_Y, 0), max_y)


def scroll_by(rows: int) -> bool:
    """Moves the view by `rows` (negative = up). True if it moved."""
    before = globals.VIEW_Y
    globals.VIEW_Y += rows
    clamp_view()
    return globals.VIEW_Y != before


def page() -> int:
    """Rows moved by PgUp/PgDn: one screen, minus a line of context."""
    return max(1, globals.TERMINAL_SIZE.lines - 1)
