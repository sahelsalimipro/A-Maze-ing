from __future__ import annotations
import logging
import sys
import time

from pixels import px_to_str
from regions import Region
import globals
from menu import handle_inputs, Redraw, start_keyboard, stop_keyboard
from viewport import clamp_view

logger = logging.getLogger(__name__)


def update_dirty_pixels(
    regions: tuple[Region, ...], clear: bool = False
) -> None:
    """Write the changed pixels of every region to the terminal.

    Moves the cursor only when needed, and skips pixels outside the
    visible part of the screen.

    Args:
        regions: the regions to output.
        clear: clear the screen first.
    """
    parts: list[str] = []
    # (row, col), 0-based, where the terminal cursor is now
    cursor: tuple[int, int] | None = None

    for region in regions:
        ox, oy = region.origin
        for x, y in region.consume_dirty():  # sorted by row, then column
            target = _to_screen(ox + x, oy + y)
            if target is None:
                continue

            # skip the move if we're already there
            if cursor != target:
                parts.append(f"\033[{target[0] + 1};{target[1] + 1}H")

            parts.append(px_to_str(region.buf[y][x]))
            # writing one char advances the cursor by one
            cursor = (target[0], target[1] + 1)

    if clear:
        parts.insert(0, "\033[2J")
    if not parts:
        return
    sys.stdout.write("\033[?2026h" + "".join(parts) + "\033[0m\033[?2026l")
    sys.stdout.flush()


def render(regions: dict[str, Region], clear: bool = False) -> None:
    """Full rebuild: every drawer draws again, then everything is sent."""
    for region in regions.values():
        region.redraw(globals.CONFIG)
    clamp_view()                        # the layout may have changed size
    update_dirty_pixels(tuple(regions.values()), clear)


def repaint(regions: dict[str, Region]) -> None:
    """Sends the current buffers again, e.g. after the view scrolled.
    Animations keep their state, unlike render()."""
    for region in regions.values():
        region.mark_all()
    update_dirty_pixels(tuple(regions.values()), clear=True)


def run(regions: dict[str, Region]) -> None:

    """Main loop: read input, animate at a fixed rate, output frames.

    Runs in the terminal's alternate screen, and restores the
    terminal on exit, even after an error or Ctrl-C.
    """
    STEP: float = globals.STEP
    acc: float = 0.0
    last: float = time.perf_counter()
    last_render: float = last

    new_render = True
    reg_list = tuple(regions.values())

    try:

        # Enter alternate screen - remove cursor - mouse wheel sends
        # arrow keys (alternate scroll mode) - move cursor to top - clear
        sys.stdout.write("\033[?1049h\033[?25l\033[?1007h\033[H\033[2J")
        sys.stdout.flush()
        start_keyboard()

        # MAIN LOOP
        while True:
            # Updating times of the loop
            now = time.perf_counter()
            acc += min(now - last, globals.MAX_DT)
            last = now

            redraw = handle_inputs()
            if redraw == Redraw.REBUILD:
                new_render = True
            elif redraw == Redraw.REPAINT and not new_render:
                repaint(regions)

            if new_render:
                # A command may have rebuilt the regions (theme change):
                # refresh the list and clear what the old layout left
                reg_list = tuple(regions.values())
                render(regions, clear=True)
                new_render = False
                continue

            # Updating simulation
            while acc >= STEP:
                for region in reg_list:
                    region.update(STEP)
                acc -= STEP

            # Updating the frame
            if now - last_render >= globals.T_FRAME:
                update_dirty_pixels(reg_list)
                last_render = now
            else:
                time.sleep(0.001)  # yields the cpu for a millisec

    finally:

        stop_keyboard()
        # End sync output - reset colors - restore cursor
        # - stop alternate scroll - exit alt screen
        sys.stdout.write("\033[?2026l\033[0m\033[?25h\033[?1007l\033[?1049l")
        sys.stdout.flush()


def _to_screen(lx: int, ly: int) -> tuple[int, int] | None:
    """Convert layout position (lx, ly) to a screen (row, col).

    Returns:
        The position, or None if it is not visible.
    """
    row, col = ly - globals.VIEW_Y, lx - globals.VIEW_X
    size = globals.TERMINAL_SIZE
    if 0 <= row < size.lines and 0 <= col < size.columns:
        return row, col
    return None
