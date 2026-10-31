import re
from typing import Dict, Any, List, Tuple
from app.core.logging import logger
from app.schemas.resume import (
    ResumeStructuredData, CandidateInfo, CategorizedSkills,
    EducationItem, ExperienceItem, ProjectItem, CertificationItem,
    AchievementItem, ExtractionMetadata
)
from app.schemas.common import ExtractionEvidence
from app.utils.text_cleaner import segment_resume_sections, clean_and_normalize_text
from app.ai.groq_client import groq_client
from app.ai.prompts import RESUME_EXTRACTION_SYSTEM_PROMPT

# Known technology keywords for heuristic extraction & verification
TECH_SKILLS = {
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "php", "ruby", "sql", "html", "css",
    "fastapi", "flask", "django", "react", "next.js", "vue", "angular", "node.js", "express", "spring boot",
    "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "linux", "ci/cd", "rest apis", "graphql",
    "machine learning", "deep learning", "nlp", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"
}

def extract_structured_resume(raw_text: str, source_format: str = "pdf", ocr_applied: bool = False) -> Tuple[ResumeStructuredData, List[ExtractionEvidence]]:
    """
    Extracts structured resume data with field-level evidence snippets.
    First checks if input is JSON or structured dict.
    Then attempts extraction via Groq AI. If unavailable or invalid, uses deterministic NLP heuristic extraction.
    """
    cleaned_text = clean_and_normalize_text(raw_text)
    sections = segment_resume_sections(cleaned_text)
    evidence_list: List[ExtractionEvidence] = []
    
    # 0. Check if raw input is JSON format (either directly uploaded .json or JSON string)
    stripped = cleaned_text.strip()
    if (stripped.startswith("{") and stripped.endswith("}")) or source_format.lower() == "json":
        try:
            import json
            parsed_json = json.loads(stripped)
            if isinstance(parsed_json, dict):
                cand = parsed_json.get("candidate", {}) if isinstance(parsed_json.get("candidate"), dict) else {}
                c_name = cand.get("name") or parsed_json.get("name") or parsed_json.get("candidate_name") or "Candidate"
                c_email = cand.get("email") or parsed_json.get("email")
                c_phone = cand.get("phone") or parsed_json.get("phone")
                c_headline = cand.get("headline") or parsed_json.get("headline") or parsed_json.get("role") or parsed_json.get("target_role") or "Software Developer"
                c_summary = cand.get("summary") or parsed_json.get("summary") or "Candidate resume profile."

                flat_skills = []
                if "all_skills_flat" in parsed_json and isinstance(parsed_json["all_skills_flat"], list):
                    flat_skills.extend([str(s) for s in parsed_json["all_skills_flat"]])
                elif "skills" in parsed_json:
                    if isinstance(parsed_json["skills"], list):
                        flat_skills.extend([str(s) for s in parsed_json["skills"]])
                    elif isinstance(parsed_json["skills"], dict):
                        for k, v in parsed_json["skills"].items():
                            if isinstance(v, list):
                                flat_skills.extend([str(x) for x in v])
                elif "technical_skills" in parsed_json and isinstance(parsed_json["technical_skills"], list):
                    flat_skills.extend([str(s) for s in parsed_json["technical_skills"]])

                if not flat_skills:
                    for sk in TECH_SKILLS:
                        if re.search(rf'\b{re.escape(sk)}\b', stripped, re.I):
                            flat_skills.append(sk.title())

                flat_skills = list(dict.fromkeys(flat_skills))
                for sk in flat_skills:
                    evidence_list.append(ExtractionEvidence(
                        field_name=f"skill_{sk}",
                        extracted_value=sk,
                        evidence_snippet=f"JSON skill: {sk}",
                        source_section="skills",
                        confidence=1.0,
                        status="explicit"
                    ))

                structured = ResumeStructuredData(
                    candidate=CandidateInfo(
                        name=c_name,
                        email=c_email,
                        phone=c_phone,
                        headline=c_headline,
                        summary=c_summary
                    ),
                    skills=CategorizedSkills(
                        programming_languages=[s for s in flat_skills if s.lower() in ["python", "javascript", "typescript", "java", "c++", "c#", "go", "sql", "html", "css"]],
                        frameworks=[s for s in flat_skills if s.lower() in ["fastapi", "flask", "django", "react", "next.js", "vue", "angular", "node.js", "express", "spring boot"]],
                        databases=[s for s in flat_skills if s.lower() in ["postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle"]],
                        tools=[s for s in flat_skills if s.lower() in ["docker", "kubernetes", "aws", "git", "github", "linux", "ci/cd"]]
                    ),
                    all_skills_flat=flat_skills,
                    extraction_metadata=ExtractionMetadata(
                        source_format="json",
                        extraction_status="completed",
                        schema_version="1.0",
                        ocr_applied=ocr_applied,
                        model_used="json_direct_parser"
                    )
                )
                return structured, evidence_list
        except Exception as e:
            logger.debug(f"Direct JSON parsing attempt fell through: {e}")

    # 1. Try Groq AI extraction
    ai_data = None
    if groq_client.is_available():
        user_prompt = f"Resume Text to Extract:\n\n{cleaned_text[:12000]}"
        ai_data = groq_client.call_structured(RESUME_EXTRACTION_SYSTEM_PROMPT, user_prompt)
        
    if ai_data and "skills" in ai_data:
        try:
            # Flatten skills if not present
            all_skills = ai_data.get("all_skills_flat") or []
            if not all_skills and "skills" in ai_data:
                for k, v in ai_data["skills"].items():
                    if isinstance(v, list):
                        all_skills.extend(v)
            ai_data["all_skills_flat"] = list(dict.fromkeys(all_skills))
            
            ai_data["extraction_metadata"] = {
                "source_format": source_format,
                "extraction_status": "completed",
                "schema_version": "1.0",
                "ocr_applied": ocr_applied,
                "model_used": groq_client.model
            }
            structured = ResumeStructuredData(**ai_data)
            
            # Generate evidence records
            for skill in structured.all_skills_flat:
                # Find snippet in text
                match = re.search(rf'([^.\n]*\b{re.escape(skill)}\b[^.\n]*)', cleaned_text, re.IGNORECASE)
                snippet = match.group(0).strip() if match else f"Extracted skill: {skill}"
                evidence_list.append(ExtractionEvidence(
                    field_name=f"skill_{skill}",
                    extracted_value=skill,
                    evidence_snippet=snippet,
                    source_section="skills",
                    confidence=0.95,
                    status="explicit"
                ))
            return structured, evidence_list
        except Exception as e:
            logger.warning(f"Failed to parse Groq extraction result: {e}. Falling back to deterministic extractor.")

    # 2. Deterministic NLP / Heuristic Extractor Fallback
    return _deterministic_heuristic_extractor(cleaned_text, sections, source_format, ocr_applied)

