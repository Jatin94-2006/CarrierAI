"""
Agent 5 - Data Loader Module
Loads and validates input from Agent 2 and Agent 3 output files.
Handles:
  1. Resume Ranking: Ranks multiple resumes by fit/readiness score, or defaults to Rank #1 for a single resume.
  2. Gap Analysis Summary: Extracts or dynamically crafts a detailed paragraph summary.
  3. Short-Duration (< 1 Week) Courses: Preserves duration metadata and short micro-course links.
"""

from __future__ import annotations
import json
import os
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CT2_ROOT = os.path.dirname(BASE_DIR)

CANDIDATE_PATHS = [
    # Agent 3 output placed directly in agent5 folder
    os.path.join(BASE_DIR, "agent3_output.json"),
    # Shared output folder
    os.path.join(CT2_ROOT, "shared_output", "agent3_output.json"),
    os.path.join(CT2_ROOT, "shared_output", "course_suggestions.json"),
    os.path.join(CT2_ROOT, "shared_output", "agent2_output.json"),
    os.path.join(CT2_ROOT, "shared_output", "gap_analysis.json"),
    os.path.join(CT2_ROOT, "shared_output", "combined_output.json"),
    # Agent 3 own folders
    os.path.join(CT2_ROOT, "agent3", "output", "course_suggestions.json"),
    os.path.join(CT2_ROOT, "agent3", "agent3_output.json"),
    os.path.join(CT2_ROOT, "agent3--course-suggestion", "output", "course_suggestions.json"),
    os.path.join(CT2_ROOT, "agent3--course-suggestion", "agent3_output.json"),
    # Agent 2 own folder
    os.path.join(CT2_ROOT, "agent2", "output", "gap_analysis.json"),
    # Fallback sample
    os.path.join(BASE_DIR, "sample_input.json"),
]


