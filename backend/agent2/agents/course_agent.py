"""
Module 3 — Course Suggestion Agent
=====================================================
INPUT  : gap_report.json    (from Module 2 output)
       + resume.json        (from Module 1 output)
       + interview_report.json (from Module 4 output)

OUTPUT : courses.json

NOTE   : Module 4 (Interview) runs BEFORE Module 3
         so that interview weak areas can be used
         to suggest more targeted courses.

This module's output (courses.json) feeds:
  → Module 5 (Learning Planner) ONLY
=====================================================
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import Module3Output, CoursesData, CourseItem

load_dotenv()


class CourseAgent:
    """Module 3: Suggests free learning resources using gap report + resume + interview results."""

    MODEL_NAME = "openai/gpt-oss-120b"

    def __init__(self):
        self.llm = ChatGroq(
            model=self.MODEL_NAME,
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def _suggest_for_skill(
        self,
        skill: str,
        candidate_skills: list[str],
        interview_weak_areas: list[str],
    ) -> CoursesData:
        """
        Use LLM to suggest free resources for a skill.
        Uses candidate's existing skills + interview weak areas
        to make suggestions more targeted and personalized.
        """
        prompt = ChatPromptTemplate.from_template(
            """You are a personalized learning resource curator.

Skill to teach: {skill}
Candidate's existing skills (for context): {existing_skills}
Interview weak areas (areas where candidate struggled): {weak_areas}

Suggest 3 FREE, highly targeted learning resources for this skill.
Prioritize beginner-friendly resources if the skill is in weak_areas.

Only use: YouTube, freeCodeCamp, W3Schools, GeeksForGeeks, Official Docs,
          Coursera (Audit), edX (Audit), Khan Academy, MDN Web Docs.

Return ONLY valid JSON — no markdown:
{{
  "skill": "{skill}",
  "resources": [
    {{
      "skill": "{skill}",
      "title": "...",
      "url": "https://...",
      "platform": "...",
      "type": "video|article|course|docs",
      "is_free": true,
      "estimated_hours": 0.0
    }}
  ]
}}"""
        )
        chain = prompt | self.llm
        response = chain.invoke({
            "skill": skill,
            "existing_skills": json.dumps(candidate_skills),
            "weak_areas": json.dumps(interview_weak_areas),
        })
        raw_json = response.content.strip()

        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]

        parsed = json.loads(raw_json)
        resources = [CourseItem(**r) for r in parsed.get("resources", [])]
        return CoursesData(skill=skill, resources=resources)

    def run(
        self,
        gap_report: dict,
        resume: dict,
        interview_report: dict,
    ) -> dict:
        """
        Run Module 3 — Course Suggestion Agent.

        ─── INPUTS (all 3 required) ──────────────────────────
        gap_report       : gap_report.json  (Module 2 output)
        resume           : resume.json      (Module 1 output)
        interview_report : interview_report.json (Module 4 output)

        ─── OUTPUT ───────────────────────────────────────────
        courses.json → goes ONLY to Module 5 (Learning Planner)
        ──────────────────────────────────────────────────────

        Args:
            gap_report      : GapReportEnvelope dict from Module 2
            resume          : ResumeData dict from Module 1
            interview_report: Module4Output dict from Module 4

        Returns:
            dict matching Module3Output schema (CTBF-AI-05)
        """
        gap_data = gap_report["data"]
        interview_data = interview_report.get("data", {})

        # All skills to cover: critical → important → optional
        skills_to_cover = (
            gap_data.get("critical_gaps", []) +
            gap_data.get("important_gaps", []) +
            gap_data.get("optional_gaps", [])
        )

        # Extract candidate's existing skills from resume
        candidate_skills = resume.get("skills", [])

        # Extract interview weak areas to personalize suggestions
        interview_weak_areas = interview_data.get("weak_areas", [])

        print(f"  [Module 3] Skills to cover : {skills_to_cover}")
        print(f"  [Module 3] Interview weak areas: {interview_weak_areas}")

        courses_list = []
        for skill in skills_to_cover:
            print(f"  [Module 3] Fetching resources for: {skill}")
            courses_data = self._suggest_for_skill(
                skill=skill,
                candidate_skills=candidate_skills,
                interview_weak_areas=interview_weak_areas,
            )
            courses_list.append(courses_data)

        output = Module3Output(
            user_id=gap_report["user_id"],
            session_id=gap_report["session_id"],
            data=courses_list,
        )
        return output.model_dump()
