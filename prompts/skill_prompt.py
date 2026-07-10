SKILL_EXTRACTION_PROMPT = """
You are an expert resume parser.

Extract:

1. Skills
2. Experience
3. Education
4. Projects

Instructions:
- Return only valid structured output.
- Do not invent skills, education, projects, or experience.
- Keep each item concise.

Resume:

{resume_text}
"""
