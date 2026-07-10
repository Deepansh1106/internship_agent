import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from models.schemas import (
    EmailGenerationResponse,
    GeneratedEmail,
    Job,
)
from prompts.email_prompt import EMAIL_GENERATION_PROMPT

load_dotenv()


class EmailGenerator:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def generate(
        self,
        profile: dict[str, Any],
        selected_job: dict[str, Any],
        match_result: dict[str, Any],
    ) -> dict[str, Any]:

        try:
            job = Job(**selected_job)

            prompt = EMAIL_GENERATION_PROMPT.format(
                candidate_profile=profile,
                job_title=job.title,
                company=job.company,
                location=job.location,
                job_description=job.description,
                match_score=match_result.get("score", ""),
                match_reasoning=match_result.get("reasoning", ""),
                match_strengths=match_result.get("strengths", []),
                missing_skills=match_result.get("missing_skills", []),
            )

            response = self.client.responses.parse(
                model="openai/gpt-oss-20b",
                input=prompt,
                text_format=GeneratedEmail,
            )

            generated_email = response.output_parsed

            return {
                "success": True,
                "data": EmailGenerationResponse(
                    email=generated_email
                ).model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }
