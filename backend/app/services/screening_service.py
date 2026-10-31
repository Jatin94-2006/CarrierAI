import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundError, BaseScreeningException
from app.schemas.resume import ResumeStructuredData
from app.schemas.job import JobStructuredData
from app.schemas.screening import (
    FullScreeningReport, CandidateRankingResult, ScoreDistributionStats,
    ScoreBreakdown, MandatoryVerificationResult, SkillMatchItem
)
from app.schemas.persona import SyntheticPersonaItem
from app.schemas.integration import (
    Module2SkillGapInput, Module3CourseInput, Module4InterviewInput,
    Module5ImprovementPlanInput
)
from app.repositories.screening_repo import screening_repo
from app.repositories.resume_repo import resume_repo
from app.repositories.job_repo import job_repo
from app.services.resume_service import resume_service
from app.services.job_service import job_service
from app.matching.ats_engine import ats_engine
from app.personas.generator import synthetic_generator
from app.ranking.ranker import compute_candidate_ranking

class ScreeningService:
    def analyze_session(
        self,
        db: Session,
        resume_id: str,
        job_id: str,
        user_id: Optional[str] = None,
        generate_synthetic_benchmark: bool = True
    ) -> FullScreeningReport:
        """
        Executes complete screening pipeline:
        1. Retrieves structured candidate & job
        2. Evaluates ATS match deterministically
        3. Generates 100 job-specific synthetic candidates and scores them identically
        4. Calculates rank, percentile, and score distribution
        5. Persists session and all entities to DB
        6. Returns FullScreeningReport
        """
        user_uuid = user_id or str(uuid.uuid4())
        
        # 1. Retrieve Data
        resume_data = resume_service.get_resume_data(db, resume_id)
        job_data = job_service.get_job_data(db, job_id)

        # Create session record
        session = screening_repo.create_session(
            db=db,
            user_id=user_uuid,
            resume_id=resume_id,
            job_id=job_id,
            scoring_config=ats_engine.weights
        )

        # 2. Evaluate Candidate with Deterministic ATS Engine
        ats_score, breakdown, mandatory, metadata = ats_engine.evaluate(resume_data, job_data)

        # 3. Synthetic Benchmark Pool
        # Check if personas already generated for this session
        existing_personas = screening_repo.get_synthetic_personas(db, session.id)
        if not existing_personas and generate_synthetic_benchmark:
            synthetic_items = synthetic_generator.generate_and_score_pool(job_data, session.id)
            screening_repo.save_synthetic_personas(db, session.id, job_id, synthetic_items)
        elif existing_personas:
            synthetic_items = [
                SyntheticPersonaItem(
                    id=p.id,
                    competency_band=p.competency_band,
                    profile=ResumeStructuredData(**p.profile_data),
                    ats_score=p.ats_score,
                    score_breakdown=p.score_breakdown
                )
                for p in existing_personas
            ]
        else:
            synthetic_items = []

        # 4. Candidate Ranking & Percentile Calculation
        ranking_res, distribution_stats = compute_candidate_ranking(ats_score, synthetic_items)
        screening_repo.save_ranking(db, session.id, ranking_res, distribution_stats)

        # 5. Assemble Full Screening Report (Section 11)
        req_matches: List[SkillMatchItem] = metadata["req_matches"]
        pref_matches: List[SkillMatchItem] = metadata["pref_matches"]

        matched = [m for m in req_matches + pref_matches if m.status in ["exact_match", "verified_equivalent"]]
        partially_matched = [m for m in req_matches + pref_matches if m.status == "related"]
        missing = [m for m in req_matches + pref_matches if m.status == "missing"]
        unverified = [m for m in req_matches + pref_matches if m.status == "unverified"]

        # Missing ATS keywords
        missing_keywords = [m.skill for m in req_matches if m.status in ["missing", "related"]]

        # Strengths & Areas of Improvement
        strengths = [f"Strong proficiency demonstrated in: {', '.join([m.skill for m in matched[:4]])}"] if matched else []
        if breakdown.experience.awarded >= (breakdown.experience.maximum_points * 0.8):
            strengths.append("Work and internship history well-aligned with role level.")
        if breakdown.projects.awarded >= (breakdown.projects.maximum_points * 0.7):
            strengths.append("Practical software projects demonstrate direct tech stack application.")

        improvements = []
        if missing:
            improvements.append(f"Acquire foundation in core required skills: {', '.join([m.skill for m in missing[:3]])}.")
        if breakdown.projects.awarded < (breakdown.projects.maximum_points * 0.6):
            improvements.append("Enhance project portfolio with measurable outcomes, deployed demos, and metrics.")
        if mandatory.unverified_count > 0:
            improvements.append("Explicitly state dates and educational credentials to clear unverified requirements.")

        report = FullScreeningReport(
            session_id=session.id,
            candidate_summary={
                "name": resume_data.candidate.name,
                "headline": resume_data.candidate.headline,
                "email": resume_data.candidate.email,
                "total_skills_count": len(resume_data.all_skills_flat)
            },
            job_summary={
                "title": job_data.title,
                "company": job_data.company,
                "seniority": job_data.seniority,
                "experience_required": job_data.experience_required
            },
            overall_ats_score=ats_score,
            score_breakdown=breakdown,
            skills_assessment={
                "matched": matched,
                "partially_matched": partially_matched,
                "missing": missing,
                "unverified": unverified
            },
            mandatory_verification=mandatory,
            experience_assessment=metadata["exp_details"],
            projects_assessment=metadata["proj_details"],
            education_assessment=metadata["edu_details"],
            certifications_assessment=metadata["cert_details"],
            missing_ats_keywords=missing_keywords,
            strengths=strengths,
            areas_requiring_improvement=improvements,
            ranking=ranking_res,
            score_distribution=distribution_stats
        )

        # 6. Save final session state
        screening_repo.save_screening_results(
            db=db,
            session_id=session.id,
            ats_score=ats_score,
            breakdown=breakdown,
            mandatory=mandatory,
            req_matches=req_matches,
            pref_matches=pref_matches,
            full_report=report.model_dump()
        )

        return report

    def get_session_report(self, db: Session, session_id: str) -> FullScreeningReport:
        session = screening_repo.get_session(db, session_id)
        if not session or not session.full_report:
            raise ResourceNotFoundError(f"Screening report for session {session_id} not found")
        return FullScreeningReport(**session.full_report)

    def get_session_ranking(self, db: Session, session_id: str) -> CandidateRankingResult:
        ranking = screening_repo.get_ranking(db, session_id)
        if not ranking:
            raise ResourceNotFoundError(f"Ranking for session {session_id} not found")
        return CandidateRankingResult(
            actual_candidate_score=ranking.actual_candidate_score,
            total_candidates_compared=ranking.total_candidates_compared,
            rank=ranking.rank,
            synthetic_candidates_above=ranking.synthetic_candidates_above,
            synthetic_candidates_below=ranking.synthetic_candidates_below,
            synthetic_candidates_tied=ranking.synthetic_candidates_tied,
            percentile=ranking.percentile,
            comparison_type=ranking.comparison_type,
            explanation=f"Rank {ranking.rank} of {ranking.total_candidates_compared} at {ranking.percentile}th percentile."
        )

    # Inter-Module Integration Outputs (Section 12)
    def get_module2_skill_gap_input(self, db: Session, session_id: str) -> Module2SkillGapInput:
        report = self.get_session_report(db, session_id)
        session = screening_repo.get_session(db, session_id)
        resume_data = resume_service.get_resume_data(db, session.resume_id)
        job_data = job_service.get_job_data(db, session.job_id)

        evidence_dict = {
            m.skill: m.evidence_snippet or ""
            for m in report.skills_assessment.get("matched", []) + report.skills_assessment.get("partially_matched", [])
        }
        weights_dict = {s: 1.0 for s in job_data.required_skills}
        weights_dict.update({s: 0.5 for s in job_data.preferred_skills})

        return Module2SkillGapInput(
            session_id=session_id,
            resume_id=session.resume_id,
            job_id=session.job_id,
            resume_data=resume_data,
            job_data=job_data,
            required_skills=job_data.required_skills,
            preferred_skills=job_data.preferred_skills,
            matched_skills=report.skills_assessment.get("matched", []),
            partially_matched_skills=report.skills_assessment.get("partially_matched", []),
            missing_skills=report.skills_assessment.get("missing", []),
            unverified_skills=report.skills_assessment.get("unverified", []),
            skill_importance_weights=weights_dict,
            evidence_snippets=evidence_dict,
            ats_score_breakdown=report.score_breakdown
        )

    def get_module3_course_input(self, db: Session, session_id: str) -> Module3CourseInput:
        report = self.get_session_report(db, session_id)
        session = screening_repo.get_session(db, session_id)
        job_data = job_service.get_job_data(db, session.job_id)

        missing_names = [m.skill for m in report.skills_assessment.get("missing", [])]
        partial_names = [m.skill for m in report.skills_assessment.get("partially_matched", [])]

        skill_levels = {s: "absent" for s in missing_names}
        skill_levels.update({s: "intermediate" for s in partial_names})

        return Module3CourseInput(
            session_id=session_id,
            target_job_title=job_data.title,
            missing_skills=missing_names,
            partially_matched_skills=partial_names,
            skill_importance={s: 1.0 for s in job_data.required_skills},
            candidate_existing_skill_level=skill_levels,
            job_requirements=job_data.technical_requirements
        )

    def get_module4_interview_input(self, db: Session, session_id: str) -> Module4InterviewInput:
        report = self.get_session_report(db, session_id)
        session = screening_repo.get_session(db, session_id)
        resume_data = resume_service.get_resume_data(db, session.resume_id)
        job_data = job_service.get_job_data(db, session.job_id)

        return Module4InterviewInput(
            session_id=session_id,
            target_job_title=job_data.title,
            resume_json=resume_data,
            job_description=job_data,
            projects=[p.model_dump() for p in resume_data.projects],
            technical_skills=resume_data.all_skills_flat,
            professional_experience=[e.model_dump() for e in resume_data.experience],
            areas_of_weak_or_missing_evidence=report.areas_requiring_improvement,
            suggested_interview_focus=[
                f"Verify depth in {s}" for s in job_data.required_skills[:3]
            ]
        )

    def get_module5_improvement_plan_input(self, db: Session, session_id: str) -> Module5ImprovementPlanInput:
        report = self.get_session_report(db, session_id)
        missing_names = [m.skill for m in report.skills_assessment.get("missing", [])]

        return Module5ImprovementPlanInput(
            session_id=session_id,
            ats_score=report.overall_ats_score,
            score_breakdown=report.score_breakdown,
            missing_skills=missing_names,
            priority_requirements=[i.requirement for i in report.mandatory_verification.requirements if i.status != "met"],
            project_gaps=report.areas_requiring_improvement,
            experience_gaps=[report.experience_assessment.get("explanation", "")],
            percentile=report.ranking.percentile,
            suggested_30_day_milestones=[
                "Day 1-10: Bridge top missing skills with hands-on labs",
                "Day 11-20: Build and document an end-to-end fullstack/backend project",
                "Day 21-30: Refactor resume with verified impact statements and prepare mock interviews"
            ]
        )

screening_service = ScreeningService()
