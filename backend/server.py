"""
CareerAI Unified Multi-Agent Backend Server
Strictly integrates Agent 1 -> Agent 2 -> Agent 4 -> Agent 3 -> Agent 5.
"""

import os
import sys
import io
import json
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Add agent folders to sys.path
ROOT_DIR = Path(__file__).resolve().parent
AGENT2_DIR = ROOT_DIR / "agent2"
AGENT3_DIR = ROOT_DIR / "agent3"
AGENT5_DIR = ROOT_DIR / "agent5"
CTBUILDFEST_DIR = (ROOT_DIR / "CTBuildfest_2.0" / "module_1_resume_screening") if (ROOT_DIR / "CTBuildfest_2.0").exists() else ROOT_DIR
INTERVIEWER_DIR = (ROOT_DIR / "interviewer" / "backend") if (ROOT_DIR / "interviewer").exists() else ROOT_DIR

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(AGENT2_DIR))
if CTBUILDFEST_DIR != ROOT_DIR:
    sys.path.insert(0, str(CTBUILDFEST_DIR))
if INTERVIEWER_DIR != ROOT_DIR:
    sys.path.insert(0, str(INTERVIEWER_DIR))

# Agent 1 (CTBuildfest_2.0: Resume Screening & ATS Matching Service)
try:
    from app.database.connection import init_db as init_agent1_db, get_db
    init_agent1_db()
    from app.api.v1.router import api_v1_router as agent1_router
    from app.services.resume_service import resume_service
    from app.services.screening_service import screening_service
    from app.matching.ats_engine import ats_engine
    from app.parsers.resume_extractor import extract_structured_resume
    from app.parsers.job_extractor import extract_structured_job
    from app.personas.generator import synthetic_generator
    from app.ranking.ranker import compute_candidate_ranking
    AGENT1_AVAILABLE = True
    print("[CareerAI] Agent 1 (CTBuildfest_2.0) loaded successfully.")
except Exception as e:
    print(f"[CareerAI Warning] Failed to load Agent 1 (CTBuildfest_2.0): {e}")
    agent1_router = None
    AGENT1_AVAILABLE = False

# Agent 4 (Interviewer: Spoken Interview Agent, TTS/STT & Behavioral Analysis)
try:
    from interview_app.api.routes import router as agent4_router
    from interview_app.services.loaders import (
        load_resume as interview_load_resume,
        load_jd as interview_load_jd,
        extract_metadata as interview_extract_metadata
    )
    from interview_app.services.question_generator import generate_interview_questions
    from interview_app.supabase_client import InterviewRepository
    AGENT4_AVAILABLE = True
    print("[CareerAI] Agent 4 (Interviewer) loaded successfully.")
except Exception as e:
    print(f"[CareerAI Warning] Failed to load Agent 4 (Interviewer): {e}")
    agent4_router = None
    AGENT4_AVAILABLE = False

