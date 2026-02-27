class AnalyzerError(Exception):

    def __init__(self, job_id: str, code: int, status: int = None, message: str = None):
        self.job_id = job_id
        self.code = code
        self.status = status
        self.message = message

        super().__init__(
            self, f"Unable to perform analysis on job {job_id}. "
            f"genai client failed with code {code}, status {status} and message {message}")