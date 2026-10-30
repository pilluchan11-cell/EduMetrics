"""
Institutional Strategic Recommendations View for EduMetrics.
Transparent, rule-based recommendations for academic, attendance, technical, and placement enhancements.
"""

import streamlit as st
import pandas as pd
from src.rules_engine import generate_cohort_recommendations
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_section_header,
    render_footer
)
from src.config import ATTENDANCE_CRITICAL_THRESHOLD


def render(df: pd.DataFrame) -> None:
    """Renders the recommendations dashboard page."""
    render_hero("Strategic Institutional Recommendations")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the active filter criteria. Adjust sidebar filters to view recommendations.")
        return
        
    st.markdown(
        """
        <div class="info-callout">
            <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 18px;">💡</span>
                <strong style="color: #1E40AF; font-size: 14.5px;">Explainable Heuristic Methodology for Educational Leaders:</strong>
            </div>
            <p style="margin: 0; color: #1E3A8A; font-size: 13px; line-height: 1.5;">
                These strategic recommendations are derived from deterministic business rules, compliance thresholds, 
                and empirical performance bands. They provide transparent, actionable interventions for department heads 
                and placement directors without relying on opaque black-box machine-learning predictions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Cohort-level automated recommendations
    render_section_header(
        "Institutional Priority Action Items",
        "Data-backed action alerts triggered by the current cohort's attendance, skill proficiencies, and placement outcomes.",
        "🏛️"
    )
    cohort_recs = generate_cohort_recommendations(df)
    
    if cohort_recs:
        for rec in cohort_recs:
            badge_color = "#2563EB" if rec["impact_type"] == "Placement Uplift" else ("#0D9488" if rec["impact_type"] == "Skill Readiness" else "#F59E0B")
            badge_bg = "#EFF6FF" if rec["impact_type"] == "Placement Uplift" else ("#CCFBF1" if rec["impact_type"] == "Skill Readiness" else "#FEF3C7")
            
            st.markdown(
                f"""
                <div class="recommendation-card">
                    <div class="recommendation-header">
                        <h4 style="margin: 0; color: #0F172A; font-size: 15.5px; font-weight: 700; word-break: break-word;">{rec['area']}</h4>
                        <span style="background: {badge_bg}; color: {badge_color}; font-weight: 700; font-size: 11.5px; padding: 3px 10px; border-radius: 6px; white-space: nowrap;">
                            {rec['impact_type'].upper()}
                        </span>
                    </div>
                    <p style="color: #64748B; font-size: 13px; margin: 0 0 10px 0; word-break: break-word;"><strong>Observed Signal:</strong> {rec['metric']}</p>
                    <div class="recommendation-action-box" style="border-left: 4px solid {badge_color};">
                        <strong>Recommended Strategic Action:</strong> {rec['recommendation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("🎉 Cohort metrics are operating comfortably within optimal institutional parameters across all monitored dimensions.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # The 4 Strategic Pillars
    render_section_header(
        "The 4 Pillars of Institutional Excellence",
        "Strategic action roadmaps for academic deans, program managers, and career development directors.",
        "🎯"
    )
    
    t1, t2, t3, t4 = st.tabs([
        "📚 Academic Quality & Support", 
        "⏰ Attendance & Discipline", 
        "💻 Technical Tool Mastery", 
        "💼 Campus Placement Conversion"
    ])
    
    with t1:
        st.markdown(
            r"""
            ### 📚 Academic Quality & Peer Mentorship Framework
            * **Early Warning Grade Audits:** Establish mid-semester grade checkpoints. Students with $< 55\%$ aggregate marks are automatically paired with distinction scholars for weekly guided tutorials.
            * **Case-Study Assessment Models:** Modernize examinations by integrating Harvard Business Review and live corporate case studies to evaluate strategic problem-solving.
            * **Remedial Quantitative Foundations:** Offer targeted refresher workshops in business mathematics, statistics, and financial accounting prior to major examinations.
            """
        )
        
    with t2:
        st.markdown(
            f"""
            ### ⏰ Attendance Compliance & Student Welfare Protocol (Benchmark: {ATTENDANCE_CRITICAL_THRESHOLD}%)
            * **Predictive Attendance Alerting:** Implement early automated alerts at the 80% mark, providing students with a 5% safety margin before crossing the mandatory 75% cutoff.
            * **Faculty Advisory Check-Ins:** Mandate 1-on-1 empathetic counseling for students falling below 75% to identify and resolve transportation, health, or personal challenges.
            * **Active Learning Formats:** Boost voluntary attendance by adopting case debriefs, simulation games, and live business analytics lab exercises in place of passive lectures.
            """
        )
        
    with t3:
        st.markdown(
            """
            ### 💻 Applied Technical Skills & Analytics Tool Mastery
            * **SQL Querying Mastery:** Ensure 100% of graduating business students achieve at least Intermediate SQL capability (joins, window functions, CTEs) verified through live coding assessments.
            * **Python Analytics Sprints:** Host weekend bootcamp sprints focusing on Pandas, NumPy, and data wrangling for real-world business datasets.
            * **Power BI & Executive Dashboarding:** Require students to publish interactive portfolio dashboards solving commercial business problems, evaluated by industry alumni.
            """
        )
        
    with t4:
        st.markdown(
            """
            ### 💼 Placement Conversion & Corporate Partner Alignment
            * **Mandatory Summer Internship Verification:** Internships correlate strongly with campus recruitment offers; students lacking corporate experience should be routed to alumni-sponsored live capstones.
            * **Simulated Corporate Recruitment Drives:** Conduct mock aptitude screenings, group discussions, and technical interview simulations with corporate talent acquisition leaders.
            * **Industry Credential Sponsorship:** Subsidize recognized professional certifications in financial modeling, cloud analytics, or supply chain operations to elevate candidate resumes.
            """
        )
        
    render_footer()
