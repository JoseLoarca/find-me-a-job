class CouldNotReadProfileError(Exception):
    def __init__(
        self,
        path: str,
        message: str,
    ):
        self.path = path
        self.message = message

        super().__init__(
            f"Unable to read profile from {self.path}, error: {self.message}"
        )