"""
PDF Report Generator for EduMetrics Individual Student Assessments.
Builds an executive-ready, branded diagnostic PDF dossier using ReportLab,
incorporating career-specific benchmarks, skill-gap analysis, coverage disclosures,
and prioritized personalized learning roadmaps.
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
        topMargin=32,
        bottomMargin=32
    )
    
    student = assessment_result.get("student_data", {})
    target_role = assessment_result.get("target_role", "Data Analyst")
    readiness = assessment_result.get("readiness", {})
    gap_analysis = readiness.get("gap_analysis", {})
    roadmap = assessment_result.get("learning_roadmap", [])
    strengths = assessment_result.get("strengths", [])
    weaknesses = assessment_result.get("weaknesses", [])
    recommendations = assessment_result.get("recommendations", [])
    disclaimer_text = assessment_result.get("disclaimer", "")
    
    styles = getSampleStyleSheet()
    
    # Custom Brand Typography Styles
    section_h1 = ParagraphStyle(
        "SectionHeading1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0F172A")
    )
    bullet_style = ParagraphStyle(
        "BulletText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#334155")
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#64748B")
    )

    story = []
    
    # -------------------------------------------------------------------------
    # 1. Header Banner Table
    # -------------------------------------------------------------------------
    header_data = [
        [
            Paragraph("<b>EduMetrics</b> | Career Assessment Suite", ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=14, textColor=colors.HexColor("#0F172A"))),
            Paragraph("<b>INDIVIDUAL STUDENT DOSSIER</b>", ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.HexColor("#2563EB"), alignment=2))
        ],
        [
            Paragraph("Career-Specific Competency Benchmarking & Readiness Interventions", ParagraphStyle("Sub", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#64748B"))),
            Paragraph(f"Target Role: <b>{target_role}</b>", ParagraphStyle("H3", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#0F172A"), alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceBefore=4, spaceAfter=8))
    
    # -------------------------------------------------------------------------
    # 2. Student Profile Summary Block
    # -------------------------------------------------------------------------
    name = student.get("student_name", "Student")
    stu_id = student.get("student_id", "N/A")
    spec = student.get("specialization", "General")
    sem = student.get("semester", "N/A")
    acad_pct = student.get("academic_percentage", 0.0)
    att_pct = student.get("attendance_percentage", 0.0)
    internship = student.get("internship_status", "Not Recorded")
    projects_count = student.get("projects_count", 0)
    cov_pct = readiness.get("coverage_percentage", 100.0)
    avail_cnt = readiness.get("available_component_count", 6)
    tot_cnt = readiness.get("total_component_count", 6)
    
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
            Paragraph("<b>Academic Marks:</b>", body_style),
            Paragraph(f"{acad_pct:.1f}%" if acad_pct > 0 else "Not Provided", body_bold),
            Paragraph("<b>Attendance:</b>", body_style),
            Paragraph(f"{att_pct:.1f}%" if att_pct > 0 else "Not Provided", body_bold)
        ],
        [
            Paragraph("<b>Internship:</b>", body_style),
            Paragraph(str(internship), body_bold),
            Paragraph("<b>Assessment Coverage:</b>", body_style),
            Paragraph(f"<b>{cov_pct:.1f}%</b> ({avail_cnt}/{tot_cnt} Components)", ParagraphStyle("Cov", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.HexColor("#0D9488")))
        ]
    ]
    info_table = Table(info_data, colWidths=[110, 160, 110, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # 3. Overall Placement Readiness Index Card & Coverage Callout
    # -------------------------------------------------------------------------
    overall_score = readiness.get("overall_score", 0.0)
    tier_label = readiness.get("tier_label", "Developing")
    tier_summary = readiness.get("tier_summary", "")
    missing_list = readiness.get("missing_components", [])
    
    missing_notice = ""
    if missing_list:
        missing_notice = f"<br/><font color='#B45309' size=7.5><b>Data Coverage Disclosure ({cov_pct:.1f}%):</b> Missing {', '.join(missing_list)}. Missing components are excluded; available weights proportionally adjusted.</font>"
        
    score_data = [
        [
            Paragraph(f"<font size=18><b>{overall_score:.1f}</b></font><font size=10>/100</font><br/><font size=7.5 color='#64748B'><b>INDICATIVE READINESS SCORE</b></font>", ParagraphStyle("Score", alignment=1, textColor=colors.HexColor("#0F172A"))),
            Paragraph(f"<b>Classification: {tier_label}</b><br/><font size=8 color='#334155'>{tier_summary}</font>{missing_notice}", ParagraphStyle("Desc", fontSize=8.5, leading=11))
        ]
    ]
    score_table = Table(score_data, colWidths=[140, 400])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('LINEBEFORE', (1,0), (1,-1), 1, colors.HexColor("#BFDBFE")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # 4. Multi-Component Evaluation Breakdown Table
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Readiness Component Breakdown & Normalized Weights", section_h1))
    comp_headers = [
        Paragraph("<b>Readiness Component</b>", body_bold),
        Paragraph("<b>Base Wt</b>", body_bold),
        Paragraph("<b>Active Wt</b>", body_bold),
        Paragraph("<b>Component Score</b>", body_bold),
        Paragraph("<b>Points Scored</b>", body_bold),
        Paragraph("<b>Input Status / Evaluation</b>", body_bold)
    ]
    comp_rows = [comp_headers]
    for comp_name, p_data in readiness.get("components", {}).items():
        if p_data["status"] == "Available":
            score_str = f"<b>{p_data['score']:.1f}</b> / 100"
            pts_str = f"<b>{p_data['weighted_points']:.1f}</b> pts"
        else:
            score_str = "<font color='#94A3B8'>N/A</font>"
            pts_str = "<font color='#94A3B8'>Excluded</font>"
            
        comp_rows.append([
            Paragraph(f"<b>{comp_name}</b>", body_style),
            Paragraph(f"{p_data['base_weight_pct']}%", body_style),
            Paragraph(f"<b>{p_data['adjusted_weight_pct']:.1f}%</b>", body_style),
            Paragraph(score_str, body_style),
            Paragraph(pts_str, body_style),
            Paragraph(str(p_data["description"]), body_style)
        ])
        
    comp_table = Table(comp_rows, colWidths=[130, 45, 50, 75, 65, 175])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # 5. Role Benchmark vs. Student Skill-Gap Comparison Table
    # -------------------------------------------------------------------------
    story.append(Paragraph(f"2. Student vs. Career Benchmark Comparison ({target_role})", section_h1))
    skill_headers = [
        Paragraph("<b>Competency</b>", body_bold),
        Paragraph("<b>Student Level</b>", body_bold),
        Paragraph("<b>Required Level</b>", body_bold),
        Paragraph("<b>Skill Gap</b>", body_bold),
        Paragraph("<b>Meets Benchmark?</b>", body_bold)
    ]
    skill_rows = [skill_headers]
    for item in gap_analysis.get("skill_comparison", []):
        gap = item["gap"]
        if gap > 0:
            status_text = f"<font color='#0D9488'><b>+{gap} (Surplus)</b></font>"
            meets_str = "<font color='#0D9488'><b>YES (Exceeds)</b></font>"
        elif gap == 0:
            status_text = "<font color='#2563EB'><b>Aligned (0)</b></font>"
            meets_str = "<font color='#2563EB'><b>YES (Meets)</b></font>"
        else:
            status_text = f"<font color='#EF4444'><b>{gap} (Deficit)</b></font>"
            meets_str = "<font color='#EF4444'><b>NO (Deficit)</b></font>"
            
        skill_rows.append([
            Paragraph(f"<b>{item['skill']}</b>", body_style),
            Paragraph(f"L{item['student_level']} ({item['student_name']})", body_style),
            Paragraph(f"L{item['target_level']} ({item['target_name']})", body_style),
            Paragraph(status_text, body_style),
            Paragraph(meets_str, body_style)
        ])
        
    skill_table = Table(skill_rows, colWidths=[120, 110, 110, 90, 110])
    skill_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(skill_table)
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # 6. Prioritized Personalized Learning Roadmap
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Prioritized Personalized Learning Roadmap", section_h1))
    road_headers = [
        Paragraph("<b>Priority Focus</b>", body_bold),
        Paragraph("<b>Competency / Deficit</b>", body_bold),
        Paragraph("<b>Specific Learning Objectives & Practical Project</b>", body_bold),
        Paragraph("<b>Timeline</b>", body_bold)
    ]
    road_rows = [road_headers]
    for r in roadmap[:4]:
        objs_text = "<br/>• ".join(r["objectives"][:2])
        desc_text = f"<b>Objectives:</b><br/>• {objs_text}<br/><b>Practical Project:</b> {r['practical_project']}"
        road_rows.append([
            Paragraph(f"<b>Priority {r['priority']}</b>", body_bold),
            Paragraph(f"<b>{r['skill']}</b><br/><font color='#64748B' size=7.5>{r['current_status']} → {r['target_status']}</font>", body_style),
            Paragraph(desc_text, bullet_style),
            Paragraph(str(r["duration"]), body_style)
        ])
        
    road_table = Table(road_rows, colWidths=[65, 115, 300, 60])
    road_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(road_table)
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # 7. Candidate Profile Strengths & Biggest Opportunities
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Diagnostic Strengths vs. Priority Opportunities", section_h1))
    diag_rows = []
    str_text = "<br/>• ".join(strengths[:3]) if strengths else "None recorded."
    weak_text = "<br/>• ".join(weaknesses[:3]) if weaknesses else "None recorded."
    
    diag_rows.append([
        Paragraph("<b>Identified Strongest Areas</b>", ParagraphStyle("S1", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.HexColor("#0D9488"))),
        Paragraph("<b>Biggest Improvement Opportunities</b>", ParagraphStyle("S2", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.HexColor("#B91C1C")))
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
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # 8. Disclaimer & Institutional Sign-off Block
    # -------------------------------------------------------------------------
    disclaimer_full = (
        f"<b>Methodological Notice:</b> {disclaimer_text} The Placement Readiness Index is an indicative "
        "heuristic metric evaluating preparation relative to curriculum expectations and does NOT constitute a statistical probability "
        "or guarantee of employment."
    )
    story.append(Paragraph(disclaimer_full, disclaimer_style))
    story.append(Spacer(1, 10))
    
    signoff_data = [
        [
            Paragraph("<b>Faculty Mentor / Academic Advisor:</b><br/><br/>________________________________________", body_style),
            Paragraph("<b>Placement & Career Services Director:</b><br/><br/>________________________________________", body_style)
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[270, 270])
    signoff_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(signoff_table)
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