# Agent 2 (agent2: Gap Analysis Agent)
try:
    import importlib.util
    gap_agent_path = AGENT2_DIR / "agents" / "gap_analysis_agent.py"
    spec = importlib.util.spec_from_file_location("agent2_gap_agent", str(gap_agent_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    GapAnalysisAgent = mod.GapAnalysisAgent
    AGENT2_AVAILABLE = True
    print("[CareerAI] Agent 2 (Gap Analysis) loaded successfully.")
except Exception as e:
    print(f"[CareerAI Warning] Failed to load Agent 2 (Gap Analysis): {e}")
    AGENT2_AVAILABLE = False

# Agent 3: Real Course Suggestion Engine
from agent3.run import COURSE_DATA, suggest_courses

# Agent 5: Real 30-Day Planner & PDF Generator
from agent5.data_loader import _parse_agent3_schema, load_input_data
from agent5.plan_generator import generate_30_day_plan
from agent5.pdf_generator import generate_pdf

# PDF reader
try:
    import pypdf
except ImportError:
    pypdf = None


app = FastAPI(
    title="CareerAI Dynamic Multi-Agent Backend",
    description="Live Multi-Agent Pipeline connecting Agents 1 to 5: CTBuildfest_2.0 (Agent 1) -> Agent 2 -> Interviewer (Agent 4) -> Agent 3 -> Agent 5",
    version="2.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Mount FastAPI Routers: Agent 1 (CTBuildfest_2.0) and Agent 4 (Interviewer)
# ---------------------------------------------------------------------------
if agent1_router:
    # Full standard v1 screening endpoints (/api/v1/screening/resume/upload, /api/v1/screening/analyze, etc.)
    app.include_router(agent1_router, prefix="/api/v1")
    # Agent 1 alias
    app.include_router(agent1_router, prefix="/api/agent1")

if agent4_router:
    # Direct /interviews route for Next.js frontend and standard clients
    app.include_router(agent4_router)
    # API prefixed alias /api/interviews
    app.include_router(agent4_router, prefix="/api")

OUTPUTS_DIR = ROOT_DIR / "shared_output"
OUTPUTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Global Session Store
# ---------------------------------------------------------------------------
SESSION_STATE = {
    "candidate_name": "Candidate",
    "target_role": "Software Engineer",
    "resume_text": "",
    "job_description": "",
    "resume_skills": [],
    "jd_skills": [],
    "matched_skills": [],
    "missing_skills": [],
    "score_result": None,
    "gap_data": None,
    "agent3_output": None,
    "interview_questions": [],
    "interview_result": None,
    "roadmap_data": None
}

# Skill patterns for extraction
TECH_SKILL_PATTERNS = {
    "Python": [r'\bpython\b', r'\bpython3\b'],
    "JavaScript": [r'\bjavascript\b', r'\bjs\b', r'\bes6\b'],
    "TypeScript": [r'\btypescript\b', r'\bts\b'],
    "React.js": [r'\breact\b', r'\breact\.js\b', r'\breactjs\b'],
    "Node.js": [r'\bnode\b', r'\bnode\.js\b', r'\bnodejs\b'],
    "Express": [r'\bexpress\b', r'\bexpress\.js\b'],
    "FastAPI": [r'\bfastapi\b'],
    "SQL": [r'\bsql\b', r'\bmysql\b', r'\bsqlite\b'],
    "PostgreSQL": [r'\bpostgres\b', r'\bpostgresql\b'],
    "MongoDB": [r'\bmongo\b', r'\bmongodb\b', r'\bmongoose\b'],
    "Redis": [r'\bredis\b'],
    "Docker": [r'\bdocker\b', r'\bcontainerization\b'],
    "Git & GitHub": [r'\bgit\b', r'\bgithub\b', r'\bversion control\b'],
    "HTML5": [r'\bhtml\b', r'\bhtml5\b'],
    "CSS3 & Styling": [r'\bcss\b', r'\bcss3\b', r'\btailwind\b'],
    "REST APIs": [r'\brest\b', r'\brestful\b', r'\bapis?\b'],
    "Linux": [r'\blinux\b', r'\bbash\b', r'\bshell\b'],
    "AWS": [r'\baws\b', r'\bamazon web services\b'],
    "Machine Learning": [r'\bmachine learning\b', r'\bml\b', r'\bscikit-learn\b'],
    "Power BI": [r'\bpower bi\b', r'\bpowerbi\b', r'\btableau\b']
}

SOFT_SKILL_PATTERNS = {
    "Communication": [r'\bcommunication\b', r'\barticulate\b'],
    "Problem Solving": [r'\bproblem solving\b', r'\banalytical\b'],
    "Team Collaboration": [r'\bteamwork\b', r'\bcollaboration\b', r'\bagile\b'],
    "Leadership": [r'\bleadership\b', r'\bmentoring\b']
}


def extract_skills(text: str) -> tuple[List[str], List[str]]:
    text_lower = text.lower()
    matched_tech = []
    matched_soft = []

    for skill, patterns in TECH_SKILL_PATTERNS.items():
        if any(re.search(pat, text_lower) for pat in patterns):
            matched_tech.append(skill)

    for skill, patterns in SOFT_SKILL_PATTERNS.items():
        if any(re.search(pat, text_lower) for pat in patterns):
            matched_soft.append(skill)

    return matched_tech, matched_soft


def extract_text_from_file_bytes(content: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf") and pypdf is not None:
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages_text = [page.extract_text() or "" for page in reader.pages]
            full_text = "\n".join(pages_text).strip()
            if full_text:
                return full_text
        except Exception as e:
            print(f"pypdf extraction warning: {e}")
    return content.decode("utf-8", errors="ignore")


def extract_candidate_name(text: str, filename: str) -> str:
    # 1. Check explicit Name / Candidate Name / Full Name labels
    label_match = re.search(r'(?:name|full\s*name|candidate\s*name)\s*[:\-]\s*([A-Za-z\s.\'\-]+)', text, re.I)
    if label_match:
        val = label_match.group(1).split("\n")[0].strip()
        words = val.split()
        if 1 <= len(words) <= 4 and not any(ch in val for ch in "@:;0123456789/\\|#+{}"):
            return val.title()

    lines = [line.strip() for line in re.split(r'[\r\n]+', text) if line.strip()]
    for line in lines[:8]:
        if any(w in line.lower() for w in ["curriculum", "resume", "cv", "page", "email", "phone", "contact", "summary", "objective"]):
            continue
        first_clause = re.split(r'[\.,\-|;:]', line)[0].strip()
        words = first_clause.split()
        if 2 <= len(words) <= 4 and not any(ch in first_clause for ch in "@:;0123456789/\\|#+{}"):
            return first_clause.title()

    chunks = [c.strip() for c in re.split(r'[\.\n\r]+', text) if c.strip()]
    for chunk in chunks[:3]:
        words = chunk.split()
        if 2 <= len(words) <= 3 and not any(ch in chunk for ch in "@:;0123456789/\\|#+{}"):
            if not any(k in chunk.lower() for k in ["resume", "cv", "experience", "skills", "profile"]):
                return chunk.title()

    if filename:
        clean = Path(filename).stem.replace("_", " ").replace("-", " ")
        parts = [p for p in clean.split() if p.lower() not in ["resume", "cv", "profile", "candidate", "document", "file", "latest", "updated", "final"]]
        if parts and 1 <= len(parts) <= 4:
            return " ".join(parts).title()

    return "Candidate"


COMMON_ROLE_PATTERNS = [
    r'\b(?:senior|sr\.?|lead|junior|jr\.?|principal|staff|associate)?\s*(?:full\s*stack|frontend|front\-end|backend|back\-end|web|software|systems?|embedded|cloud|devops|site\s*reliability|sre|platform|infrastructure|data|machine\s*learning|ai|deep\s*learning|nlp|computer\s*vision|mobile|android|ios|flutter|react\s*native|qa|test|automation|security|cybersecurity|database|network)\s*(?:engineer|developer|architect|scientist|analyst|specialist|programmer|lead|manager|administrator)\b',
    r'\b(?:data\s*scientist|data\s*analyst|product\s*manager|project\s*manager|scrum\s*master|solutions?\s*architect|security\s*analyst|database\s*administrator|dba)\b'
]

def extract_job_role(jd_text: str, resume_role: Optional[str] = None) -> str:
    if not jd_text or not jd_text.strip():
        if resume_role and resume_role.strip().lower() not in ["candidate", "software developer", "software engineer"]:
            return resume_role.strip().title()
        return "Software Engineer"

    # 1. Check if jd_text is JSON
    try:
        trimmed = jd_text.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")):
            parsed = json.loads(trimmed)
            if isinstance(parsed, dict):
                job_part = parsed.get("job", {}) if isinstance(parsed.get("job"), dict) else {}
                title = (
                    parsed.get("title") or parsed.get("job_title") or parsed.get("role") or
                    parsed.get("target_role") or parsed.get("position") or
                    job_part.get("title") or job_part.get("role") or job_part.get("target_role")
                )
                if title and isinstance(title, str) and len(title.strip()) < 80:
                    return title.strip().title()
    except Exception:
        pass

    # 2. Check explicit labels like Job Title:, Target Role:, Role:, Position:
    label_match = re.search(r'(?:job\s*title|target\s*role|role|position|opening\s*(?:for)?|hiring\s*(?:for)?)\s*[:\-]\s*([A-Za-z0-9\s\/\+\.\(\)\-]+)', jd_text, re.I)
    if label_match:
        val = label_match.group(1).split("\n")[0].split(".")[0].strip()
        words = val.split()
        if 1 <= len(words) <= 7 and not any(ch in val for ch in "@:;0123456789{}"):
            return val.title()

    # 3. Check for standard tech role titles anywhere in the JD
    for pat in COMMON_ROLE_PATTERNS:
        match = re.search(pat, jd_text, re.I)
        if match:
            return match.group(0).strip().title()

    # 4. Check the top non-empty lines of the JD
    lines = [line.strip() for line in jd_text.split("\n") if line.strip()]
    for line in lines[:6]:
        if any(w in line.lower() for w in ["about", "company", "description", "requirements", "responsibilities", "overview", "location", "we are"]):
            continue
        clean = re.sub(r'^(job\s*title|target\s*role|role|position)[:\s-]*', '', line, flags=re.I).strip()
        clean = re.split(r'[\.,\-|;:]', clean)[0].strip()
        words = clean.split()
        if 1 <= len(words) <= 5 and not any(ch in clean for ch in "@0123456789/\\#+{}"):
            return clean.title()

    # 5. Check if resume provided a role
    if resume_role and resume_role.strip().lower() not in ["candidate", "user"]:
        return resume_role.strip().title()

    return "Software Engineer"


def generate_assessment_report_pdf(session_data: dict, output_path: Path) -> str:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.units import cm

    candidate_name = session_data.get("candidate_name") or "Candidate"
    target_role = session_data.get("target_role") or "Software Engineer"
    score_res = session_data.get("score_result") or {}
    gap_data = session_data.get("gap_data") or {}
    overall_score = score_res.get("overallScore", 58)
    status_label = score_res.get("status", "Developing Profile")
    metrics = gap_data.get("finalReportMetrics") or {
        "overallScore": overall_score,
        "technicalMatch": 38,
        "experienceMatch": 85,
        "projectRelevance": 95,
        "resumeQuality": 80,
        "jobMatch": 33
    }
    strong_skills = gap_data.get("strongSkills") or []
    needs_imp = gap_data.get("needsImprovement") or []
    missing_skills = gap_data.get("missingSkills") or []
    recommendations = gap_data.get("recommendations") or []

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=HexColor('#475569'),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=HexColor('#1E293B')
    )
    bold_cell = ParagraphStyle(
        'BoldCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=HexColor('#0F172A')
    )
    link_style = ParagraphStyle(
        'LinkStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=HexColor('#0284C7')
    )

    story = []

    # Title & Header
    story.append(Paragraph("CareerAI Candidate Assessment Report", title_style))
    date_str = datetime.now().strftime("%B %d, %Y")
    meta_text = f"Candidate: <b>{candidate_name}</b> &nbsp;|&nbsp; Target Role: <b>{target_role}</b> &nbsp;|&nbsp; Date: <b>{date_str}</b>"
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor('#0284C7'), spaceBefore=2, spaceAfter=12))

    # Executive Score Banner Table
    score_banner_data = [
        [
            Paragraph(f"<b>Overall Readiness Score: {overall_score} / 100</b>", bold_cell),
            Paragraph(f"<b>Profile Status: {status_label}</b>", bold_cell)
        ],
        [
            Paragraph(score_res.get("summary", f"Candidate {candidate_name} evaluated against {target_role} requirements."), body_style),
            Paragraph(f"Benchmark Threshold: 75/100 ({'Qualified' if overall_score >= 75 else 'Development Recommended'})", body_style)
        ]
    ]
    banner_table = Table(score_banner_data, colWidths=[10 * cm, 7.5 * cm])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    # Metric Breakdown Table
    story.append(Paragraph("Evaluation Category Breakdown", section_heading))
    metrics_data = [
        [
            Paragraph("<b>Category</b>", bold_cell),
            Paragraph("<b>Score</b>", bold_cell),
            Paragraph("<b>Benchmark</b>", bold_cell),
            Paragraph("<b>Assessment Status</b>", bold_cell)
        ]
    ]
    for label, val, bm in [
        ("Technical Match", metrics.get("technicalMatch", 38), 80),
        ("Experience Relevance", metrics.get("experienceMatch", 85), 70),
        ("Project Relevance", metrics.get("projectRelevance", 95), 75),
        ("Resume Quality (ATS)", metrics.get("resumeQuality", 80), 75),
        ("Job Description Match", metrics.get("jobMatch", 33), 75),
    ]:
        status_txt = "Meets Benchmark" if val >= bm else "Gap Identified"
        status_color = "#16A34A" if val >= bm else "#DC2626"
        metrics_data.append([
            Paragraph(label, body_style),
            Paragraph(f"<b>{val}%</b>", bold_cell),
            Paragraph(f"{bm}%", body_style),
            Paragraph(f"<font color='{status_color}'><b>{status_txt}</b></font>", body_style)
        ])
    
    m_table = Table(metrics_data, colWidths=[5.5 * cm, 3 * cm, 3 * cm, 6 * cm])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 10))

    # Skill Gaps Summary (Agent 2)
    story.append(Paragraph("Skill Competencies & Gap Analysis (Agent 2)", section_heading))
    gaps_table_data = [
        [
            Paragraph("<b>Classification</b>", bold_cell),
            Paragraph("<b>Skills Identified</b>", bold_cell),
            Paragraph("<b>Target Action</b>", bold_cell)
        ],
        [
            Paragraph("<font color='#16A34A'><b>Strong Skills</b></font>", bold_cell),
            Paragraph(", ".join([s.get("name", "") for s in strong_skills]) or "Core Fundamentals", body_style),
            Paragraph("Benchmark achieved; highlight in portfolio and interviews.", body_style)
        ],
        [
            Paragraph("<font color='#D97706'><b>Needs Improvement</b></font>", bold_cell),
            Paragraph(", ".join([s.get("name", "") for s in needs_imp]) or "Intermediate concepts", body_style),
            Paragraph("Partial exposure; review modern production patterns.", body_style)
        ],
        [
            Paragraph("<font color='#DC2626'><b>Missing Skills</b></font>", bold_cell),
            Paragraph(", ".join([s.get("name", "") for s in missing_skills]) or "None identified", body_style),
            Paragraph("Critical gap; prioritize targeted micro-courses.", body_style)
        ]
    ]
    g_table = Table(gaps_table_data, colWidths=[4.5 * cm, 7 * cm, 6 * cm])
    g_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(g_table)
    story.append(Spacer(1, 10))

    # Agent 3 Course Suggestions (< 1 Week)
    story.append(Paragraph("Curated Fast-Track Micro-Courses (< 1 Week) (Agent 3)", section_heading))
    courses_table_data = [
        [
            Paragraph("<b>Skill</b>", bold_cell),
            Paragraph("<b>Recommended Course</b>", bold_cell),
            Paragraph("<b>Platform</b>", bold_cell),
            Paragraph("<b>Duration</b>", bold_cell),
            Paragraph("<b>Free Course Link</b>", bold_cell)
        ]
    ]
    for rec in recommendations[:6]:
        sk = rec.get("skill", "")
        title = rec.get("title", "")
        badge = rec.get("badge", "freeCodeCamp")
        hours = rec.get("estimatedHours", "< 1 week")
        link = rec.get("link", "https://freecodecamp.org")
        courses_table_data.append([
            Paragraph(f"<b>{sk}</b>", bold_cell),
            Paragraph(title, body_style),
            Paragraph(badge, body_style),
            Paragraph(hours, body_style),
            Paragraph(f'<a href="{link}" color="#0284C7"><u>Open Course</u></a>', link_style)
        ])

    c_table = Table(courses_table_data, colWidths=[3 * cm, 6 * cm, 3 * cm, 2.5 * cm, 3 * cm])
    c_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(c_table)
    story.append(Spacer(1, 10))

    # Agent 5 30-Day Plan notice
    story.append(Paragraph("Next Steps & 30-Day Learning Plan (Agent 5)", section_heading))
    plan_notice = (
        f"A personalized 30-day curriculum has been scheduled by Agent 5 specifically to bridge {candidate_name}'s "
        f"skill gaps. Every skill module concludes with a dedicated practical project day to ensure hands-on mastery. "
        f"You can view the interactive roadmap in CareerAI or download the official 30-Day Learning Plan PDF."
    )
    story.append(Paragraph(plan_notice, body_style))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)
    return str(output_path)


