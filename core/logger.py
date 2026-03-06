from logging import Logger, getLogger, DEBUG, Formatter, FileHandler, StreamHandler
from pathlib import Path
from datetime import datetime

_logger_instance = None  # singleton


def get_session_logger() -> Logger:
    """Return a singleton logger for the current session."""
    global _logger_instance
    if _logger_instance is not None:
        return _logger_instance

    # Create logs folder if missing
    Path("logs").mkdir(exist_ok=True)

    # Timestamp-based session filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = Path("logs") / f"session_{timestamp}.log"

    # Create logger
    logger = getLogger("findmeajob")
    logger.setLevel(DEBUG)

    # Prevent duplicate handlers
    if not logger.handlers:
        formatter = Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = FileHandler(logfile)
        file_handler.setFormatter(formatter)

        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    _logger_instance = logger
    return logger