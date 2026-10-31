"""
Agent 5 - Plan Generator Module
Builds a 30-day personalized learning schedule from gap-analysis + course data.

Features:
  1. Each skill has learning days followed by exactly 1 dedicated Project Day.
  2. Project is an entire day in the schedule, NOT a separate column.
  3. No duration mentions.
  4. 4-Phase logical progression (Fundamentals -> Intermediate -> Advanced -> Capstone).
"""

from __future__ import annotations
import math
from typing import Any

# ---------------------------------------------------------------------------
# Dedicated Project Bank per skill (1 dedicated full-day project per skill)
# ---------------------------------------------------------------------------
SKILL_PROJECTS = {
    "Machine Learning": [
        "Customer Churn Prediction Model & Pipeline",
        "Predictive House Price Regression Engine",
        "Credit Risk Classification & Evaluation Suite",
    ],
    "Power BI": [
        "Interactive Executive Sales Performance Dashboard",
        "Comprehensive HR Analytics & Retention KPI Report",
        "Regional Revenue & Customer Cohort BI Dashboard",
    ],
    "SQL": [
        "E-Commerce Multi-Table Analytics Query Suite",
        "Customer Retention & Cohort Analysis Database Queries",
        "Executive KPI & Revenue Trend SQL Reports",
    ],
    "Python": [
        "Automated Data Cleaning & ETL Pipeline Script",
        "Web Scraping & Structured CSV Extraction System",
        "Exploratory Data Analysis & Automated PDF Summary Generator",
    ],
    "FastAPI": [
        "Production REST API with JWT Auth, Pydantic & PostgreSQL",
        "High-Concurrency Async Microservice with Background Tasks",
        "FastAPI Service with Swagger Docs & Rate Limiting",
    ],
    "PostgreSQL": [
        "Relational Database Schema Design with Foreign Keys & Indexes",
        "ACID Transactions, Stored Procedures & Query Optimization",
        "PostgreSQL Full-Text Search & JSONB Document Queries",
    ],
    "Docker": [
        "Multi-Stage Dockerfile & Containerized Backend Service",
        "Docker Compose Multi-Container Setup (FastAPI + Postgres + Redis)",
        "Production Container Optimization & Volume Management",
    ],
    "Linux": [
        "Automated Bash Server Setup & Deployment Script",
        "Linux Process Monitoring, Cron Jobs & SSH Key Hardening",
        "Systemd Service Daemon & Nginx Reverse Proxy Config",
    ],
    "Redis": [
        "High-Speed API Response Caching & TTL Expiration Layer",
        "Redis Pub/Sub Message Queue & Rate Limiter for APIs",
        "In-Memory Session Store & Cache Invalidation Pipeline",
    ],
    "AWS": [
        "Deploy FastAPI App to AWS EC2 with RDS & S3 Storage",
        "Serverless AWS Lambda Function with API Gateway & IAM",
        "Cloud Architecture Deployment with CloudWatch Logging",
    ],
    "LangGraph": [
        "Stateful Multi-Agent AI Workflow with Cyclical Execution",
        "Multi-Agent Research Assistant with Human-in-the-Loop",
        "Autonomous Agent Architecture with State Checkpoints",
    ],
    "Advanced RAG Optimization": [
        "High-Speed Hybrid Search Pipeline (Dense + BM25) with Re-Ranking",
        "Sub-400ms Query Latency RAG Engine with Semantic Chunking",
        "Token-Budget-Optimized Context Compression RAG System",
    ],
    "Git": [
        "Production Multi-Branch Git Flow & Pull Request Template",
        "Merge Conflict Resolution & Interactive Rebase Workflow",
    ],
    "Communication": [
        "Executive Data Storytelling Slide Deck & Brief",
        "Business KPI Insight Memo for Senior Stakeholders",
        "Data Dictionary & Technical Project Documentation",
    ],
    "Team Collaboration": [
        "Agile Sprint Planning, PR Code Review Checklist & Retrospective",
        "Asynchronous Developer Collaboration & Issue Triage Guide",
    ],
    "Stakeholder Communication & Business Impact": [
        "STAR-Method Business Impact Brief on Tech Incident & Resolution",
        "Translating Architectural Technical Debt to Business ROI Deck",
    ],
    "Leadership": [
        "Project Charter, Agile Sprint Roadmap & Risk Matrix",
        "Cross-Functional Team Retrospective & Decision Framework",
        "Strategic Problem-Solving Case Study & Action Plan",
    ],
    "Interview Skills": [
        "Comprehensive Analytics Mock Interview & Problem Defense",
        "STAR-Method Behavioral Portfolio & Resume Showcase",
        "Technical Case Study: Diagnosing Metric Anomalies",
    ],
    "NumPy": [
        "Scientific Matrix Computations & Image Grayscale Engine",
    ],
    "Pandas": [
        "End-to-End Data Wrangling & Automated Quality Audit",
    ],
    "Data Visualization (Matplotlib & Seaborn)": [
        "Multi-Metric Visual Analytics Dashboard & Infographic",
    ],
    "Statistics & Probability": [
        "Hypothesis Testing & Statistical Distribution Modeling Suite",
    ],
    "Data Structures": [
        "Custom Stack, Queue & Graph Traversal Implementation",
    ],
    "Algorithms": [
        "Search & Sorting Algorithm Benchmarking Toolkit",
    ],
    "Version Control (Git)": [
        "Multi-Branch Git Workflow & Open-Source Collaboration Repo",
    ],
}

