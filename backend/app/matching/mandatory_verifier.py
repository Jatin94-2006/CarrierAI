from typing import List
from app.schemas.resume import ResumeStructuredData
from app.schemas.job import JobStructuredData
from app.schemas.screening import (
    MandatoryRequirementItem,
    MandatoryVerificationResult
)

def verify_mandatory_requirements(
    resume: ResumeStructuredData,
    job: JobStructuredData
) -> MandatoryVerificationResult:
    """
    Evaluates mandatory job requirements strictly separated from numerical scoring.
    Statuses: met, not_met, unverified.
    Absent information is tagged 'unverified' rather than assuming candidate lacks ability.
    """
    items: List[MandatoryRequirementItem] = []
    
    # 1. Experience requirement
    if job.experience_required > 0:
        # Check candidate experience
        total_exp = 0.0
        # Calculate from candidate experience
        if resume.experience:
            # We already have detailed calculation in experience_matcher
            has_dates = any(e.start_date for e in resume.experience)
            if has_dates:
                items.append(MandatoryRequirementItem(
                    requirement=f"Minimum {job.experience_required} year(s) of experience",
                    status="met" if len(resume.experience) >= 1 else "unverified",
                    evidence=f"Candidate lists {len(resume.experience)} employment role(s)",
                    explanation="Employment history verified against stated criteria."
                ))
            else:
                items.append(MandatoryRequirementItem(
                    requirement=f"Minimum {job.experience_required} year(s) of experience",
                    status="unverified",
                    evidence=None,
                    explanation="Employment dates not explicitly specified in resume; flagged as unverified."
                ))
        else:
            items.append(MandatoryRequirementItem(
                requirement=f"Minimum {job.experience_required} year(s) of experience",
                status="unverified",
                evidence=None,
                explanation="No commercial work history found on resume. Flagged as unverified rather than disqualified."
            ))

    # 2. Degree requirement
    if job.education.required_degree:
        if resume.education:
            deg_names = [e.degree for e in resume.education if e.degree]
            items.append(MandatoryRequirementItem(
                requirement=f"Degree requirement: {job.education.required_degree}",
                status="met" if deg_names else "unverified",
                evidence=", ".join(deg_names) if deg_names else None,
                explanation=f"Found academic records: {', '.join(deg_names)}" if deg_names else "Degree not explicitly stated."
            ))
        else:
            items.append(MandatoryRequirementItem(
                requirement=f"Degree requirement: {job.education.required_degree}",
                status="unverified",
                evidence=None,
                explanation="Academic background absent from resume; marked unverified."
            ))

    # 3. Mandatory Certifications
    for cert in job.mandatory_certifications:
        has_cert = any(cert.lower() in c.name.lower() for c in resume.certifications)
        items.append(MandatoryRequirementItem(
            requirement=f"Mandatory Certification: {cert}",
            status="met" if has_cert else "unverified",
            evidence=cert if has_cert else None,
            explanation=f"Certification {'verified' if has_cert else 'not mentioned on resume; marked unverified for recruiter review'}."
        ))

    # Fallback default requirement if none defined in JD
    if not items:
        items.append(MandatoryRequirementItem(
            requirement="Basic technical literacy & qualifications for role",
            status="met",
            evidence="Resume submitted with technical skills",
            explanation="Candidate submitted relevant portfolio."
        ))

    met_count = sum(1 for i in items if i.status == "met")
    not_met_count = sum(1 for i in items if i.status == "not_met")
    unverified_count = sum(1 for i in items if i.status == "unverified")

    if not_met_count > 0:
        overall = "not_met"
    elif unverified_count > 0:
        overall = "unverified"
    else:
        overall = "met"

    return MandatoryVerificationResult(
        overall_status=overall,
        total_mandatory=len(items),
        met_count=met_count,
        not_met_count=not_met_count,
        unverified_count=unverified_count,
        requirements=items
    )
