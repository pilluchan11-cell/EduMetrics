"""
Academic Performance Analytics View for EduMetrics.
Deep-dive analysis of score distributions, attendance relations, grade bands, and cohorts.
"""

import streamlit as st
import pandas as pd
from src.metrics import (
    compute_academic_summary,
    compute_grade_distribution,
    compute_specialization_performance,
    get_top_and_support_students
)
from src.visualizations import (
    plot_academic_distribution,
    plot_grade_distribution,
    plot_attendance_vs_academic,
    plot_semester_comparison
)
from src.ui_components import render_hero, render_disclaimer, render_kpi
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_ACCENT


def render(df: pd.DataFrame) -> None:
    """Renders the academic performance analytics page."""
    render_hero("Academic Performance Analytics")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the current filter criteria.")
        return
        
    stats = compute_academic_summary(df)
    
    # Statistical Summary KPIs
    st.markdown('<div class="section-title">📊 Statistical Summary (Marks & Scores)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Mean Score", f"{stats['mean']}%", f"Median: {stats['median']}%", COLOR_PRIMARY)
    with c2:
        render_kpi("Standard Deviation", f"{stats['std']}%", "Score Dispersion", COLOR_ACCENT)
    with c3:
        render_kpi("Interquartile Range (IQR)", f"{stats['iqr']}%", f"Q25: {stats['q25']}% | Q75: {stats['q75']}%", COLOR_SUCCESS)
    with c4:
        render_kpi("Score Range", f"{stats['min']}% - {stats['max']}%", "Min to Max Observed", "#64748B")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Distributions Row: Grade Bands & Semester Boxplot
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">🏆 Grade Band Distribution</div>', unsafe_allow_html=True)
        grades_df = compute_grade_distribution(df)
        fig_grades = plot_grade_distribution(grades_df)
        st.plotly_chart(fig_grades, use_container_width=True)
        
    with col2:
        st.markdown('<div class="section-title">📅 Semester-Level Score Comparison</div>', unsafe_allow_html=True)
        fig_sem = plot_semester_comparison(df)
        st.plotly_chart(fig_sem, use_container_width=True)
        
    # Attendance vs Academic Performance
    st.markdown('<div class="section-title">🎯 Attendance Compliance vs. Academic Achievement</div>', unsafe_allow_html=True)
    fig_att = plot_attendance_vs_academic(df)
    st.plotly_chart(fig_att, use_container_width=True)
    
    # Specialization Academic Performance Table
    st.markdown('<div class="section-title">🏛️ Academic Metrics by Specialization</div>', unsafe_allow_html=True)
    spec_perf = compute_specialization_performance(df)
    st.dataframe(
        spec_perf.rename(columns={
            "specialization": "Specialization",
            "Total_Students": "Students",
            "Avg_Academic": "Avg Marks (%)",
            "Avg_Attendance": "Avg Attendance (%)",
            "Avg_Tech_Index": "Tech Index (10)",
            "Placed_Count": "Placed",
            "Placement_Rate": "Placement Rate (%)"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cohort Tables: Top Performers & Students Requiring Academic Support
    cohorts = get_top_and_support_students(df, top_n=10)
    
    col_top, col_supp = st.columns(2)
    with col_top:
        st.markdown('<div class="section-title">🌟 Top Performing Students</div>', unsafe_allow_html=True)
        st.caption("Recognizing highest aggregate academic percentages.")
        st.dataframe(
            cohorts["top"].rename(columns={
                "student_id": "ID",
                "student_name": "Name",
                "specialization": "Major",
                "academic_percentage": "Marks (%)",
                "attendance_percentage": "Att (%)",
                "placement_status": "Status"
            }),
            use_container_width=True,
            hide_index=True
        )
        
    with col_supp:
        st.markdown('<div class="section-title">⚠️ Students Requiring Support / Intervention</div>', unsafe_allow_html=True)
        st.caption("Students with Marks < 58% or Attendance < 75% cutoff.")
        if len(cohorts["support"]) > 0:
            st.dataframe(
                cohorts["support"].rename(columns={
                    "student_id": "ID",
                    "student_name": "Name",
                    "specialization": "Major",
                    "academic_percentage": "Marks (%)",
                    "attendance_percentage": "Att (%)",
                    "placement_status": "Status"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("🎉 No students currently flagged in the critical intervention category.")
