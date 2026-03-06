from hashlib import sha256
from typing import Optional

from exceptions import AnalyzerError, EvaluationError, FailedSearch
from logger import get_session_logger
from models import AppConfig, GoogleSearchMetadata, GoogleSearchOrganicResult, JobPosting, AnalysisFailure, \
    EvaluationFailure, JobFitScore
from services import JobSearch, JobListingAnalyzer, ProfileEvaluator
from storage import JobStorage

logger = get_session_logger()

class Orchestrator:

    def __init__(self,
                 config: AppConfig,
                 storage: JobStorage,
                 analyzer_service: Optional[JobListingAnalyzer] = None,
                 evaluator_service: Optional[ProfileEvaluator] = None):

        # *** Make sure analyzer service is set if evaluator service is set ***
        if evaluator_service and not analyzer_service:
            logger.error(f"Evaluation requires analyzer service.")
            raise ValueError("Evaluation requires analyzer service.")

        # *** Initialize services ***
        self.config = config
        self.search_service = JobSearch(config.serpapi_apikey)
        self.storage = storage
        self.analyzer_service = analyzer_service
        self.evaluator_service = evaluator_service

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
            logger.error(f"Search failed: {e}. Search configuration: {self.config.search_config}")
            return dict(error=str(e))

    def analyze_job_postings(self, job_postings: list[GoogleSearchOrganicResult]) -> tuple[
        list[JobPosting], list[AnalysisFailure]]:
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
                logger.error(f"Analyzer failed: {e}. Analysis service: {self.config.analyzer_service}")
                failures.append(AnalysisFailure(job=job, message=str(e)))
                continue

        return enriched, failures

    def evaluate_profile_fit(self, job_postings: list[JobPosting]) -> tuple[list[JobFitScore], list[EvaluationFailure]]:
        """Run profile evaluation on job postings.

        Args:
            job_postings: lists of roles to evaluate

        Returns: a tuple containing a list of evaluated job postings and a list of failed evaluation operations

        """
        evald = []  # eval'd as in evaluated
        failures = []

        for job in job_postings:
            try:
                eval_result = self.evaluator_service.evaluate_profile_fit(job)
                evald.append(eval_result)
            except EvaluationError as e:
                logger.error(f"Evaluator failed: {e}. Evaluation service: {self.config.evaluator_service}")
                failures.append(EvaluationFailure(job=job, message=str(e)))
                continue

        return evald, failures

    def save_search_results(self, metadata: GoogleSearchMetadata,
                            search_results: list[GoogleSearchOrganicResult]) -> None:
        """Stores job postings search results

        Args:
            metadata: search metadata
            search_results: lists of job postings search results (unprocessed)

        Returns: None

        """
        self.storage.save_search_results(metadata, search_results)

    def save_jobs(self, job_postings: list[JobPosting]) -> None:
        """Stores enriched job postings

        Args:
            job_postings: lists of job postings

        Returns: None

        """
        self.storage.save_jobs(job_postings)

    def save_evaluations(self, evaluations: list[JobFitScore]) -> None:
        """Stores job postings evaluation results

        Args:
            evaluations: lists of job postings evaluation results

        Returns: None

        """
        self.storage.save_evaluations(evaluations)

    def save(self, collection: str, data: list[dict]) -> None:
        """This is a general save method.

        Args:
            collection: collection name
            data: data to be saved

        Returns: None

        """
        self.storage.save(collection, data)

    def run_pipeline(self) -> dict:
        """Execute pipeline dynamically based on configured services.

        The pipeline adapts depending on which engines were provided.
        - Always performs search.
        - Runs analyzer only if analyzer_service is set.
        - Evaluation depends on enriched data, so will only run if analyzer_service AND evaluator_service are set.
        """

        # 1. SEARCH
        search_response = self.search_for_jobs()
        if "error" in search_response:
            return {"error": search_response["error"]}

        metadata = search_response["search_metadata"]
        organic_results = search_response["organic_results"]

        self.save_search_results(metadata, organic_results)

        enriched = []
        analysis_failures = []
        evaluations = []
        evaluation_failures = []

        # 2. ANALYZE: optional, only happens if the analyzer service is set
        if self.analyzer_service:
            enriched, analysis_failures = self.analyze_job_postings(organic_results)
            self.save_jobs(enriched)
            self.save(self.config.analyzer_service + 'analysis_failures', [failure.model_dump() for failure in analysis_failures])

            # 3. EVALUATE_ optional, we can't evaluate raw search results so this will only happen if
            # the eval service is set AND enriched data is available.
            if self.evaluator_service and enriched:
                evaluations, evaluation_failures = self.evaluate_profile_fit(enriched)
                self.save_evaluations(evaluations)
                self.save(self.config.analyzer_service + 'evaluation_failures', [failure.model_dump() for failure in evaluation_failures])

        return {
            "search_metadata": metadata,
            "organic_results": organic_results,
            "organic_results_count": len(organic_results),
            "enriched_count": len(enriched),
            "enriched": enriched,
            "analysis_failures": analysis_failures,
            "evaluations_count": len(evaluations),
            "evaluation_failures": evaluation_failures,
            "evaluations": evaluations
        }