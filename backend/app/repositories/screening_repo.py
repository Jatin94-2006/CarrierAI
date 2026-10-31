from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.screening import ScreeningSession, ScreeningScoreBreakdown, CandidateSkillMatch
from app.models.persona import SyntheticPersona, PersonaGenerationBatch
from app.models.ranking import CandidateRanking
from app.schemas.screening import (
    ScoreBreakdown, MandatoryVerificationResult, CandidateRankingResult,
    ScoreDistributionStats, SkillMatchItem
)
from app.schemas.persona import SyntheticPersonaItem

class ScreeningRepository:
    def create_session(
        self,
        db: Session,
        user_id: str,
        resume_id: str,
        job_id: str,
        scoring_config: Dict[str, Any]
    ) -> ScreeningSession:
        session = ScreeningSession(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            status="pending",
            scoring_config=scoring_config
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_session(self, db: Session, session_id: str) -> Optional[ScreeningSession]:
        return db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()

    def save_screening_results(
        self,
        db: Session,
        session_id: str,
        ats_score: float,
        breakdown: ScoreBreakdown,
        mandatory: MandatoryVerificationResult,
        req_matches: List[SkillMatchItem],
        pref_matches: List[SkillMatchItem],
        full_report: Dict[str, Any]
    ) -> ScreeningSession:
        session = self.get_session(db, session_id)
        if not session:
            return None

        session.ats_score = ats_score
        session.mandatory_status = mandatory.overall_status
        session.mandatory_summary = mandatory.model_dump()
        session.full_report = full_report
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)

        # Save breakdown
        score_rec = ScreeningScoreBreakdown(
            session_id=session.id,
            required_skills_score=breakdown.required_skills.awarded,
            preferred_skills_score=breakdown.preferred_skills.awarded,
            experience_score=breakdown.experience.awarded,
            projects_score=breakdown.projects.awarded,
            education_score=breakdown.education.awarded,
            certifications_score=breakdown.certifications.awarded,
            role_relevance_score=breakdown.role_relevance.awarded,
            total_score=ats_score,
            detailed_components=breakdown.model_dump()
        )
        db.add(score_rec)

        # Save skill matches
        for m in req_matches + pref_matches:
            db.add(CandidateSkillMatch(
                session_id=session.id,
                skill_name=m.skill,
                skill_type=m.category,
                match_status=m.status,
                awarded_credit=m.credit,
                evidence_snippet=m.evidence_snippet
            ))

        db.commit()
        db.refresh(session)
        return session

    def save_synthetic_personas(
        self,
        db: Session,
        session_id: str,
        job_id: str,
        personas: List[SyntheticPersonaItem]
    ):
        batch = PersonaGenerationBatch(
            session_id=session_id,
            batch_number=1,
            groq_model="llama-3.3-70b-versatile",
            total_generated=len(personas)
        )
        db.add(batch)
        db.flush()

        for p in personas:
            db.add(SyntheticPersona(
                id=p.id,
                session_id=session_id,
                job_id=job_id,
                batch_id=batch.id,
                competency_band=p.competency_band,
                profile_data=p.profile.model_dump(),
                ats_score=p.ats_score,
                score_breakdown=p.score_breakdown
            ))
        db.commit()

    def get_synthetic_personas(self, db: Session, session_id: str) -> List[SyntheticPersona]:
        return db.query(SyntheticPersona).filter(SyntheticPersona.session_id == session_id).all()

    def save_ranking(
        self,
        db: Session,
        session_id: str,
        ranking: CandidateRankingResult,
        distribution: ScoreDistributionStats
    ) -> CandidateRanking:
        rank_rec = CandidateRanking(
            session_id=session_id,
            actual_candidate_score=ranking.actual_candidate_score,
            total_candidates_compared=ranking.total_candidates_compared,
            rank=ranking.rank,
            synthetic_candidates_above=ranking.synthetic_candidates_above,
            synthetic_candidates_below=ranking.synthetic_candidates_below,
            synthetic_candidates_tied=ranking.synthetic_candidates_tied,
            percentile=ranking.percentile,
            comparison_type=ranking.comparison_type,
            score_distribution=distribution.model_dump(),
            competency_band_distribution=distribution.band_counts
        )
        db.add(rank_rec)
        db.commit()
        db.refresh(rank_rec)
        return rank_rec

    def get_ranking(self, db: Session, session_id: str) -> Optional[CandidateRanking]:
        return db.query(CandidateRanking).filter(CandidateRanking.session_id == session_id).first()

screening_repo = ScreeningRepository()
