from app.ai.groq_client import groq_client, GroqClient
from app.ai.prompts import (
    RESUME_EXTRACTION_SYSTEM_PROMPT,
    JOB_EXTRACTION_SYSTEM_PROMPT,
    SYNTHETIC_CANDIDATE_BATCH_PROMPT,
)

__all__ = [
    "groq_client",
    "GroqClient",
    "RESUME_EXTRACTION_SYSTEM_PROMPT",
    "JOB_EXTRACTION_SYSTEM_PROMPT",
    "SYNTHETIC_CANDIDATE_BATCH_PROMPT",
]
