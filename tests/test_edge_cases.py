"""
Edge Case & Fault Tolerance Tests for EduMetrics.
Validates robust handling of empty datasets, missing values, extreme inputs,
and zero-record filter slicing across all analytical and visualization layers.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.metrics import (
    compute_executive_kpis,
    compute_academic_summary,
    compute_attendance_summary,
    compute_salary_detailed_summary,
    compute_grade_distribution,
    compute_specialization_performance,
    compute_placement_by_specialization,
    compute_placement_by_academic_tier,
    compute_company_placement_stats,
    compute_skill_placement_matrix,
    get_top_and_support_students,
    compute_correlation_matrix,
    compute_correlation_with_significance,
    compute_group_comparisons,
    compute_placement_logistic_regression,
    generate_dynamic_business_insights
)
from src.rules_engine import evaluate_student_profile, generate_cohort_recommendations
from src.visualizations import (
    plot_placement_donut,
    plot_academic_distribution,
    plot_grade_distribution,
    plot_attendance_vs_academic,
    plot_placement_by_specialization,
    plot_salary_distribution,
    plot_company_hires,
    plot_skills_placement_impact,
    plot_student_radar_benchmark,
    plot_correlation_heatmap,
    plot_semester_comparison
)
from src.database import save_dataframe_to_db, load_data_from_db


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Returns an empty DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def empty_schema_df() -> pd.DataFrame:
    """Returns an empty DataFrame with valid EduMetrics columns."""
    from src.config import EXPECTED_COLUMNS
    return pd.DataFrame(columns=EXPECTED_COLUMNS)


# ====================================================================
# 1. Empty Dataset Metrics Tests
# ====================================================================

def test_metrics_empty_dataframe(empty_df):
    """Verifies that all metrics return safe zero/default values on empty data."""
    kpis = compute_executive_kpis(empty_df)
    assert kpis["total_students"] == 0
    assert kpis["placement_rate"] == 0.0
    assert kpis["avg_salary"] == 0.0

    acad = compute_academic_summary(empty_df)
    assert acad["mean"] == 0.0
    assert acad["iqr"] == 0.0

    att = compute_attendance_summary(empty_df)
    assert att["compliant_count"] == 0
    assert att["compliant_rate"] == 0.0

    sal = compute_salary_detailed_summary(empty_df)
    assert sal["count"] == 0
    assert sal["median"] == 0.0

    grades = compute_grade_distribution(empty_df)
    assert len(grades) == 0

    spec_perf = compute_specialization_performance(empty_df)
    assert len(spec_perf) == 0

    spec_place = compute_placement_by_specialization(empty_df)
    assert len(spec_place) == 0

    tier = compute_placement_by_academic_tier(empty_df)
    assert len(tier) == 0

    comp = compute_company_placement_stats(empty_df)
    assert len(comp) == 0

    matrix = compute_skill_placement_matrix(empty_df, "python_proficiency")
    assert len(matrix) == 0

    top_sup = get_top_and_support_students(empty_df)
    assert len(top_sup["top"]) == 0
    assert len(top_sup["support"]) == 0

    corr = compute_correlation_matrix(empty_df)
    assert len(corr) == 0

    sig = compute_correlation_with_significance(empty_df)
    assert len(sig) == 0

    comp_groups = compute_group_comparisons(empty_df)
    assert len(comp_groups["placed_vs_unplaced"]) == 0
    assert comp_groups["anova_specializations"] is None

    logit = compute_placement_logistic_regression(empty_df)
    assert logit is None

    insights = generate_dynamic_business_insights(empty_df)
    assert len(insights) == 0

    recs = generate_cohort_recommendations(empty_df)
    assert len(recs) == 0


# ====================================================================
# 2. Missing Values & NaNs in Student Rules Engine
# ====================================================================

def test_rules_engine_nan_handling():
    """Verifies that missing or NaN attributes do not crash student diagnostic engine."""
    student_nan = pd.Series({
        "student_id": "EDU-TEST-NAN",
        "student_name": "Incomplete Profile",
        "gender": None,
        "specialization": "Finance",
        "semester": "Semester 1",
        "academic_percentage": np.nan,
        "attendance_percentage": np.nan,
        "sql_proficiency": None,
        "python_proficiency": None,
        "power_bi_proficiency": None,
        "certifications_count": np.nan,
        "internship_status": None,
        "placement_status": None,
        "company": None,
        "salary_lpa": np.nan
    })
    
    recs = evaluate_student_profile(student_nan)
    assert len(recs) > 0
    # Must identify pending records without throwing exception
    titles = [r["title"] for r in recs]
    assert "Attendance Record Pending" in titles
    assert "Academic Marks Pending" in titles


# ====================================================================
# 3. Homogeneous Cohorts (All Placed or All Unplaced)
# ====================================================================

def test_all_placed_cohort():
    """Verifies analytics when 100% of the cohort is placed."""
    placed_all_df = pd.DataFrame([
        {
            "student_id": f"EDU-{i:03d}",
            "student_name": f"Student {i}",
            "gender": "Female",
            "specialization": "Business Analytics",
            "semester": "Semester 3",
            "academic_percentage": 80.0 + (i % 10),
            "attendance_percentage": 85.0,
            "sql_proficiency": "Advanced",
            "python_proficiency": "Advanced",
            "power_bi_proficiency": "Intermediate",
            "certifications_count": 3,
            "internship_status": "Completed",
            "placement_status": "Placed",
            "company": "Apex Analytics",
            "salary_lpa": 12.0 + (i * 0.5),
            "grade_band": "Distinction (>=80%)",
            "attendance_band": "High (>=85%)",
            "technical_score_10": 8.89
        }
        for i in range(10)
    ])
    
    kpis = compute_executive_kpis(placed_all_df)
    assert kpis["total_students"] == 10
    assert kpis["placed_count"] == 10
    assert kpis["unplaced_count"] == 0
    assert kpis["placement_rate"] == 100.0
    assert kpis["avg_salary"] > 0
    
    donut = plot_placement_donut(placed_all_df)
    assert isinstance(donut, go.Figure)


def test_all_unplaced_cohort():
    """Verifies analytics when 0% of the cohort is placed (all seeking)."""
    unplaced_all_df = pd.DataFrame([
        {
            "student_id": f"EDU-{i:03d}",
            "student_name": f"Student {i}",
            "gender": "Male",
            "specialization": "Marketing",
            "semester": "Semester 2",
            "academic_percentage": 65.0,
            "attendance_percentage": 78.0,
            "sql_proficiency": "Beginner",
            "python_proficiency": "Beginner",
            "power_bi_proficiency": "Beginner",
            "certifications_count": 0,
            "internship_status": "Not Completed",
            "placement_status": "Unplaced",
            "company": None,
            "salary_lpa": np.nan,
            "grade_band": "First Class (65-79%)",
            "attendance_band": "Standard (75-84%)",
            "technical_score_10": 3.33
        }
        for i in range(10)
    ])
    
    kpis = compute_executive_kpis(unplaced_all_df)
    assert kpis["total_students"] == 10
    assert kpis["placed_count"] == 0
    assert kpis["unplaced_count"] == 10
    assert kpis["placement_rate"] == 0.0
    assert kpis["avg_salary"] == 0.0
    assert kpis["median_salary"] == 0.0
    assert kpis["highest_salary"] == 0.0
    
    sal_box = plot_salary_distribution(unplaced_all_df)
    assert isinstance(sal_box, go.Figure)


# ====================================================================
# 4. Plotly Charts on Empty and Edge-Case Datasets
# ====================================================================

def test_plotly_charts_empty_dataframe(empty_df):
    """Verifies that none of the Plotly visualizations raise exceptions when given empty data."""
    fig1 = plot_placement_donut(empty_df)
    assert isinstance(fig1, go.Figure)

    fig2 = plot_academic_distribution(empty_df)
    assert isinstance(fig2, go.Figure)

    fig3 = plot_grade_distribution(pd.DataFrame())
    assert isinstance(fig3, go.Figure)

    fig4 = plot_attendance_vs_academic(empty_df)
    assert isinstance(fig4, go.Figure)

    fig5 = plot_placement_by_specialization(pd.DataFrame())
    assert isinstance(fig5, go.Figure)

    fig6 = plot_salary_distribution(empty_df)
    assert isinstance(fig6, go.Figure)

    fig7 = plot_company_hires(pd.DataFrame())
    assert isinstance(fig7, go.Figure)

    fig8 = plot_skills_placement_impact(empty_df, "python_proficiency", "Python")
    assert isinstance(fig8, go.Figure)

    single_student = pd.Series({
        "academic_percentage": 75.0,
        "attendance_percentage": 82.0,
        "sql_proficiency": "Intermediate",
        "python_proficiency": "Advanced",
        "power_bi_proficiency": "Beginner",
        "certifications_count": 2,
        "student_name": "Test Radar"
    })
    fig9 = plot_student_radar_benchmark(single_student, empty_df)
    assert isinstance(fig9, go.Figure)

    fig10 = plot_correlation_heatmap(pd.DataFrame())
    assert isinstance(fig10, go.Figure)

    fig11 = plot_semester_comparison(empty_df)
    assert isinstance(fig11, go.Figure)


# ====================================================================
# 5. Database Save on Empty DataFrame
# ====================================================================

def test_database_save_empty_df(empty_df):
    """Verifies that saving an empty dataframe returns 0 without crashing."""
    res = save_dataframe_to_db(empty_df)
    assert res == 0
