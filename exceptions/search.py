class FailedSearch(Exception):
    def __init__(
        self,
        query: str,
        message: str
    ):
        self.query = query
        self.message = message

        super().__init__(
            f"Search for {query} failed: {self.message}"
        )