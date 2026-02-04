from models import AppConfig, GoogleSearchMetadata, GoogleSearchOrganicResult, LLMJobListingAnalysis
from services import JobSearch, JobAnalyzer


class Orchestrator:

    def __init__(self, config: AppConfig):
        # Initialize services
        self.config = config
        self.search_service = JobSearch(config.serpapi_key)
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

    def analyze_job_listings(self, job_listings: list[GoogleSearchOrganicResult]):
        """Analyze, extract, and enrich Google Search results

        Args:
            job_listings: job listings results from Google Search

        Returns: list of enriched job listings objects

        """
        enriched_job_listings = []

        for job in job_listings:
            enriched_job_listings.append(self.analyzer_service.analyze_job_listing(job).get("response"))

        return enriched_job_listings

    def assess_profile_fit(self, job_listings: list[LLMJobListingAnalysis]):
        """

        Args:
            job_listings:

        Returns:

        """
        profile_scores = []

        for job in job_listings:
            profile_scores.append(self.analyzer_service.analyze_profile_fit(job))

        return profile_scores
