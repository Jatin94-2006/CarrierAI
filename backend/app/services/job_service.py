from typing import Optional, Union, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import ResourceNotFoundError
from app.repositories.job_repo import job_repo
from app.parsers.job_extractor import extract_structured_job
from app.schemas.job import JobStructuredData
from app.models.job import Job

class JobService:
    def create_or_parse_job(
        self,
        db: Session,
        job_input: Union[str, Dict[str, Any]]
    ) -> Tuple[Job, JobStructuredData]:
        raw_text = job_input if isinstance(job_input, str) else None
        structured = extract_structured_job(job_input)
        job_record = job_repo.create_job(db, structured, raw_text=raw_text)
        return job_record, structured

    def get_job_data(self, db: Session, job_id: str) -> JobStructuredData:
        job = job_repo.get_job(db, job_id)
        if not job:
            raise ResourceNotFoundError(f"Job description with id {job_id} not found")
        return JobStructuredData(**job.structured_data)

job_service = JobService()