# Sub-topics to explore during learning days before the project day
SKILL_MODULES = {
    "Machine Learning": [
        "Core Concepts, Model Life-cycle & Problem Framing",
        "Supervised Learning: Regression, Trees & Classification",
        "Model Evaluation Metrics, Overfitting & Validation",
    ],
    "Power BI": [
        "Data Ingestion, Schema Modeling & Table Relationships",
        "DAX Measures, Calculated Columns & Quick Calculations",
        "Visual Reporting, Slicers & Page Interaction Design",
    ],
    "SQL": [
        "Relational Querying: SELECT, Filtering & Aggregations",
        "Advanced JOINs, Subqueries & Common Table Expressions",
        "Window Functions: Ranking, Partitions & Running Totals",
    ],
    "FastAPI": [
        "Path Operations, Pydantic Models & Request Validation",
        "Dependency Injection, JWT Authentication & Security",
    ],
    "PostgreSQL": [
        "Schema Design, Constraints, Indexes & Normalization",
        "Transactions, Query Execution Plans & Performance Tuning",
    ],
    "Docker": [
        "Dockerfiles, Image Building, Layers & Port Mapping",
        "Docker Compose, Multi-Service Networking & Volumes",
    ],
    "Linux": [
        "Command Line Mastery: Pipes, Redirection & Permissions",
        "Process Management, Systemd Daemons, Cron & SSH",
    ],
    "Redis": [
        "In-Memory Data Structures, Key Expiration & TTL",
        "Caching Strategies, Invalidation & Pub/Sub Messaging",
    ],
    "AWS": [
        "Cloud Core: EC2 Compute, S3 Storage & VPC Networking",
        "Managed Databases (RDS), IAM Security Roles & Lambda",
    ],
    "LangGraph": [
        "StateGraph Architecture, Nodes, Edges & State Schemas",
        "Persistence, Memory Checkpointers & Multi-Agent Coordination",
    ],
    "Advanced RAG Optimization": [
        "Semantic Chunking Strategies, Metadata Enrichment & Embeddings",
        "Hybrid Search (Dense + Sparse), Cross-Encoder Re-Ranking & Latency",
    ],
    "Git": [
        "Branching Workflows, Staging, Merge Strategies & Conflicts",
        "Interactive Rebasing, Pull Request Reviews & Remote Sync",
    ],
    "Team Collaboration": [
        "Code Review Culture, Pull Request Etiquette & Branch Policies",
        "Agile Sprint Ceremonies, Backlog Refinement & Async Comms",
    ],
    "Stakeholder Communication & Business Impact": [
        "Translating Technical Metrics to Business ROI & Stakeholder Alignment",
        "Incident Management, Post-Mortems & Executive Reporting with STAR",
    ],
    "Python": [
        "Core Syntax, Data Structures & Modular Functions",
        "Data Manipulation with Pandas & NumPy Arrays",
        "Exploratory Data Analysis & Statistical Profiling",
    ],
    "Communication": [
        "Principles of Data Storytelling & Visual Encoding",
        "Stakeholder Communication & Technical Documentation",
    ],
    "Leadership": [
        "Project Scoping, Agile Workflows & Sprint Planning",
        "Team Retrospectives, Decision Matrices & Consensus",
    ],
    "Interview Skills": [
        "Technical Analytics Problem Solving & SQL Drills",
        "Behavioral STAR Method & Scenario-Based Questions",
    ],
}

