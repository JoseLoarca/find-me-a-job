from models import JobPosting, JobFitScore, GoogleSearchMetadata, GoogleSearchOrganicResult
from storage.interface import JobStorage


class DynamoDBStorage(JobStorage):
    def save(self, collection: str, data: list[dict]) -> None:
        pass

    def save_search_results(self, metadata: GoogleSearchMetadata, results: list[GoogleSearchOrganicResult]) -> None:
        pass

    def save_jobs(self, jobs: list[JobPosting]) -> None:
        pass

    def save_evaluations(self, evaluations: list[JobFitScore]) -> None:
        pass

    def list_by_date_range(self, min_date: str, max_date: str) -> list[JobPosting]:
        pass
