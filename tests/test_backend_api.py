from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.main import app


class TestBackendApi(TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.profile = {
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
        self.job = {
            "job_id": "1",
            "title": "Backend Engineer Intern",
            "company": "Optiver",
            "location": "Austin",
            "description": "Looking for Python, FastAPI, SQL and Docker.",
            "source": "LinkedIn",
            "source_link": "",
            "apply_option": "https://example.com/apply",
            "posted_at": "2 days ago",
            "employment_type": "Internship",
            "salary": ""
        }
        self.match_result = {
            "job": self.job,
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
        self.email = {
            "subject": "Application for Backend Engineer Intern",
            "body": "Dear Hiring Team,\n\nI am interested in this internship."
        }

    @patch("backend.main.ResumeReader.extract_text")
    def test_upload_resume(self, mock_extract_text):
        mock_extract_text.return_value = {
            "success": True,
            "text": "Sample resume text",
            "error": None
        }

        response = self.client.post(
            "/upload-resume",
            files={
                "file": (
                    "resume.pdf",
                    b"%PDF-1.4 sample",
                    "application/pdf",
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "Sample resume text")

    @patch("backend.main.skill_extractor")
    def test_extract_skills(self, mock_tool):
        mock_tool.extract.return_value = {
            "success": True,
            "data": self.profile
        }

        response = self.client.post(
            "/extract-skills",
            json={
                "resume_text": "Sample resume text"
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["skills"], self.profile["skills"])

    @patch("backend.main.job_role_specifier")
    def test_suggest_roles(self, mock_tool):
        mock_tool.suggest.return_value = {
            "success": True,
            "data": {
                "roles": [
                    "Backend Engineer Intern"
                ]
            }
        }

        response = self.client.post(
            "/suggest-roles",
            json={
                "profile": self.profile
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["roles"], ["Backend Engineer Intern"])

    @patch("backend.main.job_searcher")
    def test_search_jobs(self, mock_tool):
        mock_tool.search.return_value = {
            "success": True,
            "data": {
                "jobs": [
                    self.job
                ]
            }
        }

        response = self.client.post(
            "/search-jobs",
            json={
                "role": "Backend Engineer Intern",
                "location": "Remote",
                "max_results": 5
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["jobs"][0]["company"], "Optiver")

    @patch("backend.main.job_matcher")
    def test_match_jobs(self, mock_tool):
        mock_tool.match.return_value = {
            "success": True,
            "data": {
                "matched_jobs": [
                    self.match_result
                ]
            }
        }

        response = self.client.post(
            "/match-jobs",
            json={
                "profile": self.profile,
                "jobs": [
                    self.job
                ]
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["matched_jobs"][0]["score"], 88)

    @patch("backend.main.email_generator")
    def test_generate_email(self, mock_tool):
        mock_tool.generate.return_value = {
            "success": True,
            "data": {
                "email": self.email
            }
        }

        response = self.client.post(
            "/generate-email",
            json={
                "profile": self.profile,
                "selected_job": self.job,
                "match_result": self.match_result
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["email"]["subject"],
            "Application for Backend Engineer Intern"
        )

    @patch("backend.main.application_store")
    def test_create_application(self, mock_store):
        mock_store.create_application.return_value = {
            "success": True,
            "data": {
                "application": {
                    "id": 1,
                    "selected_job": self.job,
                    "generated_email": self.email,
                    "score": 88,
                    "status": "approved",
                    "created_at": "2026-07-10T00:00:00+00:00"
                }
            }
        }

        response = self.client.post(
            "/applications",
            json={
                "selected_job": self.job,
                "generated_email": self.email,
                "score": 88,
                "status": "approved"
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["application"]["status"], "approved")

    @patch("backend.main.application_store")
    def test_list_applications(self, mock_store):
        mock_store.list_applications.return_value = {
            "success": True,
            "data": {
                "applications": []
            }
        }

        response = self.client.get("/applications")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["applications"], [])

    @patch("backend.main.skill_extractor")
    def test_tool_error_returns_http_400(self, mock_tool):
        mock_tool.extract.return_value = {
            "success": False,
            "error": "Tool failed"
        }

        response = self.client.post(
            "/extract-skills",
            json={
                "resume_text": "Sample resume text"
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Tool failed")
