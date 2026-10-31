import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "AI Spoken Interview Agent"
    DEBUG: bool = True
    
    # OpenRouter LLM (Using NVIDIA Nemotron Models)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    OPENROUTER_FALLBACK_MODEL: str = "nvidia/nemotron-3.5-lightning:free"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # STT Provider ("groq", "openai", "faster_whisper", "edge_or_browser")
    STT_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    WHISPER_MODEL_SIZE: str = "small"
    
    # TTS Provider ("edge_tts", "kokoro", "browser")
    TTS_PROVIDER: str = "edge_tts"
    TTS_VOICE: str = "en-US-GuyNeural"
    
    # Audio Storage Cache
    AUDIO_CACHE_DIR: str = str(Path(__file__).parent.parent.parent / "cache" / "audio")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure audio cache directory exists
os.makedirs(settings.AUDIO_CACHE_DIR, exist_ok=True)
