import time


class RateLimiter:
    def __init__(self, max_requests_per_minute: int, logger=None):
        self.interval = 60 / max_requests_per_minute  # This will be our interval between requests in seconds
        self.last_request = 0
        self.logger = logger

    def wait(self):
        now = time.time()
        delta = now - self.last_request

        if delta < self.interval:
            sleep_time = self.interval - delta
            if self.logger:
                self.logger.debug(f"Rate limit sleep: {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request = time.time()
