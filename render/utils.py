def clear_console() -> None:
    """Move the cursor to the top left and clear the screen."""
    print("\033[H\033[J", end="")
    return
