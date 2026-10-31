from typing import List, Tuple, Dict, Any
from app.schemas.resume import ExperienceItem, InternshipItem
from app.utils.date_utils import calculate_total_experience_years

def evaluate_experience_matching(
    experience_list: List[ExperienceItem],
    internships_list: List[InternshipItem],
    required_years: float,
    seniority: str = "Entry Level"
) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluates candidate experience:
    - Calculates non-overlapping professional employment years.
    - Separates internships and treats them as valuable supplementary experience.
    - If job is entry-level (required_years == 0), freshers receive full 1.0 credit without penalty.
    Returns (score_ratio 0.0 to 1.0, details_dict).
    """
    # Extract professional experience dates
    prof_date_pairs = [(exp.start_date, exp.end_date) for exp in experience_list]
    prof_years, prof_unverified = calculate_total_experience_years(prof_date_pairs)
    
    # Extract internship dates
    intern_date_pairs = [(intern.start_date, intern.end_date) for intern in internships_list]
    intern_years, intern_unverified = calculate_total_experience_years(intern_date_pairs)
    
    is_entry_level = (required_years <= 0.0) or ("entry" in seniority.lower()) or ("fresher" in seniority.lower())
    
    if is_entry_level:
        # Freshers / Entry-level: Not penalized for lacking multi-year professional experience
        # If they have internships or work experience, they get full 1.0; even with 0 years they get 0.95
        if prof_years > 0 or intern_years > 0:
            score_ratio = 1.0
            explanation = f"Entry-level position. Candidate has {prof_years} yrs professional experience and {intern_years} yrs internships, fully satisfying requirements."
        else:
            score_ratio = 0.95
            explanation = "Entry-level position. Candidate does not possess prior commercial experience, but is not penalized per recruitment standards."
    else:
        # Experienced position
        if prof_years >= required_years:
            score_ratio = 1.0
            explanation = f"Candidate possesses {prof_years} years of documented non-overlapping experience, meeting or exceeding required {required_years} years."
        else:
            # Partial credit: fraction of required years, with internship boost
            ratio = (prof_years + (0.5 * intern_years)) / required_years
            score_ratio = max(0.0, min(1.0, ratio))
            explanation = f"Candidate has {prof_years} yrs professional experience vs required {required_years} yrs (supplemented by {intern_years} yrs internships)."

    details = {
        "calculated_professional_years": prof_years,
        "calculated_internship_years": intern_years,
        "required_years": required_years,
        "is_entry_level": is_entry_level,
        "has_unverified_dates": prof_unverified or intern_unverified,
        "explanation": explanation
    }
    
    return score_ratio, details
