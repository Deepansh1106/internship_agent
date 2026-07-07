from pydantic import BaseModel
from typing import List


class ResumeProfile(BaseModel):
    skills: List[str]
    experience: List[str]
    education: List[str]
    projects: List[str]

class JobRoles(BaseModel):
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