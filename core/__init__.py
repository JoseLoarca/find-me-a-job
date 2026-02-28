from hashlib import sha256

from exceptions import AnalyzerError, FailedSearch
from models import AppConfig, GoogleSearchMetadata, GoogleSearchOrganicResult, JobPosting, AnalysisFailure, \
    EvaluationFailure
from services import JobSearch, JobAnalyzer
from storage import JobStorage


class Orchestrator:

    def __init__(self, config: AppConfig, storage: JobStorage):
        # Initialize services
        self.config = config
        self.storage = storage
        self.search_service = JobSearch(config.serpapi_apikey)
        self.analyzer_service = JobAnalyzer(gemini_api_key=config.gemini_api_key)

    def search_for_jobs(self) -> dict[str, GoogleSearchMetadata | list[GoogleSearchOrganicResult]] | dict[str, str]:
        """Searches for jobs

        Returns: a tuple containing the metadata of the searches executed and the results,
                    or a dict with an error message if the search fails

        """
        try:
            search_results = self.search_service.execute_search(self.config.search_config, self.config.search_max_pages)

            # Convert search response to objects
            search_metadata = GoogleSearchMetadata(session_id=search_results.get("session_id"),
                                                   search_ids=search_results.get("search_ids"),
                                                   query=search_results.get("query"),
                                                   total_pages=search_results.get("total_pages"))

            organic_results = [GoogleSearchOrganicResult(position=result.get("position"),
                                                         title=result.get("title"), link=result.get("link"),
                                                         snippet=result.get("snippet"), source=result.get("source"),
                                                         job_id=sha256(result.get("link").encode('utf-8')).hexdigest())
                               for result in search_results.get("organic_results")]

            return dict(search_metadata=search_metadata, organic_results=organic_results)

        except FailedSearch as e:
            return dict(error=str(e))

    def analyze_job_postings(self, job_postings: list[GoogleSearchOrganicResult]) -> tuple[
        list[GoogleSearchOrganicResult], list[AnalysisFailure]]:
        """Analyze, extract, and enrich Google Search results

        Args:
            job_postings: job listings results from Google Search

        Returns: a tuple containing a list of enriched job listings and a list of failed analysis operations

        """
        enriched = []
        failures = []

        for job in job_postings:
            try:
                analysis_result = self.analyzer_service.analyze_job_listing(job)
                enriched.append(analysis_result)
            except AnalyzerError as e:
                failures.append(AnalysisFailure(job=job, message=str(e)))
                continue

        return enriched, failures

    def evaluate_profile_fit(self, job_postings: list[JobPosting]) -> tuple[list[JobPosting], list[EvaluationFailure]]:
        """Run profile evaluation on job postings.

        Args:
            job_postings: lists of roles to evaluate

        Returns: a tuple containing a list of evaluated job postings and a list of failed evaluation operations

        """
        evald = []  # eval'd as in evaluated
        failures = []

        for job in job_postings:
            try:
                eval_result = self.analyzer_service.evaluate_profile_fit(job)
                evald.append(eval_result)
            except AnalyzerError as e:
                failures.append(EvaluationFailure(job=job, message=str(e)))
                continue

        return evald, failures

    def save_jobs(self, job_postings: list[JobPosting]) -> None:
        """Stores job postings

        Args:
            job_postings: lists of job postings

        Returns: None

        """
        self.storage.save_all(job_postings)
