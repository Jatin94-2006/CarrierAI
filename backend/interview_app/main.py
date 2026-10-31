import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from interview_app.config import settings
from interview_app.api.routes import router as interview_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Spoken Interview Agent backend module with Google Meet experience and Supabase persistence.",
    version="1.0.0"
)

# CORS configuration for Next.js web application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(interview_router)

@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "supabase_configured": bool(settings.SUPABASE_URL and "your-project" not in settings.SUPABASE_URL),
        "tts_provider": settings.TTS_PROVIDER,
        "stt_provider": settings.STT_PROVIDER
    }
