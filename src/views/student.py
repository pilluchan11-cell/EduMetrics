"""
Individual Student Analytics View for EduMetrics.
Deep-dive profile explorer, benchmark radar chart, and explainable personalized guidance.
"""

import streamlit as st
import pandas as pd
from src.rules_engine import evaluate_student_profile
from src.visualizations import plot_student_radar_benchmark
from src.ui_components import render_hero, render_disclaimer, render_kpi
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_ACCENT


def render(df: pd.DataFrame) -> None:
    """Renders the individual student analytics page."""
    render_hero("Individual Student Deep Dive & Profiler")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records available in the filtered dataset.")
        return
        
    st.markdown('<div class="section-title">🔍 Select or Search Student Record</div>', unsafe_allow_html=True)
    
    # Quick filter and selector
    student_labels = {
        row["student_id"]: f"{row['student_id']} - {row['student_name']} ({row['specialization']})"
        for _, row in df.iterrows()
    }
    
    col_sel1, col_sel2 = st.columns([8, 4])
    with col_sel1:
        selected_id = st.selectbox(
            "Choose a student:",
            options=list(student_labels.keys()),
            format_func=lambda x: student_labels[x]
        )
    with col_sel2:
        quick_placed_filter = st.radio(
            "Browse Cohort:",
            options=["All", "Only Placed", "Only Unplaced"],
            horizontal=True
        )
        
    # Re-evaluate selection if browse cohort changes
    filtered_students = df.copy()
    if quick_placed_filter == "Only Placed":
        filtered_students = filtered_students[filtered_students["placement_status"].str.lower() == "placed"]
    elif quick_placed_filter == "Only Unplaced":
        filtered_students = filtered_students[filtered_students["placement_status"].str.lower() == "unplaced"]
        
    if selected_id not in filtered_students["student_id"].values:
        if len(filtered_students) > 0:
            selected_id = filtered_students["student_id"].iloc[0]
        else:
            st.info("No students found in this filter.")
            return

    student = df[df["student_id"] == selected_id].iloc[0]
    
    st.markdown("---")
    
    # Student Header Banner
    is_placed = str(student.get("placement_status", "")).lower() == "placed"
    status_badge_class = "badge-placed" if is_placed else "badge-unplaced"
    
    banner_html = f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 24px; color: #0F172A;">{student['student_name']}</h2>
                <span style="color: #64748B; font-size: 14px; font-weight: 500;">
                    ID: <strong>{student['student_id']}</strong> | Specialization: <strong>{student['specialization']}</strong> | Semester: <strong>{student['semester']}</strong>
                </span>
            </div>
            <div>
                <span class="{status_badge_class}" style="font-size: 14px; padding: 6px 14px;">
                    {student['placement_status'].upper()}
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)
    
    # Student Core Metrics Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Academic Score", f"{student['academic_percentage']}%", student.get("grade_band", ""), COLOR_PRIMARY)
    with c2:
        render_kpi("Attendance", f"{student['attendance_percentage']}%", student.get("attendance_band", ""), COLOR_ACCENT if student['attendance_percentage'] >= 75 else COLOR_DANGER)
    with c3:
        render_kpi("Technical Competence", f"{student.get('technical_score_10', 'N/A')}/10", "Composite Skill Index", COLOR_SUCCESS)
    with c4:
        if is_placed:
            render_kpi("Placed Package", f"₹{student.get('salary_lpa', 'N/A')} LPA", f"Company: {student.get('company', '-')}", COLOR_SUCCESS)
        else:
            render_kpi("Placement Status", "In Process", "Seeking Placement", "#64748B")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Profile Details & Radar Benchmark
    col_radar, col_details = st.columns([6, 6])
    
    with col_radar:
        st.markdown('<div class="section-title">📊 Competency Radar Benchmark</div>', unsafe_allow_html=True)
        fig_radar = plot_student_radar_benchmark(student, df)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_details:
        st.markdown('<div class="section-title">📋 Academic & Profile Record</div>', unsafe_allow_html=True)
        
        profile_data = {
            "Attribute": [
                "Gender (Demographic Record)",
                "Undergraduate / Current Major",
                "Python Proficiency",
                "SQL Proficiency",
                "Power BI Proficiency",
                "Verified Certifications",
                "Summer Internship Status",
                "Recruiting Corporate Entity",
                "Compensation Package (CTC)"
            ],
            "Recorded Details": [
                student.get("gender", "-"),
                student.get("specialization", "-"),
                student.get("python_proficiency", "-"),
                student.get("sql_proficiency", "-"),
                student.get("power_bi_proficiency", "-"),
                f"{student.get('certifications_count', 0)} completed",
                student.get("internship_status", "-"),
                student.get("company", "Not Placed / In Process"),
                f"₹{student.get('salary_lpa')} LPA" if is_placed else "N/A"
            ]
        }
        st.dataframe(pd.DataFrame(profile_data), hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Personalized Recommendations Engine Output
    st.markdown('<div class="section-title">💡 Personalized Diagnostic & Actionable Guidance</div>', unsafe_allow_html=True)
    recs = evaluate_student_profile(student)
    
    for r in recs:
        status_color = "#10B981" if r["status"] == "Strength" else ("#EF4444" if r["status"] == "Critical" else "#F59E0B")
        badge_class = "badge-placed" if r["status"] == "Strength" else ("badge-danger" if r["status"] == "Critical" else "badge-warning")
        
        card_html = f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-left: 5px solid {status_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 700; font-size: 15px; color: #0F172A;">{r['title']}</span>
                <span class="{badge_class}">{r['category']} • {r['status']}</span>
            </div>
            <p style="margin: 0 0 6px 0; color: #334155; font-size: 13.5px;">{r['message']}</p>
            <div style="font-size: 13px; color: #1E3A8A; background: #F8FAFC; padding: 8px 12px; border-radius: 6px;">
                <strong>Actionable Next Step:</strong> {r['action']}
            </div>
            <div style="font-size: 11.5px; color: #64748B; margin-top: 5px;">
                <em>Policy/Rationale:</em> {r['rationale']}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
