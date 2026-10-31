from typing import List, Tuple, Dict, Any
from app.schemas.resume import ProjectItem

def evaluate_project_matching(
    projects: List[ProjectItem],
    required_skills: List[str],
    preferred_skills: List[str]
) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluates candidate projects based on:
    - Tech stack overlap with required/preferred skills.
    - Presence of clear descriptions, contribution, and features.
    - Demonstrated measurable outcomes.
    Returns (score_ratio 0.0 to 1.0, details_dict).
    """
    if not projects:
        return 0.20, {
            "total_projects": 0,
            "relevant_projects": 0,
            "technologies_demonstrated": [],
            "explanation": "No projects documented in candidate profile."
        }

    target_techs = {s.lower().strip() for s in (required_skills + preferred_skills)}
    project_scores = []
    all_demo_techs = []

    for proj in projects:
        score = 0.0
        # 1. Tech stack alignment (up to 0.40)
        proj_techs = {t.lower().strip() for t in proj.technologies}
        all_demo_techs.extend(proj.technologies)
        overlap = proj_techs.intersection(target_techs)
        if overlap:
            tech_ratio = len(overlap) / max(1, min(4, len(target_techs)))
            score += min(0.40, tech_ratio * 0.40)
        elif proj.technologies:
            score += 0.15 # Demonstrates technical initiative even if slightly different stack

        # 2. Evidence of features & contribution (up to 0.35)
        if proj.features and len(proj.features) > 0:
            score += 0.20
        if proj.contribution and len(proj.contribution.strip()) > 10:
            score += 0.15
        elif proj.description and len(proj.description.strip()) > 30:
            score += 0.15

        # 3. Measurable outcomes / complexity (up to 0.25)
        if proj.outcomes and len(proj.outcomes.strip()) > 10:
            score += 0.25
        elif proj.description and any(kw in proj.description.lower() for kw in ["reduced", "increased", "deployed", "users", "api", "tested"]):
            score += 0.15

        project_scores.append(min(1.0, score))

    # Weight best 2-3 projects
    sorted_scores = sorted(project_scores, reverse=True)
    if len(sorted_scores) >= 2:
        final_ratio = (sorted_scores[0] * 0.6) + (sorted_scores[1] * 0.4)
    else:
        final_ratio = sorted_scores[0] * 0.85 # Slight discount for having only 1 project

    final_ratio = max(0.1, min(1.0, final_ratio))
    
    details = {
        "total_projects": len(projects),
        "technologies_demonstrated": list(dict.fromkeys(all_demo_techs)),
        "project_evaluations": [
            {"title": p.title, "score": round(s, 2), "techs": p.technologies}
            for p, s in zip(projects, project_scores)
        ],
        "explanation": f"Evaluated {len(projects)} project(s). Demonstrated stack alignment on {len(all_demo_techs)} distinct technologies."
    }

    return final_ratio, details
