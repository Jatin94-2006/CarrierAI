# AI Career Guidance & Job Preparation Platform

> **For New Models:** Read this file completely before doing anything. This is the single source of truth for the entire project. Do NOT ask for code previews — everything you need to understand the project is here. Update this file whenever anything changes or is added.

---

## 📌 Project Overview

A **centralized, multi-agent AI backend platform** that helps students and job seekers prepare for their dream job roles. The system analyzes a user's resume and target Job Description (JD), identifies skill gaps, suggests free learning resources, conducts mock interviews, and generates a personalized learning roadmap.

**No frontend.** Everything runs as:
- Pure **Backend** (FastAPI)
- **Terminal-based CLI** execution
- Data exchange via **standardized JSON contracts**

---

## 🏗️ Architecture Summary

```
User Input (Resume + JD)
        │
        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Pipeline)                    │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Agent 1  │───▶│ Agent 2  │───▶│ Agent 3  │    │ Agent 4  │  │
│  │ Resume   │    │   Gap    │    │  Course  │    │Interview │  │
│  │ Screen   │    │Analysis  │    │Suggestion│    │   Prep   │  │
│  └──────────┘    └────┬─────┘    └──────────┘    └──────────┘  │
│                       │                                          │
│                       │          ┌──────────┐                   │
│                       └─────────▶│ Agent 5  │                   │
│                                  │ Learning │                   │
│                                  │ Planner  │                   │
│                                  └──────────┘                   │
└──────────────────────────────────────────────────────────────────┘
        │
        ▼
  Supabase (PostgreSQL) — Shared DB for all modules
```

**Pattern:** Multi-agent pipeline (sequential, output of one feeds the next)

---

## 🔄 Pipeline Step-by-Step Workflow

### Step 1 — Resume Screening (Module 1)
- **What happens:** User ka raw resume aur JD parse hota hai
- **Input:** Raw resume file + raw JD text
- **Output:**
  - `resume.json` → structured resume data
  - `jd.json` → structured JD data
- **Feeds into:** Module 2 (Gap Analysis)

---

### Step 2 — Gap Analysis (Module 2) ⭐ CORE
- **What happens:** resume.json aur jd.json ko compare karta hai — candidate mein kya missing ya weak hai
- **Input:** `resume.json` + `jd.json`
- **Output:** `gap_report.json` — detailed skill gap analysis
- **Feeds into:** Module 3 (Course Suggestions) + Module 4 (Mock Interview) + Module 5 (Learning Plan)
- **Critical Note:** Yeh module sabse central hai — iska output 3 downstream modules consume karte hain

---

### Step 3 — Course Suggestions (Module 3)
- **What happens:** Gap report + Resume + Interview results consume karke free learning resources recommend karta hai
- **Input:**
  - `gap_report.json` (from Module 2) — kya skills missing hain
  - `resume.json` (from Module 1) — candidate ka existing skill context
  - `interview_report.json` (from Module 4) — interview mein kahan struggle kiya
- **Output:** `courses.json` — free resources mapped to each gap skill
- **Sources:** W3Schools, freeCodeCamp, GeeksForGeeks (GFG), YouTube, docs, etc.
- **Feeds into:** Module 5 (Learning Planner) ONLY

> ⚠️ **Module 4 (Interview) Module 3 se PEHLE chalta hai** — taaki interview ke weak areas bhi course suggestion mein use ho sakein.

---

### Step 4 — Mock Interview (Module 4)
- **What happens:** Resume aur gap report ke basis par technical/HR questions generate karta hai, terminal mein mock interview leta hai
- **Input:** `resume.json` + `gap_report.json` (from Module 1 & 2)
- **Output:** `interview_report.json` — Q&A session, evaluation, weak areas
- **Mode:** Terminal-based interactive session
- **Feeds into:** Module 3 (Course Suggestions)

---

### Step 5 — Improvement / Learning Plan (Module 5)
- **What happens:** Saare gaps aur courses ko mila kar ek actionable roadmap banata hai
- **Input:** `gap_report.json` + `courses.json` (from Module 2 & 3)
- **Output:** `learning_plan.json` — daily/weekly 30-day or 3–6 month roadmap
- **Mode:** Both 30-day (intensive) and 3–6 month (comprehensive) plans

