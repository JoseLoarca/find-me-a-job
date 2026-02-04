from pydantic import BaseModel, Field


class GoogleSearchResult(BaseModel):
    session_id: str
    search_ids: list[str]
    query: str


class GoogleSearchOrganicResult(BaseModel):
    position: int
    title: str
    link: str
    snippet: str
    source: str


class LLMJobListingAnalysis(BaseModel):
    role_name: str = Field(description="Name of the role.")
    company_name: str = Field(description="Name of the company.")
    location: str = Field(description="Location of this role. It can be either be a city name if hybrid or on-site, "
                                      "or remote if 100% remote.")
    description: str = Field(description="Description of the role.")
    stack: str = Field(description="Stack of technologies.")
    salary_range_posted: str = Field(description="Salary range. If posted, should be formatted as $xxx - $xxx, "
                                                 "if not posted then Not Posted should be the value")
    skills: str = Field(description="Required and optional skills for this role.")
    inferred_seniority: str = Field(description="Role's seniority. If its not listed it should be inferred.")
    additional_info: str = Field(description="Any other information that might be relevant.")


class LLMJobFitScore(BaseModel):
    fit_score: int = Field(description="Represents the fit score of the user profile and a specific role, "
                                       "from 0 to 100.", ge=0, le=100)
    fit_assessment_feedback: str = Field(description="Further elaborates on the fit score. For example, "
                                                     "if a fit is considered to be 25%, explains why.")
