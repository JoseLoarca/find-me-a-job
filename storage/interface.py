from abc import ABC, abstractmethod

from models import JobPosting, JobFitScore, GoogleSearchMetadata, GoogleSearchOrganicResult


class JobStorage(ABC):

    @abstractmethod
    def save(self, collection: str, data: list[dict]) -> None:
        pass

    @abstractmethod
    def save_search_results(self, metadata: GoogleSearchMetadata, results: list[GoogleSearchOrganicResult]) -> None:
        pass

    @abstractmethod
    def save_jobs(self, jobs: list[JobPosting]) -> None:
        pass

    @abstractmethod
    def save_evaluations(self, evaluations: list[JobFitScore]) -> None:
        pass

    @abstractmethod
    def list_by_date_range(self, min_date: str, max_date: str) -> list[JobPosting]:
        pass
