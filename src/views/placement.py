"""
Placement Analytics View for EduMetrics.
In-depth analysis of placement rates, compensation packages, companies, and skill drivers.
"""

import streamlit as st
import pandas as pd
from src.metrics import (
    compute_executive_kpis,
    compute_placement_by_specialization,
    compute_company_placement_stats,
    compute_skill_placement_matrix
)
from src.visualizations import (
    plot_placement_by_specialization,
    plot_salary_distribution,
    plot_company_hires,
    plot_skills_placement_impact
)
from src.ui_components import render_hero, render_disclaimer, render_kpi
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ACCENT, COLOR_SECONDARY


def render(df: pd.DataFrame) -> None:
    """Renders the placement analytics dashboard page."""
    render_hero("Placement & Compensation Analytics")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the current filter criteria.")
        return
        
    kpis = compute_executive_kpis(df)
    
    # Placement KPI summary
    st.markdown('<div class="section-title">💼 Placement & Salary Benchmarks</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Overall Placement Rate", f"{kpis['placement_rate']}%", f"{kpis['placed_count']} of {kpis['total_students']} Students", COLOR_SUCCESS)
    with c2:
        render_kpi("Median CTC Offer", f"₹{kpis['median_salary']} LPA", "50th Percentile Compensation", COLOR_PRIMARY)
    with c3:
        render_kpi("Mean CTC Offer", f"₹{kpis['avg_salary']} LPA", "Average Placed Package", COLOR_SECONDARY)
    with c4:
        render_kpi("Highest Salary Offered", f"₹{kpis['highest_salary']} LPA", "Campus High Offer", COLOR_ACCENT)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 1: Specialization Placement Rates & Salary Distribution Boxplot
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">📊 Placement Rate by Specialization</div>', unsafe_allow_html=True)
        spec_df = compute_placement_by_specialization(df)
        fig_spec = plot_placement_by_specialization(spec_df)
        st.plotly_chart(fig_spec, use_container_width=True)
        
    with col2:
        st.markdown('<div class="section-title">💰 Salary Package Spread (LPA)</div>', unsafe_allow_html=True)
        fig_sal = plot_salary_distribution(df)
        st.plotly_chart(fig_sal, use_container_width=True)
        
    # Row 2: Top Recruiting Companies & Grade Band Breakdown
    st.markdown('<div class="section-title">🏢 Corporate Hiring Insights</div>', unsafe_allow_html=True)
    comp_df = compute_company_placement_stats(df)
    
    col_c1, col_c2 = st.columns([7, 5])
    with col_c1:
        fig_comp = plot_company_hires(comp_df)
        st.plotly_chart(fig_comp, use_container_width=True)
    with col_c2:
        st.write(" ")
        st.write(" ")
        st.dataframe(
            comp_df,
            use_container_width=True,
            hide_index=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 3: Skills & Certifications Impact
    st.markdown('<div class="section-title">🎯 Technical Skill & Placement Uplift</div>', unsafe_allow_html=True)
    st.caption("Investigating how proficiency levels in key tools relate to recruitment outcomes.")
    
    sk1, sk2, sk3 = st.columns(3)
    with sk1:
        fig_py = plot_skills_placement_impact(df, "python_proficiency", "Python")
        st.plotly_chart(fig_py, use_container_width=True)
    with sk2:
        fig_sql = plot_skills_placement_impact(df, "sql_proficiency", "SQL")
        st.plotly_chart(fig_sql, use_container_width=True)
    with sk3:
        fig_bi = plot_skills_placement_impact(df, "power_bi_proficiency", "Power BI")
        st.plotly_chart(fig_bi, use_container_width=True)
        
    # Placement by Internship Status
    st.markdown('<div class="section-title">🚀 Internship & Certification Correlation</div>', unsafe_allow_html=True)
    c_int, c_cert = st.columns(2)
    
    with c_int:
        intern_summary = df.groupby("internship_status").agg(
            Total=("student_id", "count"),
            Placed=("placement_status", lambda x: (x.str.lower() == "placed").sum())
        ).reset_index()
        intern_summary["Placement Rate (%)"] = (
            (intern_summary["Placed"] / intern_summary["Total"]) * 100.0
        ).round(1)
        
        st.markdown("**Placement Conversion by Internship Completion:**")
        st.dataframe(intern_summary.rename(columns={"internship_status": "Internship Status"}), hide_index=True, use_container_width=True)
        
    with c_cert:
        cert_summary = df.groupby("certifications_count").agg(
            Total=("student_id", "count"),
            Placed=("placement_status", lambda x: (x.str.lower() == "placed").sum())
        ).reset_index()
        cert_summary["Placement Rate (%)"] = (
            (cert_summary["Placed"] / cert_summary["Total"]) * 100.0
        ).round(1)
        
        st.markdown("**Placement Conversion by Number of Certifications:**")
        st.dataframe(cert_summary.rename(columns={"certifications_count": "Verified Certifications Count"}), hide_index=True, use_container_width=True)
