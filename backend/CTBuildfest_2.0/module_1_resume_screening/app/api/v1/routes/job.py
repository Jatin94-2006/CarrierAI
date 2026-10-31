from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.job_service import job_service
from app.schemas.common import APIResponseEnvelope
from app.schemas.job import JobCreateTextRequest, JobCreateJSONRequest
from app.parsers.job_extractor import extract_structured_job

router = APIRouter(prefix="/screening/job", tags=["Job Description"])

@router.post("/parse", response_model=APIResponseEnvelope)
def parse_job_description(
    req: JobCreateTextRequest,
    db: Session = Depends(get_db)
):
    """Parses raw text of a job description into structured requirements without storing."""
    structured = extract_structured_job(req.raw_text)
    return APIResponseEnvelope(
        status="completed",
        data=structured.model_dump()
    )

@router.post("", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
def create_job(
    req: JobCreateTextRequest,
    db: Session = Depends(get_db)
):
    """Creates, parses, and persists a new Job Description in Supabase."""
    job_rec, structured = job_service.create_or_parse_job(db, req.raw_text)
    return APIResponseEnvelope(
        job_id=job_rec.id,
        status="completed",
        data={
            "job_id": job_rec.id,
            "title": job_rec.title,
            "structured_data": structured.model_dump(),
            "created_at": job_rec.created_at.isoformat() + "Z"
        }
    )

@router.get("/{job_id}", response_model=APIResponseEnvelope)
def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves structured Job Description by ID."""
    data = job_service.get_job_data(db, job_id)
    return APIResponseEnvelope(
        job_id=job_id,
        status="completed",
        data=data.model_dump()
    )
