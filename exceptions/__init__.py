class GenAIError(Exception):
    def __init__(
        self,
        job_id: str,
        code: int,
        status: int | None = None,
        message: str | None = None,
        *,
        action: str
    ):
        self.job_id = job_id
        self.code = code
        self.status = status
        self.message = message
        self.action = action

        super().__init__(
            f"Unable to perform {action} on job {job_id}. "
            f"genai client failed with code {code}, status {status}, and message {message}"
        )


class AnalyzerError(GenAIError):
    def __init__(self, job_id: str, code: int, status: int | None = None, message: str | None = None):
        super().__init__(
            job_id=job_id,
            code=code,
            status=status,
            message=message,
            action="analysis"
        )


class EvaluationError(GenAIError):
    def __init__(self, job_id: str, code: int, status: int | None = None, message: str | None = None):
        super().__init__(
            job_id=job_id,
            code=code,
            status=status,
            message=message,
            action="fit evaluation"
        )
