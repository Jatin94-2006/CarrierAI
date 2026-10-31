"""
Agent 3: Course Suggestion Agent
FastAPI application — main entry point.
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from models.schemas import SkillGapInput, CourseResponse, HealthResponse
from agents.course_agent import run_agent, _is_demo_mode
from utils.sample_data import get_sample_data, SAMPLE_TECHNICAL, SAMPLE_SOFT
from models.schemas import CourseRecommendation, ResponseMetadata
from datetime import datetime

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("agent3")


# ─── App ──────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    demo = _is_demo_mode()
    mode = "DEMO (sample data)" if demo else "LIVE (real API calls)"
    logger.info(f"Agent 3 — Course Suggestion Agent starting in {mode} mode.")
    yield


app = FastAPI(
    title="Agent 3: Course Suggestion Agent",
    description=(
        "Recommends FREE learning resources based on skill gaps identified by Agent 2. "
        "Integrates with OpenRouter (LLM), Tavily (web search), and YouTube Data API."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS — allow React/Next.js frontend to call this API ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Exception handler ────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": str(exc)},
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint. Confirms the service is running."""
    return HealthResponse(
        status="ok",
        agent="Course Suggestion Agent (Agent 3)",
        demo_mode=_is_demo_mode(),
        version="1.0.0",
    )


@app.post(
    "/api/v1/courses/recommend",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Get personalized course recommendations",
    description=(
        "Receives skill gap data from Agent 2 (Gap Analysis Agent) and returns "
        "FREE course recommendations for both technical and soft skills. "
        "Output is also consumable by Agent 5 (Learning Planner)."
    ),
)
async def recommend_courses(payload: SkillGapInput) -> CourseResponse:
    """
    Main endpoint for Agent 3.

    **Input** (from Agent 2):
    - `technical_skills`: list of missing/weak technical skills
    - `soft_skills`: list of missing/weak soft skills
    - `skill_levels`: dict mapping skill → proficiency level
    - `target_job_role`: optional target job title
    - `resume_summary`: optional context from Agent 1

    **Output** (for frontend + Agent 5):
    - `technical_recommendations`: list of free courses/tutorials for tech skills
    - `soft_recommendations`: list of free resources for soft skills
    - `metadata`: summary statistics and integration metadata
    """
    if not payload.technical_skills and not payload.soft_skills:
        raise HTTPException(
            status_code=422,
            detail="At least one technical or soft skill must be provided.",
        )

    try:
        result = await run_agent(payload)
        return result
    except Exception as e:
        logger.error(f"Agent run failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get(
    "/api/v1/courses/sample",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Get sample recommendations (for testing)",
    description="Returns a pre-built set of sample course recommendations. Useful for frontend development and integration testing without triggering live API calls.",
)
async def sample_courses() -> CourseResponse:
    """Returns full sample output — no API keys required."""
    tech = [
        CourseRecommendation(**{**r, "source": "sample"})
        for r in SAMPLE_TECHNICAL
    ]
    soft = [
        CourseRecommendation(**{**r, "source": "sample"})
        for r in SAMPLE_SOFT
    ]

    all_skills = list(set([r.skill for r in tech + soft]))

    return CourseResponse(
        status="success",
        message="Sample data — no live API calls made.",
        technical_recommendations=tech,
        soft_recommendations=soft,
        metadata=ResponseMetadata(
            total_resources=len(tech) + len(soft),
            technical_count=len(tech),
            soft_count=len(soft),
            skills_covered=all_skills,
            demo_mode=True,
            generated_at=datetime.utcnow().isoformat() + "Z",
        ),
    )


@app.get(
    "/api/v1/courses/skills",
    tags=["Courses"],
    summary="List all supported skills",
)
async def supported_skills():
    """Returns the full list of skills Agent 3 can handle."""
    return {
        "technical_skills": [
            "Python", "Java", "C++", "SQL", "Data Science",
            "Machine Learning", "Artificial Intelligence", "Web Development",
            "Data Analytics", "Power BI", "JavaScript", "React", "Node.js",
            "Data Visualization", "Statistics",
        ],
        "soft_skills": [
            "Communication", "Leadership", "Teamwork", "Problem Solving",
            "Critical Thinking", "Time Management", "Public Speaking",
            "Interview Skills", "Emotional Intelligence", "Adaptability",
        ],
    }
