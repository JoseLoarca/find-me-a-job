from abc import ABC, abstractmethod

from models import JobPosting


class JobStorage(ABC):

    @abstractmethod
    def save_all(self, jobs: list[JobPosting]) -> None:
        pass

    @abstractmethod
    def list_by_date_range(self, min_date: str, max_date: str) -> list[JobPosting]:
        pass
