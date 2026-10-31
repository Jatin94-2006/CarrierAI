import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    extractions = relationship("ResumeExtraction", back_populates="resume", cascade="all, delete-orphan")
    screening_sessions = relationship("ScreeningSession", back_populates="resume")

class ResumeExtraction(Base):
    __tablename__ = "resume_extractions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Structured JSON data
    candidate_info = Column(JSON, nullable=False, default=dict)
    education = Column(JSON, nullable=False, default=list)
    skills = Column(JSON, nullable=False, default=list)
    experience = Column(JSON, nullable=False, default=list)
    internships = Column(JSON, nullable=False, default=list)
    projects = Column(JSON, nullable=False, default=list)
    certifications = Column(JSON, nullable=False, default=list)
    achievements = Column(JSON, nullable=False, default=list)
    extraction_metadata = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="extractions")
    evidence_items = relationship("ExtractedEvidence", back_populates="extraction", cascade="all, delete-orphan")

class ExtractedEvidence(Base):
    __tablename__ = "extracted_evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    extraction_id = Column(String(36), ForeignKey("resume_extractions.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    extracted_value = Column(Text, nullable=True)
    evidence_snippet = Column(Text, nullable=False)
    source_section = Column(String(100), nullable=True)
    confidence = Column(String(50), nullable=True)
    status = Column(String(50), default="explicit")  # explicit, inferred, not_found, requires_verification
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    extraction = relationship("ResumeExtraction", back_populates="evidence_items")
