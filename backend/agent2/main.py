"""
AI Career Guidance & Job Preparation Platform
FastAPI Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Career Guidance Platform",
    description="Multi-agent pipeline: Resume Analysis → Gap Analysis → Course Suggestions → Mock Interview → Learning Plan",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "AI Career Guidance Platform",
        "version": "1.0.0",
        "modules": [
            "Module 1 — Resume Analysis",
            "Module 2 — Gap Analysis (Core)",
            "Module 3 — Course Suggestions",
            "Module 4 — Mock Interview",
            "Module 5 — Learning Planner",
        ],
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
