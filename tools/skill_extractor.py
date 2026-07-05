from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser

from models.schemas import ResumeProfile
from prompts.skill_prompt import SKILL_EXTRACTION_PROMPT


class SkillExtractor:

    def __init__(self):
        self.llm = ChatOllama(
            model="qwen3:4b",
            temperature=0
        )
        self.parser = PydanticOutputParser(
            pydantic_object=ResumeProfile
        )
    def extract(self, resume_text: str):
        prompt = SKILL_EXTRACTION_PROMPT.format(
            resume_text=resume_text,
            format_instructions=self.parser.get_format_instructions()
        )
        response = self.llm.invoke(prompt)

        try:
            result = self.parser.parse(response.content)

            return {
                "success": True,
                "data": result.model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }