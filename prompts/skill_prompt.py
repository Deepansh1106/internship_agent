SKILL_EXTRACTION_PROMPT = """
You are an expert resume parser.

Extract:

1. Skills
2. Experience
3. Education
4. Projects

Return ONLY valid JSON.

Resume:

{resume_text}

{format_instructions}
"""
