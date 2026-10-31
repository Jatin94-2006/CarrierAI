import pytest
from app.personas.generator import synthetic_generator
from app.personas.validator import validate_persona_uniqueness_and_schema
from app.schemas.job import JobStructuredData

def test_generate_exactly_100_personas_across_7_bands():
    from unittest.mock import patch
    job = JobStructuredData(
        title="Python Backend Developer",
        required_skills=["Python", "FastAPI", "SQL"],
        preferred_skills=["Docker", "AWS", "Redis"]
    )
    with patch("app.personas.generator.groq_client.is_available", return_value=False):
        pool = synthetic_generator.generate_and_score_pool(job, session_id="test_session_100")
    
    # Must be exactly 100 profiles
    assert len(pool) == 100
    
    # Check exact band counts
    band_counts = {}
    for p in pool:
        band_counts[p.competency_band] = band_counts.get(p.competency_band, 0) + 1
        
    assert band_counts["very_high"] == 10
    assert band_counts["high"] == 20
    assert band_counts["upper_middle"] == 20
    assert band_counts["middle"] == 20
    assert band_counts["lower_middle"] == 15
    assert band_counts["low"] == 10
    assert band_counts["very_low"] == 5

    # Check scores were computed
    for p in pool:
        assert 0.0 <= p.ats_score <= 100.0
        assert p.id is not None
        assert p.profile.candidate.name is not None

    # Uniqueness validation
    valid, msg = validate_persona_uniqueness_and_schema([p.profile for p in pool])
    assert valid
