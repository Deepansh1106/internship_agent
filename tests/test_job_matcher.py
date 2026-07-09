from tools.job_matcher import JobMatcher
import json

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
        "Autonomous Internship Application Agent"
    ]
}

jobs = [
    {
        "job_id": "1",
        "title": "Backend Engineer Intern",
        "company": "Optiver",
        "location": "Austin",

        "description": "Looking for Python, FastAPI, SQL and Docker.",

        "source": "LinkedIn",
        "source_link": "",
        "apply_option": "",
        "posted_at": "2 days ago",
        "employment_type": "Internship",
        "salary": ""
    },
    {
        "job_id": "2",
        "title": "ML Engineer Intern",
        "company": "Adobe",
        "location": "Remote",

        "description": "Machine Learning, TensorFlow, Python.",

        "source": "LinkedIn",
        "source_link": "",
        "apply_option": "",
        "posted_at": "1 day ago",
        "employment_type": "Internship",
        "salary": ""
    }
]

matcher = JobMatcher()

result = matcher.match(profile, jobs)

print(json.dumps(result, indent=4))