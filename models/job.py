from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    job_id: str = Field(description="The job id of the role.")
    company_name: str = Field(description="Name of the company.")
    industry: str = Field(description="Industry of the company.")
    role_name: str = Field(description="Name of the role.")
    location: str = Field(description="Location and modality (remote, hybrid, or on site). "
                                      "If the remote is based in a specific city or state, this should contain the city "
                                      "or state followed by the modality, eg: 'Boston - Hybrid', or 'Massachusetts - Remote'. "
                                      "If it is fully remote, it should just say 'Fully remote'")
    job_link: str = Field(description="Link to the job posting.")
    source: str = Field(description="Source of the job posting.")
    description: str = Field(description="Description of the role.")
    stack: str = Field(description="Stack of technologies.")
    salary_range_posted: str = Field(description="Salary range. If posted, should be formatted as $xxx - $xxx, "
                                                 "if not posted then Not Posted should be the value")
    seniority: str = Field(description="Role's seniority. If its not listed it should be inferred.")
    skills: str = Field(description="Required and optional skills (hard/soft) for this role.")
    additional_info: str = Field(description="Any other information that might be relevant.")


class JobFitScore(BaseModel):
    fit_score: int = Field(description="Represents the fit score of the user profile and a specific role, "
                                       "from 0 to 100.", ge=0, le=100)
    fit_assessment_feedback: str = Field(description="Further elaborates on the fit score. For example, "
                                                     "if a fit is considered to be 25%, explains why.")
