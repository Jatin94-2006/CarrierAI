import os
import asyncio
import logging
from typing import List
from pathlib import Path

from interview_app.config import settings
from interview_app.models.schemas import Question
from interview_app.services.tts.base import TTSProvider
from interview_app.services.tts.edge_tts_impl import EdgeTTSProvider
from interview_app.services.tts.kokoro_impl import KokoroTTSProvider

logger = logging.getLogger(__name__)

_generating_interview_ids = set()

def get_tts_provider() -> TTSProvider:
    provider_name = (settings.TTS_PROVIDER or "edge_tts").lower()
    if provider_name == "kokoro":
        return KokoroTTSProvider()
    return EdgeTTSProvider()

def get_audio_file_path(interview_id: str, q_id: int) -> Path:
    cache_dir = Path(settings.AUDIO_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{interview_id}_{q_id}.mp3"

async def synthesize_single_question(provider: TTSProvider, interview_id: str, question: Question) -> str:
    path_obj = get_audio_file_path(interview_id, question.q_id)
    audio_path = str(path_obj)
    
    # If valid audio is already synthesized on disk, avoid duplicate work
    if path_obj.exists() and path_obj.stat().st_size > 0:
        return audio_path

    try:
        await provider.synthesize(question.question, audio_path)
        logger.info(f"Synthesized question audio {question.q_id} for interview {interview_id}")
    except Exception as e:
        logger.error(f"Failed to synthesize question {question.q_id}: {e}")
    return audio_path

async def pregenerate_remaining_questions_audio(interview_id: str, questions: List[Question]):
    """
    Synthesizes audio for remaining questions simultaneously in parallel
    while candidate is answering the first question.
    """
    if interview_id in _generating_interview_ids:
        logger.info(f"Audio pre-generation already active for interview {interview_id}")
        return

    _generating_interview_ids.add(interview_id)
    try:
        provider = get_tts_provider()
        sem = asyncio.Semaphore(6)

        async def worker(q: Question):
            async with sem:
                return await synthesize_single_question(provider, interview_id, q)

        tasks = [worker(q) for q in questions]
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Completed simultaneous audio pre-generation for {len(questions)} remaining questions in interview {interview_id}")
    except Exception as e:
        logger.error(f"Error in simultaneous audio pre-generation: {e}")
    finally:
        _generating_interview_ids.discard(interview_id)

async def pregenerate_all_questions_audio(interview_id: str, questions: List[Question]):
    """
    Synthesizes audio for interview questions in parallel.
    """
    await pregenerate_remaining_questions_audio(interview_id, questions)
