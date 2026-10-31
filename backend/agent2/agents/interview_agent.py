"""
Module 4 — Interview Preparation Agent
Generates technical/HR mock interview questions and evaluates answers.
Terminal-based interactive session.
Output: interview_report.json
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import Module4Output, InterviewReportData, QAItem

load_dotenv()


class InterviewAgent:
    """Module 4: Terminal-based mock interview session."""

    MODEL_NAME = "openai/gpt-oss-120b"

    def __init__(self):
        self.llm = ChatGroq(
            model=self.MODEL_NAME,
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def _generate_questions(self, resume_data: dict, gap_report: dict) -> list[str]:
        """Generate interview questions based on resume and gap report."""
        prompt = ChatPromptTemplate.from_template(
            """You are a technical interviewer. Generate 5 interview questions based on:

Candidate Skills: {skills}
Critical Gaps: {critical_gaps}
Important Gaps: {important_gaps}
Experience Years: {experience}

Mix: 3 technical questions on their skills, 2 questions that probe their gap areas.
Return ONLY a valid JSON array of question strings — no explanation:
["question1", "question2", "question3", "question4", "question5"]"""
        )
        chain = prompt | self.llm
        response = chain.invoke({
            "skills": json.dumps(resume_data.get("skills", [])),
            "critical_gaps": json.dumps(gap_report["data"].get("critical_gaps", [])),
            "important_gaps": json.dumps(gap_report["data"].get("important_gaps", [])),
            "experience": resume_data.get("experience_years", 0.0),
        })
        raw_json = response.content.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
        return json.loads(raw_json)

    def _evaluate_answer(self, question: str, user_answer: str) -> tuple[str, float]:
        """Evaluate a user's answer and return (evaluation_label, score)."""
        prompt = ChatPromptTemplate.from_template(
            """You are a strict technical interviewer evaluating a candidate's answer.

Question: {question}
Candidate's Answer: {answer}

Evaluate the answer and return ONLY valid JSON:
{{
  "evaluation": "strong|average|weak",
  "score": 0.0,
  "expected_answer": "brief ideal answer"
}}
Score: 1.0 = perfect, 0.5 = average, 0.0 = wrong/blank"""
        )
        chain = prompt | self.llm
        response = chain.invoke({"question": question, "answer": user_answer})
        raw_json = response.content.strip()
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
        parsed = json.loads(raw_json)
        return parsed.get("evaluation", "weak"), parsed.get("score", 0.0), parsed.get("expected_answer", "")

    def run(self, resume_data: dict, gap_report: dict) -> dict:
        """
        Run Module 4 — interactive terminal mock interview.

        Args:
            resume_data: Module1Output['resume'] dict
            gap_report: GapReportEnvelope dict from Module 2

        Returns:
            dict matching Module4Output schema
        """
        resume = resume_data.get("resume", resume_data)
        questions = self._generate_questions(resume, gap_report)

        print("\n" + "=" * 60)
        print("  MOCK INTERVIEW SESSION — START")
        print("  Answer each question. Type your response and press Enter.")
        print("=" * 60 + "\n")

        qa_pairs = []
        scores = []

        for i, question in enumerate(questions, 1):
            print(f"\nQ{i}: {question}")
            print("-" * 40)
            user_answer = input("Your Answer: ").strip()

            evaluation, score, expected = self._evaluate_answer(question, user_answer)
            scores.append(score)

            print(f"  ✦ Evaluation: {evaluation.upper()} (Score: {score:.1f})")

            qa_pairs.append(QAItem(
                question=question,
                expected_answer=expected,
                user_answer=user_answer,
                evaluation=evaluation,
                score=score,
            ))

        overall_score = sum(scores) / len(scores) if scores else 0.0
        weak_areas = [qa.question for qa in qa_pairs if qa.evaluation == "weak"]
        strong_areas = [qa.question for qa in qa_pairs if qa.evaluation == "strong"]

        report_data = InterviewReportData(
            total_questions=len(questions),
            qa_pairs=qa_pairs,
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            overall_score=overall_score,
            recommendation=(
                "Ready for interviews" if overall_score >= 0.7
                else "Need more preparation in gap areas"
            ),
        )

        output = Module4Output(
            user_id=gap_report["user_id"],
            session_id=gap_report["session_id"],
            data=report_data,
        )
        return output.model_dump()
