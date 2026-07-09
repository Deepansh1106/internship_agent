import os

from dotenv import load_dotenv
from openai import OpenAI

from models.schemas import (
    Job,
    MatchEvaluation,
    JobRecommendation,
    JobMatchResponse,
)

from prompts.job_match_prompt import JOB_MATCH_PROMPT

load_dotenv()


class JobMatcher:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def match(self, profile: dict, jobs: list[dict]):

        try:

            recommendations = []

            for job in jobs:

                prompt = JOB_MATCH_PROMPT.format(
                    candidate_profile=profile,
                    job_title=job["title"],
                    company=job["company"],
                    job_description=job["description"],
                )

                response = self.client.responses.parse(
                    model="openai/gpt-oss-20b",
                    input=prompt,
                    text_format=MatchEvaluation,
                )

                evaluation = response.output_parsed

                recommendation = JobRecommendation(
                    job=Job(**job),
                    score=evaluation.score,
                    reasoning=evaluation.reasoning,
                    strengths=evaluation.strengths,
                    missing_skills=evaluation.missing_skills,
                )

                recommendations.append(recommendation)

            recommendations.sort(
                key=lambda recommendation: recommendation.score,
                reverse=True,
            )

            return {
                "success": True,
                "data": JobMatchResponse(
                    matched_jobs=recommendations
                ).model_dump()
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }