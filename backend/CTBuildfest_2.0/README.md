# CTBF-AI-05: Module 1 – Resume Screening, ATS Matching & Synthetic Candidate Ranking

Production-grade Python/FastAPI backend service for **CTBF-AI-05: Resume–Job Matching and Skill-Gap Coach for Tier-2 Graduates**.

Module 1 serves as the foundational evaluation gateway of the platform, performing multi-format document parsing, deterministic explainable ATS matching, mandatory requirements validation, 100-synthetic candidate benchmarking, and standardized payload distribution to Modules 2, 3, 4, and 5.

---

## 🌟 Core Features

1. **Multi-Format Ingestion**:
   - Accepts **PDF** (PyMuPDF with automatic OCR scan detection and fallback), **DOCX** (python-docx), and **JSON** resumes.
   - Accepts Job Descriptions in **plain text** or **structured JSON**.
2. **Deterministic, Explainable ATS Scoring**:
   - 100% computed in Python across 7 configurable weight categories summing to 100 points:
     - **Required Skills & Keywords (35%)**
     - **Preferred Skills (15%)**
     - **Relevant Experience (15%)** (Non-overlapping calendar dates; entry-level parity for freshers)
     - **Projects & Practical Evidence (15%)**
     - **Education & Qualifications (10%)** (Prestige-neutral STEM alignment)
     - **Certifications (5%)**
     - **Job-Title & Role Relevance (5%)**
   - Strictly reproducible: identical inputs yield identical outputs.
3. **Mandatory Requirement Verification**:
   - Evaluated as an independent verification gate: `MET`, `NOT_MET`, or `UNVERIFIED` (unmentioned criteria are marked unverified rather than disqualifying).
4. **100 Synthetic Candidate Benchmarking Pool**:
   - Dynamically generates exactly **100 realistic candidate profiles** across 7 competency bands:
     - Very High: 10
     - High: 20
     - Upper-Middle: 20
     - Middle: 20
     - Lower-Middle: 15
     - Low: 10
     - Very Low: 5
   - Evaluated with the **exact same deterministic ATS engine** as the real candidate.
   - Computes fair percentile: $\text{Percentile} = \left(\frac{\text{Synthetic Candidates Below}}{100}\right) \times 100$.
5. **Standardized Inter-Module Contracts**:
   - Exposes dedicated endpoints for **Module 2** (Skill Gap Analysis), **Module 3** (Course Recommendations), **Module 4** (Mock Interview), and **Module 5** (30-Day Improvement Plan).

---

## 🛠 Technology Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI, Uvicorn
- **Data Validation:** Pydantic v2, Pydantic-Settings
- **ORM & Database:** SQLAlchemy 2.0, Alembic, PostgreSQL / Supabase (with automatic SQLite local fallback)
- **AI / LLM Orchestration:** Groq API (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`)
- **Document Extractors:** PyMuPDF (`fitz`), `python-docx`, Tesseract OCR Fallback
- **Data & Metrics:** NumPy, Scikit-learn
- **Testing:** Pytest

---

## 🚀 Quickstart & Setup

### 1. Clone & Environment Setup
```bash
git clone <repo-url>
cd CTBuildfest_2.0
python -m venv .venv

# Windows Powershell
.venv\Scripts\Activate.ps1

# Linux / MacOS
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your credentials when ready:
```ini
GROQ_API_KEY="gsk_your_groq_api_key_here"
DATABASE_URL="postgresql+psycopg2://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres"
```
*(Note: If no Supabase or Groq credentials are provided, the service automatically runs locally with SQLite and deterministic heuristic models, so all endpoints and tests function out-of-the-box.)*

---

### 4. Database Migrations (Alembic)
Run migrations to set up the database schema:
```bash
alembic upgrade head
```

---

## 💻 Running the Application

Start the server using the entrypoint:
```bash
python run.py
```
Or with Uvicorn:
```bash
uvicorn app.main:app --app-dir module_1_resume_screening --host 0.0.0.0 --port 8000 --reload
```

- **Interactive API Documentation (Swagger):** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`
- **Health Check:** `http://127.0.0.1:8000/health`

---

## 🧪 Running Automated Tests & Evaluation Framework

### 1. Test Suite
Run the 26 automated tests covering multi-format parsing, ATS determinism, fresher parity, 100-persona pool, ranking percentiles, reliability metrics, and API integrations:
```bash
python -m pytest -v
```

### 2. Evaluation & Reliability Framework (Section 18)
Execute the benchmark evaluation framework to calculate Precision, Recall, F1, Exact Match, Evidence Veracity, MAE, Spearman $\rho$, Kendall $\tau$, NDCG@5, NDCG@10, and Expected Calibration Error (ECE):
```bash
python -m module_1_resume_screening.app.evaluation.runner
```

---

## 📡 API Endpoints Overview

All endpoints return data wrapped in the standardized response envelope:
```json
{
  "schema_version": "1.0",
  "user_id": "...",
  "resume_id": "...",
  "job_id": "...",
  "session_id": "...",
  "module": "resume_screening",
  "status": "completed",
  "data": { ... },
  "created_at": "2026-10-30T10:00:00Z"
}
```

### 1. Resume Endpoints
- `POST /api/v1/screening/resume/upload`: Upload PDF, DOCX, or JSON resume.
- `POST /api/v1/screening/resume/parse`: Parse existing resume.
- `GET /api/v1/screening/resume/{resume_id}`: Retrieve resume metadata.
- `GET /api/v1/screening/resume/{resume_id}/extraction`: Retrieve structured JSON extraction with evidence snippets.

### 2. Job Description Endpoints
- `POST /api/v1/screening/job/parse`: Parse raw text without saving.
- `POST /api/v1/screening/job`: Create and persist Job Description.
- `GET /api/v1/screening/job/{job_id}`: Retrieve structured Job Description.

### 3. Screening & Ranking Endpoints
- `POST /api/v1/screening/analyze`: Run screening session for stored resume and job IDs.
- `POST /api/v1/screening/analyze-json`: Run screening directly on JSON payloads.
- `GET /api/v1/screening/{session_id}`: Get screening session status.
- `GET /api/v1/screening/{session_id}/score`: Get ATS score and 7-component weight breakdown.
- `GET /api/v1/screening/{session_id}/report`: Get full comprehensive screening report.
- `GET /api/v1/screening/{session_id}/ranking`: Get candidate rank and percentile.
- `GET /api/v1/screening/{session_id}/distribution`: Get score distribution and competency band stats.
- `GET /api/v1/screening/{session_id}/synthetic-candidates`: Get the 100 benchmark candidates generated for this session.

### 4. Inter-Module Integration Endpoints
- `GET /api/v1/screening/{session_id}/skill-gap-input`: Standardized payload for **Module 2** (Skill Gap Analysis).
- `GET /api/v1/screening/{session_id}/course-input`: Standardized payload for **Module 3** (Course Recommendations).
- `GET /api/v1/screening/{session_id}/interview-input`: Standardized payload for **Module 4** (Mock Interview).
- `GET /api/v1/screening/{session_id}/improvement-plan-input`: Standardized payload for **Module 5** (30-Day Improvement Plan).
