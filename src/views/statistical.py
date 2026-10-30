"""
Statistical Analysis View for EduMetrics.
Pairwise correlations, bivariate scatter analyses, distribution skewness, and statistical summaries.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.metrics import compute_correlation_matrix
from src.visualizations import plot_correlation_heatmap
from src.ui_components import render_hero, render_disclaimer, render_kpi
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS


def render(df: pd.DataFrame) -> None:
    """Renders the statistical analysis page."""
    render_hero("Statistical & Correlation Analysis")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the current filter criteria.")
        return
        
    st.markdown('<div class="section-title">📊 Correlation Matrix (Pairwise Statistical Associations)</div>', unsafe_allow_html=True)
    corr_df = compute_correlation_matrix(df)
    
    col_heat, col_corr_text = st.columns([7, 5])
    with col_heat:
        fig_heat = plot_correlation_heatmap(corr_df)
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_corr_text:
        st.markdown("**Key Correlation Observations:**")
        if "academic_percentage" in corr_df and "attendance_percentage" in corr_df:
            r_att = corr_df.loc["academic_percentage", "attendance_percentage"]
            st.markdown(f"• **Academic Score vs. Attendance:** $r = {r_att:+.3f}$ (Positive moderate association; higher classroom attendance aligns with superior exam marks).")
            
        if "technical_score_10" in corr_df and "salary_lpa" in corr_df:
            r_tech_sal = corr_df.loc["technical_score_10", "salary_lpa"]
            st.markdown(f"• **Tech Competence vs. Salary Package:** $r = {r_tech_sal:+.3f}$ (Positive association; elevated software proficiency corresponds with premium compensation offers).")
            
        if "certifications_count" in corr_df and "salary_lpa" in corr_df:
            r_cert_sal = corr_df.loc["certifications_count", "salary_lpa"]
            st.markdown(f"• **Certifications vs. Salary:** $r = {r_cert_sal:+.3f}$ (Certifications provide marginal positive lift on final salary packages).")
            
        st.info("💡 Note: Statistical correlations demonstrate mathematical association within this synthetic benchmark and do not prove direct causation.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bivariate Scatter Analysis
    st.markdown('<div class="section-title">📈 Bivariate Scatter & Trendline Explorations</div>', unsafe_allow_html=True)
    
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("**Attendance vs. Academic Percentage (with OLS Trendline)**")
        fig_scatter1 = px.scatter(
            df,
            x="attendance_percentage",
            y="academic_percentage",
            color="placement_status",
            trendline="ols",
            color_discrete_map={"Placed": COLOR_SUCCESS, "Unplaced": "#94A3B8"},
            labels={"attendance_percentage": "Attendance %", "academic_percentage": "Academic %"}
        )
        fig_scatter1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_scatter1, use_container_width=True)
        
    with sc2:
        st.markdown("**Technical Score vs. Salary Package (Placed Students)**")
        placed_df = df[df["placement_status"].str.lower() == "placed"].dropna(subset=["salary_lpa"])
        if len(placed_df) > 5:
            fig_scatter2 = px.scatter(
                placed_df,
                x="technical_score_10",
                y="salary_lpa",
                color="specialization",
                trendline="ols",
                labels={"technical_score_10": "Technical Score (out of 10)", "salary_lpa": "Salary (LPA)"}
            )
            fig_scatter2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_scatter2, use_container_width=True)
        else:
            st.info("Insufficient placed data points for trendline analysis.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistical Distribution Summary Table
    st.markdown('<div class="section-title">📑 Parametric & Non-Parametric Summary Statistics</div>', unsafe_allow_html=True)
    num_cols = ["academic_percentage", "attendance_percentage", "technical_score_10", "certifications_count"]
    if "salary_lpa" in df.columns:
        num_cols.append("salary_lpa")
        
    desc_df = df[num_cols].describe(percentiles=[0.10, 0.25, 0.50, 0.75, 0.90]).T
    desc_df = desc_df.rename(columns={
        "count": "Count",
        "mean": "Mean",
        "std": "Std Dev",
        "min": "Min",
        "10%": "P10",
        "25%": "P25 (Q1)",
        "50%": "Median (Q2)",
        "75%": "P75 (Q3)",
        "90%": "P90",
        "max": "Max"
    }).round(2)
    
    st.dataframe(desc_df, use_container_width=True)
