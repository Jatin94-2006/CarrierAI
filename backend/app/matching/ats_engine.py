from typing import Dict, Any, Tuple, Optional
from app.config import settings
from app.schemas.resume import ResumeStructuredData
from app.schemas.job import JobStructuredData
from app.schemas.screening import (
    ScoreBreakdown,
    ScoreComponentItem,
    SkillMatchItem,
    MandatoryVerificationResult,
)
from app.matching.skill_matcher import evaluate_skills_matching
from app.matching.experience_matcher import evaluate_experience_matching
from app.matching.project_matcher import evaluate_project_matching
from app.matching.education_matcher import evaluate_education_matching
from app.matching.certification_matcher import evaluate_certification_matching
from app.matching.role_matcher import evaluate_role_relevance
from app.matching.mandatory_verifier import verify_mandatory_requirements

class ATSEngine:
    """
    Deterministic Explainable ATS Evaluation Engine.
    Executes 100% in Python using configurable weights.
    Guarantee: Exactly identical inputs yield exactly identical scores.
    """
    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        # Default weights from settings summing to 1.0 (100%)
        self.weights = {
            "required_skills": settings.ATS_WEIGHT_REQUIRED_SKILLS,       # 0.35 (35 pts)
            "preferred_skills": settings.ATS_WEIGHT_PREFERRED_SKILLS,     # 0.15 (15 pts)
            "experience": settings.ATS_WEIGHT_EXPERIENCE,                 # 0.15 (15 pts)
            "projects": settings.ATS_WEIGHT_PROJECTS,                     # 0.15 (15 pts)
            "education": settings.ATS_WEIGHT_EDUCATION,                   # 0.10 (10 pts)
            "certifications": settings.ATS_WEIGHT_CERTIFICATIONS,         # 0.05 (5 pts)
            "role_relevance": settings.ATS_WEIGHT_ROLE_RELEVANCE,         # 0.05 (5 pts)
        }
        if custom_weights:
            self.weights.update(custom_weights)
            # Normalize to ensure sum is 1.0
            total_w = sum(self.weights.values())
            if total_w > 0:
                self.weights = {k: v / total_w for k, v in self.weights.items()}

    def evaluate(
        self,
        resume: ResumeStructuredData,
        job: JobStructuredData
    ) -> Tuple[float, ScoreBreakdown, MandatoryVerificationResult, Dict[str, Any]]:
        """
        Calculates explainable ATS score (0 to 100) and produces score breakdown.
        """
        # 1. Skills Matching
        req_matches, pref_matches, req_ratio, pref_ratio = evaluate_skills_matching(
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            candidate_skills=resume.all_skills_flat
        )
        
        # 2. Experience Matching
        exp_ratio, exp_details = evaluate_experience_matching(
            experience_list=resume.experience,
            internships_list=resume.internships,
            required_years=job.experience_required,
            seniority=job.seniority
        )
        
        # 3. Project Matching
        proj_ratio, proj_details = evaluate_project_matching(
            projects=resume.projects,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills
        )
        
        # 4. Education Matching
        edu_ratio, edu_details = evaluate_education_matching(
            education_list=resume.education,
            job_education=job.education
        )
        
        # 5. Certification Matching
        cert_ratio, cert_details = evaluate_certification_matching(
            certifications=resume.certifications,
            mandatory_certs=job.mandatory_certifications,
            required_skills=job.required_skills
        )
        
        # 6. Role Relevance Matching
        role_ratio, role_details = evaluate_role_relevance(resume, job)
        
        # 7. Mandatory Verification (Strictly separate from score)
        mandatory_res = verify_mandatory_requirements(resume, job)
        
        # Points calculation
        w_req = self.weights["required_skills"] * 100
        w_pref = self.weights["preferred_skills"] * 100
        w_exp = self.weights["experience"] * 100
        w_proj = self.weights["projects"] * 100
        w_edu = self.weights["education"] * 100
        w_cert = self.weights["certifications"] * 100
        w_role = self.weights["role_relevance"] * 100

        pts_req = round(req_ratio * w_req, 2)
        pts_pref = round(pref_ratio * w_pref, 2)
        pts_exp = round(exp_ratio * w_exp, 2)
        pts_proj = round(proj_ratio * w_proj, 2)
        pts_edu = round(edu_ratio * w_edu, 2)
        pts_cert = round(cert_ratio * w_cert, 2)
        pts_role = round(role_ratio * w_role, 2)

        total_ats_score = round(min(100.0, pts_req + pts_pref + pts_exp + pts_proj + pts_edu + pts_cert + pts_role), 2)

        # Assemble Explainable Breakdown
        breakdown = ScoreBreakdown(
            required_skills=ScoreComponentItem(
                weight=w_req,
                maximum_points=w_req,
                awarded=pts_req,
                calculation_method="Exact matches (1.0), verified aliases (0.85), related skills (0.40)",
                matching_evidence=[m.evidence_snippet for m in req_matches if m.credit > 0 and m.evidence_snippet],
                missing_requirements=[m.skill for m in req_matches if m.status == "missing"],
                explanation=f"Awarded {pts_req}/{w_req} points. {sum(1 for m in req_matches if m.credit >= 0.85)}/{len(req_matches)} required skills satisfied."
            ),
            preferred_skills=ScoreComponentItem(
                weight=w_pref,
                maximum_points=w_pref,
                awarded=pts_pref,
                calculation_method="Bonus point allocation for nice-to-have capabilities",
                matching_evidence=[m.evidence_snippet for m in pref_matches if m.credit > 0 and m.evidence_snippet],
                missing_requirements=[m.skill for m in pref_matches if m.status == "missing"],
                explanation=f"Awarded {pts_pref}/{w_pref} points for preferred stack competencies."
            ),
            experience=ScoreComponentItem(
                weight=w_exp,
                maximum_points=w_exp,
                awarded=pts_exp,
                calculation_method="Non-overlapping calendar dates; entry-level parity for freshers",
                matching_evidence=[f"Professional years: {exp_details['calculated_professional_years']}"],
                missing_requirements=[],
                explanation=exp_details["explanation"]
            ),
            projects=ScoreComponentItem(
                weight=w_proj,
                maximum_points=w_proj,
                awarded=pts_proj,
                calculation_method="Tech stack overlap, features, and measurable outcomes",
                matching_evidence=[f"Techs demonstrated: {', '.join(proj_details['technologies_demonstrated'][:4])}"],
                missing_requirements=[],
                explanation=proj_details["explanation"]
            ),
            education=ScoreComponentItem(
                weight=w_edu,
                maximum_points=w_edu,
                awarded=pts_edu,
                calculation_method="Prestige-neutral STEM degree and branch relevance",
                matching_evidence=edu_details.get("evidence", []),
                missing_requirements=[],
                explanation=edu_details["explanation"]
            ),
            certifications=ScoreComponentItem(
                weight=w_cert,
                maximum_points=w_cert,
                awarded=pts_cert,
                calculation_method="Relevant credential validation",
                matching_evidence=cert_details.get("certified_skills", []),
                missing_requirements=[],
                explanation=cert_details["explanation"]
            ),
            role_relevance=ScoreComponentItem(
                weight=w_role,
                maximum_points=w_role,
                awarded=pts_role,
                calculation_method="Semantic role vocabulary and engineering context overlap",
                matching_evidence=[f"Matched role tokens: {', '.join(role_details['matched_tokens'])}"],
                missing_requirements=[],
                explanation=role_details["explanation"]
            )
        )

        metadata = {
            "req_matches": req_matches,
            "pref_matches": pref_matches,
            "exp_details": exp_details,
            "proj_details": proj_details,
            "edu_details": edu_details,
            "cert_details": cert_details,
            "role_details": role_details,
        }

        return total_ats_score, breakdown, mandatory_res, metadata

ats_engine = ATSEngine()
