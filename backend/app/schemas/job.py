from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JobEducationRequirements(BaseModel):
    required_degree: Optional[str] = None
    preferred_specialization: Optional[str] = None

class JobStructuredData(BaseModel):
    title: str
    company: Optional[str] = None
    category: Optional[str] = None
    seniority: str = "Entry Level"
    experience_required: float = 0.0
    preferred_experience: Optional[float] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    required_soft_skills: List[str] = Field(default_factory=list)
    education: JobEducationRequirements = Field(default_factory=JobEducationRequirements)
    mandatory_certifications: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    technical_requirements: List[str] = Field(default_factory=list)
    tools_and_technologies: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    mandatory_requirements: List[str] = Field(default_factory=list)

class JobCreateTextRequest(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    raw_text: str = Field(..., description="Job description in normal text format")

    model_config = {
        "json_schema_extra": {
            "example": {
                "raw_text": "Senior Python Developer\nCompany: TechCorp\nExperience: 4+ years\nRequired Skills: Python, FastAPI, Docker, PostgreSQL, Redis\nEducation: Bachelor's in Computer Science\nResponsibilities: Design scalable microservices and build clean REST APIs."
            }
        }
    }

class JobCreateJSONRequest(BaseModel):
    job: JobStructuredData
