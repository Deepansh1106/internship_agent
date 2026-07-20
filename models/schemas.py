from pydantic import BaseModel, ConfigDict
from typing import Any, List


class ResumeProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skills: List[str]
    experience: List[str]
    education: List[str]
    projects: List[str]

class JobRoles(BaseModel):
    model_config = ConfigDict(extra="forbid")
    roles: List[str]

class Job(BaseModel):
    job_id: str
    title: str
    company: str
    location: str

    description: str

    source: str
    source_link: str

    apply_option: str

    posted_at: str
    employment_type: str
    salary: str


class JobSearchResponse(BaseModel):
    jobs: List[Job]

class MatchEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    score: int
    reasoning: str
    strengths: List[str]
    missing_skills: List[str]


# ---------- Final Response ----------

class JobRecommendation(BaseModel):
    job: Job
    score: int
    reasoning: str
    strengths: List[str]
    missing_skills: List[str]


class JobMatchResponse(BaseModel):
    matched_jobs: List[JobRecommendation]


class GeneratedEmail(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject: str
    body: str


class EmailGenerationResponse(BaseModel):
    email: GeneratedEmail


class ApplicationCreate(BaseModel):
    selected_job: Job
    generated_email: GeneratedEmail
    score: int
    status: str = "pending"


class ApplicationRecord(BaseModel):
    id: int
    selected_job: Job
    generated_email: GeneratedEmail
    score: int
    status: str
    created_at: str


class ApplicationStoreResponse(BaseModel):
    application: ApplicationRecord


class ApplicationListResponse(BaseModel):
    applications: List[ApplicationRecord]


class ExtractSkillsRequest(BaseModel):
    resume_text: str


class SuggestRolesRequest(BaseModel):
    profile: ResumeProfile


class SearchJobsRequest(BaseModel):
    role: str
    location: str | None = None
    max_results: int = 10


class MatchJobsRequest(BaseModel):
    profile: ResumeProfile
    jobs: List[Job]


class GenerateEmailRequest(BaseModel):
    profile: ResumeProfile
    selected_job: Job
    match_result: JobRecommendation


class CreateApplicationRequest(BaseModel):
    selected_job: Job
    generated_email: GeneratedEmail
    score: int
    status: str = "pending"


class WorkflowResumeRequest(BaseModel):
    """The value supplied by a user when resuming a paused LangGraph run."""

    thread_id: str
    resume_value: Any
