from random import randrange

import globals

RGB = tuple[int, int, int]

# (background, walls, trail)
PALETTES: tuple[tuple[RGB, RGB, RGB], ...] = (
    ((10, 10, 30), (80, 140, 255), (255, 210, 60)),     # night blue
    ((25, 10, 10), (230, 60, 50), (255, 240, 200)),     # crimson
    ((8, 20, 10), (60, 200, 90), (240, 120, 255)),      # forest
)
_palette_idx: int = -1     # first press shows PALETTES[0]


def recolor() -> bool:
    """Switches to the next predefined palette (loops back after the last)."""
    global _palette_idx
    _palette_idx = (_palette_idx + 1) % len(PALETTES)
    bg, walls, trail = PALETTES[_palette_idx]

    for key in ("BACKGROUND_CLR", "TOP_PADDING_CLR", "BOT_PADDING_CLR",
                "LEFT_PADDING_CLR", "RIGHT_PADDING_CLR", "BANNER_BCKG_CLR"):
        globals.CONFIG.set(key, bg)
    for key in ("WALLS_CLR", "BANNER_FRAME_CLR"):
        globals.CONFIG.set(key, walls)
    for key in ("TRAIL_CLR", "ENTRYPOINT_CLR", "EXITPOINT_CLR",
                "BANNER_TITLE_CLR"):
        globals.CONFIG.set(key, trail)
    return True


def toggle_solve() -> bool:
    """Shows/hides the solution path. The path itself is computed once at
    startup; the maze drawer only paints it when SOLVED is on."""
    globals.CONFIG.set("SOLVED", not globals.CONFIG["SOLVED"])
    return True


def _remake_maze() -> None:
    # Imported here: maze_builder -> themes -> menu would be a circular import
    from maze_builder import build_maze, attach_drawers
    attach_drawers(build_maze(globals.CONFIG))


def regenerate() -> bool:
    """Rebuilds the maze from the current SEED."""
    _remake_maze()
    return True


def new_seed() -> bool:
    """Picks a random SEED, then rebuilds the maze from it."""
    globals.CONFIG.set("SEED", randrange(2**31))
    _remake_maze()
    return True


def toggle_theme() -> bool:
    pass


def change_theme() -> bool:
    pass


def exit_prog() -> bool:
    raise KeyboardInterrupt()
