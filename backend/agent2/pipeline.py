"""
Agent Pipeline Orchestrator
Runs all 5 modules in corrected order, passing outputs between them.

─── CORRECTED PIPELINE ORDER ─────────────────────────────────────────
  Module 1  →  resume.json + jd.json
  Module 2  →  gap_report.json                        (Core)
  Module 4  →  interview_report.json  ← BEFORE Module 3
  Module 3  →  courses.json           ← needs gap_report + resume + interview
  Module 5  →  learning_plan.json
──────────────────────────────────────────────────────────────────────

─── WHO FEEDS MODULE 3 (Course Suggestions) ──────────────────────────
  gap_report.json      (Module 2 output)    ✅
  resume.json          (Module 1 output)    ✅
  interview_report.json (Module 4 output)  ✅
  → courses.json goes ONLY to Module 5
──────────────────────────────────────────────────────────────────────
"""

import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agents.resume_agent import ResumeAgent
from agents.gap_analysis_agent import GapAnalysisAgent
from agents.course_agent import CourseAgent
from agents.interview_agent import InterviewAgent
from agents.planner_agent import PlannerAgent

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def run_pipeline(resume_path: str, jd_text: str, user_id: str) -> dict:
    """
    Runs the full 5-agent pipeline in corrected order.

    Pipeline order:
        1  →  Resume Analysis    (Module 1)
        2  →  Gap Analysis       (Module 2) ← Core
        4  →  Mock Interview     (Module 4) ← runs BEFORE Module 3
        3  →  Course Suggestions (Module 3) ← needs gap_report + resume + interview
        5  →  Learning Planner   (Module 5)

    Args:
        resume_path: Path to resume file (PDF or .txt)
        jd_text    : Raw job description text
        user_id    : Unique user identifier (UUID string)

    Returns:
        dict with all module outputs
    """
    print("\n" + "=" * 60)
    print("  AI CAREER GUIDANCE PIPELINE — STARTING")
    print("=" * 60)

    # ─── Module 1: Resume Analysis ────────────────────────────
    print("\n[Module 1] Resume Analysis Agent — Running...")
    resume_agent = ResumeAgent()
    module1_output = resume_agent.run(
        resume_path=resume_path,
        jd_text=jd_text,
        user_id=user_id,
    )
    _save_output(module1_output, "resume.json")
    print("[Module 1] ✅ Done — resume.json saved")

    # ─── Module 2: Gap Analysis (Core) ────────────────────────
    print("\n[Module 2] Gap Analysis Agent — Running (Core)...")
    gap_agent = GapAnalysisAgent()
    module2_output = gap_agent.run(module1_output=module1_output)
    _save_output(module2_output, "gap_report.json")
    print("[Module 2] ✅ Done — gap_report.json saved")

    # ─── Module 4: Mock Interview (runs BEFORE Module 3) ──────
    # Interview must run before Module 3 so that interview weak
    # areas can be used to suggest more targeted courses.
    print("\n[Module 4] Interview Preparation Agent — Running...")
    interview_agent = InterviewAgent()
    module4_output = interview_agent.run(
        resume_data=module1_output,
        gap_report=module2_output,
    )
    _save_output(module4_output, "interview_report.json")
    print("[Module 4] ✅ Done — interview_report.json saved")

    # ─── Module 3: Course Suggestions ─────────────────────────
    # Input  : gap_report.json + resume.json + interview_report.json
    # Output : courses.json  →  goes ONLY to Module 5
    print("\n[Module 3] Course Suggestion Agent — Running...")
    course_agent = CourseAgent()
    module3_output = course_agent.run(
        gap_report=module2_output,
        resume=module1_output["resume"],
        interview_report=module4_output,
    )
    _save_output(module3_output, "courses.json")
    print("[Module 3] ✅ Done — courses.json saved")

    # ─── Module 5: Learning Planner ───────────────────────────
    print("\n[Module 5] Learning Planner Agent — Running...")
    planner_agent = PlannerAgent()
    module5_output = planner_agent.run(
        gap_report=module2_output,
        courses=module3_output,
    )
    _save_output(module5_output, "learning_plan.json")
    print("[Module 5] ✅ Done — learning_plan.json saved")

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE ✅")
    print(f"  Outputs saved to: {OUTPUT_DIR.resolve()}")
    print("=" * 60 + "\n")

    return {
        "resume":           module1_output,
        "gap_report":       module2_output,
        "interview_report": module4_output,
        "courses":          module3_output,
        "learning_plan":    module5_output,
    }


def _save_output(data: dict, filename: str) -> None:
    """Save module output as JSON to outputs/ directory."""
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
