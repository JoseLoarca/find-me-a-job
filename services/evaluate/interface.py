from abc import ABC, abstractmethod

from models import JobPosting, JobFitScore


class ProfileEvaluator(ABC):

    @abstractmethod
    def evaluate_profile_fit(self, role: JobPosting) -> JobFitScore:
        pass
