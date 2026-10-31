import re
import unicodedata
from typing import Dict, List, Tuple

def clean_and_normalize_text(text: str) -> str:
    """
    Cleans raw extracted text from PDF/DOCX:
    - Normalizes unicode characters (NFKD).
    - Replaces non-standard whitespace and multiple blank lines.
    - Strips non-printable characters.
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Replace non-breaking spaces and line separators
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    # Normalize quotes and hyphens
    text = re.sub(r'[“”]', '"', text)
    text = re.sub(r'[‘’]', "'", text)
    text = re.sub(r'[—–]', '-', text)
    
    # Condense consecutive horizontal spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Condense multiple newlines to max 2
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    return text.strip()

COMMON_SECTIONS = [
    "summary", "objective", "profile",
    "experience", "work history", "employment history",
    "internships", "internship experience",
    "education", "academic background",
    "skills", "technical skills", "core competencies",
    "projects", "academic projects", "personal projects",
    "certifications", "licenses", "courses",
    "achievements", "awards", "honors", "publications"
]

def segment_resume_sections(text: str) -> Dict[str, str]:
    """
    Segments resume text into canonical section blocks using regex heuristics.
    Helps locate provenance and section evidence snippets.
    """
    lines = text.split('\n')
    sections: Dict[str, List[str]] = {"general": []}
    current_section = "general"
    
    for line in lines:
        cleaned_line = line.strip().lower()
        matched_section = None
        
        # Check if line looks like a header (short and contains keyword)
        if len(cleaned_line) < 50:
            for s in COMMON_SECTIONS:
                # Match standalone header or header with colon/dash
                if re.match(rf'^(#+\s*)?{re.escape(s)}[:\s]*$', cleaned_line):
                    matched_section = s
                    break
        
        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(line)
            
    return {k: clean_and_normalize_text('\n'.join(v)) for k, v in sections.items() if v}

def is_text_insufficient_or_scanned(text: str, min_chars: int = 60) -> bool:
    """Detects whether extracted text is empty or too sparse, indicating a scanned image PDF."""
    if not text or len(text.strip()) < min_chars:
        return True
    # If ratio of alpha characters is lower than 40%, it may be garbage/scanned
    alpha_count = sum(c.isalpha() for c in text)
    return (alpha_count / max(1, len(text))) < 0.35
