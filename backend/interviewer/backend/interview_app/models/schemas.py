from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator

class Question(BaseModel):
    q_id: int
    phase: Literal["intro", "project", "technical", "scenario", "hr", "closing", "farewell"]
    type: Literal["technical", "hr"] = "technical"
    source: str  # "project: <name>" or "skill: <name>"
    skill_tested: str
    difficulty: Literal["easy", "medium", "hard"]
    question: str
    time_limit_sec: int = Field(ge=60, le=240)

class QuestionSet(BaseModel):
    role: str
    questions: List[Question] = Field(min_length=5, max_length=8)

    @model_validator(mode="after")
    def enough_time(self):
        total_time = sum(q.time_limit_sec for q in self.questions)
        if total_time < 300:
            raise ValueError(f"Total time budget must be at least 5 minutes (300s), got {total_time}s")
        return self

class BehavioralAnalysis(BaseModel):
    primary_expression: str = "neutral and attentive"
    eye_contact_score: float = Field(ge=0.0, le=1.0, default=0.85)
    confidence_level: Literal["low", "medium", "high"] = "medium"
    nervousness: Literal["low", "medium", "high"] = "low"
    observations: str = "Maintained steady gaze and composed posture."

class InterviewItem(BaseModel):
    q_id: int
    phase: Literal["intro", "project", "technical", "scenario", "hr", "closing", "farewell"]
    type: Literal["technical", "hr"]
    source: str
    skill_tested: str
    difficulty: Literal["easy", "medium", "hard"]
    question: str
    time_limit_sec: int
    status: Literal["answered", "skipped", "in_progress", "pending"] = "pending"
    answer: Optional[str] = None
    duration_sec: int = 0
    behavioral_analysis: Optional[BehavioralAnalysis] = None

class CreateInterviewResponse(BaseModel):
    interview_id: str
    role: str
    candidate_name: str
    total_questions: int
    questions: List[Question]

class AnswerSubmissionResponse(BaseModel):
    q_id: int
    status: str
    transcript: str
    duration_sec: int
    behavioral_analysis: Optional[BehavioralAnalysis] = None

class UpdateAnswerRequest(BaseModel):
    transcript: str

class FinalInterviewOutput(BaseModel):
    interview_id: str
    role: str
    candidate_name: str
    total_questions: int
    answered_count: int
    skipped_count: int
    items: List[InterviewItem]
