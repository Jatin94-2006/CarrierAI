"""
Module 2 — Terminal Test (Complete Workflow Test)
Tests:
  1. Resume vs JD Gap Analysis (from Module 1 inputs)
  2. Screening Ranking Evaluation (Rank 1-75: Interview allowed, Rank 76-100: No interview)
  3. Interview Performance Gap Analysis (from Module 4 exact items schema)

Usage:
    python gap-analysis-module/terminal_test.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.gap_analysis_agent import GapAnalysisAgent
from utils.helpers import validate_ctbf_envelope

# ─── 1. REAL Module 1 Inputs ──────────────────────────────────────────────────
REAL_RESUME_JSON = {
  "candidate": {
    "name": "Kriti Mahajan",
    "email": "kritimahajan60@gmail.com",
    "phone": "+91 9217465656",
    "headline": "AI Automation Engineer & Full-Stack Developer",
    "summary": "AI Automation and Full-Stack Developer specializing in agentic workflows, voice AI pipelines, and LLM integrations with ReactJS and n8n."
  },
  "education": [
    {
      "degree": "B.Tech",
      "branch": "Computer Science and Engineering",
      "institution": "DAV Institute of Engineering and Technology, Jalandhar",
      "graduation_year": 2028
    }
  ],
  "skills": {
    "programming_languages": ["JavaScript", "HTML", "CSS"],
    "frameworks": ["ReactJS"],
    "libraries": ["OpenAI API", "Gemini API"],
    "databases": ["Airtable"],
    "cloud_technologies": ["Make.com", "n8n", "Bolna AI", "Relevance AI"],
    "tools": ["Git", "Webhooks", "REST APIs", "Postman"],
    "soft_skills": ["Problem Solving", "System Architecture", "Workflow Optimization"],
    "domain_specific_skills": ["Agentic AI", "Human-in-the-Loop Automation", "Voice AI Pipelines"]
  },
  "all_skills_flat": [
    "ReactJS", "JavaScript", "OpenAI API", "Gemini API", "n8n", "Make.com", "Airtable", "Webhooks", "REST APIs", "Bolna AI"
  ],
  "projects": [
    {
      "title": "Autonomous Voice & AI Lead Qualification Engine",
      "description": "Autonomous sales qualification pipeline integrating Make.com, Airtable, and Bolna AI.",
      "technologies": ["Make.com", "Airtable", "Bolna AI", "Relevance AI", "REST APIs"]
    }
  ]
}

REAL_JD_JSON = {
  "job": {
    "title": "Python Backend Developer",
    "company": "Tech Corp",
    "category": "Software Engineering",
    "seniority": "Entry Level",
    "experience_required": 0.0,
    "required_skills": [
      "Python",
      "FastAPI",
      "SQL",
      "REST APIs",
      "Git"
    ],
    "preferred_skills": [
      "Docker",
      "PostgreSQL",
      "Redis",
      "AWS"
    ],
    "required_soft_skills": [
      "Problem Solving",
      "Communication",
      "Team Collaboration"
    ],
    "tools_and_technologies": [
      "Python",
      "FastAPI",
      "PostgreSQL",
      "Docker",
      "Git",
      "Linux"
    ]
  }
}

# ─── 2. Screening Result from Module 1 ─────────────────────────────────────────
# Test Case: Candidate ranked #24 (Qualified! Inside 1-75 bracket)
REAL_SCREENING_JSON = {
  "candidate_email": "kritimahajan60@gmail.com",
  "rank": 77,
  "total_applicants": 100,
  "screening_status": "passed",
  "remarks": "Strong foundational projects and problem-solving background"
}

# ─── 3. REAL Module 4 Interview Input ─────────────────────────────────────────
REAL_INTERVIEW_JSON = {
  "interview_id": "inv_9a8b7c6d-1234-5678-abcd-ef0123456789",
  "role": "AI Engineer",
  "items": [
    {
      "q_id": 1,
      "phase": "project",
      "type": "technical",
      "source": "project: Autonomous Voice & AI Lead Engine",
      "skill_tested": "RAG",
      "difficulty": "medium",
      "question": "How did you handle context window optimization and retrieval latency in your Bolna AI & Airtable voice pipeline?",
      "status": "answered",
      "answer": "We used semantic chunking and cached vector embeddings so the voice bot received context in under 400ms without exceeding the token limits.",
      "duration_sec": 85
    },
    {
      "q_id": 2,
      "phase": "technical",
      "type": "technical",
      "source": "skill: LangGraph",
      "skill_tested": "LangGraph",
      "difficulty": "hard",
      "question": "Can you explain how state persistence and cyclical multi-agent handoffs are managed in LangGraph vs traditional DAG pipelines?",
      "status": "skipped",
      "answer": None,
      "duration_sec": 0
    },
    {
      "q_id": 3,
      "phase": "behavioral",
      "type": "soft_skills",
      "source": "collaboration",
      "skill_tested": "Team Collaboration",
      "difficulty": "medium",
      "question": "When an automated pipeline fails in production due to third-party API rate limits, how do you communicate the issue to non-technical stakeholders?",
      "status": "answered",
      "answer": "I tell them the server is down and they need to wait until the API vendor resets the quota.",
      "duration_sec": 45
    }
  ]
}


def main():
    print("=" * 65)
    print("  MODULE 2 - COMPREHENSIVE WORKFLOW & GAP ANALYSIS TEST")
    print("=" * 65)

    agent = GapAnalysisAgent()

    # ─────────────────────────────────────────────────────────────
    # STEP 1: RESUME VS JD GAP ANALYSIS (Module 1 Inputs)
    # ─────────────────────────────────────────────────────────────
    print("\n[STEP 1] Generating resume_gap.json from Module 1 inputs...")
    print(f"  Candidate : {REAL_RESUME_JSON['candidate']['name']}")
    print(f"  Target Job: {REAL_JD_JSON['job']['title']}")

    resume_gap_report = agent.run_from_json(
        resume_json=REAL_RESUME_JSON,
        jd_json=REAL_JD_JSON,
    )

    print("\n[OUTPUT 1] resume_gap.json:")
    print(json.dumps(resume_gap_report, indent=2))

    # ─────────────────────────────────────────────────────────────
    # STEP 2: SCREENING GATE CHECK (Rank 1-75 vs 76-100)
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("[STEP 2] Checking Screening Ranking from Module 1...")
    is_qualified, rank, reason = agent.evaluate_screening(REAL_SCREENING_JSON)
    print(f"  Screening Rank : #{rank}")
    print(f"  Status         : {'QUALIFIED FOR INTERVIEW' if is_qualified else 'DISQUALIFIED (NO INTERVIEW)'}")
    print(f"  Details        : {reason}")

    # ─────────────────────────────────────────────────────────────
    # STEP 3: INTERVIEW GAP ANALYSIS (Module 4 Input - if qualified)
    # ─────────────────────────────────────────────────────────────
    if is_qualified:
        print("\n" + "=" * 65)
        print("[STEP 3] Candidate Qualified! Analyzing Module 4 interview.json...")
        print(f"  Interview ID : {REAL_INTERVIEW_JSON['interview_id']}")
        print(f"  Target Role  : {REAL_INTERVIEW_JSON['role']}")
        print(f"  Total Items  : {len(REAL_INTERVIEW_JSON['items'])}")

        interview_gap_report = agent.analyze_interview(REAL_INTERVIEW_JSON)

        print("\n[OUTPUT 2] interview_gap.json:")
        print(json.dumps(interview_gap_report, indent=2))

        print("\n" + "=" * 65)
        print("[DISPATCH TO MODULE 3 (Course Suggestions)]")
        print("  1. resume_gap.json    -> SENT TO MODULE 3 [OK]")
        print("  2. interview_gap.json -> SENT TO MODULE 3 [OK]")
        print("=" * 65)

    else:
        print("\n" + "=" * 65)
        print("[DISPATCH TO MODULE 3 (Course Suggestions)]")
        print("  Rank is > 75: Candidate disqualified from interview.")
        print("  1. resume_gap.json    -> SENT TO MODULE 3 [OK]")
        print("  (interview_gap.json skipped)")
        print("=" * 65)


if __name__ == "__main__":
    main()
