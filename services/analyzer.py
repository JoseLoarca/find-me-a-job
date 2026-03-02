import json
import os

from google.genai import errors, Client as GeminiClient
from google.genai.errors import APIError
from google.genai.types import GenerateContentConfig

from exceptions import AnalyzerError, EvaluationError, CouldNotReadProfileError
from models import GoogleSearchOrganicResult, JobPosting, JobFitScore

DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"

JOB_ANALYZER_PROMPT = """You are a tech job ingestion and normalization agent in a job hunting automation workflow.
Your task is to extract, structure, and normalize data from a tech job posting sourced from {source}.
This step is part of a multi-stage pipeline. Your only responsibilities are to extract job attributes, and to enrich
missing fields only when clearly inferrable from context. 
Job posting link: {job_link}
"""

PROFILE_ANALYZER_PROMPT = """You are a tech job fit evaluation agent in a job hunting automation workflow. 
Your task is to evaluate the alignment between the current user profile and a specific tech role. 
Based on this evaluation provide a fit score from 0 to 100 and a concise explanation of the score (feedback).

Follow these scoring rules:
0 = no alignment
50 = partial alignment with major gaps
100 = strong alignment across core requirements

These are your operating principles:
- Use only the information explicitly provided to you.
- Produce a score and feedback only when the provided data contains sufficient information to evaluate the alignment,
- Treat missing data as unknown.
- Base all reasoning on observable fields.
- Maintain neutral, non-advisory language.
- If the data provided is insufficient, default the score to 0, and explain in the feedback that the evaluation was not possible.

Job data: {role}
"""


class JobAnalyzer:

    def __init__(self, gemini_api_key: str = None, profile_path: str = None):
        # Gemini should automatically read the key from env vars, but we should allow to override the key to be used
        # If there's no key in env vars, and no key is manually passed, return an error
        if gemini_api_key:
            self.gemini_client = GeminiClient(api_key=gemini_api_key)
        else:
            if not os.getenv('GEMINI_API_KEY'):
                raise Exception("Couldn't initialize Gemini client, GEMINI_API_KEY not found.")

            self.gemini_client = GeminiClient()

        if profile_path:
            self.profile_path = profile_path
        else:
            if not os.getenv('DEFAULT_PROFILE_PATH'):
                raise Exception("Couldn't initialize JobAnalyzer instance, DEFAULT_PROFILE_PATH not found.")
            self.profile_path = os.getenv('DEFAULT_PROFILE_PATH')


    def get_current_user_profile(self) -> dict:
        """Gets the current user profile. The profile contains all the necessary information (location, work exp,
        skills, personal preferences, etc.) to evaluate the alignment between current user and a tech role.

        Returns: A dictionary containing the user's profile (location, work experience, skills, etc.)

        """
        with open(self.profile_path) as json_profile:
            try:
                return json.load(json_profile)
            except Exception as e:
                raise CouldNotReadProfileError(path=self.profile_path, message=str(e))

    def analyze_job_listing(self, organic_result: GoogleSearchOrganicResult) -> JobPosting:
        """Analyzes a job listing obtained from a Google Search using only its link.

        Args:
            organic_result: an organic result from a Google Search

        Returns: a JobPosting instance

        Raises:
            AnalyzerError: if an error occurred while analyzing the job listing

        """
        # @TODO: remove this
        # print('Analyzing: ', organic_result.link, organic_result.title)

        try:
            response = self.gemini_client.models.generate_content(
                model=DEFAULT_GEMINI_MODEL,
                contents=JOB_ANALYZER_PROMPT.format(source=organic_result.source, job_link=organic_result.link),
                config=GenerateContentConfig(
                    tools=[{"url_context": {}}],
                    response_mime_type="application/json",
                    response_json_schema=JobPosting.model_json_schema()
                )
            )

            # @TODO: remove this
            # for candidate in response.candidates:
            #     for metadata in candidate.url_context_metadata.url_metadata:
            #         print('URL: ', metadata.retrieved_url)
            #         print('Status: ', metadata.url_retrieval_status)

            return JobPosting.model_validate_json(response.text)

        except errors.APIError as e:
            raise AnalyzerError(job_id=organic_result.job_id, code=e.code, status=e.status, message=e.message)


    def evaluate_profile_fit(self, role: JobPosting) -> JobFitScore:
        """Evaluates if the current user is a good fit for a specific role.

        Args:
            role: the role to evaluate

        Returns: the evaluated role, with the fit score and feedback from the LLM

        Raises:
            EvaluationError: if an error occurred while evaluating the role
        """
        try:
            role_for_eval = role.model_dump_json(exclude={"link"})

            response = self.gemini_client.models.generate_content(
                model=DEFAULT_GEMINI_MODEL,
                contents=PROFILE_ANALYZER_PROMPT.format(role=role_for_eval),
                config=GenerateContentConfig(
                    tools=[self.get_current_user_profile],
                    response_mime_type="application/json",
                    response_json_schema=JobFitScore.model_json_schema()
                )
            )

            # @TODO:
            # there are non-text parts in the response: ['function_call'], returning concatenated text result from
            # text parts. Check the full candidates.content.parts accessor to get the full model response.

            return JobFitScore.model_validate_json(response.text)

        except APIError as e:
            raise EvaluationError(job_id=role.id, code=e.code, status=e.status, message=e.message)
