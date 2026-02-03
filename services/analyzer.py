import os

from google import genai
from google.genai.types import GenerateContentConfig

from models import GoogleSearchOrganicResult, LLMJobListingAnalysisSchema

DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"


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

    def analyze_job_listing(self, organic_result: GoogleSearchOrganicResult, persist: bool = True):
        """Analyzes a job listing obtained from a Google Search using only its link.

        Args:
            organic_result: an organic result from a Google Search
            persist: whether to store this information in the database or not

        Returns: a LLMJobListingAnalysisSchema compliant dict

        """
        response = self.gemini_client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=f'You are a job hunting assistant. '
                     f'Analyze and extract information from the following job listing: {organic_result.link}',
            config=GenerateContentConfig(
                tools=[{"url_context": {}}],
                response_mime_type="application/json",
                response_json_schema=LLMJobListingAnalysisSchema.model_json_schema()
            )
        )

        if persist:
            # @todo: add db insertion
            pass

        return {"response": LLMJobListingAnalysisSchema.model_validate_json(response.text), "persisted": persist}

    def analyze_profile_fit(self):
        pass
