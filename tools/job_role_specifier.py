import os
from dotenv import load_dotenv
from openai import OpenAI

from models.schemas import JobRoles
from prompts.job_role_prompt import JOB_ROLE_PROMPT

load_dotenv()


class JobRoleSpecifier:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def suggest(self, profile: dict):

        try:
            response = self.client.responses.parse(
                model="openai/gpt-oss-20b",
                input=JOB_ROLE_PROMPT.format(
                    candidate_profile=profile
                ),
                text_format=JobRoles,
            )

            return {
                "success": True,
                "data": response.output_parsed.model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }