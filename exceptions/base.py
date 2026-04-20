from typing import Any


class BaseServiceException(Exception):
    def __init__(
        self,
        job_id: str,
        service: str,
        code: Any | None = None,
        status: Any | None = None,
        message: str | None = None,
        model: str | None = None,
        *,
        action: str
    ):
        self.job_id = job_id
        self.service = service
        self.code = code
        self.status = status
        self.message = message
        self.model = model
        self.action = action

        super().__init__(
            f"Unable to perform {action} on job {job_id}. "
            f"{service} failed with code {code}, status {status}, and message {message}. "
            f"Model: {model}."

        )