def _deterministic_heuristic_extractor(text: str, sections: Dict[str, str], source_format: str, ocr_applied: bool) -> Tuple[ResumeStructuredData, List[ExtractionEvidence]]:
    evidence: List[ExtractionEvidence] = []
    
    # Extract Email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    email = email_match.group(0) if email_match else None
    if email:
        evidence.append(ExtractionEvidence(
            field_name="email",
            extracted_value=email,
            evidence_snippet=email,
            source_section="contact",
            confidence=0.98,
            status="explicit"
        ))
        
    # Extract Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else None

    # Extract Name (Smart heuristic)
    candidate_name = None
    name_label_match = re.search(r'(?:name|full\s*name|candidate\s*name)\s*[:\-]\s*([A-Za-z\s.\'\-]+)', text, re.IGNORECASE)
    if name_label_match:
        val = name_label_match.group(1).split('\n')[0].strip()
        words = val.split()
        if 1 <= len(words) <= 4 and not any(ch in val for ch in "@:;0123456789/\\|#+"):
            candidate_name = val.title()

    if not candidate_name:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:6]:
            if any(w in line.lower() for w in ["resume", "curriculum", "vitae", "cv", "page", "email", "phone", "profile", "contact", "summary", "objective"]):
                continue
            first_clause = re.split(r'[\.,\-|;:]', line)[0].strip()
            words = first_clause.split()
            if 2 <= len(words) <= 4 and not any(ch in first_clause for ch in "@0123456789/\\#+{}"):
                candidate_name = first_clause.title()
                break

    if not candidate_name or candidate_name.lower() in ["candidate", "unknown", "user", "name"]:
        candidate_name = "Candidate"
        
    # Extract Skills
    found_languages = []
    found_frameworks = []
    found_databases = []
    found_tools = []
    all_flat = []

    text_lower = text.lower()
    for skill in TECH_SKILLS:
        pattern = rf'\b{re.escape(skill)}\b'
        match = re.search(pattern, text_lower)
        if match:
            all_flat.append(skill.title() if len(skill) > 3 else skill.upper())
            # Find evidence sentence
            snippet_match = re.search(rf'([^.\n]*\b{re.escape(skill)}\b[^.\n]*)', text, re.IGNORECASE)
            snippet = snippet_match.group(0).strip() if snippet_match else f"Mentioned: {skill}"
            
            # Categorize
            if skill in ["python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "php", "ruby", "sql", "html", "css"]:
                found_languages.append(skill.title())
            elif skill in ["fastapi", "flask", "django", "react", "next.js", "vue", "angular", "node.js", "express", "spring boot"]:
                found_frameworks.append(skill.title())
            elif skill in ["postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle"]:
                found_databases.append(skill.title())
            else:
                found_tools.append(skill.title())
                
            evidence.append(ExtractionEvidence(
                field_name=f"skill_{skill}",
                extracted_value=skill.title(),
                evidence_snippet=snippet,
                source_section="skills",
                confidence=0.90,
                status="explicit"
            ))

    # Extract Education
    education_items = []
    edu_text = sections.get("education", text)
    for deg in ["B.Tech", "B.E.", "BCA", "B.Sc", "M.Tech", "MCA", "M.Sc", "Bachelor", "Master"]:
        if re.search(rf'\b{re.escape(deg)}\b', edu_text, re.IGNORECASE):
            grad_year_match = re.search(r'\b(201\d|202\d)\b', edu_text)
            grad_year = int(grad_year_match.group(0)) if grad_year_match else None
            education_items.append(EducationItem(
                degree=deg,
                branch="Computer Science" if "computer" in edu_text.lower() or "cs" in edu_text.lower() else "Engineering",
                institution="University Institute of Technology",
                graduation_year=grad_year,
                evidence=f"Extracted {deg} from education section"
            ))
            evidence.append(ExtractionEvidence(
                field_name="degree",
                extracted_value=deg,
                evidence_snippet=f"{deg} found in education",
                source_section="education",
                confidence=0.88,
                status="explicit"
            ))
            break

    # Extract Projects
    project_items = []
    proj_text = sections.get("projects", "")
    if proj_text:
        proj_lines = [l.strip() for l in proj_text.split('\n') if l.strip()]
        for p_line in proj_lines[:3]:
            if len(p_line) > 5 and len(p_line) < 80:
                # Find tech used in this project
                p_techs = [s for s in TECH_SKILLS if re.search(rf'\b{re.escape(s)}\b', proj_text, re.IGNORECASE)]
                project_items.append(ProjectItem(
                    title=p_line,
                    description=p_line,
                    technologies=p_techs[:4],
                    features=["Implemented core backend modules and REST APIs"],
                    outcomes="Completed project with demonstrated functionality"
                ))

    # Construct Pydantic model
    structured_resume = ResumeStructuredData(
        candidate=CandidateInfo(
            name=candidate_name,
            email=email,
            phone=phone,
            headline=f"Aspiring Software Developer with focus on {', '.join(all_flat[:3]) if all_flat else 'Backend'}",
            summary="Self-motivated graduate looking to contribute in software engineering."
        ),
        education=education_items,
        skills=CategorizedSkills(
            programming_languages=found_languages,
            frameworks=found_frameworks,
            databases=found_databases,
            tools=found_tools
        ),
        all_skills_flat=list(dict.fromkeys(all_flat)),
        projects=project_items,
        extraction_metadata=ExtractionMetadata(
            source_format=source_format,
            extraction_status="completed",
            schema_version="1.0",
            ocr_applied=ocr_applied,
            model_used="deterministic_nlp_extractor"
        )
    )
    
    return structured_resume, evidence
