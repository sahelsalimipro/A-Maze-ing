from __future__ import annotations
from typing import Any
import logging
import sys
import time

from pixels import px_to_str
from regions import Region
import globals
from menu import handle_inputs

logger = logging.getLogger(__name__)


def clear_console() -> None:
    print("\033[H\033[J", end="")
    return


def update_dirty_pixels(regions: list[Region]) -> None:
    parts: list[str] = []
    # (row, col), 0-based, where the terminal cursor is now
    cursor: tuple[int, int] | None = None

    for region in regions:
        ox, oy = region.origin
        for x, y in region.consume_dirty():  # sorted by row, then column
            target = (oy + y, ox + x)

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
    print("\n".join(lines))


def run(regions: list[Region]) -> None:

    sys.stdout.write("\033[?25l")  # Remove the user's cursor
    sys.stdout.flush()

    STEP: float = globals.STEP
    acc: float = 0.0
    last: float = time.perf_counter()
    last_render: float = last

    try:

        # MAIN LOOP
        while True:
            # Updating times of the loop
            now = time.perf_counter()
            acc += min(now - last, globals.MAX_DT)
            last = now

            handle_inputs()

            # Updating simulation
            while acc >= STEP:
                for region in regions:
                    region.update(STEP)
                acc -= STEP

            # Updating the frame
            if now - last_render >= globals.T_FRAME:
                update_dirty_pixels(regions)
                last_render = now
            else:
                time.sleep(0.001)  # yields the cpu for a millisec

    finally:

        sys.stdout.write("\033[0m\033[?25h")  # Restore the cursor
        sys.stdout.flush()
