"""
Pydantic Schemas — CTBF-AI-05 Standard JSON Contracts
All inter-module data MUST pass through these schemas.
"""

from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


# ─── Shared ──────────────────────────────────────────────────────────────────

def new_uuid() -> str:
    return str(uuid.uuid4())


# ─── Module 1 — Resume Analysis ──────────────────────────────────────────────

class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: Optional[List[str]] = None


class ExperienceItem(BaseModel):
    company: str
    role: str
    duration_years: Optional[float] = None
    responsibilities: Optional[List[str]] = None


class ResumeData(BaseModel):
    """Parsed structured resume output from Module 1."""
    user_id: str = Field(default_factory=new_uuid)
    resume_id: str = Field(default_factory=new_uuid)
    full_name: Optional[str] = None
    email: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    education: Optional[str] = None
    projects: List[ProjectItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    raw_resume_text: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class JDData(BaseModel):
    """Parsed structured Job Description output from Module 1."""
    job_id: str = Field(default_factory=new_uuid)
    title: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_required: Optional[float] = None
    raw_jd_text: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class Module1Output(BaseModel):
    """Complete output of Module 1 → fed as input to Module 2."""
    resume: ResumeData
    jd: JDData
    session_id: str = Field(default_factory=new_uuid)


# ─── Module 2 — Gap Analysis ─────────────────────────────────────────────────

class GapAnalysisData(BaseModel):
    """Core gap analysis results (CTBF-AI-05 data envelope)."""
    critical_gaps: List[str] = Field(default_factory=list)
    important_gaps: List[str] = Field(default_factory=list)
    optional_gaps: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    improvement_priority_order: List[str] = Field(default_factory=list)


class GapReportEnvelope(BaseModel):
    """CTBF-AI-05 Standard Envelope — Module 2 output."""
    user_id: str
    resume_id: str
    job_id: str
    session_id: str
    module: str = "skill_gap_analysis"
    status: str = "completed"
    data: GapAnalysisData
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# ─── Module 3 — Course Suggestions ───────────────────────────────────────────

class CourseItem(BaseModel):
    """A single learning resource."""
    skill: str
    title: str
    url: str
    platform: str
    type: str  # 'video' | 'article' | 'course' | 'docs'
    is_free: bool = True
    estimated_hours: Optional[float] = None


class CoursesData(BaseModel):
    """Grouped courses per skill."""
    skill: str
    resources: List[CourseItem]


class Module3Output(BaseModel):
    """CTBF-AI-05 envelope — Module 3 output."""
    user_id: str
    session_id: str
    module: str = "course_suggestions"
    status: str = "completed"
    data: List[CoursesData]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# ─── Module 4 — Interview Preparation ────────────────────────────────────────

class QAItem(BaseModel):
    """Single question-answer pair from mock interview."""
    question: str
    expected_answer: Optional[str] = None
    user_answer: Optional[str] = None
    evaluation: Optional[str] = None  # 'strong' | 'average' | 'weak'
    score: Optional[float] = None  # 0.0–1.0


class InterviewReportData(BaseModel):
    total_questions: int
    qa_pairs: List[QAItem]
    weak_areas: List[str]
    strong_areas: List[str]
    overall_score: float  # 0.0–1.0
    recommendation: Optional[str] = None


class Module4Output(BaseModel):
    """CTBF-AI-05 envelope — Module 4 output."""
    user_id: str
    session_id: str
    module: str = "interview_preparation"
    status: str = "completed"
    data: InterviewReportData
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# ─── Module 5 — Learning Planner ─────────────────────────────────────────────

class DayPlan(BaseModel):
    day: int
    topic: str
    skill: str
    tasks: List[str]
    resources: List[str]
    estimated_hours: float


class WeekPlan(BaseModel):
    week: int
    focus: str
    days: List[DayPlan]


class LearningPlanData(BaseModel):
    plan_type: str  # '30_day' | '3_month' | '6_month'
    total_days: int
    skills_covered: List[str]
    schedule: List[DayPlan]


class Module5Output(BaseModel):
    """CTBF-AI-05 envelope — Module 5 output."""
    user_id: str
    session_id: str
    module: str = "learning_planner"
    status: str = "completed"
    data: LearningPlanData
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
