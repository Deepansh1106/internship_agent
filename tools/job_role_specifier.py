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
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "Return only JSON matching the supplied schema.",
                    },
                    {
                        "role": "user",
                        "content": JOB_ROLE_PROMPT.format(candidate_profile=profile),
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "job_roles",
                        "strict": True,
                        "schema": JobRoles.model_json_schema(),
                    },
                },
            )
            roles = JobRoles.model_validate_json(response.choices[0].message.content)

            return {
                "success": True,
                "data": roles.model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }
