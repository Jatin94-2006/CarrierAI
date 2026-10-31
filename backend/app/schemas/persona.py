from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.resume import ResumeStructuredData

class SyntheticPersonaItem(BaseModel):
    id: str
    competency_band: str # very_high, high, upper_middle, middle, lower_middle, low, very_low
    profile: ResumeStructuredData
    ats_score: float
    score_breakdown: Optional[Dict[str, Any]] = None

class SyntheticPersonaPoolResponse(BaseModel):
    session_id: str
    job_id: str
    total_personas: int = 100
    bands_distribution: Dict[str, int]
    personas: List[SyntheticPersonaItem]
