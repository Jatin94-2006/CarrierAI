from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.screening_service import screening_service
from app.services.resume_service import resume_service
from app.services.job_service import job_service
from app.repositories.resume_repo import resume_repo
from app.repositories.screening_repo import screening_repo
from app.schemas.common import APIResponseEnvelope
from app.schemas.screening import (
    AnalyzeRequest,
    AnalyzeJSONRequest,
    FullScreeningReport,
)
from app.core.exceptions import ResourceNotFoundError, BaseScreeningException

router = APIRouter(prefix="/screening", tags=["ATS Screening"])

@router.post("/analyze", response_model=APIResponseEnvelope, status_code=status.HTTP_200_OK)
def analyze_resume_against_job(
    req: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Triggers complete ATS screening pipeline:
    - Calculates explainable ATS score (0-100)
    - Verifies mandatory requirements
    - Generates 100 synthetic benchmark candidates
    - Computes rank & percentile
    - Persists all results to Supabase
    """
    report = screening_service.analyze_session(
        db=db,
        resume_id=req.resume_id,
        job_id=req.job_id,
        user_id=req.user_id,
        generate_synthetic_benchmark=req.generate_synthetic_benchmark
    )
    return APIResponseEnvelope(
        user_id=req.user_id,
        resume_id=req.resume_id,
        job_id=req.job_id,
        session_id=report.session_id,
        status="completed",
        data=report.model_dump()
    )

@router.post("/analyze-json", response_model=APIResponseEnvelope)
def analyze_direct_json(
    req: AnalyzeJSONRequest,
    db: Session = Depends(get_db)
):
    """
    Analyzes pre-structured JSON resume directly against pre-structured JSON job description.
    Persists entities and screening session.
    """
    user_id = req.user_id or "json_user"
    
    # 1. Store resume
    resume_rec = resume_repo.create_resume(
        db=db,
        user_id=user_id,
        file_name="direct_json_candidate.json",
        file_type="json",
        file_size=1024,
        raw_text=req.resume_data.candidate.summary or ""
    )
    resume_repo.save_extraction(db, resume_rec.id, req.resume_data, [])

    # 2. Store job (supports either pre-structured JSON or normal plain text)
    if req.job_data:
        job_rec, _ = job_service.create_or_parse_job(db, req.job_data.model_dump())
    elif req.job_text:
        job_rec, _ = job_service.create_or_parse_job(db, req.job_text)
    else:
        raise BaseScreeningException("Either 'job_data' (JSON) or 'job_text' (normal plain text) must be provided", status_code=400)

    # 3. Analyze
    report = screening_service.analyze_session(
        db=db,
        resume_id=resume_rec.id,
        job_id=job_rec.id,
        user_id=user_id,
        generate_synthetic_benchmark=req.generate_synthetic_benchmark
    )

    return APIResponseEnvelope(
        user_id=user_id,
        resume_id=resume_rec.id,
        job_id=job_rec.id,
        session_id=report.session_id,
        status="completed",
        data=report.model_dump()
    )

@router.get("/{session_id}", response_model=APIResponseEnvelope)
def get_session_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Checks session status and overall ATS score."""
    session = screening_repo.get_session(db, session_id)
    if not session:
        raise ResourceNotFoundError(f"Screening session {session_id} not found")
    return APIResponseEnvelope(
        user_id=session.user_id,
        resume_id=session.resume_id,
        job_id=session.job_id,
        session_id=session.id,
        status=session.status,
        data={
            "session_id": session.id,
            "status": session.status,
            "ats_score": session.ats_score,
            "mandatory_status": session.mandatory_status,
            "created_at": session.created_at.isoformat() + "Z",
            "completed_at": session.completed_at.isoformat() + "Z" if session.completed_at else None
        }
    )

@router.get("/{session_id}/score", response_model=APIResponseEnvelope)
def get_screening_score(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves explainable ATS match score and 7-component weight breakdown."""
    report = screening_service.get_session_report(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        resume_id=session.resume_id if session else None,
        job_id=session.job_id if session else None,
        session_id=session_id,
        status="completed",
        data={
            "ats_score": report.overall_ats_score,
            "score_breakdown": report.score_breakdown.model_dump(),
            "mandatory_verification": report.mandatory_verification.model_dump()
        }
    )

@router.get("/{session_id}/report", response_model=APIResponseEnvelope)
def get_screening_report(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves complete detailed screening report."""
    report = screening_service.get_session_report(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        resume_id=session.resume_id if session else None,
        job_id=session.job_id if session else None,
        session_id=session_id,
        status="completed",
        data=report.model_dump()
    )
