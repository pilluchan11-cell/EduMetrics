"""
Statistical Analysis View for EduMetrics.
Pairwise correlations, bivariate scatter analyses, distribution skewness, and statistical summaries.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.metrics import compute_correlation_matrix
from src.visualizations import plot_correlation_heatmap
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_section_header,
    render_footer
)
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS


def render(df: pd.DataFrame) -> None:
    """Renders the statistical analysis page."""
    render_hero("Statistical & Correlation Analysis")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the active filter criteria. Adjust sidebar filters to view data.")
        return
        
    render_section_header(
        "Pairwise Correlation Analysis",
        "Statistical matrix evaluating linear associations between attendance, academic marks, technical score, and CTC.",
        "📊"
    )
    corr_df = compute_correlation_matrix(df)
    
    col_heat, col_corr_text = st.columns([7, 5])
    with col_heat:
        fig_heat = plot_correlation_heatmap(corr_df)
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_corr_text:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <h4 style="margin: 0 0 12px 0; color: #0F172A; font-size: 16px; font-weight: 700;">Executive Statistical Takeaways</h4>
            """,
            unsafe_allow_html=True
        )
        if "academic_percentage" in corr_df and "attendance_percentage" in corr_df:
            r_att = corr_df.loc["academic_percentage", "attendance_percentage"]
            st.markdown(f"• **Academic Score vs. Attendance:** $r = {r_att:+.3f}$<br><span style='font-size:12px; color:#64748B;'>Moderate positive association; consistent classroom presence aligns with higher exam scores.</span>", unsafe_allow_html=True)
            
        if "technical_score_10" in corr_df and "salary_lpa" in corr_df:
            r_tech_sal = corr_df.loc["technical_score_10", "salary_lpa"]
            st.markdown(f"<br>• **Tech Skill Index vs. Salary Package:** $r = {r_tech_sal:+.3f}$<br><span style='font-size:12px; color:#64748B;'>Positive association; technical proficiency in SQL, Python, and Power BI commands premium offers.</span>", unsafe_allow_html=True)
            
        if "certifications_count" in corr_df and "salary_lpa" in corr_df:
            r_cert_sal = corr_df.loc["certifications_count", "salary_lpa"]
            st.markdown(f"<br>• **Certifications vs. Salary:** $r = {r_cert_sal:+.3f}$<br><span style='font-size:12px; color:#64748B;'>Incremental credential verification correlates with higher compensation shortlisting.</span>", unsafe_allow_html=True)
            
        st.markdown(
            """
                <hr style="margin: 16px 0; border: none; border-top: 1px solid #E2E8F0;">
                <div style="font-size: 11.5px; color: #64748B; line-height: 1.4;">
                    <em>Methodology Note:</em> Pearson correlation measures mathematical linear association within this research benchmark and does not establish direct causality.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bivariate Scatter Analysis with Pure NumPy Trendlines
    render_section_header(
        "Bivariate Regressions & Trendline Modeling",
        "Ordinary Least Squares (OLS) regression models highlighting statistical patterns across cohort variables.",
        "📈"
    )
    
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("**Attendance Rate vs. Academic Aggregate Marks:**")
        fig_scatter1 = px.scatter(
            df,
            x="attendance_percentage",
            y="academic_percentage",
            color="placement_status",
            color_discrete_map={"Placed": COLOR_SUCCESS, "Unplaced": "#94A3B8"},
            labels={"attendance_percentage": "Attendance Rate (%)", "academic_percentage": "Academic Aggregate (%)"}
        )
        fig_scatter1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig_scatter1.update_traces(marker=dict(size=6.5, opacity=0.75))
        
        # Add regression line via NumPy
        valid_att = df.dropna(subset=["attendance_percentage", "academic_percentage"])
        if len(valid_att) > 2:
            x_vals = valid_att["attendance_percentage"].values
            y_vals = valid_att["academic_percentage"].values
            slope, intercept = np.polyfit(x_vals, y_vals, 1)
            x_line = np.linspace(x_vals.min(), x_vals.max(), 30)
            y_line = slope * x_line + intercept
            fig_scatter1.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                name=f"OLS Trend (Slope: {slope:+.2f})",
                line=dict(color="#1E3A8A", width=2.5, dash="dash")
            ))
            
        st.plotly_chart(fig_scatter1, use_container_width=True)
        
    with sc2:
        st.markdown("**Technical Skill Score vs. Placed Package (₹ LPA):**")
        placed_df = df[df["placement_status"].str.lower() == "placed"].dropna(subset=["salary_lpa", "technical_score_10"])
        if len(placed_df) > 3:
            fig_scatter2 = px.scatter(
                placed_df,
                x="technical_score_10",
                y="salary_lpa",
                color="specialization",
                labels={"technical_score_10": "Technical Skill Index (10)", "salary_lpa": "Package (₹ LPA)"}
            )
            fig_scatter2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig_scatter2.update_traces(marker=dict(size=6.5, opacity=0.8))
            
            # Add regression line via NumPy
            x_t = placed_df["technical_score_10"].values
            y_t = placed_df["salary_lpa"].values
            slope_t, intercept_t = np.polyfit(x_t, y_t, 1)
            x_t_line = np.linspace(x_t.min(), x_t.max(), 30)
            y_t_line = slope_t * x_t_line + intercept_t
            fig_scatter2.add_trace(go.Scatter(
                x=x_t_line,
                y=y_t_line,
                mode="lines",
                name=f"OLS Trend (Slope: ₹{slope_t:+.2f}LPA/pt)",
                line=dict(color="#0D9488", width=2.5, dash="dot")
            ))
            
            st.plotly_chart(fig_scatter2, use_container_width=True)
        else:
            st.info("Insufficient placed data points in this filtered view for trendline calculation.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistical Distribution Summary Table
    render_section_header(
        "Complete Parametric & Percentile Distribution Summary",
        "Detailed quantiles (P10 through P90), standard deviations, and quartile ranges across numerical attributes.",
        "📑"
    )
    num_cols = ["academic_percentage", "attendance_percentage", "technical_score_10", "certifications_count"]
    if "salary_lpa" in df.columns:
        num_cols.append("salary_lpa")
        
    desc_df = df[num_cols].describe(percentiles=[0.10, 0.25, 0.50, 0.75, 0.90]).T
    desc_df = desc_df.rename(columns={
        "count": "Sample Count",
        "mean": "Arithmetic Mean",
        "std": "Standard Deviation",
        "min": "Minimum",
        "10%": "10th Percentile (P10)",
        "25%": "Lower Quartile (P25)",
        "50%": "Median (P50)",
        "75%": "Upper Quartile (P75)",
        "90%": "90th Percentile (P90)",
        "max": "Maximum"
    }).round(2)
    
    st.dataframe(desc_df, use_container_width=True)
    
    render_footer()
