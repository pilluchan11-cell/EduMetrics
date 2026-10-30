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
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_kpi, 
    render_section_header,
    render_footer
)
from src.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_ACCENT, COLOR_SECONDARY


def render(df: pd.DataFrame) -> None:
    """Renders the placement analytics dashboard page."""
    render_hero("Placement & Compensation Analytics")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the active filter criteria. Adjust the sidebar filters to view data.")
        return
        
    kpis = compute_executive_kpis(df)
    
    # Section 1: Placement & Compensation KPIs
    render_section_header(
        "Recruitment Conversion & Salary Benchmarks",
        "Key market compensation figures evaluating batch competitiveness and offer distribution.",
        "💼"
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi(
            "Overall Placement Conversion", 
            f"{kpis['placement_rate']}%", 
            f"{kpis['placed_count']} of {kpis['total_students']} Students Placed", 
            COLOR_SUCCESS, 
            icon="🎯",
            chip_text="Placement %",
            chip_color="#DCFCE7"
        )
    with c2:
        render_kpi(
            "Median CTC Package", 
            f"₹{kpis['median_salary']} LPA", 
            "50th Percentile Compensation", 
            COLOR_PRIMARY, 
            icon="📊",
            chip_text="Median Offer",
            chip_color="#EFF6FF"
        )
    with c3:
        render_kpi(
            "Average CTC Package", 
            f"₹{kpis['avg_salary']} LPA", 
            "Mean Placed Compensation", 
            COLOR_SECONDARY, 
            icon="💵",
            chip_text="Mean Package",
            chip_color="#CCFBF1"
        )
    with c4:
        render_kpi(
            "Top Campus Offer", 
            f"₹{kpis['highest_salary']} LPA", 
            "Highest Verified Corporate Offer", 
            COLOR_ACCENT, 
            icon="🏆",
            chip_text="Peak CTC",
            chip_color="#FEF3C7"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 2: Specialization Rates & Salary Distribution Boxplot
    col1, col2 = st.columns(2)
    with col1:
        spec_df = compute_placement_by_specialization(df)
        fig_spec = plot_placement_by_specialization(spec_df)
        st.plotly_chart(fig_spec, use_container_width=True)
        
    with col2:
        fig_sal = plot_salary_distribution(df)
        st.plotly_chart(fig_sal, use_container_width=True)
        
    # Section 3: Corporate Hiring Insights
    render_section_header(
        "Corporate Recruiting Partner Intelligence",
        "Analysis of hiring partners by placement volume, minimum package, and average offer package.",
        "🏢"
    )
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
    
    # Section 4: Skills & Certifications Impact
    render_section_header(
        "Technical Competencies & Placement Lift",
        "Investigating how student proficiency across Python, SQL, and Power BI correlates with placement rates.",
        "💻"
    )
    
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
        
    # Section 5: Experiential Learning Uplift
    render_section_header(
        "Experiential Learning & Industry Credentials",
        "Measuring placement premiums associated with summer internship completion and verified certifications.",
        "🚀"
    )
    c_int, c_cert = st.columns(2)
    
    with c_int:
        intern_summary = df.groupby("internship_status").agg(
            Total=("student_id", "count"),
            Placed=("placement_status", lambda x: (x.str.lower() == "placed").sum())
        ).reset_index()
        intern_summary["Placement Rate (%)"] = (
            (intern_summary["Placed"] / intern_summary["Total"]) * 100.0
        ).round(1)
        
        st.markdown("**Placement Conversion by Summer Internship Completion:**")
        st.dataframe(
            intern_summary.rename(columns={
                "internship_status": "Summer Internship Status",
                "Total": "Enrolled Students",
                "Placed": "Placed Students"
            }), 
            hide_index=True, 
            use_container_width=True
        )
        
    with c_cert:
        cert_summary = df.groupby("certifications_count").agg(
            Total=("student_id", "count"),
            Placed=("placement_status", lambda x: (x.str.lower() == "placed").sum())
        ).reset_index()
        cert_summary["Placement Rate (%)"] = (
            (cert_summary["Placed"] / cert_summary["Total"]) * 100.0
        ).round(1)
        
        st.markdown("**Placement Conversion by Count of Industry Certifications:**")
        st.dataframe(
            cert_summary.rename(columns={
                "certifications_count": "Verified Certifications Count",
                "Total": "Enrolled Students",
                "Placed": "Placed Students"
            }), 
            hide_index=True, 
            use_container_width=True
        )
        
    render_footer()
