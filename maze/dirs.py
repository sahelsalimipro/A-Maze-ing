from typing import Literal

Direction = Literal["N", "S", "W", "E"]

DIRS: tuple[Direction, ...] = ("N", "S", "W", "E")

OPP_DIR: dict[Direction, Direction] = {
    "N": "S",
    "S": "N",
    "W": "E",
    "E": "W",
}

PERPENDICULAR: dict[Direction, Direction] = {
    "N": "E", "S": "E",
    "E": "N", "W": "N"
}

# (dx, dy), y grows downward (row index), so North is -1
DELTAS: dict[Direction, tuple[int, int]] = {
    "N": (0, -1),
    "S": (0, +1),
    "W": (-1, 0),
    "E": (+1, 0),
}
