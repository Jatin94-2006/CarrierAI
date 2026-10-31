from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.screening_service import screening_service
from app.repositories.screening_repo import screening_repo
from app.schemas.common import APIResponseEnvelope

router = APIRouter(prefix="/screening", tags=["Inter-Module Integration"])

@router.get("/{session_id}/skill-gap-input", response_model=APIResponseEnvelope)
def get_module2_skill_gap_input(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Standardized payload for Module 2: Skill Gap Analysis.
    Provides structured resume, JD, matched/partially matched/missing skills,
    skill importance weights, and evidence snippets.
    """
    data = screening_service.get_module2_skill_gap_input(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        resume_id=session.resume_id if session else None,
        job_id=session.job_id if session else None,
        session_id=session_id,
        module="skill_gap_analysis",
        status="completed",
        data=data.model_dump()
    )

@router.get("/{session_id}/course-input", response_model=APIResponseEnvelope)
def get_module3_course_input(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Standardized payload for Module 3: Course Recommendations.
    Provides missing skills, partially matched skills, skill importance,
    and existing skill competency levels.
    """
    data = screening_service.get_module3_course_input(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        session_id=session_id,
        module="course_recommendations",
        status="completed",
        data=data.model_dump()
    )

@router.get("/{session_id}/interview-input", response_model=APIResponseEnvelope)
def get_module4_interview_input(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Standardized payload for Module 4: AI Mock Interview.
    Provides resume JSON, JD, project details, and areas with weak evidence
    or missing skills to target in interview questions.
    """
    data = screening_service.get_module4_interview_input(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        session_id=session_id,
        module="mock_interview",
        status="completed",
        data=data.model_dump()
    )

@router.get("/{session_id}/improvement-plan-input", response_model=APIResponseEnvelope)
def get_module5_improvement_plan_input(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Standardized payload for Module 5: Personalized 30-Day Improvement Plan.
    Provides ATS score breakdown, missing skills, prioritized requirements,
    and project/experience gaps.
    """
    data = screening_service.get_module5_improvement_plan_input(db, session_id)
    session = screening_repo.get_session(db, session_id)
    return APIResponseEnvelope(
        user_id=session.user_id if session else None,
        session_id=session_id,
        module="improvement_plan",
        status="completed",
        data=data.model_dump()
    )
