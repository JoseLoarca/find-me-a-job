import os

from google.genai import Client as GeminiClient
from google.genai.errors import APIError
from google.genai.types import GenerateContentConfig

from exceptions import EvaluationError
from logger import get_session_logger
from models import JobPosting, JobFitScore, AppConfig
from .helpers import get_current_user_profile
from .interface import ProfileEvaluator
from ..gemini.rate_limiter import RateLimiter

EVALUATOR_PROMPT = """You are a tech job fit evaluation agent in a job hunting automation workflow. 
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

logger = get_session_logger()
rate_limiter = RateLimiter(int(os.getenv("GEMINI_DEFAULT_RPM")), logger)

class GeminiEvaluator(ProfileEvaluator):

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
            raise Exception("Couldn't initialize Gemini client, GEMINI_DEFAULT_MODE not found.")

        self.gemini_default_model = os.getenv('GEMINI_DEFAULT_MODEL')


    def evaluate_profile_fit(self, role: JobPosting) -> JobFitScore:
        """Evaluates if the user's profile is a good fit for a specific role.

        Args:
            role: the role to evaluate

        Returns: the evaluated role, with the fit score and feedback from the LLM

        Raises:
            EvaluationError: if an error occurred while evaluating the role
        """
        try:
            role_for_eval = role.model_dump_json(exclude={"link"})

            rate_limiter.wait()
            response = self.gemini_client.models.generate_content(
                model=self.gemini_default_model,
                contents=EVALUATOR_PROMPT.format(role=role_for_eval),
                config=GenerateContentConfig(
                    tools=[get_current_user_profile],
                    response_mime_type="application/json",
                    response_json_schema=JobFitScore.model_json_schema()
                )
            )

            # @TODO:
            # there are non-text parts in the response: ['function_call'], returning concatenated text result from
            # text parts. Check the full candidates.content.parts accessor to get the full model response.

            return JobFitScore.model_validate_json(response.text)

        except APIError as e:
            logger.error(f"Gemini failed with error {e.message}, status {e.status} and code {e.code}.")
            raise EvaluationError(job_id=role.id, code=e.code, status=e.status, message=e.message)
