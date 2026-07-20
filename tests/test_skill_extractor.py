import json
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from models.schemas import ResumeProfile
from tools.skill_extractor import SkillExtractor


class TestSkillExtractor(TestCase):

    @patch("tools.skill_extractor.OpenAI")
    def test_skill_extractor_returns_structured_profile(self, mock_openai):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps({
                            "skills": ["Python", "FastAPI", "SQL", "Machine Learning"],
                            "experience": ["Backend Development Intern"],
                            "education": ["B.Tech Computer Science"],
                            "projects": ["Autonomous Internship Application Agent"],
                        })
                    )
                )
            ]
        )
        mock_openai.return_value = mock_client

        extractor = SkillExtractor()
        result = extractor.extract("Sample resume text")

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["skills"][0], "Python")
        mock_client.chat.completions.create.assert_called_once()

    @patch("tools.skill_extractor.OpenAI")
    def test_skill_extractor_returns_error_on_failure(self, mock_openai):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("LLM failed")
        mock_openai.return_value = mock_client

        extractor = SkillExtractor()
        result = extractor.extract("Sample resume text")

        self.assertFalse(result["success"])
        self.assertIn("LLM failed", result["error"])


if __name__ == "__main__":
    main()
