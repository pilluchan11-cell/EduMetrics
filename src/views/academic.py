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
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_kpi, 
    render_section_header,
    render_footer
)
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_ACCENT, COLOR_SECONDARY


def render(df: pd.DataFrame) -> None:
    """Renders the academic performance analytics page."""
    render_hero("Academic Performance Analytics")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the active filter criteria. Adjust the sidebar filters to view data.")
        return
        
    stats = compute_academic_summary(df)
    
    # Section 1: Statistical Summary
    render_section_header(
        "Parametric & Non-Parametric Academic Summary",
        "Statistical spread of marks across the cohort, measuring central tendency, dispersion, and range.",
        "📊"
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi(
            "Cohort Mean Score", 
            f"{stats['mean']}%", 
            f"Median: {stats['median']}%", 
            COLOR_PRIMARY, 
            icon="📐",
            chip_text="Central Value",
            chip_color="#EFF6FF"
        )
    with c2:
        render_kpi(
            "Standard Deviation", 
            f"{stats['std']}%", 
            "Score Dispersion Metric", 
            COLOR_ACCENT, 
            icon="⚡",
            chip_text="Variation",
            chip_color="#FEF3C7"
        )
    with c3:
        render_kpi(
            "Interquartile Range (IQR)", 
            f"{stats['iqr']}%", 
            f"Q25: {stats['q25']}% | Q75: {stats['q75']}%", 
            COLOR_SUCCESS, 
            icon="📏",
            chip_text="Middle 50%",
            chip_color="#DCFCE7"
        )
    with c4:
        render_kpi(
            "Total Score Spread", 
            f"{stats['min']}% - {stats['max']}%", 
            "Min to Max Range", 
            "#64748B", 
            icon="📊",
            chip_text="Observed Range",
            chip_color="#F1F5F9"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 2: Distributions (Grade Bands & Semester Comparison)
    col1, col2 = st.columns(2)
    with col1:
        grades_df = compute_grade_distribution(df)
        fig_grades = plot_grade_distribution(grades_df)
        st.plotly_chart(fig_grades, use_container_width=True)
        
    with col2:
        fig_sem = plot_semester_comparison(df)
        st.plotly_chart(fig_sem, use_container_width=True)
        
    # Section 3: Attendance vs. Marks
    render_section_header(
        "Classroom Attendance vs. Academic Achievement",
        "Correlating attendance percentage with examination marks, highlighting the 75% institutional compliance cutoff.",
        "🎯"
    )
    fig_att = plot_attendance_vs_academic(df)
    st.plotly_chart(fig_att, use_container_width=True)
    
    # Section 4: Specialization Breakdown Table
    render_section_header(
        "Specialization-Level Academic & Technical Benchmark",
        "Department-level aggregation comparing aggregate marks, attendance, and technical indices across majors.",
        "🏛️"
    )
    spec_perf = compute_specialization_performance(df)
    
    formatted_spec_df = spec_perf.rename(columns={
        "specialization": "Specialization",
        "Total_Students": "Enrolled",
        "Avg_Academic": "Mean Marks (%)",
        "Avg_Attendance": "Mean Attendance (%)",
        "Avg_Tech_Index": "Tech Index (10)",
        "Placed_Count": "Placed",
        "Placement_Rate": "Placement Rate (%)"
    })
    
    st.dataframe(
        formatted_spec_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 5: Cohort Segmentation
    render_section_header(
        "Student Cohort Segmentation",
        "Recognizing top academic performers and identifying students needing faculty advisory intervention.",
        "👥"
    )
    cohorts = get_top_and_support_students(df, top_n=10)
    
    col_top, col_supp = st.columns(2)
    with col_top:
        st.markdown(
            """
            <div style="font-weight: 700; font-size: 15px; color: #166534; margin-bottom: 8px;">
                🌟 Top Performing Students (Distinction Tier)
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.dataframe(
            cohorts["top"].rename(columns={
                "student_id": "ID",
                "student_name": "Full Name",
                "specialization": "Major",
                "academic_percentage": "Marks (%)",
                "attendance_percentage": "Attendance (%)",
                "placement_status": "Recruitment Status"
            }),
            use_container_width=True,
            hide_index=True
        )
        
    with col_supp:
        st.markdown(
            """
            <div style="font-weight: 700; font-size: 15px; color: #991B1B; margin-bottom: 8px;">
                ⚠️ Students Requiring Academic Support / Intervention
            </div>
            """, 
            unsafe_allow_html=True
        )
        if len(cohorts["support"]) > 0:
            st.dataframe(
                cohorts["support"].rename(columns={
                    "student_id": "ID",
                    "student_name": "Full Name",
                    "specialization": "Major",
                    "academic_percentage": "Marks (%)",
                    "attendance_percentage": "Attendance (%)",
                    "placement_status": "Recruitment Status"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("🎉 No students currently flagged below the academic or attendance support thresholds.")
            
    render_footer()