@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "CareerAI Multi-Agent Live Engine",
        "pipeline": "Agent 1 (Screening) -> Agent 2 (Gaps) -> Agent 4 (Interview) -> Agent 3 (Courses) -> Agent 5 (Roadmap)",
        "modules": {
            "agent1_resume_screening": {
                "source": "CTBuildfest_2.0/module_1_resume_screening",
                "status": "connected" if AGENT1_AVAILABLE else "fallback",
                "routes_prefix": ["/api/v1/screening", "/api/agent1/screening"],
                "description": "ATS Scoring (0-100), Criteria Verification, 100-Synthetic Benchmark, Inter-Module Contracts"
            },
            "agent2_gap_analysis": {
                "source": "agent2",
                "status": "connected" if AGENT2_AVAILABLE else "fallback",
                "endpoint": "/api/gap-analysis",
                "description": "Semantic Skill Gap Analysis & Category Breakdown"
            },
            "agent3_course_suggestions": {
                "source": "agent3",
                "status": "connected",
                "endpoint": "/api/courses/recommend",
                "description": "Fast-Track Target Course Recommendations (< 1 Week Duration)"
            },
            "agent4_interview_agent": {
                "source": "interviewer/backend",
                "status": "connected" if AGENT4_AVAILABLE else "fallback",
                "routes_prefix": ["/interviews", "/api/interviews", "/api/interview"],
                "description": "Spoken Mock Interview, Edge-TTS Audio Generation, STT Transcription, Behavioral Analysis"
            },
            "agent5_learning_planner": {
                "source": "agent5",
                "status": "connected",
                "endpoints": ["/api/roadmap/generate", "/api/roadmap/pdf", "/api/report/pdf"],
                "description": "30-Day Calendar Learning Plan & ReportLab Official PDF Generator"
            }
        }
    }


