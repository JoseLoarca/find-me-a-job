import os

from pymongo import MongoClient
import ollama

from logger import get_session_logger
from models import AppConfig

logger = get_session_logger()

def _mongo_health_check() -> bool:
    """Perform a quick health check on the MongoDB database.
    The health check consists of a simple ping to the db.

    Returns: True if the health check succeeded, False otherwise.
    """
    try:
        logger.info("Starting Mongo Health Check")
        client = MongoClient(os.getenv("MONGODB_CONN"), serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Mongo health check failed: {e}")
        return False

def _ollama_health_check() -> bool:
    """Perform a quick health check on the Ollama connection.
    In order to consider the Ollama configuration "healthy", the following criteria should be met:
    - Ollama is up and running.
    - The base model exists in the system.

    Returns: True if the health check succeeded, False otherwise.
    """
    try:
        logger.info("Starting Ollama Health Check")
        ollama.show(os.getenv("OLLAMA_EVALUATOR_BASE_MODEL"))
        return True
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return False


class HealthChecker:

    def __init__(self, config: AppConfig):
        self.config = config

    def run(self) -> dict[str, bool]:
        logger.info("Starting Health Check")
        # Search always checked
        checks = {"serpapi": bool(self.config.serpapi_apikey)}

        # Shared Gemini availability (from config or env)
        gemini_available = bool(
            self.config.gemini_api_key or os.getenv("GEMINI_API_KEY")
        )

        # Analyzer health
        if self.config.analyzer_service == "gemini":
            checks["gemini_for_analyzer"] = gemini_available


        # Evaluator health
        if self.config.evaluator_service == "gemini":
            checks["gemini_for_evaluator"] = gemini_available

        if self.config.evaluator_service == "ollama":
            checks["ollama_for_evaluator"] = _ollama_health_check()

        # Storage health
        if self.config.storage_service == "mongodb":
            checks["mongo_conn"] = _mongo_health_check()

        return checks
