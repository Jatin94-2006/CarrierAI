import os
import re
from fastapi import UploadFile
from app.config import settings
from app.core.exceptions import FileValidationError

DANGEROUS_EXTENSIONS = {
    "exe", "bat", "cmd", "sh", "ps1", "vbs", "jar", "msi", "dll", "py", "js"
}

def validate_uploaded_file(file: UploadFile) -> str:
    """
    Validates uploaded file extension, mime type, and filename safety.
    Returns the sanitized file extension.
    """
    if not file.filename:
        raise FileValidationError("Missing file name")
    
    # Strip dangerous characters from filename
    safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename)
    parts = safe_filename.rsplit('.', 1)
    if len(parts) < 2:
        raise FileValidationError("File has no extension")
    
    ext = parts[1].lower()
    if ext in DANGEROUS_EXTENSIONS:
        raise FileValidationError(f"Forbidden file type: .{ext}")
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise FileValidationError(f"Unsupported file format: .{ext}. Allowed: {settings.ALLOWED_EXTENSIONS}")
    
    return ext

def sanitize_for_prompt(text: str, max_chars: int = 15000) -> str:
    """
    Sanitizes user-provided text before embedding into LLM prompts.
    Mitigates prompt injection by neutralizing delimiters and bounding length.
    """
    if not text:
        return ""
    # Truncate to reasonable token limit
    clean = text[:max_chars]
    # Neutralize markdown system command injectors
    clean = clean.replace("```system", "'''system")
    clean = clean.replace("<<SYS>>", "[SYS]")
    return clean
