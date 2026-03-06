import os

from pymongo import MongoClient

from logger import get_session_logger
from models import AppConfig

logger = get_session_logger()

def _mongo_health_check() -> bool:
    try:
        logger.info("Starting Mongo Health Check")
        client = MongoClient(os.getenv("MONGODB_CONN"), serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        client.close()
        return True
    except Exception as e:
        logger.error('Mongo health check failed: ', e)
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

        # Storage health
        if self.config.storage_service == "mongodb":
            checks["mongo_conn"] = _mongo_health_check()

        return checks