DEFAULT_RESOURCES = {
    "default": {
        "priority_link": "https://www.geeksforgeeks.org/",
        "optional_link": "https://www.freecodecamp.org/",
        "rec_title": "GeeksforGeeks Guide",
        "opt_title": "freeCodeCamp Tutorial",
    }
}

PHASES = {
    (1,  7):  "Phase 1 - Fundamentals & Core Skill Acquisition",
    (8,  14): "Phase 2 - Intermediate Concepts & Practical Hands-on",
    (15, 21): "Phase 3 - Advanced Problem Solving & Tool Mastery",
    (22, 30): "Phase 4 - Capstone Integration, Revision & Interview Readiness",
}


def _get_phase(day: int) -> str:
    for (start, end), label in PHASES.items():
        if start <= day <= end:
            return label
    return "Phase 4 - Capstone Integration, Revision & Interview Readiness"


def _clean_title(title: str, default: str) -> str:
    """Remove any duration or week references from course titles."""
    if not title:
        return default
    bad_phrases = ["(< 1 Week)", "(< 1 week)", "< 1 Week", "< 1 week", "4.5 hours", "8 hours", "3 hours", "6 hours", "12 weeks", "8 weeks"]
    cleaned = title
    for b in bad_phrases:
        cleaned = cleaned.replace(b, "")
    cleaned = cleaned.strip(" -:,()")
    return cleaned if cleaned else default


def _get_course_details(skill: str, agent3_data: dict[str, Any]) -> dict[str, str]:
    clean_skill = skill.replace("Revision: ", "").replace("Project Day: ", "").strip()
    if clean_skill in agent3_data:
        rec = agent3_data[clean_skill]
        rec_title = _clean_title(rec.get("rec_title", ""), rec.get("rec_platform", "Official Course"))
        opt_title = _clean_title(rec.get("opt_title", ""), rec.get("opt_platform", "Reference Tutorial"))
        return {
            "priority_link": rec.get("priority_link", DEFAULT_RESOURCES["default"]["priority_link"]),
            "optional_link": rec.get("optional_link", DEFAULT_RESOURCES["default"]["optional_link"]),
            "rec_title": rec_title,
            "opt_title": opt_title,
        }
    return DEFAULT_RESOURCES["default"]


