import os
import serpapi

from dotenv import load_dotenv

from models.schemas import Job, JobSearchResponse

load_dotenv()

class JobSearcher:

    def __init__(self):
        self.client = serpapi.Client(
            api_key=os.getenv("SERPAPI_API_KEY")
        )

    def search(self, role: str, location: str | None = None, max_results: int = 10):

        try:

            params = {
                "engine": "google_jobs",
                "q": role,
                "google_domain": "google.com",
                "hl": "en"
            }

            if location:
                params["location"] = location

            results = self.client.search(params)

            jobs = []

            for job in results.get("jobs_results", [])[:max_results]:

                apply_option = ""

                if job.get("apply_options"):
                    apply_option = job["apply_options"][0].get("link", "")

                jobs.append(
                    Job(
                        job_id=job.get("job_id", ""),
                        title=job.get("title", ""),
                        company=job.get("company_name", ""),
                        location=job.get("location", ""),
                        description=job.get("description", ""),
                        source=job.get("via", ""),
                        source_link=job.get("source_link", ""),
                        apply_option=apply_option,
                        posted_at=job.get("detected_extensions", {}).get("posted_at", ""),
                        employment_type=job.get("detected_extensions", {}).get("schedule_type", ""),
                        salary=job.get("detected_extensions", {}).get("salary", "")
                    )
                )

            response = JobSearchResponse(jobs=jobs)

            return {
                "success": True,
                "data": response.model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }