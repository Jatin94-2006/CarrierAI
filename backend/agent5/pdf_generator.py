"""
Agent 5 - PDF Generator Module
Creates a professional, multi-page PDF for the 30-Day Learning Plan.

Key Features:
  - 4 Clean Columns: Day | Skill / Topic | Recommended Course | Optional Course
  - No project column: Every skill finishes with 1 full dedicated Project Day.
  - No duration mentioned anywhere in the PDF.
  - Candidate Ranking & Readiness Score displayed prominently.
  - Comprehensive Gap Analysis paragraph summary.
  - Fully clickable hyperlinks to free official platforms.
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.colors import HexColor

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
BRAND_BLUE     = HexColor("#1A237E")   # deep navy blue - header / footer bg
ACCENT_BLUE    = HexColor("#1565C0")   # royal blue - section headings, borders
LIGHT_BLUE     = HexColor("#F0F7FF")   # soft blue - alternate row tint
PROJECT_ROW_BG = HexColor("#FFF9C4")   # soft amber tint for dedicated project days
BORDER_AMBER   = HexColor("#FFE082")
WHITE          = colors.white
BLACK          = colors.black
DARK_GREY      = HexColor("#263238")
MID_GREY       = HexColor("#546E7A")

PHASE_COLOURS = {
    "Phase 1 - Fundamentals & Core Skill Acquisition":                 HexColor("#FFF8E1"),
    "Phase 2 - Intermediate Concepts & Practical Hands-on":             HexColor("#E8F5E9"),
    "Phase 3 - Advanced Problem Solving & Tool Mastery":                 HexColor("#FCE4EC"),
    "Phase 4 - Capstone Integration, Revision & Interview Readiness": HexColor("#EDE7F6"),
}

# ---------------------------------------------------------------------------
# Column widths for Landscape A4 (usable ~ 271 mm)
# 4 Clean Columns: Day | Skill / Topic | Recommended Course | Optional Course
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = landscape(A4)
MARGIN    = 1.3 * cm
USABLE_W  = PAGE_W - 2 * MARGIN

COL_WIDTHS = [
    0.07 * USABLE_W,   # Day
    0.43 * USABLE_W,   # Skill / Topic
    0.25 * USABLE_W,   # Recommended Course
    0.25 * USABLE_W,   # Optional Course
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _course_cell(url: str, label: str, style_link: ParagraphStyle) -> Paragraph:
    """Format a clean course cell with title and clickable link, NO duration."""
    if len(label) > 42:
        label = label[:39] + "..."

    html = (
        f'<b>{label}</b><br/>'
        f'<link href="{url}" color="#1565C0"><u>Click to open course</u></link>'
    )
    return Paragraph(html, style_link)


def _url_label(url: str, default_title: str = "") -> str:
    """Return a clean human-readable label without any duration text."""
    if default_title and len(default_title) > 3:
        clean = default_title
        for bad in ["(< 1 Week)", "(< 1 week)", "< 1 Week", "< 1 week", "4.5 hours", "8 hours", "3 hours", "6 hours", "12 weeks", "8 weeks"]:
            clean = clean.replace(bad, "")
        clean = clean.strip(" -:,()")
        if clean and len(clean) <= 38:
            return clean

    mapping = {
        "w3schools.com":        "W3Schools Interactive Tutorial",
        "geeksforgeeks.org":    "GeeksforGeeks Guide",
        "freecodecamp.org":     "freeCodeCamp Tutorial",
        "kaggle.com":           "Kaggle Learn Micro-Course",
        "khanacademy.org":      "Khan Academy Tutorial",
        "learn.microsoft.com":  "Microsoft Learn Module",
        "microsoft.com":        "Microsoft Learn Path",
        "scikit-learn.org":     "scikit-learn Documentation",
        "developer.mozilla.org":"MDN Web Docs",
        "learning.tcsionhub.in":"TCS iON Modular Course",
        "tcsionhub.in":         "TCS iON Course",
        "sqlzoo.net":           "SQLZoo Interactive Practice",
        "youtube.com":          "YouTube Educational Tutorial",
        "youtu.be":             "YouTube Video Walkthrough",
    }
    for key, label in mapping.items():
        if key in url:
            return label
    try:
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        return domain[:25]
    except Exception:
        return url[:25]


# ---------------------------------------------------------------------------
# Page header / footer callback
# ---------------------------------------------------------------------------
def _header_footer(canvas, doc):
    canvas.saveState()

    # --- Header bar ---
    canvas.setFillColor(BRAND_BLUE)
    canvas.rect(0, PAGE_H - 1.2 * cm, PAGE_W, 1.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawCentredString(
        PAGE_W / 2, PAGE_H - 0.80 * cm,
        "30-Day Personalized Learning Roadmap  |  AI-Powered Career Guidance & Job Preparation System"
    )

    # --- Footer bar ---
    canvas.setFillColor(BRAND_BLUE)
    canvas.rect(0, 0, PAGE_W, 0.85 * cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(
        MARGIN, 0.30 * cm,
        "Generated: " + datetime.now().strftime("%B %d, %Y") + "  |  1 Dedicated Project Day after every skill"
    )
    canvas.drawCentredString(PAGE_W / 2, 0.30 * cm, "Agent 5 - 30-Day Learning Planner")
    canvas.drawRightString(PAGE_W - MARGIN, 0.30 * cm, "Page " + str(doc.page))

    canvas.restoreState()


# ---------------------------------------------------------------------------
# Main PDF builder
# ---------------------------------------------------------------------------
def generate_pdf(
    schedule: list[dict[str, Any]],
    user_profile: dict[str, Any],
    missing_skills: list[str],
    output_path: str,
    gap_analysis_summary: str = "",
) -> str:
    """
    Build and save the PDF with:
      - 4 Columns: Day | Skill / Topic | Recommended Course | Optional Course
      - Dedicated 1-Day Project rows following each skill module
      - No duration mentioned
      - Candidate Ranking & Readiness Score
      - Gap Analysis paragraph
    """
    title_style = ParagraphStyle(
        "Title2", fontName="Helvetica-Bold", fontSize=19, leading=24,
        textColor=BRAND_BLUE, alignment=TA_CENTER, spaceAfter=2)

    subtitle_style = ParagraphStyle(
        "Subtitle", fontName="Helvetica", fontSize=10, leading=14,
        textColor=MID_GREY, alignment=TA_CENTER, spaceAfter=4)

    section_style = ParagraphStyle(
        "Section", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
        textColor=ACCENT_BLUE, spaceBefore=6, spaceAfter=3)

    summary_para_style = ParagraphStyle(
        "SummaryPara", fontName="Helvetica", fontSize=8, leading=12,
        textColor=DARK_GREY, alignment=TA_JUSTIFY)

    cell_style = ParagraphStyle(
        "Cell", fontName="Helvetica", fontSize=7.5, leading=10.5,
        textColor=DARK_GREY, wordWrap="CJK")

    cell_project_style = ParagraphStyle(
        "CellProject", fontName="Helvetica-Bold", fontSize=8, leading=11,
        textColor=HexColor("#B71C1C"), wordWrap="CJK")

    cell_bold = ParagraphStyle(
        "CellBold", fontName="Helvetica-Bold", fontSize=8, leading=11,
        textColor=DARK_GREY, alignment=TA_CENTER)

    link_cell_style = ParagraphStyle(
        "LinkCell", fontName="Helvetica", fontSize=7, leading=9.5,
        textColor=DARK_GREY, wordWrap="CJK")

    header_cell_style = ParagraphStyle(
        "HeaderCell", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
        textColor=WHITE, alignment=TA_CENTER)

    phase_style = ParagraphStyle(
        "Phase", fontName="Helvetica-Bold", fontSize=8.5, leading=12,
        textColor=ACCENT_BLUE)

    note_style = ParagraphStyle(
        "Note", fontName="Helvetica-Oblique", fontSize=7.5, leading=10.5,
        textColor=MID_GREY)

    # ---- Document template ----
    doc = BaseDocTemplate(
        output_path,
        pagesize=landscape(A4),
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=1.5 * cm,
        bottomMargin=1.1 * cm,
    )
    frame = Frame(
        MARGIN, 1.1 * cm,
        USABLE_W, PAGE_H - 1.5 * cm - 1.1 * cm,
        id="main",
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
    )
    template = PageTemplate(id="main", frames=[frame], onPage=_header_footer)
    doc.addPageTemplates([template])

    story = []

    # ================================================================
    # 1. HEADER & COVER SECTION
    # ================================================================
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("30-Day Personalized Learning Roadmap", title_style))
    story.append(Paragraph("AI-Powered Career Guidance &amp; Job Preparation System", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=6))

    # ================================================================
    # 2. CANDIDATE PROFILE & RANKING BOX (NO DURATION)
    # ================================================================
    cand_rank = user_profile.get("rank", 1)
    tot_cand  = user_profile.get("total_candidates", 1)
    score     = user_profile.get("readiness_score", 58.3)
    rank_str  = f"<b>Rank #{cand_rank}</b> of {tot_cand}  (Readiness Score: <b>{score}%</b>)"

    profile_rows = [
        [
            Paragraph("<b>Candidate Name:</b>", cell_style),
            Paragraph(str(user_profile.get("name", "Candidate 1")), cell_style),
            Paragraph("<b>Candidate Rank:</b>", cell_style),
            Paragraph(rank_str, cell_style),
        ],
        [
            Paragraph("<b>Target Role:</b>", cell_style),
            Paragraph(f"<b>{user_profile.get('target_role', 'Data Analyst')}</b>", cell_style),
            Paragraph("<b>Current Skill Level:</b>", cell_style),
            Paragraph(str(user_profile.get("current_skill_level", "Intermediate")), cell_style),
        ],
        [
            Paragraph("<b>Plan Scope:</b>", cell_style),
            Paragraph("30 Days  (Structured 4-Phase Curriculum)", cell_style),
            Paragraph("<b>Project Structure:</b>", cell_style),
            Paragraph("<b>Dedicated 1-Day Hands-on Project</b> following each skill module", cell_style),
        ],
    ]
    pCol = [0.15 * USABLE_W, 0.35 * USABLE_W, 0.16 * USABLE_W, 0.34 * USABLE_W]
    profile_table = Table(profile_rows, colWidths=pCol, hAlign="LEFT")
    profile_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX",          (0, 0), (-1, -1), 0.5, ACCENT_BLUE),
        ("INNERGRID",    (0, 0), (-1, -1), 0.25, colors.grey),
        ("TOPPADDING",   (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3.5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 0.2 * cm))

    # ================================================================
    # 3. GAP ANALYSIS SUMMARY PARAGRAPH
    # ================================================================
    story.append(Paragraph("Gap Analysis Summary &amp; Learning Strategy", section_style))

    if not gap_analysis_summary:
        gap_analysis_summary = (
            f"Based on the gap analysis for the target role of {user_profile.get('target_role', 'Data Analyst')}, "
            f"the candidate exhibits solid foundations but needs immediate closure on identified high-priority gaps. "
            f"Key technical and soft skill areas requiring acceleration include {', '.join(missing_skills)}. "
            f"Each skill is structured into focused module study followed immediately by a dedicated 1-day practical project, "
            f"enabling quick practical mastery and demonstrable portfolio assets."
        )

    summary_box_data = [
        [Paragraph(f"<b>Executive Summary:</b> {gap_analysis_summary}", summary_para_style)]
    ]
    summary_box = Table(summary_box_data, colWidths=[USABLE_W], hAlign="LEFT")
    summary_box.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), HexColor("#FFF8E1")),
        ("BOX",          (0, 0), (-1, -1), 0.5, BORDER_AMBER),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_box)
    story.append(Spacer(1, 0.25 * cm))

    # ================================================================
    # 4. 30-DAY SCHEDULE TABLE (4 Columns: Day | Skill / Topic | Recommended Course | Optional Course)
    #    Dedicated project days are rows, NOT a separate column!
    # ================================================================
    story.append(Paragraph("30-Day Learning Schedule", section_style))
    story.append(Spacer(1, 0.08 * cm))

    header_row = [
        Paragraph("Day",                header_cell_style),
        Paragraph("Skill / Topic",      header_cell_style),
        Paragraph("Recommended Course", header_cell_style),
        Paragraph("Optional Course",    header_cell_style),
    ]

    table_data   = [header_row]
    table_styles = [
        ("BACKGROUND",    (0, 0), (-1, 0), BRAND_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
        ("BOX",           (0, 0), (-1, -1), 0.5, ACCENT_BLUE),
        ("INNERGRID",     (0, 0), (-1, -1), 0.2, colors.lightgrey),
        ("ALIGN",         (0, 1), (0, -1), "CENTER"),
    ]

    current_phase = ""
    phase_sep_indices = []
    project_row_indices = []

    for entry in schedule:
        # Phase separator row
        if entry.get("phase") != current_phase:
            current_phase = entry.get("phase")
            phase_bg = PHASE_COLOURS.get(current_phase, LIGHT_BLUE)
            sep_idx  = len(table_data)
            table_data.append([
                Paragraph(f"<b>{current_phase}</b>", phase_style),
                "", "", "",
            ])
            phase_sep_indices.append((sep_idx, phase_bg))

        p1_url   = entry["priority_link"]
        opt_url  = entry["optional_link"]
        p1_label = _url_label(p1_url, entry.get("rec_title", ""))
        opt_label= _url_label(opt_url, entry.get("opt_title", ""))

        is_proj = entry.get("is_project_day", False)
        row_idx = len(table_data)

        if is_proj:
            project_row_indices.append(row_idx)
            topic_cell = Paragraph(f"<b>{entry['skill']}</b>", cell_project_style)
        else:
            topic_cell = Paragraph(entry["skill"], cell_style)

        row = [
            Paragraph(f"<b>{entry['day']}</b>", cell_bold),
            topic_cell,
            _course_cell(p1_url, p1_label, link_cell_style),
            _course_cell(opt_url, opt_label, link_cell_style),
        ]
        table_data.append(row)

    # Apply phase headers styling
    for sep_idx, bg in phase_sep_indices:
        table_styles += [
            ("SPAN",          (0, sep_idx), (-1, sep_idx)),
            ("BACKGROUND",    (0, sep_idx), (-1, sep_idx), bg),
            ("TOPPADDING",    (0, sep_idx), (-1, sep_idx), 4),
            ("BOTTOMPADDING", (0, sep_idx), (-1, sep_idx), 4),
            ("LEFTPADDING",   (0, sep_idx), (-1, sep_idx), 6),
            ("LINEABOVE",     (0, sep_idx), (-1, sep_idx), 0.8, ACCENT_BLUE),
            ("LINEBELOW",     (0, sep_idx), (-1, sep_idx), 0.4, colors.grey),
        ]

    # Apply dedicated Project Day highlighting
    for p_idx in project_row_indices:
        table_styles += [
            ("BACKGROUND", (0, p_idx), (-1, p_idx), PROJECT_ROW_BG),
            ("LINEABOVE",  (0, p_idx), (-1, p_idx), 0.4, HexColor("#FFB300")),
            ("LINEBELOW",  (0, p_idx), (-1, p_idx), 0.4, HexColor("#FFB300")),
        ]

    schedule_table = Table(
        table_data,
        colWidths=COL_WIDTHS,
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=True,
    )
    schedule_table.setStyle(TableStyle(table_styles))
    story.append(schedule_table)

    # ================================================================
    # 5. FOOTER NOTES (NO DURATION)
    # ================================================================
    story.append(Spacer(1, 0.25 * cm))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.grey))
    story.append(Spacer(1, 0.08 * cm))
    story.append(Paragraph(
        "<b>Important Guidelines:</b> (1) All recommended and optional courses are 100% free, publicly accessible resources. "
        "(2) Highlighted <b>Project Days</b> represent dedicated full-day practical implementations immediately following each skill module. "
        "(3) Click any course link to open the respective official learning platform directly.",
        note_style
    ))

    # ================================================================
    # BUILD PDF
    # ================================================================
    doc.build(story)
    return os.path.abspath(output_path)
