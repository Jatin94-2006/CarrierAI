"""
Agent 3: Course Suggestion Agent
OpenRouter LLM service — generates skill-aware search strategies.
"""

import os
import json
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
# Use a fast, capable model available on OpenRouter
DEFAULT_MODEL = "mistralai/mixtral-8x7b-instruct"


def _get_api_key() -> Optional[str]:
    return os.getenv("OPENROUTER_API_KEY")


async def generate_search_strategy(
    technical_skills: list[str],
    soft_skills: list[str],
    skill_levels: dict,
    target_job_role: str = "",
) -> dict:
    """
    Ask the LLM to:
    1. Classify each skill (Technical / Soft).
    2. Generate 2-3 search keywords per skill.
    3. Identify the right difficulty for each skill.
    4. Suggest best platforms to search.

    Returns a dict with structured search plan, or raises an exception.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    all_skills = technical_skills + soft_skills
    skill_level_str = json.dumps(skill_levels, indent=2)

    system_prompt = """You are an expert educational content strategist helping users find FREE learning resources.
Your task is to analyze skill gaps and generate a structured search plan.
Always respond with valid JSON only — no markdown, no explanation outside JSON."""

    user_prompt = f"""
I have a user who wants to learn the following skills to become a {target_job_role or "software professional"}.

Technical Skills: {json.dumps(technical_skills)}
Soft Skills: {json.dumps(soft_skills)}

Skill Levels:
{skill_level_str}

For EACH skill, generate a JSON object with:
- "skill": the skill name
- "category": "Technical" or "Soft"
- "level": the user's current level (Missing → treat as Beginner)
- "search_queries": list of 2-3 specific search queries optimized for finding FREE tutorials (e.g. "Python tutorial for beginners free 2024", "free Python course freeCodeCamp")
- "preferred_platforms": list of 2-3 platforms most suitable (choose from: W3Schools, GeeksforGeeks, freeCodeCamp, Kaggle, Microsoft Learn, MDN Web Docs, SWAYAM, NPTEL, YouTube, TCS iON, Khan Academy)
- "resource_types": list of preferred types e.g. ["Tutorial", "Video", "Course"]

Return ONLY a JSON object in this exact format:
{{
  "search_plan": [
    {{
      "skill": "Python",
      "category": "Technical",
      "level": "Intermediate",
      "search_queries": ["Python intermediate tutorial free", "Python OOP free course"],
      "preferred_platforms": ["GeeksforGeeks", "YouTube", "freeCodeCamp"],
      "resource_types": ["Tutorial", "Video"]
    }}
  ]
}}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Career Guidance Agent 3",
    }

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENROUTER_BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    raw_content = data["choices"][0]["message"]["content"]

    try:
        result = json.loads(raw_content)
        return result
    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON: {raw_content[:500]}")
        raise ValueError(f"LLM returned invalid JSON: {e}")


def build_fallback_search_plan(
    technical_skills: list[str],
    soft_skills: list[str],
    skill_levels: dict,
) -> dict:
    """
    Fallback search plan when OpenRouter is not available.
    Uses rule-based keyword generation.
    """
    plan = []

    tech_platform_map = {
        "python": ["freeCodeCamp", "GeeksforGeeks", "YouTube"],
        "java": ["GeeksforGeeks", "W3Schools", "YouTube"],
        "c++": ["GeeksforGeeks", "W3Schools", "YouTube"],
        "sql": ["W3Schools", "SQLZoo", "Kaggle"],
        "data science": ["Kaggle", "freeCodeCamp", "YouTube"],
        "machine learning": ["Kaggle", "YouTube", "GeeksforGeeks"],
        "artificial intelligence": ["Kaggle", "YouTube", "GeeksforGeeks"],
        "web development": ["freeCodeCamp", "MDN Web Docs", "W3Schools"],
        "data analytics": ["Kaggle", "YouTube", "GeeksforGeeks"],
        "power bi": ["Microsoft Learn", "YouTube", "GeeksforGeeks"],
    }

    soft_platform_map = {
        "communication": ["NPTEL", "SWAYAM", "YouTube"],
        "leadership": ["TCS iON", "NPTEL", "YouTube"],
        "teamwork": ["SWAYAM", "TCS iON", "YouTube"],
        "problem solving": ["GeeksforGeeks", "YouTube", "Khan Academy"],
        "critical thinking": ["YouTube", "NPTEL", "Khan Academy"],
        "time management": ["NPTEL", "YouTube", "TCS iON"],
        "public speaking": ["YouTube", "NPTEL", "Khan Academy"],
        "interview skills": ["TCS iON", "YouTube", "GeeksforGeeks"],
    }

    for skill in technical_skills:
        level = skill_levels.get(skill, "Missing")
        effective_level = "Beginner" if level == "Missing" else level
        platforms = tech_platform_map.get(skill.lower(), ["GeeksforGeeks", "YouTube", "freeCodeCamp"])
        plan.append({
            "skill": skill,
            "category": "Technical",
            "level": effective_level,
            "search_queries": [
                f"{skill} tutorial for {effective_level.lower()}s free",
                f"learn {skill} free course",
                f"{skill} free tutorial site:youtube.com OR site:geeksforgeeks.org",
            ],
            "preferred_platforms": platforms,
            "resource_types": ["Tutorial", "Video", "Course"],
        })

    for skill in soft_skills:
        level = skill_levels.get(skill, "Missing")
        effective_level = "Beginner" if level == "Missing" else level
        platforms = soft_platform_map.get(skill.lower(), ["NPTEL", "SWAYAM", "YouTube"])
        plan.append({
            "skill": skill,
            "category": "Soft",
            "level": effective_level,
            "search_queries": [
                f"{skill} skills free course",
                f"improve {skill} free training",
                f"{skill} development tutorial free",
            ],
            "preferred_platforms": platforms,
            "resource_types": ["Course", "Video"],
        })

    return {"search_plan": plan}
