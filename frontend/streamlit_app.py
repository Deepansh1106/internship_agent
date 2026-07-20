import os
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
WORKFLOW_STEPS = [
    ("Resume", "📄"),
    ("Skills", "🧠"),
    ("Role", "🎯"),
    ("Jobs", "💼"),
    ("AI Match", "🤖"),
    ("Email", "✉️"),
    ("Complete", "✓"),
]


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem;}
        [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
            background-color: #f8fafc !important;
            border-right: 1px solid #e2e8f0;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {color: #1e293b !important;}
        [data-testid="stExpander"] {
            border: 1px solid #dbe3ef !important;
            border-radius: 12px !important;
            background: #ffffff;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
            margin-bottom: 0.75rem;
        }
        [data-testid="stExpander"] details summary {padding: 0.35rem 0.5rem;}
        [data-testid="stAlert"] {border-radius: 12px; border: 1px solid #cfe0ff;}
        [data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
            padding: 0.8rem 1rem;
        }
        .stButton > button, .stLinkButton > a {
            border-radius: 9px;
            border: 1px solid #2563eb;
            font-weight: 600;
        }
        [data-baseweb="select"] > div, [data-baseweb="input"] > div {
            border-radius: 9px;
        }
        .workflow-tracker {
            display: flex;
            align-items: flex-start;
            width: 100%;
            padding: 1.25rem 1rem 0.75rem;
            margin: 0.2rem 0 2rem;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            background: #ffffff;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
            overflow-x: auto;
        }
        .workflow-step {min-width: 76px; text-align: center; flex: 0 0 auto;}
        .workflow-circle {
            width: 38px;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.45rem;
            border: 2px solid #cbd5e1;
            border-radius: 50%;
            color: #94a3b8;
            background: #ffffff;
            font-size: 1rem;
            transition: background-color 250ms ease, border-color 250ms ease,
                color 250ms ease, transform 250ms ease, box-shadow 250ms ease;
        }
        .workflow-title {
            color: #94a3b8;
            font-size: 0.77rem;
            font-weight: 500;
            white-space: nowrap;
            transition: color 250ms ease, font-weight 250ms ease;
        }
        .workflow-step.completed .workflow-circle {
            background: #16a34a;
            border-color: #16a34a;
            color: #ffffff;
        }
        .workflow-step.completed .workflow-title {color: #1e293b;}
        .workflow-step.current .workflow-circle {
            background: #2563eb;
            border-color: #2563eb;
            color: #ffffff;
            box-shadow: 0 0 0 5px rgba(37, 99, 235, 0.12);
            transform: scale(1.08);
        }
        .workflow-step.current .workflow-title {color: #1e3a8a; font-weight: 700;}
        .workflow-connector {
            height: 2px;
            min-width: 24px;
            flex: 1 1 48px;
            margin-top: 18px;
            background: #e2e8f0;
            transition: background-color 300ms ease;
        }
        .workflow-connector.completed {background: #16a34a;}
        .workflow-connector.current {background: #2563eb;}
        @media (max-width: 760px) {
            .workflow-tracker {justify-content: flex-start;}
            .workflow-connector {min-width: 18px; flex: 0 0 18px;}
            .workflow-step {min-width: 68px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    defaults = {
        "thread_id": None,
        "workflow_state": {},
        "interrupt": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_url(path: str) -> str:
    return f"{API_BASE_URL}{path}"


def show_api_error(response: requests.Response) -> None:
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    st.error(detail)


def post_start(file_name: str, file_bytes: bytes, location: str, max_results: int):
    try:
        response = requests.post(
            api_url("/workflow/start"),
            files={"file": (file_name, file_bytes, "application/pdf")},
            data={"location": location, "max_results": max_results},
            timeout=120,
        )
    except requests.RequestException as error:
        st.error(str(error))
        return None

    if response.status_code >= 400:
        show_api_error(response)
        return None
    return response.json()


def resume_workflow(resume_value: Any):
    try:
        response = requests.post(
            api_url("/workflow/resume"),
            json={
                "thread_id": st.session_state.thread_id,
                "resume_value": resume_value,
            },
            timeout=120,
        )
    except requests.RequestException as error:
        st.error(str(error))
        return None

    if response.status_code >= 400:
        show_api_error(response)
        return None
    return response.json()


def get_json(path: str):
    try:
        response = requests.get(api_url(path), timeout=60)
    except requests.RequestException as error:
        st.error(str(error))
        return None

    if response.status_code >= 400:
        show_api_error(response)
        return None
    return response.json()


def delete_json(path: str):
    try:
        response = requests.delete(api_url(path), timeout=60)
    except requests.RequestException as error:
        st.error(str(error))
        return None

    if response.status_code >= 400:
        show_api_error(response)
        return None
    return response.json()


def save_workflow_response(response: dict[str, Any]) -> None:
    st.session_state.thread_id = response["thread_id"]
    st.session_state.workflow_state = response["state"]
    st.session_state.interrupt = response["interrupt"]


def current_workflow_step() -> int:
    """Derive the visible stage from LangGraph state, not from UI navigation."""
    if st.session_state.thread_id is None:
        return 0

    state = st.session_state.workflow_state
    interrupt = st.session_state.interrupt or {}

    if state.get("stored_applications") is not None and interrupt == {}:
        return 6

    interrupt_steps = {
        "role_selection": 2,
        "job_selection": 4,
        "email_approval": 5,
    }
    if interrupt.get("type") in interrupt_steps:
        return interrupt_steps[interrupt["type"]]

    if state.get("generated_emails"):
        return 5
    if state.get("matched_jobs"):
        return 4
    if state.get("searched_jobs"):
        return 3
    if state.get("suggested_roles"):
        return 2
    if state.get("candidate_profile"):
        return 1
    return 0


def render_workflow_tracker() -> None:
    current_step = current_workflow_step()
    tracker_parts = ['<div class="workflow-tracker">']

    for index, (title, icon) in enumerate(WORKFLOW_STEPS):
        state = "completed" if index < current_step else "current" if index == current_step else "upcoming"
        circle_content = "✓" if state == "completed" else icon
        tracker_parts.append(
            f'<div class="workflow-step {state}">'
            f'<div class="workflow-circle">{circle_content}</div>'
            f'<div class="workflow-title">{title}</div>'
            '</div>'
        )

        if index < len(WORKFLOW_STEPS) - 1:
            connector_state = "completed" if index < current_step - 1 else "current" if index == current_step - 1 else "upcoming"
            tracker_parts.append(f'<div class="workflow-connector {connector_state}"></div>')

    tracker_parts.append("</div>")
    st.markdown("".join(tracker_parts), unsafe_allow_html=True)


def format_job_label(match: dict[str, Any]) -> str:
    job = match["job"]
    return f"{match['score']}/100 - {job['title']} at {job['company']} ({job['location']})"


def render_profile(profile: dict[str, Any]) -> None:
    for section in ["skills", "experience", "education", "projects"]:
        values = profile.get(section, [])
        if values:
            st.subheader(section.replace("_", " ").title())
            st.write(", ".join(values))


def render_matches(matches: list[dict[str, Any]]) -> None:
    for match in matches:
        job = match["job"]
        with st.expander(format_job_label(match)):
            st.write(match["reasoning"])
            st.write(f"Employment type: {job['employment_type'] or 'Not listed'}")
            st.write(f"Posted: {job['posted_at'] or 'Not listed'}")
            st.write("Strengths: " + ", ".join(match.get("strengths", [])))
            st.write("Missing skills: " + ", ".join(match.get("missing_skills", [])))
            if job.get("apply_option"):
                st.link_button("Open Apply Link", job["apply_option"])


def render_start_form() -> None:
    st.header("Start an Application Workflow")
    uploaded_file = st.file_uploader("Resume PDF", type=["pdf"])
    location = st.text_input("Location", value="Remote")
    max_results = st.number_input("Maximum jobs", 1, 25, 10)

    if st.button("Start workflow", disabled=uploaded_file is None):
        with st.spinner("LangGraph is reading the resume and suggesting roles"):
            response = post_start(
                uploaded_file.name,
                uploaded_file.getvalue(),
                location,
                int(max_results),
            )
        if response:
            save_workflow_response(response)
            st.rerun()


def render_role_selection(interrupt: dict[str, Any]) -> None:
    roles = interrupt["roles"]
    selected_role = st.radio("Choose a role to search", roles)
    if st.button("Search and rank jobs"):
        with st.spinner("LangGraph is searching and ranking jobs"):
            response = resume_workflow(selected_role)
        if response:
            save_workflow_response(response)
            st.rerun()


def render_job_selection(interrupt: dict[str, Any]) -> None:
    matches = interrupt["matched_jobs"]
    requested = st.session_state.workflow_state.get("max_results", len(matches))
    st.metric("Ranked jobs found", len(matches), f"Requested up to {requested}")
    if len(matches) < requested:
        st.caption(
            "The job source returned fewer matches than requested for this role and location. "
            "Try a broader role or location to see more results."
        )
    render_matches(matches)
    options = {format_job_label(match): match["job"]["job_id"] for match in matches}
    selected_labels = st.multiselect("Choose jobs for email generation", options)
    if st.button("Generate emails", disabled=not selected_labels):
        with st.spinner("LangGraph is generating emails"):
            response = resume_workflow([options[label] for label in selected_labels])
        if response:
            save_workflow_response(response)
            st.rerun()


def render_email_approval(interrupt: dict[str, Any]) -> None:
    st.subheader("Review and approve emails")
    approvals = []
    for index, application in enumerate(interrupt["generated_emails"]):
        job = application["job"]
        email = application["email"]
        st.markdown(f"### {job['title']} at {job['company']}")
        approved = st.checkbox("Approve this application", value=True, key=f"approve_{index}")
        subject = st.text_input("Subject", email["subject"], key=f"subject_{index}")
        body = st.text_area("Body", email["body"], height=220, key=f"body_{index}")
        if approved:
            approvals.append({
                "job_id": job["job_id"],
                "email": {"subject": subject, "body": body},
            })

    if st.button("Save approved applications"):
        with st.spinner("LangGraph is saving approved applications"):
            response = resume_workflow({"approved_applications": approvals})
        if response:
            save_workflow_response(response)
            st.rerun()


def render_workflow() -> None:
    if st.session_state.thread_id is None:
        render_start_form()
        return

    state = st.session_state.workflow_state
    interrupt = st.session_state.interrupt
    st.caption(f"Workflow thread: {st.session_state.thread_id}")

    if state.get("candidate_profile"):
        with st.expander("Extracted resume profile", expanded=False):
            render_profile(state["candidate_profile"])

    if state.get("error"):
        st.error(state["error"])
        return

    if interrupt is None:
        stored = state.get("stored_applications", [])
        st.success(f"Workflow finished. Saved {len(stored)} application(s).")
        return

    st.info(interrupt["message"])
    if interrupt["type"] == "role_selection":
        render_role_selection(interrupt)
    elif interrupt["type"] == "job_selection":
        render_job_selection(interrupt)
    elif interrupt["type"] == "email_approval":
        render_email_approval(interrupt)


def render_history() -> None:
    st.header("Application History")
    clear_column, _ = st.columns([1, 3])
    if clear_column.button("Clear history", type="secondary"):
        result = delete_json("/applications")
        if result:
            st.success(f"Cleared {result['count']} saved application(s).")

    history = get_json("/applications") or {}
    if not history.get("applications", []):
        st.info("No applications saved yet.")
        return

    for application in history.get("applications", []):
        job = application["selected_job"]
        with st.expander(f"{job['title']} at {job['company']} - {application['status']}"):
            st.write(f"Score: {application['score']}")
            st.write(application["generated_email"]["subject"])
            st.text(application["generated_email"]["body"])


def reset_workflow() -> None:
    st.session_state.thread_id = None
    st.session_state.workflow_state = {}
    st.session_state.interrupt = None
    st.rerun()


def main() -> None:
    st.set_page_config(page_title="Internship Application Agent", layout="wide")
    initialize_state()
    apply_styles()
    st.title("Autonomous Internship Application Agent")
    render_workflow_tracker()
    page = st.sidebar.radio("Page", ["Workflow", "Application History"])
    st.sidebar.caption(f"Backend: {API_BASE_URL}")
    if st.session_state.thread_id and st.sidebar.button("Start a new workflow"):
        reset_workflow()

    if page == "Workflow":
        render_workflow()
    else:
        render_history()


if __name__ == "__main__":
    main()