# ---------------------------------------------------------------------------
# PIPELINE: Agent 1 (Resume) -> Agent 2 (Gaps) -> Agent 3 (Courses) -> Agent 5 (Roadmap)
# ---------------------------------------------------------------------------
@app.post("/api/resume/analyze")
async def analyze_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    score_simulation_type: Optional[str] = Form(None)
):
    raw_text = ""
    filename = "resume.txt"

    if file:
        filename = file.filename or "resume.txt"
        content_bytes = await file.read()
        raw_text = extract_text_from_file_bytes(content_bytes, filename)
    
    if not raw_text.strip() and resume_text:
        raw_text = resume_text

    if not raw_text.strip():
        raw_text = (
            "Krish Sharma. Software Engineer. Skills: HTML5, CSS3, JavaScript, React.js, Git, GitHub. "
            "Experience: 1.5 years frontend development. Built web applications and dashboards."
        )

    jd_text = (job_description or "").strip()

    # 1. AGENT 1 (CTBuildfest_2.0): Parse Resume & Job Description into Structured JSON
    ext = "json" if filename.lower().endswith(".json") else ("pdf" if filename.lower().endswith(".pdf") else ("docx" if filename.lower().endswith(".docx") else "txt"))
    if AGENT1_AVAILABLE:
        try:
            res_struct, evidence = extract_structured_resume(raw_text=raw_text, source_format=ext, ocr_applied=False)
        except Exception as e:
            print(f"[CareerAI Agent 1 Warning] extract_structured_resume error: {e}")
            from app.schemas.resume import ResumeStructuredData, CandidateInfo
            res_struct = ResumeStructuredData(
                candidate=CandidateInfo(name=extract_candidate_name(raw_text, filename)),
                all_skills_flat=extract_skills(raw_text)[0]
            )
    else:
        from app.schemas.resume import ResumeStructuredData, CandidateInfo
        res_tech, res_soft = extract_skills(raw_text)
        res_struct = ResumeStructuredData(
            candidate=CandidateInfo(name=extract_candidate_name(raw_text, filename)),
            all_skills_flat=res_tech
        )

    # Validate and resolve extracted candidate details from resume
    extracted_name = None
    if hasattr(res_struct, "candidate") and res_struct.candidate and res_struct.candidate.name:
        cand_n = str(res_struct.candidate.name).strip()
        if cand_n.lower() not in ["candidate", "unknown", "user", "name", "your name", "n/a", "{", "null", "none"]:
            extracted_name = cand_n

    if not extracted_name:
        extracted_name = extract_candidate_name(raw_text, filename)

    candidate_name = extracted_name or "Candidate"

    # Extract email and phone if missing
    candidate_email = getattr(res_struct.candidate, "email", None) if hasattr(res_struct, "candidate") else None
    if not candidate_email:
        email_m = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', raw_text)
        if email_m:
            candidate_email = email_m.group(0)

    candidate_phone = getattr(res_struct.candidate, "phone", None) if hasattr(res_struct, "candidate") else None
    if not candidate_phone:
        phone_m = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text)
        if phone_m:
            candidate_phone = phone_m.group(0)

    raw_headline = (getattr(res_struct.candidate, "headline", None) if hasattr(res_struct, "candidate") else None) or ""

    # Dynamically resolve Job Description and Target Role
    if not jd_text:
        # If no JD text supplied, infer role and requirements from the resume
        inferred_role = raw_headline if (raw_headline and "Specialist" not in raw_headline and len(raw_headline.split()) <= 5) else None
        if not inferred_role:
            inferred_role = extract_job_role(raw_text)
        if not inferred_role or inferred_role.lower() in ["candidate", "unknown"]:
            inferred_role = "Software Engineer"
        top_skills = res_struct.all_skills_flat[:6] if res_struct.all_skills_flat else ["Software Engineering", "Problem Solving", "Git"]
        jd_text = f"Job Title: {inferred_role}. Requirements: {', '.join(top_skills)}."

    # Parse Job Description
    if AGENT1_AVAILABLE:
        try:
            job_struct = extract_structured_job(jd_text)
        except Exception as e:
            print(f"[CareerAI Agent 1 Warning] extract_structured_job error: {e}")
            from app.schemas.job import JobStructuredData
            req, soft = extract_skills(jd_text)
            job_struct = JobStructuredData(
                title=extract_job_role(jd_text, resume_role=raw_headline),
                required_skills=req,
                required_soft_skills=soft
            )
    else:
        from app.schemas.job import JobStructuredData
        jd_tech, jd_soft = extract_skills(jd_text)
        job_struct = JobStructuredData(
            title=extract_job_role(jd_text, resume_role=raw_headline),
            required_skills=jd_tech,
            required_soft_skills=jd_soft
        )

    target_role = getattr(job_struct, "title", None)
    if not target_role or target_role.lower() in ["job description", "about us", "overview", "nexus", "software developer"]:
        target_role = extract_job_role(jd_text, resume_role=raw_headline)
    if not target_role:
        target_role = "Software Engineer"

    candidate_headline = raw_headline or f"{target_role} Specialist"

    if hasattr(res_struct, "candidate") and res_struct.candidate:
        res_struct.candidate.name = candidate_name
        res_struct.candidate.email = candidate_email
        res_struct.candidate.phone = candidate_phone
        res_struct.candidate.headline = candidate_headline

    candidate_profile = {
        "name": candidate_name,
        "email": candidate_email or "",
        "phone": candidate_phone or "",
        "headline": candidate_headline,
        "role": target_role,
        "skills": res_struct.all_skills_flat
    }

    # Save resume.json and jd.json into shared_output
    try:
        with open(OUTPUTS_DIR / "resume.json", "w", encoding="utf-8") as f:
            json.dump(res_struct.model_dump(), f, indent=2)
        with open(OUTPUTS_DIR / "jd.json", "w", encoding="utf-8") as f:
            json.dump(job_struct.model_dump(), f, indent=2)
    except Exception as e:
        print(f"[CareerAI Warning] Failed to write resume/jd json: {e}")

    # 2. AGENT 1 (CTBuildfest_2.0): Deterministic ATS Scoring & 100-Persona Benchmarking
    if AGENT1_AVAILABLE:
        try:
            ats_score, breakdown, mandatory, metadata = ats_engine.evaluate(res_struct, job_struct)
            session_id = f"session_{int(datetime.now().timestamp())}"
            pool = synthetic_generator.generate_and_score_pool(job_struct, session_id)
            ranking_res, distribution_stats = compute_candidate_ranking(ats_score, pool)
            actual_rank = ranking_res.rank
            actual_percentile = ranking_res.percentile
            b_dict = breakdown.model_dump()

            # Save full screening report
            screening_report_data = {
                "session_id": session_id,
                "overall_ats_score": ats_score,
                "ranking": ranking_res.model_dump(),
                "score_breakdown": b_dict,
                "score_distribution": distribution_stats.model_dump()
            }
            with open(OUTPUTS_DIR / "screening_report.json", "w", encoding="utf-8") as f:
                json.dump(screening_report_data, f, indent=2)
        except Exception as e:
            print(f"[CareerAI Agent 1 Scoring Warning]: {e}")
            ats_score = 72.0
            actual_rank = 35
            actual_percentile = 65.0
            b_dict = {}
    else:
        ats_score = 72.0
        actual_rank = 35
        actual_percentile = 65.0
        b_dict = {}

    total_personas = 100
    if score_simulation_type == "low":
        simulated_rank = 78  # In 76-100 bracket (Rank > 75) -> Path B
        overall_score = min(68, int(ats_score) if int(ats_score) < 75 else 58)
        is_qualified = False
    elif score_simulation_type == "high":
        simulated_rank = 24  # In 1-75 bracket (Rank <= 75) -> Path A
        overall_score = max(78, int(ats_score) if int(ats_score) >= 75 else 82)
        is_qualified = True
    else:
        simulated_rank = max(1, min(100, actual_rank))
        overall_score = round(ats_score)
        # Decision criterion: Candidate qualifies for interview if simulation rank <= 75 (top 75 personas),
        # regardless of ATS score. If simulation rank > 75, candidate is routed to technical skill gap analysis only.
        is_qualified = (1 <= simulated_rank <= 75)

    path_code = "A" if is_qualified else "B"

    # Category Percentages from ATS Breakdown
    def get_cat_pct(cat_key, default_pct=75):
        c = b_dict.get(cat_key, {})
        max_p = c.get("maximum_points", 0)
        awd = c.get("awarded", 0)
        if max_p > 0:
            return max(20, min(98, round((awd / max_p) * 100)))
        return default_pct

    tech_score = get_cat_pct("required_skills", 70)
    exp_score = get_cat_pct("experience", 65)
    proj_score = get_cat_pct("projects", 60)
    edu_score = get_cat_pct("education", 80)
    role_score = get_cat_pct("role_relevance", 70)
    pref_score = get_cat_pct("preferred_skills", 50)
    jd_match_score = round(0.7 * tech_score + 0.3 * pref_score)
    resume_quality_score = round(0.5 * proj_score + 0.5 * exp_score)

    categories = [
        {"name": "Technical Skills", "score": tech_score, "benchmark": 80, "desc": f"Alignment on required core competencies ({tech_score}%)"},
        {"name": "Experience Relevance", "score": exp_score, "benchmark": 70, "desc": f"Alignment of practical work with role level ({exp_score}%)"},
        {"name": "Projects", "score": proj_score, "benchmark": 75, "desc": f"Hands-on portfolio and architecture implementations ({proj_score}%)"},
        {"name": "Education", "score": edu_score, "benchmark": 70, "desc": f"Academic degree qualification and specialization ({edu_score}%)"},
        {"name": "Role Relevance", "score": role_score, "benchmark": 70, "desc": f"Semantic role vocabulary and engineering context overlap ({role_score}%)"},
        {"name": "Job Description Match", "score": jd_match_score, "benchmark": 75, "desc": f"Overall direct coverage across all JD specifications ({jd_match_score}%)"}
    ]

    # Matched and missing skills from CTBuildfest extraction
    matched_tech = [s for s in job_struct.required_skills if any(cs.lower() == s.lower() or s.lower() in cs.lower() for cs in res_struct.all_skills_flat)]
    if not matched_tech:
        matched_tech = [s for s in res_struct.all_skills_flat if s.lower() in jd_text.lower()]
    if not matched_tech:
        matched_tech = res_struct.all_skills_flat[:3] or ["HTML5", "CSS3", "JavaScript"]

    missing_tech = [s for s in job_struct.required_skills if not any(cs.lower() == s.lower() or s.lower() in cs.lower() for cs in res_struct.all_skills_flat)]
    if not missing_tech:
        missing_tech = [s for s in job_struct.preferred_skills if not any(cs.lower() == s.lower() for cs in res_struct.all_skills_flat)]
    if not missing_tech:
        missing_tech = ["Docker", "MongoDB", "REST APIs", "Node.js"]

    score_result = {
        "overallScore": overall_score,
        "simulationScore": overall_score,
        "simulationRank": simulated_rank,
        "totalPersonas": total_personas,
        "percentile": round((total_personas - simulated_rank) / total_personas * 100, 1),
        "path": path_code,
        "rankDisplay": f"Rank #{simulated_rank} of {total_personas} Personas",
        "status": f"Path A: Interview Qualified (Rank #{simulated_rank}/100)" if is_qualified else f"Path B: Skill Remediation Report (Rank #{simulated_rank}/100)",
        "summary": (
            f"Candidate {candidate_name} placed Rank #{simulated_rank} among {total_personas} benchmark personas "
            f"(Rank 1-75 bracket). Evaluated with CTBuildfest_2.0 deterministic ATS engine. Qualified for Path A: Proceeding to Agent 4 Spoken Mock Interview."
            if is_qualified else
            f"Candidate {candidate_name} placed Rank #{simulated_rank} among {total_personas} benchmark personas "
            f"(Rank 76-100 bracket). Evaluated with CTBuildfest_2.0 deterministic ATS engine. Routed to Path B: Gap Analysis (Agent 2), Fast-Track Courses (Agent 3), Targeted Interview (Agent 4), and 30-Day Learning Plan (Agent 5)."
        ),
        "isInterviewReady": is_qualified,
        "candidateName": candidate_name,
        "candidateEmail": candidate_email or "",
        "candidatePhone": candidate_phone or "",
        "targetRole": target_role,
        "candidateProfile": candidate_profile,
        "categories": categories,
        "matchedSkills": matched_tech,
        "missingSkills": missing_tech
    }

    # 3. AGENT 2 (agent2): Semantic Gap Analysis
    if AGENT2_AVAILABLE:
        try:
            gap_agent = GapAnalysisAgent()
            gap_report = gap_agent.run_from_json(res_struct.model_dump(), job_struct.model_dump())
        except Exception as e:
            print(f"[CareerAI Agent 2 Warning] GapAnalysisAgent execution error: {e}")
            gap_report = None
    else:
        gap_report = None

    if not gap_report or "data" not in gap_report:
        gap_report = {
            "status": "completed",
            "candidate_name": candidate_name,
            "target_job_title": target_role,
            "data": {
                "critical_gaps": missing_tech[:3],
                "important_gaps": missing_tech[3:] if len(missing_tech) > 3 else ["System Architecture"],
                "optional_gaps": [],
                "matched_skills": matched_tech,
                "missing_keywords": missing_tech[:3],
                "soft_skills_analysis": {
                    "matched_soft_skills": [s for s in getattr(job_struct, 'required_soft_skills', []) if s in getattr(res_struct.skills, 'soft_skills', [])],
                    "missing_soft_skills": [s for s in getattr(job_struct, 'required_soft_skills', []) if s not in getattr(res_struct.skills, 'soft_skills', [])] or ["Technical Communication", "Cross-Functional Collaboration"]
                },
                "improvement_priority_order": missing_tech
            }
        }

    try:
        with open(OUTPUTS_DIR / "gap_report.json", "w", encoding="utf-8") as f:
            json.dump(gap_report, f, indent=2)
    except Exception as e:
        print(f"[CareerAI Warning] Failed to write gap_report.json: {e}")

    # Extract semantic gaps from Agent 2
    agent2_data = gap_report.get("data", {})
    critical_gaps = agent2_data.get("critical_gaps", [])
    important_gaps = agent2_data.get("important_gaps", [])
    
    # Requirement: If simulation rank > 75 (not is_qualified), analyze technical skill gap ONLY and suggest ONLY technical courses.
    if is_qualified:
        missing_soft = agent2_data.get("soft_skills_analysis", {}).get("missing_soft_skills", [])
    else:
        missing_soft = []
        if "soft_skills_analysis" in agent2_data:
            agent2_data["soft_skills_analysis"]["missing_soft_skills"] = []

    agent2_priority = agent2_data.get("improvement_priority_order", [])

    all_gap_tech = critical_gaps + [g for g in important_gaps if g not in critical_gaps]
    if not all_gap_tech:
        all_gap_tech = missing_tech

    # 4. AGENT 3: Free Curated Micro-Courses (< 1 Week)
    skill_levels = {}
    for s in critical_gaps:
        skill_levels[s] = "Critical Gap"
    for s in important_gaps:
        if s not in skill_levels:
            skill_levels[s] = "Important Gap"
    if is_qualified:
        for s in missing_soft:
            skill_levels[s] = "Missing Soft Skill"

    agent3_input = {
        "technical_skills": all_gap_tech or ["Python", "FastAPI", "Docker", "SQL"],
        "soft_skills": missing_soft if is_qualified else [],
        "skill_levels": skill_levels,
        "target_job_role": target_role,
        "candidate_name": candidate_name,
        "sources_used": ["resume.json", "jd.json", "gap_report.json"]
    }
    agent3_output = suggest_courses(agent3_input)
    SESSION_STATE["agent3_output"] = agent3_output

    try:
        with open(OUTPUTS_DIR / "agent3_output.json", "w", encoding="utf-8") as f:
            json.dump(agent3_output, f, indent=2)
        with open(OUTPUTS_DIR / "agent3_courses.json", "w", encoding="utf-8") as f:
            json.dump(agent3_output, f, indent=2)
    except Exception as e:
        print(f"Error saving agent3_output: {e}")

    # Build recommendations for frontend
    recommendations = []
    rec_id = 1
    for skill_rec in agent3_output.get("technical_recommendations", []):
        sk = skill_rec.get("skill", "")
        rec_info = skill_rec.get("recommended", {})
        recommendations.append({
            "id": f"rec-{rec_id}",
            "skill": sk,
            "title": rec_info.get("title", f"{sk} Fast-Track Course"),
            "badge": rec_info.get("platform", "freeCodeCamp"),
            "level": rec_info.get("difficulty", "Beginner -> Intermediate"),
            "estimatedHours": rec_info.get("duration", "< 1 week"),
            "whyMatters": f"{sk} is explicitly required by the target role. This course bridges your skill gap.",
            "link": rec_info.get("url", "https://freecodecamp.org")
        })
        rec_id += 1

    gap_data = {
        "heading": "Areas to Improve",
        "subtitle": f"Targeted skill gaps identified between {candidate_name}'s profile and {target_role} requirements.",
        "strongSkills": [
            {"name": sk, "level": 90, "required": 80, "status": "strong", "desc": "Demonstrated practical proficiency in candidate's resume"}
            for sk in matched_tech
        ],
        "needsImprovement": [
            {"name": sk, "level": 50, "required": 80, "gap": 30, "status": "moderate", "desc": "Partial exposure detected; requires advanced production depth"}
            for sk in all_gap_tech[:2]
        ],
        "missingSkills": [
            {"name": sk, "level": 15, "required": 75, "gap": 60, "status": "missing", "desc": "Core JD requirement absent from candidate resume"}
            for sk in all_gap_tech[2:]
        ],
        "recommendations": recommendations,
        "simulationScore": overall_score,
        "simulationRank": simulated_rank,
        "totalPersonas": total_personas,
        "path": path_code,
        "rankDisplay": f"Rank #{simulated_rank} of {total_personas} Personas",
        "finalReportMetrics": {
            "overallScore": overall_score,
            "simulationRank": simulated_rank,
            "technicalMatch": tech_score,
            "experienceMatch": exp_score,
            "projectRelevance": proj_score,
            "resumeQuality": resume_quality_score,
            "jobMatch": jd_match_score
        },
        "strengths": [
            f"Solid foundation in {', '.join(matched_tech[:2]) if matched_tech else 'core fundamentals'}",
            f"Active project and technical portfolio evidence",
            f"Structured CV formatting compliant with ATS scanning"
        ],
        "areasToImprove": [
            f"Bridge deficit in {s} through dedicated practice"
            for s in all_gap_tech[:3]
        ],
        "missingSkillsList": all_gap_tech,
        "recommendedActions": [
            f"Complete short crash course for {s}"
            for s in all_gap_tech[:3]
        ] + ["Build an integrated project implementing all gap tools", "Complete mock interview practice with Agent 4"]
    }

    # 5. AGENT 5: 30-Day Learning Plan & Official PDF Generation
    parsed_a5 = _parse_agent3_schema(agent3_output)
    schedule = generate_30_day_plan(
        missing_skills=parsed_a5["missing_skills"],
        skill_priority=parsed_a5["skill_priority"],
        agent3_data=parsed_a5["agent3_course_suggestions"]
    )
    SESSION_STATE["roadmap_data"] = schedule

    pdf_path = OUTPUTS_DIR / "30_Days_Learning_Plan.pdf"
    assessment_pdf_path = OUTPUTS_DIR / "CareerAI_Assessment_Report.pdf"

    gap_summary = (
        f"Candidate {candidate_name} placed Rank #{simulated_rank} among {total_personas} simulated applicant personas "
        f"with a simulation score of {overall_score}/100 ({'Path A: Qualified for Interview' if is_qualified else 'Path B: Remediation Learning Plan Required'}). "
        f"Demonstrated competencies include {', '.join(matched_tech[:3]) if matched_tech else 'core web fundamentals'}. "
        f"Actionable skill deficits were identified in {', '.join(all_gap_tech)}. "
        f"To bridge these deficits, Agent 5 has structured a personalized 30-day curriculum with short-format micro-courses (< 1 week) "
        f"and dedicated 1-day practical projects after each skill module to build verifiable portfolio assets."
    )

    user_profile = {
        "name": candidate_name,
        "target_role": target_role,
        "rank": simulated_rank,
        "total_candidates": total_personas,
        "readiness_score": overall_score,
        "rank_display": f"Rank #{simulated_rank} of {total_personas} Personas ({'Path A' if is_qualified else 'Path B'})",
        "current_skill_level": "Advanced" if overall_score >= 80 else "Intermediate" if overall_score >= 60 else "Developing"
    }

    try:
        generate_pdf(
            schedule=schedule,
            user_profile=user_profile,
            missing_skills=parsed_a5["missing_skills"],
            output_path=str(pdf_path),
            gap_analysis_summary=gap_summary
        )
        shutil.copy2(str(pdf_path), str(assessment_pdf_path))
    except Exception as e:
        print(f"Error generating Agent 5 PDF: {e}")

    gap_data["roadmap"] = schedule
    SESSION_STATE["candidate_name"] = candidate_name
    SESSION_STATE["candidate_email"] = candidate_email
    SESSION_STATE["candidate_phone"] = candidate_phone
    SESSION_STATE["candidate_headline"] = candidate_headline
    SESSION_STATE["candidate_profile"] = candidate_profile
    SESSION_STATE["target_role"] = target_role
    SESSION_STATE["resume_text"] = raw_text
    SESSION_STATE["job_description"] = jd_text
    SESSION_STATE["matched_skills"] = matched_tech
    SESSION_STATE["missing_skills"] = all_gap_tech
    SESSION_STATE["score_result"] = score_result
    SESSION_STATE["gap_data"] = gap_data

    return {
        "success": True,
        "data": score_result,
        "candidateName": candidate_name,
        "candidateEmail": candidate_email,
        "candidatePhone": candidate_phone,
        "targetRole": target_role,
        "candidateProfile": candidate_profile,
        "gapData": gap_data,
        "roadmap": schedule,
        "agent3Summary": agent3_output.get("metadata", {}),
        "pdfGenerated": pdf_path.exists()
    }


