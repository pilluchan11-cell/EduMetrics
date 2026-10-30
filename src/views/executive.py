"""
Executive Dashboard View for EduMetrics.
Displays institutional high-level KPIs, placement funnel, and strategic overviews.
"""

import streamlit as st
import pandas as pd
from src.metrics import (
    compute_executive_kpis,
    compute_placement_by_specialization
)
from src.visualizations import (
    plot_placement_donut,
    plot_placement_by_specialization,
    plot_academic_distribution
)
from src.ui_components import render_hero, render_disclaimer, render_kpi
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ACCENT, COLOR_SECONDARY


def render(df: pd.DataFrame) -> None:
    """Renders the executive dashboard page."""
    render_hero("Executive Overview & Institutional KPIs")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the current filter criteria.")
        return
        
    kpis = compute_executive_kpis(df)
    
    # KPI Row 1: Core Institutional Metrics
    st.markdown('<div class="section-title">📌 Key Performance Indicators</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Total Enrolled Cohort", f"{kpis['total_students']:,}", "Active Student Profiles", COLOR_PRIMARY)
    with c2:
        render_kpi("Overall Placement Rate", f"{kpis['placement_rate']}%", f"{kpis['placed_count']} Placed / {kpis['unplaced_count']} Unplaced", COLOR_SUCCESS)
    with c3:
        render_kpi("Average Academic Score", f"{kpis['avg_academic']}%", "Aggregate Across Semesters", COLOR_SECONDARY)
    with c4:
        render_kpi("Average Attendance", f"{kpis['avg_attendance']}%", "Threshold Benchmark: 75%", COLOR_ACCENT)
        
    # KPI Row 2: Compensation & Placement Metrics
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        render_kpi("Placed Students", f"{kpis['placed_count']}", "Offers Accepted", COLOR_SUCCESS)
    with c6:
        render_kpi("Unplaced / In-Process", f"{kpis['unplaced_count']}", "Seeking Placement", "#64748B")
    with c7:
        render_kpi("Average Salary (Placed)", f"₹{kpis['avg_salary']} LPA", "Mean Compensation", COLOR_PRIMARY)
    with c8:
        render_kpi("Highest Salary Package", f"₹{kpis['highest_salary']} LPA", "Top Corporate Offer", COLOR_ACCENT)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Visual Analytics Row
    col_left, col_right = st.columns([5, 7])
    
    with col_left:
        st.markdown('<div class="section-title">🎯 Placement Conversion</div>', unsafe_allow_html=True)
        fig_donut = plot_placement_donut(df)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_right:
        st.markdown('<div class="section-title">📊 Placement Rate by Specialization</div>', unsafe_allow_html=True)
        spec_df = compute_placement_by_specialization(df)
        fig_spec = plot_placement_by_specialization(spec_df)
        st.plotly_chart(fig_spec, use_container_width=True)
        
    # Full Width Academic Overview
    st.markdown('<div class="section-title">📈 Batch Academic Score Distribution</div>', unsafe_allow_html=True)
    fig_dist = plot_academic_distribution(df)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Executive Summary Card
    st.markdown(
        f"""
        <div style="background: #F1F5F9; border-radius: 10px; padding: 18px 24px; margin-top: 15px; border-left: 4px solid #2563EB;">
            <h4 style="margin: 0 0 8px 0; color: #1E3A8A;">Strategic Executive Takeaways</h4>
            <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px; line-height: 1.6;">
                <li>The current active cohort exhibits an overall placement rate of <strong>{kpis['placement_rate']}%</strong> with an average package of <strong>₹{kpis['avg_salary']} LPA</strong>.</li>
                <li>Batch attendance stands at <strong>{kpis['avg_attendance']}%</strong>, comfortably above the institution's 75% critical cutoff.</li>
                <li><strong>{kpis['unplaced_count']} students</strong> currently require targeted intervention in resume refinement, technical coding bootcamps, and mock interviews.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
