"""
Institutional Strategic Recommendations View for EduMetrics.
Transparent, rule-based recommendations for academic, attendance, technical, and placement enhancements.
"""

import streamlit as st
import pandas as pd
from src.rules_engine import generate_cohort_recommendations
from src.ui_components import render_hero, render_disclaimer
from src.config import ATTENDANCE_CRITICAL_THRESHOLD


def render(df: pd.DataFrame) -> None:
    """Renders the recommendations dashboard page."""
    render_hero("Explainable Strategic Recommendations")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the current filter criteria.")
        return
        
    st.markdown(
        """
        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;">
            <p style="margin: 0; color: #1E40AF; font-size: 13.5px;">
                <strong>💡 Explainable Heuristic Methodology:</strong> These institutional recommendations are derived 
                from deterministic business rules and historical data associations. They prioritize actionable student 
                welfare and career readiness without relying on opaque machine-learning predictions or claiming unverified causality.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Cohort-level automated recommendations
    st.markdown('<div class="section-title">🏛️ Institutional Action Priorities</div>', unsafe_allow_html=True)
    cohort_recs = generate_cohort_recommendations(df)
    
    if cohort_recs:
        for rec in cohort_recs:
            badge_color = "#2563EB" if rec["impact_type"] == "Placement Uplift" else "#0D9488"
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 1px 4px rgba(0,0,0,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #0F172A; font-size: 16px;">{rec['area']}</h4>
                        <span style="background: #F1F5F9; color: {badge_color}; font-weight: 600; font-size: 12px; padding: 4px 10px; border-radius: 6px;">
                            {rec['impact_type']}
                        </span>
                    </div>
                    <p style="color: #64748B; font-size: 13px; margin: 0 0 10px 0;"><strong>Observed Signal:</strong> {rec['metric']}</p>
                    <div style="background: #F8FAFC; border-left: 4px solid {badge_color}; padding: 10px 14px; border-radius: 4px; font-size: 13.5px; color: #1E293B;">
                        <strong>Recommended Strategic Action:</strong> {rec['recommendation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("🎉 Cohort metrics are operating within optimal institutional parameters across all monitored dimensions.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # The 4 Strategic Pillars
    st.markdown('<div class="section-title">🎯 The 4 Institutional Strategic Pillars</div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs([
        "📚 Academic Improvement", 
        "⏰ Attendance Interventions", 
        "💻 Technical Skill Upskilling", 
        "💼 Campus Placement Preparation"
    ])
    
    with t1:
        st.markdown("### 📚 Academic Quality & Peer Support Framework")
        st.markdown(
            r"""
            * **Early Warning Indicator:** Establish mid-semester grade checkpoints. Students with $< 55\%$ aggregate should receive peer tutoring from top-quartile distinction students.
            * **Applied Business Projects:** Integrate industry case studies into exam assessments to elevate theoretical comprehension into practical business acumen.
            * **Elective Advisory:** Guide students struggling in quantitative subjects toward structured remedial foundational courses.
            """
        )
        
    with t2:
        st.markdown(f"### ⏰ Attendance Enforcement & Welfare Protocol (Benchmark: {ATTENDANCE_CRITICAL_THRESHOLD}%)")
        st.markdown(
            """
            * **Proactive Automated Alerting:** Trigger SMS/Email notifications at the 80% mark, giving students a 5% buffer before hitting the mandatory 75% cutoff.
            * **Faculty Mentorship Check-ins:** For students under 75%, arrange empathetic 1-on-1 counseling to diagnose medical, personal, or transportation obstacles.
            * **Interactive Lecture Formats:** Incorporate live polls, interactive discussions, and hands-on lab exercises to boost classroom attendance naturally.
            """
        )
        
    with t3:
        st.markdown("### 💻 Applied Technical Skills & Tool Mastery")
        st.markdown(
            """
            * **SQL Relational Database Bootcamps:** Ensure 100% of graduating business students achieve at least Intermediate SQL querying capability (joins, window functions, aggregations).
            * **Python Analytics Immersion:** Offer weekend workshop sprints on Pandas, NumPy, and business analytics libraries.
            * **BI & Dashboarding Showcases:** Host campus business intelligence competitions requiring students to deliver interactive Power BI dashboards to industry alumni judges.
            """
        )
        
    with t4:
        st.markdown("### 💼 Placement Conversion & Career Readiness")
        st.markdown(
            """
            * **Mandatory Summer Internship Verification:** Internships correlate strongly with campus hiring; students without internships should be connected with corporate partner live-projects.
            * **Mock Technical & HR Interview Rounds:** Partner with alumni to conduct simulated recruitment drives complete with aptitude testing and behavioral interview coaching.
            * **Industry Credential Sponsorship:** Subsidize exam fees for recognized professional certificates in financial modeling, cloud data, or supply chain.
            """
        )
