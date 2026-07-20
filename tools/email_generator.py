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

            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "Return only JSON matching the supplied schema.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "application_email",
                        "strict": True,
                        "schema": GeneratedEmail.model_json_schema(),
                    },
                },
            )

            generated_email = GeneratedEmail.model_validate_json(
                response.choices[0].message.content
            )

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
