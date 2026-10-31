import os
import uuid
import tempfile
import logging
import asyncio
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse

from interview_app.models.schemas import (
    CreateInterviewResponse,
    AnswerSubmissionResponse,
    UpdateAnswerRequest,
    FinalInterviewOutput,
    InterviewItem,
    BehavioralAnalysis,
    Question
)
from interview_app.services.loaders import load_resume, load_jd, extract_metadata
from interview_app.services.question_generator import generate_interview_questions
from interview_app.services.tts.manager import (
    pregenerate_remaining_questions_audio,
    synthesize_single_question,
    get_tts_provider,
    get_audio_file_path
)
from interview_app.services.stt import get_stt_provider
from interview_app.services.behavior_analyzer import analyze_applicant_behavior
from interview_app.supabase_client import InterviewRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])

@router.post("", response_model=CreateInterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    background_tasks: BackgroundTasks,
    resume_file: Optional[UploadFile] = File(None),
    jd_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    jd_text: Optional[str] = Form(None)
):
    """
    Initializes an interview session.
    Loads and sanitizes resume and JD, generates 15-18 questions in 1 call,
    triggers parallel audio pre-generation, and persists session in Supabase.
    """
    # 1. Parse Resume
    try:
        if resume_file:
            raw_resume = await resume_file.read()
            resume_data = load_resume(raw_resume)
        elif resume_text:
            resume_data = load_resume(resume_text)
        else:
            raise HTTPException(status_code=400, detail="Missing resume file or resume text.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {e}")

    # 2. Parse JD
    try:
        if jd_file:
            raw_jd = await jd_file.read()
            jd_data = load_jd(raw_jd)
        elif jd_text:
            jd_data = load_jd(jd_text)
        else:
            raise HTTPException(status_code=400, detail="Missing JD file or JD text.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse JD: {e}")

    # 3. Extract Metadata
    first_name, full_name, role_title = extract_metadata(resume_data, jd_data)

    # 4. Generate Question Set (Single LLM call + retry validation)
    question_set = await generate_interview_questions(resume_data, jd_data)
    interview_id = str(uuid.uuid4())

    # 5. Initialize Interview Items
    items = []
    for q in question_set.questions:
        items.append({
            "q_id": q.q_id,
            "phase": q.phase,
            "type": q.type,
            "source": q.source,
            "skill_tested": q.skill_tested,
            "difficulty": q.difficulty,
            "question": q.question,
            "time_limit_sec": q.time_limit_sec,
            "status": "pending",
            "answer": None,
            "duration_sec": 0,
            "behavioral_analysis": None
        })

    # 6. Save initial session to Supabase (Audio generated on-demand at runtime)
    db_record = {
        "id": interview_id,
        "role": question_set.role,
        "candidate_name": full_name,
        "status": "in_progress",
        "total_questions": len(question_set.questions),
        "answered_count": 0,
        "skipped_count": 0,
        "questions": [q.model_dump() for q in question_set.questions],
        "items": items
    }

    await InterviewRepository.create_interview(db_record)

    return CreateInterviewResponse(
        interview_id=interview_id,
        role=question_set.role,
        candidate_name=full_name,
        total_questions=len(question_set.questions),
        questions=question_set.questions
    )

@router.post("/{interview_id}/generate-remaining-audio")
async def trigger_remaining_audio(interview_id: str):
    """
    Endpoint for runtime TTS mode. Audio is generated on-demand per question.
    """
    interview = await InterviewRepository.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")
    return {"status": "runtime_mode", "message": "Audio is generated at runtime on demand."}

@router.get("/{interview_id}")
async def get_interview_session(interview_id: str):
    """Retrieves full interview session state."""
    interview = await InterviewRepository.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return interview

@router.get("/{interview_id}/questions/{q_id}/audio")
async def get_question_audio(interview_id: str, q_id: int):
    """Streams runtime on-demand TTS audio for a specific question."""
    interview = await InterviewRepository.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    audio_path = get_audio_file_path(interview_id, q_id)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        # Runtime on-demand synthesis
        questions = interview.get("questions", [])
        target_q = next((q for q in questions if (q.get("q_id") if isinstance(q, dict) else q.q_id) == q_id), None)
        if not target_q:
            raise HTTPException(status_code=404, detail=f"Question {q_id} not found.")
        
        q_text = target_q.get("question") if isinstance(target_q, dict) else target_q.question
        provider = get_tts_provider()
        await provider.synthesize(q_text, str(audio_path))

    return FileResponse(
        str(audio_path),
        media_type="audio/mpeg",
        filename=f"question_{q_id}.mp3"
    )

