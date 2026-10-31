"""
Utility helpers shared across all modules.
"""

import json
from pathlib import Path
from datetime import datetime


def save_json(data: dict, filepath: str) -> None:
    """Save dict as formatted JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Saved: {path.resolve()}")


def load_json(filepath: str) -> dict:
    """Load JSON file and return as dict."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def utc_now() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.utcnow().isoformat() + "Z"


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def validate_ctbf_envelope(data: dict) -> bool:
    """
    Validate that a dict conforms to CTBF-AI-05 envelope structure.
    Returns True if valid, raises ValueError if not.
    """
    required_keys = ["user_id", "module", "status", "data", "created_at"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise ValueError(f"CTBF-AI-05 validation failed. Missing keys: {missing}")
    return True
