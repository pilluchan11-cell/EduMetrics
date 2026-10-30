"""
Statistical Analysis View for EduMetrics.
Pairwise correlations with p-values, hypothesis tests, logistic regression, and MBA statistical methodology.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.metrics import (
    compute_correlation_matrix,
    compute_correlation_with_significance,
    compute_group_comparisons,
    compute_placement_logistic_regression
)
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
    render_hero("Statistical & Econometric Analysis")
    render_disclaimer()
    
    if len(df) == 0:
        st.warning("⚠️ No student records match the active filter criteria. Adjust sidebar filters to view data.")
        return
        
    # Section 1: Pairwise Correlation with Statistical Significance
    render_section_header(
        "Pairwise Correlation Matrix & Hypothesis Significance (p-values)",
        "Measuring linear associations and testing null hypotheses (H0: r = 0) with two-tailed p-values.",
        "📊"
    )
    corr_df = compute_correlation_matrix(df)
    
    col_heat, col_corr_table = st.columns([6, 6])
    with col_heat:
        fig_heat = plot_correlation_heatmap(corr_df)
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_corr_table:
        st.markdown("**Bivariate Significance Tests (Pearson r):**")
        sig_list = compute_correlation_with_significance(df)
        if sig_list:
            st.dataframe(pd.DataFrame(sig_list), hide_index=True, use_container_width=True)
        st.caption("Significance levels: *** (p < 0.001), ** (p < 0.01), * (p < 0.05), ns (not significant).")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 2: Group Comparisons & Hypothesis Testing (Placed vs Unplaced)
    render_section_header(
        "Cohort Group Comparisons & Inferential Hypothesis Tests",
        "Two-sample Welch's t-tests and Cohen's d effect sizes comparing placed vs unplaced student profiles.",
        "⚖️"
    )
    group_comp = compute_group_comparisons(df)
    if len(group_comp["placed_vs_unplaced"]) > 0:
        st.dataframe(
            group_comp["placed_vs_unplaced"],
            hide_index=True,
            use_container_width=True
        )
        
    if group_comp.get("anova_specializations"):
        anova = group_comp["anova_specializations"]
        sig_text = "statistically significant (p < 0.05)" if anova["is_significant"] else "not statistically significant"
        st.info(
            f"🏛️ **One-Way ANOVA Across Specializations (Academic Marks):** "
            f"F-Statistic = **{anova['f_statistic']}**, p-value = **{anova['p_value']}** ({sig_text}). "
            f"Indicates whether academic score differences between majors are attributable to systematic department variation or random sampling."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 3: Bivariate Scatter Analysis with Trendlines
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
        
        # Add regression line via pure NumPy
        valid_att = df.dropna(subset=["attendance_percentage", "academic_percentage"])
        if len(valid_att) > 2 and valid_att["attendance_percentage"].min() != valid_att["attendance_percentage"].max():
            try:
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
            except Exception:
                pass
            
        st.plotly_chart(fig_scatter1, use_container_width=True)
        
    with sc2:
        st.markdown("**Technical Skill Score vs. Placed Package (₹ LPA):**")
        placed_df = df[df["placement_status"].str.lower() == "placed"].dropna(subset=["salary_lpa", "technical_score_10"])
        if len(placed_df) > 3 and placed_df["technical_score_10"].min() != placed_df["technical_score_10"].max():
            fig_scatter2 = px.scatter(
                placed_df,
                x="technical_score_10",
                y="salary_lpa",
                color="specialization",
                labels={"technical_score_10": "Technical Skill Index (10)", "salary_lpa": "Package (₹ LPA)"}
            )
            fig_scatter2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig_scatter2.update_traces(marker=dict(size=6.5, opacity=0.8))
            
            # Add regression line via pure NumPy
            try:
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
            except Exception:
                pass
            
            st.plotly_chart(fig_scatter2, use_container_width=True)
        else:
            st.info("Insufficient placed data points in this filtered view for trendline calculation.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 4: Multivariate Logistic Regression for Placement Outcomes
    render_section_header(
        "Multivariate Econometric Demonstration: Logistic Regression",
        "Quantifying the marginal contribution of academics, attendance, and skills to placement odds.",
        "🤖"
    )
    
    logit_res = compute_placement_logistic_regression(df)
    if logit_res:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: clamp(10px, 2vw, 14px) clamp(12px, 2.5vw, 18px); margin-bottom: 14px;">
                <div class="stat-badge-row">
                    <div>Model Classification Accuracy: <strong style="color: #2563EB;">{logit_res['accuracy']}%</strong></div>
                    <div>ROC-AUC Score: <strong style="color: #0D9488;">{logit_res['roc_auc']}</strong></div>
                    <div>Sample Cohort Evaluated: <strong>{logit_res['sample_size']} Students</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.dataframe(logit_res["coefficients_table"], hide_index=True, use_container_width=True)
        st.caption(
            "Odds Ratio (e^β) interpretation: Values > 1.0 indicate an increase in placement odds per unit increase in the predictor, holding other variables constant. Note: Synthetic benchmark demonstration only."
        )
    else:
        st.info("A minimum of 30 records with both placed and unplaced outcomes is required for logistic regression.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 5: MBA Presentation Statistical Methods Guide
    render_section_header(
        "Executive Methodology Guide for MBA Presentation",
        "Key statistical concepts used throughout this dashboard to explain to faculty and executive panels.",
        "📖"
    )
    
    with st.expander("📚 View Statistical Concepts & Defense Guide", expanded=False):
        st.markdown(
            r"""
            ### 1. Why Median vs. Mean for Compensation?
            * **Problem with Mean:** Corporate compensation distributions are heavily right-skewed by a few exceptionally high packages (e.g. 24 LPA vs cohort baseline of 8 LPA).
            * **Methodological Defense:** The **Median (50th percentile)** represents the true typical student package and is resistant to extreme outliers, while the **Interquartile Range (IQR = P75 - P25)** accurately captures the core 50% spread.
            
            ### 2. Pearson Correlation Coefficient ($r$) & p-Values
            * **Correlation ($r$):** Measures the linear association between continuous variables ($-1 \le r \le +1$).
            * **p-Value Significance:** A $p < 0.05$ indicates that the probability of observing such an association purely by random sampling chance is less than 5%.
            
            ### 3. Welch's Two-Sample t-Test & Cohen's $d$
            * **Welch's t-Test:** Tests whether the observed difference between Placed and Unplaced students (e.g. in marks or attendance) is statistically significant without assuming equal cohort variances.
            * **Cohen's $d$ (Effect Size):** Quantifies practical significance ($d \approx 0.2$ is small, $d \approx 0.5$ is moderate, $d \ge 0.8$ is large).
            
            ### 4. Logistic Regression Odds Ratios ($\text{OR} = e^\beta$)
            * **Concept:** In binary classification (Placed vs. Unplaced), the logistic link function models log-odds $\ln(\frac{p}{1-p})$.
            * **Odds Ratio ($\text{OR}$):** Exponentiating coefficients yields direct business interpretations: an $\text{OR} = 1.35$ means each unit increase increases placement odds by 35%, controlling for other variables.
            """
        )
        
    render_footer()
