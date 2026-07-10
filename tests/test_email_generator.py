from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from models.schemas import GeneratedEmail
from tools.email_generator import EmailGenerator


class TestEmailGenerator(TestCase):

    @patch("tools.email_generator.OpenAI")
    def test_email_generator_returns_structured_email(self, mock_openai):
        profile = {
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

        selected_job = {
            "job_id": "1",
            "title": "Backend Engineer Intern",
            "company": "Optiver",
            "location": "Austin",
            "description": "Looking for Python, FastAPI, SQL and Docker.",
            "source": "LinkedIn",
            "source_link": "",
            "apply_option": "",
            "posted_at": "2 days ago",
            "employment_type": "Internship",
            "salary": ""
        }

        match_result = {
            "score": 88,
            "reasoning": "Strong backend fit with relevant Python and API experience.",
            "strengths": [
                "Python",
                "FastAPI",
                "SQL"
            ],
            "missing_skills": [
                "Docker"
            ]
        }

        mock_client = MagicMock()
        mock_client.responses.parse.return_value = SimpleNamespace(
            output_parsed=GeneratedEmail(
                subject="Application for Backend Engineer Intern",
                body="Dear Hiring Team,\n\nI am interested in the Backend Engineer Intern role."
            )
        )
        mock_openai.return_value = mock_client

        generator = EmailGenerator()
        result = generator.generate(profile, selected_job, match_result)

        self.assertTrue(result["success"])
        self.assertEqual(
            result["data"]["email"]["subject"],
            "Application for Backend Engineer Intern"
        )
        self.assertIn("Backend Engineer Intern", result["data"]["email"]["body"])

    @patch("tools.email_generator.OpenAI")
    def test_email_generator_returns_error_for_invalid_job(self, mock_openai):
        mock_openai.return_value = MagicMock()

        generator = EmailGenerator()
        result = generator.generate(
            profile={},
            selected_job={},
            match_result={},
        )

        self.assertFalse(result["success"])
        self.assertIn("error", result)


if __name__ == "__main__":
    main()
