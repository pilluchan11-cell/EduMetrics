"""
Individual Student Analytics View for EduMetrics.
Deep-dive profile explorer, benchmark radar chart, and explainable personalized guidance.
"""

import streamlit as st
import pandas as pd
from src.rules_engine import evaluate_student_profile
from src.visualizations import plot_student_radar_benchmark
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_kpi, 
    render_section_header,
    render_footer
)
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_ACCENT, COLOR_SECONDARY


def render(df: pd.DataFrame) -> None:
    """Renders the individual student analytics page."""
    render_hero("Individual Student Profile & Diagnostic Dossier")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records available in the filtered dataset. Reset sidebar filters.")
        return
        
    render_section_header(
        "Student Profile Selector",
        "Select or search any student to inspect individual grades, attendance, skills, and personalized guidance.",
        "🔍"
    )
    
    # Search and Cohort Slicing
    col_search, col_filter = st.columns([7, 5])
    with col_search:
        search_query = st.text_input(
            "🔎 Search Student by ID, Name, or Major:",
            placeholder="e.g. EDU-2026-001, Priya, or Business Analytics",
            help="Filter candidate profiles in real-time."
        )
    with col_filter:
        quick_placed_filter = st.radio(
            "Cohort Quick View:",
            options=["All Students", "Placed Only", "Unplaced Only"],
            horizontal=True
        )
        
    filtered_students = df.copy()
    if quick_placed_filter == "Placed Only":
        filtered_students = filtered_students[filtered_students["placement_status"].str.lower() == "placed"]
    elif quick_placed_filter == "Unplaced Only":
        filtered_students = filtered_students[filtered_students["placement_status"].str.lower() == "unplaced"]
        
    if search_query.strip():
        q = search_query.strip().lower()
        filtered_students = filtered_students[
            filtered_students["student_id"].astype(str).str.lower().str.contains(q, na=False) |
            filtered_students["student_name"].astype(str).str.lower().str.contains(q, na=False) |
            filtered_students["specialization"].astype(str).str.lower().str.contains(q, na=False)
        ]
        
    if len(filtered_students) == 0:
        st.info("ℹ️ No students match your search criteria or placement filter. Try refining your search query.")
        render_footer()
        return
        
    student_labels = {
        row["student_id"]: f"{row['student_id']} - {row['student_name']} ({row['specialization']}) [{row['placement_status']}]"
        for _, row in filtered_students.iterrows()
    }
    
    selected_id = st.selectbox(
        f"Select Profile ({len(filtered_students)} candidates matching):",
        options=list(student_labels.keys()),
        format_func=lambda x: student_labels[x]
    )

    student = filtered_students[filtered_students["student_id"] == selected_id].iloc[0]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Executive Student Dossier Banner
    is_placed = str(student.get("placement_status", "")).lower() == "placed"
    status_badge_class = "badge-placed" if is_placed else "badge-unplaced"
    status_icon = "✅" if is_placed else "⏳"
    status_text = "OFFER ACCEPTED" if is_placed else "IN PLACEMENT PIPELINE"
    
    banner_html = f"""
    <div class="student-dossier-card">
        <div class="student-dossier-left">
            <div class="student-dossier-avatar">
                👤
            </div>
            <div>
                <div class="student-dossier-name-row">
                    <h2 class="student-dossier-name">{student['student_name']}</h2>
                    <span style="background: #EFF6FF; color: #1E40AF; padding: 2px 8px; border-radius: 6px; font-size: 11.5px; font-weight: 700; white-space: nowrap;">{student['student_id']}</span>
                </div>
                <div class="student-dossier-meta">
                    Major: <strong style="color: #334155;">{student['specialization']}</strong> • 
                    Semester: <strong style="color: #334155;">{student['semester']}</strong> • 
                    Demographics: <strong style="color: #334155;">{student.get('gender', '-')}</strong>
                </div>
            </div>
        </div>
        <div>
            <span class="{status_badge_class}" style="font-size: 12px; padding: 5px 12px; letter-spacing: 0.03em;">
                {status_icon} {status_text}
            </span>
        </div>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)
    
    # Core Student Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi(
            "Academic Marks", 
            f"{student['academic_percentage']}%", 
            student.get("grade_band", ""), 
            COLOR_PRIMARY,
            icon="🎓",
            chip_text="Score",
            chip_color="#EFF6FF"
        )
    with c2:
        att_col = COLOR_ACCENT if student['attendance_percentage'] >= 75 else COLOR_DANGER
        render_kpi(
            "Attendance Compliance", 
            f"{student['attendance_percentage']}%", 
            student.get("attendance_band", ""), 
            att_col,
            icon="⏰",
            chip_text="Attendance",
            chip_color="#FEF3C7" if student['attendance_percentage'] >= 75 else "#FEE2E2"
        )
    with c3:
        render_kpi(
            "Technical Skill Index", 
            f"{student.get('technical_score_10', 'N/A')}/10", 
            "Software Competency Rating", 
            COLOR_SECONDARY,
            icon="💻",
            chip_text="Tool Index",
            chip_color="#CCFBF1"
        )
    with c4:
        if is_placed:
            render_kpi(
                "Secured Offer Package", 
                f"₹{student.get('salary_lpa', 'N/A')} LPA", 
                f"Company: {student.get('company', '-')}", 
                COLOR_SUCCESS,
                icon="💼",
                chip_text="Placed",
                chip_color="#DCFCE7"
            )
        else:
            render_kpi(
                "Recruitment Status", 
                "Seeking Offer", 
                "Active in Placement Drives", 
                "#64748B",
                icon="⏳",
                chip_text="In Process",
                chip_color="#F1F5F9"
            )
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Profile Details & Radar Benchmark Row
    col_radar, col_details = st.columns([6, 6])
    
    with col_radar:
        fig_radar = plot_student_radar_benchmark(student, df)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_details:
        render_section_header("Academic & Technical Profile Record", "Detailed institutional log of student qualifications.", "📋")
        
        profile_data = {
            "Dimension": [
                "Undergraduate / Current Major",
                "Python Proficiency Level",
                "SQL Relational Proficiency",
                "Power BI Business Analytics",
                "Verified Industry Certifications",
                "Summer Internship Completed",
                "Hiring Corporate Partner",
                "Accepted Compensation Package"
            ],
            "Logged Credential": [
                student.get("specialization", "-"),
                student.get("python_proficiency", "-"),
                student.get("sql_proficiency", "-"),
                student.get("power_bi_proficiency", "-"),
                f"{student.get('certifications_count', 0)} Verified Credentials",
                "Yes (Summer Internship Verified)" if student.get("internship_status") == "Completed" else "No Prior Internship Logged",
                student.get("company", "Not Placed / Seeking Offer"),
                f"₹{student.get('salary_lpa')} LPA" if is_placed else "N/A"
            ]
        }
        st.dataframe(pd.DataFrame(profile_data), hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Personalized Recommendations Engine Output
    render_section_header(
        "Explainable Career Diagnostic & Actionable Guidance",
        "Deterministic, rule-based diagnostic flags tailored specifically to this student's profile.",
        "💡"
    )
    recs = evaluate_student_profile(student)
    
    for r in recs:
        status_color = "#10B981" if r["status"] == "Strength" else ("#EF4444" if r["status"] == "Critical" else "#F59E0B")
        badge_class = "badge-placed" if r["status"] == "Strength" else ("badge-danger" if r["status"] == "Critical" else "badge-warning")
        
        card_html = f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid {status_color}; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 15px; color: #0F172A;">{r['title']}</span>
                <span class="{badge_class}">{r['category']} • {r['status']}</span>
            </div>
            <p style="margin: 0 0 8px 0; color: #334155; font-size: 13.5px; line-height: 1.5;">{r['message']}</p>
            <div style="font-size: 13px; color: #1E3A8A; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 9px 14px; border-radius: 6px; margin-bottom: 6px;">
                <strong>Recommended Next Action:</strong> {r['action']}
            </div>
            <div style="font-size: 11.5px; color: #64748B;">
                <em>Policy / Rationale:</em> {r['rationale']}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
    render_footer()
