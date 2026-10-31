import pytest
from app.matching.ats_engine import ats_engine, ATSEngine
from app.schemas.resume import (
    ResumeStructuredData, CandidateInfo, CategorizedSkills,
    EducationItem, ExperienceItem, ProjectItem, CertificationItem
)
from app.schemas.job import JobStructuredData, JobEducationRequirements
from app.utils.date_utils import calculate_total_experience_years, merge_overlapping_intervals
from datetime import date

def test_overlapping_dates_merging():
    # Jan 2021 to Dec 2021 AND Jun 2021 to May 2022 -> should merge to Jan 2021 to May 2022 (~1.4 years, NOT 2.0 years)
    intervals = [
        ("01/2021", "12/2021"),
        ("06/2021", "05/2022")
    ]
    years, unverified = calculate_total_experience_years(intervals)
    assert not unverified
    assert 1.3 <= years <= 1.5  # merged non-overlapping

def test_deterministic_scoring_reproducibility():
    resume = ResumeStructuredData(
        candidate=CandidateInfo(name="Test Candidate", headline="Python Developer"),
        skills=CategorizedSkills(programming_languages=["Python", "SQL"], frameworks=["FastAPI"]),
        all_skills_flat=["Python", "SQL", "FastAPI"],
        education=[EducationItem(degree="B.Tech", branch="Computer Science")],
        projects=[ProjectItem(title="REST API", technologies=["Python", "FastAPI"], outcomes="Deployed")]
    )
    job = JobStructuredData(
        title="Python Backend Developer",
        required_skills=["Python", "FastAPI", "SQL"],
        preferred_skills=["Docker"],
        experience_required=0.0
    )

    score1, breakdown1, mandatory1, _ = ats_engine.evaluate(resume, job)
    score2, breakdown2, mandatory2, _ = ats_engine.evaluate(resume, job)

    assert score1 == score2
    assert breakdown1.required_skills.awarded == breakdown2.required_skills.awarded
    assert score1 <= 100.0
    assert mandatory1.overall_status == mandatory2.overall_status

def test_fresher_entry_level_parity():
    # Entry level position with 0 years required
    job = JobStructuredData(
        title="Junior Developer",
        seniority="Entry Level",
        experience_required=0.0,
        required_skills=["Python"]
    )
    # Fresher with no professional experience
    fresher_resume = ResumeStructuredData(
        candidate=CandidateInfo(name="Fresher"),
        skills=CategorizedSkills(programming_languages=["Python"]),
        all_skills_flat=["Python"],
        education=[EducationItem(degree="B.Tech", branch="Computer Science")],
        experience=[] # 0 commercial experience
    )
    score, breakdown, _, _ = ats_engine.evaluate(fresher_resume, job)
    # Fresher should NOT be penalized on experience when entry level
    assert breakdown.experience.awarded >= (breakdown.experience.maximum_points * 0.90)

def test_mandatory_criteria_separation():
    resume = ResumeStructuredData(
        candidate=CandidateInfo(name="Candidate"),
        skills=CategorizedSkills(),
        all_skills_flat=["Python"],
        education=[] # Missing degree record
    )
    job = JobStructuredData(
        title="Software Engineer",
        required_skills=["Python"],
        education=JobEducationRequirements(required_degree="Bachelor in Computer Science")
    )
    score, breakdown, mandatory, _ = ats_engine.evaluate(resume, job)
    # Numerical score exists
    assert score > 0
    # Mandatory requirement is marked unverified rather than auto-rejecting or destroying score
    assert mandatory.overall_status == "unverified"
