import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Information
    APP_NAME: str = "CTBF-AI-05 Resume Screening Service"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase / PostgreSQL Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./screening_local.db",
        description="Supabase PostgreSQL connection string or local fallback"
    )
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""

    # Groq API Configuration (The ONLY LLM Provider)
    GROQ_API_KEY: str = Field(
        default="",
        description="Groq API Key (gsk_...)"
    )
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FALLBACK_MODEL: str = "llama-3.1-8b-instant"

    # Deterministic ATS Scoring Weights (Must sum to 1.0)
    ATS_WEIGHT_REQUIRED_SKILLS: float = 0.35
    ATS_WEIGHT_PREFERRED_SKILLS: float = 0.15
    ATS_WEIGHT_EXPERIENCE: float = 0.15
    ATS_WEIGHT_PROJECTS: float = 0.15
    ATS_WEIGHT_EDUCATION: float = 0.10
    ATS_WEIGHT_CERTIFICATIONS: float = 0.05
    ATS_WEIGHT_ROLE_RELEVANCE: float = 0.05

    # Uploads & Security
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "json"]
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")

    # Synthetic Benchmark
    SYNTHETIC_POOL_SIZE: int = 100
    SYNTHETIC_BATCH_SIZE: int = 10
    USE_GROQ_FOR_SYNTHETIC_POOL: bool = False

    # Band distribution as strictly requested by CTBF-AI-05
    SYNTHETIC_BAND_DISTRIBUTION: Dict[str, int] = {
        "very_high": 10,
        "high": 20,
        "upper_middle": 20,
        "middle": 20,
        "lower_middle": 15,
        "low": 10,
        "very_low": 5,
    }

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
