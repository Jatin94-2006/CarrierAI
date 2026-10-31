import io
import pytest
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.json_parser import parse_resume_json
from app.parsers.resume_extractor import extract_structured_resume
from app.core.exceptions import FileValidationError

def test_json_resume_parsing_valid():
    sample_json = {
        "candidate": {
            "name": "Jane Doe",
            "headline": "Python Developer"
        },
        "education": [
            {"degree": "B.Tech", "branch": "Computer Science"}
        ],
        "skills": {
            "programming_languages": ["Python", "SQL"],
            "frameworks": ["FastAPI"]
        },
        "projects": [
            {"title": "ATS System", "technologies": ["Python", "FastAPI"]}
        ]
    }
    parsed = parse_resume_json(sample_json)
    assert parsed.candidate.name == "Jane Doe"
    assert "Python" in parsed.all_skills_flat
    assert len(parsed.projects) == 1

def test_json_resume_parsing_invalid():
    with pytest.raises(FileValidationError):
        parse_resume_json("not valid json string {{{")

def test_empty_text_resume_extraction():
    structured, evidence = extract_structured_resume("", source_format="pdf")
    assert structured.extraction_metadata.extraction_status == "completed"
    assert len(structured.all_skills_flat) == 0

def test_heuristic_resume_extraction_with_content():
    raw_text = """
    Jane Smith
    Email: jane.smith@example.com | Phone: (555) 123-4567
    Summary: Enthusiastic developer experienced with Python, FastAPI, and PostgreSQL.
    
    Education:
    B.Tech in Computer Science from National Institute of Technology, 2023.
    
    Projects:
    E-Commerce API: Built scalable microservice using Python and Docker. Reduced latency by 20%.
    """
    structured, evidence = extract_structured_resume(raw_text, source_format="pdf")
    assert structured.candidate.email == "jane.smith@example.com"
    assert any("Python" in s for s in structured.all_skills_flat)
    assert any("Postgresql" in s or "PostgreSQL" in s for s in structured.all_skills_flat)
    assert len(evidence) > 0
