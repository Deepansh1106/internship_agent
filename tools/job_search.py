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

            jobs = []
            seen_job_ids = set()
            next_page_token = None

            # Google Jobs returns up to 10 results per page. Keep following the
            # pagination token until we have enough jobs or Google has no more.
            while len(jobs) < max_results:
                if next_page_token:
                    params["next_page_token"] = next_page_token

                results = self.client.search(params)
                page_jobs = results.get("jobs_results", [])

                for job in page_jobs:
                    job_id = job.get("job_id", "")
                    unique_id = job_id or "|".join([
                        job.get("title", ""),
                        job.get("company_name", ""),
                        job.get("location", ""),
                    ])

                    if unique_id in seen_job_ids:
                        continue

                    seen_job_ids.add(unique_id)

                    apply_option = ""

                    if job.get("apply_options"):
                        apply_option = job["apply_options"][0].get("link", "")

                    jobs.append(
                        Job(
                            job_id=job_id,
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

                    if len(jobs) == max_results:
                        break

                next_page_token = results.get("serpapi_pagination", {}).get(
                    "next_page_token"
                )

                if not next_page_token or not page_jobs:
                    break

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
