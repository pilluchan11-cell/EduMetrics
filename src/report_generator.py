"""
PDF Report Generator for EduMetrics Individual Student Assessments.
Builds an executive-ready, branded diagnostic PDF dossier using ReportLab.
"""

import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Spacer, 
    Table, 
    TableStyle, 
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


def generate_student_pdf_report(assessment_result: Dict[str, Any]) -> bytes:
    """
    Compiles an individual student assessment into a publication-ready PDF document.
    
    Returns:
        bytes of the generated PDF file.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    student = assessment_result.get("student_data", {})
    target_role = assessment_result.get("target_role", "Data Analyst")
    readiness = assessment_result.get("readiness", {})
    gap_analysis = readiness.get("gap_analysis", {})
    strengths = assessment_result.get("strengths", [])
    weaknesses = assessment_result.get("weaknesses", [])
    recommendations = assessment_result.get("recommendations", [])
    
    styles = getSampleStyleSheet()
    
    # Custom Brand Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B")
    )
    section_h1 = ParagraphStyle(
        "SectionHeading1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#334155")
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#0F172A")
    )
    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E40AF"),
        alignment=1 # Center
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B")
    )

    story = []
    
    # 1. Header Banner Table
    header_data = [
        [
            Paragraph("<b>EduMetrics</b> | Decision Science & Assessment Suite", ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15, textColor=colors.HexColor("#0F172A"))),
            Paragraph("<b>CONFIDENTIAL STUDENT DOSSIER</b>", ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#2563EB"), alignment=2))
        ],
        [
            Paragraph("Individual Student Performance & Career-Readiness Assessment", subtitle_style),
            Paragraph(f"Target Role: <b>{target_role}</b>", ParagraphStyle("H3", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#475569"), alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceBefore=6, spaceAfter=10))
    
    # 2. Student Profile Summary Block
    name = student.get("student_name", "Student")
    stu_id = student.get("student_id", "N/A")
    spec = student.get("specialization", "General")
    sem = student.get("semester", "N/A")
    acad_pct = student.get("academic_percentage", 0.0)
    att_pct = student.get("attendance_percentage", 0.0)
    internship = student.get("internship_status", "Not Completed")
    certs_count = len(student.get("certifications", []))
    projects_count = student.get("projects_count", 0)
    
    info_data = [
        [
            Paragraph("<b>Candidate Name:</b>", body_style),
            Paragraph(str(name), body_bold),
            Paragraph("<b>Student ID:</b>", body_style),
            Paragraph(str(stu_id), body_bold)
        ],
        [
            Paragraph("<b>Specialization:</b>", body_style),
            Paragraph(str(spec), body_bold),
            Paragraph("<b>Semester:</b>", body_style),
            Paragraph(str(sem), body_bold)
        ],
        [
            Paragraph("<b>Academic Aggregate:</b>", body_style),
            Paragraph(f"{acad_pct:.1f}%", body_bold),
            Paragraph("<b>Class Attendance:</b>", body_style),
            Paragraph(f"{att_pct:.1f}%", body_bold)
        ],
        [
            Paragraph("<b>Corporate Internship:</b>", body_style),
            Paragraph(str(internship), body_bold),
            Paragraph("<b>Completed Projects:</b>", body_style),
            Paragraph(f"{projects_count} Project{'s' if projects_count!=1 else ''}", body_bold)
        ]
    ]
    info_table = Table(info_data, colWidths=[110, 160, 110, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))
    
    # 3. Overall Placement Readiness Index Card
    overall_score = readiness.get("overall_score", 0.0)
    tier_label = readiness.get("tier_label", "Developing")
    tier_summary = readiness.get("tier_summary", "")
    tier_color_hex = readiness.get("tier_color", "#2563EB")
    
    score_data = [
        [
            Paragraph(f"<font size=20><b>{overall_score:.1f}</b></font><font size=11>/100</font><br/><font size=8.5 color='#64748B'><b>INDICATIVE READINESS INDEX</b></font>", ParagraphStyle("Score", alignment=1, textColor=colors.HexColor("#0F172A"))),
            Paragraph(f"<b>Classification: {tier_label}</b><br/><font size=8.5 color='#334155'>{tier_summary}</font>", ParagraphStyle("Desc", fontSize=9, leading=12))
        ]
    ]
    score_table = Table(score_data, colWidths=[150, 390])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('LINEBEFORE', (1,0), (1,-1), 1, colors.HexColor("#BFDBFE")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))
    
    # 4. Multi-Component Evaluation Breakdown Table
    story.append(Paragraph("1. Multi-Pillar Readiness Score Breakdown", section_h1))
    comp_headers = [
        Paragraph("<b>Readiness Pillar</b>", body_bold),
        Paragraph("<b>Weight</b>", body_bold),
        Paragraph("<b>Candidate Status / Score</b>", body_bold),
        Paragraph("<b>Pillar Points (Max 100)</b>", body_bold)
    ]
    comp_rows = [comp_headers]
    for pillar_name, p_data in readiness.get("components", {}).items():
        comp_rows.append([
            Paragraph(f"<b>{pillar_name}</b>", body_style),
            Paragraph(f"{p_data['weight']}%", body_style),
            Paragraph(str(p_data["input_val"]), body_style),
            Paragraph(f"<b>{p_data['score']:.1f}</b> / 100 ({p_data['weighted_points']:.1f} pts)", body_bold)
        ])
        
    comp_table = Table(comp_rows, colWidths=[160, 60, 200, 120])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 12))
    
    # 5. Role-Specific Competency Benchmarking & Skill Gap Analysis
    story.append(Paragraph(f"2. Technical Competency Benchmarking vs. {target_role}", section_h1))
    skill_headers = [
        Paragraph("<b>Competency</b>", body_bold),
        Paragraph("<b>Candidate Level</b>", body_bold),
        Paragraph("<b>Role Benchmark</b>", body_bold),
        Paragraph("<b>Variance (Gap)</b>", body_bold),
        Paragraph("<b>Status</b>", body_bold)
    ]
    skill_rows = [skill_headers]
    for item in gap_analysis.get("skill_comparison", []):
        gap = item["gap"]
        if gap > 0:
            status_text = f"<font color='#0D9488'><b>+{gap} Surplus</b></font>"
        elif gap == 0:
            status_text = "<font color='#2563EB'><b>Aligned</b></font>"
        else:
            status_text = f"<font color='#EF4444'><b>{gap} Deficit</b></font>"
            
        skill_rows.append([
            Paragraph(f"<b>{item['skill']}</b>", body_style),
            Paragraph(f"L{item['student_level']} ({item['student_name']})", body_style),
            Paragraph(f"L{item['target_level']} ({item['target_name']})", body_style),
            Paragraph(status_text, body_style),
            Paragraph(item["status"], body_style)
        ])
        
    skill_table = Table(skill_rows, colWidths=[110, 110, 110, 80, 130])
    skill_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(skill_table)
    story.append(Spacer(1, 12))
    
    # 6. Candidate Profile Strengths & Areas for Improvement
    story.append(Paragraph("3. Profile Diagnostics (Strengths & Observations)", section_h1))
    diag_rows = []
    
    str_text = "<br/>• ".join(strengths[:4]) if strengths else "None recorded."
    weak_text = "<br/>• ".join(weaknesses[:4]) if weaknesses else "None recorded."
    
    diag_rows.append([
        Paragraph("<b>Identified Key Strengths</b>", ParagraphStyle("S1", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#0D9488"))),
        Paragraph("<b>Priority Focus Areas & Gaps</b>", ParagraphStyle("S2", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#B91C1C")))
    ])
    diag_rows.append([
        Paragraph(f"• {str_text}", body_style),
        Paragraph(f"• {weak_text}", body_style)
    ])
    diag_table = Table(diag_rows, colWidths=[270, 270])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#ECFDF5")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#FEF2F2")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 12))
    
    # 7. Actionable Recommendations
    story.append(Paragraph("4. Actionable Strategic Interventions", section_h1))
    rec_headers = [
        Paragraph("<b>Intervention Focus</b>", body_bold),
        Paragraph("<b>Priority</b>", body_bold),
        Paragraph("<b>Recommended Strategic Action</b>", body_bold)
    ]
    rec_rows = [rec_headers]
    for r in recommendations[:5]:
        p_color = "#EF4444" if r["priority"] == "Critical" else ("#F59E0B" if r["priority"] == "High" else "#2563EB")
        p_badge = f"<font color='{p_color}'><b>{r['priority'].upper()}</b></font>"
        rec_rows.append([
            Paragraph(f"<b>{r['category']}</b>", body_style),
            Paragraph(p_badge, body_style),
            Paragraph(f"{r['action']}<br/><font color='#64748B' size=7.5><em>Rationale: {r['rationale']}</em></font>", body_style)
        ])
    rec_table = Table(rec_rows, colWidths=[120, 60, 360])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 14))
    
    # 8. Methodological Disclaimer and Institutional Sign-off Block
    disclaimer_text = (
        "<b>Methodological Notice:</b> This diagnostic assessment is generated using deterministic heuristics, "
        "benchmark competency mapping, and academic institutional thresholds. The Placement Readiness Index is an indicative "
        "measure of preparation relative to corporate expectations and does not constitute a statistical probability or guarantee of employment."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    story.append(Spacer(1, 14))
    
    signoff_data = [
        [
            Paragraph("<b>Faculty Mentor / Academic Advisor:</b><br/><br/>________________________________________", body_style),
            Paragraph("<b>Placement & Career Services Director:</b><br/><br/>________________________________________", body_style)
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[270, 270])
    signoff_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(signoff_table)
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
