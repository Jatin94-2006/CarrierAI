import uuid
import os
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.core.exceptions import FileValidationError, ResourceNotFoundError
from app.core.security import validate_uploaded_file
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.json_parser import parse_resume_json
from app.parsers.ocr_parser import apply_ocr_fallback
from app.parsers.resume_extractor import extract_structured_resume
from app.repositories.resume_repo import resume_repo
from app.schemas.resume import ResumeStructuredData, ResumeUploadResponse

class ResumeService:
    async def upload_resume(
        self,
        db: Session,
        file: UploadFile,
        user_id: Optional[str] = None
    ) -> ResumeUploadResponse:
        ext = validate_uploaded_file(file)
        user_uuid = user_id or str(uuid.uuid4())
        content = await file.read()
        file_size = len(content)

        ocr_applied = False
        raw_text = ""

        if ext == "pdf":
            raw_text, is_scanned = extract_text_from_pdf(content)
            if is_scanned:
                ocr_text = apply_ocr_fallback(content)
                if ocr_text:
                    raw_text = ocr_text
                    ocr_applied = True
        elif ext == "docx":
            raw_text = extract_text_from_docx(content)
        elif ext == "json":
            # For JSON, validate immediately and keep raw string
            structured = parse_resume_json(content)
            raw_text = content.decode("utf-8", errors="ignore")

        resume_rec = resume_repo.create_resume(
            db=db,
            user_id=user_uuid,
            file_name=file.filename or "uploaded_resume",
            file_type=ext,
            file_size=file_size,
            raw_text=raw_text
        )

        # Automatically extract and store structured representation
        if ext == "json":
            structured_data = parse_resume_json(content)
            resume_repo.save_extraction(db, resume_rec.id, structured_data, [])
        else:
            structured_data, evidence = extract_structured_resume(
                raw_text=raw_text,
                source_format=ext,
                ocr_applied=ocr_applied
            )
            resume_repo.save_extraction(db, resume_rec.id, structured_data, evidence)

        return ResumeUploadResponse(
            resume_id=resume_rec.id,
            user_id=user_uuid,
            file_name=resume_rec.file_name,
            file_type=resume_rec.file_type,
            file_size=resume_rec.file_size,
            raw_text_preview=raw_text[:300] if raw_text else "",
            created_at=resume_rec.created_at.isoformat() + "Z"
        )

    def parse_existing_resume(
        self,
        db: Session,
        resume_id: str
    ) -> ResumeStructuredData:
        resume = resume_repo.get_resume(db, resume_id)
        if not resume:
            raise ResourceNotFoundError(f"Resume with id {resume_id} not found")

        # Check if already extracted
        existing_extraction = resume_repo.get_extraction(db, resume_id)
        if existing_extraction:
            # Reconstruct model from stored fields
            return ResumeStructuredData(
                candidate=existing_extraction.candidate_info,
                education=existing_extraction.education,
                skills=existing_extraction.skills,
                experience=existing_extraction.experience,
                internships=existing_extraction.internships,
                projects=existing_extraction.projects,
                certifications=existing_extraction.certifications,
                achievements=existing_extraction.achievements,
                extraction_metadata=existing_extraction.extraction_metadata
            )

        # Otherwise extract fresh
        structured_data, evidence = extract_structured_resume(
            raw_text=resume.raw_text or "",
            source_format=resume.file_type
        )
        resume_repo.save_extraction(db, resume.id, structured_data, evidence)
        return structured_data

    def get_resume_data(self, db: Session, resume_id: str) -> ResumeStructuredData:
        return self.parse_existing_resume(db, resume_id)

resume_service = ResumeService()
