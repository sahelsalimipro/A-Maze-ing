from dataclasses import dataclass

OUTSIDE_GAP = 1
INSIDE_GAP = 1
BALL_SIZE = 1 # FORBIDDEN TO CHANGE BALL_SIZE
WALL_SIZE = 2
# Here is what these values represent:

#
# ------------------
# ------------------
#
# o   o   o   o   o
#
# ------------------
# ------------------
#

HEIGHT = (OUTSIDE_GAP * 2) + (WALL_SIZE * 2) + (INSIDE_GAP * 2) + BALL_SIZE


@dataclass
class Colors():
    def __init__(
            self,
            bg_clr: tuple[int, int, int],
            wall_clr: tuple[int, int, int],
            ball_clr: tuple[int, int, int]
        ) -> None:

        self.bg_clr = bg_clr
        self.wall_clr = wall_clr
        self.ball_clr = ball_clr
        return

COLORS = Colors((0, 0, 0), (13, 13, 103), (255, 255, 255))
