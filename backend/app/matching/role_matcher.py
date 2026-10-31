from typing import List, Tuple, Dict, Any
from app.schemas.resume import ResumeStructuredData
from app.schemas.job import JobStructuredData

def evaluate_role_relevance(
    resume: ResumeStructuredData,
    job: JobStructuredData
) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluates holistic role relevance across headline, summary, project titles, and experience responsibilities.
    Does NOT rely solely on verbatim title match.
    Returns (score_ratio 0.0 to 1.0, details_dict).
    """
    target_tokens = set(job.title.lower().split())
    # Remove generic filler words
    target_tokens = {t for t in target_tokens if t not in ["developer", "engineer", "software", "specialist", "junior", "senior", "lead", "associate"]}
    
    # Candidate text pool
    pool = []
    if resume.candidate.headline:
        pool.append(resume.candidate.headline.lower())
    if resume.candidate.summary:
        pool.append(resume.candidate.summary.lower())
    for proj in resume.projects:
        pool.append(proj.title.lower())
        pool.extend([f.lower() for f in proj.features])
    for exp in resume.experience:
        if exp.job_title:
            pool.append(exp.job_title.lower())
        pool.extend([r.lower() for r in exp.responsibilities])

    corpus = " ".join(pool)

    # Check matches with target domain/title tokens
    matched_tokens = [t for t in target_tokens if t in corpus]
    ratio = len(matched_tokens) / max(1, len(target_tokens))

    # Also check category / domain overlap
    domain_score = 0.5
    if any(kw in corpus for kw in ["backend", "api", "data", "web", "cloud", "system"]):
        domain_score += 0.3

    final_ratio = min(1.0, (ratio * 0.6) + (domain_score * 0.4))
    final_ratio = max(0.3, final_ratio)

    details = {
        "target_tokens": list(target_tokens),
        "matched_tokens": matched_tokens,
        "explanation": f"Evaluated role alignment between '{job.title}' and candidate portfolio. Overlap ratio: {round(final_ratio, 2)}."
    }

    return final_ratio, details