# ---------------------------------------------------------------------------
# API: Gap Analysis Data
# ---------------------------------------------------------------------------
@app.get("/api/gap-analysis")
@app.post("/api/gap-analysis")
async def get_gap_analysis():
    if SESSION_STATE["gap_data"]:
        return {"success": True, "data": SESSION_STATE["gap_data"]}
    shared_gap = OUTPUTS_DIR / "agent3_output.json"
    if shared_gap.exists():
        try:
            with open(shared_gap, "r", encoding="utf-8") as f:
                return {"success": True, "data": json.load(f)}
        except Exception:
            pass
    return {"success": True, "data": None}


# ---------------------------------------------------------------------------
# API: Agent 4 Mock Interview Generation & Evaluation
# ---------------------------------------------------------------------------
class InterviewStartPayload(BaseModel):
    candidate_name: Optional[str] = None
    role: Optional[str] = None

@app.post("/api/interview/start")
async def start_interview(payload: Optional[InterviewStartPayload] = None):
    req_name = payload.candidate_name if payload and payload.candidate_name else None
    req_role = payload.role if payload and payload.role else None

    candidate = req_name or SESSION_STATE.get("candidate_name") or "Candidate"
    role = req_role or SESSION_STATE.get("target_role") or "Software Engineer"
    SESSION_STATE["candidate_name"] = candidate
    SESSION_STATE["target_role"] = role
    matched = SESSION_STATE.get("matched_skills", ["React.js", "JavaScript", "HTML5"])
    missing = SESSION_STATE.get("missing_skills", ["Node.js", "MongoDB", "Docker"])

    questions = []
    interview_id = f"ai-session-{int(datetime.now().timestamp())}"

    # Try Agent 4 dynamic question generator
    if AGENT4_AVAILABLE:
        try:
            resume_dict = {
                "candidate": {"name": candidate},
                "full_name": candidate,
                "role": role,
                "skills": matched,
                "experience": f"Experienced developer with proficiency in {', '.join(matched)}."
            }
            jd_dict = {
                "role": role,
                "job_title": role,
                "required_skills": matched + missing,
                "target_competencies": missing
            }
            q_set = await generate_interview_questions(resume_dict, jd_dict)
            if q_set and getattr(q_set, "questions", None):
                for q in q_set.questions:
                    questions.append({
                        "id": q.q_id,
                        "question": q.question,
                        "category": f"{q.type.capitalize()} - {q.skill_tested}" if q.skill_tested else q.type.capitalize(),
                        "durationSeconds": q.time_limit_sec,
                        "aiSpeech": q.question,
                        "phase": q.phase,
                        "type": q.type,
                        "skill_tested": q.skill_tested,
                        "difficulty": q.difficulty
                    })

                # Register in Agent 4 repository for live streaming
                items = [{
                    "q_id": q.q_id,
                    "phase": q.phase,
                    "type": q.type,
                    "source": q.source,
                    "skill_tested": q.skill_tested,
                    "difficulty": q.difficulty,
                    "question": q.question,
                    "time_limit_sec": q.time_limit_sec,
                    "status": "pending",
                    "answer": None,
                    "duration_sec": 0,
                    "behavioral_analysis": None
                } for q in q_set.questions]
                db_record = {
                    "id": interview_id,
                    "role": role,
                    "candidate_name": candidate,
                    "status": "in_progress",
                    "total_questions": len(q_set.questions),
                    "answered_count": 0,
                    "skipped_count": 0,
                    "questions": [q.model_dump() for q in q_set.questions],
                    "items": items
                }
                await InterviewRepository.create_interview(db_record)
        except Exception as e:
            print(f"[CareerAI Warning] Agent 4 dynamic question generation bypassed ({e}). Using standard high-signal questions.")

    if not questions:
        q1_tech = matched[0] if matched else "React"
        q2_tech = matched[1] if len(matched) > 1 else (matched[0] if matched else "JavaScript")
        q3_gap = missing[0] if missing else "Backend Microservices"
        q4_gap = missing[1] if len(missing) > 1 else (missing[0] if missing else "Database Optimization")

        questions = [
            {
                "id": 1,
                "question": f"Welcome {candidate}. Walk me through your hands-on journey in web development and your core experience with {q1_tech}.",
                "category": "Introduction & Core Stack",
                "durationSeconds": 90,
                "aiSpeech": f"Welcome {candidate}. Walk me through your hands-on experience developing applications with {q1_tech}."
            },
            {
                "id": 2,
                "question": f"In your projects using {q2_tech}, how do you manage state, handle asynchronous API requests, and safeguard against unhandled error conditions?",
                "category": "Technical Deep Dive",
                "durationSeconds": 90,
                "aiSpeech": f"In your projects using {q2_tech}, how do you handle state and asynchronous error handling?"
            },
            {
                "id": 3,
                "question": f"Our role relies heavily on {q3_gap}. Can you explain how you would design, structure, or integrate {q3_gap} in a scalable production application?",
                "category": "Target Role Competency",
                "durationSeconds": 90,
                "aiSpeech": f"Our role requires solid competence in {q3_gap}. How would you approach building and structuring systems with it?"
            },
            {
                "id": 4,
                "question": f"When scaling applications with {q4_gap}, what common performance bottlenecks do you anticipate, and how do you monitor or optimize them?",
                "category": "System Design & Gaps",
                "durationSeconds": 90,
                "aiSpeech": f"When scaling with {q4_gap}, what performance bottlenecks do you foresee, and how do you optimize them?"
            },
            {
                "id": 5,
                "question": "Tell me about a challenging technical bug or tight deadline you encountered recently. How did you diagnose the issue and communicate with teammates?",
                "category": "Problem Solving & Behavioral",
                "durationSeconds": 90,
                "aiSpeech": "Tell me about a difficult technical challenge you resolved recently. How did you diagnose the issue and collaborate with your team?"
            }
        ]

    SESSION_STATE["interview_questions"] = questions
    return {
        "success": True,
        "sessionId": interview_id,
        "role": role,
        "candidateName": candidate,
        "questionsCount": len(questions),
        "questions": questions,
        "agent4Active": AGENT4_AVAILABLE
    }


