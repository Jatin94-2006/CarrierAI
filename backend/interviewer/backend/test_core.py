import os
import sys
import asyncio
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from interview_app.services.loaders import load_resume, load_jd, extract_metadata
from interview_app.services.question_generator import generate_interview_questions
from interview_app.services.tts.manager import get_tts_provider
from interview_app.models.schemas import QuestionSet

async def main():
    print("=== TEST 1: Loaders & Privacy Sanitization ===")
    sample_resume_path = Path(__file__).parent / "sample_data" / "sample_resume.json"
    sample_jd_path = Path(__file__).parent / "sample_data" / "sample_jd.json"
    
    with open(sample_resume_path, "r", encoding="utf-8") as f:
        raw_resume = f.read()
    with open(sample_jd_path, "r", encoding="utf-8") as f:
        raw_jd = f.read()
        
    resume = load_resume(raw_resume)
    jd = load_jd(raw_jd)
    
    # Assert PII removal
    assert "email" not in resume.get("candidate", {}), "FAIL: Email was not stripped!"
    assert "phone" not in resume.get("candidate", {}), "FAIL: Phone was not stripped!"
    print("[PASS] PII successfully sanitized (email & phone removed).")

    # Assert handling extra trailing data (e.g. Extra data at line 61)
    extra_data_resume = raw_resume + "\n\nExtra data trailing at line 61 char 3008"
    resume_from_extra = load_resume(extra_data_resume)
    assert resume_from_extra.get("candidate", {}).get("name") == "Kriti Mahajan"
    print("[PASS] Extra trailing data gracefully handled and parsed without error.")
    
    first_name, full_name, role_title = extract_metadata(resume, jd)
    print(f"[PASS] Metadata extracted: Name='{full_name}', First='{first_name}', Role='{role_title}'")
    
    print("\n=== TEST 2: Question Generation & Acceptance Criteria ===")
    q_set: QuestionSet = await generate_interview_questions(resume, jd)
    
    total_q = len(q_set.questions)
    total_time = sum(q.time_limit_sec for q in q_set.questions)
    
    print(f"Total questions generated: {total_q}")
    print(f"Total time budget: {total_time}s ({total_time / 60:.1f} minutes)")
    
    assert 5 <= total_q <= 8, f"FAIL: Expected 5-8 questions, got {total_q}"
    assert total_time >= 300, f"FAIL: Total time must be >= 300s, got {total_time}s"
    print("[PASS] 5-8 questions generated with time budget >= 5 minutes.")
    
    # Verify phases
    phases = [q.phase for q in q_set.questions]
    print(f"Phases sequence: {phases}")
    assert phases[0] == "intro", "FAIL: First question must be intro"
    assert phases[-1] in ("farewell", "closing"), f"FAIL: Last question must be farewell or closing, got {phases[-1]}"
    assert any(q.type == "technical" for q in q_set.questions), "FAIL: Missing technical questions"
    assert any(q.type == "hr" for q in q_set.questions), "FAIL: Missing HR questions"
    print("[PASS] Combined Technical & HR structure conforms to specifications.")
    
    # Verify sources
    for q in q_set.questions:
        if q.phase == "project":
            assert "project" in q.source.lower(), f"FAIL: Project source invalid: {q.source}"
        if q.phase == "technical":
            assert any(k in q.source.lower() for k in ("skill", "technical", "project", "candidate", "jd")), f"FAIL: Technical source invalid: {q.source}"
    print("[PASS] Project and technical sources strictly verified.")

    print("\n=== TEST 3: TTS Synthesis ===")
    tts = get_tts_provider()
    test_audio_path = Path(__file__).parent / "cache" / "audio" / "test_sample.mp3"
    test_audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    res_path = await tts.synthesize("Welcome to your interview. Let's begin.", str(test_audio_path))
    assert os.path.exists(res_path), "FAIL: Audio file was not created!"
    file_size = os.path.getsize(res_path)
    print(f"[PASS] TTS Audio generated successfully at {res_path} ({file_size} bytes)")
    
    print("\n===========================================")
    print("ALL CORE ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
    print("===========================================")

if __name__ == "__main__":
    asyncio.run(main())
