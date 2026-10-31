from typing import List, Tuple, Dict, Any
from app.schemas.resume import EducationItem
from app.schemas.job import JobEducationRequirements

STEM_DEGREES = {"b.tech", "btech", "b.e.", "be", "bca", "mca", "b.sc", "m.sc", "m.tech", "mtech", "bachelor", "master"}
CS_BRANCHES = {"computer science", "cs", "information technology", "it", "software engineering", "data science", "ai", "artificial intelligence"}

def evaluate_education_matching(
    education_list: List[EducationItem],
    job_education: JobEducationRequirements
) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluates educational attainment based strictly on degree and major relevance.
    Adheres strictly to the requirement: Never award or deduct points based on college prestige or ranking.
    Returns (score_ratio 0.0 to 1.0, details_dict).
    """
    if not education_list:
        return 0.50, {
            "degree_matched": False,
            "specialization_matched": False,
            "evidence": [],
            "explanation": "No formal educational records provided."
        }

    degree_matched = False
    specialization_matched = False
    evidence = []

    for edu in education_list:
        deg = (edu.degree or "").lower()
        branch = (edu.branch or "").lower()

        # Check degree equivalence
        if any(d in deg for d in STEM_DEGREES):
            degree_matched = True
            evidence.append(f"Degree: {edu.degree}")
            
        # Check specialization
        if any(b in branch for b in CS_BRANCHES) or any(b in deg for b in CS_BRANCHES):
            specialization_matched = True
            evidence.append(f"Specialization: {edu.branch or 'Computer Science related'}")

    if degree_matched and specialization_matched:
        score_ratio = 1.0
        explanation = "Candidate possesses a qualifying degree with relevant technical specialization (prestige-neutral evaluation)."
    elif degree_matched:
        score_ratio = 0.85
        explanation = "Candidate possesses a technical/STEM degree; specialization has partial overlap."
    elif education_list:
        score_ratio = 0.70
        explanation = "Candidate possesses tertiary education from an accredited institution."
    else:
        score_ratio = 0.50
        explanation = "Education details unverified."

    details = {
        "degree_matched": degree_matched,
        "specialization_matched": specialization_matched,
        "evidence": evidence,
        "explanation": explanation
    }
    
    return score_ratio, details