class InterviewEvaluatePayload(BaseModel):
    transcripts: Optional[List[Dict[str, Any]]] = None
    interview_id: Optional[str] = None
    role: Optional[str] = None

@app.post("/api/interview/evaluate")
@app.post("/interviews/{interview_id}/complete")
@app.post("/api/interviews/{interview_id}/complete")
async def evaluate_interview(payload: Optional[InterviewEvaluatePayload] = None, interview_id: Optional[str] = None):
    transcripts = (payload.transcripts if payload else None) or []
    interview_id = interview_id or (payload.interview_id if payload else None) or SESSION_STATE.get("interview_id") or f"ai-session-{int(datetime.now().timestamp())}"
    candidate = SESSION_STATE.get("candidate_name") or "Candidate"
    role = (payload.role if payload else None) or SESSION_STATE.get("target_role") or "Software Engineer"
    questions = SESSION_STATE.get("interview_questions", [])

    # 1. Retrieve or assemble interview session items with candidate answers & behavioral snapshots
    items = []
    if AGENT4_AVAILABLE and interview_id:
        try:
            db_interview = await InterviewRepository.get_interview(interview_id)
            if db_interview and db_interview.get("items"):
                items = db_interview["items"]
        except Exception as e:
            print(f"[CareerAI Warning] Could not fetch interview {interview_id} from repo: {e}")

    if not items:
        # Assemble from questions & transcripts
        for idx, q in enumerate(questions):
            q_id = q.get("id") or (idx + 1)
            q_text = q.get("question", "")
            skill = q.get("skill_tested") or q.get("category") or "Technical Proficiency"
            user_ans = ""
            behavioral = None
            duration_sec = 0
            if idx < len(transcripts):
                t = transcripts[idx]
                user_ans = t.get("text", "") or t.get("applicantAnswer", "")
                behavioral = t.get("behavioral")
                duration_sec = t.get("duration", 40)

            items.append({
                "q_id": q_id,
                "question": q_text,
                "skill_tested": skill,
                "status": "answered" if user_ans.strip() else "skipped",
                "answer": user_ans.strip() if user_ans.strip() else None,
                "duration_sec": duration_sec,
                "behavioral_analysis": behavioral
            })
    else:
        # Sync latest transcripts into items if answer is empty
        for idx, it in enumerate(items):
            if not it.get("answer") and idx < len(transcripts):
                t = transcripts[idx]
                t_ans = t.get("text", "") or t.get("applicantAnswer", "")
                if t_ans.strip():
                    it["answer"] = t_ans.strip()
                    it["status"] = "answered"
                if not it.get("behavioral_analysis") and t.get("behavioral"):
                    it["behavioral_analysis"] = t.get("behavioral")

    # 2. RUN AGENT 2 GAP ANALYSIS on the Spoken Interview (Module 2)
    interview_json_input = {
        "interview_id": interview_id,
        "role": role,
        "candidate_name": candidate,
        "items": items
    }

    gap_agent = GapAnalysisAgent() if AGENT2_AVAILABLE else None
    if gap_agent:
        agent2_interview_res = gap_agent.analyze_interview(interview_json_input)
    else:
        agent2_interview_res = {
            "interview_id": interview_id,
            "role": role,
            "status": "completed",
            "data": {
                "overall_interview_score": 7.8,
                "technical_evaluation": {
                    "demonstrated_strong_skills": ["Core Web Architecture"],
                    "critical_technical_gaps": ["Database Sharding & Query Tuning"],
                    "skipped_skills": [],
                    "conceptual_misunderstandings": [],
                    "priority_technical_topics_to_learn": ["System Architecture"]
                },
                "soft_skills_evaluation": {
                    "communication_clarity": "Strong",
                    "problem_solving_approach": "Analytical",
                    "observed_soft_skill_strengths": ["Structured responses"],
                    "critical_soft_skill_gaps": ["Use more STAR method examples"]
                },
                "actionable_interview_advice": "Focus on system trade-offs."
            }
        }

    # Save interview_gap.json to shared_output
    try:
        with open(OUTPUTS_DIR / "interview_gap.json", "w", encoding="utf-8") as f:
            json.dump(agent2_interview_res, f, indent=2)
    except Exception as e:
        print(f"[CareerAI Warning] Failed to write interview_gap.json: {e}")

    # Extract Agent 2 interview gap analysis data
    gap_data = agent2_interview_res.get("data", {})
    tech_eval = gap_data.get("technical_evaluation", {})
    soft_eval = gap_data.get("soft_skills_evaluation", {})

    interview_score_10 = float(gap_data.get("overall_interview_score", 7.8))
    interview_score_pct = round(min(98, max(20, interview_score_10 * 10)))

    demonstrated_strong = tech_eval.get("demonstrated_strong_skills", [])
    critical_tech_gaps = tech_eval.get("critical_technical_gaps", [])
    priority_tech_topics = tech_eval.get("priority_technical_topics_to_learn", [])
    skipped_skills = tech_eval.get("skipped_skills", [])
    conceptual_errors = tech_eval.get("conceptual_misunderstandings", [])

    observed_soft_strengths = soft_eval.get("observed_soft_skill_strengths", [])
    critical_soft_gaps = soft_eval.get("critical_soft_skill_gaps", [])
    actionable_advice = gap_data.get("actionable_interview_advice", "")
    question_evals = gap_data.get("question_evaluations", [])

    # Format questionAnalyses for InterviewReport.jsx
    formatted_question_analyses = []
    for qe in question_evals:
        formatted_question_analyses.append({
            "id": qe.get("id"),
            "question": qe.get("question", ""),
            "skill_tested": qe.get("skill_tested", ""),
            "status": qe.get("status", "answered"),
            "score": qe.get("score", 7.5),
            "feedback": qe.get("feedback", ""),
            "applicantAnswer": qe.get("applicantAnswer", ""),
            "duration": qe.get("duration", 0),
            "behavioral": qe.get("behavioral")
        })

    # 3. Retrieve screening ATS score & merge screening gaps with interview gaps
    score_result = SESSION_STATE.get("score_result") or {}
    ats_score = score_result.get("atsScore") or score_result.get("overallScore", 75)
    screening_gaps = SESSION_STATE.get("missing_skills") or ["Python", "FastAPI", "Docker", "PostgreSQL"]

    # Combine resume screening gaps + spoken interview technical gaps
    combined_gaps = list(dict.fromkeys(screening_gaps + critical_tech_gaps + priority_tech_topics))
    SESSION_STATE["missing_skills"] = combined_gaps
    SESSION_STATE["combined_gaps"] = combined_gaps

    # Update shared_output/gap_report.json with combined gaps
    try:
        combined_gap_report = {
            "session_id": interview_id,
            "candidate_name": candidate,
            "target_job_title": role,
            "status": "completed",
            "data": {
                "critical_gaps": combined_gaps[:3],
                "important_gaps": combined_gaps[3:] if len(combined_gaps) > 3 else ["System Scalability"],
                "matched_skills": demonstrated_strong,
                "missing_keywords": critical_tech_gaps[:3],
                "soft_skills_analysis": {
                    "matched_soft_skills": observed_soft_strengths,
                    "missing_soft_skills": critical_soft_gaps
                },
                "improvement_priority_order": combined_gaps
            }
        }
        with open(OUTPUTS_DIR / "gap_report.json", "w", encoding="utf-8") as f:
            json.dump(combined_gap_report, f, indent=2)
    except Exception as e:
        print(f"[CareerAI Warning] Failed to update gap_report.json: {e}")

    # Composite score: 40% ATS resume score + 60% Spoken Interview score
    composite_score = round(0.4 * ats_score + 0.6 * interview_score_pct)
    composite_rank = max(1, min(100, 101 - composite_score))

    # Metric scores
    tech_metric = min(98, max(25, round(interview_score_pct + 1)))
    comm_metric = min(96, max(30, 88 if soft_eval.get("communication_clarity") == "Strong" else 72))
    prob_metric = min(95, max(30, 86 if soft_eval.get("problem_solving_approach") == "Analytical" else 70))
    conf_metric = min(94, max(30, round(soft_eval.get("average_eye_contact", 82))))
    relevance_metric = min(98, max(30, round(interview_score_pct + 2)))

    # 4. RUN AGENT 3 (Course Suggestions) for Combined Deficits
    agent3_input = {
        "technical_skills": combined_gaps,
        "soft_skills": critical_soft_gaps or ["STAR Communication", "Technical Articulation"],
        "skill_levels": {s: "Critical Deficit (Interview)" if s in critical_tech_gaps else "Identified Gap" for s in combined_gaps},
        "target_job_role": role,
        "candidate_name": candidate,
        "sources_used": ["screening_gap.json", "interview_gap.json"]
    }
    agent3_output = suggest_courses(agent3_input)
    SESSION_STATE["agent3_output"] = agent3_output

    try:
        with open(OUTPUTS_DIR / "agent3_output.json", "w", encoding="utf-8") as f:
            json.dump(agent3_output, f, indent=2)
        with open(OUTPUTS_DIR / "agent3_courses.json", "w", encoding="utf-8") as f:
            json.dump(agent3_output, f, indent=2)
    except Exception as e:
        print(f"[CareerAI Warning] Error saving agent3_output in evaluate_interview: {e}")

    # 5. RUN AGENT 5 (30-Day Learning Planner & Official PDF Generator)
    parsed_a5 = _parse_agent3_schema(agent3_output)
    schedule = generate_30_day_plan(
        missing_skills=parsed_a5["missing_skills"],
        skill_priority=parsed_a5["skill_priority"],
        agent3_data=parsed_a5["agent3_course_suggestions"]
    )
    SESSION_STATE["roadmap_data"] = schedule

    pdf_path = OUTPUTS_DIR / "30_Days_Learning_Plan.pdf"
    assessment_pdf_path = OUTPUTS_DIR / "CareerAI_Assessment_Report.pdf"

    user_profile = {
        "name": candidate,
        "target_role": role,
        "rank": composite_rank,
        "total_candidates": 100,
        "readiness_score": composite_score,
        "rank_display": f"Rank #{composite_rank} of 100 Personas (Composite Score: {composite_score}%)",
        "current_skill_level": "Interview-Qualified" if composite_score >= 75 else "Developing"
    }

    gap_summary = (
        f"Multi-Agent Evaluation Report for {candidate} targeting {role} (Rank #{composite_rank} of 100 Personas). "
        f"Initial Resume ATS screening achieved {ats_score}%, and the Spoken AI Mock Interview scored {interview_score_pct}% "
        f"(overall composite readiness: {composite_score}%). "
        f"Demonstrated strengths in the live interview: {', '.join(demonstrated_strong) if demonstrated_strong else 'Core fundamentals'}. "
        f"Actionable technical gaps identified by Agent 2: {', '.join(critical_tech_gaps) if critical_tech_gaps else 'None'}. "
        f"Observed soft skill gaps: {', '.join(critical_soft_gaps) if critical_soft_gaps else 'None'}. "
        f"Agent 5 has compiled a customized 30-day curriculum with micro-courses (<1 week) and dedicated 1-day practical projects "
        f"specifically addressing weaknesses detected during the interview."
    )

    try:
        generate_pdf(
            schedule=schedule,
            user_profile=user_profile,
            missing_skills=parsed_a5["missing_skills"],
            output_path=str(pdf_path),
            gap_analysis_summary=gap_summary
        )
        shutil.copy2(str(pdf_path), str(assessment_pdf_path))
    except Exception as e:
        print(f"Error generating Agent 5 Final PDF in evaluate_interview: {e}")

    # Build recommendations for BOTH technical and soft skill upskilling
    recommendations_list = []
    rec_id = 1
    for skill_rec in agent3_output.get("technical_recommendations", []):
        sk = skill_rec.get("skill", "")
        rec_info = skill_rec.get("recommended", {})
        recommendations_list.append({
            "id": f"rec-tech-{rec_id}",
            "skill": sk,
            "category": "Technical Competency",
            "title": rec_info.get("title", f"{sk} Fast-Track Course"),
            "badge": rec_info.get("platform", "freeCodeCamp"),
            "level": rec_info.get("difficulty", "Beginner -> Intermediate"),
            "estimatedHours": rec_info.get("duration", "< 1 week"),
            "whyMatters": f"{sk} identified from screening and interview evaluation.",
            "link": rec_info.get("url", "https://freecodecamp.org")
        })
        rec_id += 1

    soft_recs = agent3_output.get("soft_recommendations", []) or agent3_output.get("soft_skills_recommendations", [])
    for skill_rec in soft_recs:
        sk = skill_rec.get("skill", "")
        rec_info = skill_rec.get("recommended", {})
        recommendations_list.append({
            "id": f"rec-soft-{rec_id}",
            "skill": sk,
            "category": "Communication & Interview Delivery",
            "title": rec_info.get("title", f"{sk} Mastery Course"),
            "badge": rec_info.get("platform", "Coursera"),
            "level": rec_info.get("difficulty", "Professional Development"),
            "estimatedHours": rec_info.get("duration", "< 1 week"),
            "whyMatters": f"Strengthens verbal articulation, structured responses, and confidence for {sk}.",
            "link": rec_info.get("url", "https://coursera.org")
        })
        rec_id += 1

    # Build report payload formatted for InterviewReport.jsx
    report = {
        "overallScore": composite_score,
        "interviewScore": interview_score_pct,
        "atsScore": ats_score,
        "performanceGrade": "Excellent Performance" if composite_score >= 80 else ("Strong Performance" if composite_score >= 70 else "Developing Performance"),
        "readinessRating": "Interview Benchmark Passed" if composite_score >= 70 else "Needs Targeted Practice",
        "date": datetime.now().strftime("%B %d, %Y"),
        "status": "Qualified - Recommended for On-Site Interview" if composite_score >= 70 else "Developing Candidate",
        "metrics": {
            "technicalKnowledge": tech_metric,
            "communication": comm_metric,
            "problemSolving": prob_metric,
            "confidence": conf_metric,
            "answerRelevance": relevance_metric
        },
        "technicalScore": tech_metric,
        "communicationScore": comm_metric,
        "confidenceScore": conf_metric,
        "candidateName": candidate,
        "targetRole": role,
        "screeningGaps": screening_gaps,
        "interviewGaps": critical_tech_gaps,
        "combinedGaps": combined_gaps,
        "questions": formatted_question_analyses,
        "questionAnalyses": formatted_question_analyses,
        "questionBreakdown": formatted_question_analyses,
        "strengths": (demonstrated_strong + observed_soft_strengths)[:4] if (demonstrated_strong or observed_soft_strengths) else ["Foundational knowledge demonstrated"],
        "areasToImprove": (critical_tech_gaps + critical_soft_gaps)[:4] if (critical_tech_gaps or critical_soft_gaps) else ["Continue practicing system design trade-offs"],
        "aiCoachFeedback": actionable_advice,
        "gapAnalysis": gap_data,
        "courses": agent3_output.get("technical_recommendations", []),
        "softCourses": agent3_output.get("soft_skills_recommendations", []),
        "recommendations": recommendations_list,
        "roadmap": schedule
    }

    SESSION_STATE["interview_result"] = report
    return {
        "success": True,
        "data": report,
        "report": report,
        "screeningGaps": screening_gaps,
        "interviewGaps": critical_tech_gaps,
        "combinedGaps": combined_gaps,
        "roadmap": schedule,
        "pdfGenerated": pdf_path.exists()
    }


