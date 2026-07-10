import tempfile
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

from langgraph.types import Command

from tools.application_store import ApplicationStore
from workflows.internship_workflow import InternshipApplicationWorkflow


class FakeSkillExtractor:

    def extract(self, resume_text):
        return {
            "success": True,
            "data": {
                "skills": [
                    "Python",
                    "FastAPI",
                    "SQL"
                ],
                "experience": [
                    "Backend Development Intern"
                ],
                "education": [
                    "B.Tech Computer Science"
                ],
                "projects": [
                    "Autonomous Internship Application Agent"
                ]
            }
        }


class FakeJobRoleSpecifier:

    def suggest(self, profile):
        return {
            "success": True,
            "data": {
                "roles": [
                    "Backend Engineer Intern",
                    "Software Engineer Intern"
                ]
            }
        }


class FakeJobSearcher:

    def search(self, role, location=None, max_results=10):
        return {
            "success": True,
            "data": {
                "jobs": [
                    {
                        "job_id": "1",
                        "title": role,
                        "company": "Optiver",
                        "location": location or "Remote",
                        "description": "Looking for Python, FastAPI, SQL and Docker.",
                        "source": "LinkedIn",
                        "source_link": "",
                        "apply_option": "https://example.com/apply",
                        "posted_at": "2 days ago",
                        "employment_type": "Internship",
                        "salary": ""
                    }
                ]
            }
        }


class FakeJobMatcher:

    def match(self, profile, jobs):
        return {
            "success": True,
            "data": {
                "matched_jobs": [
                    {
                        "job": jobs[0],
                        "score": 88,
                        "reasoning": "Strong backend fit.",
                        "strengths": [
                            "Python",
                            "FastAPI",
                            "SQL"
                        ],
                        "missing_skills": [
                            "Docker"
                        ]
                    }
                ]
            }
        }


class FakeEmailGenerator:

    def generate(self, profile, selected_job, match_result):
        return {
            "success": True,
            "data": {
                "email": {
                    "subject": "Application for Backend Engineer Intern",
                    "body": "Dear Hiring Team,\n\nI am interested in this internship."
                }
            }
        }


class TestInternshipWorkflow(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "applications.db"

        self.workflow = InternshipApplicationWorkflow(
            skill_extractor=FakeSkillExtractor(),
            job_role_specifier=FakeJobRoleSpecifier(),
            job_searcher=FakeJobSearcher(),
            job_matcher=FakeJobMatcher(),
            email_generator=FakeEmailGenerator(),
            application_store=ApplicationStore(str(self.db_path)),
        )
        self.graph = self.workflow.compile()
        self.config = {
            "configurable": {
                "thread_id": "workflow-test"
            }
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("workflows.internship_workflow.ResumeReader.extract_text")
    def test_workflow_uses_interrupts_and_stores_application(self, mock_extract_text):
        mock_extract_text.return_value = {
            "success": True,
            "text": "Sample resume text"
        }

        first_result = self.graph.invoke(
            {
                "resume_file_path": "resume.pdf",
                "location": "Remote",
                "max_results": 5,
            },
            self.config,
        )

        self.assertIn("__interrupt__", first_result)
        self.assertEqual(
            first_result["__interrupt__"][0].value["type"],
            "role_selection"
        )

        second_result = self.graph.invoke(
            Command(resume=0),
            self.config,
        )

        self.assertIn("__interrupt__", second_result)
        self.assertEqual(
            second_result["__interrupt__"][0].value["type"],
            "job_selection"
        )

        third_result = self.graph.invoke(
            Command(resume=[0]),
            self.config,
        )

        self.assertIn("__interrupt__", third_result)
        self.assertEqual(
            third_result["__interrupt__"][0].value["type"],
            "email_approval"
        )

        final_result = self.graph.invoke(
            Command(resume=True),
            self.config,
        )

        self.assertEqual(final_result["selected_role"], "Backend Engineer Intern")
        self.assertEqual(len(final_result["selected_matches"]), 1)
        self.assertEqual(len(final_result["generated_emails"]), 1)
        self.assertEqual(len(final_result["stored_applications"]), 1)
        self.assertEqual(
            final_result["stored_applications"][0]["status"],
            "approved"
        )

    @patch("workflows.internship_workflow.ResumeReader.extract_text")
    def test_workflow_stops_on_tool_error(self, mock_extract_text):
        mock_extract_text.return_value = {
            "success": False,
            "error": "File not found"
        }

        result = self.graph.invoke(
            {
                "resume_file_path": "missing.pdf",
            },
            {
                "configurable": {
                    "thread_id": "workflow-error-test"
                }
            },
        )

        self.assertEqual(result["error"], "File not found")
        self.assertNotIn("__interrupt__", result)

    def test_workflow_mermaid_graph_contains_connected_workflow(self):
        mermaid = self.graph.get_graph().draw_mermaid()

        expected_edges = [
            "__start__ --> resume_reader;",
            "resume_reader -.-> skill_extractor;",
            "skill_extractor -.-> job_role_specifier;",
            "job_role_specifier -.-> human_role_selection;",
            "human_role_selection -.-> job_search;",
            "job_search -.-> job_matcher;",
            "job_matcher -.-> human_job_selection;",
            "human_job_selection -.-> email_generator;",
            "email_generator -.-> human_approval;",
            "human_approval -.-> application_store;",
            "application_store --> __end__;",
        ]

        for edge in expected_edges:
            self.assertIn(edge, mermaid)


if __name__ == "__main__":
    main()
