"""Drawers of the matrix theme: falling-glyph rain and repeating-glyph strips.

How the rain stays cheap
------------------------
* Event-driven: a column is a *stream* (a head and a trail behind it). Pixels
  are touched only when a head crosses a row boundary, never "every tick for
  every pixel". An idle column costs one float subtraction per tick.
* Banded trails: instead of fading every trail pixel each step, the trail has
  a few brightness bands (head, then 4 shades). When the head moves one row,
  each band edge moves one row too, so only the pixels sitting on an edge
  change colour. A step is O(bands) whatever the trail length.
* Own clock: the screen refreshes at 12 FPS while update() is called at
  60 Hz, so the simulation only advances every TICK (24 Hz) and returns
  immediately in between.
* Dirty marks: only pixels whose look changed are marked, so the renderer's
  work is proportional to what moved.
* Pre-warm: the first seconds are simulated in draw(), so the very first
  frame already has rain instead of an empty screen.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from random import Random

from drawers import Drawer
from pixels import Pixel
from config import Settings

RGB = tuple[int, int, int]
Mark = Callable[[int, int], None]

# Half-width katakana: one terminal cell wide (the full-width ones take two).
KATAKANA = "".join(map(chr, range(0xFF66, 0xFF9E)))
GLYPHS = KATAKANA + "0123456789:.=*+<>"

TICK = 1 / 24       # simulation step of the rain, in seconds
PREWARM = 5.0       # seconds simulated before the first frame is printed
QUOTE_HOLD = 10     # rows a quote stays fully readable once completely written

# ---------- Palette ---------- #
HEAD: RGB = (190, 255, 205)
TRAIL: tuple[RGB, ...] = ((0, 255, 70), (0, 200, 55), (0, 140, 38), (0, 80, 24))

QUOTE_HEAD: RGB = (225, 255, 235)
QUOTE_BODY: RGB = (110, 255, 150)
QUOTE_MID: RGB = (0, 190, 55)
QUOTE_DIM: RGB = (0, 105, 32)


def _mul(color: RGB, k: float) -> RGB:
    return (int(color[0] * k), int(color[1] * k), int(color[2] * k))


def _noop(x: int, y: int) -> None:
    return


# ---------- Rain ---------- #
@dataclass(frozen=True)
class RainStyle:
    speed: tuple[float, float]                  # rows per second
    length: tuple[int, int]                     # trail length, in rows
    delay: tuple[float, float]                  # idle seconds between 2 streams
    brightness: float                           # 0..1, scales the palette
    flicker: float                              # glyph changes / column / second
    quote_every: tuple[float, float] | None     # seconds between quotes


# Padding regions: the foreground layer. Extra regions: dimmer and slower.
NEAR = RainStyle(speed=(7.0, 15.0), length=(8, 22), delay=(0.0, 2.0),
                 brightness=1.0, flicker=0.4, quote_every=(25.0, 50.0))
FAR = RainStyle(speed=(4.0, 10.0), length=(5, 14), delay=(0.5, 4.0),
                brightness=0.45, flicker=0.2, quote_every=(40.0, 80.0))


class QuoteDirector:
    """Hands out quotes from a shuffled bag, shared by every rain drawer,
    so the same line doesn't fall twice in a row or in two places at once."""

    def __init__(self, quotes: tuple[str, ...]) -> None:
        self._quotes = [q for q in quotes if q.strip()]
        self._bag: list[str] = []
        self._rng = Random()

    def pick(self, max_len: int) -> str | None:
        """A quote of at most `max_len` characters, None if none fits."""
        if not any(len(q) <= max_len for q in self._quotes):
            return None
        while True:
            if not self._bag:
                self._bag = self._rng.sample(self._quotes, len(self._quotes))
            quote = self._bag.pop()
            if len(quote) <= max_len:
                return quote


