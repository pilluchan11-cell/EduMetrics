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
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_kpi, 
    render_section_header,
    render_footer
)
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ACCENT, COLOR_SECONDARY


def render(df: pd.DataFrame) -> None:
    """Renders the executive dashboard page."""
    render_hero("Executive Dashboard & Strategic KPIs")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the active filter criteria. Adjust the sidebar filters to view data.")
        return
        
    kpis = compute_executive_kpis(df)
    
    # Section 1: Academic & Cohort Health
    render_section_header(
        "Institutional Cohort Health & Compliance", 
        "Key operational indicators tracking cohort size, academic aggregates, and classroom attendance.",
        "🏛️"
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi(
            "Total Enrolled Cohort", 
            f"{kpis['total_students']:,}", 
            "Active Student Records", 
            COLOR_PRIMARY, 
            icon="👥",
            chip_text="Active Batch",
            chip_color="#EFF6FF"
        )
    with c2:
        render_kpi(
            "Overall Placement Rate", 
            f"{kpis['placement_rate']}%", 
            f"{kpis['placed_count']} Placed / {kpis['unplaced_count']} Seeking", 
            COLOR_SUCCESS, 
            icon="🎯",
            chip_text="Recruitment Rate",
            chip_color="#DCFCE7"
        )
    with c3:
        render_kpi(
            "Average Academic Marks", 
            f"{kpis['avg_academic']}%", 
            "Cohort Aggregate Score", 
            COLOR_SECONDARY, 
            icon="📚",
            chip_text="Aggregate",
            chip_color="#CCFBF1"
        )
    with c4:
        att_color = COLOR_ACCENT if kpis['avg_attendance'] >= 75 else "#EF4444"
        render_kpi(
            "Average Attendance", 
            f"{kpis['avg_attendance']}%", 
            "Threshold Cutoff: 75%", 
            att_color, 
            icon="⏰",
            chip_text="Compliance",
            chip_color="#FEF3C7" if kpis['avg_attendance'] >= 75 else "#FEE2E2"
        )
        
    # Section 2: Compensation & Placement Market Performance
    render_section_header(
        "Recruitment & Market Outcomes", 
        "Placement conversion statistics and compensation packages secured across recruiting partners.",
        "💼"
    )
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        render_kpi(
            "Offers Accepted", 
            f"{kpis['placed_count']}", 
            "Corporate Placements", 
            COLOR_SUCCESS, 
            icon="✅",
            chip_text="Confirmed",
            chip_color="#DCFCE7"
        )
    with c6:
        render_kpi(
            "Active In-Process", 
            f"{kpis['unplaced_count']}", 
            "Awaiting Offers / Drives", 
            "#64748B", 
            icon="⏳",
            chip_text="In Pipeline",
            chip_color="#F1F5F9"
        )
    with c7:
        render_kpi(
            "Average CTC Package", 
            f"₹{kpis['avg_salary']} LPA", 
            "Mean Placement Compensation", 
            COLOR_PRIMARY, 
            icon="💰",
            chip_text="Mean Package",
            chip_color="#EFF6FF"
        )
    with c8:
        render_kpi(
            "Highest Campus CTC", 
            f"₹{kpis['highest_salary']} LPA", 
            "Top Tier Corporate Offer", 
            COLOR_ACCENT, 
            icon="🏆",
            chip_text="Max Offer",
            chip_color="#FEF3C7"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Visual Analytics Row
    col_left, col_right = st.columns([5, 7])
    
    with col_left:
        fig_donut = plot_placement_donut(df)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_right:
        spec_df = compute_placement_by_specialization(df)
        fig_spec = plot_placement_by_specialization(spec_df)
        st.plotly_chart(fig_spec, use_container_width=True)
        
    # Full Width Academic Overview
    render_section_header(
        "Academic Achievement Distribution",
        "Statistical curve showing how academic scores are dispersed across the entire postgraduate cohort.",
        "📈"
    )
    fig_dist = plot_academic_distribution(df)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Strategic Executive Takeaways Callout
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px 26px; margin-top: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); border-left: 5px solid #2563EB;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <span style="font-size: 20px;">📋</span>
                <h4 style="margin: 0; color: #0F172A; font-size: 17px; font-weight: 700;">Executive Takeaways & Management Summary</h4>
            </div>
            <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px; line-height: 1.7;">
                <li>The active student cohort demonstrates an overall placement conversion of <strong>{kpis['placement_rate']}%</strong> with an average salary package of <strong>₹{kpis['avg_salary']} LPA</strong>.</li>
                <li>Batch average attendance is currently <strong>{kpis['avg_attendance']}%</strong>, tracking above the mandatory 75% institutional compliance requirement.</li>
                <li>There are <strong>{kpis['unplaced_count']} students</strong> currently in the career development pipeline who would benefit from targeted technical workshops and mentorship interventions.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    render_footer()