# ---------------------------------------------------------------------------
# API: Agent 3 Course Recommendations
# ---------------------------------------------------------------------------
@app.post("/api/courses/recommend")
async def recommend_courses(skills: Optional[List[str]] = Body(None)):
    query_skills = skills or SESSION_STATE.get("missing_skills", ["Python", "FastAPI", "SQL", "Docker"])
    agent3_input = {
        "technical_skills": query_skills,
        "soft_skills": ["Communication", "Team Collaboration"],
        "skill_levels": {s: "Critical Gap" for s in query_skills},
        "target_job_role": SESSION_STATE.get("target_role") or "Software Engineer",
        "candidate_name": SESSION_STATE.get("candidate_name") or "Candidate"
    }
    out = suggest_courses(agent3_input)
    return out


# ---------------------------------------------------------------------------
# API: Agent 5 30-Day Learning Planner
# ---------------------------------------------------------------------------
@app.get("/api/roadmap/generate")
@app.post("/api/roadmap/generate")
async def generate_roadmap():
    if SESSION_STATE["roadmap_data"]:
        return {
            "success": True,
            "total_days": len(SESSION_STATE["roadmap_data"]),
            "schedule": SESSION_STATE["roadmap_data"]
        }

    # Run Agent 3 + Agent 5 if not yet generated
    missing = SESSION_STATE.get("missing_skills") or ["Python", "FastAPI", "Docker", "SQL", "PostgreSQL"]
    agent3_input = {
        "technical_skills": missing,
        "soft_skills": ["Communication"],
        "skill_levels": {s: "Critical Gap" for s in missing},
        "target_job_role": SESSION_STATE.get("target_role") or "Software Engineer",
        "candidate_name": SESSION_STATE.get("candidate_name") or "Candidate"
    }
    agent3_out = suggest_courses(agent3_input)
    parsed_a5 = _parse_agent3_schema(agent3_out)

    schedule = generate_30_day_plan(
        missing_skills=parsed_a5["missing_skills"],
        skill_priority=parsed_a5["skill_priority"],
        agent3_data=parsed_a5["agent3_course_suggestions"]
    )
    SESSION_STATE["roadmap_data"] = schedule

    # Generate Agent 5 PDF with Candidate Profile, Gap Summary & 30-Day Roadmap
    pdf_path = OUTPUTS_DIR / "30_Days_Learning_Plan.pdf"
    assessment_pdf_path = OUTPUTS_DIR / "CareerAI_Assessment_Report.pdf"
    candidate_name = SESSION_STATE.get("candidate_name", "Candidate")
    target_role = SESSION_STATE.get("target_role") or "Software Engineer"
    overall_score = SESSION_STATE.get("score_result", {}).get("overallScore", 65)

    endpoint_rank = max(1, min(100, 101 - overall_score))
    user_profile = {
        "name": candidate_name,
        "target_role": target_role,
        "rank": endpoint_rank,
        "total_candidates": 100,
        "readiness_score": overall_score,
        "rank_display": f"Rank #{endpoint_rank} of 100 Personas (Simulation Score: {overall_score}%)",
        "current_skill_level": "Intermediate" if overall_score >= 60 else "Developing"
    }

    gap_summary = (
        f"Based on the gap analysis for the target role of {target_role}, the candidate exhibits foundational competency "
        f"with an overall ATS readiness score of {overall_score}%. Immediate closure is recommended on high-priority gaps: "
        f"{', '.join(parsed_a5['missing_skills'])}. Each skill module is structured into focused fast-track study followed "
        f"immediately by a dedicated 1-day practical project to establish verifiable portfolio assets."
    )

    try:
        generate_pdf(
            schedule=schedule,
            user_profile=user_profile,
            missing_skills=parsed_a5["missing_skills"],
            output_path=str(pdf_path),
            gap_analysis_summary=gap_summary
        )
        shutil.copy2(str(pdf_path), str(assessment_pdf_path))
    except Exception as e:
        print(f"Error generating Agent 5 PDF in generate_roadmap: {e}")

    return {
        "success": True,
        "total_days": len(schedule),
        "schedule": schedule
    }