def _load_json(path):
    """Try to load a JSON file; return None on any error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError):
        return None


def calculate_resume_score(skill_levels: dict[str, str]) -> float:
    """
    Calculate an objective candidate readiness/fit score (0-100%).
    Takes into account possessed skills vs target role requirements.
    """
    if not skill_levels:
        return 75.0
    
    total_pts = 0.0
    for lvl in skill_levels.values():
        lvl_str = str(lvl).lower()
        if "advanced" in lvl_str:
            total_pts += 3.0
        elif "intermediate" in lvl_str:
            total_pts += 2.5
        elif "beginner" in lvl_str or "needs improvement" in lvl_str:
            total_pts += 1.5
        elif "important" in lvl_str:
            total_pts += 1.0
        else: # critical gap, missing, etc.
            total_pts += 0.5

    max_pts = len(skill_levels) * 3.0
    if max_pts == 0:
        return 75.0
    ratio = total_pts / max_pts
    score = round(40.0 + (ratio * 55.0), 1)
    return score


def generate_gap_summary_paragraph(target_role: str, skill_levels: dict[str, str], missing_skills: list[str]) -> str:
    """
    Generate a cohesive, comprehensive paragraph detailing the candidate's
    strengths, gaps, and the 30-day intervention strategy with <1 week courses.
    """
    missing = [s for s, lvl in skill_levels.items() if str(lvl).lower() == "missing"]
    if not missing:
        missing = [s for s in missing_skills[:3]]

    beginner = [s for s, lvl in skill_levels.items() if str(lvl).lower() == "beginner"]
    intermediate = [s for s, lvl in skill_levels.items() if str(lvl).lower() == "intermediate"]

    parts = []
    parts.append(
        f"Based on the comprehensive gap analysis for the target role of {target_role}, the candidate "
        f"demonstrates foundational competencies but requires targeted skill acceleration."
    )

    if intermediate:
        parts.append(f"Existing technical strengths include {', '.join(intermediate)} at an Intermediate level.")

    if beginner:
        parts.append(f"Foundational proficiency is noted in {', '.join(beginner)}, which will benefit from structured consolidation.")

    if missing:
        parts.append(
            f"Crucially, high-priority domain prerequisites currently categorized as Missing include {', '.join(missing)}."
        )

    parts.append(
        "To bridge these gaps swiftly and ensure candidate competitiveness, this 30-day personalized learning roadmap "
        "is engineered with high-impact, free practical learning resources. Each skill module is directly followed by a "
        "dedicated full-day practical project to ensure hands-on mastery before progressing to the next competency, "
        "culminating in an end-to-end multi-phase capstone portfolio project."
    )

    return " ".join(parts)


def _parse_agent3_schema(data):
    """
    Parse Agent 3's output format:
      - technical_recommendations[].skill -> skill name
      - recommended.url -> Recommended Course link + duration
      - options[0].url  -> Optional Course link + duration
      - input_summary.skill_levels -> derive priority + resume ranking
    """
    target_role = data.get("target_job_role", "Data Analyst")
    input_summary = data.get("input_summary", {})
    skill_levels = input_summary.get("skill_levels", {})

    # ---- 1. Resume Ranking Logic ----
    # If a list of resumes/candidates exists in input, rank them all.
    candidates_list = data.get("candidates") or data.get("resumes") or []
    if candidates_list and isinstance(candidates_list, list):
        # Multi-candidate ranking
        ranked_candidates = []
        for c in candidates_list:
            c_levels = c.get("skill_levels", {})
            c_score = calculate_resume_score(c_levels)
            ranked_candidates.append({
                "name": c.get("name", "Candidate"),
                "score": c_score,
                "data": c
            })
        ranked_candidates.sort(key=lambda x: x["score"], reverse=True)
        for idx, cand in enumerate(ranked_candidates):
            cand["rank"] = idx + 1
        top_cand = ranked_candidates[0]
        rank_num = top_cand["rank"]
        total_cand = len(ranked_candidates)
        readiness_score = top_cand["score"]
        cand_name = top_cand["name"]
    else:
        # Single candidate evaluation -> Guaranteed Rank #1
        readiness_score = calculate_resume_score(skill_levels)
        rank_num = 1
        total_cand = 1
        cand_name = (
            data.get("candidate_name")
            or data.get("candidate_profile", {}).get("name")
            or "Candidate 1 (Evaluated Resume)"
        )

    # Overall skill level badge
    level_values = [str(v).lower() for v in skill_levels.values()]
    if any("advanced" in v for v in level_values):
        overall_level = "Advanced"
    elif any("intermediate" in v for v in level_values):
        overall_level = "Intermediate"
    else:
        overall_level = "Beginner to Intermediate"

    # ---- 2. Skill Priority Mapping ----
    skill_priority = {}
    for skill, level in skill_levels.items():
        lvl_lower = str(level).lower()
        if any(w in lvl_lower for w in ["critical", "high", "missing"]):
            skill_priority[skill] = "High"
        elif any(w in lvl_lower for w in ["important", "needs improvement", "medium"]):
            skill_priority[skill] = "Medium"
        else:
            skill_priority[skill] = "Low"

    # ---- 3. Extract Courses (with < 1 Week durations) ----
    course_suggestions = {}
    all_recs = (
        data.get("technical_recommendations", []) +
        data.get("soft_recommendations", [])
    )

    for rec in all_recs:
        skill = rec.get("skill", "")
        if not skill:
            continue

        recommended = rec.get("recommended", {})
        options = rec.get("options", [])

        # Priority 1 -> Recommended Course
        priority_link = recommended.get("url", "https://www.geeksforgeeks.org/")
        rec_duration = recommended.get("duration", "< 1 Week")
        rec_title = recommended.get("title", skill)
        rec_platform = recommended.get("platform", "")

        # Optional Course
        if options:
            opt = options[0]
            optional_link = opt.get("url", "https://www.freecodecamp.org/")
            opt_duration = opt.get("duration", "< 1 Week")
            opt_title = opt.get("title", f"{skill} Practice")
            opt_platform = opt.get("platform", "")
        else:
            optional_link = "https://www.freecodecamp.org/"
            opt_duration = "< 1 Week"
            opt_title = f"{skill} Tutorial"
            opt_platform = "freeCodeCamp"

        course_suggestions[skill] = {
            "priority_link": priority_link,
            "optional_link": optional_link,
            "rec_duration": rec_duration,
            "opt_duration": opt_duration,
            "rec_title": rec_title,
            "opt_title": opt_title,
            "rec_platform": rec_platform,
            "opt_platform": opt_platform,
        }

        if skill not in skill_priority:
            skill_priority[skill] = "Medium"

    missing_skills = list(course_suggestions.keys())
    meta_skills = data.get("metadata", {}).get("skills_covered", [])
    if meta_skills:
        ordered = list(meta_skills)
        for s in missing_skills:
            if s not in ordered:
                ordered.append(s)
        missing_skills = ordered

    # ---- 4. Gap Analysis Summary Paragraph ----
    gap_summary = data.get("gap_analysis_summary")
    if not gap_summary or len(gap_summary.strip()) < 40:
        gap_summary = generate_gap_summary_paragraph(target_role, skill_levels, missing_skills)

    user_profile = {
        "name": cand_name,
        "current_role": "Fresher / Data Aspirant",
        "target_role": target_role,
        "current_skill_level": overall_level,
        "rank": rank_num,
        "total_candidates": total_cand,
        "readiness_score": readiness_score,
        "rank_display": f"Rank #{rank_num} of {total_cand}  (Readiness Score: {readiness_score}%)",
    }

    return {
        "user_profile": user_profile,
        "missing_skills": missing_skills,
        "skill_priority": skill_priority,
        "agent3_course_suggestions": course_suggestions,
        "gap_analysis_summary": gap_summary,
    }


def _parse_standard_schema(data):
    """Fallback parser for standard format."""
    user_profile = data.get("user_profile", {
        "name": "Candidate 1",
        "current_role": "Fresher / Student",
        "target_role": "Data Analyst",
        "current_skill_level": "Beginner",
    })

    gap = data.get("agent2_gap_analysis", data.get("gap_analysis", {}))
    skills = (
        gap.get("missing_skills")
        or data.get("missing_skills")
        or data.get("skill_gaps")
        or []
    )
    missing_skills = [str(s) for s in skills]

    skill_priority = (
        gap.get("skill_priority")
        or data.get("skill_priority")
        or {}
    )

    course_suggestions = (
        data.get("agent3_course_suggestions")
        or data.get("course_suggestions")
        or data.get("courses")
        or {}
    )

    # Ensure ranking
    user_profile.setdefault("rank", 1)
    user_profile.setdefault("total_candidates", 1)
    user_profile.setdefault("readiness_score", 75.0)
    user_profile["rank_display"] = f"Rank #1 of 1  (Readiness Score: {user_profile['readiness_score']}%)"

    gap_summary = data.get("gap_analysis_summary") or generate_gap_summary_paragraph(
        user_profile.get("target_role", "Data Analyst"),
        {s: "Missing" for s in missing_skills},
        missing_skills
    )

    return {
        "user_profile": user_profile,
        "missing_skills": missing_skills,
        "skill_priority": skill_priority,
        "agent3_course_suggestions": course_suggestions,
        "gap_analysis_summary": gap_summary,
    }


def _detect_and_parse(data):
    if "technical_recommendations" in data or "soft_recommendations" in data:
        return _parse_agent3_schema(data)
    return _parse_standard_schema(data)


def load_input_data(custom_path=None):
    paths_to_try = []
    if custom_path:
        paths_to_try.append(custom_path)
    paths_to_try.extend(CANDIDATE_PATHS)

    for path in paths_to_try:
        data = _load_json(path)
        if not data:
            continue
        result = _detect_and_parse(data)
        if result["missing_skills"]:
            print("  [OK] Loaded input from: " + path)
            return result
        else:
            print("  [WARN] Found " + path + " but no skills -- skipping.")

    print("  [WARN] No input file found. Using built-in defaults.")
    return _parse_standard_schema({
        "user_profile": {
            "name": "Candidate 1",
            "current_role": "Fresher",
            "target_role": "Data Analyst",
            "current_skill_level": "Intermediate",
            "rank": 1,
            "total_candidates": 1,
            "readiness_score": 75.0,
        },
        "agent2_gap_analysis": {
            "missing_skills": [
                "Machine Learning", "Power BI", "SQL",
                "Python", "Leadership", "Communication", "Interview Skills"
            ],
            "skill_priority": {
                "Machine Learning": "High",
                "Power BI": "High",
                "SQL": "Medium",
                "Python": "Low",
                "Leadership": "High",
                "Communication": "Medium",
                "Interview Skills": "Medium",
            },
        },
        "agent3_course_suggestions": {},
    })
