from typing import Any, Optional, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class APIResponseEnvelope(BaseModel):
    """Standardized response contract for all Module 1 APIs as requested in Section 13."""
    schema_version: str = Field(default="1.0", description="Contract schema version")
    user_id: Optional[str] = Field(default=None, description="UUID of the requesting user")
    resume_id: Optional[str] = Field(default=None, description="UUID of the resume")
    job_id: Optional[str] = Field(default=None, description="UUID of the job description")
    session_id: Optional[str] = Field(default=None, description="UUID of the screening session")
    module: str = Field(default="resume_screening", description="Module identifier")
    status: str = Field(default="completed", description="pending, processing, completed, or failed")
    data: Any = Field(default_factory=dict, description="Payload data for the request")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ExtractionEvidence(BaseModel):
    field_name: str
    extracted_value: Optional[str] = None
    evidence_snippet: str
    source_section: Optional[str] = None
    confidence: Optional[float] = None
    status: str = "explicit"  # explicit, inferred, not_found, requires_verification
