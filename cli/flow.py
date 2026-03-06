import os
from json import load

from core.health import HealthChecker
from core.registry import (
    ANALYZER_REGISTRY,
    EVALUATOR_REGISTRY,
    STORAGE_REGISTRY,
)
from core.orchestrator import Orchestrator
from logger import get_session_logger
from models import GoogleSearchQueryConfig, AppConfig

logger = get_session_logger()

def build_query_config_from_json() -> GoogleSearchQueryConfig:
    """Build query config from JSON file.

    Returns: a GoogleSearchQueryConfig object

    """
    with open('config.json') as config_file:
        json_config = load(config_file)

        logger.info("Loaded JSON file for search configuration.")

        return GoogleSearchQueryConfig.model_validate(json_config)

def run_flow() -> None:
    config = collect_config()

    # 1. Health Check
    health = HealthChecker(config)
    results = health.run()

    logger.info("Health check complete.")
    for k, v in results.items():
        logger.info(f"  {k}: {'OK' if v else 'FAILED'}")

    if not all(results.values()):
        return

    # 2. Wire engines
    logger.info("Wiring engines.")
    storage = STORAGE_REGISTRY[config.storage_service](config)

    analyzer = (
        ANALYZER_REGISTRY[config.analyzer_service](config)
        if config.analyzer_service
        else None
    )

    evaluator = (
        EVALUATOR_REGISTRY[config.evaluator_service](config)
        if config.evaluator_service
        else None
    )

    # 3. Build orchestrator
    logger.info("Building orchestrator.")
    orchestrator = Orchestrator(
        config=config,
        storage=storage,
        analyzer_service=analyzer,
        evaluator_service=evaluator,
    )

    # 4. Execute!
    logger.info("Starting execution of full pipeline.")
    result = orchestrator.run_pipeline()
    logger.info("Finished execution of full pipeline.")
    logger.info(result)


def collect_config() -> AppConfig:
    """Initialize app config.

    This method acts as the initial version for the app configuration initialization.
    TODO: build the configuration interactively
    """
    logger.info("Building app config. TODO: build the configuration interactively")
    serpapi_apikey = os.environ.get('SERPAPI_KEY')
    search_config = build_query_config_from_json()

    return AppConfig(
        serpapi_apikey=serpapi_apikey,
        search_config=search_config,
        search_max_pages=3,
        storage_service="mongodb",
        analyzer_service="gemini",
        evaluator_service="gemini",
        gemini_api_key=None,
        mongodb_uri=os.environ.get('MONGODB_CONN'),
        mongodb_dbname=os.environ.get('MONGODB_DBNAME'),
    )