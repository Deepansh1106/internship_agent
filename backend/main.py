import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from langgraph.types import Command

from models.schemas import (
    WorkflowResumeRequest,
)
from tools.application_store import ApplicationStore
from workflows.internship_workflow import build_internship_workflow


app = FastAPI(
    title="Autonomous Internship Application Agent",
    version="1.0.0",
)

# This compiled graph owns the order in which tools run.
workflow = build_internship_workflow()
application_store = ApplicationStore()


def workflow_response(result: dict[str, Any], thread_id: str) -> dict[str, Any]:
    """Return graph state plus the next human decision, if the graph paused."""
    interrupts = result.get("__interrupt__", [])
    interrupt_value = interrupts[0].value if interrupts else None

    state = {
        key: value
        for key, value in result.items()
        if key != "__interrupt__"
    }
    return jsonable_encoder({
        "thread_id": thread_id,
        "state": state,
        "interrupt": interrupt_value,
    })


@app.post("/workflow/start")
async def start_workflow(
    file: UploadFile,
    location: str = Form("Remote"),
    max_results: int = Form(10),
) -> dict[str, Any]:
    """Start a graph run. It continues until LangGraph reaches an interrupt."""
    suffix = Path(file.filename or "").suffix or ".pdf"

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        thread_id = str(uuid4())
        result = workflow.invoke(
            {
                "resume_file_path": temp_path,
                "delete_resume_file": True,
                "location": location or None,
                "max_results": max_results,
            },
            {"configurable": {"thread_id": thread_id}},
        )
        return workflow_response(result, thread_id)

    except Exception as error:
        if "temp_path" in locals():
            Path(temp_path).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/workflow/resume")
def resume_workflow(request: WorkflowResumeRequest) -> dict[str, Any]:
    """Give a human decision to LangGraph and let it choose the next nodes."""
    try:
        result = workflow.invoke(
            Command(resume=request.resume_value),
            {"configurable": {"thread_id": request.thread_id}},
        )
        return workflow_response(result, request.thread_id)

    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/applications")
def list_applications() -> dict[str, Any]:
    result = application_store.list_applications()

    if result["success"]:
        return result["data"]

    raise HTTPException(status_code=400, detail=result["error"])


@app.delete("/applications")
def clear_applications() -> dict[str, Any]:
    """Clear saved history. This does not affect a running LangGraph workflow."""
    result = application_store.clear_applications()

    if result["success"]:
        return result["data"]

    raise HTTPException(status_code=400, detail=result["error"])
