import tempfile
from pathlib import Path
from unittest import TestCase, main

from tools.application_store import ApplicationStore


class TestApplicationStore(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "applications.db"
        self.store = ApplicationStore(str(self.db_path))

        self.selected_job = {
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

        self.generated_email = {
            "subject": "Application for Backend Engineer Intern",
            "body": "Dear Hiring Team,\n\nI am interested in this internship."
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_is_created_automatically(self):
        self.assertTrue(self.db_path.exists())

    def test_create_and_get_application(self):
        create_result = self.store.create_application(
            selected_job=self.selected_job,
            generated_email=self.generated_email,
            score=88,
            status="pending",
        )

        self.assertTrue(create_result["success"])

        application_id = create_result["data"]["application"]["id"]
        get_result = self.store.get_application(application_id)

        self.assertTrue(get_result["success"])
        self.assertEqual(
            get_result["data"]["application"]["selected_job"]["company"],
            "Optiver"
        )
        self.assertEqual(get_result["data"]["application"]["score"], 88)

    def test_list_applications(self):
        self.store.create_application(
            selected_job=self.selected_job,
            generated_email=self.generated_email,
            score=88,
        )

        result = self.store.list_applications()

        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["applications"]), 1)

    def test_update_application_status(self):
        create_result = self.store.create_application(
            selected_job=self.selected_job,
            generated_email=self.generated_email,
            score=88,
        )
        application_id = create_result["data"]["application"]["id"]

        update_result = self.store.update_application_status(
            application_id=application_id,
            status="applied",
        )

        self.assertTrue(update_result["success"])
        self.assertEqual(
            update_result["data"]["application"]["status"],
            "applied"
        )

    def test_delete_application(self):
        create_result = self.store.create_application(
            selected_job=self.selected_job,
            generated_email=self.generated_email,
            score=88,
        )
        application_id = create_result["data"]["application"]["id"]

        delete_result = self.store.delete_application(application_id)
        get_result = self.store.get_application(application_id)

        self.assertTrue(delete_result["success"])
        self.assertFalse(get_result["success"])

    def test_clear_applications(self):
        self.store.create_application(
            selected_job=self.selected_job,
            generated_email=self.generated_email,
            score=88,
        )
        self.store.create_application(
            selected_job=self.selected_job,
            generated_email=self.generated_email,
            score=90,
        )

        result = self.store.clear_applications()

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["count"], 2)
        self.assertEqual(self.store.list_applications()["data"]["applications"], [])


if __name__ == "__main__":
    main()
