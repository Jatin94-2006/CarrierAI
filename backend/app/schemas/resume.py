from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CandidateInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    current_job_title: Optional[str] = None

class EducationItem(BaseModel):
    degree: Optional[str] = None
    branch: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    score: Optional[str] = None
    evidence: Optional[str] = None

class ExperienceItem(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    employment_type: Optional[str] = None  # Full-time, Part-time, Contract
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    evidence: Optional[str] = None

class InternshipItem(BaseModel):
    organization: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)

class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    contribution: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    outcomes: Optional[str] = None

class CertificationItem(BaseModel):
    name: str
    issuing_organization: Optional[str] = None
    date: Optional[str] = None
    related_skills: List[str] = Field(default_factory=list)

class AchievementItem(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None  # award, competition, publication

class CategorizedSkills(BaseModel):
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud_technologies: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    domain_specific_skills: List[str] = Field(default_factory=list)

class ExtractionMetadata(BaseModel):
    source_format: str = "pdf"
    extraction_status: str = "completed"
    schema_version: str = "1.0"
    ocr_applied: bool = False
    model_used: Optional[str] = None

class ResumeStructuredData(BaseModel):
    candidate: CandidateInfo = Field(default_factory=CandidateInfo)
    education: List[EducationItem] = Field(default_factory=list)
    skills: CategorizedSkills = Field(default_factory=CategorizedSkills)
    all_skills_flat: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    internships: List[InternshipItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    achievements: List[AchievementItem] = Field(default_factory=list)
    extraction_metadata: ExtractionMetadata = Field(default_factory=ExtractionMetadata)

    def model_post_init(self, __context: Any) -> None:
        if not self.all_skills_flat and self.skills:
            flat: List[str] = []
            for cat_list in [
                self.skills.programming_languages,
                self.skills.frameworks,
                self.skills.libraries,
                self.skills.databases,
                self.skills.cloud_technologies,
                self.skills.tools,
                self.skills.soft_skills,
                self.skills.domain_specific_skills,
            ]:
                flat.extend(cat_list)
            self.all_skills_flat = list(dict.fromkeys(flat))

class ResumeUploadResponse(BaseModel):
    resume_id: str
    user_id: str
    file_name: str
    file_type: str
    file_size: int
    raw_text_preview: str
    created_at: str

class ResumeParseRequest(BaseModel):
    resume_id: str
    raw_text: Optional[str] = None
