"""
Agent 3: Course Suggestion Agent
Pydantic schemas for input/output data models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime


# ─────────────────────────────────────────────
#  INPUT  (from Agent 2 – Gap Analysis Agent)
# ─────────────────────────────────────────────

class SkillGapInput(BaseModel):
    """
    Input received from Agent 2 (Gap Analysis Agent).
    Also used directly via the API for standalone testing.
    """
    technical_skills: List[str] = Field(
        default_factory=list,
        description="List of missing or weak technical skills",
        example=["Python", "SQL", "Power BI"]
    )
    soft_skills: List[str] = Field(
        default_factory=list,
        description="List of missing or weak soft skills",
        example=["Communication", "Leadership"]
    )
    skill_levels: Dict[str, Literal["Missing", "Beginner", "Intermediate", "Advanced"]] = Field(
        default_factory=dict,
        description="Proficiency level per skill",
        example={"Python": "Intermediate", "SQL": "Beginner", "Power BI": "Missing"}
    )
    target_job_role: Optional[str] = Field(
        default=None,
        description="User's target job role, e.g. 'Data Analyst'",
        example="Data Analyst"
    )
    resume_summary: Optional[str] = Field(
        default=None,
        description="Optional summary from Agent 1 (Resume Analysis)"
    )


# ─────────────────────────────────────────────
#  OUTPUT  (to frontend + Agent 5 – Learning Planner)
# ─────────────────────────────────────────────

class CourseRecommendation(BaseModel):
    """A single course / tutorial / video recommendation."""
    title: str = Field(description="Course or video title")
    platform: str = Field(description="Platform name (e.g. freeCodeCamp, YouTube)")
    skill: str = Field(description="The skill this resource targets")
    skill_category: Literal["Technical", "Soft"] = Field(description="Technical or Soft skill")
    difficulty: Literal["Beginner", "Intermediate", "Advanced"] = Field(
        description="Difficulty level of the resource"
    )
    description: str = Field(description="Short description of the resource")
    url: str = Field(description="Direct URL to the learning resource")
    resource_type: Literal["Course", "Tutorial", "Video", "Playlist", "Documentation"] = Field(
        description="Type of resource"
    )
    is_free: bool = Field(default=True, description="Verified free resource")
    thumbnail: Optional[str] = Field(default=None, description="Thumbnail image URL")
    duration: Optional[str] = Field(default=None, description="Estimated duration if available")
    source: Literal["tavily", "youtube", "sample"] = Field(
        default="sample",
        description="Where this recommendation came from"
    )


class ResponseMetadata(BaseModel):
    total_resources: int
    technical_count: int
    soft_count: int
    skills_covered: List[str]
    demo_mode: bool = Field(
        description="True when running without real API keys (sample data)"
    )
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class CourseResponse(BaseModel):
    """
    Full response from Agent 3.
    Returned to the frontend and available to Agent 5 (Learning Planner).
    """
    status: Literal["success", "partial", "error"] = "success"
    message: Optional[str] = None
    technical_recommendations: List[CourseRecommendation] = Field(default_factory=list)
    soft_recommendations: List[CourseRecommendation] = Field(default_factory=list)
    metadata: ResponseMetadata


class HealthResponse(BaseModel):
    status: str = "ok"
    agent: str = "Course Suggestion Agent (Agent 3)"
    demo_mode: bool
    version: str = "1.0.0"