---

## 📊 Data Flow & Screening Gate Diagram

```
[Module 1: Resume & Screening Engine]
  ├── resume.json
  ├── jd.json
  └── screening.json (Rank: 1 to 100)
             │
             ▼
┌────────────────────────────────────────────────────────┐
│ ⭐ MODULE 2: Core Gap Analysis Engine                   │
│                                                        │
│ 1. Resume Gap Analysis -> resume_gap.json              │
│ 2. Screening Gate Check:                               │
│    - Rank 1 to 75  -> QUALIFIED FOR INTERVIEW          │
│    - Rank 76 to 100 -> NO INTERVIEW (Skip to Courses)  │
└───────────────────────────┬────────────────────────────┘
                            │
               Is Rank 1-75?│
            ┌───────────────┴───────────────┐
            │ YES                           │ NO
            ▼                               ▼
   [Module 4: Interview]                    │
     interview.json                         │
            │                               │
            ▼                               │
   [⭐ MODULE 2 (Phase 2)]                   │
   Interview Gap Evaluation                 │
   (Technical + Soft Skills)                │
            │                               │
            ▼ (interview_gap.json)          ▼
   ┌────────────────────────────────────────┴───────────┐
   │ MODULE 3: Course Suggestions                       │
   │ Inputs: resume_gap.json (+ interview_gap.json)     │
   │ Output: courses.json                               │
   └────────────────────────┬───────────────────────────┘
                            │
                            ▼
   ┌────────────────────────────────────────────────────┐
   │ MODULE 5: Learning Planner                         │
   │ Output: learning_plan.json                         │
   └────────────────────────────────────────────────────┘
```

---

## 🤖 Modules / Agents

| # | Agent Name | Module | Status |
|---|-----------|--------|--------|
| 1 | Resume Analysis Agent | Module 1 | 🔲 Pending |
| 2 | Gap Analysis Agent | Module 2 ⭐ Core | 🔲 Pending |
| 3 | Course Suggestion Agent | Module 3 | 🔲 Pending |
| 4 | Interview Preparation Agent | Module 4 | 🔲 Pending |
| 5 | 30-Day / 3–6 Month Learning Planner | Module 5 | 🔲 Pending |

> ⭐ **Module 2 (Gap Analysis Agent) is the core module** — it is the central piece around which others are built.

---

## 🧩 Module Details

### Module 1 — Resume Analysis Agent
- **Input:** Raw resume (PDF/text) + raw JD text
- **Output:** `resume.json` (structured skills, experience, education, projects) + `jd.json`
- **Responsibility:** Parse and normalize resume + JD data for downstream agents

### Module 2 — Gap Analysis Agent ⭐ (Core)
- **Input:** `resume.json` (from Module 1) + `jd.json` (from Module 1)
- **Output:** `gap_report.json` — missing skills, weak areas, keyword mismatches, gap score
- **Responsibility:** Central comparison engine — drives all 3 downstream modules
- **Downstream consumers:** Module 3, Module 4, Module 5

---

## 🔬 Module 2 — Gap Analysis Agent: Detailed Blueprint

> ⚠️ **Critical:** Module 2 is the central bridge of the entire pipeline. If this analysis is wrong, Course Suggestion (Module 3) and Learning Planner (Module 5) both become useless. Accuracy is non-negotiable.

### A. Inputs — What Module 2 Receives (from Module 1)

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | `UUID` (string) | Candidate ki unique ID |
| `resume_id` | `UUID` (string) | Resume ki unique ID |
| `job_id` | `UUID` (string) | Target Job Description ki unique ID |
| `session_id` | `UUID` (string) | Analysis session ki unique ID |
| `candidate_skills` | `List[str]` | e.g. `["Python", "SQL", "Git"]` |
| `jd_required_skills` | `List[str]` | e.g. `["Python", "FastAPI", "Docker", "AWS"]` |
| `candidate_experience` | `float` | Experience in years (e.g. `2.5`) |

