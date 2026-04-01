from abc import ABC, abstractmethod

from models import JobPosting, GoogleSearchOrganicResult


class JobListingAnalyzer(ABC):

    @abstractmethod
    def analyze_job_listing(self, organic_result: GoogleSearchOrganicResult) -> JobPosting:
        pass
