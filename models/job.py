from typing import Literal

from pydantic import BaseModel, Field


class JobOrg(BaseModel):
    name: str = Field(description="Name of the organization.")
    industry: str = Field(description="Industry of the company.")


class JobLocation(BaseModel):
    modality: Literal["remote", "hybrid", "onsite"] = Field(description="Modality of the role.")
    region: str = Field(description="Region of the role. This can be global, country-wide in the US, a specific US state, or a city.")


class JobCompensation(BaseModel):
    min_usd: str | int = Field(description="Minimum USD compensation posted. If not posted this should say 'Not posted'")
    max_usd: str | int = Field(description="Maximum USD compensation posted. If not posted this should say 'Not posted'")


class JobRole(BaseModel):
    title: str = Field(description="Title of the role.")
    category: Literal[
        "backend_engineering",
        "frontend_engineering",
        "fullstack_engineering",
        "data_engineering",
        "product_marketing",
        "product_management",
        "devops",
        "support_engineering",
        "solutions_engineering",
        "other"
    ] = Field(description="Role category.")
    seniority: Literal["junior", "mid", "senior", "staff", "principal", "lead"] = Field(description="Role seniority.")

class JobPosting(BaseModel):
    id: str = Field(description="Unique identifier of the job.")
    source: str = Field(description="Source of the job posting.")
    link: str = Field(description="Link to the job posting.")

    org: JobOrg = Field(description="Organization.")
    role: JobRole = Field(description="Job role.")
    location: JobLocation =Field(description="Job location.")
    comp: JobCompensation = Field(description="Job compensation.")

    tech_stack: list[str] = Field(description="Normalized tech stack")
    skills: list[str] = Field(description="Normalized skills")

    signals: dict = Field(default_factory=dict, description="inferred contextual attributes of the role that influence "
                                                            "evaluation quality and fit scoring but are not explicit requirements, skills, or constraints.")



class JobFitScore(BaseModel):
    fit_score: int = Field(description="Represents the fit score of the user profile and a specific role, "
                                       "from 0 to 100.", ge=0, le=100)
    fit_assessment_feedback: str = Field(description="Further elaborates on the fit score. For example, "
                                                     "if a fit is considered to be 25%, explains why.")