**Sample Input JSON:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "resume_id": "r1b2c3d4-e5f6-7890-abcd-ef1234567891",
  "job_id": "j1b2c3d4-e5f6-7890-abcd-ef1234567892",
  "session_id": "s1b2c3d4-e5f6-7890-abcd-ef1234567893",
  "candidate_skills": ["Python", "SQL", "Git"],
  "jd_required_skills": ["Python", "FastAPI", "Docker", "AWS"],
  "candidate_experience": 2.0
}
```

> ⚠️ More input fields may be added as subsequent chunks arrive. Schema will be finalized here.

---

### B. Core Processing & Logic — What Module 2 Must Do

#### 1. Semantic Matching (NOT dumb string matching)
- **No simple `==` comparison** — LLM-powered semantic intelligence required
- **Tech:** `Groq API` + `LangChain`
- **Example:** JD mein `"PostgreSQL"` manga, resume mein sirf `"SQL"` hai
  - Dumb match → ❌ Gap
  - Semantic match → ✅ Intelligently evaluate: *critical gap ya minor discrepancy?*
- LLM decides **how close** the candidate skill is to the JD requirement

#### 2. Skill Categorization (Strict 5-Category Output)

| Category | Description | Example |
|----------|-------------|---------|
| `critical_gaps` | Mandatory core skills — JD ke liye jaan hain, resume se gayab | `Docker`, `AWS` |
| `important_gaps` | Secondary required skills or weak proficiencies | `FastAPI`, `Redis` |
| `optional_gaps` | Nice-to-have bonus skills | `Terraform` |
| `matched_skills` | Skills that successfully matched between resume & JD | `Python`, `SQL` |
| `missing_keywords` | Domain-specific tools/keywords missing | `CI/CD`, `Cloud Deployment` |

#### 3. Improvement Priority Order
- Output must include a **sequenced list** — `improvement_priority_order`
- Order: pehle kaunsi skill sikhni chahiye (critical → important → optional)
- This list directly drives **Module 5 (Learning Planner)** day-by-day schedule

---

### C. Output Contract — CTBF-AI-05 Standard JSON Envelope

> ⚠️ **STRICT FORMAT:** Module 2 MUST return exactly this envelope. Module 3 reads this without any transformation — any deviation will break the pipeline.

**Standard:** `CTBF-AI-05`
**`schema_version`:** `"1.0"`

```json
{
  "user_id": "user_001",
  "resume_id": "resume_001",
  "job_id": "job_001",
  "session_id": "session_001",
  "module": "skill_gap_analysis",
  "status": "completed",
  "data": {
    "critical_gaps": ["Docker", "Kubernetes", "AWS"],
    "important_gaps": ["FastAPI", "Redis"],
    "optional_gaps": ["Terraform"],
    "matched_skills": ["Python", "SQL", "Git"],
    "missing_keywords": ["CI/CD", "Cloud Deployment"],
    "improvement_priority_order": ["Docker", "FastAPI", "AWS", "Kubernetes", "Redis"]
  },
  "created_at": "2026-10-30T10:00:00Z"
}
```

**Output Field Rules:**
| Field | Type | Rule |
|-------|------|------|
| `module` | `str` | Always `"skill_gap_analysis"` |
| `status` | `str` | `"completed"` \| `"failed"` \| `"partial"` |
| `data.critical_gaps` | `List[str]` | Never empty if JD has mandatory skills missing |
| `data.improvement_priority_order` | `List[str]` | Must be ordered — critical first |
| `created_at` | `str` | ISO 8601 UTC timestamp |

---

### Module 2 — LLM & Tech Details

| Component | Technology |
|-----------|-----------|
| LLM Provider | **Groq API** |
| LLM Framework | **LangChain** |
| Matching Strategy | Semantic (LLM-based), NOT string equality |
| Output Standard | CTBF-AI-05 JSON Envelope |

### Module 3 — Course Suggestion Agent
- **Input:** `gap_report.json` (from Module 2)
- **Output:** `courses.json` — free resources per gap skill
- **Sources:** W3Schools, freeCodeCamp, GFG, YouTube, official docs
- **Responsibility:** Map each skill gap to free/freemium learning material

### Module 4 — Interview Preparation Agent
- **Input:** `resume.json` (Module 1) + `gap_report.json` (Module 2)
- **Output:** `interview_report.json` — Q&A, evaluation, weak area summary
- **Mode:** Terminal-based interactive mock interview session
- **Responsibility:** Generate technical/HR questions, evaluate user answers

### Module 5 — Learning Planner (30-Day / 3–6 Month)
- **Input:** `gap_report.json` (Module 2) + `courses.json` (Module 3)
- **Output:** `learning_plan.json` — day-by-day or week-by-week actionable roadmap
- **Plans:** 30-day (intensive sprint) and 3–6 month (comprehensive track)
- **Responsibility:** Generate structured, time-bound personalized learning plans

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | **FastAPI** (Python) |
| Database | **Supabase** (PostgreSQL) |
| ORM | **SQLAlchemy** |
| Validation | **Pydantic** (mandatory on all I/O) |
| AI / LLM Provider | **Groq API** — model: `llama-3.3-70b-versatile` |
| LLM Framework | **LangChain** |
| Execution | Terminal / CLI |
| Data Format | JSON (strict CTBF-AI-05 contracts between modules) |
| Agent Pattern | Multi-agent Pipeline |

---

## 📂 Project Structure (Planned)

```
gap analysis/
│
├── PROJECT.md                  ← This file (source of truth)
│
├── main.py                     ← FastAPI app entry point
├── pipeline.py                 ← Agent pipeline orchestrator
│
├── agents/
│   ├── resume_agent.py         ← Module 1
│   ├── gap_analysis_agent.py   ← Module 2 (Core)
│   ├── course_agent.py         ← Module 3
│   ├── interview_agent.py      ← Module 4
│   └── planner_agent.py        ← Module 5
│
├── models/
│   └── schemas.py              ← Pydantic models / JSON contracts
│
├── db/
│   └── supabase_client.py      ← Supabase connection & queries
│
├── utils/
│   └── helpers.py
│
├── cli/
│   └── run_pipeline.py         ← Terminal CLI entry point
│
├── .env                        ← API keys, Supabase URL/key
└── requirements.txt
```

---

## 🔗 JSON Contract Flow (Between Modules)

```
Module 1 Output → Module 2 Input
{
  "user_id": "uuid",
  "skills": ["Python", "SQL", ...],
  "experience_years": 2,
  "education": "B.Tech CS",
  "projects": [...],
  "raw_resume_text": "..."
}

