from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from tools.job_search import JobSearcher


def raw_job(job_id: str) -> dict:
    return {
        "job_id": job_id,
        "title": "Software Engineer Intern",
        "company_name": f"Company {job_id}",
        "location": "Remote",
        "description": "Python internship",
        "via": "LinkedIn",
        "source_link": "",
        "apply_options": [],
        "detected_extensions": {},
    }


class TestJobSearcher(TestCase):

    @patch("tools.job_search.serpapi.Client")
    def test_search_uses_next_page_until_max_results(self, mock_client_class):
        client = MagicMock()
        client.search.side_effect = [
            {
                "jobs_results": [raw_job("1")],
                "serpapi_pagination": {"next_page_token": "next-page"},
            },
            {"jobs_results": [raw_job("2"), raw_job("3")]},
        ]
        mock_client_class.return_value = client

        result = JobSearcher().search("Software Engineer Intern", max_results=3)

        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["jobs"]), 3)
        self.assertEqual(client.search.call_count, 2)
        self.assertEqual(client.search.call_args_list[1].args[0]["next_page_token"], "next-page")

    @patch("tools.job_search.serpapi.Client")
    def test_search_returns_available_jobs_when_no_next_page_exists(self, mock_client_class):
        client = MagicMock()
        client.search.return_value = {"jobs_results": [raw_job("1")]}
        mock_client_class.return_value = client

        result = JobSearcher().search("Software Engineer Intern", max_results=10)

        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["jobs"]), 1)
        self.assertEqual(client.search.call_count, 1)


if __name__ == "__main__":
    main()
