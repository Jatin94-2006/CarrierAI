import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True) # pending, processing, completed, failed
    
    # Overall ATS calculation
    ats_score = Column(Float, nullable=True)
    mandatory_status = Column(String(50), nullable=True) # met, not_met, unverified
    mandatory_summary = Column(JSON, nullable=True, default=dict)
    
    scoring_config = Column(JSON, nullable=False, default=dict)
    full_report = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    resume = relationship("Resume", back_populates="screening_sessions")
    job = relationship("Job", back_populates="screening_sessions")
    score_breakdown = relationship("ScreeningScoreBreakdown", back_populates="session", uselist=False, cascade="all, delete-orphan")
    skill_matches = relationship("CandidateSkillMatch", back_populates="session", cascade="all, delete-orphan")
    personas = relationship("SyntheticPersona", back_populates="session", cascade="all, delete-orphan")
    ranking = relationship("CandidateRanking", back_populates="session", uselist=False, cascade="all, delete-orphan")

class ScreeningScoreBreakdown(Base):
    __tablename__ = "screening_score_breakdowns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    required_skills_score = Column(Float, default=0.0)
    preferred_skills_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    projects_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    certifications_score = Column(Float, default=0.0)
    role_relevance_score = Column(Float, default=0.0)
    
    total_score = Column(Float, default=0.0)
    detailed_components = Column(JSON, nullable=False, default=dict)

    session = relationship("ScreeningSession", back_populates="score_breakdown")

class CandidateSkillMatch(Base):
    __tablename__ = "candidate_skill_matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    skill_type = Column(String(50), nullable=False) # required, preferred
    match_status = Column(String(50), nullable=False) # exact_match, verified_equivalent, related, missing, unverified
    awarded_credit = Column(Float, default=0.0)
    evidence_snippet = Column(Text, nullable=True)

    session = relationship("ScreeningSession", back_populates="skill_matches")
