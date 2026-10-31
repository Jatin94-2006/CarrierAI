# CareerAI - Autonomous Multi-Agent Career Readiness & Technical Interview Platform

An end-to-end autonomous multi-agent career acceleration engine built with FastAPI, React (Vite + Tailwind CSS), Supabase Authentication, Edge-TTS, and deterministic ATS evaluation.

---

## Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │              Candidate Inputs                │
                      │         (Resume PDF/Text & Job Spec)         │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │    Agent 1: Deterministic ATS Engine         │
                      │    (100 Synthetic Applicant Benchmarking)    │
                      └──────────────────────┬───────────────────────┘
                                             │
                       ┌─────────────────────┴──────────────────────┐
                       │                                            │
                       ▼ (Simulation Rank <= 75)                    ▼ (Simulation Rank > 75)
          ┌───────────────────────────┐                ┌───────────────────────────┐
          │ Agent 4: Mock Interviewer │                │   Agent 2: Technical Gap  │
          │  (Dynamic Questions, TTS) │                │     Analysis Engine       │
          └─────────────┬─────────────┘                └─────────────┬─────────────┘
                        │                                            │
                        ▼                                            ▼
          ┌───────────────────────────┐                ┌───────────────────────────┐
          │  Agent 2: Post-Interview  │                │  Agent 3: Technical-Only  │
          │   Comprehensive Analysis  │                │   Courses (< 1 Week)      │
          └─────────────┬─────────────┘                └─────────────┬─────────────┘
                        │                                            │
                        ▼                                            ▼
          ┌───────────────────────────┐                ┌───────────────────────────┐
          │ Agent 3: Dual Upskilling  │                │ Agent 5: 30-Day Technical │
          │ (Tech + Behavioral Track) │                │      Learning Plan        │
          └─────────────┬─────────────┘                └───────────────────────────┘
                        │
                        ▼
          ┌───────────────────────────┐
          │ Agent 5: 30-Day Plan &    │
          │   Official PDF Scorecard  │
          └───────────────────────────┘
```

---

## Directory Structure

```text
final/
├── backend/
│   ├── app/                   # Agent 1: Resume Screening, ATS Scorer, 100-Synthetic Benchmark
│   ├── interview_app/         # Agent 4: Spoken Mock Interview, Edge-TTS Audio & STT
│   ├── agent2/                # Agent 2: Technical & Spoken Interview Gap Analysis
│   ├── agent3/                # Agent 3: Fast-Track Micro-Courses (< 1 Week)
│   ├── agent5/                # Agent 5: 30-Day Learning Planner & ReportLab PDF Generator
│   ├── shared_output/         # Pipeline output artifacts
│   ├── uploads/               # Staging uploads
│   ├── server.py              # Unified FastAPI Multi-Agent Backend Server
│   ├── requirements.txt       # Production Python dependencies
│   ├── .env.example           # Reference configuration
│   └── .gitignore             # Python exclusions
│
└── frontend/
    ├── src/                   # React components, pages, hooks, Supabase Auth
    ├── index.html             # Vite SPA entrypoint
    ├── package.json           # Dependencies and build scripts
    ├── package-lock.json      # Locked dependencies
    ├── vite.config.js         # Vite configuration with proxy rules
    ├── tailwind.config.js     # Tailwind CSS theme
    ├── postcss.config.js      # PostCSS configuration
    └── .gitignore             # Node exclusions
```

---

## Getting Started

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

The FastAPI backend will be available at `http://127.0.0.1:8000`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The Vite frontend will be available at `http://127.0.0.1:3000`.
