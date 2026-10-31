"""
Agent 3: Course Suggestion Agent
YouTube Data API v3 service — finds free educational videos and playlists.
"""

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# Channels known for high-quality FREE educational content
EDUCATIONAL_CHANNEL_IDS = [
    "UC8butISFwT-Wl7EV0hUK0BQ",  # freeCodeCamp
    "UCVTlvUkGslCV_h-nSAId8Sw",  # Programming with Mosh
    "UCW5YeuERMmlnqo4oq8vwUpg",  # Tech With Tim
    "UCJZv4d5rbIKd4QHMPkcABCw",  # Bro Code
    "UCWX3yGbODI3HCDwFQQiuB9A",  # Alex The Analyst (Data)
    "UCLLw7jmFsvfIVaUFsLs8mlQ",  # Luke Barousse (Data)
]


def _get_api_key() -> Optional[str]:
    return os.getenv("YOUTUBE_API_KEY")


async def search_youtube(
    skill: str,
    query: str,
    category: str,
    difficulty: str,
    max_results: int = 4,
) -> list[dict]:
    """
    Search YouTube for free educational videos/playlists for a given skill.
    Returns resource dicts.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not set")

    params = {
        "key": api_key,
        "q": query,
        "part": "snippet",
        "type": "video",
        "maxResults": max_results,
        "videoEmbeddable": "true",
        "relevanceLanguage": "en",
        "safeSearch": "strict",
        "order": "relevance",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

    items = data.get("items", [])
    resources = []

    for item in items:
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue

        title = snippet.get("title", "Untitled")
        channel = snippet.get("channelTitle", "Unknown Channel")
        description = snippet.get("description", "")[:300]
        thumbnail = (
            snippet.get("thumbnails", {}).get("medium", {}).get("url")
            or snippet.get("thumbnails", {}).get("default", {}).get("url")
        )

        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Skip low-quality or clearly unrelated results
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["reaction", "vlog", "unboxing", "review"]):
            continue

        resources.append({
            "title": title,
            "platform": f"YouTube – {channel}",
            "skill": skill,
            "skill_category": category,
            "difficulty": difficulty,
            "description": description or f"Free YouTube tutorial on {skill} by {channel}.",
            "url": video_url,
            "resource_type": "Video",
            "is_free": True,
            "thumbnail": thumbnail,
            "duration": None,
            "source": "youtube",
        })

    return resources


async def search_youtube_playlists(
    skill: str,
    query: str,
    category: str,
    difficulty: str,
    max_results: int = 2,
) -> list[dict]:
    """Search for educational YouTube playlists."""
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY not set")

    params = {
        "key": api_key,
        "q": query + " full course playlist",
        "part": "snippet",
        "type": "playlist",
        "maxResults": max_results,
        "relevanceLanguage": "en",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(YOUTUBE_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

    items = data.get("items", [])
    resources = []

    for item in items:
        snippet = item.get("snippet", {})
        playlist_id = item.get("id", {}).get("playlistId")
        if not playlist_id:
            continue

        title = snippet.get("title", "Untitled Playlist")
        channel = snippet.get("channelTitle", "Unknown Channel")
        description = snippet.get("description", "")[:300]
        thumbnail = (
            snippet.get("thumbnails", {}).get("medium", {}).get("url")
            or snippet.get("thumbnails", {}).get("default", {}).get("url")
        )

        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

        resources.append({
            "title": title,
            "platform": f"YouTube – {channel}",
            "skill": skill,
            "skill_category": category,
            "difficulty": difficulty,
            "description": description or f"Free YouTube playlist on {skill} by {channel}.",
            "url": playlist_url,
            "resource_type": "Playlist",
            "is_free": True,
            "thumbnail": thumbnail,
            "duration": None,
            "source": "youtube",
        })

    return resources


async def search_all_skills_youtube(search_plan: list[dict]) -> list[dict]:
    """
    Run YouTube searches for all skills in the plan.
    Returns a combined list of resource dicts.
    """
    import asyncio

    all_resources = []
    tasks = []

    for item in search_plan:
        skill = item["skill"]
        category = item["category"]
        difficulty = item["level"]
        queries = item.get("search_queries", [f"{skill} tutorial free"])

        # One video search + one playlist search per skill
        tasks.append(search_youtube(skill, queries[0] + " free tutorial", category, difficulty))
        tasks.append(search_youtube_playlists(skill, queries[0], category, difficulty))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"YouTube search error: {result}")
        else:
            all_resources.extend(result)

    return all_resources