def generate_30_day_plan(
    missing_skills: list[str],
    skill_priority: dict[str, str],
    agent3_data: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Generate exactly 30 entries where:
      - Each skill has structured learning days followed immediately by 1 dedicated Project Day.
      - Projects do NOT live in a column; they occupy their own dedicated day row.
      - No duration is mentioned anywhere.
    """
    if not missing_skills:
        missing_skills = ["Machine Learning", "Power BI", "SQL", "Python", "Communication", "Leadership", "Interview Skills"]

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_skills = sorted(
        missing_skills,
        key=lambda s: priority_order.get(skill_priority.get(s, "Medium"), 1),
    )

    TOTAL_DAYS = 30
    schedule: list[dict[str, Any]] = []
    day = 1
    num_skills = len(sorted_skills)

    # We reserve at least 2 days for final Capstone project
    min_capstone_days = 2
    max_days_for_skills = TOTAL_DAYS - min_capstone_days # e.g. 28

    # If there are many skills (e.g. 14):
    # Each skill takes 1 learning day + 1 project day = 2 days
    if num_skills * 2 >= max_days_for_skills:
        # Cap skills to what fits or 1 learn + 1 project day each
        # 14 skills * 2 = 28 days
        skill_learning_days = {s: 1 for s in sorted_skills}
    else:
        # We have room for multiple learning days per skill
        # Each skill takes 1 project day, so remaining days go to learning
        available_learning = max_days_for_skills - num_skills
        base_learn = available_learning // num_skills
        rem_learn = available_learning % num_skills
        skill_learning_days = {}
        for idx, s in enumerate(sorted_skills):
            skill_learning_days[s] = base_learn + (1 if idx < rem_learn else 0)

    for skill in sorted_skills:
        if day > TOTAL_DAYS - min_capstone_days:
            break

        learn_count = skill_learning_days.get(skill, 1)
        courses = _get_course_details(skill, agent3_data)
        
        submodules = SKILL_MODULES.get(skill, [
            f"Core Concepts, Architecture & Best Practices",
            f"Applied Implementation & Configuration",
            f"Advanced Optimization & Production Workflows",
        ])

        # 1. Learning Day(s)
        for l_idx in range(learn_count):
            if day > TOTAL_DAYS - min_capstone_days:
                break
            mod_title = submodules[l_idx % len(submodules)]
            schedule.append({
                "day": str(day),
                "phase": _get_phase(day),
                "skill": f"{skill}: {mod_title}",
                "is_project_day": False,
                "priority_link": courses["priority_link"],
                "optional_link": courses["optional_link"],
                "rec_title": courses["rec_title"],
                "opt_title": courses["opt_title"],
            })
            day += 1

        # 2. Dedicated 1-Day Project for this skill
        if day <= TOTAL_DAYS - min_capstone_days + 1:
            project_options = SKILL_PROJECTS.get(skill, [f"Practical End-to-End {skill} Application"])
            proj_title = project_options[0]
            schedule.append({
                "day": str(day),
                "phase": _get_phase(day),
                "skill": f"[Project Day] {skill} - {proj_title}",
                "is_project_day": True,
                "priority_link": courses["priority_link"],
                "optional_link": courses["optional_link"],
                "rec_title": f"{courses['rec_title']} (Project Guide)",
                "opt_title": f"{courses['opt_title']} (Reference Code)",
            })
            day += 1

    # Remaining days up to 30: Capstone Project & Portfolio Defense
    capstone_modules = [
        ("Capstone Project (Phase 1)", "End-to-End Multi-Tier Architecture & Database Schema Design"),
        ("Capstone Project (Phase 2)", "High-Concurrency Backend Microservice & AI Agent Integration"),
        ("Capstone Project (Phase 3)", "Caching, Vector Search & Production Containerization"),
        ("Capstone Project (Phase 4)", "Cloud Deployment, Stress Testing & CI/CD Pipeline"),
        ("Final Portfolio Showcase", "GitHub Repository Deployment & Technical Defense"),
    ]

    cap_idx = 0
    while day <= TOTAL_DAYS:
        cap_phase, cap_desc = capstone_modules[cap_idx % len(capstone_modules)]
        top_skill = sorted_skills[0] if sorted_skills else "Python"
        top_courses = _get_course_details(top_skill, agent3_data)

        schedule.append({
            "day": str(day),
            "phase": _get_phase(day),
            "skill": f"[{cap_phase}] {cap_desc}",
            "is_project_day": True,
            "priority_link": top_courses["priority_link"],
            "optional_link": top_courses["optional_link"],
            "rec_title": "Capstone Implementation Guide",
            "opt_title": "Project Documentation & Reference",
        })
        day += 1
        cap_idx += 1

    assert len(schedule) == TOTAL_DAYS, f"Expected 30 entries, got {len(schedule)}"
    return schedule
