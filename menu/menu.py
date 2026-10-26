import textwrap
from dataclasses import dataclass

from .commands import Command

# ----------------- Actions ---------------------
# Press: a
# Name: Recolor
# Indicator: OFF
# Description: 	blabalabalbla-
# 				blablabla

# Press: b
# Name: launch rabbit
# Indicator:
# Description: bkzjdjshdsjdh


@dataclass(frozen=True)
class MenuRenderingCtx:

    labels: tuple[str, ...] = ("Press:", "Name:", "Indicator:", "Description:")
    label_w: int = max(len(l) for l in labels)
    margin: int = 1
    text_x: int = margin + label_w + 1          # where every value starts
    min_text_w: int = 10                        # below this, wrapping is pointless
    block_gap: int = 1                          # blank lines between commands


@dataclass(frozen=True)
class MenuBlock:
    y_press: int
    y_name: int
    name_lines: tuple[str, ...]
    y_indicator: int
    y_desc: int
    desc_lines: tuple[str, ...]


@dataclass(frozen=True)
class MenuLayout:
    text_x: int
    text_w: int
    indicator_w: tuple[int, ...]       # fixed width of each indicator
    blocks: tuple[MenuBlock, ...]
    height: int


def _wrap(text: str, width: int) -> tuple[str, ...]:
    # break_long_words=True: a very long word is split instead of failing
    return tuple(textwrap.wrap(text, width, break_long_words=True)) or ("",)


def compute_menu_layout(commands: tuple[Command, ...], width: int) -> MenuLayout:
    text_w = width - MenuRenderingCtx.text_x - MenuRenderingCtx.margin
    if text_w < MenuRenderingCtx.min_text_w:
        raise ValueError(f"Terminal too narrow for the menu ({width} columns)")

    blocks: list[MenuBlock] = []
    y = 2                                           # 0 = title bar, 1 = blank
    for c in commands:
        name_lines = _wrap(c.name, text_w)
        desc_lines = _wrap(c.description, text_w)

        y_press = y
        y_name = y_press + 1
        y_indicator = y_name + len(name_lines)
        y_desc = y_indicator + 1
        y = y_desc + len(desc_lines) + MenuRenderingCtx.block_gap

        blocks.append(MenuBlock(y_press, y_name, name_lines,
                                y_indicator, y_desc, desc_lines))

    return MenuLayout(
        text_x=MenuRenderingCtx.text_x,
        text_w=text_w,
        indicator_w=tuple(
            c.indicator.width if c.indicator else 0 for c in commands),
        blocks=tuple(blocks),
        # no trailing blank line
        height=y - MenuRenderingCtx.block_gap
    )
