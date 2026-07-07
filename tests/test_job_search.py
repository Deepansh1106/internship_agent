from tools.job_search import JobSearcher
import json
searcher = JobSearcher()

response = searcher.search("Software Engineer Intern")

print(json.dumps(response, indent=4))