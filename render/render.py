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

_scrolled: int = 0          # layout rows pushed into the scrollback by the first print

def update_dirty_pixels(regions: tuple[Region, ...]) -> None:
    parts: list[str] = []
    # (row, col), 0-based, where the terminal cursor is now
    cursor: tuple[int, int] | None = None
    max_col = globals.TERMINAL_SIZE.columns

    for region in regions:
        ox, oy = region.origin
        for x, y in region.consume_dirty():  # sorted by row, then column
            # OLD:
            target = (oy + y, ox + x)
            # NEW:
            # target = (oy + y - _scrolled, ox + x)
            if target[0] < 0 or target[1] >= max_col: # in scrollback (can't redraw)
                continue

            if cursor != target:             # skip the move if we're already there
                parts.append(f"\033[{target[0] + 1};{target[1] + 1}H")

            parts.append(px_to_str(region.buf[y][x]))
            # writing one char advances the cursor by one
            cursor = (target[0], target[1] + 1)

    if not parts:                            # nothing changed: no write, no flush
        return

    sys.stdout.write("\033[?2026h" + "".join(parts) + "\033[0m\033[?2026l")
    sys.stdout.flush()


def render(regions: dict[str, Region]) -> None:

    lines = []
    total_y: int = 0
    for reg_name in globals.MID_REGION_ORDER:  # excludes the side padding and the menu
        region = regions.get(reg_name)
        if region is None:
            continue
        for y in range(region.height):
            line = (
                "".join(px_to_str(px)
                        for px in regions["extra-left"].buf[total_y])
                + "".join(px_to_str(px)
                          for px in regions["padd-left"].buf[total_y])
                + "".join(px_to_str(px) for px in region.buf[y])
                + "".join(px_to_str(px)
                          for px in regions["padd-right"].buf[total_y])
                + "".join(px_to_str(px)
                          for px in regions["extra-right"].buf[total_y])
            )
            lines.append(line)
            total_y += 1

    for row in regions["menu"].buf:
        lines.append("".join(px_to_str(px) for px in row))
    # OLD:
    # print("\n".join(lines))
    # NEW:
    # global _scrolled
    # _scrolled = max(0, len(lines) - globals.TERMINAL_SIZE.lines)
    sys.stdout.write("\n".join(lines))      # no trailing newline, it would scroll one extra row
    sys.stdout.flush()


def run(regions: dict[str, Region]) -> None:

    sys.stdout.write("\033[?1049h") # Enter alternate screen
    # sys.stdout.write("\033[?25l")   # Remove cursor
    sys.stdout.flush()
    start_keyboard()

    STEP: float = globals.STEP
    acc: float = 0.0
    last: float = time.perf_counter()
    last_render: float = last

    new_render = True
    reg_list = tuple(regions.values())

    try:

        # MAIN LOOP
        while True:
            # Updating times of the loop
            now = time.perf_counter()
            acc += min(now - last, globals.MAX_DT)
            last = now

            handle_inputs()

            if new_render:
                render(regions)
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
        # sys.stdout.write("\033[0m\033[?25h")    # Restore cursor
        sys.stdout.write("\033[?1049l")         # Exit alternate screen
        sys.stdout.flush()
