from typing import Optional
from sqlalchemy.orm import Session
from app.models.job import Job, JobRequirement
from app.schemas.job import JobStructuredData

class JobRepository:
    def create_job(
        self,
        db: Session,
        job_data: JobStructuredData,
        raw_text: Optional[str] = None
    ) -> Job:
        job = Job(
            title=job_data.title,
            company=job_data.company,
            category=job_data.category,
            seniority=job_data.seniority,
            min_experience_years=job_data.experience_required,
            raw_text=raw_text,
            structured_data=job_data.model_dump()
        )
        db.add(job)
        db.flush()

        # Add requirements
        for skill in job_data.required_skills:
            db.add(JobRequirement(
                job_id=job.id,
                requirement_type="skill",
                category="required",
                description=skill,
                importance_weight=1.0
            ))
        for skill in job_data.preferred_skills:
            db.add(JobRequirement(
                job_id=job.id,
                requirement_type="skill",
                category="preferred",
                description=skill,
                importance_weight=0.5
            ))
        for req in job_data.mandatory_requirements:
            db.add(JobRequirement(
                job_id=job.id,
                requirement_type="mandatory",
                category="mandatory",
                description=req,
                importance_weight=1.5
            ))

        db.commit()
        db.refresh(job)
        return job

    def get_job(self, db: Session, job_id: str) -> Optional[Job]:
        return db.query(Job).filter(Job.id == job_id).first()

job_repo = JobRepository()
