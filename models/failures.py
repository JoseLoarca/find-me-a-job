from pydantic import BaseModel

from models import GoogleSearchOrganicResult, JobPosting


class AnalysisFailure(BaseModel):
    job: GoogleSearchOrganicResult
    message: str

class EvaluationFailure(BaseModel):
    job: JobPosting
    message: str