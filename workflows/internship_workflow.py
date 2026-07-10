from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from tools.application_store import ApplicationStore
from tools.email_generator import EmailGenerator
from tools.job_matcher import JobMatcher
from tools.job_role_specifier import JobRoleSpecifier
from tools.job_search import JobSearcher
from tools.resume_reader import ResumeReader
from tools.skill_extractor import SkillExtractor


class InternshipWorkflowState(TypedDict, total=False):
    resume_file_path: str
    location: str
    max_results: int
    application_db_path: str

    resume_text: str
    candidate_profile: dict[str, Any]
    suggested_roles: list[str]
    selected_role: str
    searched_jobs: list[dict[str, Any]]
    matched_jobs: list[dict[str, Any]]
    selected_matches: list[dict[str, Any]]
    generated_emails: list[dict[str, Any]]
    approved_applications: list[dict[str, Any]]
    stored_applications: list[dict[str, Any]]
    error: str


class InternshipApplicationWorkflow:

    def __init__(
        self,
        skill_extractor: SkillExtractor | None = None,
        job_role_specifier: JobRoleSpecifier | None = None,
        job_searcher: JobSearcher | None = None,
        job_matcher: JobMatcher | None = None,
        email_generator: EmailGenerator | None = None,
        application_store: ApplicationStore | None = None,
    ):
        self.skill_extractor = skill_extractor or SkillExtractor()
        self.job_role_specifier = job_role_specifier or JobRoleSpecifier()
        self.job_searcher = job_searcher or JobSearcher()
        self.job_matcher = job_matcher or JobMatcher()
        self.email_generator = email_generator or EmailGenerator()
        self.application_store = application_store

    @staticmethod
    def _tool_error(result: dict[str, Any]) -> dict[str, Any]:
        return {
            "error": result.get("error", "Unknown workflow error")
        }

    @staticmethod
    def _route_on_error(next_node: str):
        def route(state: InternshipWorkflowState) -> str:
            if state.get("error"):
                return END

            return next_node

        return route

    @staticmethod
    def _resolve_role_selection(
        selected_role: Any,
        roles: list[str],
    ) -> str:
        if isinstance(selected_role, int):
            return roles[selected_role]

        if isinstance(selected_role, dict):
            selected_role = selected_role.get("role")

        if selected_role not in roles:
            raise ValueError(f"Invalid role selection: {selected_role}")

        return selected_role

    @staticmethod
    def _resolve_job_selection(
        selection: Any,
        matched_jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if isinstance(selection, dict):
            selection = selection.get("selected_jobs", [])

        if not isinstance(selection, list):
            raise ValueError("Job selection must be a list.")

        selected_matches = []

        for item in selection:
            if isinstance(item, int):
                selected_matches.append(matched_jobs[item])
                continue

            if isinstance(item, str):
                selected_matches.extend(
                    match
                    for match in matched_jobs
                    if match["job"]["job_id"] == item
                )
                continue

            raise ValueError(f"Invalid job selection: {item}")

        return selected_matches

    @staticmethod
    def _resolve_approval(
        approval: Any,
        generated_emails: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if approval is True:
            return generated_emails

        if approval is False or approval is None:
            return []

        if isinstance(approval, dict):
            approval = approval.get("approved_applications", [])

        if not isinstance(approval, list):
            raise ValueError("Approval must be a boolean or a list.")

        approved_applications = []

        for item in approval:
            if isinstance(item, int):
                approved_applications.append(generated_emails[item])
                continue

            if isinstance(item, str):
                approved_applications.extend(
                    application
                    for application in generated_emails
                    if application["job"]["job_id"] == item
                )
                continue

            raise ValueError(f"Invalid approval selection: {item}")

        return approved_applications

    def read_resume(self, state: InternshipWorkflowState) -> dict[str, Any]:
        result = ResumeReader.extract_text(state["resume_file_path"])

        if not result["success"]:
            return self._tool_error(result)

        return {
            "resume_text": result["text"]
        }

    def extract_skills(self, state: InternshipWorkflowState) -> dict[str, Any]:
        result = self.skill_extractor.extract(state["resume_text"])

        if not result["success"]:
            return self._tool_error(result)

        return {
            "candidate_profile": result["data"]
        }

    def suggest_roles(self, state: InternshipWorkflowState) -> dict[str, Any]:
        result = self.job_role_specifier.suggest(state["candidate_profile"])

        if not result["success"]:
            return self._tool_error(result)

        return {
            "suggested_roles": result["data"]["roles"]
        }

    def human_role_selection(
        self,
        state: InternshipWorkflowState,
    ) -> dict[str, Any]:
        selected_role = interrupt({
            "type": "role_selection",
            "roles": state["suggested_roles"],
            "message": "Select one role to search jobs for."
        })

        try:
            return {
                "selected_role": self._resolve_role_selection(
                    selected_role,
                    state["suggested_roles"],
                )
            }

        except Exception as e:
            return {
                "error": str(e)
            }

    def search_jobs(self, state: InternshipWorkflowState) -> dict[str, Any]:
        result = self.job_searcher.search(
            role=state["selected_role"],
            location=state.get("location"),
            max_results=state.get("max_results", 10),
        )

        if not result["success"]:
            return self._tool_error(result)

        return {
            "searched_jobs": result["data"]["jobs"]
        }

    def match_jobs(self, state: InternshipWorkflowState) -> dict[str, Any]:
        result = self.job_matcher.match(
            profile=state["candidate_profile"],
            jobs=state["searched_jobs"],
        )

        if not result["success"]:
            return self._tool_error(result)

        return {
            "matched_jobs": result["data"]["matched_jobs"]
        }

    def human_job_selection(
        self,
        state: InternshipWorkflowState,
    ) -> dict[str, Any]:
        selected_jobs = interrupt({
            "type": "job_selection",
            "matched_jobs": state["matched_jobs"],
            "message": "Select one or more ranked jobs."
        })

        try:
            return {
                "selected_matches": self._resolve_job_selection(
                    selected_jobs,
                    state["matched_jobs"],
                )
            }

        except Exception as e:
            return {
                "error": str(e)
            }

    @staticmethod
    def route_after_job_selection(state: InternshipWorkflowState) -> str:
        if state.get("error"):
            return END

        if not state.get("selected_matches"):
            return END

        return "email_generator"

    def generate_emails(self, state: InternshipWorkflowState) -> dict[str, Any]:
        generated_emails = []

        for match in state["selected_matches"]:
            result = self.email_generator.generate(
                profile=state["candidate_profile"],
                selected_job=match["job"],
                match_result=match,
            )

            if not result["success"]:
                return self._tool_error(result)

            generated_emails.append({
                "job": match["job"],
                "score": match["score"],
                "email": result["data"]["email"],
            })

        return {
            "generated_emails": generated_emails
        }

    def human_approval(self, state: InternshipWorkflowState) -> dict[str, Any]:
        approval = interrupt({
            "type": "email_approval",
            "generated_emails": state["generated_emails"],
            "message": "Approve generated emails before saving applications."
        })

        try:
            return {
                "approved_applications": self._resolve_approval(
                    approval,
                    state["generated_emails"],
                )
            }

        except Exception as e:
            return {
                "error": str(e)
            }

    @staticmethod
    def route_after_approval(state: InternshipWorkflowState) -> str:
        if state.get("error"):
            return END

        if not state.get("approved_applications"):
            return END

        return "application_store"

    def store_applications(
        self,
        state: InternshipWorkflowState,
    ) -> dict[str, Any]:
        store = self.application_store or ApplicationStore(
            state.get("application_db_path", "applications.db")
        )
        stored_applications = []

        for application in state["approved_applications"]:
            result = store.create_application(
                selected_job=application["job"],
                generated_email=application["email"],
                score=application["score"],
                status="approved",
            )

            if not result["success"]:
                return self._tool_error(result)

            stored_applications.append(result["data"]["application"])

        return {
            "stored_applications": stored_applications
        }

    def compile(self):
        builder = StateGraph(InternshipWorkflowState)

        builder.add_node("resume_reader", self.read_resume)
        builder.add_node("skill_extractor", self.extract_skills)
        builder.add_node("job_role_specifier", self.suggest_roles)
        builder.add_node("human_role_selection", self.human_role_selection)
        builder.add_node("job_search", self.search_jobs)
        builder.add_node("job_matcher", self.match_jobs)
        builder.add_node("human_job_selection", self.human_job_selection)
        builder.add_node("email_generator", self.generate_emails)
        builder.add_node("human_approval", self.human_approval)
        builder.add_node("application_store", self.store_applications)

        builder.add_edge(START, "resume_reader")
        builder.add_conditional_edges(
            "resume_reader",
            self._route_on_error("skill_extractor"),
            {
                "skill_extractor": "skill_extractor",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "skill_extractor",
            self._route_on_error("job_role_specifier"),
            {
                "job_role_specifier": "job_role_specifier",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "job_role_specifier",
            self._route_on_error("human_role_selection"),
            {
                "human_role_selection": "human_role_selection",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "human_role_selection",
            self._route_on_error("job_search"),
            {
                "job_search": "job_search",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "job_search",
            self._route_on_error("job_matcher"),
            {
                "job_matcher": "job_matcher",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "job_matcher",
            self._route_on_error("human_job_selection"),
            {
                "human_job_selection": "human_job_selection",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "human_job_selection",
            self.route_after_job_selection,
            {
                "email_generator": "email_generator",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "email_generator",
            self._route_on_error("human_approval"),
            {
                "human_approval": "human_approval",
                END: END,
            },
        )
        builder.add_conditional_edges(
            "human_approval",
            self.route_after_approval,
            {
                "application_store": "application_store",
                END: END,
            },
        )
        builder.add_edge("application_store", END)

        return builder.compile(checkpointer=MemorySaver())


def build_internship_workflow():
    return InternshipApplicationWorkflow().compile()
