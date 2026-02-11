from models import JobPosting
from storage.interface import JobStorage


class DynamoDBStorage(JobStorage):
    def save_all(self, job: JobPosting) -> None:
        pass

    def list_by_date_range(self, min_date: str, max_date: str) -> list[JobPosting]:
        pass