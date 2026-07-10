import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile

from models.schemas import (
    CreateApplicationRequest,
    ExtractSkillsRequest,
    GenerateEmailRequest,
    MatchJobsRequest,
    SearchJobsRequest,
    SuggestRolesRequest,
)
from tools.application_store import ApplicationStore
from tools.email_generator import EmailGenerator
from tools.job_matcher import JobMatcher
from tools.job_role_specifier import JobRoleSpecifier
from tools.job_search import JobSearcher
from tools.resume_reader import ResumeReader
from tools.skill_extractor import SkillExtractor


app = FastAPI(
    title="Autonomous Internship Application Agent",
    version="1.0.0",
)

skill_extractor = SkillExtractor()
job_role_specifier = JobRoleSpecifier()
job_searcher = JobSearcher()
job_matcher = JobMatcher()
email_generator = EmailGenerator()
application_store = ApplicationStore()


def handle_tool_result(result: dict[str, Any]) -> dict[str, Any]:
    if result["success"]:
        return result["data"]

    raise HTTPException(
        status_code=400,
        detail=result.get("error", "Unknown backend error"),
    )


@app.post("/upload-resume")
async def upload_resume(file: UploadFile) -> dict[str, Any]:
    suffix = Path(file.filename or "").suffix or ".pdf"

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        result = ResumeReader.extract_text(temp_path)

        if result["success"]:
            return {
                "text": result["text"]
            }

        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Resume upload failed"),
        )

    finally:
        if "temp_path" in locals():
            Path(temp_path).unlink(missing_ok=True)


@app.post("/extract-skills")
def extract_skills(request: ExtractSkillsRequest) -> dict[str, Any]:
    result = skill_extractor.extract(request.resume_text)

    return handle_tool_result(result)


@app.post("/suggest-roles")
def suggest_roles(request: SuggestRolesRequest) -> dict[str, Any]:
    result = job_role_specifier.suggest(request.profile.model_dump())

    return handle_tool_result(result)


@app.post("/search-jobs")
def search_jobs(request: SearchJobsRequest) -> dict[str, Any]:
    result = job_searcher.search(
        role=request.role,
        location=request.location,
        max_results=request.max_results,
    )

    return handle_tool_result(result)


@app.post("/match-jobs")
def match_jobs(request: MatchJobsRequest) -> dict[str, Any]:
    result = job_matcher.match(
        profile=request.profile.model_dump(),
        jobs=[
            job.model_dump()
            for job in request.jobs
        ],
    )

    return handle_tool_result(result)


@app.post("/generate-email")
def generate_email(request: GenerateEmailRequest) -> dict[str, Any]:
    result = email_generator.generate(
        profile=request.profile.model_dump(),
        selected_job=request.selected_job.model_dump(),
        match_result=request.match_result.model_dump(),
    )

    return handle_tool_result(result)


@app.post("/applications")
def create_application(request: CreateApplicationRequest) -> dict[str, Any]:
    result = application_store.create_application(
        selected_job=request.selected_job.model_dump(),
        generated_email=request.generated_email.model_dump(),
        score=request.score,
        status=request.status,
    )

    return handle_tool_result(result)


@app.get("/applications")
def list_applications() -> dict[str, Any]:
    result = application_store.list_applications()

    return handle_tool_result(result)
