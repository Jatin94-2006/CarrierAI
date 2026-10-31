import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    seniority = Column(String(50), nullable=True)
    min_experience_years = Column(Float, default=0.0)
    raw_text = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    screening_sessions = relationship("ScreeningSession", back_populates="job")
    synthetic_personas = relationship("SyntheticPersona", back_populates="job")

class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_type = Column(String(50), nullable=False) # skill, experience, education, certification
    category = Column(String(50), nullable=False) # mandatory, required, preferred, optional
    description = Column(Text, nullable=False)
    importance_weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    job = relationship("Job", back_populates="requirements")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True) # language, framework, database, cloud, tool, soft_skill
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aliases = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")

class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    alias = Column(String(100), nullable=False, index=True)
    is_verified_equivalent = Column(Boolean, default=True)

    skill = relationship("Skill", back_populates="aliases")
