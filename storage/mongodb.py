from pymongo import MongoClient

from logger import get_session_logger
from models import JobPosting, JobFitScore, GoogleSearchMetadata, GoogleSearchOrganicResult, AppConfig
from .interface import JobStorage

logger = get_session_logger()


class MongoDBStorage(JobStorage):

    def __init__(self, config: AppConfig):
        self.client = MongoClient(config.mongodb_uri)
        self.db = self.client[config.mongodb_dbname]

    def save(self, collection: str, data: list[dict]) -> None:
        if not data:
            return
        self.db[collection].insert_many(data)
        logger.info(f"Saved {len(data)} records to {collection}.")

    def save_search_results(self, metadata: GoogleSearchMetadata, results: list[GoogleSearchOrganicResult]) -> None:
        if not metadata or not results:
            return

        results_as_dict = [res.model_dump() for res in results]
        doc = dict(metadata=metadata.model_dump(), results=results_as_dict)
        self.db['search_results'].insert_one(doc)
        logger.info(f"Saved {len(results)} search results .")

    def save_jobs(self, jobs: list[JobPosting]) -> None:
        if not jobs:
            return

        docs = [job.model_dump() for job in jobs]  # pydantic -> dict
        self.db['jobs'].insert_many(docs)
        logger.info(f"Saved {len(jobs)} enriched jobs.")

    def save_evaluations(self, evaluations: list[JobFitScore]) -> None:
        if not evaluations:
            return

        docs = [eva.model_dump() for eva in evaluations]  # pydantic -> dict
        self.db['evaluations'].insert_many(docs)
        logger.info(f"Saved {len(evaluations)} evaluations.")

    def list_by_date_range(self, min_date: str, max_date: str) -> list[JobPosting]:
        # @TODO: implement
        pass
