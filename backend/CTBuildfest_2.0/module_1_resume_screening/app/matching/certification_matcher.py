from typing import List, Tuple, Dict, Any
from app.schemas.resume import CertificationItem

def evaluate_certification_matching(
    certifications: List[CertificationItem],
    mandatory_certs: List[str],
    required_skills: List[str]
) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluates certifications against mandatory requirements and role skill alignment.
    Returns (score_ratio 0.0 to 1.0, details_dict).
    """
    if not mandatory_certs and not certifications:
        # If no certifications are required and none provided, baseline credit is given
        return 0.70, {
            "has_mandatory_certs": True,
            "relevant_certs_count": 0,
            "total_certifications": 0,
            "certified_skills": [],
            "explanation": "No mandatory certifications required for this position."
        }

    relevant_count = 0
    skills_lower = {s.lower().strip() for s in required_skills}

    for cert in certifications:
        name_lower = cert.name.lower()
        # Check if certification name matches tech skills
        if any(s in name_lower for s in skills_lower):
            relevant_count += 1
        elif any(s.lower() in skills_lower for s in cert.related_skills):
            relevant_count += 1

    if relevant_count >= 2:
        score_ratio = 1.0
        explanation = f"Candidate holds {relevant_count} highly relevant industry certifications."
    elif relevant_count == 1:
        score_ratio = 0.85
        explanation = "Candidate holds a verified relevant technical certification."
    elif certifications:
        score_ratio = 0.60
        explanation = "Candidate has non-core or general certifications."
    else:
        score_ratio = 0.40
        explanation = "No certifications provided (recommended to pursue recognized credentials)."

    details = {
        "total_certifications": len(certifications),
        "relevant_count": relevant_count,
        "certified_skills": [c.name for c in certifications],
        "explanation": explanation
    }

    return score_ratio, details
