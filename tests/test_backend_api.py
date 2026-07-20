from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


class TestBackendApi(TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch("backend.main.workflow")
    def test_start_workflow_returns_graph_interrupt(self, mock_workflow):
        mock_workflow.invoke.return_value = {
            "candidate_profile": {"skills": ["Python"]},
            "__interrupt__": [
                SimpleNamespace(value={
                    "type": "role_selection",
                    "roles": ["Backend Engineer Intern"],
                    "message": "Select one role to search jobs for.",
                })
            ],
        }

        response = self.client.post(
            "/workflow/start",
            data={"location": "Remote", "max_results": 5},
            files={"file": ("resume.pdf", b"%PDF-1.4 sample", "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["interrupt"]["type"], "role_selection")
        self.assertEqual(response.json()["state"]["candidate_profile"]["skills"], ["Python"])
        mock_workflow.invoke.assert_called_once()

    @patch("backend.main.workflow")
    def test_resume_workflow_passes_human_answer_to_graph(self, mock_workflow):
        mock_workflow.invoke.return_value = {
            "stored_applications": [],
        }

        response = self.client.post(
            "/workflow/resume",
            json={
                "thread_id": "test-thread",
                "resume_value": "Backend Engineer Intern",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["thread_id"], "test-thread")
        self.assertIsNone(response.json()["interrupt"])
        mock_workflow.invoke.assert_called_once()

    @patch("backend.main.application_store")
    def test_list_applications_is_read_only_endpoint(self, mock_store):
        mock_store.list_applications.return_value = {
            "success": True,
            "data": {"applications": []},
        }

        response = self.client.get("/applications")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"applications": []})

    @patch("backend.main.application_store")
    def test_clear_applications(self, mock_store):
        mock_store.clear_applications.return_value = {
            "success": True,
            "data": {"deleted": True, "count": 2},
        }

        response = self.client.delete("/applications")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"deleted": True, "count": 2})


if __name__ == "__main__":
    import unittest
    unittest.main()
