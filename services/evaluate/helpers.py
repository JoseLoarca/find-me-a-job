from json import load
from os import getenv

from exceptions import CouldNotReadProfileError
from logger import get_session_logger

PROFILE_PATH = getenv("DEFAULT_PROFILE_PATH")
logger = get_session_logger()

def get_current_user_profile() -> dict:
    """Gets the current user profile. The profile contains all the necessary information (location, work exp,
    skills, personal preferences, etc.) to evaluate the alignment between current user and a tech role.

    Returns: A dictionary containing the user's profile (location, work experience, skills, etc.)

    """
    with open(PROFILE_PATH) as json_profile:
        try:
            return load(json_profile)
        except Exception as e:
            logger.error(f"Unable to load profile from {PROFILE_PATH} due to {e}")
            raise CouldNotReadProfileError(path=PROFILE_PATH, message=str(e))