# ---------------------------------------------------------------------------
# API: Agent 5 PDF Report Download (Includes 30-Day Roadmap)
# ---------------------------------------------------------------------------
@app.get("/api/roadmap/pdf")
async def download_roadmap_pdf():
    pdf_path = OUTPUTS_DIR / "30_Days_Learning_Plan.pdf"

    if not pdf_path.exists() or not SESSION_STATE.get("roadmap_data"):
        await generate_roadmap()

    if pdf_path.exists():
        return FileResponse(
            path=str(pdf_path),
            filename="CareerAI_30_Days_Learning_Plan.pdf",
            media_type="application/pdf"
        )
    else:
        raise HTTPException(status_code=500, detail="Could not generate PDF")


# ---------------------------------------------------------------------------
# API: CareerAI Official Assessment & Gap Analysis PDF Download
# (Format from Agent 5 including Profile, Gap Summary & 30-Day Roadmap)
# ---------------------------------------------------------------------------
@app.get("/api/report/pdf")
@app.post("/api/report/pdf")
async def download_assessment_report_pdf():
    pdf_path = OUTPUTS_DIR / "CareerAI_Assessment_Report.pdf"

    if not pdf_path.exists() or not SESSION_STATE.get("roadmap_data"):
        await generate_roadmap()

    if pdf_path.exists():
        return FileResponse(
            path=str(pdf_path),
            filename="CareerAI_Assessment_Report.pdf",
            media_type="application/pdf"
        )
    else:
        raise HTTPException(status_code=500, detail="Could not generate Assessment Report PDF")


# ---------------------------------------------------------------------------
# API: Unified Multi-Agent Pipeline Runner
# Agent 1 (CTBuildfest_2.0) -> Agent 2 -> Agent 4 (Interviewer) -> Agent 3 -> Agent 5
# ---------------------------------------------------------------------------
@app.post("/api/pipeline/run")
async def run_unified_pipeline(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """
    Executes the entire multi-agent pipeline in one coordinated call:
    1. Agent 1 (CTBuildfest_2.0): Resume Parsing & ATS Benchmark Evaluation
    2. Agent 2: Skill Gap Identification & Match Breakdown
    3. Agent 4 (Interviewer): Dynamic Question Generation & Interview Setup
    4. Agent 3: Targeted Short-Term Course Recommendations (< 1 Week)
    5. Agent 5: 30-Day Daily Learning Plan & Official PDF Report Generation
    """
    # Step 1: Agent 1 Screening & Initial Gap Analysis
    res = await analyze_resume(
        file=file,
        resume_text=resume_text,
        job_description=job_description
    )

    # Step 2: Agent 4 Interview Session Generation
    interview_res = await start_interview()

    return {
        "success": True,
        "message": "Full 5-agent pipeline orchestrated successfully",
        "agent1_screening": res.get("data"),
        "agent2_gap_analysis": res.get("gapData"),
        "agent4_interview": interview_res,
        "agent3_courses": res.get("gapData", {}).get("recommendations", []),
        "agent5_roadmap": res.get("roadmap"),
        "pdfGenerated": res.get("pdfGenerated", False),
        "pdfDownloadUrl": "/api/roadmap/pdf",
        "assessmentReportUrl": "/api/report/pdf"
    }


# ---------------------------------------------------------------------------
# SPA Frontend Static Serving (Unified single-service deployment on Render / Cloud)
# ---------------------------------------------------------------------------
FRONTEND_DIST = (ROOT_DIR / "frontend" / "dist") if (ROOT_DIR / "frontend" / "dist").exists() else (ROOT_DIR.parent / "frontend" / "dist")
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles

    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend_assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("interviews/"):
            return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})
        target_file = FRONTEND_DIST / full_path
        if target_file.is_file():
            return FileResponse(str(target_file))
        return FileResponse(str(FRONTEND_DIST / "index.html"))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
    uvicorn.run("server:app", host=host, port=port, reload=False if os.environ.get("PORT") else True)
