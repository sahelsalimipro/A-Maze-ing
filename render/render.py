from __future__ import annotations
from typing import Any
import logging
import sys
import time

from pixels import px_to_str
from regions import Region
import globals
from menu import handle_inputs, start_keyboard, stop_keyboard

logger = logging.getLogger(__name__)

def update_dirty_pixels(regions: tuple[Region, ...], clear: bool = False) -> None:
    parts: list[str] = []
    # (row, col), 0-based, where the terminal cursor is now
    cursor: tuple[int, int] | None = None

    for region in regions:
        ox, oy = region.origin
        for x, y in region.consume_dirty():  # sorted by row, then column
            target = _to_screen(ox + x, oy + y)
            if target is None:
                continue

            if cursor != target:             # skip the move if we're already there
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
    for region in regions.values():
        region.redraw(globals.CONFIG)
    update_dirty_pixels(tuple(regions.values()), clear)



def run(regions: dict[str, Region]) -> None:


    STEP: float = globals.STEP
    acc: float = 0.0
    last: float = time.perf_counter()
    last_render: float = last

    new_render = True
    reg_list = tuple(regions.values())

    try:

        # Enter alternate screen - move cursor to top - remove cursor
        sys.stdout.write("\033[?1049h\033[?25l\033[H\033[2J")
        sys.stdout.flush()
        start_keyboard()

        # MAIN LOOP
        while True:
            # Updating times of the loop
            now = time.perf_counter()
            acc += min(now - last, globals.MAX_DT)
            last = now

            if handle_inputs():
                new_render = True

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
        # End sync output - Restore cursor - Exit alt screen
        sys.stdout.write("\033[?2026l\033[0m\033[?25h\033[?1049l")
        sys.stdout.flush()

def _to_screen(lx: int, ly: int) -> tuple[int, int] | None:
    row, col = ly - globals.VIEW_Y, lx - globals.VIEW_X
    size = globals.TERMINAL_SIZE
    if 0 <= row < size.lines and 0 <= col < size.columns:
        return row, col
    return None
