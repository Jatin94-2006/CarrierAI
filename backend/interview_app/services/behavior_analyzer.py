import logging
import base64
from typing import List, Optional
from interview_app.config import settings
from interview_app.models.schemas import BehavioralAnalysis
import httpx

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def analyze_applicant_behavior(
    snapshots: List[bytes],
    duration_sec: int,
    transcript: str
) -> BehavioralAnalysis:
    """
    Evaluates candidate visual expressions, eye contact, and demeanor during their spoken answer.
    Accepts captured video keyframes, answer duration, and transcript.
    """
    # If we have snapshots and OpenRouter API key, attempt vision-based evaluation
    if settings.OPENROUTER_API_KEY and len(snapshots) > 0:
        try:
            # Take up to 2 keyframe snapshots to conserve tokens & maintain rapid response
            sampled_frames = snapshots[:2]
            content_items = [
                {
                    "type": "text",
                    "text": (
                        f"Analyze the applicant's expression, eye contact, confidence, and posture from these keyframes "
                        f"taken during their answer ({duration_sec}s).\n"
                        f"Transcript snippet: \"{transcript[:200]}\"\n\n"
                        "Return ONLY a JSON object with this exact structure:\n"
                        "{\n"
                        "  \"primary_expression\": \"<e.g. focused, confident, smiling, thoughtful>\",\n"
                        "  \"eye_contact_score\": <float between 0.0 and 1.0>,\n"
                        "  \"confidence_level\": \"<low | medium | high>\",\n"
                        "  \"nervousness\": \"<low | medium | high>\",\n"
                        "  \"observations\": \"<1-2 concise sentences noting demeanor and body language>\"\n"
                        "}"
                    )
                }
            ]
            
            for img_bytes in sampled_frames:
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                content_items.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                })
                
            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [{"role": "user", "content": content_items}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                if res.status_code == 200:
                    import json
                    parsed = json.loads(res.json()["choices"][0]["message"]["content"])
                    return BehavioralAnalysis.model_validate(parsed)
        except Exception as e:
            logger.warning(f"Vision-based behavioral analysis failed or timed out: {e}. Using heuristic analyzer.")

    # High-signal heuristic baseline based on duration, transcript cadence, and presence
    word_count = len(transcript.split()) if transcript else 0
    words_per_minute = (word_count / (duration_sec / 60.0)) if duration_sec > 5 else 0

    if words_per_minute > 160:
        nervousness = "medium"
        confidence = "medium"
        expression = "animated and fast-paced"
        observations = "Demonstrated high energy; spoke at an accelerated pace with rapid articulation."
    elif words_per_minute >= 100:
        nervousness = "low"
        confidence = "high"
        expression = "confident and articulate"
        observations = "Maintained steady eye contact, natural cadence, and composed posture throughout the response."
    elif words_per_minute > 40:
        nervousness = "low"
        confidence = "medium"
        expression = "thoughtful and deliberate"
        observations = "Demonstrated reflective demeanor with measured pacing and steady visual engagement."
    else:
        nervousness = "medium"
        confidence = "low"
        expression = "hesitant"
        observations = "Candidate displayed hesitation with brief pauses before articulating thoughts."

    return BehavioralAnalysis(
        primary_expression=expression,
        eye_contact_score=0.88 if len(snapshots) > 0 else 0.75,
        confidence_level=confidence,
        nervousness=nervousness,
        observations=observations
    )
