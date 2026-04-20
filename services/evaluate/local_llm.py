import os
from logging import DEBUG

import ollama
from ollama import ResponseError

from exceptions.local_llm import OllamaEvaluationError
from logger import get_session_logger
from models import JobPosting, JobFitScore, AppConfig
from .helpers import get_current_user_profile
from .interface import ProfileEvaluator

OLLAMA_EVALUATOR_MODEL = 'find-me-a-job-ollama-evaluator-model:latest'

EVALUATOR_DESCRIPTION = "You are a tech job fit evaluation agent in a job hunting automation workflow."

EVALUATOR_PROMPT = """Your task is to evaluate the alignment between the current user profile and a specific tech role. 
Based on this evaluation provide a fit score from 0 to 100 and a concise explanation of the score (feedback).

Follow these scoring rules:
0 = no alignment
50 = partial alignment with major gaps
100 = strong alignment across core requirements

These are your operating principles:
- If the role location is outside the U.S., the evaluation should automatically stop with a final score of 0.
- Use only the information explicitly provided to you.
- Produce a score and feedback only when the provided data contains sufficient information to evaluate the alignment,
- Treat missing data as unknown.
- Base all reasoning on observable fields.
- Maintain neutral, non-advisory language.
- If the data provided is insufficient, default the score to 0, and explain in the feedback that the evaluation was not possible.

This is the job data: {role}
This is the user profile: {user_profile}

Use the following JSON schema for the response: {schema}
"""

logger = get_session_logger()


class OllamaEvaluator(ProfileEvaluator):

    def __init__(self, config: AppConfig):
        # Create a custom model
        self.model_name = config.ollama_evaluator_model

        # If the model doesn't already exist locally, then we create it
        logger.info("Checking if local model exists.")

        local_models = [m.model for m in ollama.list().models]
        if self.model_name not in local_models:
            logger.info("Local model not found, creating new one.")
            base_model = os.getenv('OLLAMA_EVALUATOR_BASE_MODEL')

            ollama.create(
                model=self.model_name,
                from_=base_model,
                system=EVALUATOR_DESCRIPTION
            )

        logger.info(f"Running local evaluator using model: {self.model_name}")
        self.ollama_evaluator_model_temp = config.ollama_evaluator_model_temp

    def evaluate_profile_fit(self, role: JobPosting) -> JobFitScore:
        """Evaluates if the user's profile is a good fit for a specific role.

            Args:
                role: the role to evaluate

            Returns: the evaluated role, with the fit score and feedback from the LLM

            Raises:
                EvaluationError: if an error occurred while evaluating the role
        """
        try:
            logger.debug(f"Evaluating: {role.role.title} @ {role.org.name} ({role.link})")

            role_for_eval = role.model_dump_json(exclude={"link"})
            output_schema = JobFitScore.model_json_schema()

            req = ollama.generate(model=self.model_name,
                                  prompt=EVALUATOR_PROMPT.format(role=role_for_eval,
                                                                 user_profile=str(get_current_user_profile()),
                                                                 schema=str(output_schema)),
                                  format=output_schema,
                                  options=dict(temperature=self.ollama_evaluator_model_temp),
                                  think=False,  # Explicitly disable thinking and streaming
                                  stream=False)

            if logger.isEnabledFor(DEBUG):  # Time and log responses
                timing = req.total_duration / 1_000_000_000
                logger.debug(f"[timing]: {timing:.2f} seconds")
                logger.debug(f"Final response from {self.model_name}: {req.response}")

            return JobFitScore.model_validate_json(req.response)

        except ResponseError as e:
            logger.error(f"{self.model_name} failed with error {e.error} and status code {e.status_code}")
            raise OllamaEvaluationError(job_id=role.id, code=e.status_code, message=e.error, model=self.model_name)
