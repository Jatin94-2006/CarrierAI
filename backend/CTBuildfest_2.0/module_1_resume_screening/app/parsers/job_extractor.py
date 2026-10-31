import re
from typing import Dict, Any, Union
from app.core.logging import logger
from app.schemas.job import JobStructuredData, JobEducationRequirements
from app.ai.groq_client import groq_client
from app.ai.prompts import JOB_EXTRACTION_SYSTEM_PROMPT
from app.utils.text_cleaner import clean_and_normalize_text

COMMON_TECH_REQUIREMENTS = [
    "python", "fastapi", "flask", "django", "sql", "postgresql", "mysql", "mongodb",
    "docker", "kubernetes", "aws", "git", "rest apis", "redis", "linux", "ci/cd",
    "react", "javascript", "typescript", "java", "c++", "data structures", "algorithms"
]

def extract_structured_job(job_input: Union[str, Dict[str, Any]]) -> JobStructuredData:
    """
    Parses a job description from raw text or JSON dictionary.
    Categorizes skills into required vs preferred, extracts seniority and min experience.
    """
    if isinstance(job_input, dict):
        if "job" in job_input and isinstance(job_input["job"], dict):
            job_input = job_input["job"]
        return JobStructuredData(**job_input)

    raw_text = clean_and_normalize_text(job_input)
    
    # 1. Try Groq AI extraction
    if groq_client.is_available():
        user_prompt = f"Job Description Text to Extract:\n\n{raw_text[:12000]}"
        ai_data = groq_client.call_structured(JOB_EXTRACTION_SYSTEM_PROMPT, user_prompt)
        if ai_data and "title" in ai_data:
            try:
                return JobStructuredData(**ai_data)
            except Exception as e:
                logger.warning(f"Groq JD extraction parsing error: {e}. Falling back to deterministic JD parser.")

    # 2. Deterministic Heuristic JD Extractor Fallback
    return _deterministic_job_extractor(raw_text)

def _deterministic_job_extractor(text: str) -> JobStructuredData:
    title = None
    # 1. Search for explicit role labels
    label_match = re.search(r'(?:job\s*title|target\s*role|role|position|opening\s*(?:for)?|hiring\s*(?:for)?)\s*[:\-]\s*([A-Za-z0-9\s\/\+\.\(\)\-]+)', text, re.I)
    if label_match:
        val = label_match.group(1).split("\n")[0].split(".")[0].strip()
        words = val.split()
        if 1 <= len(words) <= 7 and not any(ch in val for ch in "@:;0123456789{}"):
            title = val.title()

    # 2. Search for common tech job roles anywhere in the text
    if not title:
        role_pat = r'\b(?:senior|sr\.?|lead|junior|jr\.?|principal|staff|associate)?\s*(?:full\s*stack|frontend|front\-end|backend|back\-end|web|software|systems?|embedded|cloud|devops|site\s*reliability|sre|platform|infrastructure|data|machine\s*learning|ai|deep\s*learning|nlp|computer\s*vision|mobile|android|ios|flutter|react\s*native|qa|test|automation|security|cybersecurity|database|network)\s*(?:engineer|developer|architect|scientist|analyst|specialist|programmer|lead|manager|administrator)\b'
        match = re.search(role_pat, text, re.I)
        if match:
            title = match.group(0).strip().title()

    # 3. Fallback to first line if clean
    if not title:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:5]:
            if any(w in line.lower() for w in ["about", "company", "description", "requirements", "responsibilities", "overview", "location", "we are", "nexus"]):
                continue
            clean = re.sub(r'^(job title|role|position)[:\s-]*', '', line, flags=re.IGNORECASE).strip()
            clean = re.split(r'[\.,\-|;:]', clean)[0].strip()
            words = clean.split()
            if 1 <= len(words) <= 5 and not any(ch in clean for ch in "@0123456789/\\#+{}"):
                title = clean.title()
                break

    if not title or title.lower() in ["job description", "about us", "overview"]:
        title = "Software Engineer"
    
    # Detect Seniority & Experience
    text_lower = text.lower()
    seniority = "Entry Level"
    if any(s in text_lower for s in ["senior", "sr.", "lead", "architect"]):
        seniority = "Senior"
    elif any(s in text_lower for s in ["mid-level", "mid level", "intermediate", "2-4 years"]):
        seniority = "Mid Level"
    elif any(s in text_lower for s in ["intern", "internship", "graduate", "fresher", "entry-level", "entry level", "junior", "jr."]):
        seniority = "Entry Level"

    # Extract required years of experience
    exp_years = 0.0
    exp_match = re.search(r'(\d+)(?:\s*-\s*\d+)?\+?\s*(?:to\s*\d+\s*)?years?(?:\s*of)?\s*experience', text_lower)
    if exp_match:
        exp_years = float(exp_match.group(1))
    elif "entry level" in seniority.lower() or "fresher" in text_lower:
        exp_years = 0.0

    # Categorize Required vs Preferred skills
    required_skills = []
    preferred_skills = []
    
    # Check for preferred / nice-to-have section
    preferred_text = ""
    req_text = text_lower
    pref_match = re.search(r'(preferred|nice to have|bonus|good to have)[:\s]+([\s\S]*)', text_lower)
    if pref_match:
        preferred_text = pref_match.group(2)
        req_text = text_lower[:pref_match.start()]

    for tech in COMMON_TECH_REQUIREMENTS:
        pattern = rf'\b{re.escape(tech)}\b'
        if preferred_text and re.search(pattern, preferred_text):
            preferred_skills.append(tech.title() if len(tech) > 3 else tech.upper())
        elif re.search(pattern, req_text):
            required_skills.append(tech.title() if len(tech) > 3 else tech.upper())

    # Fallback default skills if none detected
    if not required_skills and not preferred_skills:
        required_skills = ["Python", "SQL", "REST APIs"]
        preferred_skills = ["FastAPI", "Docker"]

    # Degree requirement
    degree_req = "B.Tech / B.E. / BCA / MCA in Computer Science or related field"
    if "master" in text_lower:
        degree_req = "Master's Degree in Computer Science or related"

    # Mandatory criteria
    mandatory = []
    if exp_years > 0:
        mandatory.append(f"Minimum {int(exp_years)} year(s) of relevant experience")
    if degree_req:
        mandatory.append("Bachelor's or Master's degree in engineering or relevant discipline")

    return JobStructuredData(
        title=title,
        company="Hiring Organization",
        category="Software Engineering",
        seniority=seniority,
        experience_required=exp_years,
        preferred_experience=exp_years + 1.0 if exp_years > 0 else 1.0,
        required_skills=list(dict.fromkeys(required_skills)),
        preferred_skills=list(dict.fromkeys(preferred_skills)),
        required_soft_skills=["Communication", "Problem Solving", "Teamwork"],
        education=JobEducationRequirements(
            required_degree=degree_req,
            preferred_specialization="Computer Science / Information Technology"
        ),
        mandatory_certifications=[],
        responsibilities=["Design and maintain backend services", "Collaborate on database schema design"],
        technical_requirements=required_skills + preferred_skills,
        tools_and_technologies=required_skills + preferred_skills,
        keywords=required_skills + preferred_skills + ["Backend", "Software Engineering"],
        mandatory_requirements=mandatory
    )
