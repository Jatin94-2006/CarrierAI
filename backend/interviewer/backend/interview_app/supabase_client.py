import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from interview_app.config import settings

logger = logging.getLogger(__name__)

# Initialize Supabase client if configured and table exists
_supabase = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY and "your-project" not in settings.SUPABASE_URL:
    try:
        import httpx
        # Fast 1.5s probe to check if remote Supabase has the 'interviews' table ready
        probe_res = httpx.get(
            f"{settings.SUPABASE_URL}/rest/v1/interviews?limit=1",
            headers={"apikey": settings.SUPABASE_KEY, "Authorization": f"Bearer {settings.SUPABASE_KEY}"},
            timeout=1.5
        )
        if probe_res.status_code == 200:
            from supabase import create_client, Client
            _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Connected successfully to Supabase.")
        else:
            logger.info(f"Supabase table 'interviews' not ready (HTTP {probe_res.status_code}). Using ultra-fast local storage.")
            _supabase = None
    except Exception as e:
        logger.info(f"Supabase probe bypassed ({e}). Using ultra-fast local storage.")
        _supabase = None
else:
    logger.info("Supabase credentials not set or placeholder. Using ultra-fast local storage.")

# In-memory and disk fallback storage
_LOCAL_STORAGE_DIR = Path(__file__).parent.parent.parent / "cache" / "db_fallback"
_LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
_in_memory_interviews: Dict[str, Dict[str, Any]] = {}

def _handle_supabase_error(e: Exception):
    global _supabase
    err_str = str(e)
    logger.warning(f"Supabase unavailable or slow ({err_str[:120]}). Switching permanently to high-speed local storage.")
    _supabase = None

class InterviewRepository:
    @staticmethod
    async def create_interview(interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates and stores a new interview record with fast 2s timeout for remote calls."""
        interview_id = interview_data["id"]
        
        if _supabase:
            try:
                def _sync_insert():
                    return _supabase.table("interviews").insert(interview_data).execute()
                res = await asyncio.wait_for(asyncio.to_thread(_sync_insert), timeout=2.0)
                if res.data:
                    return res.data[0]
            except Exception as e:
                _handle_supabase_error(e)
        
        # Local fallback
        _in_memory_interviews[interview_id] = interview_data
        file_path = _LOCAL_STORAGE_DIR / f"{interview_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(interview_data, f, indent=2)
            
        return interview_data

    @staticmethod
    async def get_interview(interview_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an interview by ID with fast 2s timeout."""
        # Fast memory check first
        if interview_id in _in_memory_interviews:
            return _in_memory_interviews[interview_id]

        if _supabase:
            try:
                def _sync_get():
                    return _supabase.table("interviews").select("*").eq("id", interview_id).execute()
                res = await asyncio.wait_for(asyncio.to_thread(_sync_get), timeout=2.0)
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                _handle_supabase_error(e)

        # Local fallback check
        file_path = _LOCAL_STORAGE_DIR / f"{interview_id}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _in_memory_interviews[interview_id] = data
                return data
                
        return None

    @staticmethod
    async def update_interview(interview_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Updates an existing interview record with fast 2s timeout."""
        if _supabase:
            try:
                def _sync_update():
                    return _supabase.table("interviews").update(updates).eq("id", interview_id).execute()
                res = await asyncio.wait_for(asyncio.to_thread(_sync_update), timeout=2.0)
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                _handle_supabase_error(e)

        # Local fallback
        current = await InterviewRepository.get_interview(interview_id)
        if not current:
            return None
            
        current.update(updates)
        _in_memory_interviews[interview_id] = current
        
        file_path = _LOCAL_STORAGE_DIR / f"{interview_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
            
        return current
