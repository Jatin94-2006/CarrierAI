from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.logging import logger
from app.core.exceptions import BaseScreeningException
from app.database.connection import init_db
from app.api.v1.router import api_v1_router
from app.schemas.common import APIResponseEnvelope

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    init_db()
    logger.info(f"{settings.APP_NAME} started successfully.")
    yield

def create_application() -> FastAPI:
    app = FastAPI(
        title="CTBF-AI-05: Resume Screening & ATS Matching Service",
        description=(
            "Module 1 Backend Service for CTBF-AI-05: Resume Screening, ATS Matching & Synthetic Candidate Ranking. "
            "Features multi-format extraction (PDF, DOCX, JSON), deterministic explainable ATS scoring (0-100), "
            "mandatory criteria verification, 100-synthetic candidate benchmarking across 7 competency bands, "
            "and standardized inter-module contracts for Modules 2, 3, 4, and 5."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Exception Handlers
    @app.exception_handler(BaseScreeningException)
    async def screening_exception_handler(request: Request, exc: BaseScreeningException):
        return JSONResponse(
            status_code=exc.status_code,
            content=APIResponseEnvelope(
                status="failed",
                data={"error": exc.detail}
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled server error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponseEnvelope(
                status="failed",
                data={"error": "An internal server error occurred. Please check logs."}
            ).model_dump()
        )

    # Mount Routes
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", tags=["Root"])
    def root():
        return {
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }

    @app.get("/health", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "groq_configured": bool(settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith("gsk_YOUR"))
        }

    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
