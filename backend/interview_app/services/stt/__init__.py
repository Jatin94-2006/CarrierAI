from interview_app.config import settings
from interview_app.services.stt.base import STTProvider
from interview_app.services.stt.groq_whisper_impl import GroqWhisperProvider
from interview_app.services.stt.faster_whisper_impl import FasterWhisperProvider

def get_stt_provider() -> STTProvider:
    provider_name = (settings.STT_PROVIDER or "groq").lower()
    if provider_name == "faster_whisper":
        return FasterWhisperProvider()
    return GroqWhisperProvider()
