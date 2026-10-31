"""
Agent 5 - 30-Day Personalized Learning Planner
================================================
Terminal entry-point for Agent 5.

Features:
  1. Candidate Ranking: Ranks incoming resumes/candidates (assigns Rank #1 for single resume).
  2. Gap Analysis Summary: Outputs comprehensive paragraph summary.
  3. Columns: Day | Skill | Recommended Course | Optional Course | Skill-Based Project
  4. < 1 Week Courses: All recommended materials are short-format micro-courses (< 7 days).
  5. PDF Generation & Auto-open.

Usage:
    python main.py
    python main.py --input path/to/agent3_output.json
    python main.py --output path/to/output.pdf
"""

from __future__ import annotations
import argparse
import os
import sys
import time
import shutil
import subprocess
import io

# Windows UTF-8 safe stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from data_loader import load_input_data
from plan_generator import generate_30_day_plan
from resource_validator import validate_schedule_links, print_validation_report
from pdf_generator import generate_pdf


BANNER = """
+------------------------------------------------------------------+
|      Agent 5  -  30-Day Personalized Learning Planner            |
|      AI-Powered Career Guidance & Job Preparation System         |
+------------------------------------------------------------------+
"""


def separator(char="-", width=66):
    print(char * width)


def main():
    parser = argparse.ArgumentParser(
        description="Agent 5 - 30-Day Personalized Learning Planner (PDF Generator)"
    )
    parser.add_argument("--input",  "-i", default=None, metavar="PATH",
        help="Path to Agent 3 JSON output file.")
    parser.add_argument("--output", "-o", default=None, metavar="PATH",
        help="Output PDF path.")
    parser.add_argument("--no-open", action="store_true",
        help="Do not auto-open the PDF after generation.")
    args = parser.parse_args()

    script_dir  = os.path.dirname(os.path.abspath(__file__))
    temp_dir    = os.environ.get("TEMP", os.environ.get("TMP", script_dir))
    temp_pdf    = os.path.join(temp_dir, "30_Days_Learning_Plan.pdf")
    project_pdf = args.output or os.path.join(script_dir, "30_Days_Learning_Plan.pdf")
    desktop_pdf = os.path.join(os.path.expanduser("~"), "Desktop", "30_Days_Learning_Plan.pdf")

    print(BANNER)
    separator()

    # ── Step 1: Load input data ────────────────────────────────────────────
    print("\n[Step 1/5]  Loading input data & evaluating resume ...")
    data = load_input_data(custom_path=args.input)

    user_profile   = data["user_profile"]
    missing_skills = data["missing_skills"]
    skill_priority = data["skill_priority"]
    agent3_data    = data["agent3_course_suggestions"]
    gap_summary    = data.get("gap_analysis_summary", "")

    rank_display = user_profile.get("rank_display", f"Rank #{user_profile.get('rank', 1)} of {user_profile.get('total_candidates', 1)}")

    print(f"  Candidate Name : {user_profile.get('name', 'Candidate 1')}")
    print(f"  Candidate Rank : {rank_display}")
    print(f"  Target Role    : {user_profile.get('target_role', '-')}")
    print(f"  Skill Level    : {user_profile.get('current_skill_level', '-')}")
    print(f"  Skill Gaps     : {len(missing_skills)} skill(s) identified ({', '.join(missing_skills)})")
    print(f"  Project Design : 1 Dedicated Project Day following each skill module")

    print("\n  [Gap Analysis Summary Paragraph]:")
    print("  " + "\n  ".join([gap_summary[i:i+64] for i in range(0, len(gap_summary), 64)][:4]) + "...")

    if not missing_skills:
        print("\n  [ERROR] No skill gaps found. Cannot generate plan.")
        sys.exit(1)

    separator()

    # ── Step 2: Generate 30-day plan ───────────────────────────────────────
    print("\n[Step 2/5]  Generating 30-day personalised learning schedule ...")
    t0 = time.time()
    schedule = generate_30_day_plan(missing_skills, skill_priority, agent3_data)
    elapsed  = time.time() - t0
    print(f"  [OK] 30-day schedule generated in {elapsed:.2f}s")

    print("\n  Preview (first 6 days showing dedicated Project Day):")
    for entry in schedule[:6]:
        day_str   = f"Day {entry['day']:>2}"
        skill_str = entry["skill"][:46].ljust(46)
        rec_str   = f"Rec: {entry.get('rec_title', 'Course')[:22]}"
        print(f"     {day_str} | {skill_str} | {rec_str}")

    separator()

    # ── Step 3: Validate resources ─────────────────────────────────────────
    print("\n[Step 3/5]  Validating learning resource links ...")
    warnings = validate_schedule_links(schedule)
    print_validation_report(warnings)

    separator()

    # ── Step 4: Generate PDF ───────────────────────────────────────────────
    print("\n[Step 4/5]  Generating professional PDF ...")
    t1 = time.time()
    try:
        saved_path = generate_pdf(
            schedule=schedule,
            user_profile=user_profile,
            missing_skills=missing_skills,
            output_path=temp_pdf,
            gap_analysis_summary=gap_summary,
        )
        elapsed_pdf = time.time() - t1
        file_size   = os.path.getsize(saved_path)
        print(f"  [OK] PDF generated in {elapsed_pdf:.2f}s  ({round(file_size / 1024, 1)} KB)")

        # Copy to project folder and desktop
        final_path = saved_path
        copy_targets = [project_pdf, desktop_pdf]
        for dest in copy_targets:
            try:
                shutil.copy2(saved_path, dest)
                final_path = dest
                print("  [OK] Saved to: " + dest)
            except Exception:
                pass

    except Exception as exc:
        import traceback
        print("\n  [ERROR] PDF generation failed: " + str(exc))
        traceback.print_exc()
        sys.exit(1)

    separator()

    # ── Step 5: Done + Auto-open ───────────────────────────────────────────
    print("\n[Step 5/5]  Completed Successfully!")
    print()
    print("  +-------------------------------------------------------------+")
    print("  |  PDF FILE CREATED:                                          |")
    print("  |  " + final_path[:60])
    print("  +-------------------------------------------------------------+")
    print()
    print(f"  Candidate Rank   : {rank_display}")
    print(f"  Target Role      : {user_profile.get('target_role', 'Data Analyst')}")
    print(f"  Summary Included : YES (Comprehensive Gap Analysis Paragraph)")
    print(f"  Table Columns    : Day | Skill / Topic | Recommended Course | Optional Course")
    print(f"  Project Layout   : 1 Dedicated Project Day following each skill module")
    print(f"  Clickable Links  : YES (Direct links to official free resources)")
    separator()
    print()

    if not args.no_open:
        print("  Opening PDF automatically ...")
        try:
            os.startfile(final_path)
        except Exception:
            try:
                subprocess.Popen(["start", "", final_path], shell=True)
            except Exception:
                pass


if __name__ == "__main__":
    main()
