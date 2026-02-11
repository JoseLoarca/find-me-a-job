from models import AppConfig, GoogleSearchMetadata, GoogleSearchOrganicResult, JobPosting
from services import JobSearch, JobAnalyzer


class Orchestrator:

    def __init__(self, config: AppConfig):
        # Initialize services
        self.config = config
        self.search_service = JobSearch(config.serpapi_apikey)
        self.analyzer_service = JobAnalyzer()

    def search_for_jobs(self) -> tuple[GoogleSearchMetadata, list[GoogleSearchOrganicResult]]:
        """Searches for jobs

        Returns: a tuple containing the metadata of the searches executed and the

        """
        search_results = self.search_service.execute_search(self.config.search_config, self.config.search_max_pages)

        # Convert search response to objects
        search_metadata = GoogleSearchMetadata(session_id=search_results.get("session_id"),
                                               search_ids=search_results.get("search_ids"),
                                               query=search_results.get("query"),
                                               total_pages=search_results.get("total_pages"))

        organic_results = [GoogleSearchOrganicResult(position=result.get("position"),
                                                     title=result.get("title"), link=result.get("link"),
                                                     snippet=result.get("snippet"), source=result.get("source"))
                           for result in search_results.get("organic_results")]

        return search_metadata, organic_results

    def analyze_job_postings(self, job_postings: list[GoogleSearchOrganicResult]):
        """Analyze, extract, and enrich Google Search results

        Args:
            job_postings: job listings results from Google Search

        Returns: list of enriched job listings objects

        """
        enriched_job_postings = []

        for job in job_postings:
            enriched_job_postings.append(self.analyzer_service.analyze_job_listing(job))

        return enriched_job_postings

    def assess_profile_fit(self, job_postings: list[JobPosting]):
        """

        Args:
            job_postings:

        Returns:

        """
        assessed_job_postings = []

        for job in job_postings:
            assessed_job_postings.append(self.analyzer_service.analyze_profile_fit(job))

        return assessed_job_postings

    def save_jobs(self, job_postings: list[JobPosting]):
        """

        Args:
            job_postings:

        Returns:

        """
        pass