Module 2 Output → Module 3 & 4 & 5 Input
{
  "user_id": "uuid",
  "jd_title": "Data Engineer",
  "required_skills": [...],
  "user_skills": [...],
  "missing_skills": [...],
  "gap_score": 0.65,
  "keyword_mismatches": [...]
}
```

> ⚠️ Exact schema will be finalized and updated here as modules are built.

---

## 🗄️ Database (Supabase / PostgreSQL)

- **All 5 modules share a single Supabase instance**
- Each module reads/writes to its own table(s)
- Tables planned (to be detailed in next chunks):
  - `users`
  - `resumes`
  - `gap_reports`
  - `course_suggestions`
  - `interview_sessions`
  - `learning_plans`

---

## 🔑 Supabase Configuration

| Key | Value |
|-----|-------|
| **Project ID** | `yvdpybqlvjgemcltqhjn` |
| **Supabase URL** | `https://yvdpybqlvjgemcltqhjn.supabase.co` |
| **Publishable (Anon) Key** | `sb_publishable_0hBHdPMw-97hFVQBZEvErw_xZbAwxW0` |
| **Secret Key** | `sb_secret_KEY_HERE` *(store in `.env` only — never commit)* |

> [!CAUTION] Never hardcode these keys in source code. Always read from `.env`. The secret key must never be committed to version control.

### Database Tables Schema

#### `users` table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `resumes` table
```sql
CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  raw_text TEXT NOT NULL,
  parsed_data JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `job_descriptions` table
```sql
CREATE TABLE job_descriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT,
  raw_text TEXT NOT NULL,
  parsed_data JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `gap_reports` table
```sql
CREATE TABLE gap_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  resume_id UUID REFERENCES resumes(id),
  job_id UUID REFERENCES job_descriptions(id),
  session_id UUID DEFAULT gen_random_uuid(),
  report_data JSONB NOT NULL,
  schema_version TEXT DEFAULT '1.0',
  status TEXT DEFAULT 'completed',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `course_suggestions` table
```sql
CREATE TABLE course_suggestions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  gap_report_id UUID REFERENCES gap_reports(id),
  courses_data JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `interview_sessions` table
