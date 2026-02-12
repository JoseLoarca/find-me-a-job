import json
import os

from google import genai
from google.genai.types import GenerateContentConfig

from models import GoogleSearchOrganicResult, JobPosting, JobFitScore

DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"
DEFAULT_PROFILE_FILE_NAME = "my_profile.json"

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


def get_current_user_profile() -> dict:
    """Gets the current user profile. The profile contains all the necessary information (location, work exp,
    skills, personal preferences, etc.) in order to assess if a specific role is a good match for the user.

    Returns: A dictionary containing the user's profile (location, work experience, skills, etc.)

    """
    with open(DEFAULT_PROFILE_FILE_NAME) as json_profile:
        try:
            return json.load(json_profile)
        except:
            return {"error": "Unable to retrieve user's profile", "profile": None}


class JobAnalyzer:

    def __init__(self, gemini_api_key: str = None):
        # Gemini should automatically read the key from env vars, but we should allow to override the key to be used
        # If there's no key in env vars, and no key is manually passed, return an error
        if gemini_api_key:
            self.gemini_client = genai.Client(api_key=gemini_api_key)
        else:
            if not os.getenv('GEMINI_API_KEY'):
                raise Exception("Couldn't initialize client, GEMINI_API_KEY not found.")

            self.gemini_client = genai.Client()

    def analyze_job_listing(self, organic_result: GoogleSearchOrganicResult) ->JobPosting:
        """Analyzes a job listing obtained from a Google Search using only its link.

        Args:
            organic_result: an organic result from a Google Search

        Returns: a JobPosting instance

        """
        response = self.gemini_client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=JOB_ANALYZER_PROMPT.format(source=organic_result.source, job_link=organic_result.link),
            config=GenerateContentConfig(
                tools=[{"url_context": {}}],
                response_mime_type="application/json",
                response_json_schema=JobPosting.model_json_schema()
            )
        )

        return JobPosting.model_validate_json(response.text)

    def evaluate_profile_fit(self, role: JobPosting) -> JobPosting:
        """Evaluates if the current user is a good fit for a specific role.

        Args:
            role: the role to evaluate

        Returns: the evaluated role, with the fit score and feedback from the LLM

        """
        role_for_eval = role.model_dump_json(exclude={"job_id", "job_link", "fit_score", "fit_assessment_feedback"})

        response = self.gemini_client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=PROFILE_ANALYZER_PROMPT.format(role=role_for_eval),
            config=GenerateContentConfig(
                tools=[get_current_user_profile],
                response_mime_type="application/json",
                response_json_schema=JobFitScore.model_json_schema()
            )
        )

        evaluation = JobFitScore.model_validate_json(response.text)

        return role.model_copy(update={"fit_score": evaluation.fit_score,
                                       "fit_assessment_feedback": evaluation.fit_assessment_feedback})
