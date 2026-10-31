"""
Module 5 — Learning Planner Agent
Generates 30-day or 3-6 month personalized learning roadmap.
Output: learning_plan.json
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import Module5Output, LearningPlanData, DayPlan

load_dotenv()


class PlannerAgent:
    """Module 5: Time-bound personalized learning plan generator."""

    MODEL_NAME = "openai/gpt-oss-120b"

    def __init__(self):
        self.llm = ChatGroq(
            model=self.MODEL_NAME,
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def _generate_plan(
        self,
        priority_order: list[str],
        courses: list[dict],
        plan_type: str = "30_day",
    ) -> list[DayPlan]:
        """Generate a day-by-day learning schedule."""
        total_days = 30 if plan_type == "30_day" else (90 if plan_type == "3_month" else 180)
        days_per_skill = max(1, total_days // max(len(priority_order), 1))

        # Build resource map: skill → list of resource titles/URLs
        resource_map = {}
        for course_group in courses:
            skill = course_group.get("skill", "")
            resources = [r.get("title", "") + " — " + r.get("url", "") for r in course_group.get("resources", [])]
            resource_map[skill] = resources

        prompt = ChatPromptTemplate.from_template(
            """You are a personalized learning coach. Create a {plan_type} learning plan.

Skills to learn (in priority order): {skills}
Available resources per skill: {resources}
Total days: {total_days}
Days per skill (approx): {days_per_skill}

Generate a day-by-day schedule. Return ONLY valid JSON — no markdown:
[
  {{
    "day": 1,
    "topic": "Introduction to Docker",
    "skill": "Docker",
    "tasks": ["Watch intro video", "Install Docker locally", "Run hello-world container"],
    "resources": ["YouTube: Docker Crash Course — https://youtube.com/..."],
    "estimated_hours": 2.0
  }}
]

Generate exactly {total_days} day entries. Be specific and actionable."""
        )
        chain = prompt | self.llm
        response = chain.invoke({
            "plan_type": plan_type,
            "skills": json.dumps(priority_order),
            "resources": json.dumps(resource_map),
            "total_days": total_days,
            "days_per_skill": days_per_skill,
        })
        raw_json = response.content.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]

        parsed = json.loads(raw_json)
        return [DayPlan(**day) for day in parsed]

    def run(self, gap_report: dict, courses: dict, plan_type: str = "30_day") -> dict:
        """
        Run Module 5.

        Args:
            gap_report: GapReportEnvelope dict from Module 2
            courses: Module3Output dict from Module 3
            plan_type: '30_day' | '3_month' | '6_month'

        Returns:
            dict matching Module5Output schema
        """
        data = gap_report["data"]
        priority_order = data.get("improvement_priority_order", [])
        courses_data = courses.get("data", [])

        schedule = self._generate_plan(
            priority_order=priority_order,
            courses=courses_data,
            plan_type=plan_type,
        )

        plan_data = LearningPlanData(
            plan_type=plan_type,
            total_days=len(schedule),
            skills_covered=priority_order,
            schedule=schedule,
        )

        output = Module5Output(
            user_id=gap_report["user_id"],
            session_id=gap_report["session_id"],
            data=plan_data,
        )
        return output.model_dump()
