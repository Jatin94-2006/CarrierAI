from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.services.resume_service import resume_service
from app.repositories.resume_repo import resume_repo
from app.schemas.common import APIResponseEnvelope
from app.schemas.resume import ResumeParseRequest
from app.core.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/screening/resume", tags=["Resume"])

@router.post("/upload", response_model=APIResponseEnvelope, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Accepts PDF, DOCX, or JSON resume upload.
    Validates file format and size, extracts text, applies OCR fallback if scanned,
    and returns standardized extraction confirmation.
    """
    result = await resume_service.upload_resume(db=db, file=file, user_id=user_id)
    return APIResponseEnvelope(
        user_id=result.user_id,
        resume_id=result.resume_id,
        status="completed",
        data=result.model_dump()
    )

@router.post("/parse", response_model=APIResponseEnvelope)
def parse_resume(
    req: ResumeParseRequest,
    db: Session = Depends(get_db)
):
    """Parses or re-parses an existing uploaded resume into structured format."""
    structured = resume_service.parse_existing_resume(db, req.resume_id)
    resume = resume_repo.get_resume(db, req.resume_id)
    return APIResponseEnvelope(
        user_id=resume.user_id if resume else None,
        resume_id=req.resume_id,
        status="completed",
        data=structured.model_dump()
    )

@router.get("/{resume_id}", response_model=APIResponseEnvelope)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves basic resume metadata and preview."""
    resume = resume_repo.get_resume(db, resume_id)
    if not resume:
        raise ResourceNotFoundError(f"Resume {resume_id} not found")
    return APIResponseEnvelope(
        user_id=resume.user_id,
        resume_id=resume.id,
        status="completed",
        data={
            "id": resume.id,
            "file_name": resume.file_name,
            "file_type": resume.file_type,
            "file_size": resume.file_size,
            "raw_text_preview": (resume.raw_text or "")[:400],
            "created_at": resume.created_at.isoformat() + "Z"
        }
    )

@router.get("/{resume_id}/extraction", response_model=APIResponseEnvelope)
def get_resume_extraction(
    resume_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves complete structured JSON extraction for a resume."""
    structured = resume_service.get_resume_data(db, resume_id)
    resume = resume_repo.get_resume(db, resume_id)
    return APIResponseEnvelope(
        user_id=resume.user_id if resume else None,
        resume_id=resume_id,
        status="completed",
        data=structured.model_dump()
    )
