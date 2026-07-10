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
            response = self.client.responses.parse(
                model="openai/gpt-oss-20b",
                input=SKILL_EXTRACTION_PROMPT.format(
                    resume_text=resume_text
                ),
                text_format=ResumeProfile,
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
