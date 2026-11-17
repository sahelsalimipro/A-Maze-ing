"""Non-blocking keyboard polling, one key press at a time.
Same API on every platform:

    start_keyboard()   once, before the main loop
    read_key()         a str, or None if nothing was pressed:
                       one character for normal keys, or one of
                       "UP", "DOWN", "PGUP", "PGDN", "ESC"
    stop_keyboard()    once, after the main loop (restores the terminal)
"""
import sys

if sys.platform == "win32":
    import msvcrt

    # Special keys arrive as a prefix ("\x00" or "\xe0") then a code
    _WIN_SPECIAL: dict[str, str] = {
        "H": "UP", "P": "DOWN", "I": "PGUP", "Q": "PGDN",
    }

    def start_keyboard() -> None:
        return

    def stop_keyboard() -> None:
        return

    def read_key() -> str | None:
        if not msvcrt.kbhit():
            return None
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            return _WIN_SPECIAL.get(msvcrt.getwch())   # None if unknown
        return ch

else:
    import os
    import select
    import termios
    import tty

    _saved: list[int | list[bytes | int]] | None = None

    # Escape sequences -> key names. "\x1bO.." is the same key when the
    # terminal is in "application cursor" mode.
    _SEQUENCES: dict[bytes, str] = {
        b"[A": "UP", b"OA": "UP",
        b"[B": "DOWN", b"OB": "DOWN",
        b"[5~": "PGUP",
        b"[6~": "PGDN",
    }
    # Bytes of one sequence are sent together; this only bounds the wait
    # if a lone ESC was pressed.
    _SEQ_TIMEOUT = 0.01

    def start_keyboard() -> None:
        global _saved
        fd = sys.stdin.fileno()
        if sys.stdin.isatty():
            _saved = termios.tcgetattr(fd)
            tty.setcbreak(fd)           # no line buffering, no echo; Ctrl-C works
        # No O_NONBLOCK here: stdin and stdout are usually the same open file
        # description, so it would make every stdout write able to fail with
        # EAGAIN ("write could not complete without blocking") whenever the
        # terminal is slow to drain. read_key() asks select() instead.

    def stop_keyboard() -> None:
        global _saved
        if _saved is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _saved)
            _saved = None

    def _read_byte(fd: int, timeout: float) -> bytes:
        """One byte, or b"" if none comes within `timeout` seconds."""
        if not select.select([fd], [], [], timeout)[0]:
            return b""
        return os.read(fd, 1)

    def _read_escape(fd: int) -> str | None:
        """Called after an ESC byte: reads the rest of the sequence."""
        intro = _read_byte(fd, _SEQ_TIMEOUT)
        if not intro:
            return "ESC"
        seq = intro
        if intro == b"O":                   # ESC O <letter>
            seq += _read_byte(fd, _SEQ_TIMEOUT)
        elif intro == b"[":                 # ESC [ <params> <final byte>
            while True:
                b = _read_byte(fd, _SEQ_TIMEOUT)
                seq += b
                # A final byte is in 0x40-0x7E ("A", "~", ...)
                if not b or 0x40 <= b[0] <= 0x7E:
                    break
        return _SEQUENCES.get(seq)          # unknown sequence: ignored

    def read_key() -> str | None:
        fd = sys.stdin.fileno()
        data = _read_byte(fd, 0)            # nothing typed: don't wait
        if not data:
            return None
        if data == b"\x1b":
            return _read_escape(fd)
        return data.decode(errors="ignore") or None
