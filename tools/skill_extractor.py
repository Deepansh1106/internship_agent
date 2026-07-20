import os

from dotenv import load_dotenv
from openai import OpenAI

from models.schemas import ResumeProfile
from prompts.skill_prompt import SKILL_EXTRACTION_PROMPT

load_dotenv()


class SkillExtractor:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def extract(self, resume_text: str):

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
                        "content": SKILL_EXTRACTION_PROMPT.format(resume_text=resume_text),
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "resume_profile",
                        "strict": True,
                        "schema": ResumeProfile.model_json_schema(),
                    },
                },
            )
            profile = ResumeProfile.model_validate_json(
                response.choices[0].message.content
            )

            return {
                "success": True,
                "data": profile.model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }
