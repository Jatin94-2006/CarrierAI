import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class PersonaGenerationBatch(Base):
    __tablename__ = "persona_generation_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_number = Column(Integer, nullable=False)
    groq_model = Column(String(100), nullable=False)
    prompt_version = Column(String(50), default="1.0")
    total_generated = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    personas = relationship("SyntheticPersona", back_populates="batch", cascade="all, delete-orphan")

class SyntheticPersona(Base):
    __tablename__ = "synthetic_personas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_id = Column(String(36), ForeignKey("persona_generation_batches.id", ondelete="CASCADE"), nullable=True)
    
    # Competency band: very_high, high, upper_middle, middle, lower_middle, low, very_low
    competency_band = Column(String(50), nullable=False, index=True)
    profile_data = Column(JSON, nullable=False) # Full structured candidate profile
    
    # Scored using identical ATS engine
    ats_score = Column(Float, nullable=False, index=True)
    score_breakdown = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ScreeningSession", back_populates="personas")
    job = relationship("Job", back_populates="synthetic_personas")
    batch = relationship("PersonaGenerationBatch", back_populates="personas")
