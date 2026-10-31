"""
Agent 3: Course Suggestion Agent
Core orchestration logic — the brain of the agent.
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

from models.schemas import (
    SkillGapInput,
    CourseRecommendation,
    CourseResponse,
    ResponseMetadata,
)
from services.openrouter_service import generate_search_strategy, build_fallback_search_plan
from services.tavily_service import search_all_skills as tavily_search_all
from services.youtube_service import search_all_skills_youtube
from utils.free_filter import filter_free_resources, deduplicate_by_url
from utils.sample_data import get_sample_data

logger = logging.getLogger(__name__)


def _is_demo_mode() -> bool:
    """Returns True if any required API key is missing."""
    openrouter = os.getenv("OPENROUTER_API_KEY", "").strip()
    tavily = os.getenv("TAVILY_API_KEY", "").strip()
    youtube = os.getenv("YOUTUBE_API_KEY", "").strip()
    return not (openrouter and tavily and youtube)


def _dict_to_recommendation(d: dict) -> CourseRecommendation:
    """Convert a raw resource dict to a CourseRecommendation model."""
    return CourseRecommendation(
        title=d.get("title", "Untitled"),
        platform=d.get("platform", "Unknown"),
        skill=d.get("skill", ""),
        skill_category=d.get("skill_category", "Technical"),
        difficulty=d.get("difficulty", "Beginner"),
        description=d.get("description", ""),
        url=d.get("url", "#"),
        resource_type=d.get("resource_type", "Tutorial"),
        is_free=d.get("is_free", True),
        thumbnail=d.get("thumbnail"),
        duration=d.get("duration"),
        source=d.get("source", "sample"),
    )


async def run_agent(input_data: SkillGapInput) -> CourseResponse:
    """
    Main orchestration function for Agent 3.

    Pipeline:
    1. Check if demo mode (missing API keys).
    2. If demo → return curated sample data.
    3. If live:
       a. Ask LLM to build a search strategy (with fallback).
       b. Fan out to Tavily + YouTube concurrently.
       c. Merge, filter, deduplicate.
       d. Return structured response.
    """
    demo_mode = _is_demo_mode()

    if demo_mode:
        logger.info("Running in DEMO mode — no API keys configured.")
        return _build_demo_response(input_data)

    logger.info("Running in LIVE mode — all API keys present.")
    return await _build_live_response(input_data)


def _build_demo_response(input_data: SkillGapInput) -> CourseResponse:
    """Return curated sample data filtered to match requested skills."""
    sample = get_sample_data(
        technical_skills=input_data.technical_skills,
        soft_skills=input_data.soft_skills,
    )

    tech_recs = [_dict_to_recommendation(r) for r in sample["technical"]]
    soft_recs = [_dict_to_recommendation(r) for r in sample["soft"]]

    all_skills = list(set(
        [r.skill for r in tech_recs] + [r.skill for r in soft_recs]
    ))

    return CourseResponse(
        status="success",
        message="Running in demo mode. Add API keys to .env to enable live search.",
        technical_recommendations=tech_recs,
        soft_recommendations=soft_recs,
        metadata=ResponseMetadata(
            total_resources=len(tech_recs) + len(soft_recs),
            technical_count=len(tech_recs),
            soft_count=len(soft_recs),
            skills_covered=all_skills,
            demo_mode=True,
            generated_at=datetime.utcnow().isoformat() + "Z",
        ),
    )


async def _build_live_response(input_data: SkillGapInput) -> CourseResponse:
    """Perform live API searches and return real recommendations."""

    # Step 1: Build search strategy via LLM (with fallback)
    try:
        logger.info("Generating search strategy via OpenRouter...")
        strategy = await generate_search_strategy(
            technical_skills=input_data.technical_skills,
            soft_skills=input_data.soft_skills,
            skill_levels=input_data.skill_levels,
            target_job_role=input_data.target_job_role or "",
        )
        search_plan = strategy.get("search_plan", [])
        logger.info(f"LLM generated {len(search_plan)} skill search plans.")
    except Exception as e:
        logger.warning(f"OpenRouter failed ({e}), using fallback strategy.")
        strategy = build_fallback_search_plan(
            technical_skills=input_data.technical_skills,
            soft_skills=input_data.soft_skills,
            skill_levels=input_data.skill_levels,
        )
        search_plan = strategy.get("search_plan", [])

    if not search_plan:
        return CourseResponse(
            status="error",
            message="No skills provided or search plan could not be generated.",
            technical_recommendations=[],
            soft_recommendations=[],
            metadata=ResponseMetadata(
                total_resources=0,
                technical_count=0,
                soft_count=0,
                skills_covered=[],
                demo_mode=False,
            ),
        )

    # Step 2: Fan out to Tavily + YouTube concurrently
    logger.info("Searching Tavily and YouTube concurrently...")
    try:
        tavily_results, youtube_results = await asyncio.gather(
            tavily_search_all(search_plan),
            search_all_skills_youtube(search_plan),
            return_exceptions=True,
        )
    except Exception as e:
        logger.error(f"Fatal error during API searches: {e}")
        tavily_results, youtube_results = [], []

    if isinstance(tavily_results, Exception):
        logger.warning(f"Tavily search failed: {tavily_results}")
        tavily_results = []
    if isinstance(youtube_results, Exception):
        logger.warning(f"YouTube search failed: {youtube_results}")
        youtube_results = []

    # Step 3: Merge all results
    all_resources = list(tavily_results) + list(youtube_results)
    logger.info(f"Retrieved {len(all_resources)} raw results total.")

    # Step 4: Filter to free only, then deduplicate
    free_resources = filter_free_resources(all_resources)
    unique_resources = deduplicate_by_url(free_resources)
    logger.info(f"{len(unique_resources)} unique free resources after filtering.")

    # Step 5: Split into Technical and Soft
    tech_recs = []
    soft_recs = []

    for r in unique_resources:
        category = r.get("skill_category", "Technical")
        rec = _dict_to_recommendation(r)
        if category == "Soft":
            soft_recs.append(rec)
        else:
            tech_recs.append(rec)

    # If live search returned nothing useful, fall back to sample data
    if not tech_recs and not soft_recs:
        logger.warning("Live search returned no results, falling back to sample data.")
        return _build_demo_response(input_data)

    all_skills = list(set([r.skill for r in tech_recs + soft_recs]))

    return CourseResponse(
        status="success",
        technical_recommendations=tech_recs,
        soft_recommendations=soft_recs,
        metadata=ResponseMetadata(
            total_resources=len(tech_recs) + len(soft_recs),
            technical_count=len(tech_recs),
            soft_count=len(soft_recs),
            skills_covered=all_skills,
            demo_mode=False,
            generated_at=datetime.utcnow().isoformat() + "Z",
        ),
    )
