import json
import os

from google import genai
from google.genai.types import GenerateContentConfig

from models import GoogleSearchOrganicResult, JobPosting, JobFitScore

DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"
DEFAULT_PROFILE_FILE_NAME = "my_profile.json"


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
            contents=f'You are a job hunting assistant. '
                     f'Analyze and extract information from the following job listing: {organic_result.link}',
            config=GenerateContentConfig(
                tools=[{"url_context": {}}],
                response_mime_type="application/json",
                response_json_schema=JobPosting.model_json_schema()
            )
        )

        return JobPosting.model_validate_json(response.text)

    def analyze_profile_fit(self, role: JobPosting) -> JobPosting:
        """Analyzes if the current user is a good fit for a specific role using a JSON file with the user profile.

        Args:
            role: the role to assess

        Returns: the assessed role, with the fit score and feedback from the LLM

        """
        response = self.gemini_client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=f"You are a job hunting assistant. "
                     f"Go over the user profile and determine if the following role is a good fit for "
                     f"the user: {role.model_dump_json()}"
                     f"Use a rating from 0 to 100, and make sure to include feedback to explain the score.",
            config=GenerateContentConfig(
                tools=[get_current_user_profile],
                response_mime_type="application/json",
                response_json_schema=JobFitScore.model_json_schema()
            )
        )

        assessment = JobFitScore.model_validate_json(response.text)

        return role.model_copy(update={'fit_score': assessment.fit_score,
                                       'fit_assessment_feedback': assessment.fit_assessment_feedback})
