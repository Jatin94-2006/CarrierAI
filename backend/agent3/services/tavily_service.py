"""
Agent 3: Course Suggestion Agent
Tavily Web Search service — searches for free learning resources.
"""

import os
import logging
import httpx
from typing import Optional

from utils.free_filter import is_likely_free, platform_from_url

logger = logging.getLogger(__name__)

TAVILY_BASE_URL = "https://api.tavily.com/search"

# Trusted domains to include in Tavily searches
INCLUDE_DOMAINS = [
    "w3schools.com",
    "geeksforgeeks.org",
    "freecodecamp.org",
    "kaggle.com",
    "learn.microsoft.com",
    "developer.mozilla.org",
    "swayam.gov.in",
    "nptel.ac.in",
    "youtube.com",
    "khanacademy.org",
    "tutorialspoint.com",
    "programiz.com",
    "cs50.harvard.edu",
    "realpython.com",
    "sqlzoo.net",
    "sqlbolt.com",
    "analyticsvidhya.com",
    "tcsion.com",
    "roadmap.sh",
    "coursera.org",
    "edx.org",
]


def _get_api_key() -> Optional[str]:
    return os.getenv("TAVILY_API_KEY")


async def search_resources_for_skill(
    skill: str,
    search_query: str,
    category: str,
    difficulty: str,
    max_results: int = 5,
) -> list[dict]:
    """
    Search Tavily for free learning resources for a given skill.
    Returns a list of resource dicts ready for CourseRecommendation conversion.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("TAVILY_API_KEY not set")

    payload = {
        "api_key": api_key,
        "query": search_query,
        "search_depth": "advanced",
        "include_domains": INCLUDE_DOMAINS,
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(TAVILY_BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()

    results = data.get("results", [])
    resources = []

    for r in results:
        url = r.get("url", "")
        title = r.get("title", "Untitled")
        description = r.get("content", "")[:400]  # trim long snippets

        if not url:
            continue

        # Only include free resources
        if not is_likely_free(url, title, description):
            continue

        platform = platform_from_url(url)
        resource_type = _infer_resource_type(url, title)

        resources.append({
            "title": title,
            "platform": platform,
            "skill": skill,
            "skill_category": category,
            "difficulty": difficulty,
            "description": description or f"Free {skill} learning resource.",
            "url": url,
            "resource_type": resource_type,
            "is_free": True,
            "thumbnail": None,
            "duration": None,
            "source": "tavily",
        })

    return resources


def _infer_resource_type(url: str, title: str) -> str:
    """Heuristic to infer the resource type from URL and title."""
    url_lower = url.lower()
    title_lower = title.lower()

    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        if "playlist" in url_lower:
            return "Playlist"
        return "Video"

    if any(kw in title_lower for kw in ["course", "certification", "program"]):
        return "Course"

    if any(kw in title_lower for kw in ["tutorial", "guide", "how to", "learn"]):
        return "Tutorial"

    if any(kw in url_lower for kw in ["docs", "documentation", "reference", "mdn"]):
        return "Documentation"

    return "Tutorial"


async def search_all_skills(search_plan: list[dict]) -> list[dict]:
    """
    Run Tavily searches for all skills in the search plan.
    Returns a combined list of resource dicts.
    """
    import asyncio

    all_resources = []
    tasks = []

    for item in search_plan:
        skill = item["skill"]
        category = item["category"]
        difficulty = item["level"]
        queries = item.get("search_queries", [])

        # Use only the first 2 queries per skill to stay within rate limits
        for query in queries[:2]:
            tasks.append(
                search_resources_for_skill(skill, query, category, difficulty)
            )

    # Run all searches concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Tavily search error: {result}")
        else:
            all_resources.extend(result)

    return all_resources