```sql
CREATE TABLE interview_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  gap_report_id UUID REFERENCES gap_reports(id),
  resume_id UUID REFERENCES resumes(id),
  session_data JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

#### `learning_plans` table
```sql
CREATE TABLE learning_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  gap_report_id UUID REFERENCES gap_reports(id),
  course_suggestion_id UUID REFERENCES course_suggestions(id),
  plan_data JSONB NOT NULL,
  plan_type TEXT CHECK (plan_type IN ('30_day', '3_month', '6_month')),
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## 📋 Development Rules (For All Models Working on This)

1. **Read this file first** before writing any code
2. **Update this file** whenever a new module, schema, table, or architectural decision is made
3. **No frontend** — do not suggest or create any UI/HTML/CSS
4. **Strict JSON contracts** — all inter-module data must match defined schemas
5. **CLI-first** — all testing and execution happens via terminal
6. **One shared DB** — Supabase for all modules, no separate databases
7. **Free resources only** — course suggestions must be free/freemium
8. **Mark module status** in the table above as work progresses: 🔲 Pending → 🔄 In Progress → ✅ Done

---

## 📐 CTBF-AI-05 — Common Technical Standards & Guidelines

> These standards are **mandatory** for all team members / all modules. Integration-time conflicts will arise if these are not followed.

### 1. Tech Stack (Locked)

| Component | Technology | Notes |
|-----------|-----------|-------|
| Language | **Python** | Only language allowed |
| Backend | **FastAPI** | All API endpoints here |
| Database | **Supabase** (PostgreSQL) | One shared project |
| ORM | **SQLAlchemy** | For DB interactions |
| Validation | **Pydantic** | Mandatory on ALL inputs & outputs |
| LLM Provider | **Groq API** | Model: `llama-3.3-70b-versatile` |
| LLM Framework | **LangChain** | For prompt chaining & agent logic |

### 2. Database Rules

| Rule | Detail |
|------|--------|
| **Single instance** | One shared Supabase project — no separate DBs per module |
| **Primary Keys** | ALL tables must use `UUID` primary keys (no integer IDs) |
| **JSON storage** | Use `JSONB` columns for any JSON/dict data (not `TEXT`) |
| **No cross-module direct DB calls** | Modules communicate via JSON contracts, not direct table reads of another module's data |

### 3. Validation Rules

- **Pydantic models are mandatory** for every incoming request AND every outgoing response
- No raw dicts passed between modules — always serialize/deserialize through Pydantic
- All schemas defined in `models/schemas.py`

### 4. GitHub Workflow

| Rule | Detail |
|------|--------|
| **Module 2 branch** | `module-2-skill-gap` |
| **Branch isolation** | Do NOT touch another module's branch without explicit permission |
| **No direct push to main** | Always work on designated branch |

### 5. Terminal Testing Protocol

- **No UI** — zero HTML/CSS/JS, no Streamlit, no Gradio
- Testing done exclusively via terminal using `terminal_test.py`
- `terminal_test.py` sends mock payloads to the module and verifies JSON response
- Every module must have its own `terminal_test.py` at its root

**Example test command:**
```bash
python terminal_test.py
# Expected: CTBF-AI-05 compliant JSON printed to stdout
```

---

## 📥 Prompt Chunks Status

User is providing project details in multiple chunks. Track intake below:

| Chunk | Topic | Status |
|-------|-------|--------|
| Chunk 1 | Overall Project Summary | ✅ Received |
| Chunk 2 | 5-Agent Architecture & Pipeline Workflow | ✅ Received |
| Chunk 3 | Module 2 Detailed Blueprint — Part A (Inputs) | ✅ Received |
| Chunk 3b | Module 2 Blueprint — Part B (Logic) + Part C (Output Contract) | ✅ Received |
| Chunk 4 | Common Technical Standards & Guidelines (CTBF-AI-05) | ✅ Received |
| Chunk 5 | Supabase Config & DB Schema | ✅ Received |

---

*Last updated: 2026-10-30 (Chunk 5 added — Supabase Config & DB Schema; all project files created) | Updated by: Antigravity AI*
