"""
Agent 3: Course Suggestion Agent
=================================
Processes skill gaps from Resume Gap Analysis (Agent 2) and Interview Gap Analysis (Agent 4)
to generate high-impact, FREE, short-duration (< 1 week / crash courses) 
learning recommendations tailored for the 30-Day Learning Planner (Agent 5).
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone

# ─── Curated Short-Duration Free Courses (< 1 Week) ─────────────────────────
# All courses are selected to be completed in under 7 days (1 to 6 hours or 1-3 days)
# to perfectly match a 30-day preparation sprint.

COURSE_DATA = {
    "Python": [
        {
            "title": "Python for Beginners – Comprehensive Crash Course",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "Python",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Fast-track Python essentials: syntax, data structures, functions, OOP, and practical exercises.",
            "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
            "resource_type": "Video",
            "is_free": True,
            "duration": "4.5 hours (< 1 day)",
            "duration_hours": 4.5
        },
        {
            "title": "Python Quickstart Tutorial",
            "platform": "W3Schools",
            "skill": "Python",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Interactive byte-sized Python modules with instant code run exercises.",
            "url": "https://www.w3schools.com/python/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "6 hours (2 days)",
            "duration_hours": 6.0
        },
        {
            "title": "Python Top Interview Coding Questions",
            "platform": "GeeksforGeeks",
            "skill": "Python",
            "skill_category": "Technical",
            "difficulty": "Intermediate",
            "description": "Targeted Python problem-solving patterns and high-frequency backend interview code snippets.",
            "url": "https://www.geeksforgeeks.org/python-programming-language/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "5 hours (2 days)",
            "duration_hours": 5.0
        }
    ],
    "FastAPI": [
        {
            "title": "FastAPI Crash Course – Build & Deploy APIs",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "FastAPI",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Hands-on API creation: routing, Pydantic validation, dependency injection, and JWT security.",
            "url": "https://www.youtube.com/watch?v=tLKKmouUams",
            "resource_type": "Video",
            "is_free": True,
            "duration": "5 hours (1 day)",
            "duration_hours": 5.0
        },
        {
            "title": "FastAPI Fast-Track Official Tutorial",
            "platform": "FastAPI Docs",
            "skill": "FastAPI",
            "skill_category": "Technical",
            "difficulty": "Intermediate",
            "description": "Concise official guide covering async def, path parameters, request bodies, and Swagger testing.",
            "url": "https://fastapi.tiangolo.com/tutorial/",
            "resource_type": "Documentation",
            "is_free": True,
            "duration": "4 hours (1-2 days)",
            "duration_hours": 4.0
        },
        {
            "title": "Building REST APIs with FastAPI in Python",
            "platform": "GeeksforGeeks",
            "skill": "FastAPI",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Quick tutorial on building and testing high-speed async microservices with Uvicorn.",
            "url": "https://www.geeksforgeeks.org/fastapi-introduction/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "3 hours (1 day)",
            "duration_hours": 3.0
        }
    ],
    "SQL": [
        {
            "title": "SQL Database Crash Course for Developers",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "SQL",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Complete core SQL: SELECT queries, WHERE filters, aggregate functions, and multi-table JOINs.",
            "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "resource_type": "Video",
            "is_free": True,
            "duration": "4.2 hours (< 1 day)",
            "duration_hours": 4.2
        },
        {
            "title": "SQL Interactive Exercises",
            "platform": "W3Schools",
            "skill": "SQL",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Quick self-paced exercises for mastering SQL syntax and subqueries in hours.",
            "url": "https://www.w3schools.com/sql/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "4 hours (1 day)",
            "duration_hours": 4.0
        },
        {
            "title": "Intro to SQL Micro-Course",
            "platform": "Kaggle Learn",
            "skill": "SQL",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Interactive notebook queries with BigQuery covering group by, joins, and indexing.",
            "url": "https://www.kaggle.com/learn/intro-to-sql",
            "resource_type": "Course",
            "is_free": True,
            "duration": "3 hours (< 1 day)",
            "duration_hours": 3.0
        }
    ],
    "PostgreSQL": [
        {
            "title": "PostgreSQL Quick Crash Course for Developers",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "PostgreSQL",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Postgres schema creation, relationships, foreign keys, transactions, and indexing.",
            "url": "https://www.youtube.com/watch?v=qw--VYLpxG4",
            "resource_type": "Video",
            "is_free": True,
            "duration": "4 hours (1 day)",
            "duration_hours": 4.0
        },
        {
            "title": "PostgreSQL Essentials in 3 Days",
            "platform": "PostgreSQL Tutorial",
            "skill": "PostgreSQL",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Hands-on guide to database administration, queries, and JSONB document storage.",
            "url": "https://www.postgresqltutorial.com/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "5 hours (2 days)",
            "duration_hours": 5.0
        }
    ],
    "Git": [
        {
            "title": "Git & GitHub Crash Course for Developers",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "Git",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Master branching, staging, commits, PR reviews, merge conflict resolution, and remotes.",
            "url": "https://www.youtube.com/watch?v=RGOj5yH7evk",
            "resource_type": "Video",
            "is_free": True,
            "duration": "1.2 hours (< 1 day)",
            "duration_hours": 1.2
        },
        {
            "title": "Git Fast Reference & Interactive Guide",
            "platform": "W3Schools",
            "skill": "Git",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Short cheatsheet-driven lessons explaining git workflows and commands.",
            "url": "https://www.w3schools.com/git/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "2 hours (1 day)",
            "duration_hours": 2.0
        }
    ],
    "Docker": [
        {
            "title": "Docker in 3 Hours – Fast-Track Containerization",
            "platform": "TechWorld with Nana (YouTube)",
            "skill": "Docker",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Dockerfiles, container lifecycles, volumes, network bridging, and docker-compose orchestration.",
            "url": "https://www.youtube.com/watch?v=3c-iBn73dDE",
            "resource_type": "Video",
            "is_free": True,
            "duration": "3 hours (< 1 day)",
            "duration_hours": 3.0
        },
        {
            "title": "Docker Hands-On Quickstart",
            "platform": "Docker Docs",
            "skill": "Docker",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Step-by-step practical guide to dockerizing a backend web app in under 2 hours.",
            "url": "https://docs.docker.com/get-started/",
            "resource_type": "Documentation",
            "is_free": True,
            "duration": "2 hours (1 day)",
            "duration_hours": 2.0
        }
    ],
    "Linux": [
        {
            "title": "Linux Command Line in 4 Hours",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "Linux",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Core shell commands, navigation, pipes, chmod permissions, systemctl, and SSH.",
            "url": "https://www.youtube.com/watch?v=ZtqBQ68cfJc",
            "resource_type": "Video",
            "is_free": True,
            "duration": "4 hours (1-2 days)",
            "duration_hours": 4.0
        },
        {
            "title": "Linux Journey – Fast Track Command Line",
            "platform": "Linux Journey",
            "skill": "Linux",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Bite-sized visual modules covering process management and server troubleshooting.",
            "url": "https://linuxjourney.com/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "3 hours (1 day)",
            "duration_hours": 3.0
        }
    ],
    "Redis": [
        {
            "title": "Redis Crash Course – High-Speed In-Memory Caching",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "Redis",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Learn Redis data types, key expiration (TTL), pub/sub messaging, and caching with Python.",
            "url": "https://www.youtube.com/watch?v=jgpVdJB2sKQ",
            "resource_type": "Video",
            "is_free": True,
            "duration": "1.5 hours (< 1 day)",
            "duration_hours": 1.5
        },
        {
            "title": "Redis for Python Developers in 1 Day",
            "platform": "Redis Official Docs",
            "skill": "Redis",
            "skill_category": "Technical",
            "difficulty": "Intermediate",
            "description": "Fast tutorial showing how to use redis-py for caching API responses and session store.",
            "url": "https://redis.io/docs/latest/develop/connect/clients/python/",
            "resource_type": "Documentation",
            "is_free": True,
            "duration": "2.5 hours (1 day)",
            "duration_hours": 2.5
        }
    ],
    "AWS": [
        {
            "title": "AWS Cloud for Backend Developers – Fast Track",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "AWS",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Concise overview of EC2, S3, RDS, Lambda, and IAM needed for deploying web apps.",
            "url": "https://www.youtube.com/watch?v=k1RI5locZE4",
            "resource_type": "Video",
            "is_free": True,
            "duration": "4 hours (1-2 days)",
            "duration_hours": 4.0
        },
        {
            "title": "AWS Cloud Essentials Micro-Path",
            "platform": "AWS Skill Builder",
            "skill": "AWS",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Official interactive self-paced micro-course covering cloud architecture fundamentals.",
            "url": "https://explore.skillbuilder.aws/",
            "resource_type": "Course",
            "is_free": True,
            "duration": "3 hours (1 day)",
            "duration_hours": 3.0
        }
    ],
    "LangGraph": [
        {
            "title": "AI Agents with LangGraph – Rapid Short Course",
            "platform": "DeepLearning.AI",
            "skill": "LangGraph",
            "skill_category": "Technical",
            "difficulty": "Intermediate",
            "description": "Build stateful multi-agent workflows, cyclical execution, persistence, and agent handoffs.",
            "url": "https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/",
            "resource_type": "Course",
            "is_free": True,
            "duration": "1.5 hours (< 1 day)",
            "duration_hours": 1.5
        },
        {
            "title": "LangGraph Quickstart & State Persistence Guide",
            "platform": "LangChain Docs",
            "skill": "LangGraph",
            "skill_category": "Technical",
            "difficulty": "Intermediate",
            "description": "Official code-along guide for StateGraph, checkpoints, and multi-agent coordination.",
            "url": "https://langchain-ai.github.io/langgraph/",
            "resource_type": "Documentation",
            "is_free": True,
            "duration": "2.5 hours (1 day)",
            "duration_hours": 2.5
        }
    ],
    "Advanced RAG Optimization": [
        {
            "title": "Advanced Retrieval for AI – Speed & Latency Optimization",
            "platform": "DeepLearning.AI",
            "skill": "Advanced RAG Optimization",
            "skill_category": "Technical",
            "difficulty": "Intermediate",
            "description": "Sub-400ms query latency, semantic chunking, embedding caching, and re-ranking pipelines.",
            "url": "https://www.deeplearning.ai/short-courses/advanced-retrieval-for-ai/",
            "resource_type": "Course",
            "is_free": True,
            "duration": "1.2 hours (< 1 day)",
            "duration_hours": 1.2
        },
        {
            "title": "Optimizing RAG Performance & Token Budget",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "Advanced RAG Optimization",
            "skill_category": "Technical",
            "difficulty": "Intermediate",
            "description": "Master vector indexing caches, hybrid search (BM25 + Dense), and token economy.",
            "url": "https://www.youtube.com/watch?v=tcqEUSNCn8I",
            "resource_type": "Video",
            "is_free": True,
            "duration": "2.5 hours (1 day)",
            "duration_hours": 2.5
        }
    ],
    "Power BI": [
        {
            "title": "Power BI Quickstart for Beginners",
            "platform": "Microsoft Learn",
            "skill": "Power BI",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Fast-track data modeling, dashboard creation, and DAX calculations.",
            "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi",
            "resource_type": "Course",
            "is_free": True,
            "duration": "4 hours (1-2 days)",
            "duration_hours": 4.0
        }
    ],
    "Machine Learning": [
        {
            "title": "Intro to Machine Learning in 3 Hours",
            "platform": "Kaggle Learn",
            "skill": "Machine Learning",
            "skill_category": "Technical",
            "difficulty": "Beginner",
            "description": "Model validation, decision trees, random forests with interactive hands-on coding.",
            "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
            "resource_type": "Course",
            "is_free": True,
            "duration": "3 hours (< 1 day)",
            "duration_hours": 3.0
        }
    ],

    # ── SHORT-DURATION SOFT SKILLS (< 1 WEEK) ─────────────────────────────────
    "Communication": [
        {
            "title": "Technical Communication & Active Listening Crash Course",
            "platform": "YouTube (Career Skills)",
            "skill": "Communication",
            "skill_category": "Soft",
            "difficulty": "Beginner",
            "description": "Master concise technical explanations, active listening, and executive clarity for dev roles.",
            "url": "https://www.youtube.com/watch?v=SRvTfx_t9yA",
            "resource_type": "Video",
            "is_free": True,
            "duration": "1.5 hours (< 1 day)",
            "duration_hours": 1.5
        },
        {
            "title": "Professional Email & Workplace Communication",
            "platform": "TCS iON",
            "skill": "Communication",
            "skill_category": "Soft",
            "difficulty": "Beginner",
            "description": "Short module on communicating clearly with engineering managers and cross-functional teams.",
            "url": "https://learning.tcsionhub.in/hub/national/",
            "resource_type": "Course",
            "is_free": True,
            "duration": "3 hours (1 day)",
            "duration_hours": 3.0
        }
    ],
    "Team Collaboration": [
        {
            "title": "Agile Teamwork & Pull Request Collaboration in Tech",
            "platform": "freeCodeCamp (YouTube)",
            "skill": "Team Collaboration",
            "skill_category": "Soft",
            "difficulty": "Beginner",
            "description": "Effective code review culture, asynchronous collaboration, sprint rituals, and conflict handling.",
            "url": "https://www.youtube.com/watch?v=H7_4a3oXmHQ",
            "resource_type": "Video",
            "is_free": True,
            "duration": "1.2 hours (< 1 day)",
            "duration_hours": 1.2
        },
        {
            "title": "Cross-Functional Team Collaboration Masterclass",
            "platform": "TCS iON",
            "skill": "Team Collaboration",
            "skill_category": "Soft",
            "difficulty": "Beginner",
            "description": "Practical lessons on working with product managers, QA, and peers effectively.",
            "url": "https://learning.tcsionhub.in/hub/national/",
            "resource_type": "Course",
            "is_free": True,
            "duration": "2.5 hours (1 day)",
            "duration_hours": 2.5
        }
    ],
    "Stakeholder Communication & Business Impact": [
        {
            "title": "Explaining Tech to Non-Tech Stakeholders & The STAR Method",
            "platform": "YouTube (Tech Career Coach)",
            "skill": "Stakeholder Communication & Business Impact",
            "skill_category": "Soft",
            "difficulty": "Intermediate",
            "description": "How to translate technical downtime into business impact, cost, resolution timelines, and mitigation.",
            "url": "https://www.youtube.com/watch?v=8QM_F3K3rS0",
            "resource_type": "Video",
            "is_free": True,
            "duration": "45 mins (< 1 day)",
            "duration_hours": 0.75
        },
        {
            "title": "Executive Communication for Engineers",
            "platform": "Google Tech Writing / Docs",
            "skill": "Stakeholder Communication & Business Impact",
            "skill_category": "Soft",
            "difficulty": "Beginner",
            "description": "Structuring post-mortems and status updates using Situation, Task, Action, and Business Result (STAR).",
            "url": "https://developers.google.com/tech-writing",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "2 hours (1 day)",
            "duration_hours": 2.0
        }
    ],
    "Leadership": [
        {
            "title": "Engineering Leadership & Ownership in 2 Hours",
            "platform": "TCS iON",
            "skill": "Leadership",
            "skill_category": "Soft",
            "difficulty": "Beginner",
            "description": "Taking initiative, proactive mitigation suggestions, and driving technical solutions.",
            "url": "https://learning.tcsionhub.in/hub/national/",
            "resource_type": "Course",
            "is_free": True,
            "duration": "2 hours (1 day)",
            "duration_hours": 2.0
        }
    ],
    "Interview Skills": [
        {
            "title": "Ace Technical & Behavioral Interviews (STAR Framework)",
            "platform": "GeeksforGeeks",
            "skill": "Interview Skills",
            "skill_category": "Soft",
            "difficulty": "Beginner",
            "description": "Fast-track interview prep: common behavioral questions, structuring honest answers, and follow-ups.",
            "url": "https://www.geeksforgeeks.org/company-interview-corner/",
            "resource_type": "Tutorial",
            "is_free": True,
            "duration": "3 hours (1 day)",
            "duration_hours": 3.0
        }
    ]
}

FALLBACK_RESOURCES = {
    "technical": {
        "title": "Crash Course & Practice – GeeksforGeeks",
        "platform": "GeeksforGeeks",
        "skill_category": "Technical",
        "difficulty": "Beginner",
        "description": "Quick tutorial with targeted concepts and code examples.",
        "url": "https://www.geeksforgeeks.org/",
        "resource_type": "Tutorial",
        "is_free": True,
        "duration": "3 hours (1 day)",
        "duration_hours": 3.0
    },
    "soft": {
        "title": "Quick Professional Skills Module – TCS iON",
        "platform": "TCS iON",
        "skill_category": "Soft",
        "difficulty": "Beginner",
        "description": "Micro-learning module for professional communication.",
        "url": "https://learning.tcsionhub.in/hub/national/",
        "resource_type": "Course",
        "is_free": True,
        "duration": "2 hours (1 day)",
        "duration_hours": 2.0
    }
}


def get_courses_for_skill(skill: str, level: str = "Beginner") -> list:
    """Get course recommendations for a single skill (< 1 week)."""
    courses = COURSE_DATA.get(skill, [])

    if not courses:
        for key in COURSE_DATA:
            if key.lower() == skill.lower():
                courses = COURSE_DATA[key]
                break

    if not courses:
        for key in COURSE_DATA:
            if key.lower() in skill.lower() or skill.lower() in key.lower():
                courses = COURSE_DATA[key]
                break

    return courses


def suggest_courses(input_data: dict) -> dict:
    """
    Takes skill gap input from Resume + Interview and produces short-duration (< 1 week)
    courses prioritized into recommended (Priority 1) and options.
    """
    technical_skills = input_data.get("technical_skills", [])
    soft_skills      = input_data.get("soft_skills", [])
    skill_levels     = input_data.get("skill_levels", {})
    target_job_role  = input_data.get("target_job_role", "")
    candidate_name   = input_data.get("candidate_name", "")
    sources_used     = input_data.get("sources_used", ["resume_gap", "interview_gap"])

    tech_recommendations = []
    soft_recommendations = []
    seen_urls = set()

    # ── Technical Skills ──────────────────────────────────────────────────────
    for skill in technical_skills:
        level = skill_levels.get(skill, "Beginner")
        courses = get_courses_for_skill(skill, level)

        if not courses:
            fallback = dict(FALLBACK_RESOURCES["technical"])
            fallback["title"] = f"{skill} Quickstart Crash Course"
            fallback["skill"] = skill
            fallback["url"]   = f"https://www.geeksforgeeks.org/{skill.lower().replace(' ', '-')}/"
            courses = [fallback]

        for course in courses:
            url = course.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                tech_recommendations.append({
                    **course,
                    "skill": skill,
                    "under_one_week": True
                })

    # ── Soft Skills ───────────────────────────────────────────────────────────
    for skill in soft_skills:
        level = skill_levels.get(skill, "Beginner")
        courses = get_courses_for_skill(skill, level)

        if not courses:
            fallback = dict(FALLBACK_RESOURCES["soft"])
            fallback["title"] = f"{skill} Fast Mastery"
            fallback["skill"] = skill
            courses = [fallback]

        for course in courses:
            url = course.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                soft_recommendations.append({
                    **course,
                    "skill": skill,
                    "under_one_week": True
                })

    # ── Group by skill: 1st = recommended (Priority 1), rest = options ──────
    def group_by_skill(recommendations):
        grouped = {}
        for course in recommendations:
            skill = course["skill"]
            if skill not in grouped:
                grouped[skill] = []
            grouped[skill].append(course)

        result = []
        for skill, courses in grouped.items():
            recommended = {
                **courses[0],
                "priority": 1,
                "highly_suggested": True,
                "under_one_week": True
            }
            options = [
                {**c, "priority": i + 2, "highly_suggested": False, "under_one_week": True}
                for i, c in enumerate(courses[1:])
            ]
            result.append({
                "skill": skill,
                "skill_category": courses[0]["skill_category"],
                "recommended": recommended,
                "options": options,
                "total_options_count": len(options)
            })
        return result

    tech_grouped = group_by_skill(tech_recommendations)
    soft_grouped = group_by_skill(soft_recommendations)

    all_skills = list(set(
        [r["skill"] for r in tech_recommendations] +
        [r["skill"] for r in soft_recommendations]
    ))

    total = len(tech_recommendations) + len(soft_recommendations)

    output = {
        "agent": "Agent 3 - Course Suggestion Agent",
        "status": "success",
        "candidate_name": candidate_name,
        "target_job_role": target_job_role,
        "duration_filter": "All resources strictly < 1 week (crash courses & micro-learning for 30-day planner)",
        "input_summary": {
            "sources_merged": sources_used,
            "technical_skills_requested": technical_skills,
            "soft_skills_requested": soft_skills,
            "skill_levels": skill_levels
        },
        "technical_recommendations": tech_grouped,
        "soft_recommendations": soft_grouped,
        "metadata": {
            "total_resources": total,
            "technical_count": len(tech_recommendations),
            "soft_count": len(soft_recommendations),
            "skills_covered": all_skills,
            "skills_covered_count": len(all_skills),
            "max_course_duration": "< 1 week (1 to 6 hours average)",
            "all_under_one_week": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "for_agent5": True
        }
    }
    return output


def load_from_gap_files(resume_file: str = "resume_gap.json", interview_file: str = "interview_gap.json") -> dict:
    """Reads both resume_gap.json and interview_gap.json and merges their gaps."""
    tech_skills = []
    soft_skills = []
    skill_levels = {}
    target_role = "Python Backend Developer / AI Engineer"
    candidate_name = ""
    sources_used = []

    # 1. Read Resume Gap file if present
    if os.path.exists(resume_file):
        try:
            with open(resume_file, "r", encoding="utf-8") as f:
                rdata = json.load(f)
            sources_used.append("resume_gap.json")
            candidate_name = rdata.get("candidate_name", candidate_name)
            target_role = rdata.get("target_job_title", target_role)
            data_body = rdata.get("data", {})

            crit = data_body.get("critical_gaps", [])
            imp = data_body.get("important_gaps", [])
            for s in crit:
                if s not in tech_skills:
                    tech_skills.append(s)
                    skill_levels[s] = "Critical Gap"
            for s in imp:
                if s not in tech_skills:
                    tech_skills.append(s)
                    skill_levels[s] = "Important Gap"

            soft_analysis = data_body.get("soft_skills_analysis", {})
            for s in soft_analysis.get("missing_soft_skills", []):
                if s not in soft_skills:
                    soft_skills.append(s)
                    skill_levels[s] = "Missing"
        except Exception as e:
            print(f"[WARN] Error reading {resume_file}: {e}")

    # 2. Read Interview Gap file if present
    if os.path.exists(interview_file):
        try:
            with open(interview_file, "r", encoding="utf-8") as f:
                idata = json.load(f)
            sources_used.append("interview_gap.json")
            if not target_role or target_role == "Python Backend Developer":
                target_role = f"{target_role} | {idata.get('role', 'AI Engineer')}"
            
            idata_body = idata.get("data", {})
            tech_eval = idata_body.get("technical_evaluation", {})
            
            for gap in tech_eval.get("critical_technical_gaps", []):
                if "langgraph" in gap.lower():
                    if "LangGraph" not in tech_skills:
                        tech_skills.append("LangGraph")
                        skill_levels["LangGraph"] = "Critical Gap (Interview)"

            for top in tech_eval.get("priority_technical_topics_to_learn", []):
                if "rag" in top.lower():
                    if "Advanced RAG Optimization" not in tech_skills:
                        tech_skills.append("Advanced RAG Optimization")
                        skill_levels["Advanced RAG Optimization"] = "High Priority (Interview)"

            soft_eval = idata_body.get("soft_skills_evaluation", {})
            if soft_eval.get("critical_soft_skill_gaps"):
                st_skill = "Stakeholder Communication & Business Impact"
                if st_skill not in soft_skills:
                    soft_skills.append(st_skill)
                    skill_levels[st_skill] = "Needs Improvement (STAR Method)"

        except Exception as e:
            print(f"[WARN] Error reading {interview_file}: {e}")

    return {
        "technical_skills": tech_skills,
        "soft_skills": soft_skills,
        "skill_levels": skill_levels,
        "target_job_role": target_role,
        "candidate_name": candidate_name,
        "sources_used": sources_used
    }


def save_output(output: dict, filename: str = "agent3_output.json"):
    """Save JSON output locally and into shared_output for Agent 5."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    shared_dir = os.path.join(os.path.dirname(__file__), "..", "shared_output")
    os.makedirs(shared_dir, exist_ok=True)
    shared_path = os.path.join(shared_dir, "agent3_courses.json")
    with open(shared_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return filename, shared_path


def main():
    parser = argparse.ArgumentParser(description="Agent 3: Course Suggestion Agent (< 1 Week Courses)")
    parser.add_argument("--resume", default="resume_gap.json", help="Path to resume_gap.json")
    parser.add_argument("--interview", default="interview_gap.json", help="Path to interview_gap.json")
    parser.add_argument("--input", "-i", default=None, help="Single input JSON file")
    parser.add_argument("--output", "-o", default="agent3_output.json", help="Output JSON path")
    args = parser.parse_args()

    print("\n[INFO] Agent 3 -- Course Suggestion Agent (< 1 Week Courses) starting...")

    if args.input:
        print(f"[INFO] Reading single input: {args.input}")
        with open(args.input, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if "data" in raw:
            input_data = load_from_gap_files(args.input, "")
        else:
            input_data = raw
    else:
        print(f"[INFO] Checking for input files: {args.resume} & {args.interview}")
        input_data = load_from_gap_files(args.resume, args.interview)

    print(f"[INFO] Generating < 1 week recommendations for {len(input_data['technical_skills'])} Tech & {len(input_data['soft_skills'])} Soft skills...")
    output = suggest_courses(input_data)

    print("\n--- AGENT 3 JSON OUTPUT (< 1 WEEK COURSES) ---\n")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print("\n--- END OF OUTPUT ---")

    local_path, shared_path = save_output(output, args.output)
    print(f"\n[SAVED] {local_path}")
    print(f"[SAVED] {shared_path} (For Agent 5 - 30-Day Planner)")
    print(f"[SUMMARY] Total Resources: {output['metadata']['total_resources']} (All strictly < 1 week)")


if __name__ == "__main__":
    main()
