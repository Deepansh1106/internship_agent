from tools.skill_extractor import SkillExtractor


sample_resume = """
Deepansh Kumar

Skills:
Python, FastAPI, SQL, Machine Learning

Projects:
Autonomous Internship Application Agent
Food Delivery Time Prediction

Education:
B.Tech Computer Science

Experience:
Backend Development Intern
"""


extractor = SkillExtractor()

result = extractor.extract(sample_resume)

print(result)