from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.screening_service import screening_service
from app.repositories.screening_repo import screening_repo
from app.schemas.common import APIResponseEnvelope
from app.core.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/screening", tags=["Ranking & Benchmarking"])

@router.get("/{session_id}/ranking", response_model=APIResponseEnvelope)
def get_candidate_ranking(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves candidate rank, percentile, and benchmark comparison statistics."""
    ranking = screening_service.get_session_ranking(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        resume_id=session.resume_id if session else None,
        job_id=session.job_id if session else None,
        session_id=session_id,
        status="completed",
        data=ranking.model_dump()
    )

@router.get("/{session_id}/distribution", response_model=APIResponseEnvelope)
def get_score_distribution(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves score distribution, variance, standard deviation, and bucket metrics."""
    report = screening_service.get_session_report(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        session_id=session_id,
        status="completed",
        data=report.score_distribution.model_dump()
    )

@router.get("/{session_id}/synthetic-candidates", response_model=APIResponseEnvelope)
def get_synthetic_benchmark_candidates(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves the persisted pool of exactly 100 synthetic benchmark candidate profiles
    generated for this screening session.
    """
    personas = screening_repo.get_synthetic_personas(db, session_id)
    if not personas:
        raise ResourceNotFoundError(f"Synthetic personas for session {session_id} not found")
    
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        session_id=session_id,
        status="completed",
        data={
            "session_id": session_id,
            "total_synthetic_candidates": len(personas),
            "candidates": [
                {
                    "id": p.id,
                    "competency_band": p.competency_band,
                    "ats_score": p.ats_score,
                    "candidate_name": p.profile_data.get("candidate", {}).get("name", "Synthetic Candidate"),
                    "skills": p.profile_data.get("all_skills_flat", []),
                    "score_breakdown": p.score_breakdown
                }
                for p in personas
            ]
        }
    )
