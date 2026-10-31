"""
Module 1 — Resume Analysis Agent
Parses raw resume + JD into structured JSON using LLM.
Output: resume.json + jd.json (as Module1Output)
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import ResumeData, JDData, Module1Output, ProjectItem, ExperienceItem

load_dotenv()


class ResumeAgent:
    """Module 1: Parses resume + JD into structured data."""

    MODEL_NAME = "openai/gpt-oss-120b"

    def __init__(self):
        self.llm = ChatGroq(
            model=self.MODEL_NAME,
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def _read_resume(self, resume_path: str) -> str:
        """Read resume as plain text (supports .txt and .pdf)."""
        path = Path(resume_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume not found: {resume_path}")

        if path.suffix.lower() == ".pdf":
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            except ImportError:
                raise ImportError("Install pdfplumber: pip install pdfplumber")
        else:
            return path.read_text(encoding="utf-8")

    def _parse_resume(self, raw_text: str) -> ResumeData:
        """Use LLM to extract structured data from raw resume text."""
        prompt = ChatPromptTemplate.from_template(
            """You are a resume parser. Extract structured information from the resume below.
Return ONLY valid JSON — no explanation, no markdown.

Resume:
{resume_text}

Return JSON with these exact keys:
{{
  "full_name": "...",
  "email": "...",
  "skills": ["skill1", "skill2"],
  "experience_years": 0.0,
  "education": "...",
  "projects": [{{"title": "...", "description": "...", "technologies": ["..."]}}],
  "experience": [{{"company": "...", "role": "...", "duration_years": 0.0, "responsibilities": ["..."]}}]
}}"""
        )
        chain = prompt | self.llm
        response = chain.invoke({"resume_text": raw_text})
        raw_json = response.content.strip()

        # Strip markdown code fences if present
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]

        parsed = json.loads(raw_json)
        return ResumeData(
            full_name=parsed.get("full_name"),
            email=parsed.get("email"),
            skills=parsed.get("skills", []),
            experience_years=parsed.get("experience_years", 0.0),
            education=parsed.get("education"),
            projects=[ProjectItem(**p) for p in parsed.get("projects", [])],
            experience=[ExperienceItem(**e) for e in parsed.get("experience", [])],
            raw_resume_text=raw_text,
        )

    def _parse_jd(self, jd_text: str) -> JDData:
        """Use LLM to extract structured data from raw JD text."""
        prompt = ChatPromptTemplate.from_template(
            """You are a job description parser. Extract structured information.
Return ONLY valid JSON — no explanation, no markdown.

Job Description:
{jd_text}

Return JSON with these exact keys:
{{
  "title": "...",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "experience_required": 0.0
}}"""
        )
        chain = prompt | self.llm
        response = chain.invoke({"jd_text": jd_text})
        raw_json = response.content.strip()

        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]

        parsed = json.loads(raw_json)
        return JDData(
            title=parsed.get("title"),
            required_skills=parsed.get("required_skills", []),
            preferred_skills=parsed.get("preferred_skills", []),
            experience_required=parsed.get("experience_required"),
            raw_jd_text=jd_text,
        )

    def run(self, resume_path: str, jd_text: str, user_id: str) -> dict:
        """
        Run Module 1.

        Args:
            resume_path: Path to resume file (.txt or .pdf)
            jd_text: Raw job description string
            user_id: User UUID string

        Returns:
            dict matching Module1Output schema
        """
        raw_resume = self._read_resume(resume_path)
        resume_data = self._parse_resume(raw_resume)
        resume_data.user_id = user_id

        jd_data = self._parse_jd(jd_text)

        output = Module1Output(resume=resume_data, jd=jd_data)
        return output.model_dump()