def _band_edges(length: int) -> list[int]:
    """Distances (in rows behind the head) where the trail changes shade."""
    edges: list[int] = []
    last = 0
    for e in (1, length // 4, length // 2, (3 * length) // 4):
        e = max(e, last + 1)
        if e >= length:
            break
        edges.append(e)
        last = e
    return edges


class _Stream:
    __slots__ = ("pos", "row", "speed", "length", "bands", "head", "text")

    def __init__(
        self,
        speed: float,
        length: int,
        bands: tuple[tuple[int, RGB], ...],
        head: RGB,
        text: str | None = None,
    ) -> None:
        self.pos = 0.0          # head position, in rows (float)
        self.row = -1           # last row the head was written on
        self.speed = speed
        self.length = length
        self.bands = bands      # ((distance behind head, colour), ...)
        self.head = head
        self.text = text        # None: random glyphs. Else: a quote


class RainDrawer(Drawer):
    """Columns of falling glyphs, one stream per column at a time."""

    def __init__(
        self,
        style: RainStyle,
        bg: RGB | None,
        quotes: QuoteDirector | None = None,
    ) -> None:
        self._style = style
        self._bg = bg
        self._quotes = quotes
        self._rng = Random()

        k = style.brightness
        self._head = _mul(HEAD, 0.5 + 0.5 * k)
        self._trail = tuple(_mul(c, k) for c in TRAIL)

        self._w = 0
        self._h = 0
        self._streams: list[_Stream | None] = []
        self._wait: list[float] = []        # seconds before a column restarts
        self._acc = 0.0
        self._flick = 0.0
        self._quote_in = 0.0

    # ---------- Drawer interface ---------- #
    def draw(self, buffer: list[list[Pixel]], config: Settings) -> None:
        self._h = len(buffer)
        self._w = len(buffer[0]) if self._h else 0
        for row in buffer:
            for px in row:
                px.char = " "
                px.fg_clr = self._bg
                px.bg_clr = self._bg

        rng, st = self._rng, self._style
        self._streams = [None] * self._w
        self._wait = [rng.uniform(0.0, st.delay[1] + 3.0)
                      for _ in range(self._w)]
        self._quote_in = rng.uniform(PREWARM + 1.0, PREWARM + 6.0)

        if self._w and self._h:
            for _ in range(int(PREWARM / TICK)):
                self._tick(buffer, TICK, _noop)

    def update(
        self,
        buffer: list[list[Pixel]],
        dt: float,
        mark: Callable[[int, int], None]
    ) -> None:
        if not (self._w and self._h):
            return
        self._acc += dt
        if self._acc < TICK:
            return
        dt, self._acc = self._acc, 0.0
        self._tick(buffer, dt, mark)

    # ---------- Simulation ---------- #
    def _tick(self, buf: list[list[Pixel]], dt: float, mark: Mark) -> None:
        rng, streams, wait = self._rng, self._streams, self._wait
        for x in range(self._w):
            s = streams[x]
            if s is None:
                wait[x] -= dt
                if wait[x] <= 0.0:
                    streams[x] = self._spawn()
                continue
            s.pos += s.speed * dt
            target = int(s.pos)
            while s.row < target:
                s.row += 1
                if self._step(buf, x, s, mark):
                    streams[x] = None
                    wait[x] = rng.uniform(*self._style.delay)
                    break
        self._flicker(buf, dt, mark)
        self._maybe_quote(dt)

    def _step(
        self, buf: list[list[Pixel]], x: int, s: _Stream, mark: Mark
    ) -> bool:
        """The head of `s` moves down one row. True once the stream is gone."""
        h, r = self._h, s.row

        # 1. the new head
        if 0 <= r < h:
            ch: str | None
            if s.text is None:
                ch = self._rng.choice(GLYPHS)
            else:
                ch = s.text[r] if r < len(s.text) else None
            if ch is not None:
                px = buf[r][x]
                px.char = ch
                px.fg_clr = s.head
                mark(x, r)

        # 2. pixels sitting on a band edge fall into the next, darker shade
        for dist, color in s.bands:
            rr = r - dist
            if 0 <= rr < h:
                buf[rr][x].fg_clr = color
                mark(x, rr)

        # 3. the tail disappears
        rr = r - s.length
        if 0 <= rr < h:
            px = buf[rr][x]
            px.char = " "
            px.fg_clr = self._bg
            mark(x, rr)

        return rr >= h - 1

    def _spawn(self) -> _Stream:
        st, rng = self._style, self._rng
        length = rng.randint(*st.length)
        bands = tuple(zip(_band_edges(length), self._trail))
        return _Stream(rng.uniform(*st.speed), length, bands, self._head)

    def _spawn_quote(self, text: str) -> _Stream:
        length = len(text) + QUOTE_HOLD
        bands = (
            (1, QUOTE_BODY),
            (length - 4, QUOTE_MID),
            (length - 2, QUOTE_DIM),
        )
        return _Stream(self._rng.uniform(5.0, 7.5), length, bands,
                       QUOTE_HEAD, text)

    def _flicker(self, buf: list[list[Pixel]], dt: float, mark: Mark) -> None:
        """Random glyphs of random trails change, like the movie's rain."""
        rng = self._rng
        self._flick += self._style.flicker * self._w * dt
        while self._flick >= 1.0:
            self._flick -= 1.0
            x = rng.randrange(self._w)
            s = self._streams[x]
            if s is None or s.text is not None or s.length < 2:
                continue
            rr = s.row - rng.randint(0, s.length - 1)
            if 0 <= rr < self._h:
                buf[rr][x].char = rng.choice(GLYPHS)
                mark(x, rr)

    def _maybe_quote(self, dt: float) -> None:
        every = self._style.quote_every
        if every is None or self._quotes is None:
            return
        self._quote_in -= dt
        if self._quote_in > 0.0:
            return
        free = [x for x, s in enumerate(self._streams) if s is None]
        if not free:
            return                              # try again next tick
        self._quote_in = self._rng.uniform(*every)
        text = self._quotes.pick(self._h)
        if text is not None:
            self._streams[self._rng.choice(free)] = self._spawn_quote(text)


# ---------- Repeating strips ---------- #
class SequenceDrawer(Drawer):
    """Fills a region with a repeating sequence of characters.

    Each row is shifted by `row_shift` so the pattern looks woven. With
    `scroll` > 0 the pattern slides left by that many columns per second.
    To use pixel art instead, see art_loader.py: stamp() it in draw().
    """

    def __init__(
        self,
        sequence: str,
        fg: RGB | None,
        bg: RGB | None,
        scroll: float = 0.0,
        row_shift: int = 2,
    ) -> None:
        self._seq = sequence or " "
        self._fg = fg
        self._bg = bg
        self._scroll = scroll
        self._row_shift = row_shift
        self._phase = 0.0
        self._offset = 0
        self._w = 0

    def draw(self, buffer: list[list[Pixel]], config: Settings) -> None:
        self._w = len(buffer[0]) if buffer else 0
        for row in buffer:
            for px in row:
                px.fg_clr = self._fg
                px.bg_clr = self._bg
        self._paint(buffer, _noop)

    def update(
        self,
        buffer: list[list[Pixel]],
        dt: float,
        mark: Callable[[int, int], None]
    ) -> None:
        if not (self._scroll and self._w):
            return
        self._phase += self._scroll * dt
        offset = int(self._phase) % len(self._seq)
        if offset == self._offset:
            return
        self._offset = offset
        self._paint(buffer, mark)

    def _paint(self, buffer: list[list[Pixel]], mark: Mark) -> None:
        seq, n = self._seq, len(self._seq)
        for y, row in enumerate(buffer):
            base = self._offset + y * self._row_shift
            for x, px in enumerate(row):
                ch = seq[(x + base) % n]
                if px.char != ch:
                    px.char = ch
                    mark(x, y)
