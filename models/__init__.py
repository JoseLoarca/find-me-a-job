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


class LLMJobListingAnalysisSchema(BaseModel):
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
