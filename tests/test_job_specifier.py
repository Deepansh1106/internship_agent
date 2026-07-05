from tools.job_role_specifier import JobRoleSpecifier

profile = {
    "skills": [
        "Python",
        "FastAPI",
        "SQL",
        "Machine Learning"
    ],
    "experience": [
        "Backend Development Intern"
    ],
    "education": [
        "B.Tech Computer Science"
    ],
    "projects": [
        "Autonomous Internship Application Agent",
        "Food Delivery Time Prediction"
    ]
}

tool = JobRoleSpecifier()

result = tool.suggest(profile)

print(result)