"""Non-blocking keyboard polling, one key press at a time.

No Enter needed and nothing echoed on the screen (an echoed key would be
painted over the animation). Same API on every platform:

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
    import termios
    import tty

    _saved: list[int | list[bytes | int]] | None = None

    def start_keyboard() -> None:
        global _saved
        fd = sys.stdin.fileno()
        if sys.stdin.isatty():
            _saved = termios.tcgetattr(fd)
            tty.setcbreak(fd)           # no line buffering, no echo; Ctrl-C works
        os.set_blocking(fd, False)      # os.read() raises instead of waiting

    def stop_keyboard() -> None:
        global _saved
        fd = sys.stdin.fileno()
        os.set_blocking(fd, True)
        if _saved is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, _saved)
            _saved = None

    def read_key() -> str | None:
        try:
            data = os.read(sys.stdin.fileno(), 1)
        except BlockingIOError:
            return None
        return data.decode(errors="ignore") or None
