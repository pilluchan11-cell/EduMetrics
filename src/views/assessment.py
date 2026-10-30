"""
Individual Student Assessment & Performance Analyzer View for EduMetrics.
Enables faculty, coordinators, and placement directors to manually enter student profiles,
benchmark against target career roles, perform competency gap analysis, and generate
downloadable PDF/CSV diagnostic dossiers.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import io

from src.assessment_engine import (
    CAREER_ROLE_BENCHMARKS,
    SKILL_LEVEL_NAMES,
    calculate_skill_gaps,
    calculate_readiness_score,
    generate_individual_assessment,
    get_sample_student_profile
)
from src.visualizations import (
    plot_skill_gap_comparison,
    plot_student_competency_radar,
    plot_readiness_component_breakdown,
    plot_subject_performance
)
from src.report_generator import generate_student_pdf_report
from src.database import (
    save_assessment_record, 
    load_all_assessments,
    save_single_student_to_db,
    get_connection
)
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_kpi, 
    render_section_header,
    render_footer
)
from src.config import (
    COLOR_PRIMARY, 
    COLOR_SUCCESS, 
    COLOR_DANGER, 
    COLOR_ACCENT, 
    COLOR_SECONDARY,
    ATTENDANCE_CRITICAL_THRESHOLD
)


def render(df_active: pd.DataFrame) -> None:
    """Renders the comprehensive Student Assessment and Career-Readiness module."""
    render_hero("Individual Student Assessment & Career-Readiness Analyzer")
    render_disclaimer()
    
    # Initialize assessment session state cache
    if "assessment_form_data" not in st.session_state:
        st.session_state["assessment_form_data"] = get_sample_student_profile("balanced")
    if "current_assessment" not in st.session_state:
        # Pre-generate assessment for instant preview
        initial_sample = st.session_state["assessment_form_data"]
        st.session_state["current_assessment"] = generate_individual_assessment(
            initial_sample, 
            initial_sample.get("target_role", "Data Analyst")
        )

    # -------------------------------------------------------------------------
    # Top Control Bar: Quick Load Demonstrations & Clear
    # -------------------------------------------------------------------------
    render_section_header(
        "Candidate Profile Ingestion & Diagnostic Setup",
        "Enter comprehensive academic, attendance, technical skill, and project details to evaluate placement readiness.",
        "📝"
    )
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        if st.button("⚡ High-Achiever Sample", use_container_width=True, help="Load sample profile: distinction student, multiple certifications, internship complete"):
            st.session_state["assessment_form_data"] = get_sample_student_profile("high_achiever")
            st.session_state["current_assessment"] = generate_individual_assessment(
                st.session_state["assessment_form_data"], 
                "Data Analyst"
            )
            st.rerun()
    with col_p2:
        if st.button("⚡ Balanced Cohort Sample", use_container_width=True, help="Load typical student profile: 72% marks, 79% attendance, 1 cert"):
            st.session_state["assessment_form_data"] = get_sample_student_profile("balanced")
            st.session_state["current_assessment"] = generate_individual_assessment(
                st.session_state["assessment_form_data"], 
                "Data Analyst"
            )
            st.rerun()
    with col_p3:
        if st.button("⚡ Support Needed Sample", use_container_width=True, help="Load at-risk sample: 58% marks, 71% attendance, skill deficits"):
            st.session_state["assessment_form_data"] = get_sample_student_profile("needs_intervention")
            st.session_state["current_assessment"] = generate_individual_assessment(
                st.session_state["assessment_form_data"], 
                "Business Analyst"
            )
            st.rerun()
    with col_p4:
        if st.button("↺ Reset Form", use_container_width=True, help="Clear form to empty defaults"):
            st.session_state["assessment_form_data"] = {
                "student_id": "",
                "student_name": "",
                "gender": "Non-Binary",
                "specialization": "Business Analytics",
                "semester": "Semester 3",
                "academic_year": "2025-2026",
                "tenth_percentage": 0.0,
                "twelfth_percentage": 0.0,
                "grad_percentage": 0.0,
                "cgpa": 6.5,
                "cgpa_scale": 10.0,
                "academic_percentage": 65.0,
                "subject_marks": {},
                "attendance_percentage": 75.0,
                "skills": {k: 2 for k in ["Excel", "SQL", "Python", "Power BI", "Tableau", "Statistics", "Machine Learning", "Communication"]},
                "certifications": [],
                "certifications_count": 0,
                "internship_status": "Not Completed",
                "internship_company": "",
                "internship_duration_months": 0,
                "project_experience": "",
                "projects_count": 0,
                "resume_status": "Draft",
                "communication_level": 3,
                "aptitude_level": 3,
                "interview_status": "Not Started",
                "placement_status": "Unplaced",
                "target_role": "Data Analyst"
            }
            st.session_state["current_assessment"] = None
            st.rerun()

    current_data = st.session_state["assessment_form_data"]

    # -------------------------------------------------------------------------
    # Structured Data Entry Form
    # -------------------------------------------------------------------------
    with st.expander("📋 Candidate Evaluation Input Form", expanded=True):
        st.markdown(
            """
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-size: 12.5px; color: #475569;">
                💡 <em>Fill in candidate metrics across all assessment dimensions. Fields marked with <strong>*</strong> are required. Optional fields may be left blank or 0 if unrecorded.</em>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ---------------- Section A: Basic Info ----------------
        st.markdown("#### A. Basic Identification & Enrollment")
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            val_id = st.text_input(
                "Student ID *", 
                value=str(current_data.get("student_id", "")),
                placeholder="e.g. STU-2026-905",
                help="Unique alphanumeric candidate code."
            )
        with r1_c2:
            val_name = st.text_input(
                "Student Full Name *", 
                value=str(current_data.get("student_name", "")),
                placeholder="e.g. Ananya Sen",
                help="Official enrolled name."
            )
        with r1_c3:
            gender_options = ["Male", "Female", "Non-Binary"]
            cur_gender = current_data.get("gender", "Non-Binary")
            val_gender = st.selectbox(
                "Gender Demographic",
                options=gender_options,
                index=gender_options.index(cur_gender) if cur_gender in gender_options else 2,
                help="Fictional demographic classification."
            )
            
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            specs = ["Business Analytics", "Finance", "Marketing", "Operations", "Human Resources"]
            cur_spec = current_data.get("specialization", "Business Analytics")
            val_spec = st.selectbox(
                "Academic Specialization *",
                options=specs,
                index=specs.index(cur_spec) if cur_spec in specs else 0
            )
        with r2_c2:
            sems = ["Semester 1", "Semester 2", "Semester 3", "Semester 4"]
            cur_sem = current_data.get("semester", "Semester 3")
            val_sem = st.selectbox(
                "Current Semester *",
                options=sems,
                index=sems.index(cur_sem) if cur_sem in sems else 2
            )
        with r2_c3:
            val_year = st.text_input(
                "Academic Year",
                value=str(current_data.get("academic_year", "2025-2026")),
                placeholder="e.g. 2025-2026"
            )
            
        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section B: Academic Performance ----------------
        st.markdown("#### B. Academic Performance & Prior Records")
        a_c1, a_c2, a_c3 = st.columns(3)
        with a_c1:
            val_10th = st.number_input(
                "10th Standard Marks (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_data.get("tenth_percentage", 0.0)),
                step=0.5,
                help="Secondary school certificate percentage."
            )
        with a_c2:
            val_12th = st.number_input(
                "12th Standard Marks (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_data.get("twelfth_percentage", 0.0)),
                step=0.5,
                help="Higher secondary certificate percentage."
            )
        with a_c3:
            val_grad = st.number_input(
                "Undergraduate Degree Marks (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_data.get("grad_percentage", 0.0)),
                step=0.5,
                help="Bachelor's degree aggregate marks."
            )
            
        g_c1, g_c2, g_c3 = st.columns(3)
        with g_c1:
            val_cgpa = st.number_input(
                "Current Cumulative GPA / CGPA",
                min_value=0.0,
                max_value=10.0,
                value=float(current_data.get("cgpa", 7.0)),
                step=0.1,
                help="Enrolled program grade point average."
            )
        with g_c2:
            val_scale = st.selectbox(
                "Grading Scale",
                options=[10.0, 4.0],
                index=0 if current_data.get("cgpa_scale", 10.0) == 10.0 else 1,
                format_func=lambda x: f"{x:.1f} Point Scale"
            )
        with g_c3:
            # Auto-calculate suggested aggregate from CGPA
            suggested_acad = round((val_cgpa / val_scale) * 100.0, 1) if val_scale > 0 else 70.0
            val_acad_pct = st.number_input(
                "Master's Overall Academic Percentage (%) *",
                min_value=0.0,
                max_value=100.0,
                value=float(current_data.get("academic_percentage", suggested_acad)),
                step=0.5,
                help="Primary academic metric utilized for recruiter screening eligibility."
            )
            
        st.markdown("##### Subject-Level Marks Breakdown (Optional - 5 Core Modules)")
        sub_c1, sub_c2, sub_c3 = st.columns([4, 2, 6])
        cur_subs = current_data.get("subject_marks", {})
        sub1_name = st.text_input("Subject 1 Name", value="Business Statistics & Analytics", key="sub1_n")
        sub1_mark = st.number_input("Subject 1 Score (%)", min_value=0.0, max_value=100.0, value=float(cur_subs.get("Business Statistics", cur_subs.get(sub1_name, 75.0))), step=1.0, key="sub1_m")
        
        s2_c1, s2_c2 = st.columns(2)
        with s2_c1:
            sub2_name = st.text_input("Subject 2 Name", value="Database & SQL Systems", key="sub2_n")
            sub2_mark = st.number_input("Subject 2 Score (%)", min_value=0.0, max_value=100.0, value=float(cur_subs.get("SQL Querying", cur_subs.get(sub2_name, 72.0))), step=1.0, key="sub2_m")
        with s2_c2:
            sub3_name = st.text_input("Subject 3 Name", value="Python Programming & Data Wrangling", key="sub3_n")
            sub3_mark = st.number_input("Subject 3 Score (%)", min_value=0.0, max_value=100.0, value=float(cur_subs.get("Python Programming", cur_subs.get(sub3_name, 70.0))), step=1.0, key="sub3_m")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section C: Attendance ----------------
        st.markdown("#### C. Classroom Attendance Compliance")
        att_c1, att_c2 = st.columns([2, 1])
        with att_c1:
            val_att = st.slider(
                "Lecture & Lab Attendance Percentage (%) *",
                min_value=0.0,
                max_value=100.0,
                value=float(current_data.get("attendance_percentage", 78.0)),
                step=0.5,
                help=f"Institutional mandatory compliance threshold is {ATTENDANCE_CRITICAL_THRESHOLD}%."
            )
        with att_c2:
            st.write(" ")
            if val_att >= ATTENDANCE_CRITICAL_THRESHOLD:
                st.success(f"✅ Attendance Compliant ({val_att:.1f}% ≥ {ATTENDANCE_CRITICAL_THRESHOLD}%)")
            else:
                st.error(f"⚠️ Policy Violation: Below {ATTENDANCE_CRITICAL_THRESHOLD}% Cutoff ({val_att:.1f}%)")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section D: Technical Skills (1-5 Scale) ----------------
        st.markdown("#### D. Technical Skills & Tools Proficiency (1 to 5 Scale)")
        st.markdown(
            """
            <div style="font-size: 11.5px; color: #64748B; margin-bottom: 10px;">
                <strong>Proficiency Scale:</strong> 1 = Beginner (Concepts) | 2 = Basic (Syntax) | 3 = Intermediate (Independent Tasks) | 4 = Advanced (Complex Queries/Models) | 5 = Expert (Production Architect)
            </div>
            """,
            unsafe_allow_html=True
        )
        
        cur_skills = current_data.get("skills", {})
        
        def skill_widget(label: str, key_name: str, default_lvl: int = 2):
            val = cur_skills.get(key_name, default_lvl)
            return st.selectbox(
                label,
                options=[1, 2, 3, 4, 5],
                index=int(val - 1) if 1 <= val <= 5 else 1,
                format_func=lambda x: f"Level {x}: {SKILL_LEVEL_NAMES[x]}",
                key=f"skill_{key_name}"
            )
            
        sk_col1, sk_col2, sk_col3, sk_col4 = st.columns(4)
        with sk_col1:
            val_excel = skill_widget("Microsoft Excel", "Excel", 3)
            val_sql = skill_widget("SQL Databases", "SQL", 3)
        with sk_col2:
            val_py = skill_widget("Python Programming", "Python", 2)
            val_bi = skill_widget("Power BI Analytics", "Power BI", 3)
        with sk_col3:
            val_tab = skill_widget("Tableau Dashboards", "Tableau", 2)
            val_stat = skill_widget("Business Statistics", "Statistics", 3)
        with sk_col4:
            val_ml = skill_widget("Machine Learning", "Machine Learning", 1)
            val_comm = skill_widget("Communication & Pitching", "Communication", 3)

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section E: Certifications ----------------
        st.markdown("#### E. Professional Industry Certifications")
        standard_certs = [
            "Microsoft Power BI Data Analyst (PL-300)",
            "Google Data Analytics Professional Certificate",
            "IBM Data Analyst",
            "SQL for Data Science",
            "Python Data Structures & Applied Analytics",
            "AWS Certified Cloud Practitioner"
        ]
        cur_certs = current_data.get("certifications", [])
        val_certs = st.multiselect(
            "Select Verified Completed Certifications:",
            options=standard_certs,
            default=[c for c in cur_certs if c in standard_certs],
            help="Select only completed credentials with verified certificates."
        )
        custom_cert = st.text_input("Other / Additional Certification (Optional):", placeholder="e.g. Financial Modeling & Valuation Analyst (FMVA)")
        if custom_cert.strip() and custom_cert.strip() not in val_certs:
            val_certs = list(val_certs) + [custom_cert.strip()]

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section F: Internship & Projects ----------------
        st.markdown("#### F. Corporate Internship & Applied Project Experience")
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            intern_opts = ["Not Completed", "Completed"]
            cur_intern = current_data.get("internship_status", "Not Completed")
            val_intern = st.selectbox(
                "Summer Internship Status",
                options=intern_opts,
                index=1 if str(cur_intern).lower() == "completed" else 0
            )
        with exp_col2:
            val_intern_co = st.text_input(
                "Internship Entity / Employer",
                value=str(current_data.get("internship_company", "")),
                placeholder="e.g. KPMG, Amazon, HDFC Bank"
            )
        with exp_col3:
            val_projects_count = st.number_input(
                "Completed Hands-On Projects",
                min_value=0,
                max_value=15,
                value=int(current_data.get("projects_count", 1)),
                step=1,
                help="Substantial analytics projects with documented code or dashboards."
            )
            
        val_proj_desc = st.text_area(
            "Project Portfolio Summary (Optional):",
            value=str(current_data.get("project_experience", "")),
            placeholder="Brief overview of domain problem, tools used, and business outcome."
        )

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section G: Placement Readiness ----------------
        st.markdown("#### G. Placement Readiness & Soft Skills")
        rdy_col1, rdy_col2, rdy_col3, rdy_col4 = st.columns(4)
        with rdy_col1:
            resume_opts = ["Not Started", "Draft", "Reviewed", "Ready / Verified"]
            cur_res = current_data.get("resume_status", "Reviewed")
            val_resume = st.selectbox(
                "Resume Preparation Status",
                options=resume_opts,
                index=resume_opts.index(cur_res) if cur_res in resume_opts else 1
            )
        with rdy_col2:
            apt_opts = [1, 2, 3, 4, 5]
            val_apt = st.selectbox(
                "Aptitude Test Preparedness",
                options=apt_opts,
                index=int(current_data.get("aptitude_level", 3) - 1),
                format_func=lambda x: f"Level {x}: {['Needs Work', 'Basic', 'Competent', 'Proficient', 'Exceptional'][x-1]}"
            )
        with rdy_col3:
            mock_opts = ["Not Started", "1 Mock Interview", "Multiple Mocks Completed", "Interview Ready"]
            cur_mock = current_data.get("interview_status", "1 Mock Interview")
            val_mock = st.selectbox(
                "Simulated Interview Experience",
                options=mock_opts,
                index=mock_opts.index(cur_mock) if cur_mock in mock_opts else 0
            )
        with rdy_col4:
            place_opts = ["Unplaced", "Placed", "In Process"]
            cur_place = current_data.get("placement_status", "Unplaced")
            val_place = st.selectbox(
                "Current Recruitment Status",
                options=place_opts,
                index=place_opts.index(cur_place) if cur_place in place_opts else 0
            )

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section H: Target Career Direction ----------------
        st.markdown("#### H. Target Career Role & Benchmark Mapping")
        role_opts = list(CAREER_ROLE_BENCHMARKS.keys())
        cur_role = current_data.get("target_role", "Data Analyst")
        val_target_role = st.selectbox(
            "Select Target Career Role for Competency Benchmarking:",
            options=role_opts,
            index=role_opts.index(cur_role) if cur_role in role_opts else 0,
            help="Candidate skills and experience will be benchmarked against this role's industry standard."
        )
        
        role_desc = CAREER_ROLE_BENCHMARKS[val_target_role]["description"]
        st.info(f"🎯 **Target Role Scope ({val_target_role}):** {role_desc}")

        # ---------------- Submit / Analyze Button ----------------
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_clicked = st.button(
            "🚀 Analyze Student Performance & Generate Diagnostic Dossier",
            use_container_width=True,
            type="primary"
        )
        
        if analyze_clicked:
            # Input validation
            errors = []
            if not val_id.strip():
                errors.append("Student ID is required.")
            if not val_name.strip():
                errors.append("Student Name is required.")
            if val_acad_pct < 0.0 or val_acad_pct > 100.0:
                errors.append("Academic Percentage must be between 0.0% and 100.0%.")
            if val_att < 0.0 or val_att > 100.0:
                errors.append("Attendance Percentage must be between 0.0% and 100.0%.")
                
            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                # Compile comprehensive student data dictionary
                subject_marks_dict = {}
                if sub1_name.strip():
                    subject_marks_dict[sub1_name.strip()] = float(sub1_mark)
                if sub2_name.strip():
                    subject_marks_dict[sub2_name.strip()] = float(sub2_mark)
                if sub3_name.strip():
                    subject_marks_dict[sub3_name.strip()] = float(sub3_mark)

                compiled_skills = {
                    "Excel": val_excel,
                    "SQL": val_sql,
                    "Python": val_py,
                    "Power BI": val_bi,
                    "Tableau": val_tab,
                    "Statistics": val_stat,
                    "Machine Learning": val_ml,
                    "Communication": val_comm
                }

                assembled_student = {
                    "student_id": val_id.strip(),
                    "student_name": val_name.strip(),
                    "gender": val_gender,
                    "specialization": val_spec,
                    "semester": val_sem,
                    "academic_year": val_year.strip(),
                    "tenth_percentage": float(val_10th),
                    "twelfth_percentage": float(val_12th),
                    "grad_percentage": float(val_grad),
                    "cgpa": float(val_cgpa),
                    "cgpa_scale": float(val_scale),
                    "academic_percentage": float(val_acad_pct),
                    "subject_marks": subject_marks_dict,
                    "attendance_percentage": float(val_att),
                    "skills": compiled_skills,
                    "certifications": val_certs,
                    "certifications_count": len(val_certs),
                    "internship_status": val_intern,
                    "internship_company": val_intern_co.strip(),
                    "internship_duration_months": 2 if val_intern == "Completed" else 0,
                    "project_experience": val_proj_desc.strip(),
                    "projects_count": int(val_projects_count),
                    "resume_status": val_resume,
                    "communication_level": val_comm,
                    "aptitude_level": val_apt,
                    "interview_status": val_mock,
                    "placement_status": val_place,
                    "target_role": val_target_role
                }

                # Update session state
                st.session_state["assessment_form_data"] = assembled_student
                st.session_state["current_assessment"] = generate_individual_assessment(
                    assembled_student,
                    val_target_role
                )
                st.success("✅ Student performance successfully assessed! Detailed diagnostic dossier generated below.")
                st.rerun()

    # -------------------------------------------------------------------------
    # Render Assessment Diagnostic Dossier (if assessment exists)
    # -------------------------------------------------------------------------
    assessment = st.session_state.get("current_assessment")
    if not assessment:
        st.info("💡 Fill in candidate details above and click 'Analyze Student Performance' to view the analytical dossier.")
        render_footer()
        return

    student_data = assessment["student_data"]
    target_role = assessment["target_role"]
    readiness = assessment["readiness"]
    gap_analysis = readiness["gap_analysis"]
    strengths = assessment["strengths"]
    weaknesses = assessment["weaknesses"]
    recommendations = assessment["recommendations"]

    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header(
        f"Diagnostic Assessment Dossier: {student_data.get('student_name', 'Student')} ({student_data.get('student_id', 'N/A')})",
        f"Multi-pillar evaluation benchmarked against industry standards for {target_role}.",
        "📊"
    )

    # 1. Candidate Overview & Executive KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        score_val = readiness["overall_score"]
        tier_col = readiness["tier_color"]
        render_kpi(
            "Readiness Index",
            f"{score_val:.1f} / 100",
            f"Tier: {readiness['tier_label']}",
            tier_col,
            icon="🎯",
            chip_text=readiness["tier_label"].split("/")[0].strip(),
            chip_color="#EFF6FF"
        )
    with k2:
        fit_pct = gap_analysis["fit_percentage"]
        render_kpi(
            f"Target Role Fit ({target_role})",
            f"{fit_pct:.1f}%",
            f"{gap_analysis['student_matched_points']} of {gap_analysis['total_required_points']} benchmark points",
            COLOR_PRIMARY,
            icon="⚡",
            chip_text="Competency Fit",
            chip_color="#EFF6FF"
        )
    with k3:
        acad_val = student_data.get("academic_percentage", 0.0)
        band_name = "Distinction" if acad_val >= 75 else ("First Class" if acad_val >= 60 else "Remedial")
        render_kpi(
            "Academic Standing",
            f"{acad_val:.1f}%",
            f"CGPA: {student_data.get('cgpa', 0.0):.1f} ({band_name})",
            COLOR_SECONDARY,
            icon="📚",
            chip_text="Academic Score",
            chip_color="#CCFBF1"
        )
    with k4:
        att_val = student_data.get("attendance_percentage", 0.0)
        att_col = COLOR_SUCCESS if att_val >= ATTENDANCE_CRITICAL_THRESHOLD else COLOR_DANGER
        att_txt = "Compliant" if att_val >= ATTENDANCE_CRITICAL_THRESHOLD else "Policy Risk"
        render_kpi(
            "Class Attendance",
            f"{att_val:.1f}%",
            f"Mandatory Cutoff: {ATTENDANCE_CRITICAL_THRESHOLD:.1f}%",
            att_col,
            icon="⏰",
            chip_text=att_txt,
            chip_color="#DCFCE7" if att_val >= ATTENDANCE_CRITICAL_THRESHOLD else "#FEE2E2"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Visual Diagnostics Tabs
    tab_gap, tab_radar, tab_pillars, tab_subs = st.tabs([
        "📊 Competency Gap Analysis",
        "🎯 Radar Capability Profile",
        "⚖️ Readiness Score Breakdown",
        "📚 Subject Performance"
    ])

    with tab_gap:
        fig_gap = plot_skill_gap_comparison(gap_analysis)
        st.plotly_chart(fig_gap, use_container_width=True)
        
        # Summary variance chips
        surplus_cnt = len(gap_analysis.get("surplus_skills", []))
        aligned_cnt = len(gap_analysis.get("aligned_skills", []))
        deficit_cnt = len(gap_analysis.get("deficit_skills", []))
        
        c_s1, c_s2, c_s3 = st.columns(3)
        with c_s1:
            st.metric("Surplus / Exceeds Benchmark", f"{surplus_cnt} Skills", delta="Competitive Edge" if surplus_cnt > 0 else None)
        with c_s2:
            st.metric("Aligned to Benchmark", f"{aligned_cnt} Skills")
        with c_s3:
            st.metric("Deficit Requiring Focus", f"{deficit_cnt} Skills", delta=f"-{deficit_cnt} Gaps" if deficit_cnt > 0 else "No Deficits", delta_color="inverse")

    with tab_radar:
        target_skills_dict = CAREER_ROLE_BENCHMARKS[target_role]["skills"]
        fig_radar = plot_student_competency_radar(student_data.get("skills", {}), target_skills_dict, target_role)
        st.plotly_chart(fig_radar, use_container_width=True)

    with tab_pillars:
        fig_pillars = plot_readiness_component_breakdown(readiness)
        st.plotly_chart(fig_pillars, use_container_width=True)

    with tab_subs:
        subs = student_data.get("subject_marks", {})
        if subs:
            fig_subs = plot_subject_performance(subs)
            st.plotly_chart(fig_subs, use_container_width=True)
        else:
            st.info("ℹ️ No individual subject-level scores were entered. Aggregate academic score used for evaluation.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Strengths vs Development Areas
    render_section_header(
        "Candidate Profile Diagnostics & Observations",
        "Rule-derived identification of core competitive advantages and areas needing remediation.",
        "🔍"
    )
    col_str, col_weak = st.columns(2)
    with col_str:
        st.markdown(
            """
            <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #166534; font-size: 15px;">🌟 Key Strengths & Competitive Assets</h4>
            """,
            unsafe_allow_html=True
        )
        if strengths:
            for s in strengths:
                st.markdown(f"<p style='color: #14532D; font-size: 13px; margin: 4px 0;'>• {s}</p>", unsafe_allow_html=True)
        else:
            st.write("No distinct competitive strengths recorded yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_weak:
        st.markdown(
            """
            <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #991B1B; font-size: 15px;">⚠️ Priority Development Areas & Gaps</h4>
            """,
            unsafe_allow_html=True
        )
        if weaknesses:
            for w in weaknesses:
                st.markdown(f"<p style='color: #7F1D1D; font-size: 13px; margin: 4px 0;'>• {w}</p>", unsafe_allow_html=True)
        else:
            st.write("No critical deficits detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Actionable Strategic Recommendations
    render_section_header(
        "Personalized Career-Development Interventions",
        f"Concrete, role-specific action steps to elevate {student_data.get('student_name', 'candidate')} into the premier recruitment band.",
        "🎯"
    )
    
    if recommendations:
        for rec in recommendations:
            badge_color = "#EF4444" if rec["priority"] == "Critical" else ("#F59E0B" if rec["priority"] == "High" else "#2563EB")
            badge_bg = "#FEE2E2" if rec["priority"] == "Critical" else ("#FEF3C7" if rec["priority"] == "High" else "#EFF6FF")
            st.markdown(
                f"""
                <div class="recommendation-card">
                    <div class="recommendation-header">
                        <h4 style="margin: 0; color: #0F172A; font-size: 15.5px; font-weight: 700;">{rec['category']}</h4>
                        <span style="background: {badge_bg}; color: {badge_color}; font-weight: 700; font-size: 11px; padding: 3px 10px; border-radius: 6px;">
                            {rec['priority'].upper()} PRIORITY
                        </span>
                    </div>
                    <div class="recommendation-action-box" style="border-left: 4px solid {badge_color}; margin-top: 6px;">
                        <strong>Actionable Step:</strong> {rec['action']}<br>
                        <span style="font-size: 12px; color: #64748B;"><em>Rationale: {rec['rationale']}</em></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("🎉 Candidate profile aligns comprehensively with all benchmark requirements for this target role!")

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Export, Persistence & Cohort Integration
    render_section_header(
        "Dossier Export, Database Persistence & Cohort Integration",
        "Download official assessment reports, persist to relational SQLite storage, or incorporate into active cohort analytics.",
        "📥"
    )
    
    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
    
    with c_btn1:
        # PDF Generation
        try:
            pdf_bytes = generate_student_pdf_report(assessment)
            st.download_button(
                label="📄 Download Assessment Dossier (PDF)",
                data=pdf_bytes,
                file_name=f"EduMetrics_Assessment_{student_data.get('student_id', 'Student')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.error(f"PDF Error: {str(pdf_err)}")
            
    with c_btn2:
        # CSV Export
        summary_df = pd.DataFrame([{
            "Student ID": student_data.get("student_id"),
            "Student Name": student_data.get("student_name"),
            "Specialization": student_data.get("specialization"),
            "Semester": student_data.get("semester"),
            "Target Role": target_role,
            "Academic Marks (%)": student_data.get("academic_percentage"),
            "Attendance (%)": student_data.get("attendance_percentage"),
            "Readiness Score": readiness.get("overall_score"),
            "Readiness Tier": readiness.get("tier_label"),
            "Technical Fit (%)": gap_analysis.get("fit_percentage"),
            "Certifications Count": len(student_data.get("certifications", [])),
            "Internship Status": student_data.get("internship_status"),
            "Projects Count": student_data.get("projects_count"),
            "Placement Status": student_data.get("placement_status")
        }])
        csv_bytes = summary_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Export Summary (CSV)",
            data=csv_bytes,
            file_name=f"student_assessment_{student_data.get('student_id', 'student')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with c_btn3:
        # SQLite Persistence
        if st.button("💾 Save Assessment to SQLite", use_container_width=True):
            try:
                row_id = save_assessment_record(assessment)
                st.success(f"Assessment successfully persisted to SQLite database (Record #{row_id})!")
            except Exception as db_err:
                st.error(f"Database error: {str(db_err)}")
                
    with c_btn4:
        # Incorporate into Active Cohort
        if st.button("📥 Add to Active Session Cohort", use_container_width=True, help="Appends this student into the active dataset so all 7 other dashboards reflect this student"):
            try:
                # Map skills to 3 standard categories for main schema compatibility
                sk = student_data.get("skills", {})
                sql_p = SKILL_LEVEL_NAMES.get(sk.get("SQL", 3), "Intermediate")
                py_p = SKILL_LEVEL_NAMES.get(sk.get("Python", 2), "Beginner")
                bi_p = SKILL_LEVEL_NAMES.get(sk.get("Power BI", 3), "Intermediate")
                
                # Constrain to 3NF schema values
                to_main_p = lambda p: "Advanced" if p in ["Advanced", "Expert"] else ("Intermediate" if p == "Intermediate" else "Beginner")
                
                new_row = {
                    "student_id": student_data["student_id"],
                    "student_name": student_data["student_name"],
                    "gender": student_data.get("gender", "Non-Binary"),
                    "specialization": student_data["specialization"],
                    "semester": student_data["semester"],
                    "academic_percentage": student_data["academic_percentage"],
                    "attendance_percentage": student_data["attendance_percentage"],
                    "sql_proficiency": to_main_p(sql_p),
                    "python_proficiency": to_main_p(py_p),
                    "power_bi_proficiency": to_main_p(bi_p),
                    "certifications_count": len(student_data.get("certifications", [])),
                    "internship_status": student_data.get("internship_status", "Not Completed"),
                    "placement_status": student_data.get("placement_status", "Unplaced"),
                    "company": student_data.get("internship_company", None) if student_data.get("placement_status") == "Placed" else None,
                    "salary_lpa": 12.0 if student_data.get("placement_status") == "Placed" else None
                }
                
                # Also save to SQLite 4 normalized tables
                save_single_student_to_db(new_row)
                
                # Enrich and append to session_state["active_dataset"]
                from src.data_loader import clean_and_enrich_data
                current_active = st.session_state["active_dataset"]
                
                # Check duplicate
                if student_data["student_id"] in current_active["student_id"].values:
                    # Update row in place
                    current_active = current_active[current_active["student_id"] != student_data["student_id"]]
                    
                new_df = pd.DataFrame([new_row])
                updated_active = pd.concat([current_active, new_df], ignore_index=True)
                updated_active = clean_and_enrich_data(updated_active)
                st.session_state["active_dataset"] = updated_active
                
                st.success(f"🎉 Candidate {student_data['student_id']} ({student_data['student_name']}) added to the active cohort! Total students: {len(updated_active)}.")
                st.rerun()
            except Exception as add_err:
                st.error(f"Cohort addition error: {str(add_err)}")

    # Historical Assessments Log Expander
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🗄️ Historical Saved Student Assessments Log (SQLite)"):
        try:
            hist_df = load_all_assessments()
            if len(hist_df) > 0:
                st.dataframe(hist_df, use_container_width=True, hide_index=True)
            else:
                st.info("No saved assessments in SQLite yet. Click 'Save Assessment to SQLite' above to persist candidate records.")
        except Exception:
            st.info("Assessments log will populate as candidates are saved.")

    render_footer()
