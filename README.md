# 🤖 Autonomous Internship Application Agent

An end-to-end autonomous agent that reads your resume, extracts your skills and experience, discovers relevant internship roles, searches and ranks live job postings, drafts personalized application emails, and tracks everything you've applied to — with human checkpoints at every key decision point.

Built with **LangGraph** for orchestration and **Streamlit** for the UI, backed by a **FastAPI** service.

---

## ✨ Features

- **Resume Parsing** — Upload a PDF resume and automatically extract skills, work experience, and education.
- **Role Suggestion** — Get AI-suggested job titles/roles based on your extracted profile.
- **Human-in-the-loop Role Selection** — Review and approve which roles the agent should search for.
- **Job Search & Ranking** — Automatically searches for live internship postings and scores each one (0–100) against your profile.
- **Human-in-the-loop Job Selection** — Pick which ranked jobs you actually want to apply to.
- **Email Generation** — Auto-drafts a tailored application email (subject + body) for each selected job.
- **Human Approval** — Review and edit the generated email before it's sent/saved.
- **Application Store & History** — Saves every approved application so you can track what you've applied to.

---

## 🧠 How It Works (Agent Graph)

The agent is implemented as a LangGraph state machine with the following flow:

```
__start__
   │
   ▼
resume_reader          → parses the uploaded PDF resume
   │
   ▼
skill_extractor         → extracts skills, experience, education
   │
   ▼
job_role_specifier      → suggests candidate job roles/titles
   │
   ▼
human_role_selection    → 🧑 user approves/edits suggested roles
   │
   ▼
job_search               → searches live postings for approved roles
   │
   ▼
job_matcher              → scores/ranks jobs against the resume profile
   │
   ▼
human_job_selection      → 🧑 user selects jobs to apply to
   │
   ▼
email_generator           → drafts a tailored application email per job
   │
   ▼
human_approval             → 🧑 user reviews/edits the email
   │
   ▼
application_store          → saves the approved application
   │
   ▼
__end__
```

Every node can also short-circuit directly to `__end__` (e.g., if the user cancels, no jobs match, or an error occurs), which is why the diagram shows dotted edges from each node straight to the end state.

---

## 🖥️ App Pages (Streamlit)

| Page | Description |
|---|---|
| **Upload Resume** | Upload your resume PDF, process it, and view extracted skills/experience/education |
| **Suggested Roles** | Review roles the agent thinks fit your profile |
| **Ranked Jobs** | Browse live job postings scored out of 100, with location and company details |
| **Email Preview** | View, edit, and save the auto-generated application email for a selected job |
| **Application History** | See a log of all applications you've saved |

---

## 🛠️ Tech Stack

- **Orchestration:** LangGraph (Python state graph for agent workflow)
- **Backend:** FastAPI (served at `http://127.0.0.1:8000`)
- **Frontend:** Streamlit
- **LLM:** [add your model provider here, e.g. OpenAI / Anthropic Claude / local model]
- **Resume Parsing:** PDF text extraction (e.g. `pypdf` / `pdfplumber`)
- **Job Search:** [add your job search API/source here]

---

## 📂 Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app entrypoint
│   ├── graph.py             # LangGraph workflow definition
│   ├── nodes/                # Individual node implementations
│   │   ├── resume_reader.py
│   │   ├── skill_extractor.py
│   │   ├── job_role_specifier.py
│   │   ├── job_search.py
│   │   ├── job_matcher.py
│   │   ├── email_generator.py
│   │   └── application_store.py
│   └── models.py             # Pydantic schemas
├── frontend/
│   └── app.py                 # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

*(Adjust this tree to match your actual folder layout.)*

---

## ⚙️ Installation

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

## ▶️ Usage

1. **Start the backend (FastAPI + LangGraph agent)**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

2. **Start the frontend (Streamlit)**
   ```bash
   streamlit run frontend/app.py
   ```

3. Open the Streamlit app in your browser (usually `http://localhost:8501`), and:
   - Go to **Upload Resume** → upload your PDF → click **Process Resume**
   - Review **Suggested Roles** and approve the ones you want
   - Check **Ranked Jobs** and select which ones to apply to
   - Preview and edit the email on **Email Preview**, then **Save Application**
   - Track everything under **Application History**

---

## 🗺️ Roadmap / Ideas

- [ ] Auto-submit applications via job board APIs
- [ ] Support multiple resume versions/profiles
- [ ] Add email sending integration (SMTP/Gmail API)
- [ ] Deduplicate previously applied jobs automatically
- [ ] Add analytics dashboard (application success rate, response tracking)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a PR or issue.

---

## 📄 License

[Add your license here, e.g. MIT]
