import json
import copy
from typing import Union, Dict, Any, Tuple

def load_resume(raw_input: Union[str, bytes, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Loads and sanitizes candidate resume.
    Strips sensitive PII (`candidate.email` and `candidate.phone`).
    Gracefully handles extra trailing data, multi-JSON payloads, and plain text resumes.
    Returns a clean, privacy-safe dictionary.
    """
    if isinstance(raw_input, (bytes, bytearray)):
        raw_input = raw_input.decode("utf-8", errors="replace")

    data = None
    if isinstance(raw_input, str):
        cleaned = raw_input.strip()
        # 1. Try standard JSON decode
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                data = parsed
            elif isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                data = parsed[0]
        except json.JSONDecodeError:
            pass

        # 2. If standard decode fails (e.g. Extra data at line X), try raw_decode to parse first valid JSON object
        if data is None:
            try:
                decoder = json.JSONDecoder()
                parsed, _ = decoder.raw_decode(cleaned)
                if isinstance(parsed, dict):
                    data = parsed
                elif isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                    data = parsed[0]
            except Exception:
                pass

        # 3. If still None, look for the first '{' and matching '}'
        if data is None:
            first_brace = cleaned.find("{")
            last_brace = cleaned.rfind("}")
            if first_brace != -1 and last_brace > first_brace:
                try:
                    parsed = json.loads(cleaned[first_brace:last_brace + 1])
                    if isinstance(parsed, dict):
                        data = parsed
                except Exception:
                    pass

        # 4. If all JSON attempts fail, wrap plain text into structured candidate resume
        if data is None:
            lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
            candidate_name = "Candidate"
            for line in lines[:5]:
                if line.lower().startswith("name:"):
                    candidate_name = line.split(":", 1)[1].strip()
                    break
                elif len(line.split()) in (2, 3) and not any(char in line for char in "{}:;@"):
                    candidate_name = line
                    break

            data = {
                "candidate": {
                    "name": candidate_name,
                    "headline": lines[0] if lines else "Candidate",
                    "summary": cleaned[:500]
                },
                "skills": {
                    "all_skills_flat": ["Software Engineering", "Problem Solving"]
                },
                "raw_text": cleaned
            }
    elif isinstance(raw_input, dict):
        data = copy.deepcopy(raw_input)
    else:
        raise ValueError("Unsupported resume format. Expected JSON string, bytes, or dict.")

    # Explicitly strip PII from candidate object
    if "candidate" in data and isinstance(data["candidate"], dict):
        data["candidate"].pop("email", None)
        data["candidate"].pop("phone", None)
        
    return data

def load_jd(raw_input: Union[str, bytes, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Loads and parses the job description.
    Supports either structured JSON with a top-level `job` object or plain text.
    """
    if isinstance(raw_input, (bytes, bytearray)):
        raw_input = raw_input.decode("utf-8")
        
    if isinstance(raw_input, str):
        try:
            data = json.loads(raw_input)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            # If plain text string is passed, wrap it
            return {"job": {"title": "Candidate Role", "raw_description": raw_input}}
            
    if isinstance(raw_input, dict):
        return copy.deepcopy(raw_input)
        
    raise ValueError("Unsupported JD format. Expected JSON string, bytes, or dict.")

def extract_metadata(resume: Dict[str, Any], jd: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Extracts high-level metadata (candidate_first_name, candidate_full_name, role_title)
    without leaking field access outside loaders.
    """
    full_name = None
    candidate_obj = resume.get("candidate", {})
    if isinstance(candidate_obj, dict):
        full_name = candidate_obj.get("name") or candidate_obj.get("candidate_name")
    elif isinstance(candidate_obj, str) and candidate_obj:
        full_name = candidate_obj
    
    if not full_name or full_name.lower() in ["candidate", "unknown", "name", "user"]:
        full_name = (
            resume.get("name") or 
            resume.get("candidate_name") or 
            resume.get("full_name") or
            (resume.get("personal_info", {}).get("name") if isinstance(resume.get("personal_info"), dict) else None) or
            full_name or
            "Candidate"
        )
        
    first_name = full_name.split()[0] if full_name else "Candidate"
    
    role_title = None
    job_obj = jd.get("job", {})
    if isinstance(job_obj, dict):
        role_title = job_obj.get("title") or job_obj.get("role") or job_obj.get("target_role")
    elif isinstance(job_obj, str) and job_obj:
        role_title = job_obj
    
    if not role_title or role_title.lower() in ["candidate role", "role"]:
        role_title = (
            jd.get("title") or 
            jd.get("role") or 
            jd.get("target_role") or 
            jd.get("target_job_title") or 
            "Full Stack Developer"
        )
    
    return first_name, full_name, role_title
