"""
Individual Student Assessment & Performance Analyzer View for EduMetrics.
Features career-specific skill benchmarking, student vs. role gap comparison,
explainable 6-pillar readiness scoring with missing-component handling,
and prioritized personalized learning roadmaps.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import io

from src.benchmarks import (
    CAREER_ROLE_BENCHMARKS,
    DEFAULT_READINESS_WEIGHTS,
    COMPONENT_DISPLAY_NAMES,
    SKILL_LEVEL_NAMES,
    BENCHMARK_DISCLAIMER
)
from src.assessment_engine import (
    calculate_skill_gaps,
    calculate_readiness_score,
    generate_learning_roadmap,
    generate_individual_assessment,
    get_sample_student_profile,
    _safe_int,
    _safe_float
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
    render_hero("Career-Specific Competency Benchmarking & Student Analyzer")
    render_disclaimer()
    
    # Initialize assessment session state cache
    if "assessment_form_data" not in st.session_state:
        st.session_state["assessment_form_data"] = get_sample_student_profile("balanced")
    if "current_assessment" not in st.session_state:
        initial_sample = st.session_state["assessment_form_data"]
        st.session_state["current_assessment"] = generate_individual_assessment(
            initial_sample, 
            initial_sample.get("target_role", "Data Analyst")
        )

    # -------------------------------------------------------------------------
    # Top Control Bar: Quick Load Demonstrations & Reset
    # -------------------------------------------------------------------------
    render_section_header(
        "Candidate Profile Ingestion & Benchmark Setup",
        "Enter student metrics or load calibrated sample profiles to benchmark competency gaps and placement readiness.",
        "📝"
    )
    
    col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
    with col_p1:
        if st.button("⚡ High Achiever", use_container_width=True, help="Load distinction sample: 86% marks, multiple certs, internship completed"):
            st.session_state["assessment_form_data"] = get_sample_student_profile("high_achiever")
            st.session_state["current_assessment"] = generate_individual_assessment(
                st.session_state["assessment_form_data"], 
                "Data Analyst"
            )
            st.rerun()
    with col_p2:
        if st.button("⚡ Balanced Cohort", use_container_width=True, help="Load typical student: 72% marks, 79% attendance, 1 cert, 1 project"):
            st.session_state["assessment_form_data"] = get_sample_student_profile("balanced")
            st.session_state["current_assessment"] = generate_individual_assessment(
                st.session_state["assessment_form_data"], 
                "Data Analyst"
            )
            st.rerun()
    with col_p3:
        if st.button("⚡ Support Needed", use_container_width=True, help="Load at-risk student: 58% marks, 71% attendance, skill deficits"):
            st.session_state["assessment_form_data"] = get_sample_student_profile("needs_intervention")
            st.session_state["current_assessment"] = generate_individual_assessment(
                st.session_state["assessment_form_data"], 
                "Business Analyst"
            )
            st.rerun()
    with col_p4:
        if st.button("⚡ Missing Data Demo", use_container_width=True, help="Demonstrates missing component recalculation & coverage disclosure"):
            st.session_state["assessment_form_data"] = get_sample_student_profile("missing_components")
            st.session_state["current_assessment"] = generate_individual_assessment(
                st.session_state["assessment_form_data"], 
                "Data Analyst"
            )
            st.rerun()
    with col_p5:
        if st.button("↺ Reset Form", use_container_width=True, help="Clear all inputs to empty defaults"):
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
                "skills": {k: 2 for k in [
                    "Excel", "SQL", "Python", "Power BI", "Tableau", "Statistics", 
                    "Machine Learning", "Mathematics", "Problem-solving", "Communication", 
                    "Data Modeling / ETL", "Product Metrics / A/B Testing"
                ]},
                "certifications": [],
                "certifications_count": 0,
                "certifications_provided": True,
                "internship_status": "Not Completed",
                "internship_provided": True,
                "internship_company": "",
                "internship_duration_months": 0,
                "project_experience": "",
                "projects_count": 0,
                "projects_provided": True,
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
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-size: 12.5px; color: #475569;">
                💡 <em>{BENCHMARK_DISCLAIMER}</em>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ---------------- Section 1: Target Career Role Selection ----------------
        st.markdown("#### 1. Select Target Career Direction")
        role_options = [
            "Business Analyst",
            "Data Analyst",
            "Data Scientist",
            "Business Intelligence Analyst",
            "Product Analyst"
        ]
        cur_role = current_data.get("target_role", "Data Analyst")
        selected_role = st.selectbox(
            "Select Candidate's Target Career Role for Benchmarking *:",
            options=role_options,
            index=role_options.index(cur_role) if cur_role in role_options else 1,
            help="Candidate competencies will be benchmarked against this role's requirement matrix."
        )
        
        role_meta = CAREER_ROLE_BENCHMARKS[selected_role]
        st.info(f"🎯 **Target Role Scope ({selected_role}):** {role_meta['description']}")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section 2: Basic Identification ----------------
        st.markdown("#### 2. Basic Identification & Academic Specialization")
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            val_id = st.text_input(
                "Student ID *", 
                value=str(current_data.get("student_id", "")),
                placeholder="e.g. STU-2026-905",
                help="Unique alphanumeric student code."
            )
        with r1_c2:
            val_name = st.text_input(
                "Student Full Name *", 
                value=str(current_data.get("student_name", "")),
                placeholder="e.g. Ananya Sen",
                help="Official enrolled student name."
            )
        with r1_c3:
            gender_options = ["Male", "Female", "Non-Binary"]
            cur_gender = current_data.get("gender", "Non-Binary")
            val_gender = st.selectbox(
                "Gender Demographic",
                options=gender_options,
                index=gender_options.index(cur_gender) if cur_gender in gender_options else 2
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

        # ---------------- Section 3: Academic Performance ----------------
        st.markdown("#### 3. Academic Performance (15% Base Weight)")
        acad_available = st.checkbox("Include Academic Marks in Assessment", value=True, help="Uncheck if academic marks are pending/unrecorded to test missing-component recalculation.")
        
        val_acad_pct = None
        val_cgpa = 7.0
        val_scale = 10.0
        sub_marks_dict = {}
        
        if acad_available:
            g_c1, g_c2, g_c3 = st.columns(3)
            with g_c1:
                val_cgpa = st.number_input(
                    "Current Cumulative GPA / CGPA",
                    min_value=0.0,
                    max_value=10.0,
                    value=_safe_float(current_data.get("cgpa"), 7.2),
                    step=0.1
                )
            with g_c2:
                val_scale = st.selectbox(
                    "Grading Scale",
                    options=[10.0, 4.0],
                    index=0 if current_data.get("cgpa_scale", 10.0) == 10.0 else 1,
                    format_func=lambda x: f"{x:.1f} Point Scale"
                )
            with g_c3:
                sug_acad = round((val_cgpa / val_scale) * 100.0, 1) if val_scale > 0 else 70.0
                val_acad_pct = st.number_input(
                    "Master's Overall Aggregate Percentage (%) *",
                    min_value=0.0,
                    max_value=100.0,
                    value=_safe_float(current_data.get("academic_percentage"), sug_acad),
                    step=0.5
                )
                
            with st.expander("Optional: Secondary Marks & Subject Breakdown"):
                p_c1, p_c2, p_c3 = st.columns(3)
                with p_c1:
                    val_10th = st.number_input("10th Standard (%)", min_value=0.0, max_value=100.0, value=_safe_float(current_data.get("tenth_percentage"), 0.0), step=0.5)
                with p_c2:
                    val_12th = st.number_input("12th Standard (%)", min_value=0.0, max_value=100.0, value=_safe_float(current_data.get("twelfth_percentage"), 0.0), step=0.5)
                with p_c3:
                    val_grad = st.number_input("Graduation Degree (%)", min_value=0.0, max_value=100.0, value=_safe_float(current_data.get("grad_percentage"), 0.0), step=0.5)
                    
                cur_subs = current_data.get("subject_marks", {})
                s1_c1, s1_c2 = st.columns(2)
                with s1_c1:
                    s1_n = st.text_input("Subject 1 Name", value="Business Statistics", key="v_sub1_n")
                    s1_m = st.number_input("Subject 1 Mark (%)", min_value=0.0, max_value=100.0, value=_safe_float(cur_subs.get("Business Statistics", 75.0)), step=1.0, key="v_sub1_m")
                with s1_c2:
                    s2_n = st.text_input("Subject 2 Name", value="Database & SQL Systems", key="v_sub2_n")
                    s2_m = st.number_input("Subject 2 Mark (%)", min_value=0.0, max_value=100.0, value=_safe_float(cur_subs.get("SQL Querying", 72.0)), step=1.0, key="v_sub2_m")
                if s1_n.strip():
                    sub_marks_dict[s1_n.strip()] = s1_m
                if s2_n.strip():
                    sub_marks_dict[s2_n.strip()] = s2_m
        else:
            st.warning("⚠️ Academic marks unrecorded: This component will be excluded from the readiness score; its 15% weight will be proportionally redistributed.")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section 4: Classroom Attendance ----------------
        st.markdown("#### 4. Classroom Attendance Compliance")
        att_c1, att_c2 = st.columns([2, 1])
        with att_c1:
            val_att = st.slider(
                "Classroom & Lab Attendance (%) *",
                min_value=0.0,
                max_value=100.0,
                value=_safe_float(current_data.get("attendance_percentage"), 78.0),
                step=0.5,
                help=f"Institutional mandatory compliance threshold is {ATTENDANCE_CRITICAL_THRESHOLD}%."
            )
        with att_c2:
            st.write(" ")
            if val_att >= ATTENDANCE_CRITICAL_THRESHOLD:
                st.success(f"✅ Compliant ({val_att:.1f}% ≥ {ATTENDANCE_CRITICAL_THRESHOLD}%)")
            else:
                st.error(f"⚠️ Policy Risk: Below {ATTENDANCE_CRITICAL_THRESHOLD}% Cutoff")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section 5: Technical Skills (40% Base Weight) ----------------
        st.markdown("#### 5. Technical & Domain Skills (40% Base Weight)")
        st.markdown(
            """
            <div style="font-size: 11.5px; color: #64748B; margin-bottom: 10px;">
                <strong>Proficiency Scale (1-5):</strong> Level 1: Beginner | Level 2: Basic | Level 3: Intermediate | Level 4: Advanced | Level 5: Expert
            </div>
            """,
            unsafe_allow_html=True
        )
        
        cur_skills = current_data.get("skills", {})
        
        def skill_input(label: str, skill_key: str, default_lvl: int = 2):
            raw = cur_skills.get(skill_key, default_lvl)
            val = _safe_int(raw, default_lvl)
            val = max(1, min(5, val))
            return st.selectbox(
                label,
                options=[1, 2, 3, 4, 5],
                index=val - 1,
                format_func=lambda x: f"L{x}: {SKILL_LEVEL_NAMES[x]}",
                key=f"skill_inp_{skill_key}"
            )
            
        sk1_col1, sk1_col2, sk1_col3, sk1_col4 = st.columns(4)
        with sk1_col1:
            v_excel = skill_input("Microsoft Excel", "Excel", 4)
            v_sql = skill_input("SQL Databases", "SQL", 3)
            v_py = skill_input("Python Programming", "Python", 2)
        with sk1_col2:
            v_bi = skill_input("Power BI", "Power BI", 3)
            v_tab = skill_input("Tableau", "Tableau", 2)
            v_stat = skill_input("Applied Statistics", "Statistics", 3)
        with sk1_col3:
            v_ml = skill_input("Machine Learning", "Machine Learning", 2)
            v_math = skill_input("Mathematics Foundations", "Mathematics", 3)
            v_ps = skill_input("Problem-solving", "Problem-solving", 4)
        with sk1_col4:
            v_comm = skill_input("Business Communication", "Communication", 4)
            v_viz = skill_input("Data Visualization", "Data Visualization", 3)
            v_etl = skill_input("Data Modeling / ETL", "Data Modeling / ETL", 2)

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section 6: Certifications (10% Base Weight) ----------------
        st.markdown("#### 6. Industry Certifications (10% Base Weight)")
        certs_available = st.checkbox("Certifications Evaluated for Candidate", value=bool(current_data.get("certifications_provided", True)))
        
        val_certs = []
        if certs_available:
            standard_certs = [
                "Microsoft Power BI Data Analyst (PL-300)",
                "Google Data Analytics Professional Certificate",
                "IBM Data Analyst Professional Certificate",
                "SQL for Data Science (Coursera / HackerRank)",
                "Python Data Structures & Applied Analytics",
                "Tableau Certified Data Analyst",
                "AWS Certified Cloud Practitioner"
            ]
            cur_certs = current_data.get("certifications", [])
            val_certs = st.multiselect(
                "Select Verified Completed Credentials:",
                options=standard_certs,
                default=[c for c in cur_certs if c in standard_certs],
                help="Only select verified completed certifications."
            )
        else:
            val_certs = None
            st.info("ℹ️ Certifications marked unrecorded/pending: Excluded from calculation and weight redistributed.")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section 7: Corporate Internship (10% Base Weight) ----------------
        st.markdown("#### 7. Corporate Internship (10% Base Weight)")
        intern_available = st.checkbox("Internship Status Evaluated for Candidate", value=bool(current_data.get("internship_provided", True)))
        
        val_intern = None
        val_intern_co = ""
        if intern_available:
            i_col1, i_col2 = st.columns([1, 2])
            with i_col1:
                intern_opts = ["Not Completed", "Completed"]
                cur_i = str(current_data.get("internship_status", "Not Completed"))
                val_intern = st.selectbox(
                    "Internship Status",
                    options=intern_opts,
                    index=1 if "completed" in cur_i.lower() and "not" not in cur_i.lower() else 0
                )
            with i_col2:
                val_intern_co = st.text_input("Employer / Entity (Optional)", value=str(current_data.get("internship_company", "")), placeholder="e.g. KPMG, Amazon, Deloitte")
        else:
            st.info("ℹ️ Internship marked unrecorded/pending: Excluded from calculation and weight redistributed.")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section 8: Practical Project Experience (10% Base Weight) ----------------
        st.markdown("#### 8. Applied Portfolio Projects (10% Base Weight)")
        proj_available = st.checkbox("Project Portfolio Evaluated for Candidate", value=bool(current_data.get("projects_provided", True)))
        
        val_proj_count = None
        val_proj_desc = ""
        if proj_available:
            p_c1, p_c2 = st.columns([1, 2])
            with p_c1:
                val_proj_count = st.number_input(
                    "Completed Analytics Projects",
                    min_value=0,
                    max_value=15,
                    value=_safe_int(current_data.get("projects_count"), 1),
                    step=1
                )
            with p_c2:
                val_proj_desc = st.text_input(
                    "Project Portfolio Summary",
                    value=str(current_data.get("project_experience", "")),
                    placeholder="Brief domain or tool highlights"
                )
        else:
            st.info("ℹ️ Project experience marked unrecorded/pending: Excluded from calculation and weight redistributed.")

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # ---------------- Section 9: Soft Skills & Placement Status ----------------
        st.markdown("#### 9. Soft Skills, Aptitude & Placement Status (15% Base Weight)")
        s_c1, s_c2, s_c3, s_c4 = st.columns(4)
        with s_c1:
            apt_opts = [1, 2, 3, 4, 5]
            val_apt = st.selectbox(
                "Cognitive Aptitude Level",
                options=apt_opts,
                index=_safe_int(current_data.get("aptitude_level"), 3) - 1,
                format_func=lambda x: f"L{x}: {['Needs Work', 'Basic', 'Competent', 'Proficient', 'Exceptional'][x-1]}"
            )
        with s_c2:
            res_opts = ["Draft", "Reviewed", "Ready / Verified"]
            cur_r = current_data.get("resume_status", "Reviewed")
            val_resume = st.selectbox(
                "Resume Review Status",
                options=res_opts,
                index=res_opts.index(cur_r) if cur_r in res_opts else 1
            )
        with s_c3:
            mock_opts = ["Not Started", "1 Mock Interview", "Multiple Mocks Completed"]
            cur_m = current_data.get("interview_status", "1 Mock Interview")
            val_mock = st.selectbox(
                "Mock Interview Experience",
                options=mock_opts,
                index=mock_opts.index(cur_m) if cur_m in mock_opts else 1
            )
        with s_c4:
            place_opts = ["Unplaced", "Placed", "In Process"]
            cur_p = current_data.get("placement_status", "Unplaced")
            val_place = st.selectbox(
                "Recruitment Status",
                options=place_opts,
                index=place_opts.index(cur_p) if cur_p in place_opts else 0
            )

        # ---------------- Action / Submit Button ----------------
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_clicked = st.button(
            "🚀 Benchmark Student Against Career Role & Generate Diagnostic Dossier",
            use_container_width=True,
            type="primary"
        )
        
        if analyze_clicked:
            errors = []
            if not val_id.strip():
                errors.append("Student ID is required.")
            if not val_name.strip():
                errors.append("Student Full Name is required.")
            if val_att < 0.0 or val_att > 100.0:
                errors.append("Attendance Percentage must be between 0.0% and 100.0%.")
            if acad_available and (val_acad_pct is not None and (val_acad_pct < 0.0 or val_acad_pct > 100.0)):
                errors.append("Academic Percentage must be between 0.0% and 100.0%.")
                
            if errors:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                compiled_skills = {
                    "Excel": v_excel,
                    "SQL": v_sql,
                    "Python": v_py,
                    "Power BI": v_bi,
                    "Tableau": v_tab,
                    "Statistics": v_stat,
                    "Machine Learning": v_ml,
                    "Mathematics": v_math,
                    "Problem-solving": v_ps,
                    "Communication": v_comm,
                    "Data Visualization": v_viz,
                    "Data Modeling / ETL": v_etl,
                    "Product Metrics / A/B Testing": 4 if selected_role == "Product Analyst" else 2
                }

                assembled_student = {
                    "student_id": val_id.strip(),
                    "student_name": val_name.strip(),
                    "gender": val_gender,
                    "specialization": val_spec,
                    "semester": val_sem,
                    "academic_year": val_year.strip(),
                    "tenth_percentage": float(val_10th) if acad_available else 0.0,
                    "twelfth_percentage": float(val_12th) if acad_available else 0.0,
                    "grad_percentage": float(val_grad) if acad_available else 0.0,
                    "cgpa": float(val_cgpa) if acad_available else 0.0,
                    "cgpa_scale": float(val_scale),
                    "academic_percentage": float(val_acad_pct) if acad_available else None,
                    "subject_marks": sub_marks_dict,
                    "attendance_percentage": float(val_att),
                    "skills": compiled_skills,
                    "certifications": val_certs,
                    "certifications_count": len(val_certs) if val_certs is not None else 0,
                    "certifications_provided": certs_available,
                    "internship_status": val_intern,
                    "internship_provided": intern_available,
                    "internship_company": val_intern_co.strip() if val_intern_co else "",
                    "internship_duration_months": 2 if val_intern == "Completed" else 0,
                    "project_experience": val_proj_desc.strip(),
                    "projects_count": val_proj_count,
                    "projects_provided": proj_available,
                    "resume_status": val_resume,
                    "communication_level": v_comm,
                    "aptitude_level": val_apt,
                    "interview_status": val_mock,
                    "placement_status": val_place,
                    "target_role": selected_role
                }

                st.session_state["assessment_form_data"] = assembled_student
                st.session_state["current_assessment"] = generate_individual_assessment(
                    assembled_student,
                    selected_role
                )
                st.success(f"✅ Performance benchmarked against {selected_role}! Diagnostic dossier updated below.")
                st.rerun()

    # -------------------------------------------------------------------------
    # Render Analytical Report & Decision-Support Dossier
    # -------------------------------------------------------------------------
    assessment = st.session_state.get("current_assessment")
    if not assessment:
        st.info("💡 Complete student information above and click benchmark button to view individual dossier.")
        render_footer()
        return

    student_data = assessment["student_data"]
    target_role = assessment["target_role"]
    readiness = assessment["readiness"]
    gap_analysis = readiness["gap_analysis"]
    roadmap = assessment["learning_roadmap"]
    strengths = assessment["strengths"]
    weaknesses = assessment["weaknesses"]
    recommendations = assessment["recommendations"]

    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header(
        f"Diagnostic Assessment: {student_data.get('student_name', 'Student')} ({student_data.get('student_id', 'N/A')})",
        f"Career-specific competency benchmarking and multi-pillar readiness evaluation vs. {target_role}.",
        "📊"
    )

    # -------------------------------------------------------------------------
    # Executive KPI Ribbon & Coverage Callout
    # -------------------------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        score_val = readiness["overall_score"]
        tier_col = readiness["tier_color"]
        render_kpi(
            "Readiness Score",
            f"{score_val:.1f} / 100",
            f"Classification: {readiness['tier_label'].split('/')[0].strip()}",
            tier_col,
            icon="🎯",
            chip_text=readiness["tier_label"].split("/")[0].strip(),
            chip_color="#EFF6FF"
        )
    with k2:
        cov_val = readiness["coverage_percentage"]
        cov_col = COLOR_SUCCESS if cov_val >= 90.0 else (COLOR_PRIMARY if cov_val >= 70.0 else COLOR_ACCENT)
        render_kpi(
            "Assessment Coverage",
            f"{cov_val:.1f}%",
            f"{readiness['available_component_count']} of {readiness['total_component_count']} Components Evaluated",
            cov_col,
            icon="📋",
            chip_text="Data Coverage",
            chip_color="#CCFBF1" if cov_val >= 90.0 else "#FEF3C7"
        )
    with k3:
        fit_pct = gap_analysis["fit_percentage"]
        render_kpi(
            "Competency Fit",
            f"{fit_pct:.1f}%",
            f"Target: {target_role} ({gap_analysis['student_matched_points']}/{gap_analysis['total_required_points']} pts)",
            COLOR_PRIMARY,
            icon="⚡",
            chip_text=target_role,
            chip_color="#EFF6FF"
        )
    with k4:
        raw_ac = student_data.get("academic_percentage")
        acad_str = f"{float(raw_ac):.1f}%" if raw_ac is not None else "Not Provided"
        render_kpi(
            "Academic Marks",
            acad_str,
            f"Attendance: {student_data.get('attendance_percentage', 0.0):.1f}%",
            COLOR_SECONDARY,
            icon="📚",
            chip_text="Academics",
            chip_color="#EFF6FF"
        )

    # Coverage Warning / Disclosure Banner
    missing_items = readiness.get("missing_components", [])
    if missing_items:
        st.markdown(
            f"""
            <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 10px 16px; margin: 12px 0 16px 0; font-size: 13px; color: #92400E;">
                <strong>⚠️ Data Coverage Notice ({cov_val:.1f}%):</strong> The candidate profile excludes: <em>{', '.join(missing_items)}</em>. 
                Missing components are not penalized as zero; available weights have been proportionally recalibrated.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Visual Diagnostics Tabs
    # -------------------------------------------------------------------------
    tab_gap, tab_radar, tab_pillars, tab_table = st.tabs([
        "📊 Student vs. Benchmark Chart",
        "🎯 Radar Competency Profile",
        "⚖️ Component Weights & Scores",
        "📋 Full Competency Gap Table"
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
            st.metric("Surplus / Exceeds Benchmark", f"{surplus_cnt} Skills", delta="Competitive Advantage" if surplus_cnt > 0 else None)
        with c_s2:
            st.metric("Meets Benchmark", f"{aligned_cnt} Skills")
        with c_s3:
            st.metric("Deficit Requiring Focus", f"{deficit_cnt} Skills", delta=f"-{deficit_cnt} Gaps" if deficit_cnt > 0 else "No Deficits", delta_color="inverse")

    with tab_radar:
        target_skills_dict = CAREER_ROLE_BENCHMARKS[target_role]["skills"]
        fig_radar = plot_student_competency_radar(student_data.get("skills", {}), target_skills_dict, target_role)
        st.plotly_chart(fig_radar, use_container_width=True)

    with tab_pillars:
        fig_pillars = plot_readiness_component_breakdown(readiness)
        st.plotly_chart(fig_pillars, use_container_width=True)

    with tab_table:
        # Full Student vs Career Benchmark Comparison Table
        table_rows = []
        for item in gap_analysis["skill_comparison"]:
            meets_str = "✅ Meets / Exceeds" if item["meets_benchmark"] else f"❌ Deficit ({abs(item['gap'])} Level{'s' if abs(item['gap']) > 1 else ''})"
            table_rows.append({
                "Competency Dimension": item["skill"],
                "Student Level": f"L{item['student_level']} ({item['student_name']})",
                "Required Benchmark": f"L{item['target_level']} ({item['target_name']})",
                "Skill Gap": f"{item['gap']:+d}",
                "Meets Benchmark?": meets_str
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Prioritized Personalized Learning Roadmap
    # -------------------------------------------------------------------------
    render_section_header(
        "Prioritized Personalized Learning Roadmap",
        f"Sequence of high-impact learning sprints and practical portfolio projects designed to close {student_data.get('student_name', 'candidate')}'s largest skill gaps.",
        "🗺️"
    )
    
    if roadmap:
        for r_item in roadmap:
            p_badge_col = "#EF4444" if r_item["priority"] == 1 else ("#2563EB" if r_item["priority"] == 2 else "#0D9488")
            p_badge_bg = "#FEE2E2" if r_item["priority"] == 1 else ("#EFF6FF" if r_item["priority"] == 2 else "#CCFBF1")
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: #0F172A; font-size: 16px; font-weight: 700;">{r_item['title']}</h4>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <span style="background: {p_badge_bg}; color: {p_badge_col}; font-weight: 700; font-size: 11px; padding: 3px 10px; border-radius: 6px;">
                                    PRIORITY {r_item['priority']}
                                </span>
                                <span style="background: #F1F5F9; color: #475569; font-weight: 600; font-size: 11px; padding: 3px 10px; border-radius: 6px;">
                                    ⏱️ {r_item['duration']}
                                </span>
                            </div>
                        </div>
                        <p style="color: #64748B; font-size: 13px; margin: 0 0 10px 0;">
                            <strong>Current vs. Target:</strong> {r_item['current_status']} → <strong style="color: #2563EB;">{r_item['target_status']}</strong>
                        </p>
                        <div style="background: #F8FAFC; border-left: 4px solid {p_badge_col}; padding: 12px 16px; border-radius: 6px; font-size: 13px; color: #1E293B; margin-bottom: 10px;">
                            <strong style="color: #0F172A;">Specific Learning Objectives:</strong>
                            <ul style="margin: 6px 0 4px 18px; padding: 0;">
                                {''.join(f"<li>{obj}</li>" for obj in r_item['objectives'])}
                            </ul>
                        </div>
                        <div style="background: #EFF6FF; border: 1px dashed #BFDBFE; padding: 10px 14px; border-radius: 6px; font-size: 12.5px; color: #1E40AF;">
                            <strong>🛠️ Practical Project Suggestion:</strong> {r_item['practical_project']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.success("🎉 Candidate profile aligns comprehensively with all benchmark requirements for this target role!")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Diagnostic Observations: Strongest Areas vs. Biggest Opportunities
    # -------------------------------------------------------------------------
    render_section_header(
        "Candidate Profile Diagnostics: Strengths vs. Priority Gaps",
        "Rule-derived identification of core competitive advantages and primary areas needing intervention.",
        "🔍"
    )
    col_str, col_weak = st.columns(2)
    with col_str:
        st.markdown(
            """
            <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #166534; font-size: 15px;">🌟 Strongest Competency Areas</h4>
            """,
            unsafe_allow_html=True
        )
        if strengths:
            for s in strengths:
                st.markdown(f"<p style='color: #14532D; font-size: 13px; margin: 4px 0;'>• {s}</p>", unsafe_allow_html=True)
        else:
            st.write("No distinct competitive advantages recorded yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_weak:
        st.markdown(
            """
            <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #991B1B; font-size: 15px;">⚠️ Biggest Improvement Opportunities</h4>
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

    # -------------------------------------------------------------------------
    # Export, Persistence & Cohort Integration
    # -------------------------------------------------------------------------
    render_section_header(
        "Dossier Export, Database Persistence & Cohort Integration",
        "Download official PDF assessment dossiers, persist records to relational SQLite storage, or incorporate into active cohort analytics.",
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
            "Readiness Score": readiness.get("overall_score"),
            "Readiness Tier": readiness.get("tier_label"),
            "Coverage Percentage": readiness.get("coverage_percentage"),
            "Technical Fit (%)": gap_analysis.get("fit_percentage"),
            "Academic Percentage": student_data.get("academic_percentage"),
            "Attendance Percentage": student_data.get("attendance_percentage"),
            "Certifications Count": len(student_data.get("certifications", [])) if student_data.get("certifications") is not None else "Unrecorded",
            "Internship Status": student_data.get("internship_status"),
            "Projects Count": student_data.get("projects_count"),
            "Top Priority Recommendation": roadmap[0]["title"] if roadmap else "N/A"
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
        if st.button("📥 Add to Active Session Cohort", use_container_width=True, help="Appends this student into the active dataset so all other dashboards reflect this student"):
            try:
                sk = student_data.get("skills", {})
                sql_p = SKILL_LEVEL_NAMES.get(sk.get("SQL", 3), "Intermediate")
                py_p = SKILL_LEVEL_NAMES.get(sk.get("Python", 2), "Beginner")
                bi_p = SKILL_LEVEL_NAMES.get(sk.get("Power BI", 3), "Intermediate")
                
                to_main_p = lambda p: "Advanced" if p in ["Advanced", "Expert"] else ("Intermediate" if p == "Intermediate" else "Beginner")
                
                acad_val = student_data.get("academic_percentage")
                acad_safe = float(acad_val) if acad_val is not None else 65.0
                
                new_row = {
                    "student_id": student_data["student_id"],
                    "student_name": student_data["student_name"],
                    "gender": student_data.get("gender", "Non-Binary"),
                    "specialization": student_data["specialization"],
                    "semester": student_data["semester"],
                    "academic_percentage": acad_safe,
                    "attendance_percentage": float(student_data.get("attendance_percentage", 75.0)),
                    "sql_proficiency": to_main_p(sql_p),
                    "python_proficiency": to_main_p(py_p),
                    "power_bi_proficiency": to_main_p(bi_p),
                    "certifications_count": len(student_data.get("certifications", [])) if student_data.get("certifications") is not None else 0,
                    "internship_status": student_data.get("internship_status", "Not Completed") if student_data.get("internship_status") is not None else "Not Completed",
                    "placement_status": student_data.get("placement_status", "Unplaced"),
                    "company": student_data.get("internship_company", None) if student_data.get("placement_status") == "Placed" else None,
                    "salary_lpa": 12.0 if student_data.get("placement_status") == "Placed" else None
                }
                
                save_single_student_to_db(new_row)
                
                from src.data_loader import clean_and_enrich_data
                current_active = st.session_state["active_dataset"]
                
                if student_data["student_id"] in current_active["student_id"].values:
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
