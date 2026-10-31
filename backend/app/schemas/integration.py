from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.resume import ResumeStructuredData
from app.schemas.job import JobStructuredData
from app.schemas.screening import ScoreBreakdown, SkillMatchItem

class Module2SkillGapInput(BaseModel):
    session_id: str
    resume_id: str
    job_id: str
    resume_data: ResumeStructuredData
    job_data: JobStructuredData
    required_skills: List[str]
    preferred_skills: List[str]
    matched_skills: List[SkillMatchItem]
    partially_matched_skills: List[SkillMatchItem]
    missing_skills: List[SkillMatchItem]
    unverified_skills: List[SkillMatchItem]
    skill_importance_weights: Dict[str, float]
    evidence_snippets: Dict[str, str]
    ats_score_breakdown: ScoreBreakdown

class Module3CourseInput(BaseModel):
    session_id: str
    target_job_title: str
    missing_skills: List[str]
    partially_matched_skills: List[str]
    skill_importance: Dict[str, float]
    candidate_existing_skill_level: Dict[str, str] # beginner, intermediate, absent
    job_requirements: List[str]

class Module4InterviewInput(BaseModel):
    session_id: str
    target_job_title: str
    resume_json: ResumeStructuredData
    job_description: JobStructuredData
    projects: List[Dict[str, Any]]
    technical_skills: List[str]
    professional_experience: List[Dict[str, Any]]
    areas_of_weak_or_missing_evidence: List[str]
    suggested_interview_focus: List[str]

class Module5ImprovementPlanInput(BaseModel):
    session_id: str
    ats_score: float
    score_breakdown: ScoreBreakdown
    missing_skills: List[str]
    priority_requirements: List[str]
    project_gaps: List[str]
    experience_gaps: List[str]
    percentile: float
    suggested_30_day_milestones: List[str]
