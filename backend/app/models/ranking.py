import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class CandidateRanking(Base):
    __tablename__ = "candidate_rankings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    actual_candidate_score = Column(Float, nullable=False)
    total_candidates_compared = Column(Integer, default=101) # 1 real + 100 synthetic
    rank = Column(Integer, nullable=False)
    synthetic_candidates_above = Column(Integer, nullable=False)
    synthetic_candidates_below = Column(Integer, nullable=False)
    synthetic_candidates_tied = Column(Integer, nullable=False)
    
    percentile = Column(Float, nullable=False)
    comparison_type = Column(String(50), default="synthetic_benchmark")
    score_distribution = Column(JSON, nullable=False, default=dict)
    competency_band_distribution = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ScreeningSession", back_populates="ranking")
