from core import get_session_logger
from .flow import run_flow


def run_cli() -> None:
    logger = get_session_logger()
    logger.info("Starting new CLI session")
    run_flow()