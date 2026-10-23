from typing import Literal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pixels import Pixel
Anchor = Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"]

# Utilities functions, that many different drawers may require.

def _center(text: str, width: int, space_char: str = ' ') -> str:
    """Centers a given text in n width, using space by default"""
    if len(text) >= width:
        return text[:width]
    pad_total = width - len(text)
    pad_left = pad_total // 2
    return space_char * pad_left + text + space_char * (pad_total - pad_left)

def _fill_sequence(seq: str, length: int) -> str:
    """Cycle `seq` until it exactly fills `length` characters."""
    if length <= 0:
        return ""
    if not seq:
        return " " * length
    full, rem = divmod(length, len(seq))
    return seq * full + seq[:rem]

def _anchor_offset(
    buf_h: int, buf_w: int, content_h: int, content_w: int, anchor: Anchor
) -> tuple[int, int]:
    """Row, col in buffer coordinates where content[0][0] lands."""
    match anchor:
        case "top-left":
            return 0, 0
        case "top-right":
            return 0, buf_w - content_w
        case "bottom-left":
            return buf_h - content_h, 0
        case "bottom-right":
            return buf_h - content_h, buf_w - content_w
        case "center":
            return (buf_h - content_h) // 2, (buf_w - content_w) // 2
        case _:
            raise ValueError(f"unknown anchor {anchor!r}")

def blit(
    buffer: list[list[Pixel]],
    content: list[list[Pixel]],
    anchor: Anchor = "top-left"
) -> None:
    """**Blit** -> bit block transfer.
    Assign content into a buffer, starting from the
    anchor (default=top-left) and cropping excess"""

    # Calculate boundaries
    buf_h = len(buffer)
    buf_w = len(buffer[0]) if buf_h else 0
    content_h = len(content)
    content_w = len(content[0]) if content_h else 0
    if buf_h == 0 or buf_w == 0 or content_h == 0 or content_w == 0:
        return

    row0, col0 = _anchor_offset(buf_h, buf_w, content_h, content_w, anchor)

    # Clip content's row/col into the buffer
    row_start = max(0, -row0)
    row_end = min(content_h, buf_h - row0)
    col_start = max(0, -col0)
    col_end = min(content_w, buf_w - col0)

    if row_start >= row_end or col_start >= col_end:
        return  # no overlap at all — fully off-buffer

    # Col a/b for the buffer, start/end for the content
    col_a, col_b = col0 + col_start, col0 + col_end
    for r in range(row_start, row_end):
        buffer[row0 + r][col_a:col_b] = content[r][col_start:col_end]
    return

def _scale(idx: int, ratio: int) -> int:
    """Buffer coordinate where content-block `idx` begins, on one axis."""
    return idx * (ratio + 1) + 1

def _total_buf(n: int, ratio: int) -> int:
    """Total buffer length needed for `n` content blocks on one axis."""
    return n * (ratio + 1) + 1
