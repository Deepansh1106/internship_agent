from pydantic import BaseModel
from typing import List


class ResumeProfile(BaseModel):
    skills: List[str]
    experience: List[str]
    education: List[str]
    projects: List[str]

class JobRoles(BaseModel):
    roles: List[str]