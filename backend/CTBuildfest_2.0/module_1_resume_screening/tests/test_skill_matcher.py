import pytest
from app.matching.skill_matcher import (
    match_skill_against_candidate_skills,
    evaluate_skills_matching,
    normalize_skill,
)

def test_exact_skill_match():
    candidate_skills = ["Python", "FastAPI", "SQL", "Docker"]
    result = match_skill_against_candidate_skills("python", candidate_skills, category="required")
    assert result.status == "exact_match"
    assert result.credit == 1.0
    assert result.matched_with == "Python"

def test_alias_match():
    candidate_skills = ["Postgres", "JS", "K8s"]
    res1 = match_skill_against_candidate_skills("PostgreSQL", candidate_skills, category="required")
    assert res1.status == "verified_equivalent"
    assert res1.credit == 0.85
    assert res1.matched_with == "Postgres"

    res2 = match_skill_against_candidate_skills("Kubernetes", candidate_skills, category="required")
    assert res2.status == "verified_equivalent"
    assert res2.credit == 0.85

def test_related_skill_not_equivalent():
    # Flask is related to FastAPI, but is NOT equivalent
    candidate_skills = ["Flask", "Django"]
    result = match_skill_against_candidate_skills("FastAPI", candidate_skills, category="required")
    assert result.status == "related"
    assert result.credit == 0.40
    assert result.credit < 0.85

def test_missing_skill():
    candidate_skills = ["HTML", "CSS"]
    result = match_skill_against_candidate_skills("Kubernetes", candidate_skills, category="required")
    assert result.status == "missing"
    assert result.credit == 0.0

def test_negative_discrimination_java_vs_javascript():
    # Java should never accidentally match JavaScript
    candidate_skills = ["Java"]
    result = match_skill_against_candidate_skills("JavaScript", candidate_skills, category="required")
    assert result.status != "exact_match"
    assert result.status != "verified_equivalent"
    assert result.credit == 0.0

def test_evaluate_skills_matching_summary():
    req = ["Python", "SQL", "FastAPI"]
    pref = ["Docker", "AWS"]
    cand = ["Python", "PostgreSQL", "Flask", "Docker"]

    req_matches, pref_matches, req_ratio, pref_ratio = evaluate_skills_matching(req, pref, cand)
    assert len(req_matches) == 3
    assert len(pref_matches) == 2
    # Python (1.0), SQL/Postgres (0.85 equivalent), FastAPI/Flask (0.40 related)
    assert req_ratio > 0.70
    assert pref_ratio > 0.40
