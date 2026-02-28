from pydantic import BaseModel

from .search import GoogleSearchOrganicResult
from .job import JobPosting


class AnalysisFailure(BaseModel):
    job: GoogleSearchOrganicResult
    message: str

class EvaluationFailure(BaseModel):
    job: JobPosting
    message: str