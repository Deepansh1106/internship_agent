import json
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from tools.job_matcher import JobMatcher


class TestJobMatcher(TestCase):

    @patch("tools.job_matcher.OpenAI")
    def test_matcher_reads_strict_json_response(self, mock_openai):
        job = {
            "job_id": "1",
            "title": "Backend Engineer Intern",
            "company": "Example",
            "location": "Remote",
            "description": "Python and FastAPI internship.",
            "source": "LinkedIn",
            "source_link": "",
            "apply_option": "",
            "posted_at": "Today",
            "employment_type": "Internship",
            "salary": "",
        }
        client = MagicMock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps({
                            "score": 88,
                            "reasoning": "Strong Python and FastAPI fit.",
                            "strengths": ["Python", "FastAPI"],
                            "missing_skills": [],
                        })
                    )
                )
            ]
        )
        mock_openai.return_value = client

        result = JobMatcher().match({"skills": ["Python", "FastAPI"]}, [job])

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["matched_jobs"][0]["score"], 88)
        request = client.chat.completions.create.call_args.kwargs
        self.assertTrue(request["response_format"]["json_schema"]["strict"])


if __name__ == "__main__":
    main()
