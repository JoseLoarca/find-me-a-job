import os
from logging import DEBUG

from google.genai import Client as GeminiClient
from google.genai.errors import APIError
from google.genai.types import GenerateContentConfig

from exceptions import AnalyzerError
from logger import get_session_logger
from models import GoogleSearchOrganicResult, JobPosting, AppConfig
from .interface import JobListingAnalyzer

JOB_ANALYZER_PROMPT = """You are a tech job ingestion and normalization agent in a job hunting automation workflow.
Your task is to extract, structure, and normalize data from a tech job posting sourced from {source}.
This step is part of a multi-stage pipeline. Your only responsibilities are to extract job attributes, and to enrich
missing fields only when clearly inferrable from context. 
Job posting link: {job_link}
"""

logger = get_session_logger()


class GeminiAnalyzer(JobListingAnalyzer):

    def __init__(self, config: AppConfig):
        # Gemini should automatically read the key from env vars, but we should allow to override the key to be used
        # If there's no key in env vars, and no key is manually passed, return an error
        if config.gemini_api_key:
            self.gemini_client = GeminiClient(api_key=config.gemini_api_key)
        else:
            if not os.getenv('GEMINI_API_KEY'):
                logger.error("Couldn't initialize Gemini client, GEMINI_API_KEY not found.")
                raise Exception("Couldn't initialize Gemini client, GEMINI_API_KEY not found.")

            self.gemini_client = GeminiClient()

        if not os.getenv('GEMINI_DEFAULT_MODEL'):
            logger.error("Couldn't initialize Gemini client, GEMINI_DEFAULT_MODEL not found.")
            raise Exception("Couldn't initialize Gemini client, GEMINI_DEFAULT_MODEL not found.")

        self.gemini_default_model = os.getenv('GEMINI_DEFAULT_MODEL')

    def analyze_job_listing(self, organic_result: GoogleSearchOrganicResult) -> JobPosting:
        """Analyzes a job listing obtained from a Google Search using only its link.

        Args:
            organic_result: an organic result from a Google Search

        Returns: a JobPosting instance

        Raises:
            AnalyzerError: if an error occurred while analyzing the job listing

        """
        logger.debug(f"Analyzing: {organic_result.link} - {organic_result.title}")

        try:
            response = self.gemini_client.models.generate_content(
                model=self.gemini_default_model,
                contents=JOB_ANALYZER_PROMPT.format(source=organic_result.source, job_link=organic_result.link),
                config=GenerateContentConfig(
                    tools=[{"url_context": {}}],
                    response_mime_type="application/json",
                    response_json_schema=JobPosting.model_json_schema()
                )
            )

            if logger.isEnabledFor(DEBUG):
                for candidate in response.candidates:
                    for metadata in candidate.url_context_metadata.url_metadata:
                        logger.debug(f"URL: {metadata.retrieved_url}")
                        logger.debug(f"Status: {metadata.url_retrieval_status}")

            return JobPosting.model_validate_json(response.text)

        except APIError as e:
            logger.error(f"Gemini failed with error {e.message}, status {e.status} and code {e.code}.")
            raise AnalyzerError(job_id=organic_result.job_id, code=e.code, status=e.status, message=e.message)
