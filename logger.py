import logging

def setup_logging(log_path: str = "amazeing.log") -> None:
    logging.basicConfig(
        filename=log_path,
        filemode="a",  # append
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
