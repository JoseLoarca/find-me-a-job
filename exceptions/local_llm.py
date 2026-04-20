from .base import BaseServiceException


class OllamaEvaluationError(BaseServiceException):
    def __init__(self, job_id: str, code: int, status: int | None = None, message: str | None = None,
                 model: str | None = None):
        super().__init__(
            job_id=job_id,
            service="ollama",
            code=code,
            status=status,
            message=message,
            model=model,
            action="profile evaluation"
        )
