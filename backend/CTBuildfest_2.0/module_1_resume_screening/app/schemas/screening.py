from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.resume import ResumeStructuredData
from app.schemas.job import JobStructuredData

class ScoreComponentItem(BaseModel):
    weight: float
    maximum_points: float
    awarded: float
    calculation_method: str
    matching_evidence: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    explanation: str

class ScoreBreakdown(BaseModel):
    required_skills: ScoreComponentItem
    preferred_skills: ScoreComponentItem
    experience: ScoreComponentItem
    projects: ScoreComponentItem
    education: ScoreComponentItem
    certifications: ScoreComponentItem
    role_relevance: ScoreComponentItem

class SkillMatchItem(BaseModel):
    skill: str
    category: str # required or preferred
    status: str # exact_match, verified_equivalent, related, missing, unverified
    credit: float # 0.0 to 1.0
    matched_with: Optional[str] = None
    evidence_snippet: Optional[str] = None

class MandatoryRequirementItem(BaseModel):
    requirement: str
    status: str # met, not_met, unverified
    evidence: Optional[str] = None
    explanation: str

class MandatoryVerificationResult(BaseModel):
    overall_status: str # met, not_met, unverified
    total_mandatory: int
    met_count: int
    not_met_count: int
    unverified_count: int
    requirements: List[MandatoryRequirementItem] = Field(default_factory=list)

class CandidateRankingResult(BaseModel):
    actual_candidate_score: float
    total_candidates_compared: int = 101
    rank: int
    synthetic_candidates_above: int
    synthetic_candidates_below: int
    synthetic_candidates_tied: int
    percentile: float
    comparison_type: str = "synthetic_benchmark"
    explanation: str

class ScoreDistributionStats(BaseModel):
    min_score: float
    max_score: float
    mean_score: float
    median_score: float
    std_dev: float
    distribution_buckets: Dict[str, int] = Field(default_factory=dict)
    band_counts: Dict[str, int] = Field(default_factory=dict)

class FullScreeningReport(BaseModel):
    session_id: str
    candidate_summary: Dict[str, Any]
    job_summary: Dict[str, Any]
    overall_ats_score: float
    score_breakdown: ScoreBreakdown
    skills_assessment: Dict[str, List[SkillMatchItem]] # matched, partially_matched, missing, unverified
    mandatory_verification: MandatoryVerificationResult
    experience_assessment: Dict[str, Any]
    projects_assessment: Dict[str, Any]
    education_assessment: Dict[str, Any]
    certifications_assessment: Dict[str, Any]
    missing_ats_keywords: List[str]
    strengths: List[str]
    areas_requiring_improvement: List[str]
    ranking: CandidateRankingResult
    score_distribution: ScoreDistributionStats

class AnalyzeRequest(BaseModel):
    resume_id: str
    job_id: str
    user_id: Optional[str] = None
    generate_synthetic_benchmark: bool = True

class AnalyzeJSONRequest(BaseModel):
    resume_data: ResumeStructuredData
    job_data: Optional[JobStructuredData] = Field(default=None, description="Structured JSON Job Description")
    job_text: Optional[str] = Field(default=None, description="Normal plain text Job Description to be automatically converted to JSON format")
    user_id: Optional[str] = None
    generate_synthetic_benchmark: bool = True
