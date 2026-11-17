"""Non-blocking keyboard polling, one key press at a time.
Same API on every platform:

    start_keyboard()   once, before the main loop
    read_key()         a str of one character, or None if nothing was pressed
    stop_keyboard()    once, after the main loop (restores the terminal)
"""
import sys

if sys.platform == "win32":
    import msvcrt

    def start_keyboard() -> None:
        return

    def stop_keyboard() -> None:
        return

    def read_key() -> str | None:
        if not msvcrt.kbhit():
            return None
        return msvcrt.getwch()

else:
    import os
    import select
    import termios
    import tty

    _saved: list[int | list[bytes | int]] | None = None

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

    def read_key() -> str | None:
        fd = sys.stdin.fileno()
        if not select.select([fd], [], [], 0)[0]:     # nothing typed: don't wait
            return None
        data = os.read(fd, 1)                         # ready, so this returns at once
        return data.decode(errors="ignore") or None