@router.post("/{interview_id}/answers/{q_id}", response_model=AnswerSubmissionResponse)
async def submit_answer(
    interview_id: str,
    q_id: int,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    duration_sec: int = Form(default=0),
    live_transcript: Optional[str] = Form(default=None),
    snapshots: List[UploadFile] = File(default=[])
):
    """
    Accepts recorded voice answer, transcribes via STT with live real-time transcript fallback,
    analyzes behavior from keyframe snapshots, deletes temporary audio file, and updates state.
    """
    interview = await InterviewRepository.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    # 1. Save audio blob to temporary file
    suffix = Path(audio.filename or "audio.webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_audio:
        content = await audio.read()
        tmp_audio.write(content)
        tmp_audio_path = tmp_audio.name

    try:
        # 2. Context prompt with skills for Whisper
        questions = interview.get("questions", [])
        curr_q = next((q for q in questions if (q.get("q_id") if isinstance(q, dict) else q.q_id) == q_id), None)
        context_prompt = (curr_q.get("skill_tested", "") if isinstance(curr_q, dict) else curr_q.skill_tested) if curr_q else ""

        # 3. Transcribe via STT Provider
        stt = get_stt_provider()
        transcript = await stt.transcribe(tmp_audio_path, context_prompt=context_prompt)
        
        # If cloud STT returned empty or fallback, use live transcript captured from candidate
        if not transcript or not transcript.strip() or "Candidate provided spoken answer" in transcript:
            if live_transcript and live_transcript.strip():
                logger.info(f"Using live client transcript for question {q_id}: {live_transcript[:80]}...")
                transcript = live_transcript.strip()
            else:
                transcript = "Candidate provided spoken answer."
    finally:
        # 4. Immediately delete recorded audio after transcription to preserve user privacy
        try:
            if os.path.exists(tmp_audio_path):
                os.remove(tmp_audio_path)
        except Exception as e:
            logger.warning(f"Failed to remove temp audio {tmp_audio_path}: {e}")

    # 5. Read visual keyframes for behavioral analysis
    snapshot_bytes = []
    for snap in snapshots:
        try:
            snapshot_bytes.append(await snap.read())
        except Exception:
            pass

    # 6. Evaluate candidate expressions and composure
    behavior = await analyze_applicant_behavior(snapshot_bytes, duration_sec, transcript)

    # 7. Update question item in Supabase
    items = interview.get("items", [])
    updated = False
    for item in items:
        if item.get("q_id") == q_id:
            item["status"] = "answered"
            item["answer"] = transcript
            item["duration_sec"] = duration_sec
            item["behavioral_analysis"] = behavior.model_dump()
            updated = True
            break

    if updated:
        answered_count = sum(1 for item in items if item.get("status") == "answered")
        await InterviewRepository.update_interview(interview_id, {
            "items": items,
            "answered_count": answered_count
        })

    return AnswerSubmissionResponse(
        q_id=q_id,
        status="answered",
        transcript=transcript,
        duration_sec=duration_sec,
        behavioral_analysis=behavior
    )

@router.put("/{interview_id}/answers/{q_id}")
async def update_transcript(interview_id: str, q_id: int, payload: UpdateAnswerRequest):
    """Updates candidate transcript after manual edits in the UI."""
    interview = await InterviewRepository.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    items = interview.get("items", [])
    found = False
    for item in items:
        if item.get("q_id") == q_id:
            item["answer"] = payload.transcript.strip()
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail=f"Question {q_id} not found in interview items.")

    await InterviewRepository.update_interview(interview_id, {"items": items})
    return {"status": "updated", "q_id": q_id, "answer": payload.transcript.strip()}

@router.post("/{interview_id}/skip/{q_id}")
async def skip_question(interview_id: str, q_id: int):
    """Marks question as skipped."""
    interview = await InterviewRepository.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    items = interview.get("items", [])
    for item in items:
        if item.get("q_id") == q_id:
            item["status"] = "skipped"
            item["answer"] = None
            item["duration_sec"] = 0
            break

    skipped_count = sum(1 for item in items if item.get("status") == "skipped")
    await InterviewRepository.update_interview(interview_id, {
        "items": items,
        "skipped_count": skipped_count
    })

    return {"status": "skipped", "q_id": q_id}

@router.post("/{interview_id}/finish", response_model=FinalInterviewOutput)
async def finish_interview(interview_id: str):
    """Builds and returns the final JSON output, marking session completed."""
    interview = await InterviewRepository.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    items_data = interview.get("items", [])
    total_q = interview.get("total_questions", len(items_data))
    answered_c = sum(1 for item in items_data if item.get("status") == "answered")
    skipped_c = sum(1 for item in items_data if item.get("status") == "skipped")

    output = FinalInterviewOutput(
        interview_id=interview_id,
        role=interview.get("role", "AI Engineer"),
        candidate_name=interview.get("candidate_name", "Candidate"),
        total_questions=total_q,
        answered_count=answered_c,
        skipped_count=skipped_c,
        items=[InterviewItem.model_validate(item) for item in items_data]
    )

    await InterviewRepository.update_interview(interview_id, {
        "status": "completed",
        "raw_output": output.model_dump()
    })

    # Execute Agent 2 Gap Analysis on the interview and save shared artifact
    try:
        import sys
        import json
        ct2_root = Path(__file__).resolve().parent.parent.parent.parent
        agent2_dir = ct2_root / "agent2"
        if str(agent2_dir) not in sys.path:
            sys.path.insert(0, str(agent2_dir))
        
        from agents.gap_analysis_agent import GapAnalysisAgent
        agent2 = GapAnalysisAgent()
        gap_res = agent2.analyze_interview(output.model_dump())
        shared_out = ct2_root / "shared_output"
        shared_out.mkdir(exist_ok=True)
        with open(shared_out / "interview_gap.json", "w", encoding="utf-8") as f:
            json.dump(gap_res, f, indent=2)
        logger.info(f"Agent 2 Gap Analysis saved for interview {interview_id}")
    except Exception as e:
        logger.warning(f"Could not run Agent 2 Gap Analysis in finish_interview: {e}")

    return output
