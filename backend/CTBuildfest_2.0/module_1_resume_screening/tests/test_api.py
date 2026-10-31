import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_full_pipeline_via_analyze_json():
    payload = {
        "user_id": "test_user_001",
        "generate_synthetic_benchmark": True,
        "resume_data": {
            "candidate": {
                "name": "Alex Johnson",
                "headline": "Junior Python Developer",
                "summary": "Enthusiastic engineer with FastAPI experience."
            },
            "education": [
                {
                    "degree": "B.Tech",
                    "branch": "Computer Science",
                    "institution": "Institute of Technology",
                    "graduation_year": 2024
                }
            ],
            "skills": {
                "programming_languages": ["Python", "SQL"],
                "frameworks": ["FastAPI"],
                "databases": ["PostgreSQL"]
            },
            "all_skills_flat": ["Python", "FastAPI", "SQL", "PostgreSQL"],
            "projects": [
                {
                    "title": "ATS Evaluator",
                    "description": "Calculates ATS match score",
                    "technologies": ["Python", "FastAPI"],
                    "features": ["Endpoint scoring"],
                    "outcomes": "Demonstrated 100% test passing"
                }
            ]
        },
        "job_data": {
            "title": "Python Developer",
            "required_skills": ["Python", "FastAPI", "SQL"],
            "preferred_skills": ["Docker", "PostgreSQL"],
            "experience_required": 0.0,
            "education": {
                "required_degree": "B.Tech in Computer Science"
            }
        }
    }

    # 1. Trigger Screening Analysis (mocking Groq to preserve tokens in unit tests as per Section 17)
    from unittest.mock import patch
    with patch("app.personas.generator.groq_client.is_available", return_value=False):
        response = client.post("/api/v1/screening/analyze-json", json=payload)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "completed"
    
    session_id = res_json["session_id"]
    data = res_json["data"]
    
    # Check score and 7-component breakdown
    assert "overall_ats_score" in data
    assert 0.0 <= data["overall_ats_score"] <= 100.0
    assert "score_breakdown" in data
    assert "ranking" in data
    assert data["ranking"]["total_candidates_compared"] == 101 # 1 real + 100 synthetic
    assert 0.0 <= data["ranking"]["percentile"] <= 100.0

    # 2. Test Get Score
    score_res = client.get(f"/api/v1/screening/{session_id}/score")
    assert score_res.status_code == 200
    assert "score_breakdown" in score_res.json()["data"]

    # 3. Test Get Report
    report_res = client.get(f"/api/v1/screening/{session_id}/report")
    assert report_res.status_code == 200
    assert "skills_assessment" in report_res.json()["data"]

    # 4. Test Get Ranking
    rank_res = client.get(f"/api/v1/screening/{session_id}/ranking")
    assert rank_res.status_code == 200
    assert rank_res.json()["data"]["rank"] >= 1

    # 5. Test Get 100 Synthetic Candidates
    syn_res = client.get(f"/api/v1/screening/{session_id}/synthetic-candidates")
    assert syn_res.status_code == 200
    assert syn_res.json()["data"]["total_synthetic_candidates"] == 100

    # 6. Test Module 2 Inter-Module Integration (Skill Gap Input)
    m2_res = client.get(f"/api/v1/screening/{session_id}/skill-gap-input")
    assert m2_res.status_code == 200
    assert m2_res.json()["module"] == "skill_gap_analysis"
    assert "required_skills" in m2_res.json()["data"]

    # 7. Test Module 3 Inter-Module Integration (Course Recommendations)
    m3_res = client.get(f"/api/v1/screening/{session_id}/course-input")
    assert m3_res.status_code == 200
    assert m3_res.json()["module"] == "course_recommendations"

    # 8. Test Module 4 Inter-Module Integration (Mock Interview)
    m4_res = client.get(f"/api/v1/screening/{session_id}/interview-input")
    assert m4_res.status_code == 200
    assert m4_res.json()["module"] == "mock_interview"

    # 9. Test Module 5 Inter-Module Integration (30-Day Plan)
    m5_res = client.get(f"/api/v1/screening/{session_id}/improvement-plan-input")
    assert m5_res.status_code == 200
    assert m5_res.json()["module"] == "improvement_plan"
    assert "suggested_30_day_milestones" in m5_res.json()["data"]

def test_screening_with_normal_text_job_description():
    payload = {
        "resume_data": {
            "candidate": {"name": "Test Candidate", "headline": "Python Dev"},
            "education": [{"degree": "B.Tech Computer Science", "graduation_year": 2024}],
            "skills": {"programming_languages": ["Python"], "frameworks": ["FastAPI"]},
            "all_skills_flat": ["Python", "FastAPI"],
            "projects": [{"title": "API Backend", "technologies": ["Python", "FastAPI"]}],
            "experience": [],
            "internships": [],
            "certifications": [],
            "achievements": []
        },
        "job_text": "We need a Junior Python Developer. Must know Python and FastAPI. Docker is preferred. 0 years experience required.",
        "generate_synthetic_benchmark": False
    }

    response = client.post("/api/v1/screening/analyze-json", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "completed"
    assert "overall_ats_score" in res_data["data"]
    assert res_data["data"]["job_summary"]["title"] is not None
    assert any(m["skill"].lower() == "python" for m in res_data["data"]["skills_assessment"]["matched"])
