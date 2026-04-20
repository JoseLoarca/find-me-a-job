from typing import Any

from base import BaseServiceException


class AnalyzerError(BaseServiceException):
    def __init__(self, job_id: str, code: int, status: Any | None = None, message: str | None = None, model=str | None):
        super().__init__(
            job_id=job_id,
            service="gemini",
            code=code,
            status=status,
            message=message,
            model=model,
            action="analysis"
        )


class EvaluationError(BaseServiceException):
    def __init__(self, job_id: str, code: int, status: Any | None = None, message: str | None = None, model=str | None):
        super().__init__(
            job_id=job_id,
            service="gemini",
            code=code,
            status=status,
            message=message,
            model=model,
            action="profile evaluation"
        )
