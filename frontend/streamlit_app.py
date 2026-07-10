import os
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def initialize_state() -> None:
    defaults = {
        "resume_text": "",
        "profile": None,
        "roles": [],
        "selected_role": "",
        "jobs": [],
        "matched_jobs": [],
        "selected_matches": [],
        "generated_emails": [],
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


def post_json(path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    try:
        response = requests.post(
            api_url(path),
            json=payload,
            timeout=120,
        )

    except requests.RequestException as e:
        st.error(str(e))
        return None

    if response.status_code >= 400:
        show_api_error(response)
        return None

    return response.json()


def post_file(path: str, file_name: str, file_bytes: bytes) -> dict[str, Any] | None:
    try:
        response = requests.post(
            api_url(path),
            files={
                "file": (
                    file_name,
                    file_bytes,
                    "application/pdf",
                )
            },
            timeout=120,
        )

    except requests.RequestException as e:
        st.error(str(e))
        return None

    if response.status_code >= 400:
        show_api_error(response)
        return None

    return response.json()


def get_json(path: str) -> dict[str, Any] | None:
    try:
        response = requests.get(
            api_url(path),
            timeout=60,
        )

    except requests.RequestException as e:
        st.error(str(e))
        return None

    if response.status_code >= 400:
        show_api_error(response)
        return None

    return response.json()


def format_job_label(match: dict[str, Any]) -> str:
    job = match["job"]
    score = match["score"]

    return f"{score}/100 - {job['title']} at {job['company']} ({job['location']})"


def render_profile(profile: dict[str, Any]) -> None:
    for section in ["skills", "experience", "education", "projects"]:
        values = profile.get(section, [])

        if values:
            st.subheader(section.replace("_", " ").title())
            st.write(", ".join(values))


def render_upload_resume() -> None:
    st.header("Upload Resume")

    uploaded_file = st.file_uploader(
        "Resume PDF",
        type=["pdf"],
    )

    if st.button("Process Resume", disabled=uploaded_file is None):
        with st.spinner("Reading resume"):
            upload_result = post_file(
                "/upload-resume",
                uploaded_file.name,
                uploaded_file.getvalue(),
            )

        if not upload_result:
            return

        st.session_state.resume_text = upload_result["text"]

        with st.spinner("Extracting profile"):
            profile = post_json(
                "/extract-skills",
                {
                    "resume_text": st.session_state.resume_text
                },
            )

        if not profile:
            return

        st.session_state.profile = profile

        with st.spinner("Suggesting roles"):
            roles = post_json(
                "/suggest-roles",
                {
                    "profile": profile
                },
            )

        if roles:
            st.session_state.roles = roles["roles"]
            st.success("Resume processed.")

    if st.session_state.profile:
        render_profile(st.session_state.profile)


def render_suggested_roles() -> None:
    st.header("Suggested Roles")

    if not st.session_state.roles:
        st.info("Upload and process a resume first.")
        return

    selected_role = st.radio(
        "Role",
        st.session_state.roles,
        index=0,
    )
    location = st.text_input("Location", value="Remote")
    max_results = st.number_input(
        "Max results",
        min_value=1,
        max_value=25,
        value=10,
        step=1,
    )

    if st.button("Find Ranked Jobs"):
        st.session_state.selected_role = selected_role

        with st.spinner("Searching jobs"):
            search_result = post_json(
                "/search-jobs",
                {
                    "role": selected_role,
                    "location": location or None,
                    "max_results": int(max_results),
                },
            )

        if not search_result:
            return

        st.session_state.jobs = search_result["jobs"]

        if not st.session_state.jobs:
            st.warning("No jobs found.")
            return

        with st.spinner("Ranking jobs"):
            match_result = post_json(
                "/match-jobs",
                {
                    "profile": st.session_state.profile,
                    "jobs": st.session_state.jobs,
                },
            )

        if match_result:
            st.session_state.matched_jobs = match_result["matched_jobs"]
            st.success("Jobs ranked.")


def render_ranked_jobs() -> None:
    st.header("Ranked Jobs")

    if not st.session_state.matched_jobs:
        st.info("Search and rank jobs first.")
        return

    labels = [
        format_job_label(match)
        for match in st.session_state.matched_jobs
    ]
    selected_labels = st.multiselect(
        "Jobs",
        labels,
        default=labels[:1],
    )
    selected_indices = [
        labels.index(label)
        for label in selected_labels
    ]

    for index, match in enumerate(st.session_state.matched_jobs):
        job = match["job"]

        with st.expander(format_job_label(match), expanded=index in selected_indices):
            st.write(match["reasoning"])
            st.write(f"Employment type: {job['employment_type'] or 'Not listed'}")
            st.write(f"Posted: {job['posted_at'] or 'Not listed'}")
            st.write(f"Salary: {job['salary'] or 'Not listed'}")
            st.write("Strengths")
            st.write(", ".join(match.get("strengths", [])) or "None listed")
            st.write("Missing skills")
            st.write(", ".join(match.get("missing_skills", [])) or "None listed")

            if job.get("apply_option"):
                st.link_button("Open Apply Link", job["apply_option"])

    if st.button("Generate Emails", disabled=not selected_indices):
        selected_matches = [
            st.session_state.matched_jobs[index]
            for index in selected_indices
        ]
        generated_emails = []

        with st.spinner("Generating emails"):
            for match in selected_matches:
                result = post_json(
                    "/generate-email",
                    {
                        "profile": st.session_state.profile,
                        "selected_job": match["job"],
                        "match_result": match,
                    },
                )

                if not result:
                    return

                generated_emails.append({
                    "job": match["job"],
                    "score": match["score"],
                    "email": result["email"],
                })

        st.session_state.selected_matches = selected_matches
        st.session_state.generated_emails = generated_emails
        st.success("Emails generated.")


def render_email_preview() -> None:
    st.header("Email Preview")

    if not st.session_state.generated_emails:
        st.info("Generate emails from ranked jobs first.")
        return

    for index, application in enumerate(st.session_state.generated_emails):
        job = application["job"]
        email = application["email"]

        st.subheader(f"{job['title']} at {job['company']}")

        subject = st.text_input(
            "Subject",
            value=email["subject"],
            key=f"email_subject_{index}",
        )
        body = st.text_area(
            "Body",
            value=email["body"],
            height=260,
            key=f"email_body_{index}",
        )

        st.session_state.generated_emails[index]["email"] = {
            "subject": subject,
            "body": body,
        }

        if job.get("apply_option"):
            st.link_button(
                "Open Apply Link",
                job["apply_option"],
            )

        if st.button("Save Application", key=f"save_application_{index}"):
            result = post_json(
                "/applications",
                {
                    "selected_job": job,
                    "generated_email": {
                        "subject": subject,
                        "body": body,
                    },
                    "score": application["score"],
                    "status": "approved",
                },
            )

            if result:
                st.success(f"Saved application #{result['application']['id']}.")


def render_application_history() -> None:
    st.header("Application History")

    if st.button("Refresh History"):
        st.session_state.application_history = get_json("/applications")

    if "application_history" not in st.session_state:
        st.session_state.application_history = get_json("/applications")

    history = st.session_state.application_history

    if not history:
        return

    applications = history.get("applications", [])

    if not applications:
        st.info("No applications saved yet.")
        return

    for application in applications:
        job = application["selected_job"]
        email = application["generated_email"]

        with st.expander(
            f"{job['title']} at {job['company']} - {application['status']}",
        ):
            st.write(f"Score: {application['score']}")
            st.write(f"Created: {application['created_at']}")
            st.write(f"Location: {job['location']}")

            if job.get("apply_option"):
                st.link_button("Open Apply Link", job["apply_option"])

            st.write("Email Subject")
            st.write(email["subject"])
            st.write("Email Body")
            st.text(email["body"])


def main() -> None:
    st.set_page_config(
        page_title="Autonomous Internship Application Agent",
        layout="wide",
    )
    initialize_state()

    st.title("Autonomous Internship Application Agent")

    page = st.sidebar.radio(
        "Page",
        [
            "Upload Resume",
            "Suggested Roles",
            "Ranked Jobs",
            "Email Preview",
            "Application History",
        ],
    )
    st.sidebar.caption(f"Backend: {API_BASE_URL}")

    if page == "Upload Resume":
        render_upload_resume()
    elif page == "Suggested Roles":
        render_suggested_roles()
    elif page == "Ranked Jobs":
        render_ranked_jobs()
    elif page == "Email Preview":
        render_email_preview()
    else:
        render_application_history()


if __name__ == "__main__":
    main()
