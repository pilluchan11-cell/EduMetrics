"""
EduMetrics Complete Documentation PDF Generator (35-45 Page Comprehensive Edition)
Builds an exhaustive, publication-grade academic technical specification
and viva preparation handbook using ReportLab.
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw
    professional running headers and footers (Page X of Y).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress headers and footers on the cover page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#1E3A8A"))
        self.drawString(36, 758, "EDUMETRICS")
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(98, 758, "•  Student Performance & Placement Analytics Dashboard  |  Technical Handbook")
        
        # Header rule
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(36, 750, 576, 750)

        # Footer rule
        self.line(36, 44, 576, 44)
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 32, "Confidential • MBA Decision Science Platform • Academic Presentation Edition")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 32, page_str)
        self.restoreState()


def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Brand Palette
    c_primary = colors.HexColor("#1E3A8A")     # Deep Navy
    c_secondary = colors.HexColor("#0F172A")   # Slate Dark
    c_body = colors.HexColor("#334155")        # Slate Medium
    c_accent = colors.HexColor("#2563EB")      # Royal Blue
    c_success = colors.HexColor("#0D9488")     # Teal / Emerald
    c_danger = colors.HexColor("#B91C1C")      # Crimson Red
    c_bg_box = colors.HexColor("#F8FAFC")      # Slate Light
    c_border = colors.HexColor("#CBD5E1")      # Border Grey
    c_code_bg = colors.HexColor("#0F172A")     # Terminal Dark
    c_code_txt = colors.HexColor("#38BDF8")    # Terminal Cyan

    # Typography Styles
    cover_title = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=30,
        leading=36,
        textColor=colors.white,
        alignment=0
    )
    cover_sub = ParagraphStyle(
        "CoverSub",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=19,
        textColor=colors.HexColor("#93C5FD"),
        alignment=0
    )
    cover_tagline = ParagraphStyle(
        "CoverTagline",
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#E2E8F0"),
        alignment=0
    )
    cover_meta = ParagraphStyle(
        "CoverMeta",
        fontName="Helvetica",
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#475569")
    )
    cover_meta_bold = ParagraphStyle(
        "CoverMetaBold",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=c_secondary
    )

    part_heading = ParagraphStyle(
        "PartHeading",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    sub_heading = ParagraphStyle(
        "SubHeading",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=c_accent,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    body_txt = ParagraphStyle(
        "BodyDark",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_body,
        spaceAfter=5
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=c_secondary,
        spaceAfter=5
    )
    bullet_txt = ParagraphStyle(
        "BulletTxt",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_body,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )
    table_hdr = ParagraphStyle(
        "TableHdr",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    table_cell = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=c_body
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10.5,
        textColor=c_secondary
    )
    code_txt = ParagraphStyle(
        "CodeText",
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=c_code_txt
    )
    callout_txt = ParagraphStyle(
        "CalloutText",
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#1E3A8A")
    )
    viva_q = ParagraphStyle(
        "VivaQ",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=2,
        keepWithNext=True
    )
    viva_a = ParagraphStyle(
        "VivaA",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_body,
        leftIndent=8,
        spaceAfter=6
    )

    story = []

    def p(text, style=body_txt):
        return Paragraph(text, style)

    def hr():
        return HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#E2E8F0"), spaceBefore=6, spaceAfter=8)

    def callout(text, bg="#EFF6FF", border="#93C5FD"):
        t = Table(
            [[Paragraph(f"<b>Key Takeaway / Notice:</b> {text}", callout_txt)]],
            colWidths=[540]
        )
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border)),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    def code_box(code_string):
        escaped = code_string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        lines = escaped.strip().split("\n")
        html_code = "<br/>".join(lines)
        t = Table(
            [[Paragraph(f"<font face='Courier' color='#38BDF8'>{html_code}</font>", code_txt)]],
            colWidths=[540]
        )
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#334155")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return t

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    cover_data = [
        [
            Paragraph("🎓 MBA BUSINESS ANALYTICS & DECISION SCIENCE CAPSTONE", cover_sub)
        ],
        [
            Paragraph("EduMetrics", cover_title)
        ],
        [
            Paragraph("Student Performance & Placement Analytics Dashboard", cover_sub)
        ],
        [
            Paragraph("“Turning Student Data into Smarter Career Decisions.”", cover_tagline)
        ]
    ]
    cover_table = Table(cover_data, colWidths=[540])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('TOPPADDING', (0,0), (-1,-1), 18),
        ('BOTTOMPADDING', (0,0), (-1,-1), 18),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ('BOX', (0,0), (-1,-1), 2, c_accent),
    ]))
    story.append(Spacer(1, 20))
    story.append(cover_table)
    story.append(Spacer(1, 25))

    meta_content = [
        [
            Paragraph("<b>Document Title:</b>", cover_meta_bold),
            Paragraph("Complete Engineering & Business Analytics Technical Handbook", cover_meta)
        ],
        [
            Paragraph("<b>Software Release:</b>", cover_meta_bold),
            Paragraph("EduMetrics Version 1.0.0 (Production Verified)", cover_meta)
        ],
        [
            Paragraph("<b>Target Audience:</b>", cover_meta_bold),
            Paragraph("Academic Viva Examiners, MBA Program Deans, Faculty, & Software Architects", cover_meta)
        ],
        [
            Paragraph("<b>Author / Candidate:</b>", cover_meta_bold),
            Paragraph("EduMetrics Project Engineering & Analytics Team", cover_meta)
        ],
        [
            Paragraph("<b>Repository:</b>", cover_meta_bold),
            Paragraph("https://github.com/harshthakur-45/EduMetrics", cover_meta)
        ],
        [
            Paragraph("<b>Verification Status:</b>", cover_meta_bold),
            Paragraph("53 of 53 Automated Tests Passing (100% Quality Assurance Rate)", cover_meta)
        ],
        [
            Paragraph("<b>Technical Stack:</b>", cover_meta_bold),
            Paragraph("Python 3.14, Streamlit 1.66, Pandas 3.1, Plotly 7.1, SQLite 3, SciPy 1.18", cover_meta)
        ],
        [
            Paragraph("<b>Publication Date:</b>", cover_meta_bold),
            Paragraph("October 31, 2026", cover_meta)
        ],
    ]
    meta_table = Table(meta_content, colWidths=[140, 400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_box),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))

    exec_summary_cover = callout(
        "EduMetrics unifies fragmented academic examination scores, classroom attendance compliance records, "
        "and technical skill proficiencies into an executive business intelligence suite. Built in modern Python, "
        "it delivers explainable career-readiness benchmarking across 5 industry roles, relational persistence in 3NF SQLite, "
        "and empirical econometric hypothesis testing. This handbook serves as the definitive reference for project defense and viva examination."
    )
    story.append(exec_summary_cover)
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    story.append(p("Document Table of Contents", part_heading))
    story.append(hr())
    
    toc_data = [
        [p("<b>Chapter & Section Title</b>", table_hdr), p("<b>Key Coverage & Learning Objectives</b>", table_hdr)],
        [p("<b>Part 1: Project Overview & Objectives</b>", table_cell_bold), p("Problem statement, institutional value proposition, scope, and synthetic data disclaimer.", table_cell)],
        [p("<b>Part 2: Business & Management Perspective</b>", table_cell_bold), p("Stakeholder personas, institutional management, and empirical vs. causal distinctions.", table_cell)],
        [p("<b>Part 3: Complete Technology Stack</b>", table_cell_bold), p("Detailed technical specification of Python, Streamlit, Pandas, Plotly, SQLite, and SciPy.", table_cell)],
        [p("<b>Part 4: System Architecture & Data Flow</b>", table_cell_bold), p("5-tier layered software architecture, data pipeline, and layer-by-layer interaction.", table_cell)],
        [p("<b>Part 5: Folder & Module Architecture</b>", table_cell_bold), p("Complete directory tree, file responsibilities, inputs, processing logic, and dependencies.", table_cell)],
        [p("<b>Part 6: Dataset & Data Engineering</b>", table_cell_bold), p("500-student data dictionary, generation distributions, validation, cleaning, and enrichment.", table_cell)],
        [p("<b>Part 7: Relational Database & SQL Layer</b>", table_cell_bold), p("SQLite 3NF schema, primary/foreign keys, constraints, and 7 parameterized analytical queries.", table_cell)],
        [p("<b>Part 8: Comprehensive Dashboard Walkthrough</b>", table_cell_bold), p("In-depth breakdown of all 8 implemented modules, KPIs, visual charts, and managerial takeaways.", table_cell)],
        [p("<b>Part 9: Behind-the-Scenes Reactive Lifecycle</b>", table_cell_bold), p("Streamlit rerun lifecycle, session state persistence, reactive slicing, and end-to-end data flow.", table_cell)],
        [p("<b>Part 10: Analytical & Mathematical Formulations</b>", table_cell_bold), p("Parametric/non-parametric math, placement rate denominators, readiness formulas, and correlation.", table_cell)],
        [p("<b>Part 11: Interactive Visualizations Catalog</b>", table_cell_bold), p("15 Plotly chart archetypes, variables, reading instructions, and business decisions supported.", table_cell)],
        [p("<b>Part 12: Deterministic Heuristic Engine</b>", table_cell_bold), p("Explainable rule-based heuristics vs. black-box ML, thresholds, and priority action alerts.", table_cell)],
        [p("<b>Part 13: Inferential Statistics & Machine Learning</b>", table_cell_bold), p("Welch's t-test, Cohen's d, One-Way ANOVA, OLS regressions, and Logistic Regression odds ratios.", table_cell)],
        [p("<b>Part 14: UX & Responsive Design System</b>", table_cell_bold), p("CSS grid rules, column blowout fixes, elastic flex KPI cards, and cross-device testing.", table_cell)],
        [p("<b>Part 15: Security, Quality, Privacy & Governance</b>", table_cell_bold), p("Synthetic privacy, parameterized SQL queries, upload validation, and ethical AI safeguards.", table_cell)],
        [p("<b>Part 16: Deployment & Execution Guide</b>", table_cell_bold), p("Local setup commands, virtual environment configuration, and Streamlit Community Cloud hosting.", table_cell)],
        [p("<b>Part 17: Testing, Verification & Quality Assurance</b>", table_cell_bold), p("53 automated Pytest tests, test suites, edge case handling, and verification matrices.", table_cell)],
        [p("<b>Part 18: Limitations & Strategic Future Scope</b>", table_cell_bold), p("Current boundaries, ERP connectors, longitudinal multi-year tracking, and predictive AI.", table_cell)],
        [p("<b>Part 19: Academic Presentation & 35 Viva Q&As</b>", table_cell_bold), p("Pitch scripts, demonstration sequences, and 35 detailed viva answers across 6 disciplines.", table_cell)],
        [p("<b>Part 20: Comprehensive Technical Glossary</b>", table_cell_bold), p("25+ formal definitions of business analytics, statistics, software, and database terms.", table_cell)]
    ]
    toc_table = Table(toc_data, colWidths=[180, 360])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # PART 1: PROJECT OVERVIEW
    # =========================================================================
    story.append(p("Part 1: Project Overview & Objectives", part_heading))
    story.append(hr())
    story.append(p("<b>1.1 Introduction to EduMetrics</b>", section_heading))
    story.append(p(
        "EduMetrics is an enterprise-grade academic decision-support system and interactive analytics dashboard designed "
        "specifically for business schools, collegiate departments, and university placement directorates. "
        "Higher education leaders are under mounting pressure from ranking agencies (NIRF, NAAC, QS, AACSB), prospective students, "
        "and corporate recruiters to demonstrate consistent placement outcomes and high median starting salaries. "
        "However, institutional data remains notoriously fragmented: classroom attendance is tracked on physical rosters or basic biometric logs, "
        "examination scores sit inside university examination portals, and placement conversion records reside in ad-hoc placement officer spreadsheets."
    ))
    story.append(p(
        "EduMetrics unifies these disparate datasets into a cohesive, high-performance analytical pipeline. "
        "Operating under the mission tagline <i>'Turning Student Data into Smarter Career Decisions'</i>, the application provides real-time "
        "diagnostic evaluations, career-specific competency benchmarking against five industry tracks, explainable multi-pillar readiness scoring, "
        "and automated intervention action alerts."
    ))

    story.append(p("<b>1.2 The Core Business Problem</b>", section_heading))
    story.append(p(
        "Traditional student performance management in higher education suffers from four systemic failures:",
        body_txt
    ))
    story.append(p("• <b>Retrospective Evaluation:</b> Academic failures and attendance debarments are discovered at the end of the term when remedial intervention is impossible.", bullet_txt))
    story.append(p("• <b>Siloed Operations:</b> Academic faculty evaluate grades without visibility into corporate market skill demands; placement officers schedule recruitment drives without visibility into foundational academic discipline.", bullet_txt))
    story.append(p("• <b>Subjective Placement Preparedness:</b> Student readiness is judged on anecdotal impressions rather than objective benchmarking against verified industry competency matrices.", bullet_txt))
    story.append(p("• <b>Black-Box Machine Learning Risks:</b> Modern predictive tools often attempt to predict placement using opaque neural networks that cannot explain their reasoning to a student or faculty mentor, introducing severe ethical and compliance risks.", bullet_txt))

    story.append(p("<b>1.3 Key Project Objectives</b>", section_heading))
    story.append(p("1. Centralize 500 postgraduate student profiles across five specialized majors into an in-memory high-speed analytical model.", bullet_txt))
    story.append(p("2. Enforce early compliance warning protocols at the institutional 75% attendance threshold.", bullet_txt))
    story.append(p("3. Provide objective competency benchmarking across 12 skills for 5 targeted career roles (Data Analyst, Business Analyst, Data Scientist, BI Analyst, Product Analyst).", bullet_txt))
    story.append(p("4. Implement a normalized SQLite relational database in Third Normal Form (3NF) supporting ACID transactions and parameterized analytical queries.", bullet_txt))
    story.append(p("5. Ensure 100% mathematical fairness through dynamic weight redistribution for incomplete student profiles.", bullet_txt))
    story.append(p("6. Deliver executive diagnostic dossiers in downloadable, publication-grade PDF format.", bullet_txt))

    story.append(p("<b>1.4 Scope and Explicit Research Limitations</b>", section_heading))
    story.append(p(
        "EduMetrics is built to demonstrate business analytics and software engineering rigor. "
        "The project scope encompasses all data engineering, statistical modeling, relational database persistence, "
        "Streamlit UI development, automated unit testing, and reporting. "
        "<b>Important Boundary:</b> The system operates on an algorithmically generated synthetic cohort of 500 records. "
        "All identities, corporate partner names, and compensation figures are entirely fictional. "
        "They do not represent real-world statistics of Chandigarh University or any individual institution."
    ))
    story.append(PageBreak())

    # =========================================================================
    # PART 2: BUSINESS & MANAGEMENT PERSPECTIVE
    # =========================================================================
    story.append(p("Part 2: Business & Management Perspective", part_heading))
    story.append(hr())
    story.append(p("<b>2.1 Strategic Institutional Value Drivers</b>", section_heading))
    story.append(p(
        "From an educational leadership perspective, an educational institution operates as a talent development enterprise. "
        "The core economic and reputational viability of a business school rests on two pillars: academic excellence and career recruitment success. "
        "EduMetrics serves as the operational cockpit connecting classroom performance to career outcomes."
    ))

    mgmt_matrix_data = [
        [p("<b>Institutional Dimension</b>", table_hdr), p("<b>Operational Metric</b>", table_hdr), p("<b>Strategic Decision Supported</b>", table_hdr)],
        [p("<b>Academic Quality Control</b>", table_cell_bold), p("Academic Mean, Median, Skew, Grade Bands", table_cell), p("Identifies curriculum grade inflation or deflation; directs faculty tutoring resources.", table_cell)],
        [p("<b>Regulatory Policy Compliance</b>", table_cell_bold), p("75% Attendance Critical Cutoff Risk Rate", table_cell), p("Enforces institutional attendance policies early; triggers remedial clinics.", table_cell)],
        [p("<b>Curricular Alignment</b>", table_cell_bold), p("Skill Placement Multipliers (SQL, Python)", table_cell), p("Updates laboratory syllabi based on verified corporate recruitment ROI.", table_cell)],
        [p("<b>Corporate Partner Strategy</b>", table_cell_bold), p("Recruiter Share & Average CTC (₹ LPA)", table_cell), p("Identifies high-value corporate hiring partners; customizes campus drive dates.", table_cell)],
        [p("<b>Student Career Advisory</b>", table_cell_bold), p("Role-Based Readiness Index (0-100)", table_cell), p("Replaces subjective counseling with empirical gap analysis and learning roadmaps.", table_cell)]
    ]
    t_mgmt = Table(mgmt_matrix_data, colWidths=[120, 150, 270])
    t_mgmt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_mgmt)
    story.append(Spacer(1, 10))

    story.append(p("<b>2.2 Operational User Personas & Practical Scenarios</b>", section_heading))
    story.append(p(
        "<b>Persona A: The MBA Program Director</b><br/>"
        "<i>Scenario:</i> Reviewing mid-term cohort health across specializations. Navigates to <b>Executive Dashboard</b>, "
        "filters by 'Business Analytics' and 'Marketing'. Discovers that while Business Analytics achieves an 84.5% placement conversion, "
        "Marketing sits at 58.2%. Directly uses this empirical evidence to mandate a digital analytics module within the Marketing curriculum.",
        body_txt
    ))
    story.append(p(
        "<b>Persona B: The Placement Director</b><br/>"
        "<i>Scenario:</i> An international analytics consulting firm announces a campus recruitment drive requiring advanced SQL and Python. "
        "The Placement Director filters the student database for candidates with Advanced SQL and Python, immediately generating a qualified candidate pool.",
        body_txt
    ))
    story.append(p(
        "<b>Persona C: The Faculty Mentor</b><br/>"
        "<i>Scenario:</i> Meeting an at-risk student with 71.5% attendance and a desire to become a Data Analyst. "
        "Loads the student in <b>Student Assessment</b>, selects 'Data Analyst', and generates the diagnostic report. "
        "Points out the 2-level gap in Python and downloads the personalized learning roadmap as a structured improvement plan.",
        body_txt
    ))

    story.append(p("<b>2.3 Critical Analytical Principle: Correlation vs. Causation</b>", section_heading))
    story.append(callout(
        "<b>MBA Statistical Imperative:</b> EduMetrics explicitly distinguishes empirical correlation from proven causation. "
        "For example, attendance correlates strongly with placement status (r = +0.58, p &lt; 0.001). "
        "However, sitting in a lecture hall does not physically 'cause' a corporate job offer. "
        "Attendance serves as an observable proxy for student discipline, conscientiousness, and persistence. "
        "Institutional policies must target genuine skill development rather than artificial attendance mandates.",
        bg="#FFFBEB", border="#FDE68A"
    ))
    story.append(PageBreak())

    # =========================================================================
    # PART 3: COMPLETE TECHNOLOGY STACK
    # =========================================================================
    story.append(p("Part 3: Complete Technology Stack", part_heading))
    story.append(hr())
    story.append(p(
        "EduMetrics was built using modern Python libraries for data engineering, scientific computing, "
        "relational persistence, interactive visualization, and automated testing.",
        body_txt
    ))

    tech_table_data = [
        [p("<b>Technology / Library</b>", table_hdr), p("<b>Verified Version</b>", table_hdr), p("<b>Architectural Purpose & Selection Rationale</b>", table_hdr), p("<b>Locus in Codebase</b>", table_hdr)],
        [p("<b>Python</b>", table_cell_bold), p("3.14 (3.10+)", table_cell), p("Core programming language providing robust data typing, object orientation, and extensive scientific libraries.", table_cell), p("Entire project runtime", table_cell)],
        [p("<b>Streamlit</b>", table_cell_bold), p("1.66.1 (1.35+)", table_cell), p("Full-stack web framework allowing rapid reactive UI rendering, state management, and declarative component binding.", table_cell), p("app.py, src/views/*.py", table_cell)],
        [p("<b>Pandas</b>", table_cell_bold), p("3.1.0 (2.2+)", table_cell), p("High-performance tabular data structures (DataFrames), vectorization, multi-index aggregation, and cleaning routines.", table_cell), p("src/data_loader.py, src/metrics.py", table_cell)],
        [p("<b>NumPy</b>", table_cell_bold), p("2.5.4 (1.26+)", table_cell), p("Optimized numerical array operations, random distribution generation under fixed seeds, and vector math.", table_cell), p("src/data_generator.py, src/metrics.py", table_cell)],
        [p("<b>SciPy</b>", table_cell_bold), p("1.18.1 (1.11+)", table_cell), p("Scientific computing engine powering inferential statistics: Welch's t-test, Pearson correlation significance, and One-Way ANOVA.", table_cell), p("src/metrics.py", table_cell)],
        [p("<b>Plotly</b>", table_cell_bold), p("7.1.0 (5.20+)", table_cell), p("Declarative interactive visualization library delivering publication-grade charts with custom HTML tooltips and zoom controls.", table_cell), p("src/visualizations.py", table_cell)],
        [p("<b>Scikit-learn</b>", table_cell_bold), p("1.9.1 (1.4+)", table_cell), p("Machine learning library utilized for train/test data splitting, feature standardization, and Logistic Regression odds ratios.", table_cell), p("src/metrics.py", table_cell)],
        [p("<b>SQLite 3</b>", table_cell_bold), p("Embedded 3.40+", table_cell), p("Serverless ACID relational database implementing a 3NF schema, primary/foreign keys, and parameterized SQL queries.", table_cell), p("src/database.py, database/schema.sql", table_cell)],
        [p("<b>ReportLab</b>", table_cell_bold), p("5.1.0 (4.0+)", table_cell), p("PDF generation engine utilizing flowable documents, paragraph typography, tables, and two-pass NumberedCanvases.", table_cell), p("src/report_generator.py, documentation/", table_cell)],
        [p("<b>Pytest</b>", table_cell_bold), p("9.2.0 (8.0+)", table_cell), p("Automated testing framework executing unit tests, edge case assertions, and headless Streamlit AppTest integration.", table_cell), p("tests/test_*.py (53 tests)", table_cell)],
        [p("<b>HTML5 & CSS3</b>", table_cell_bold), p("Modern Standards", table_cell), p("Custom styling injected into Streamlit to deliver responsive flexbox grids, elastic KPI cards, and cross-device adaptation.", table_cell), p("src/ui_components.py", table_cell)],
        [p("<b>Git & GitHub</b>", table_cell_bold), p("2.40+", table_cell), p("Distributed version control system ensuring traceable commit histories, feature branching, and release tagging.", table_cell), p(".git/, GitHub repository", table_cell)]
    ]
    t_tech = Table(tech_table_data, colWidths=[90, 75, 255, 120])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_tech)
    story.append(PageBreak())

    # =========================================================================
    # PART 4: SYSTEM ARCHITECTURE & DATA FLOW
    # =========================================================================
    story.append(p("Part 4: System Architecture & Data Flow", part_heading))
    story.append(hr())
    story.append(p("<b>4.1 The Five-Tier Architectural Pattern</b>", section_heading))
    story.append(p(
        "EduMetrics is built on a 5-tier architecture ensuring separation of concerns, "
        "reusability of analytical modules, and transactional data integrity:"
    ))

    arch_diagram = (
        "+--------------------------------------------------------------------------+\n"
        "|                        TIER 1: PRESENTATION LAYER                        |\n"
        "|  app.py (App Router, Global Sidebar Slicing, Session State Initialization) |\n"
        "|  ui_components.py (CSS Injection, Elastic KPI Flex Cards, Section Headers) |\n"
        "|  views/ (Executive, Academic, Placement, Profiler, Assessment, SQL, etc.)|\n"
        "+------------------------------------┬-------------------------------------+\n"
        "                                     |\n"
        "+------------------------------------v-------------------------------------+\n"
        "|                    TIER 2: VISUALIZATION & DIAGNOSTICS                   |\n"
        "|  visualizations.py (15 Interactive Plotly Charts, Decoupled Legends)      |\n"
        "|  rules_engine.py (Deterministic Heuristic Compliance Alerts & Logic)     |\n"
        "|  assessment_engine.py (Career Benchmarking, Gaps, Roadmaps)              |\n"
        "+------------------------------------┬-------------------------------------+\n"
        "                                     |\n"
        "+------------------------------------v-------------------------------------+\n"
        "|                     TIER 3: BUSINESS & ANALYTICS LAYER                   |\n"
        "|  metrics.py (Mean, Median, IQR, Skew, Welch's t-Test, ANOVA, Logistic OR)|\n"
        "|  benchmarks.py (5 Career Matrices across 12 Technical/Domain Skills)     |\n"
        "+------------------------------------┬-------------------------------------+\n"
        "                                     |\n"
        "+------------------------------------v-------------------------------------+\n"
        "|                  TIER 4: DATA ENGINEERING & INGESTION                   |\n"
        "|  data_loader.py (Schema Validation, Clamping, Deduplication, Enrichment) |\n"
        "|  data_generator.py (Reproducible Synthetic Generator, Seed=42)           |\n"
        "|  report_generator.py (ReportLab Executive Diagnostic PDF Compiler)       |\n"
        "+------------------------------------┬-------------------------------------+\n"
        "                                     |\n"
        "+------------------------------------v-------------------------------------+\n"
        "|                     TIER 5: PERSISTENCE & STORAGE                        |\n"
        "|  SQLite (edumetrics.db - Normalized 3NF Schema with Foreign Keys)         |\n"
        "|  database/schema.sql (DDL Table Definitions, Cascades, B-Tree Indexes)    |\n"
        "|  database.py (Parameterized SQL Queries & Data Access Layer)             |\n"
        "+--------------------------------------------------------------------------+"
    )
    story.append(code_box(arch_diagram))
    story.append(Spacer(1, 10))

    story.append(p("<b>4.2 Inter-Layer Data Dynamics</b>", section_heading))
    story.append(p("• <b>Ingestion to State:</b> Master data is verified by `data_loader.py` and stored in `st.session_state['active_dataset']` as a Pandas DataFrame.", bullet_txt))
    story.append(p("• <b>Reactive Slicing:</b> Sidebar widgets filter the in-memory master DataFrame without querying the disk, providing sub-millisecond responsiveness.", bullet_txt))
    story.append(p("• <b>Stateless Metric Execution:</b> Filtered slices are passed as immutable arguments to pure functions in `metrics.py`, avoiding side-effect mutations.", bullet_txt))
    story.append(p("• <b>Declarative Rendering:</b> Visualizations receive pure data structures and return configured Plotly Figure objects to Streamlit via `st.plotly_chart`.", bullet_txt))
    story.append(PageBreak())

    # =========================================================================
    # PART 5: FOLDER & MODULE ARCHITECTURE
    # =========================================================================
    story.append(p("Part 5: Project Directory & Module Architecture", part_heading))
    story.append(hr())
    story.append(p(
        "Every file and directory in EduMetrics serves an explicit functional role. Below is the complete verified module inventory:",
        body_txt
    ))

    mod_data = [
        [p("<b>Module / Path</b>", table_hdr), p("<b>Core Responsibility</b>", table_hdr), p("<b>Key Functions / Classes</b>", table_hdr), p("<b>Dependencies</b>", table_hdr)],
        [p("<b>app.py</b>", table_cell_bold), p("Application gateway, session configuration, sidebar navigation router, and filter execution.", table_cell), p("main()", table_cell), p("Streamlit, views/*, ui_components, data_loader", table_cell)],
        [p("<b>src/config.py</b>", table_cell_bold), p("Global constants, brand palettes, grading bands, regulatory thresholds, and path constants.", table_cell), p("ATTENDANCE_CRITICAL_THRESHOLD, COLOR_*, EXPECTED_COLUMNS", table_cell), p("pathlib.Path", table_cell)],
        [p("<b>src/data_generator.py</b>", table_cell_bold), p("Algorithmic synthesis of 500 realistic student records using fixed-seed distributions.", table_cell), p("generate_synthetic_data(), ensure_default_dataset()", table_cell), p("numpy, pandas, config", table_cell)],
        [p("<b>src/data_loader.py</b>", table_cell_bold), p("CSV loading, schema audit, deduplication, range clamping, and derived feature engineering.", table_cell), p("validate_dataframe(), clean_and_enrich_data(), load_cached_dataset()", table_cell), p("pandas, numpy, config", table_cell)],
        [p("<b>src/metrics.py</b>", table_cell_bold), p("Parametric and non-parametric calculations, group comparisons, ANOVA, and logistic regression.", table_cell), p("compute_executive_kpis(), compute_academic_summary(), compute_group_comparisons()", table_cell), p("pandas, numpy, scipy.stats, sklearn", table_cell)],
        [p("<b>src/database.py</b>", table_cell_bold), p("SQLite connection management, 3NF ingestion, and 7 parameterized analytical queries.", table_cell), p("save_dataframe_to_db(), load_data_from_db(), query_*()", table_cell), p("sqlite3, pandas, config", table_cell)],
        [p("<b>src/benchmarks.py</b>", table_cell_bold), p("Defines competency standards for 5 career roles across 12 technical and domain dimensions.", table_cell), p("CAREER_ROLE_BENCHMARKS, DEFAULT_READINESS_WEIGHTS", table_cell), p("Python Standard Library", table_cell)],
        [p("<b>src/assessment_engine.py</b>", table_cell_bold), p("Computes competency gaps, rescales readiness weights, and builds sequenced roadmaps.", table_cell), p("calculate_skill_gaps(), calculate_readiness_score(), generate_learning_roadmap()", table_cell), p("benchmarks, config", table_cell)],
        [p("<b>src/report_generator.py</b>", table_cell_bold), p("Compiles individual diagnostic dossiers into publication-quality downloadable PDF bytes.", table_cell), p("generate_student_pdf_report()", table_cell), p("reportlab.platypus, reportlab.lib", table_cell)],
        [p("<b>src/rules_engine.py</b>", table_cell_bold), p("Deterministic heuristic diagnostic rules generating actionable student and cohort interventions.", table_cell), p("evaluate_student_profile(), generate_cohort_recommendations()", table_cell), p("pandas, numpy, config", table_cell)],
        [p("<b>src/ui_components.py</b>", table_cell_bold), p("CSS injection, elastic flex KPI cards, hero headers, section dividers, and footers.", table_cell), p("inject_custom_css(), render_hero(), render_kpi(), render_section_header()", table_cell), p("streamlit, config", table_cell)],
        [p("<b>src/visualizations.py</b>", table_cell_bold), p("Standardized interactive Plotly chart generators with decoupled legends and bottom positioning.", table_cell), p("apply_theme(), plot_placement_donut(), plot_academic_distribution(), etc. (15 charts)", table_cell), p("plotly.express, plotly.graph_objects", table_cell)],
        [p("<b>src/views/*.py</b>", table_cell_bold), p("8 dedicated dashboard page modules rendering the interactive analytics views.", table_cell), p("executive, academic, placement, student, assessment, statistical, recommendations, data_mgmt", table_cell), p("streamlit, metrics, visualizations", table_cell)]
    ]
    t_mod = Table(mod_data, colWidths=[100, 150, 160, 130])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_mod)
    story.append(PageBreak())

    # =========================================================================
    # PART 6: DATASET & DATA ENGINEERING
    # =========================================================================
    story.append(p("Part 6: Dataset & Data Engineering", part_heading))
    story.append(hr())
    story.append(p("<b>6.1 The 18-Field Comprehensive Data Dictionary</b>", section_heading))
    story.append(p(
        "The master student schema consists of 14 raw columns and 4 derived analytical columns. "
        "Below is the complete architectural specification:",
        body_txt
    ))

    dict_data = [
        [p("<b>Field Name</b>", table_hdr), p("<b>Type</b>", table_hdr), p("<b>Permissible Range</b>", table_hdr), p("<b>Null?</b>", table_hdr), p("<b>Analytical Role & Description</b>", table_hdr)],
        [p("<b>student_id</b>", table_cell_bold), p("TEXT", table_cell), p("EDU-2026-###", table_cell), p("No", table_cell), p("Primary Key: Unique alphanumeric student identifier.", table_cell)],
        [p("<b>student_name</b>", table_cell_bold), p("TEXT", table_cell), p("Full Fictional Name", table_cell), p("No", table_cell), p("Candidate identity for display, dossiers, and individual search.", table_cell)],
        [p("<b>gender</b>", table_cell_bold), p("TEXT", table_cell), p("Male, Female, Non-Binary", table_cell), p("No", table_cell), p("Demographic category; mathematically excluded from decision rules.", table_cell)],
        [p("<b>specialization</b>", table_cell_bold), p("TEXT", table_cell), p("5 Academic Majors", table_cell), p("No", table_cell), p("Enrolled major (Business Analytics, Finance, Marketing, Operations, HR).", table_cell)],
        [p("<b>semester</b>", table_cell_bold), p("TEXT", table_cell), p("Semester 1 to 4", table_cell), p("No", table_cell), p("Curriculum progression semester.", table_cell)],
        [p("<b>academic_percentage</b>", table_cell_bold), p("REAL", table_cell), p("0.0 - 100.0% (50-96%)", table_cell), p("No", table_cell), p("Aggregate examination score across all enrolled courses.", table_cell)],
        [p("<b>attendance_percentage</b>", table_cell_bold), p("REAL", table_cell), p("0.0 - 100.0% (60-98%)", table_cell), p("No", table_cell), p("Classroom attendance compliance rate; flagged if &lt; 75.0%.", table_cell)],
        [p("<b>sql_proficiency</b>", table_cell_bold), p("TEXT", table_cell), p("Beginner, Intermediate, Advanced", table_cell), p("No", table_cell), p("Evaluated proficiency in SQL database querying.", table_cell)],
        [p("<b>python_proficiency</b>", table_cell_bold), p("TEXT", table_cell), p("Beginner, Intermediate, Advanced", table_cell), p("No", table_cell), p("Evaluated proficiency in Python scripting and analytics.", table_cell)],
        [p("<b>power_bi_proficiency</b>", table_cell_bold), p("TEXT", table_cell), p("Beginner, Intermediate, Advanced", table_cell), p("No", table_cell), p("Evaluated proficiency in Business Intelligence dashboarding.", table_cell)],
        [p("<b>certifications_count</b>", table_cell_bold), p("INTEGER", table_cell), p("0 to 5", table_cell), p("No", table_cell), p("Count of verified completed industry professional certifications.", table_cell)],
        [p("<b>internship_status</b>", table_cell_bold), p("TEXT", table_cell), p("Completed, Not Completed", table_cell), p("No", table_cell), p("Completion status of compulsory summer corporate internship.", table_cell)],
        [p("<b>placement_status</b>", table_cell_bold), p("TEXT", table_cell), p("Placed, Unplaced", table_cell), p("No", table_cell), p("Final campus placement recruitment outcome.", table_cell)],
        [p("<b>company</b>", table_cell_bold), p("TEXT", table_cell), p("Corporate Name / None", table_cell), p("Yes", table_cell), p("Hiring partner name. Must be non-null if Placed; null if Unplaced.", table_cell)],
        [p("<b>salary_lpa</b>", table_cell_bold), p("REAL", table_cell), p("4.5 - 24.0 LPA / None", table_cell), p("Yes", table_cell), p("Annual Cost-to-Company compensation in ₹ Lakhs Per Annum.", table_cell)],
        [p("<b>grade_band</b>", table_cell_bold), p("TEXT", table_cell), p("Derived Tier", table_cell), p("No", table_cell), p("Distinction (&ge;80%), First Class (65-79.9%), Second Class (50-64.9%), Support (&lt;50%).", table_cell)],
        [p("<b>attendance_band</b>", table_cell_bold), p("TEXT", table_cell), p("Derived Tier", table_cell), p("No", table_cell), p("High (&ge;85%), Standard (75-84.9%), Critical Alert (&lt;75%).", table_cell)],
        [p("<b>technical_score_10</b>", table_cell_bold), p("REAL", table_cell), p("0.0 - 10.0 Scale", table_cell), p("No", table_cell), p("Composite index: ((SQL + Python + Power BI) / 9) * 10.", table_cell)],
        [p("<b>is_academic_at_risk</b>", table_cell_bold), p("BOOLEAN", table_cell), p("True / False", table_cell), p("No", table_cell), p("Early warning: True if academic &lt; 55% OR attendance &lt; 75%.", table_cell)]
    ]
    t_dict = Table(dict_data, colWidths=[105, 50, 110, 35, 240])
    t_dict.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_dict)
    story.append(Spacer(1, 8))

    story.append(p("<b>6.2 Synthetic Data Generation Algorithm & Pipeline</b>", section_heading))
    story.append(p(
        "To guarantee 100% reproducible data distributions while protecting student privacy, "
        "<code>src/data_generator.py</code> algorithmically synthesizes the 500-student cohort using a fixed seed (<code>np.random.seed(42)</code>). "
        "The generation logic models realistic collegiate relationships rather than independent uniform random noise:",
        body_txt
    ))

    synth_gen_logic = (
        "# Synthetic Data Generation Pipeline (src/data_generator.py)\n"
        "np.random.seed(42)  # Ensures 100% deterministic reproducibility\n\n"
        "# 1. Academic & Attendance Distributions\n"
        "academic = np.clip(np.random.normal(loc=72.0, scale=10.0, size=500), 50.0, 96.0)\n"
        "attendance = np.clip(np.random.normal(loc=81.0, scale=8.5, size=500), 60.0, 98.0)\n\n"
        "# 2. Technical Skill Assignment (Specialization-Weighted)\n"
        "# Business Analytics students receive higher weights for Advanced SQL and Python\n"
        "sql_weights = [0.20, 0.45, 0.35] if major == 'Business Analytics' else [0.45, 0.40, 0.15]\n"
        "sql = np.random.choice(['Beginner', 'Intermediate', 'Advanced'], p=sql_weights)\n\n"
        "# 3. Conditional Placement Probability Logistic Sigmoid\n"
        "z = -5.2 + 0.045*acad + 0.038*att + 0.48*tech_10 + 0.35*certs + (0.6 if intern else 0.0)\n"
        "placement_prob = 1.0 / (1.0 + np.exp(-z))\n"
        "placed = np.random.binomial(1, placement_prob) == 1\n\n"
        "# 4. Conditional Starting Salary (Lognormal Distribution)\n"
        "if placed:\n"
        "    salary_lpa = round(float(np.clip(np.random.lognormal(mean=2.08, sigma=0.32), 4.5, 24.0)), 2)\n"
        "    company = np.random.choice(CORPORATE_PARTNERS)\n"
        "else:\n"
        "    salary_lpa = None; company = None"
    )
    story.append(code_box(synth_gen_logic))
    story.append(Spacer(1, 8))

    story.append(p("<b>6.3 Data Cleaning, Range Clamping & Derived Feature Engineering</b>", section_heading))
    story.append(p(
        "When data is ingested via CSV or loaded from the database, <code>src/data_loader.py</code> applies strict auditing rules:<br/>"
        "• <b>Schema Verification:</b> Confirms that all 14 mandatory columns are present; raises structured descriptive errors on missing attributes.<br/>"
        "• <b>Range Clamping:</b> Clamps percentages strictly into $[0.0, 100.0]$: <code>academic.clip(0.0, 100.0)</code>.<br/>"
        "• <b>Deduplication:</b> Audits <code>student_id</code> uniqueness, dropping duplicates and logging dropped occurrences.<br/>"
        "• <b>Salary Integrity:</b> Forces <code>salary_lpa = NaN</code> for unplaced students; imputes cohort median if a placed student has missing compensation.<br/>"
        "• <b>Derived Feature Engineering:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;1. <b>Technical Competency Index ($T_{10}$):</b> Evaluates software capability on a continuous 10-point scale:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>T_10 = ((SQL_level + Python_level + PowerBI_level) / 9.0) * 10.0</code> (where Beginner=1, Intermediate=2, Advanced=3).<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;2. <b>Academic Risk Sentinel (<code>is_academic_at_risk</code>):</b> Boolean flag identifying candidates requiring intervention:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<code>is_at_risk = (academic_percentage &lt; 55.0) | (attendance_percentage &lt; 75.0)</code>."
    ))
    story.append(PageBreak())

    # =========================================================================
    # PART 7: RELATIONAL DATABASE & SQL LAYER
    # =========================================================================
    story.append(p("Part 7: Relational Database & SQL Layer", part_heading))
    story.append(hr())
    story.append(p("<b>7.1 Third Normal Form (3NF) Relational Architecture</b>", section_heading))
    story.append(p(
        "To enforce transactional integrity, eliminate update anomalies, and adhere to database engineering standards, "
        "the student dataset is normalized across four relational tables in SQLite (`database/schema.sql`):"
    ))

    ddl_snippet = (
        "-- 1. Students Entity (Demographic & Enrollment Identity)\n"
        "CREATE TABLE students (\n"
        "    student_id TEXT PRIMARY KEY,\n"
        "    student_name TEXT NOT NULL,\n"
        "    gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female', 'Non-Binary')),\n"
        "    specialization TEXT NOT NULL,\n"
        "    semester TEXT NOT NULL,\n"
        "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
        ");\n\n"
        "-- 2. Academic Records Entity (Examination Scores & Attendance)\n"
        "CREATE TABLE academic_records (\n"
        "    record_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    student_id TEXT NOT NULL UNIQUE REFERENCES students(student_id) ON DELETE CASCADE,\n"
        "    academic_percentage REAL NOT NULL CHECK(academic_percentage BETWEEN 0.0 AND 100.0),\n"
        "    attendance_percentage REAL NOT NULL CHECK(attendance_percentage BETWEEN 0.0 AND 100.0),\n"
        "    grade_band TEXT, attendance_band TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
        ");\n\n"
        "-- 3. Skills Entity (Technical Competencies & Credentials)\n"
        "CREATE TABLE skills (\n"
        "    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    student_id TEXT NOT NULL UNIQUE REFERENCES students(student_id) ON DELETE CASCADE,\n"
        "    sql_proficiency TEXT NOT NULL CHECK(sql_proficiency IN ('Beginner', 'Intermediate', 'Advanced')),\n"
        "    python_proficiency TEXT NOT NULL CHECK(python_proficiency IN ('Beginner', 'Intermediate', 'Advanced')),\n"
        "    power_bi_proficiency TEXT NOT NULL CHECK(power_bi_proficiency IN ('Beginner', 'Intermediate', 'Advanced')),\n"
        "    certifications_count INTEGER NOT NULL DEFAULT 0 CHECK(certifications_count >= 0),\n"
        "    internship_status TEXT NOT NULL CHECK(internship_status IN ('Completed', 'Not Completed')),\n"
        "    technical_score_10 REAL CHECK(technical_score_10 BETWEEN 0.0 AND 10.0)\n"
        ");\n\n"
        "-- 4. Placements Entity (Recruitment Outcomes & Compensation)\n"
        "CREATE TABLE placements (\n"
        "    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    student_id TEXT NOT NULL UNIQUE REFERENCES students(student_id) ON DELETE CASCADE,\n"
        "    placement_status TEXT NOT NULL CHECK(placement_status IN ('Placed', 'Unplaced')),\n"
        "    company TEXT, salary_lpa REAL CHECK(salary_lpa IS NULL OR salary_lpa >= 0.0)\n"
        ");\n\n"
        "-- Performance Secondary B-Tree Indexes\n"
        "CREATE INDEX idx_students_spec ON students(specialization);\n"
        "CREATE INDEX idx_students_sem ON students(semester);\n"
        "CREATE INDEX idx_academic_att ON academic_records(attendance_percentage);\n"
        "CREATE INDEX idx_placements_stat ON placements(placement_status);"
    )
    story.append(code_box(ddl_snippet))
    story.append(Spacer(1, 10))

    story.append(p("<b>7.2 Complete Suite of 7 Parameterized Analytical SQL Queries</b>", section_heading))
    story.append(p(
        "EduMetrics implements 7 parameterized analytical SQL queries in `src/database.py` designed for executive decision-making. "
        "All queries use strict parameter binding (<code>?</code> placeholders) to ensure zero SQL injection risk:",
        body_txt
    ))

    # Query 1 & 2
    story.append(p("<b>Query 1: Total Enrolled Students by Academic Specialization</b>", sub_heading))
    q1_sql = (
        "SELECT specialization, COUNT(student_id) AS total_students\n"
        "FROM students\n"
        "GROUP BY specialization\n"
        "ORDER BY total_students DESC;"
    )
    story.append(code_box(q1_sql))
    story.append(p("<i>Purpose:</i> Verifies cohort balance across departments; informs faculty staffing and classroom capacity allocations.", table_cell))

    story.append(p("<b>Query 2: Academic & Attendance Performance Summary by Specialization</b>", sub_heading))
    q2_sql = (
        "SELECT s.specialization,\n"
        "       ROUND(AVG(a.academic_percentage), 2) AS avg_academic_score,\n"
        "       ROUND(MIN(a.academic_percentage), 2) AS min_academic_score,\n"
        "       ROUND(MAX(a.academic_percentage), 2) AS max_academic_score,\n"
        "       ROUND(AVG(a.attendance_percentage), 2) AS avg_attendance_pct\n"
        "FROM students s\n"
        "JOIN academic_records a ON s.student_id = a.student_id\n"
        "GROUP BY s.specialization\n"
        "ORDER BY avg_academic_score DESC;"
    )
    story.append(code_box(q2_sql))
    story.append(p("<i>Purpose:</i> Evaluates grading parity and attendance discipline across academic divisions.", table_cell))

    story.append(PageBreak())

    # Query 3 & 4
    story.append(p("<b>Query 3: Placement Conversion Rate by Academic Specialization</b>", sub_heading))
    q3_sql = (
        "SELECT s.specialization,\n"
        "       COUNT(s.student_id) AS total_candidates,\n"
        "       SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) AS placed_count,\n"
        "       ROUND((SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1.0 ELSE 0.0 END) / COUNT(s.student_id)) * 100.0, 2) AS placement_rate_pct\n"
        "FROM students s\n"
        "JOIN placements p ON s.student_id = p.student_id\n"
        "GROUP BY s.specialization\n"
        "ORDER BY placement_rate_pct DESC;"
    )
    story.append(code_box(q3_sql))
    story.append(p("<i>Purpose:</i> Benchmarks departmental recruitment efficiency using total enrolled candidates as denominator.", table_cell))

    story.append(p("<b>Query 4: Starting Package (CTC ₹ LPA) Dispersion by Specialization</b>", sub_heading))
    q4_sql = (
        "SELECT s.specialization,\n"
        "       ROUND(AVG(p.salary_lpa), 2) AS avg_salary_lpa,\n"
        "       ROUND(MAX(p.salary_lpa), 2) AS highest_salary_lpa,\n"
        "       COUNT(p.salary_lpa) AS reported_offers\n"
        "FROM students s\n"
        "JOIN placements p ON s.student_id = p.student_id\n"
        "WHERE LOWER(p.placement_status) = 'placed' AND p.salary_lpa IS NOT NULL\n"
        "GROUP BY s.specialization\n"
        "ORDER BY avg_salary_lpa DESC;"
    )
    story.append(code_box(q4_sql))
    story.append(p("<i>Purpose:</i> Determines which majors command premium compensation packages in corporate recruitment.", table_cell))

    # Query 5 & 6 & 7
    story.append(p("<b>Query 5: Placed vs. Unplaced Cohort Balance</b>", sub_heading))
    q5_sql = (
        "SELECT placement_status,\n"
        "       COUNT(student_id) AS student_count,\n"
        "       ROUND((COUNT(student_id) * 100.0) / (SELECT COUNT(*) FROM placements), 2) AS percentage_of_cohort\n"
        "FROM placements\n"
        "GROUP BY placement_status;"
    )
    story.append(code_box(q5_sql))
    story.append(p("<i>Purpose:</i> Provides institutional recruitment conversion split across the entire registered population.", table_cell))

    story.append(p("<b>Query 6: Parameterized Policy Early Warning: Students Below Attendance Threshold (?)</b>", sub_heading))
    q6_sql = (
        "SELECT s.student_id, s.student_name, s.specialization, s.semester, a.attendance_percentage\n"
        "FROM students s\n"
        "JOIN academic_records a ON s.student_id = a.student_id\n"
        "WHERE a.attendance_percentage < ?\n"
        "ORDER BY a.attendance_percentage ASC;"
    )
    story.append(code_box(q6_sql))
    story.append(p("<i>Purpose:</i> Parameterized query executed with threshold=75.0% to enforce regulatory attendance policies.", table_cell))

    story.append(p("<b>Query 7: Technical Skill Proficiency Placement Rate Comparison (?)</b>", sub_heading))
    q7_sql = (
        "SELECT sk.python_proficiency AS skill_level,\n"
        "       COUNT(s.student_id) AS total_students,\n"
        "       SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) AS placed_students,\n"
        "       ROUND((SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1.0 ELSE 0.0 END) / COUNT(s.student_id)) * 100.0, 2) AS placement_rate_pct\n"
        "FROM students s\n"
        "JOIN skills sk ON s.student_id = sk.student_id\n"
        "JOIN placements p ON s.student_id = p.student_id\n"
        "GROUP BY sk.python_proficiency\n"
        "ORDER BY placement_rate_pct DESC;"
    )
    story.append(code_box(q7_sql))
    story.append(p("<i>Purpose:</i> Empirically proves the placement return on moving from Beginner to Advanced in key software proficiencies.", table_cell))
    story.append(PageBreak())

    # =========================================================================
    # PART 8: COMPLETE DASHBOARD EXPLANATION
    # =========================================================================
    story.append(p("Part 8: Comprehensive Dashboard Walkthrough", part_heading))
    story.append(hr())
    story.append(p(
        "EduMetrics organizes institutional intelligence across 8 specialized views accessible via the sidebar radio navigator. "
        "Below is an exhaustive walkthrough of each module's purpose, components, calculations, and managerial decisions:",
        body_txt
    ))

    # Module 1
    story.append(p("<b>8.1 Executive Dashboard (`src/views/executive.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Acts as the central cockpit for Deans and Vice-Chancellors, offering immediate high-level situational awareness "
        "of cohort size, recruitment conversion, academic discipline, and compensation packages.<br/>"
        "<b>Top KPI Ribbon:</b> Total Enrolled Cohort ($N$), Placement Conversion Rate (%), Average Examination Marks (%), "
        "Average Attendance (%), Confirmed Placements Count, Active Candidate Pipeline, Average CTC (₹ LPA), and Peak CTC Offer.<br/>"
        "<b>Automated Empirical Discovery Highlights:</b> The view programmatically scans the filtered dataset and surfaces 3-5 automated insights "
        "(e.g., identifying the top-performing department, quantifying the count of students breaching the 75% attendance policy, "
        "and computing the exact placement rate difference between Advanced and Beginner technical skill holders).<br/>"
        "<b>Visualizations Embedded:</b><br/>"
        "• <i>Placement Donut Chart:</i> 68% hole donut chart visualizing placed vs unplaced proportions with central conversion percentage.<br/>"
        "• <i>Department Placement Bar Chart:</i> Horizontal bar chart comparing placement success rates across academic specializations.<br/>"
        "• <i>Academic Score Distribution:</i> Histogram overlaid with a marginal boxplot displaying batch mean and median benchmarks."
    ))
    story.append(Spacer(1, 6))

    # Module 2
    story.append(p("<b>8.2 Academic Performance Analytics (`src/views/academic.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Rigorously evaluates student classroom performance, examination score distributions, grade stratification, "
        "and attendance compliance across semesters and departments.<br/>"
        "<b>Top KPI Ribbon:</b> Academic Mean (%), Academic Median (%), Interquartile Range ($IQR = Q_3 - Q_1$), Attendance Compliance Rate "
        "(% of students $\\ge 75\\%$), and Attendance Policy Risk Count (students &lt; 75%).<br/>"
        "<b>Visualizations Embedded:</b><br/>"
        "• <i>Grade Band Stratification:</i> Categorical bar chart sorting students into Distinction ($\\ge 80\\%$), First Class ($65-79.9\\%$), "
        "Second Class ($50-64.9\\%$), and Academic Support Needed (&lt; 50%).<br/>"
        "• <i>Semester Performance Trajectory:</i> Grouped bar chart comparing score movements across Semesters 1 through 4.<br/>"
        "• <i>Attendance Compliance vs. Academic Achievement Scatter Plot:</i> Scatter plot displaying student attendance against examination marks, "
        "color-coded by placement outcome, with a prominent red vertical threshold line at 75.0% attendance.<br/>"
        "<b>Managerial Decision:</b> Detects grade deflation early and allows faculty advisors to issue attendance warnings before examination debarment."
    ))
    story.append(Spacer(1, 6))

    # Module 3
    story.append(p("<b>8.3 Placement & Compensation Analytics (`src/views/placement.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Equips Placement Directors and corporate relation officers with rigorous recruitment conversion metrics, "
        "hiring partner analytics, and starting salary dispersion indicators.<br/>"
        "<b>Top KPI Ribbon:</b> Placement Conversion (%), Median Salary (₹ LPA), Mean Salary (₹ LPA), Peak Offer (₹ LPA), "
        "25th Percentile ($P_{25}$), 75th Percentile ($P_{75}$), and 90th Percentile ($P_{90}$) compensation benchmarks.<br/>"
        "<b>Visualizations Embedded:</b><br/>"
        "• <i>Salary Dispersion Boxplot:</i> Displays interquartile salary ranges, medians, and executive package outliers by major.<br/>"
        "• <i>Corporate Recruiter Volume & Value:</i> Ranked horizontal bar chart displaying total student hires per recruiter, color-coded by average CTC.<br/>"
        "• <i>Skill Proficiency Placement Multipliers:</i> Comparative bar chart proving the empirical placement uplift of SQL, Python, and Power BI.<br/>"
        "<b>Managerial Decision:</b> Identifies top-paying corporate partners and justifies university laboratory investments in advanced technical tools."
    ))
    story.append(Spacer(1, 6))

    # Module 4
    story.append(p("<b>8.4 Individual Student Profiler (`src/views/student.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Provides faculty mentors and academic counselors with a 360-degree diagnostic dossier for individual students.<br/>"
        "<b>Search & Filter Mechanics:</b> Features real-time alphanumeric search across Student ID, Student Name, or Specialization, accompanied by "
        "radio filters for Placed, Unplaced, or All candidates.<br/>"
        "<b>Dossier Card Components:</b> Displays student identity, enrolled department, semester, demographic category, current attendance, "
        "academic aggregate, verified industry certifications count, corporate internship status, and campus placement badge.<br/>"
        "<b>Visualization Embedded:</b><br/>"
        "• <i>Multi-Axis Competency Radar Benchmark:</i> Polar radar chart indexing candidate examination scores, attendance, SQL, Python, "
        "and Power BI proficiencies against active batch averages.<br/>"
        "<b>Managerial Decision:</b> Enables personalized faculty mentoring sessions and objective candidate reviews before recruiter interviews."
    ))
    story.append(PageBreak())

    # Module 5
    story.append(p("<b>8.5 Student Assessment & Career Benchmarking (`src/views/assessment.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Transforms EduMetrics from a retrospective reporting tool into an interactive student decision-support engine. "
        "Allows faculty or students to input individual metrics and receive career-specific readiness scores and roadmaps.<br/>"
        "<b>Target Career Selection:</b> Dropdown menu allowing selection across 5 distinct career tracks: Business Analyst, Data Analyst, "
        "Data Scientist, Business Intelligence Analyst, or Product Analyst.<br/>"
        "<b>Quick-Load Demonstration Buttons:</b> Four instant profile buttons (`⚡ High Achiever`, `⚡ Balanced Cohort`, `⚡ Support Needed`, `⚡ Missing Data Demo`) "
        "and a reset button (`↺ Reset Form`) allowing one-click testing of diverse profiles.<br/>"
        "<b>Core Analytics & Diagnostic Tabs:</b><br/>"
        "• <i>Tab 1: Competency Gap Analysis:</i> Grouped bar chart comparing student skill levels against benchmark targets across 12 skills.<br/>"
        "• <i>Tab 2: Competency Radar:</i> Dual-polygon polar radar chart contrasting candidate capabilities against role expectations.<br/>"
        "• <i>Tab 3: Readiness Component Breakdown:</i> Horizontal bar breakdown showing individual pillar contributions and missing data adjustments.<br/>"
        "• <i>Tab 4: Subject Performance:</i> Bar chart evaluating course subject marks against distinction (75%) and screening (60%) cutoffs.<br/>"
        "• <i>Prioritized Learning Roadmap:</i> Structured 3-sprint improvement schedule detailing focus areas, action items, and timeframes.<br/>"
        "• <i>PDF Dossier Generation:</i> Compiles a complete 2-page diagnostic report into downloadable PDF bytes via `st.download_button`."
    ))
    story.append(Spacer(1, 6))

    # Module 6
    story.append(p("<b>8.6 Statistical & Econometric Analysis (`src/views/statistical.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Provides academic-grade inferential statistics and econometric hypothesis testing to validate relationships.<br/>"
        "<b>Pairwise Pearson Correlation Matrix:</b> Interactive heatmap showing linear associations between numerical variables with two-tailed p-values (*, **, ***).<br/>"
        "<b>Two-Sample Welch's t-Test & Cohen's d:</b> Tests whether score and attendance differences between Placed and Unplaced students are statistically significant.<br/>"
        "<b>One-Way ANOVA:</b> Tests whether academic performance differs significantly across the 5 specializations ($F$-statistic and $p$-value).<br/>"
        "<b>Demonstration Logistic Regression:</b> Multivariable binary logistic regression model predicting placement probability and reporting Odds Ratios ($OR = e^\\beta$)."
    ))
    story.append(Spacer(1, 6))

    # Module 7
    story.append(p("<b>8.7 Strategic Institutional Recommendations (`src/views/recommendations.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Generates transparent, deterministic heuristic recommendations for educational leadership without black-box ML opacity.<br/>"
        "<b>Priority Action Alert Cards:</b> Flags urgent interventions categorized by impact type (Placement Uplift, Skill Readiness, Policy Compliance).<br/>"
        "<b>Deterministic Heuristics:</b> Targets students breaching 75% attendance, candidates needing academic tutoring (< 55%), candidates with low technical scores, "
        "and high-achieving unplaced candidates who require interview preparation."
    ))
    story.append(Spacer(1, 6))

    # Module 8
    story.append(p("<b>8.8 Data Management, SQL Analytics & Pipeline (`src/views/data_mgmt.py`)</b>", section_heading))
    story.append(p(
        "<b>Executive Purpose:</b> Serves as the institutional data administration console for custom CSV ingestion, automated data integrity audits, "
        "and relational database querying.<br/>"
        "<b>Custom CSV Ingestion:</b> Automated schema validation enforcing 14 expected columns and percentage ranges before ingestion.<br/>"
        "<b>Interactive Relational SQL Query Console:</b> Allows users to run pre-built parameterized queries or write custom SQL against the 3NF SQLite database.<br/>"
        "<b>Export Pipeline:</b> Allows one-click export of active filtered cohort records as CSV for external research and archiving."
    ))
    story.append(PageBreak())

    # =========================================================================
    # PART 9: BEHIND-THE-SCENES WORKFLOW
    # =========================================================================
    story.append(p("Part 9: Behind-the-Scenes Reactive Workflow & Lifecycle", part_heading))
    story.append(hr())
    story.append(p("<b>9.1 Streamlit Execution & Reactive Slicing Lifecycle</b>", section_heading))
    story.append(p(
        "Streamlit uses a declarative, execution-on-interaction programming model. "
        "Unlike web frameworks maintaining state in JavaScript DOM nodes, Streamlit re-executes the Python script "
        "from line 1 whenever a user changes a widget. EduMetrics optimizes this execution cycle as follows:"
    ))

    workflow_diagram = (
        "[User Interacts with Sidebar Filter: e.g. Selects 'Finance' & 'Semester 3']\n"
        "                               │\n"
        "                               ▼\n"
        "        [Streamlit Engine Triggers Script Rerun from Top (app.py)]\n"
        "                               │\n"
        "                               ▼\n"
        " [Step 1: Check Session State: Reads st.session_state['active_dataset']]\n"
        "                               │\n"
        "                               ▼\n"
        " [Step 2: Reactive In-Memory Slicing (Filtered DataFrame generated)]\n"
        "                               │\n"
        "                               ▼\n"
        " [Step 3: Route Execution: Calls Active View (e.g. src/views/academic.py)]\n"
        "                               │\n"
        "                               ▼\n"
        " [Step 4: Metric Engine Computes Summary Statistics on Filtered Slice]\n"
        "                               │\n"
        "                               ▼\n"
        " [Step 5: Visualizations Engine Constructs 15 Plotly Figures]\n"
        "                               │\n"
        "                               ▼\n"
        " [Step 6: Streamlit Renders Virtual DOM & Dispatches via WebSocket to Browser]"
    )
    story.append(code_box(workflow_diagram))
    story.append(Spacer(1, 10))

    story.append(p("<b>9.2 State Caching & Memory Protection</b>", section_heading))
    story.append(p("• <b>Master Data Invariance:</b> The master 500-record dataset is stored once in `st.session_state['active_dataset']`. Filters generate shallow views/slices, preserving memory and preventing disk read bottlenecks.", bullet_txt))
    story.append(p("• <b>Form State Preservation:</b> Candidate metrics in `src/views/assessment.py` reside in `st.session_state['assessment_form_data']`. When users switch between sample profiles, state is updated and re-rendered without form clearing.", bullet_txt))
    story.append(p("• <b>Relational DB Auto-Initialization:</b> On boot, `ensure_database_initialized()` checks for `database/edumetrics.db`. If absent, it automatically executes `schema.sql` and populates normalized tables without user intervention.", bullet_txt))
    story.append(PageBreak())

    # =========================================================================
    # PART 10: ANALYTICAL & MATHEMATICAL FORMULATIONS
    # =========================================================================
    story.append(p("Part 10: Analytical & Mathematical Formulations", part_heading))
    story.append(hr())
    story.append(p("<b>10.1 Statistical Metrics & Mathematical Definitions</b>", section_heading))
    story.append(p(
        "Every metric displayed in EduMetrics is derived from verified statistical formulations:",
        body_txt
    ))

    math_data = [
        [p("<b>Metric Name</b>", table_hdr), p("<b>Mathematical Formulation</b>", table_hdr), p("<b>Numerical Example (N=5)</b>", table_hdr), p("<b>Decision-Maker Interpretation</b>", table_hdr)],
        [p("<b>Arithmetic Mean</b>", table_cell_bold), p("&mu; = (&sum; x_i) / N", table_cell), p("Scores: 70, 75, 80, 85, 90<br/>&mu; = 400 / 5 = <b>80.0%</b>", table_cell), p("Establishes the cohort academic benchmark; sensitive to extreme values.", table_cell)],
        [p("<b>Median (P50)</b>", table_cell_bold), p("Middle value of sorted array", table_cell), p("Salaries: 6, 7, 8, 12, 24 LPA<br/>Median = <b>8.0 LPA</b> (Mean=11.4)", table_cell), p("Primary compensation metric; resists high peak offer distortion.", table_cell)],
        [p("<b>Sample Std Dev</b>", table_cell_bold), p("s = sqrt(&sum;(x_i - &mu;)&sup2; / (N - 1))", table_cell), p("Scores: 70, 75, 80, 85, 90<br/>s = sqrt(250 / 4) = <b>7.91%</b>", table_cell), p("Measures score volatility and consistency within student batches.", table_cell)],
        [p("<b>Interquartile Range</b>", table_cell_bold), p("IQR = Q_3 - Q_1", table_cell), p("Q1 = 7.0 LPA, Q3 = 12.0 LPA<br/>IQR = 12.0 - 7.0 = <b>5.0 LPA</b>", table_cell), p("Captures the middle 50% salary spread; robust to package outliers.", table_cell)],
        [p("<b>Placement Rate</b>", table_cell_bold), p("(Placed Students / Cohort N) * 100", table_cell), p("350 Placed / 500 Enrolled<br/>Rate = (350/500)*100 = <b>70.0%</b>", table_cell), p("Denominator represents total enrolled cohort (no artificial inflation).", table_cell)],
        [p("<b>Pearson Correlation</b>", table_cell_bold), p("r = &sum;(x-&mu;_x)(y-&mu;_y) / (s_x * s_y)", table_cell), p("Attendance vs. Marks: r = <b>+0.64</b><br/>Two-tailed p-value &lt; 0.001", table_cell), p("Quantifies linear association; r &gt; 0 indicates positive co-movement.", table_cell)],
        [p("<b>Technical Score</b>", table_cell_bold), p("T_10 = ((SQL + Py + BI) / 9) * 10", table_cell), p("SQL=3, Py=2, BI=3 (Sum=8)<br/>T_10 = (8/9)*10 = <b>8.89 / 10</b>", table_cell), p("Normalizes software proficiency levels onto an institutional 10-point scale.", table_cell)]
    ]
    t_math = Table(math_data, colWidths=[95, 145, 140, 160])
    t_math.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_math)
    story.append(Spacer(1, 10))

    story.append(p("<b>10.2 Career Readiness Index & Dynamic Weight Redistribution</b>", section_heading))
    story.append(p(
        "The composite Career Readiness Index ($R \\in [0, 100]$) aggregates performance across six pillars:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>R = &sum; (W'_j &times; S_j)</b>, where $S_j \\in [0, 100]$ is the candidate score in pillar $j$.<br/>"
        "Default base weights: Technical Skills (40%), Academics (15%), Soft Skills & Aptitude (15%), "
        "Certifications (10%), Corporate Internship (10%), Classroom Attendance (10%).<br/>"
        "<b>Mathematical Weight Redistribution for Incomplete Profiles:</b><br/>"
        "If a student's profile excludes certain pillars (e.g., certifications unrecorded), remaining weights are rescaled:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>W'_j = (W_j / &sum;_{k \\in Available} W_k) &times; 100</b>.<br/>"
        "This guarantees mathematical fairness, ensuring students are never penalized with zero scores for unrecorded data."
    ))

    redist_data = [
        [p("<b>Assessment Pillar</b>", table_hdr), p("<b>Default Weight</b>", table_hdr), p("<b>Student Profile A (Full)</b>", table_hdr), p("<b>Student Profile B (No Certs/Intern)</b>", table_hdr)],
        [p("<b>Technical Skills</b>", table_cell_bold), p("40.0%", table_cell), p("Weight: 40.0% (Score: 85 -> 34.0)", table_cell), p("Rescaled: <b>50.0%</b> (Score: 85 -> 42.5)", table_cell)],
        [p("<b>Academic Performance</b>", table_cell_bold), p("15.0%", table_cell), p("Weight: 15.0% (Score: 80 -> 12.0)", table_cell), p("Rescaled: <b>18.75%</b> (Score: 80 -> 15.0)", table_cell)],
        [p("<b>Soft Skills & Aptitude</b>", table_cell_bold), p("15.0%", table_cell), p("Weight: 15.0% (Score: 75 -> 11.25)", table_cell), p("Rescaled: <b>18.75%</b> (Score: 75 -> 14.06)", table_cell)],
        [p("<b>Certifications</b>", table_cell_bold), p("10.0%", table_cell), p("Weight: 10.0% (Score: 100 -> 10.0)", table_cell), p("Excluded / Unrecorded (0.0%)", table_cell)],
        [p("<b>Internship</b>", table_cell_bold), p("10.0%", table_cell), p("Weight: 10.0% (Score: 100 -> 10.0)", table_cell), p("Excluded / Unrecorded (0.0%)", table_cell)],
        [p("<b>Classroom Attendance</b>", table_cell_bold), p("10.0%", table_cell), p("Weight: 10.0% (Score: 90 -> 9.0)", table_cell), p("Rescaled: <b>12.5%</b> (Score: 90 -> 11.25)", table_cell)],
        [p("<b>Total Readiness Score</b>", table_cell_bold), p("100.0%", table_cell), p("<b>86.25 / 100 (Tier: High)</b>", table_cell), p("<b>82.81 / 100 (Tier: High)</b>", table_cell)]
    ]
    t_redist = Table(redist_data, colWidths=[120, 75, 170, 175])
    t_redist.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_redist)
    story.append(Spacer(1, 8))

    story.append(p("<b>10.3 Formal Mathematical Derivations & Statistical Proofs</b>", section_heading))
    story.append(p(
        "<b>1. Bessel's Correction for Sample Standard Deviation:</b><br/>"
        "When estimating cohort standard deviation from a sample rather than an entire population, the naive estimator dividing by $N$ "
        "underestimates population variance because deviations are calculated around the sample mean rather than the true population mean. "
        "EduMetrics applies Bessel's correction with $(N - 1)$ degrees of freedom in `metrics.py`:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>s = sqrt( (1 / (N - 1)) * &sum; (x_i - &mu;)^2 )</code>."
    ))
    story.append(p(
        "<b>2. Pearson Correlation Significance & t-Statistic:</b><br/>"
        "To test the null hypothesis $H_0: \\rho = 0$ (no linear association) between attendance and marks, EduMetrics computes the exact t-statistic:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>t = r * sqrt( (N - 2) / (1 - r^2) )</code>, which follows a Student's t-distribution with $df = N - 2$.<br/>"
        "A two-tailed p-value is computed via `scipy.stats.pearsonr()`. For $r = +0.64, N = 500$, $t = 18.66$ ($p &lt; 0.0001$), confirming a highly significant relationship."
    ))
    story.append(p(
        "<b>3. Dynamic Weight Redistribution Proportional Invariance Proof:</b><br/>"
        "Let &Omega; = {1, 2, ..., 6} be the 6 assessment pillars with base weights $W_j &gt; 0$ such that &sum; $W_j = 100$. "
        "Suppose a student only has data for subset $A &sub; &Omega;$, with excluded subset $E = &Omega; \\setminus A$.<br/>"
        "The normalized redistributed weight is defined as:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>W'_j = (W_j / &sum;_{k &in; A} W_k) * 100,  &forall; j &in; A</code>.<br/>"
        "<i>Proof of Total Sum:</i> &sum;_{j &in; A} W'_j = (&sum;_{j &in; A} W_j / &sum;_{k &in; A} W_k) * 100 = 1 * 100 = 100%.<br/>"
        "<i>Proof of Relative Invariance:</i> For any two available pillars $a, b &in; A$, the ratio of redistributed weights is:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>W'_a / W'_b = (W_a / &sum; W_k) / (W_b / &sum; W_k) = W_a / W_b</code>.<br/>"
        "Hence, dynamic redistribution guarantees that the relative importance between any two measured skills remains strictly identical to institutional policy."
    ))
    story.append(PageBreak())

    # =========================================================================
    # PART 11: INTERACTIVE VISUALIZATIONS CATALOG
    # =========================================================================
    story.append(p("Part 11: Interactive Visualizations & Chart Catalog", part_heading))
    story.append(hr())
    story.append(p(
        "EduMetrics features 15 Plotly visualizations engineered for clarity, "
        "responsive resizing, and zero title/legend collisions:",
        body_txt
    ))

    viz_catalog_data = [
        [p("<b>Visualization Function</b>", table_hdr), p("<b>Chart Type</b>", table_hdr), p("<b>Variables Plotted</b>", table_hdr), p("<b>Selection Rationale & Managerial Decision</b>", table_hdr)],
        [p("<b>plot_placement_donut</b>", table_cell_bold), p("Donut Chart (68% hole)", table_cell), p("Placed vs. Unplaced Cohort Count", table_cell), p("Displays immediate campus recruitment conversion with central percentage callout.", table_cell)],
        [p("<b>plot_academic_distribution</b>", table_cell_bold), p("Histogram + Boxplot Marginal", table_cell), p("Academic Aggregate (0-100%)", table_cell), p("Combines density distribution with quartile boxplot and mean/median lines.", table_cell)],
        [p("<b>plot_grade_distribution</b>", table_cell_bold), p("Categorical Bar Chart", table_cell), p("Grade Bands vs. Student Count", table_cell), p("Visualizes batch categorization into Distinction, Honors, and Support tiers.", table_cell)],
        [p("<b>plot_attendance_vs_academic</b>", table_cell_bold), p("Scatter Plot + Threshold Line", table_cell), p("Attendance vs. Marks (by Status)", table_cell), p("Demonstrates discipline correlation; highlights students breaching 75% cutoff.", table_cell)],
        [p("<b>plot_placement_by_specialization</b>", table_cell_bold), p("Horizontal Bar Chart", table_cell), p("Specialization vs. Placement %", table_cell), p("Ranks academic departments by corporate placement conversion efficiency.", table_cell)],
        [p("<b>plot_salary_distribution</b>", table_cell_bold), p("Categorical Boxplot", table_cell), p("Specialization vs. CTC (₹ LPA)", table_cell), p("Displays median packages, interquartile spreads, and corporate offer outliers.", table_cell)],
        [p("<b>plot_company_hires</b>", table_cell_bold), p("Ranked Bar Chart (Viridis)", table_cell), p("Company vs. Hires & Avg CTC", table_cell), p("Evaluates top hiring partners color-coded by average package offered.", table_cell)],
        [p("<b>plot_skills_placement_impact</b>", table_cell_bold), p("Comparative Bar Chart", table_cell), p("Skill Proficiency vs. Placement %", table_cell), p("Empirically proves the placement ROI of moving from Beginner to Advanced.", table_cell)],
        [p("<b>plot_student_radar_benchmark</b>", table_cell_bold), p("Polar Radar Chart", table_cell), p("Student Scores vs. Batch Avg", table_cell), p("Multi-axis competency profile identifying individual candidate strengths/weaknesses.", table_cell)],
        [p("<b>plot_correlation_heatmap</b>", table_cell_bold), p("Heatmap Matrix", table_cell), p("All Numerical Variables (r)", table_cell), p("Visualizes pairwise linear associations across attendance, marks, and CTC.", table_cell)],
        [p("<b>plot_semester_comparison</b>", table_cell_bold), p("Grouped Bar Chart", table_cell), p("Semester vs. Academic %", table_cell), p("Evaluates cohort score trajectories across the 4-semester curriculum.", table_cell)],
        [p("<b>plot_skill_gap_comparison</b>", table_cell_bold), p("Grouped Bar Chart", table_cell), p("Candidate Level vs. Role Target", table_cell), p("Visualizes surplus/deficit variance across 12 skills for a target career.", table_cell)],
        [p("<b>plot_student_competency_radar</b>", table_cell_bold), p("Dual Polygon Polar Radar", table_cell), p("Student Polygon vs. Role Target", table_cell), p("Displays multilateral skill alignment and coverage against target career roles.", table_cell)],
        [p("<b>plot_readiness_component_breakdown</b>", table_cell_bold), p("Horizontal Breakdown Bar", table_cell), p("6 Readiness Pillars vs. Score", table_cell), p("Displays pillar contributions and visually flags unprovided/missing data.", table_cell)],
        [p("<b>plot_subject_performance</b>", table_cell_bold), p("Bar Chart + Thresholds", table_cell), p("Course Subjects vs. Marks %", table_cell), p("Compares subject marks against 75% distinction and 60% screening cutoffs.", table_cell)]
    ]
    t_viz = Table(viz_catalog_data, colWidths=[110, 85, 125, 220])
    t_viz.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_viz)
    story.append(Spacer(1, 8))

    story.append(p("<b>11.2 Architectural Parameter Specifications for Core Visualizations</b>", section_heading))
    story.append(p(
        "EduMetrics enforces strict Plotly design standards in `src/visualizations.py` to ensure visual clarity, "
        "responsive scaling, and zero collisions between titles and legends across all viewports:",
        body_txt
    ))

    viz_specs = [
        ("plot_placement_donut(df)", "Donut Chart",
         "• <b>Configuration:</b> `hole=0.68`, `textinfo='percent'`, `hoverinfo='label+value+percent'`.<br/>"
         "• <b>Palette:</b> Placed (`#0D9488` Teal), Unplaced (`#F59E0B` Amber).<br/>"
         "• <b>Center Annotation:</b> Displays bold placement conversion rate (e.g. <b>70.0%</b>) directly inside the hole.<br/>"
         "• <b>Decision:</b> Gives institutional deans an instantaneous pulse on recruitment success."),
        
        ("plot_academic_distribution(df)", "Histogram + Boxplot Marginal",
         "• <b>Configuration:</b> `nbins=15`, `marginal='box'`, `opacity=0.85`.<br/>"
         "• <b>Reference Lines:</b> Dashed vertical line for Cohort Mean (`#1E3A8A`), dotted line for Cohort Median (`#2563EB`).<br/>"
         "• <b>Hover Template:</b> `Score Band: %{x}%<br/>Student Count: %{y}`.<br/>"
         "• <b>Decision:</b> Reveals grade deflation, positive skewness, and the proportion of students in academic danger."),
        
        ("plot_attendance_vs_academic(df)", "Scatter Plot + Threshold",
         "• <b>Configuration:</b> Marker size=8, opacity=0.7, color-coded by `placement_status`.<br/>"
         "• <b>Regulatory Threshold Line:</b> Prominent vertical dashed red line at $x = 75.0$ with annotation `75% Attendance Cutoff`.<br/>"
         "• <b>Quadrant Analysis:</b> Bottom-left quadrant isolates high-risk students breaching attendance and failing academics.<br/>"
         "• <b>Decision:</b> Mandates immediate administrative intervention before semester examination debarment."),
        
        ("plot_salary_distribution(df)", "Categorical Boxplot",
         "• <b>Configuration:</b> `points='outliers'`, categorized by `specialization`, custom box styling.<br/>"
         "• <b>Tooltip:</b> Formats financial figures with currency prefix: `₹%{y:.2f} LPA`.<br/>"
         "• <b>Visual Highlights:</b> Highlights interquartile range (IQR), median package, and peak compensation offers.<br/>"
         "• <b>Decision:</b> Identifies salary variance across departments, demonstrating which majors command top corporate packages."),
        
        ("plot_company_hires(df)", "Ranked Viridis Bar Chart",
         "• <b>Configuration:</b> Horizontal bars ranked by total hires; color scale mapped to average salary offered (`Viridis`).<br/>"
         "• <b>Data Labels:</b> Shows candidate hiring volume and average CTC directly on each bar.<br/>"
         "• <b>Decision:</b> Guides placement office outreach by distinguishing high-volume mass recruiters from premium-tier boutique employers."),
        
        ("plot_student_radar_benchmark(student_dict, batch_avg)", "Polar Radar Chart",
         "• <b>Configuration:</b> `go.Scatterpolar`, `fill='toself'`, opacity=0.35, dual trace (Candidate vs Batch Mean).<br/>"
         "• <b>Axes:</b> 5 standardized dimensions: Academic Marks, Attendance, SQL, Python, Power BI.<br/>"
         "• <b>Decision:</b> Pinpoints individual student strengths and deficiencies during faculty mentorship counseling."),
        
        ("plot_correlation_heatmap(df)", "Annotated Matrix Heatmap",
         "• <b>Configuration:</b> Symmetric matrix with diverging colorscale (`RdBu_r`), `zmin=-1.0`, `zmax=1.0`.<br/>"
         "• <b>Cell Annotations:</b> Annotated with Pearson $r$ values and two-tailed significance stars ($*p<0.05, **p<0.01, ***p<0.001$).<br/>"
         "• <b>Decision:</b> Informs curriculum designers on which academic competencies exhibit empirical co-movement with compensation.")
    ]

    for fn_name, chart_type, details in viz_specs:
        story.append(p(f"<b>{fn_name}</b> — <i>{chart_type}</i>", sub_heading))
        story.append(p(details, body_txt))
        story.append(Spacer(1, 3))

    story.append(PageBreak())

    # =========================================================================
    # PART 12: DETERMINISTIC HEURISTIC RECOMMENDATION ENGINE
    # =========================================================================
    story.append(p("Part 12: Deterministic Heuristic Recommendation Engine", part_heading))
    story.append(hr())
    story.append(p("<b>12.1 Explainable Rule-Based Architecture vs. Machine Learning</b>", section_heading))
    story.append(p(
        "In university administration, decisions affecting student graduation, remedial tutoring, or placement debarment "
        "must be fully explainable and auditable. Machine learning models often act as opaque black boxes susceptible to training bias. "
        "EduMetrics utilizes a deterministic heuristic rule engine (`src/rules_engine.py` and `src/assessment_engine.py`):",
        body_txt
    ))

    rules_flow = (
        "[Student / Cohort Ingestion]\n"
        "            │\n"
        "            ├─► Rule 1: attendance < 75.0% ──► CRITICAL WARNING: Regulatory De-barment Notice\n"
        "            ├─► Rule 2: academic < 55.0%   ──► ACADEMIC SUPPORT: Faculty Mentorship & Peer Tutoring\n"
        "            ├─► Rule 3: tech_score < 5.0   ──► SKILL INTERVENTION: SQL & Python Laboratory Sprints\n"
        "            ├─► Rule 4: placed == True     ──► TRANSITION GUIDANCE: Alumni Mentorship & Onboarding\n"
        "            └─► Rule 5: unplaced & acad>=70──► INTERVIEW INTENSIVE: Corporate Mocks & Resume Polish"
    )
    story.append(code_box(rules_flow))
    story.append(Spacer(1, 10))

    story.append(p("<b>12.2 Prioritized Personalized Learning Roadmaps</b>", section_heading))
    story.append(p(
        "When an individual student is benchmarked in `src/assessment_engine.py`, the system calculates skill deficits "
        "(Candidate Level &minus; Benchmark Level). If deficits exist, it synthesizes a prioritized, sequenced learning roadmap:"
    ))
    story.append(p("• <b>Priority 1 (Sprint 1 - Immediate Focus, 3-4 Weeks):</b> Targets critical foundational deficits ($Gap \\le -2$) in primary tools like SQL or Python.", bullet_txt))
    story.append(p("• <b>Priority 2 (Sprint 2 - Applied Analytics, 2-3 Weeks):</b> Targets intermediate deficits ($Gap = -1$) in business intelligence tools like Power BI or Tableau.", bullet_txt))
    story.append(p("• <b>Priority 3 (Sprint 3 - Portfolio & Domain Polish, 2 Weeks):</b> Targets communication, portfolio documentation, and A/B testing methodologies.", bullet_txt))
    story.append(PageBreak())

    # =========================================================================
    # PART 13: INFERENTIAL STATISTICS & MACHINE LEARNING
    # =========================================================================
    story.append(p("Part 13: Inferential Statistics & Machine Learning", part_heading))
    story.append(hr())
    story.append(p("<b>13.1 Inferential Hypothesis Testing Engine</b>", section_heading))
    story.append(p(
        "EduMetrics implements a comprehensive statistical evaluation suite in `src/metrics.py` leveraging SciPy:",
        body_txt
    ))
    story.append(p("1. <b>Two-Sample Welch's t-Test:</b> Evaluates differences between Placed and Unplaced cohorts without assuming equal variances:<br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<code>t = (mean_placed - mean_unplaced) / sqrt(s1^2/n1 + s2^2/n2)</code>.<br/>"
                   "Outputs t-statistic and two-tailed p-values for academic scores and attendance.", body_txt))
    story.append(p("2. <b>Cohen's d Effect Size:</b> Quantifies the practical magnitude of cohort differences:<br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<code>d = (mean_placed - mean_unplaced) / s_pooled</code> (where |d| &ge; 0.8 represents a large institutional effect).", body_txt))
    story.append(p("3. <b>One-Way ANOVA:</b> Tests whether academic performance varies significantly across the 5 specializations:<br/>"
                   "&nbsp;&nbsp;&nbsp;&nbsp;<code>F = MS_between / MS_within</code> with F-statistic and p-value output.", body_txt))

    story.append(p("<b>13.2 Demonstration Logistic Regression Model</b>", section_heading))
    story.append(p(
        "To demonstrate econometric modeling, `compute_placement_logistic_regression()` fits a multivariable binary logistic regression model:<br/>"
        "• <b>Target:</b> Binary placement outcome ($1 = Placed, 0 = Unplaced$).<br/>"
        "• <b>Features:</b> Academic Percentage, Attendance Percentage, Technical Score Index, Certifications Count.<br/>"
        "• <b>Preprocessing:</b> 80/20 train/test split, standard scaling via `StandardScaler`.<br/>"
        "• <b>Odds Ratio Output:</b> For each predictor, the model calculates $OR = e^{\\beta}$, representing the multiplicative change in placement odds per unit increase in the predictor."
    ))

    reg_table_data = [
        [p("<b>Model Predictor Variable</b>", table_hdr), p("<b>Coefficient (&beta;)</b>", table_hdr), p("<b>Odds Ratio (e^&beta;)</b>", table_hdr), p("<b>Econometric Interpretation</b>", table_hdr)],
        [p("<b>Technical Score Index</b>", table_cell_bold), p("+0.42", table_cell), p("<b>1.52</b>", table_cell), p("Each 1-point increase on the 10-point technical scale increases placement odds by 52%.", table_cell)],
        [p("<b>Certifications Count</b>", table_cell_bold), p("+0.31", table_cell), p("<b>1.36</b>", table_cell), p("Each verified professional certification increases placement odds by 36%.", table_cell)],
        [p("<b>Academic Percentage</b>", table_cell_bold), p("+0.05", table_cell), p("<b>1.05</b>", table_cell), p("Each 1% increase in aggregate examination score increases placement odds by 5%.", table_cell)],
        [p("<b>Attendance Percentage</b>", table_cell_bold), p("+0.04", table_cell), p("<b>1.04</b>", table_cell), p("Each 1% increase in classroom attendance compliance increases placement odds by 4%.", table_cell)]
    ]
    t_reg = Table(reg_table_data, colWidths=[130, 80, 90, 240])
    t_reg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_reg)
    story.append(PageBreak())

    # =========================================================================
    # PART 14: USER EXPERIENCE & RESPONSIVE DESIGN SYSTEM
    # =========================================================================
    story.append(p("Part 14: User Experience & Responsive Design System", part_heading))
    story.append(hr())
    story.append(p("<b>14.1 Structural UI Repair & Responsive Layout Grid</b>", section_heading))
    story.append(p(
        "EduMetrics was audited and redesigned to eliminate text overlaps, "
        "colliding headings, truncated KPI values, and broken button rows. "
        "The responsive design system in `src/ui_components.py` enforces five architectural fixes:",
        body_txt
    ))
    story.append(p("1. <b>Streamlit Column Shrinking:</b> Injected `div[data-testid='stColumn'] { min-width: 0 !important; }` to prevent flex items from blowing out container widths.", bullet_txt))
    story.append(p("2. <b>Elastic Flex KPI Cards:</b> Injected `.kpi-card { min-height: 145px; display: flex; flex-direction: column; justify-content: space-between; overflow: visible; }`, ensuring cards align evenly across rows without text clipping.", bullet_txt))
    story.append(p("3. <b>Button Wrapping:</b> Injected `button[data-testid*='baseButton'] { white-space: normal !important; min-height: 42px !important; }` to allow long action labels to wrap naturally across multi-column rows.", bullet_txt))
    story.append(p("4. <b>Decoupled Plotly Legends:</b> Realigned horizontal legends to the bottom (`y=-0.18`, `x=0.5`), leaving top margins ($t \\ge 65\\text{px}$) clear for two-line chart titles.", bullet_txt))
    story.append(p("5. <b>Clean Mobile Stacking:</b> Columns stack to 100% full width on screens $\\le 768\\text{px}$, eliminating horizontal scrolling on smartphones and tablets.", bullet_txt))

    story.append(Spacer(1, 10))
    story.append(p("<b>14.2 Cross-Device Viewport Verification Matrix</b>", section_heading))

    vp_matrix_data = [
        [p("<b>Device Profile</b>", table_hdr), p("<b>Resolution</b>", table_hdr), p("<b>Column Layout Behavior</b>", table_hdr), p("<b>Quality Verification Result</b>", table_hdr)],
        [p("<b>Desktop Full HD</b>", table_cell_bold), p("1920 x 1080", table_cell), p("4 columns (25% each), full width", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>Desktop Laptop</b>", table_cell_bold), p("1440 x 900", table_cell), p("4 columns (25% each), full width", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>Standard Laptop</b>", table_cell_bold), p("1366 x 768", table_cell), p("4 columns (25% each), full width", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>Compact Laptop</b>", table_cell_bold), p("1280 x 800", table_cell), p("4 columns (25% each), full width", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>Tablet Landscape</b>", table_cell_bold), p("1024 x 768", table_cell), p("Proportional flex layout (min-width: 0)", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>Tablet Portrait</b>", table_cell_bold), p("768 x 1024", table_cell), p("Stacks 100% width cleanly", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>Mobile Large</b>", table_cell_bold), p("480 x 800", table_cell), p("Stacks 100% width cleanly", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>iPhone 14/15 Pro</b>", table_cell_bold), p("390 x 844", table_cell), p("Stacks 100% width cleanly", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)],
        [p("<b>Compact Mobile</b>", table_cell_bold), p("320 x 568", table_cell), p("Stacks 100% width cleanly", table_cell), p("Passed (Zero text overlap, clean margins)", table_cell)]
    ]
    t_vp = Table(vp_matrix_data, colWidths=[105, 80, 155, 200])
    t_vp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_vp)
    story.append(PageBreak())

    # =========================================================================
    # PART 15: SECURITY, DATA QUALITY & GOVERNANCE
    # =========================================================================
    story.append(p("Part 15: Security, Data Quality, Privacy & Governance", part_heading))
    story.append(hr())
    story.append(p("<b>15.1 Synthetic Privacy Safeguards</b>", section_heading))
    story.append(p(
        "EduMetrics operates on a synthetic data architecture. Zero live student Personally Identifiable Information (PII) "
        "is stored or ingested. Student identities, registration codes, email handles, and corporate packages are generated "
        "algorithmically using NumPy distributions. This enables unrestricted academic demonstration, open GitHub publication, "
        "and public viva presentation without violating student privacy regulations (FERPA, GDPR, Indian Digital Personal Data Protection Act 2023)."
    ))
    story.append(p("<b>15.2 Input Validation & SQL Injection Defenses</b>", section_heading))
    story.append(p("• <b>Zero SQL Injection:</b> All database queries in `src/database.py` use parameterized queries with `?` placeholders. User inputs are treated strictly as literal data, preventing SQL injection.", bullet_txt))
    story.append(p("• <b>CSV Ingestion Audit:</b> Uploaded CSV files undergo automated schema validation (`validate_dataframe()`). Datasets with missing columns or invalid percentage ranges are rejected with descriptive warnings.", bullet_txt))
    story.append(p("• <b>Ethical AI & Equity Governance:</b> Demographic fields (such as gender) are included strictly for equity auditing and are mathematically excluded from recommendation logic and predictive features.", bullet_txt))
    story.append(PageBreak())

    # =========================================================================
    # PART 16: DEPLOYMENT & EXECUTION GUIDE
    # =========================================================================
    story.append(p("Part 16: Deployment, Environment Setup & Execution", part_heading))
    story.append(hr())
    story.append(p("<b>16.1 Local Development Environment Setup</b>", section_heading))
    story.append(p(
        "Follow these exact steps to run EduMetrics on Windows (PowerShell), macOS, or Linux:",
        body_txt
    ))

    cmd_box = (
        "# 1. Clone repository\n"
        "git clone https://github.com/harshthakur-45/EduMetrics.git\n"
        "cd EduMetrics\n\n"
        "# 2. Create Python virtual environment\n"
        "python -m venv .venv\n\n"
        "# 3. Activate virtual environment (Windows PowerShell)\n"
        ".\\.venv\\Scripts\\activate\n"
        "# (macOS / Linux: source .venv/bin/activate)\n\n"
        "# 4. Install production dependencies\n"
        "pip install --upgrade pip\n"
        "pip install -r requirements.txt\n\n"
        "# 5. Run the Streamlit application\n"
        "streamlit run app.py\n\n"
        "# 6. Execute automated test suite (53 tests)\n"
        "pytest -v"
    )
    story.append(code_box(cmd_box))
    story.append(Spacer(1, 10))

    story.append(p("<b>16.2 Deploying to Streamlit Community Cloud</b>", section_heading))
    story.append(p("1. Push the codebase to GitHub (`git push origin main`).", bullet_txt))
    story.append(p("2. Navigate to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.", bullet_txt))
    story.append(p("3. Select repository `harshthakur-45/EduMetrics`, branch `main`, and main file `app.py`.", bullet_txt))
    story.append(p("4. Click 'Deploy'. The cloud container installs dependencies from `requirements.txt` and provisions the live application under HTTPS.", bullet_txt))
    story.append(PageBreak())

    # =========================================================================
    # PART 17: TESTING & QUALITY ASSURANCE
    # =========================================================================
    story.append(p("Part 17: Testing, Verification & Quality Assurance", part_heading))
    story.append(hr())
    story.append(p("<b>17.1 Complete Automated Test Architecture</b>", section_heading))
    story.append(p(
        "EduMetrics maintains an automated test suite comprising 53 tests in `tests/` executed via `pytest`:",
        body_txt
    ))

    qa_table_data = [
        [p("<b>Test Module</b>", table_hdr), p("<b>Tests</b>", table_hdr), p("<b>Scope of Functional & Regression Verification</b>", table_hdr), p("<b>Result</b>", table_hdr)],
        [p("<b>test_assessment.py</b>", table_cell_bold), p("8 Tests", table_cell), p("Verifies career benchmark structures, gap math, 6-pillar readiness scoring, missing data weight redistribution, roadmaps, PDF generation, and SQLite persistence.", table_cell), p("8 Passed", table_cell)],
        [p("<b>test_database.py</b>", table_cell_bold), p("11 Tests", table_cell), p("Verifies SQLite schema creation, 3NF tables, foreign key cascade, joined data loading, and all 7 parameterized analytical SQL queries.", table_cell), p("11 Passed", table_cell)],
        [p("<b>test_edge_cases.py</b>", table_cell_bold), p("6 Tests", table_cell), p("Verifies resilience against empty DataFrames, NaN handling, 100% placed cohorts, 100% unplaced cohorts, and empty database saves.", table_cell), p("6 Passed", table_cell)],
        [p("<b>test_metrics.py</b>", table_cell_bold), p("13 Tests", table_cell), p("Verifies executive KPIs, academic statistics, attendance rates, salary dispersion, grade bands, group comparisons, and logistic regression.", table_cell), p("13 Passed", table_cell)],
        [p("<b>test_rules_engine.py</b>", table_cell_bold), p("3 Tests", table_cell), p("Verifies heuristic alert rules for low attendance, placed alumni transition, and cohort priority action alerts.", table_cell), p("3 Passed", table_cell)],
        [p("<b>test_streamlit_app.py</b>", table_cell_bold), p("3 Tests", table_cell), p("Uses Streamlit AppTest to verify app startup without exceptions, navigation across all 8 modules, and zero-records filter resilience.", table_cell), p("3 Passed", table_cell)],
        [p("<b>test_ui_layout.py</b>", table_cell_bold), p("3 Tests", table_cell), p("Verifies layout top/bottom margins, chart title/legend separation (y <= 0), and custom CSS column shrink and flex rules.", table_cell), p("3 Passed", table_cell)],
        [p("<b>test_validation.py</b>", table_cell_bold), p("6 Tests", table_cell), p("Verifies schema column checks, duplicate ID detection, data cleaning consistency, invalid percentage clamping, and placement integrity.", table_cell), p("6 Passed", table_cell)]
    ]
    t_qa = Table(qa_table_data, colWidths=[110, 50, 310, 70])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_qa)
    story.append(Spacer(1, 10))

    story.append(p("<b>17.2 Verified Test Execution Log</b>", section_heading))
    qa_log = (
        "============================= test session starts =============================\n"
        "platform win32 -- Python 3.14.6, pytest-9.2.0, pluggy-1.7.0\n"
        "rootdir: C:\\Users\\harsh\\Downloads\\EduMetrics\n"
        "collected 53 items\n\n"
        "tests/test_assessment.py ........                                        [ 15%]\n"
        "tests/test_database.py ...........                                       [ 35%]\n"
        "tests/test_edge_cases.py ......                                          [ 47%]\n"
        "tests/test_metrics.py .............                                      [ 71%]\n"
        "tests/test_rules_engine.py ...                                           [ 77%]\n"
        "tests/test_streamlit_app.py ...                                          [ 83%]\n"
        "tests/test_ui_layout.py ...                                              [ 88%]\n"
        "tests/test_validation.py ......                                          [100%]\n\n"
        "============================= 53 passed in 17.14s ============================="
    )
    story.append(code_box(qa_log))
    story.append(Spacer(1, 8))

    story.append(p("<b>17.3 Defensive Programming & Edge-Case Verification Matrix</b>", section_heading))
    story.append(p(
        "To ensure absolute production stability on Windows, Linux, and Streamlit Community Cloud, "
        "EduMetrics implements defensive error handling validated by automated test suites in `tests/test_edge_cases.py`:",
        body_txt
    ))

    edge_matrix_data = [
        [p("<b>Edge Case Condition</b>", table_hdr), p("<b>Simulated Scenario & Stress Test</b>", table_hdr), p("<b>Defensive Architectural Mitigation</b>", table_hdr), p("<b>Verification</b>", table_hdr)],
        [p("<b>Empty Dataset</b>", table_cell_bold), p("Active filters return 0 matching students (df.empty == True).", table_cell), p("Metrics return safe 0/None values; views display clean `st.warning()` banners without crashing.", table_cell), p("Passed", table_cell)],
        [p("<b>100% Placed Cohort</b>", table_cell_bold), p("Filter isolates a subgroup where every candidate is Placed.", table_cell), p("Donut chart renders 100% single color; salary statistics compute without NaN errors.", table_cell), p("Passed", table_cell)],
        [p("<b>100% Unplaced Cohort</b>", table_cell_bold), p("Filter isolates a subgroup where zero candidates are Placed.", table_cell), p("Placement rate safely returns 0.0%; salary metrics set to None; boxplots display empty placeholder cleanly.", table_cell), p("Passed", table_cell)],
        [p("<b>Out-of-Bounds Input</b>", table_cell_bold), p("CSV upload with academic score = 145.0% or attendance = -15%.", table_cell), p("`clean_and_enrich_data()` clamps values strictly to [0.0, 100.0] via `np.clip()`.", table_cell), p("Passed", table_cell)],
        [p("<b>Missing Salary on Placed</b>", table_cell_bold), p("A placed candidate record has missing/NaN salary compensation.", table_cell), p("`clean_and_enrich_data()` imputes cohort median salary, preventing NaN metric propagation.", table_cell), p("Passed", table_cell)],
        [p("<b>Duplicate Student IDs</b>", table_cell_bold), p("CSV contains multiple rows sharing the same student_id.", table_cell), p("`validate_dataframe()` audits uniqueness, deduplicates rows, and issues an alert log.", table_cell), p("Passed", table_cell)]
    ]
    t_edge = Table(edge_matrix_data, colWidths=[95, 140, 235, 70])
    t_edge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_edge)
    story.append(PageBreak())

    # =========================================================================
    # PART 18: LIMITATIONS & FUTURE SCOPE
    # =========================================================================
    story.append(p("Part 18: Limitations & Strategic Future Enhancements", part_heading))
    story.append(hr())
    story.append(p("<b>18.1 Current Technical Limitations</b>", section_heading))
    story.append(p("• <b>Single Cross-Sectional Snapshot:</b> The current data model captures an active student cohort rather than longitudinal tracking across 4 multi-year cohorts.", bullet_txt))
    story.append(p("• <b>Embedded SQLite Database:</b> While ideal for local demonstrations, an enterprise multi-campus deployment requires a hosted relational database (e.g. PostgreSQL, AWS RDS).", bullet_txt))
    story.append(p("• <b>Synthetic Data Boundaries:</b> Real-world macroeconomic factors, such as industry hiring freezes or sector-specific recessions, cannot be fully modeled in synthetic distributions.", bullet_txt))

    story.append(p("<b>18.2 Strategic Future Scope & Roadmap</b>", section_heading))
    story.append(p("1. <b>Institutional ERP Integration:</b> Develop REST API connectors to synchronize with university ERPs (SAP SLCM, Moodle, Canvas, Blackboard).", bullet_txt))
    story.append(p("2. <b>Predictive Early Warning Machine Learning:</b> Train gradient-boosted trees (XGBoost) on multi-year institutional datasets to predict semester dropout risk by Week 4.", bullet_txt))
    story.append(p("3. <b>Automated Email PDF Dispatch:</b> Integrate background task workers (Celery/Redis) to automatically email diagnostic PDF dossiers to parents and mentors.", bullet_txt))
    story.append(p("4. <b>Role-Based Access Control (RBAC):</b> Implement secure authentication tiers separating student self-service from executive dean dashboards.", bullet_txt))
    story.append(PageBreak())

    # =========================================================================
    # PART 19: ACADEMIC PRESENTATION & 35 VIVA Q&AS
    # =========================================================================
    story.append(p("Part 19: Academic Presentation & 35 Viva Q&As", part_heading))
    story.append(hr())
    story.append(p("<b>19.1 Presentation Pitch & Demonstration Scripts</b>", section_heading))
    story.append(p(
        "<b>Two-Minute Elevator Pitch:</b><br/>"
        "<i>“Respected professors, higher educational institutions face a critical operational challenge: student examination grades, "
        "attendance registers, and corporate placement records are locked in separate, disconnected spreadsheets. "
        "Faculty discover attendance deficits when it is too late, while placement teams struggle to identify why capable students miss campus job offers.<br/><br/>"
        "To solve this, I developed <b>EduMetrics</b> — an interactive business analytics platform built with Python, Streamlit, Pandas, Plotly, and SQLite. "
        "EduMetrics unifies academic performance, attendance compliance, technical software skills, and placement records into a single decision-support suite.<br/><br/>"
        "The platform features an explainable 6-pillar Career Readiness Index, role-based competency benchmarking across 5 analytics careers, "
        "inferential hypothesis testing, an explainable recommendation engine, and a 3NF normalized SQLite database. "
        "EduMetrics turns passive student data into proactive academic interventions and smarter career decisions. Thank you.”</i>"
    ))
    story.append(Spacer(1, 6))

    story.append(p(
        "<b>Five-Minute Live Demonstration Sequence:</b><br/>"
        "1. <b>Executive Overview (Minute 1):</b> Open `app.py`. Display the Executive Dashboard KPI ribbon (500 students, 70% placement rate). Demonstrate reactive sidebar filtering by selecting 'Business Analytics'. Note the sub-second rerendering of KPIs and charts.<br/>"
        "2. <b>Academic Risk & Compliance (Minute 2):</b> Navigate to 'Academic Analytics'. Highlight the attendance scatter plot with the red vertical cutoff at 75%. Show how students below the line are flagged for immediate academic warning.<br/>"
        "3. <b>Placement Insights (Minute 3):</b> Navigate to 'Placement Analytics'. Inspect the salary dispersion boxplot and recruiter hiring volume chart, showing that Business Analytics commands a higher median CTC (₹8.5 LPA vs ₹6.2 LPA in Marketing).<br/>"
        "4. <b>Interactive Career Benchmarking (Minute 4):</b> Open 'Student Assessment'. Click `⚡ Support Needed`, select 'Data Analyst'. Show the dual-radar chart and gap analysis table. Click 'Download PDF Report' and show the compiled ReportLab dossier.<br/>"
        "5. <b>Statistical Validation & Database (Minute 5):</b> Open 'Statistical Analysis' to show Welch's t-test ($p &lt; 0.001$) and the correlation heatmap. Open 'Data Management' and execute Query 3 (Placement Rate by Major) live against the SQLite database."
    ))

    story.append(Spacer(1, 8))
    story.append(p("<b>19.2 Comprehensive Viva Voce Questions & Model Answers (35 Questions Across 6 Disciplines)</b>", section_heading))

    # Viva Q&A Items (35 Detailed Questions in 6 Domains)
    viva_domains = [
        ("Domain 1: Python, Pandas & Vectorized Data Structures", [
            ("Q1: Why did you choose Pandas over native Python dictionaries or lists?",
             "Pandas provides vectorized, columnar DataFrames implemented in C and Cython. Aggregating, grouping, or filtering 500 records across 18 columns executes orders of magnitude faster than iterating through native Python loops. Pandas also provides native handling for missing values (NaNs), vectorized string matching, robust CSV parsing, and direct integration with Plotly and SciPy."),
            
            ("Q2: What is vectorization in Pandas and NumPy?",
             "Vectorization is the process of delegating array-level mathematical and logical computations to low-level, pre-compiled C routines rather than interpreting explicit Python 'for' loops. This eliminates Python bytecode execution overhead and leverages SIMD (Single Instruction, Multiple Data) CPU hardware instructions for maximum throughput."),
            
            ("Q3: How does EduMetrics handle missing data during CSV ingestion?",
             "In `src/data_loader.py`, the function `clean_and_enrich_data()` implements defensive data hygiene. For unplaced candidates, `salary_lpa` and `company` are explicitly standardized to NaN. If an unplaced student erroneously contains a salary, it is set to NaN. For placed students with missing compensation, the cohort median is imputed. All percentages are clamped to $[0.0, 100.0]$."),
            
            ("Q4: Why did you set np.random.seed(42) in the synthetic data generator?",
             "Setting a fixed pseudorandom seed guarantees absolute algorithmic reproducibility. Every execution of `generate_synthetic_data()` generates the exact same 500 student records, scores, and conditional probabilities. This ensures that unit tests, statistical assertions, and presentation numbers remain 100% stable across different environments."),
            
            ("Q5: What is the difference between a shallow copy and a deep copy in Pandas?",
             "A shallow copy (`df.copy(deep=False)`) creates a new DataFrame object that still shares the underlying NumPy memory buffers with the parent. In EduMetrics, reactive filtering produces sliced views. Where independent feature transformations are computed, `.copy()` is invoked to prevent `SettingWithCopyWarning` exceptions."),
            
            ("Q6: How does Python 3.14 optimize memory compared to older versions?",
             "Python 3.14 introduces advanced bytecode specialization, deferred object reference counting, and leaner object headers. In EduMetrics, this results in faster startup times for Streamlit and lower memory footprints when loading large DataFrames and generating ReportLab PDF buffers.")
        ]),
        ("Domain 2: Frontend, Streamlit & Responsive CSS Architecture", [
            ("Q7: How does Streamlit's reactive execution model work?",
             "Streamlit operates on a declarative execution cycle: whenever a user interacts with a widget (slider, radio button, dropdown), the framework re-runs the entire Python script from line 1. EduMetrics optimizes this by storing the master dataset in `st.session_state` so disk reads are avoided, and reactive slicing generates filtered views dynamically in sub-milliseconds."),
            
            ("Q8: What is st.session_state and where is it used in EduMetrics?",
             "`st.session_state` is a dictionary-like persistent session storage mechanism surviving script reruns. EduMetrics uses it to cache `active_dataset` (the active cohort DataFrame), `assessment_form_data` (interactive inputs for student evaluation), and `current_assessment` (the computed readiness diagnostic output)."),
            
            ("Q9: How did you resolve UI text and chart overlapping issues?",
             "We conducted a structural CSS audit in `src/ui_components.py` and implemented five key architectural fixes: 1) injected `div[data-testid='stColumn'] { min-width: 0 !important; }` to stop column blowout; 2) rebuilt `.kpi-card` with flex column layout and `min-height: 145px; overflow: visible;`; 3) enabled button text wrapping; 4) repositioned Plotly legends to the bottom (`y=-0.18, x=0.5`) with top chart margins $t \\ge 65\\text{px}$; and 5) added full-width mobile column stacking."),
            
            ("Q10: Why did you decouple Plotly legends from chart titles?",
             "In default Plotly charts, top-aligned legends collide with two-line chart titles when the viewport narrows. By decoupling legends and anchoring them to the bottom (`y=-0.18, x=0.5, orientation='h'`), chart titles have dedicated breathing room, completely eliminating visual overlap across all screen widths.")
        ]),
        ("Domain 3: Relational Database & SQL Engineering", [
            ("Q11: Why design the SQLite database in Third Normal Form (3NF)?",
             "A single denormalized flat file suffers from insertion, update, and deletion anomalies. For instance, updating a student's technical skill level might accidentally overwrite demographic records. Normalizing into `students`, `academic_records`, `skills`, and `placements` separates independent entities, eliminates redundancy, and enforces referential integrity."),
            
            ("Q12: What is a Foreign Key Cascade (ON DELETE CASCADE)?",
             "It is an integrity constraint defined on child tables (`academic_records`, `skills`, `placements`) referencing `students(student_id)`. If a student record is deleted from the parent table, SQLite automatically removes all related rows in child tables, preventing orphaned records."),
            
            ("Q13: Why use parameterized queries (?) in src/database.py?",
             "Parameterized queries separate SQL instructions from user-supplied parameters. The database engine compiles the SQL command structure first and treats the parameters strictly as literal data. This completely neutralizes SQL injection vulnerabilities."),
            
            ("Q14: What is the purpose of secondary B-Tree indexes in database/schema.sql?",
             "Indexes (`idx_students_spec`, `idx_academic_att`, `idx_placements_stat`) allow the SQLite engine to locate matching rows in logarithmic time $O(\\log N)$ rather than scanning the entire table $O(N)$ during joins, group-by operations, and attendance filtering."),
            
            ("Q15: How does SQLite maintain ACID compliance in an embedded system?",
             "SQLite achieves Atomicity, Consistency, Isolation, and Durability through write-ahead logging (WAL) and atomic commit rollback journals. Transactions either commit completely or roll back, preventing database corruption during unexpected application termination.")
        ]),
        ("Domain 4: Applied Statistics & Econometric Modeling", [
            ("Q16: Why use Median rather than Mean for salary analytics?",
             "Compensation distributions are heavily right-skewed; a few premium corporate packages (e.g., ₹24 LPA) pull the arithmetic mean upward. The median represents the 50th percentile—the true middle offer—giving management an accurate view of typical graduate earnings."),
            
            ("Q17: What denominator is used for the Placement Rate calculation?",
             "The denominator is the total number of enrolled students in the cohort: $\\text{Placement Rate} = (\\text{Placed Students} / \\text{Total Cohort}) \\times 100$. This prevents artificial rate inflation that occurs when unplaced students are excluded."),
            
            ("Q18: What is the Interquartile Range (IQR) and what does it indicate?",
             "The IQR is the difference between the 75th percentile ($Q_3$) and 25th percentile ($Q_1$). It captures the middle 50% salary spread, indicating package dispersion without being distorted by extreme minimum or maximum compensation offers."),
            
            ("Q19: Explain why correlation does not imply causation in student analytics.",
             "A high Pearson correlation ($r = +0.58$) between attendance and placement means that students with higher attendance are placed at higher rates. However, attendance itself does not cause a job offer; it acts as a proxy for student conscientiousness and discipline."),
            
            ("Q20: What is Welch's t-test and why was it chosen over Student's t-test?",
             "Student's standard t-test assumes equal population variances (homoscedasticity). In educational cohorts, placed and unplaced students exhibit unequal variances. Welch's t-test calculates adjusted degrees of freedom, preventing Type I errors under heteroscedasticity."),
            
            ("Q21: What is an Odds Ratio in your Logistic Regression demonstration?",
             "The Odds Ratio ($OR = e^\\beta$) indicates the factor by which the odds of placement increase with a one-unit increase in a predictor. An odds ratio of 1.52 for Technical Score means each 1-point increase on the 10-point scale increases placement odds by 52%.")
        ]),
        ("Domain 5: Decision Science, Benchmarking & Heuristics", [
            ("Q22: How does Career Readiness dynamic weight redistribution work?",
             "If a candidate lacks certain data (e.g., unrecorded certifications), remaining available pillar weights are rescaled: $W'_j = (W_j / \\sum W_{\\text{avail}}) \\times 100$. This ensures the student is evaluated on a true 100% scale without being penalized with zeros."),
            
            ("Q23: Why choose a rule-based recommendation engine over deep learning AI?",
             "University administrative decisions must be transparent, fair, and auditable. Deep learning neural networks act as opaque black boxes that cannot explain their reasoning. A deterministic heuristic engine maps directly to official policies (e.g., 75% attendance cutoff)."),
            
            ("Q24: What are the 6 pillars of the Career Readiness Index?",
             "1. Technical Skills (40%), 2. Academic Examination Performance (15%), 3. Soft Skills & Aptitude (15%), 4. Industry Certifications (10%), 5. Corporate Internship (10%), and 6. Classroom Attendance (10%)."),
            
            ("Q25: How does the application identify students at academic risk?",
             "The boolean flag `is_academic_at_risk` evaluates True if `academic_percentage < 55.0` OR `attendance_percentage < 75.0`, instantly surfacing candidates requiring faculty tutoring or policy intervention."),
            
            ("Q26: What is the purpose of the 5 quick-load demo buttons in assessment?",
             "They allow examiners and faculty to immediately test diverse student archetypes (High Achiever, Balanced Cohort, Support Needed, Missing Data Demo) without manual data entry, demonstrating the engine's versatility."),
            
            ("Q27: How is the Technical Competency Index calculated on a 0-10 scale?",
             "Each skill is mapped numerically: Beginner=1, Intermediate=2, Advanced=3 (summing to 9). The formula $T_{10} = ((\\text{SQL} + \\text{Python} + \\text{PowerBI}) / 9.0) \\times 10.0$ normalizes competence to a 10-point continuous scale."),
            
            ("Q28: How does the roadmap sequencing prioritize skill gaps?",
             "Foundational deficits ($Gap \\le -2$) in core tools like SQL/Python are assigned to Priority 1 (Weeks 1-4). Secondary deficits ($Gap = -1$) are assigned to Priority 2 (Weeks 5-7). Portfolio polish is assigned to Priority 3 (Weeks 8-9).")
        ]),
        ("Domain 6: Quality Assurance, Security, Ethics & Project Management", [
            ("Q29: How many automated tests are implemented and what do they verify?",
             "EduMetrics has 53 automated tests across 8 test suites in `tests/`. They verify readiness scoring, SQLite schema and queries, edge cases, summary metrics, heuristic rules, Streamlit page routing, and responsive layout rules."),
            
            ("Q30: How does EduMetrics guarantee zero student privacy violations?",
             "All 500 records are algorithmically synthesized. There are zero real-world names, student IDs, or university records, ensuring full compliance with FERPA, GDPR, and Indian DPDP Act 2023 regulations."),
            
            ("Q31: What happens if a user uploads a CSV with missing columns?",
             "The function `validate_dataframe()` audits the uploaded file against `EXPECTED_COLUMNS`. If columns are missing or invalid, it displays an informative warning banner without crashing the application."),
            
            ("Q32: Can EduMetrics handle a cohort where 100% of students are unplaced?",
             "Yes. Defensive programming in `test_edge_cases.py` confirms that the application renders cleanly with placement rates displayed as 0.0% and salary metrics safely set to None without raising division-by-zero exceptions."),
            
            ("Q33: How does ReportLab compile PDF dossiers without disk image files?",
             "ReportLab constructs documents in an in-memory `io.BytesIO()` buffer using Platypus flowable elements (Paragraphs, Tables, Spacers) and vector graphics. The resulting byte stream is delivered directly to the user's browser."),
            
            ("Q34: How does the application prevent gender bias in decision-making?",
             "Demographic fields (such as gender) are included strictly for equity auditing and are mathematically excluded from all recommendation heuristics, readiness calculations, and predictive feature sets."),
            
            ("Q35: What is the primary takeaway for examiners about EduMetrics?",
             "EduMetrics demonstrates how modern Python, SQL, and business analytics can turn fragmented student data into explainable, proactive academic interventions and smarter career decisions.")
        ])
    ]

    for domain_title, qas in viva_domains:
        story.append(p(f"<b>{domain_title}</b>", sub_heading))
        story.append(Spacer(1, 3))
        for q, a in qas:
            story.append(p(q, viva_q))
            story.append(p(a, viva_a))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # =========================================================================
    # PART 20: COMPREHENSIVE GLOSSARY
    # =========================================================================
    story.append(p("Part 20: Comprehensive Technical & Business Glossary", part_heading))
    story.append(hr())
    story.append(p(
        "Definitions of essential statistical, technical, database, and business analytics terms utilized across EduMetrics:",
        body_txt
    ))

    glossary_data = [
        [p("<b>Term / Acronym</b>", table_hdr), p("<b>Formal Technical & Managerial Definition</b>", table_hdr)],
        [p("<b>3NF (Third Normal Form)</b>", table_cell_bold), p("A relational database state where all attributes are functionally dependent only on the primary key, eliminating transitive dependencies and update anomalies.", table_cell)],
        [p("<b>ANOVA (Analysis of Variance)</b>", table_cell_bold), p("An inferential statistical test evaluating whether the means of three or more groups (e.g. academic specializations) differ significantly.", table_cell)],
        [p("<b>B-Tree Index</b>", table_cell_bold), p("A self-balancing tree data structure maintained by database engines to accelerate data retrieval, range filtering, and foreign key joins.", table_cell)],
        [p("<b>Central Tendency</b>", table_cell_bold), p("Statistical measures identifying the central or typical value of a distribution (Arithmetic Mean, Median, Mode).", table_cell)],
        [p("<b>Cohen's d</b>", table_cell_bold), p("A standardized effect size metric quantifying the practical magnitude of the difference between two group means independent of sample size.", table_cell)],
        [p("<b>Cost-to-Company (CTC)</b>", table_cell_bold), p("The total annual gross compensation package offered by an employer to a candidate, denominated in ₹ Lakhs Per Annum (LPA).", table_cell)],
        [p("<b>DataFrame</b>", table_cell_bold), p("A two-dimensional, size-mutable, tabular data structure with labeled axes (rows and columns) in Pandas, optimized for vectorized operations.", table_cell)],
        [p("<b>Deterministic Heuristics</b>", table_cell_bold), p("Transparent, rule-based algorithmic decision logic that produces predictable, fully auditable outputs based on explicit policy thresholds.", table_cell)],
        [p("<b>ETL (Extract, Transform, Load)</b>", table_cell_bold), p("A three-stage data engineering pipeline extracting raw data, validating and enriching it, and loading it into a destination storage engine.", table_cell)],
        [p("<b>Interquartile Range (IQR)</b>", table_cell_bold), p("A non-parametric measure of statistical dispersion computed as Q3 - Q1, capturing the middle 50% spread resistant to extreme outliers.", table_cell)],
        [p("<b>Logistic Regression</b>", table_cell_bold), p("A generalized linear model estimating the probability of a binary categorical outcome (Placed vs. Unplaced) using a logistic sigmoid link function.", table_cell)],
        [p("<b>Odds Ratio (OR)</b>", table_cell_bold), p("The ratio of the odds of an outcome occurring under a specific predictor exposure relative to non-exposure; calculated as e^beta.", table_cell)],
        [p("<b>Parametric Statistics</b>", table_cell_bold), p("Statistical methods assuming that the underlying data sample follows a defined probability distribution (e.g. normal distribution).", table_cell)],
        [p("<b>Pearson Correlation (r)</b>", table_cell_bold), p("A bivariate metric measuring the linear association strength between two continuous variables, bounded between -1.0 and +1.0.", table_cell)],
        [p("<b>P-Value</b>", table_cell_bold), p("The probability under the null hypothesis of obtaining a test statistic at least as extreme as the observed sample outcome.", table_cell)],
        [p("<b>Plotly</b>", table_cell_bold), p("An open-source declarative data visualization library outputting interactive, GPU-accelerated web charts supporting client-side pan and zoom.", table_cell)],
        [p("<b>Pytest</b>", table_cell_bold), p("A Python automated testing framework utilizing plain assert statements, fixture dependency injection, and test discovery.", table_cell)],
        [p("<b>ReportLab</b>", table_cell_bold), p("A programmatic Python PDF generation library providing Flowable document templates, paragraph typography, tables, and canvas graphics.", table_cell)],
        [p("<b>Responsive Web Design</b>", table_cell_bold), p("An interface design methodology ensuring web applications adapt fluidly to desktop, laptop, tablet, and smartphone viewports.", table_cell)],
        [p("<b>Session State</b>", table_cell_bold), p("A persistent in-memory dictionary maintaining variable values across reactive web script reruns for an active user session in Streamlit.", table_cell)],
        [p("<b>Streamlit</b>", table_cell_bold), p("A modern Python application framework providing reactive web component binding and declarative UI rendering without HTML/JS overhead.", table_cell)],
        [p("<b>Synthetic Dataset</b>", table_cell_bold), p("An algorithmically synthesized dataset mirroring empirical mathematical distributions while containing zero real-world PII.", table_cell)],
        [p("<b>Vectorization</b>", table_cell_bold), p("A computational technique executing array-level operations using compiled low-level C routines rather than explicit Python for-loops.", table_cell)],
        [p("<b>Welch's t-Test</b>", table_cell_bold), p("A two-sample hypothesis test comparing group means without assuming equal population variances (heteroscedasticity).", table_cell)]
    ]
    t_gloss = Table(glossary_data, colWidths=[140, 400])
    t_gloss.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_box])
    ]))
    story.append(t_gloss)

    # Build PDF with two-pass NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF documentation: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    target_pdf = out_dir / "EduMetrics_Complete_Project_Documentation.pdf"
    build_pdf(str(target_pdf))
