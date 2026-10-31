from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.resume import Resume, ResumeExtraction, ExtractedEvidence
from app.schemas.resume import ResumeStructuredData
from app.schemas.common import ExtractionEvidence

class ResumeRepository:
    def create_resume(
        self,
        db: Session,
        user_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        raw_text: str,
        file_path: Optional[str] = None
    ) -> Resume:
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            raw_text=raw_text,
            file_path=file_path
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    def get_resume(self, db: Session, resume_id: str) -> Optional[Resume]:
        return db.query(Resume).filter(Resume.id == resume_id).first()

    def save_extraction(
        self,
        db: Session,
        resume_id: str,
        data: ResumeStructuredData,
        evidence_items: List[ExtractionEvidence]
    ) -> ResumeExtraction:
        extraction = ResumeExtraction(
            resume_id=resume_id,
            candidate_info=data.candidate.model_dump(),
            education=[e.model_dump() for e in data.education],
            skills=data.skills.model_dump(),
            experience=[e.model_dump() for e in data.experience],
            internships=[i.model_dump() for i in data.internships],
            projects=[p.model_dump() for p in data.projects],
            certifications=[c.model_dump() for c in data.certifications],
            achievements=[a.model_dump() for a in data.achievements],
            extraction_metadata=data.extraction_metadata.model_dump()
        )
        db.add(extraction)
        db.flush()

        for evi in evidence_items:
            ev_record = ExtractedEvidence(
                extraction_id=extraction.id,
                field_name=evi.field_name,
                extracted_value=evi.extracted_value,
                evidence_snippet=evi.evidence_snippet,
                source_section=evi.source_section,
                confidence=str(evi.confidence) if evi.confidence else None,
                status=evi.status
            )
            db.add(ev_record)

        db.commit()
        db.refresh(extraction)
        return extraction

    def get_extraction(self, db: Session, resume_id: str) -> Optional[ResumeExtraction]:
        return db.query(ResumeExtraction).filter(ResumeExtraction.resume_id == resume_id).order_by(ResumeExtraction.created_at.desc()).first()

resume_repo = ResumeRepository()
