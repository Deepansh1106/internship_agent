# 🤖 Autonomous Internship Application Agent

An end-to-end autonomous agent that reads your resume, extracts your skills and experience, discovers relevant internship roles, searches and ranks live job postings, drafts personalized application emails, and tracks everything you've applied to — with human checkpoints at every key decision point.

Built with **LangGraph** for orchestration and **Streamlit** for the UI, backed by a **FastAPI** service.

---

##  Features

- **Resume Parsing** — Upload a PDF resume and automatically extract skills, work experience, and education.
- **Role Suggestion** — Get AI-suggested job titles/roles based on your extracted profile.
- **Human-in-the-loop Role Selection** — Review and approve which roles the agent should search for.
- **Job Search & Ranking** — Automatically searches for live internship postings and scores each one (0–100) against your profile.
- **Human-in-the-loop Job Selection** — Pick which ranked jobs you actually want to apply to.
- **Email Generation** — Auto-drafts a tailored application email (subject + body) for each selected job.
- **Human Approval** — Review and edit the generated email before it's sent/saved.
- **Application Store & History** — Saves every approved application so you can track what you've applied to.

---

##  How It Works (Agent Graph)

The agent is implemented as a LangGraph state machine with the following flow:

<img width="708" height="1086" alt="image" src="https://github.com/user-attachments/assets/b98e002b-a906-46ea-8e88-c7454cb5c896" />


Every node can also short-circuit directly to `__end__` (e.g., if the user cancels, no jobs match, or an error occurs), which is why the diagram shows dotted edges from each node straight to the end state.

---

##  App Pages (Streamlit)

| Page | Description |
|---|---|
| **Upload Resume** | Upload your resume PDF, process it, and view extracted skills/experience/education |
| **Suggested Roles** | Review roles the agent thinks fit your profile |
| **Ranked Jobs** | Browse live job postings scored out of 100, with location and company details |
| **Email Preview** | View, edit, and save the auto-generated application email for a selected job |
| **Application History** | See a log of all applications you've saved |

---

##  Tech Stack

- **Orchestration:** LangGraph (Python state graph for agent workflow)
- **Backend:** FastAPI (served at `http://127.0.0.1:8000`)
- **Frontend:** Streamlit
- **LLM:** [add your model provider here, e.g. OpenAI / Anthropic Claude / local model]
- **Resume Parsing:** PDF text extraction (e.g. `pypdf` / `pdfplumber`)
- **Job Search:** [add your job search API/source here]

---

##  Project Structure

```
INTERNSHIP-AGENT/
├── backend/
│   ├── __init__.py
│   └── main.py                    # FastAPI app entrypoint
│
├── frontend/
│   ├── __init__.py
│   └── streamlit_app.py           # Streamlit UI
│
├── models/
│   ├── __init__.py
│   └── schemas.py                 # Pydantic schemas / data models
│
├── prompts/
│   ├── __init__.py
│   ├── email_prompt.py            # Prompt template for email_generator
│   ├── job_match_prompt.py        # Prompt template for job_matcher
│   ├── job_role_prompt.py         # Prompt template for job_role_specifier
│   └── skill_prompt.py            # Prompt template for skill_extractor
│
├── tools/
│   ├── __init__.py
│   ├── resume_reader.py           # Node: parses uploaded PDF resume
│   ├── skill_extractor.py         # Node: extracts skills/experience/education
│   ├── job_role_specifier.py      # Node: suggests candidate job roles
│   ├── job_search.py              # Node: searches live job postings
│   ├── job_matcher.py             # Node: scores/ranks jobs against profile
│   ├── email_generator.py         # Node: drafts application emails
│   └── application_store.py       # Node: saves approved applications
│
├── workflows/
│   ├── __init__.py
│   ├── internship_workflow.py     # LangGraph state graph definition (the agent)
│   └── graph_view.py               # Script to render/export the workflow diagram
│
├── tests/
│   ├── __init__.py
│   ├── test_backend_api.py
│   ├── test_internship_workflow.py
│   ├── test_resume_reader.py
│   ├── test_skill_extractor.py
│   ├── test_job_specifier.py
│   ├── test_job_search.py
│   ├── test_job_matcher.py
│   ├── test_email_generator.py
│   └── test_application_store.py
│
├── venv/                          # Virtual environment (not committed)
├── .env                            # API keys / secrets (not committed)
├── .gitignore
├── applications.db                 # SQLite DB storing saved applications
├── workflow.png                    # Exported graph diagram
└── README.md
```

**Module responsibilities:**
- `tools/` — the actual implementation of each LangGraph node (one file per node)
- `prompts/` — LLM prompt templates, kept separate from the node logic that uses them
- `workflows/internship_workflow.py` — wires all the `tools/` nodes together into the LangGraph state graph
- `workflows/graph_view.py` — utility to visualize the graph (produces `workflow.png`)
- `models/schemas.py` — shared Pydantic models used across backend, tools, and frontend
- `applications.db` — persistent storage backing the **Application History** page

---

##  Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file (see `.env.example`) with your API keys:
   ```
   OPENAI_API_KEY=your_key_here
   # or ANTHROPIC_API_KEY=your_key_here
   JOB_SEARCH_API_KEY=your_key_here
   ```

---

##  Usage

1. **Start the backend (FastAPI + LangGraph agent)**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Start the frontend (Streamlit)**
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

3. Open the Streamlit app in your browser (usually `http://localhost:8501`), and:
   - Go to **Upload Resume** → upload your PDF → click **Process Resume**
   - Review **Suggested Roles** and approve the ones you want
   - Check **Ranked Jobs** and select which ones to apply to
   - Preview and edit the email on **Email Preview**, then **Save Application**
   - Track everything under **Application History**

---

##  Roadmap / Ideas

- [ ] Auto-submit applications via job board APIs
- [ ] Support multiple resume versions/profiles
- [ ] Add email sending integration (SMTP/Gmail API)
- [ ] Deduplicate previously applied jobs automatically
- [ ] Add analytics dashboard (application success rate, response tracking)

---

##  License

MIT License

Copyright (c) 2026 Deepansh Kumar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
