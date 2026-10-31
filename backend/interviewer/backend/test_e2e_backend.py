import os
import sys
import asyncio
import io
from pathlib import Path
import httpx

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from interview_app.main import interview_app
from interview_app.services.tts.manager import get_audio_file_path

async def run_backend_tests():
    print("=" * 60)
    print("STARTING E2E BACKEND INTEGRATION TESTS")
    print("=" * 60)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Health check
        print("\n[1] Testing GET /health...")
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        print(f"    Health check PASS: {data}")

        # 2. Load Sample Data
        sample_resume_path = Path(__file__).parent / "sample_data" / "sample_resume.json"
        sample_jd_path = Path(__file__).parent / "sample_data" / "sample_jd.json"

        with open(sample_resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()
        with open(sample_jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()

        # 3. Create Interview (POST /interviews)
        print("\n[2] Testing POST /interviews (creating interview session)...")
        print("    Verifying interview creation without pre-generation wait...")
        create_res = await client.post(
            "/interviews",
            data={
                "resume_text": resume_text,
                "jd_text": jd_text
            }
        )
        assert create_res.status_code == 201, f"Create interview failed: {create_res.status_code} {create_res.text}"
        interview_data = create_res.json()
        interview_id = interview_data["interview_id"]
        questions = interview_data["questions"]
        print(f"    Interview created successfully! ID: {interview_id}")
        print(f"    Total questions: {len(questions)}")
        print(f"    Role: {interview_data['role']}, Candidate: {interview_data['candidate_name']}")
        assert 5 <= len(questions) <= 8, f"Expected 5 to 8 questions, got {len(questions)}"

        # 4. Verify Runtime Audio Generation (No audio upfront)
        print("\n[3] Verifying Runtime (On-Demand) Audio Generation...")
        q1_audio_path = get_audio_file_path(interview_id, 1)
        q2_audio_path = get_audio_file_path(interview_id, 2)

        q1_exists_before = q1_audio_path.exists() and q1_audio_path.stat().st_size > 0
        print(f"    [PASS] Question 1 audio exists before runtime request? {q1_exists_before} (Expected: False in runtime mode)")
        assert not q1_exists_before, "FAIL: Audio should not be pre-generated at interview creation time in runtime mode!"

        # 5. Fetch Question 1 audio stream (GET /interviews/{id}/questions/1/audio)
        print("\n[4] Testing GET /interviews/{interview_id}/questions/1/audio (On-demand synthesis at runtime)...")
        audio_res = await client.get(f"/interviews/{interview_id}/questions/1/audio")
        assert audio_res.status_code == 200, f"Audio stream failed: {audio_res.status_code}"
        assert audio_res.headers.get("content-type") == "audio/mpeg"
        assert len(audio_res.content) > 0
        assert q1_audio_path.exists() and q1_audio_path.stat().st_size > 0, "Question 1 audio should exist after on-demand synthesis"
        print(f"    [PASS] Runtime synthesized & streamed Q1 audio: {len(audio_res.content)} bytes")

        # 6. Test runtime remaining audio endpoint and Question 2 on-demand audio
        print("\n[5] Testing POST /interviews/{interview_id}/generate-remaining-audio & Question 2 audio...")
        trigger_res = await client.post(f"/interviews/{interview_id}/generate-remaining-audio")
        assert trigger_res.status_code == 200, f"Trigger failed: {trigger_res.text}"
        print(f"    Runtime mode response: {trigger_res.json()}")

        audio2_res = await client.get(f"/interviews/{interview_id}/questions/2/audio")
        assert audio2_res.status_code == 200
        assert q2_audio_path.exists() and q2_audio_path.stat().st_size > 0
        print(f"    [PASS] Runtime synthesized & streamed Q2 audio: {len(audio2_res.content)} bytes")

        # 7. Submit answer for Question 1 (POST /interviews/{id}/answers/1)
        print("\n[6] Testing POST /interviews/{interview_id}/answers/1 (submitting recorded answer)...")
        # Test sample audio file for real transcription verification
        sample_audio_path = Path(__file__).parent / "cache" / "audio" / "test_sample.mp3"
        if sample_audio_path.exists():
            with open(sample_audio_path, "rb") as f:
                audio_bytes = f.read()
            files = {
                "audio": ("answer_1.mp3", io.BytesIO(audio_bytes), "audio/mpeg")
            }
        else:
            files = {
                "audio": ("answer_1.webm", io.BytesIO(b"dummy_short_audio"), "audio/webm")
            }
        data = {
            "duration_sec": 45,
            "live_transcript": "Welcome to your interview. Let's begin."
        }
        answer_res = await client.post(
            f"/interviews/{interview_id}/answers/1",
            files=files,
            data=data
        )
        assert answer_res.status_code == 200, f"Submit answer failed: {answer_res.status_code} {answer_res.text}"
        ans_json = answer_res.json()
        print(f"    [PASS] Answer submitted: transcript='{ans_json.get('transcript')}'")
        assert len(ans_json.get("transcript", "")) > 0, "Transcript should not be empty"
        print(f"           Behavioral analysis: {ans_json.get('behavioral_analysis')}")

        # 8. Update answer transcript (PUT /interviews/{id}/answers/1)
        print("\n[7] Testing PUT /interviews/{interview_id}/answers/1 (manual edit review)...")
        put_res = await client.put(
            f"/interviews/{interview_id}/answers/1",
            json={"transcript": "Hello, I am Kriti Mahajan and I specialize in distributed AI systems."}
        )
        assert put_res.status_code == 200
        print(f"    [PASS] Transcript updated: {put_res.json()}")

        # 9. Skip a question (POST /interviews/{id}/skip/2)
        print("\n[8] Testing POST /interviews/{interview_id}/skip/2...")
        skip_res = await client.post(f"/interviews/{interview_id}/skip/2")
        assert skip_res.status_code == 200
        print(f"    [PASS] Question 2 skipped: {skip_res.json()}")

        # 10. Get full session state (GET /interviews/{id})
        print("\n[9] Testing GET /interviews/{interview_id}...")
        sess_res = await client.get(f"/interviews/{interview_id}")
        assert sess_res.status_code == 200
        sess_json = sess_res.json()
        print(f"    [PASS] Session state retrieved: answered_count={sess_json.get('answered_count')}, skipped_count={sess_json.get('skipped_count')}")

        # 11. Finalize interview (POST /interviews/{id}/finish)
        print("\n[10] Testing POST /interviews/{interview_id}/finish...")
        finish_res = await client.post(f"/interviews/{interview_id}/finish")
        assert finish_res.status_code == 200
        final_json = finish_res.json()
        print(f"    [PASS] Final output generated: total={final_json.get('total_questions')}, answered={final_json.get('answered_count')}, skipped={final_json.get('skipped_count')}")

        print("\n" + "=" * 60)
        print("ALL 10 BACKEND INTEGRATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_backend_tests())

