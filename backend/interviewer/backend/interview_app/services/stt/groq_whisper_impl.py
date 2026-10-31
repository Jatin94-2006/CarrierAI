import os
import logging
from pathlib import Path
import httpx
from interview_app.config import settings
from interview_app.services.stt.base import STTProvider

logger = logging.getLogger(__name__)

class GroqWhisperProvider(STTProvider):
    """
    STT using Groq Whisper API (whisper-large-v3-turbo) or OpenAI Whisper API.
    """
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY or settings.OPENAI_API_KEY
        if settings.GROQ_API_KEY:
            self.endpoint = "https://api.groq.com/openai/v1/audio/transcriptions"
            self.model = "whisper-large-v3-turbo"
        else:
            self.endpoint = "https://api.openai.com/v1/audio/transcriptions"
            self.model = "whisper-1"

    async def transcribe(self, audio_path: str, context_prompt: str = "") -> str:
        if not self.api_key:
            logger.warning("No Groq or OpenAI API key found for STT.")
            return ""

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            if len(audio_bytes) < 100:
                logger.warning(f"Audio file is too small ({len(audio_bytes)} bytes) for transcription.")
                return ""

            ext = Path(audio_path).suffix.lower() or ".webm"
            if ext not in [".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".wav", ".webm"]:
                ext = ".webm"
            upload_filename = f"speech{ext}"

            content_type = "audio/webm"
            if ext == ".mp3":
                content_type = "audio/mpeg"
            elif ext == ".wav":
                content_type = "audio/wav"
            elif ext == ".m4a":
                content_type = "audio/mp4"

            async with httpx.AsyncClient(timeout=15.0) as client:
                files = {
                    "file": (upload_filename, audio_bytes, content_type)
                }
                data = {
                    "model": self.model,
                    "language": "en"
                }
                if context_prompt:
                    data["prompt"] = context_prompt[:200]
                    
                resp = await client.post(self.endpoint, headers=headers, files=files, data=data)
                if resp.status_code != 200:
                    logger.warning(f"Groq STT returned HTTP {resp.status_code}: {resp.text}")
                    return ""
                    
                result = resp.json()
                return result.get("text", "").strip()
        except Exception as e:
            logger.warning(f"Groq transcription error: {e}")
            return ""
