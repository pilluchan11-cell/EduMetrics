"""
Unit tests for EduMetrics metrics calculations and statistical engine.
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics import (
    compute_executive_kpis,
    compute_academic_summary,
    compute_attendance_summary,
    compute_salary_detailed_summary,
    compute_grade_distribution,
    compute_placement_by_specialization,
    compute_placement_by_academic_tier,
    compute_company_placement_stats,
    compute_skill_placement_matrix,
    compute_correlation_matrix,
    compute_correlation_with_significance,
    compute_group_comparisons,
    compute_placement_logistic_regression,
    generate_dynamic_business_insights
)
from src.data_generator import generate_synthetic_data


@pytest.fixture
def sample_students_df():
    return pd.DataFrame([
        {
            "student_id": "EDU-001",
            "student_name": "Test Student 1",
            "gender": "Female",
            "specialization": "Business Analytics",
            "semester": "Semester 3",
            "academic_percentage": 85.0,
            "attendance_percentage": 90.0,
            "sql_proficiency": "Advanced",
            "python_proficiency": "Advanced",
            "power_bi_proficiency": "Intermediate",
            "certifications_count": 3,
            "internship_status": "Completed",
            "placement_status": "Placed",
            "company": "Apex Analytics",
            "salary_lpa": 14.5,
            "grade_band": "Distinction (>=80%)",
            "attendance_band": "High (>=85%)",
            "technical_score_10": 8.89
        },
        {
            "student_id": "EDU-002",
            "student_name": "Test Student 2",
            "gender": "Male",
            "specialization": "Finance",
            "semester": "Semester 3",
            "academic_percentage": 60.0,
            "attendance_percentage": 70.0,
            "sql_proficiency": "Beginner",
            "python_proficiency": "Beginner",
            "power_bi_proficiency": "Beginner",
            "certifications_count": 0,
            "internship_status": "Not Completed",
            "placement_status": "Unplaced",
            "company": None,
            "salary_lpa": np.nan,
            "grade_band": "Second Class (50-64%)",
            "attendance_band": "Critical Alert (<75%)",
            "technical_score_10": 3.33
        }
    ])


def test_compute_executive_kpis(sample_students_df):
    kpis = compute_executive_kpis(sample_students_df)
    assert kpis["total_students"] == 2
    assert kpis["placed_count"] == 1
    assert kpis["unplaced_count"] == 1
    assert kpis["placement_rate"] == 50.0
    assert kpis["avg_salary"] == 14.5
    assert kpis["highest_salary"] == 14.5
    assert kpis["avg_academic"] == 72.5
    assert kpis["avg_attendance"] == 80.0


def test_compute_executive_kpis_empty():
    kpis = compute_executive_kpis(pd.DataFrame())
    assert kpis["total_students"] == 0
    assert kpis["placement_rate"] == 0.0
    assert kpis["avg_salary"] == 0.0


def test_compute_academic_summary(sample_students_df):
    stats = compute_academic_summary(sample_students_df)
    assert stats["mean"] == 72.5
    assert stats["min"] == 60.0
    assert stats["max"] == 85.0
    assert stats["iqr"] == 12.5


def test_compute_attendance_summary(sample_students_df):
    att = compute_attendance_summary(sample_students_df)
    assert att["mean"] == 80.0
    assert att["compliant_count"] == 1
    assert att["compliant_rate"] == 50.0
    assert att["risk_count"] == 1
    assert att["risk_rate"] == 50.0


def test_compute_salary_detailed_summary(sample_students_df):
    sal = compute_salary_detailed_summary(sample_students_df)
    assert sal["count"] == 1
    assert sal["mean"] == 14.5
    assert sal["median"] == 14.5


def test_compute_grade_distribution(sample_students_df):
    grades = compute_grade_distribution(sample_students_df)
    assert len(grades) == 2
    assert "Distinction (>=80%)" in grades["Grade Band"].values


def test_compute_placement_by_specialization(sample_students_df):
    spec_df = compute_placement_by_specialization(sample_students_df)
    ba_row = spec_df[spec_df["Specialization"] == "Business Analytics"].iloc[0]
    assert ba_row["Placement Rate (%)"] == 100.0
    fin_row = spec_df[spec_df["Specialization"] == "Finance"].iloc[0]
    assert fin_row["Placement Rate (%)"] == 0.0


def test_compute_placement_by_academic_tier(sample_students_df):
    tier_df = compute_placement_by_academic_tier(sample_students_df)
    assert len(tier_df) == 2
    dist_row = tier_df[tier_df["Academic Performance Tier"] == "Distinction (>=80%)"].iloc[0]
    assert dist_row["Placement Rate (%)"] == 100.0


def test_compute_company_placement_stats(sample_students_df):
    comp_df = compute_company_placement_stats(sample_students_df)
    assert len(comp_df) == 1
    assert comp_df.iloc[0]["Company"] == "Apex Analytics"
    assert comp_df.iloc[0]["Students Hired"] == 1


def test_compute_skill_placement_matrix(sample_students_df):
    mat = compute_skill_placement_matrix(sample_students_df, "python_proficiency")
    assert len(mat) > 0
    adv_row = mat[mat["Proficiency Level"] == "Advanced"].iloc[0]
    assert adv_row["Placement Rate (%)"] == 100.0


def test_dynamic_business_insights():
    # Use realistic synthetic dataset of 100 rows to test dynamic generation
    full_df = generate_synthetic_data(n=100, seed=42)
    # Add enriched columns
    mapping = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    full_df["technical_score_10"] = full_df.apply(
        lambda r: round(((mapping[r["sql_proficiency"]] + mapping[r["python_proficiency"]] + mapping[r["power_bi_proficiency"]]) / 9.0) * 10, 2),
        axis=1
    )
    
    insights = generate_dynamic_business_insights(full_df)
    assert len(insights) >= 5
    for item in insights:
        assert "title" in item
        assert "finding" in item
        assert "mba_takeaway" in item
        assert "method" in item


def test_group_comparisons():
    full_df = generate_synthetic_data(n=60, seed=42)
    mapping = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    full_df["technical_score_10"] = full_df.apply(
        lambda r: round(((mapping[r["sql_proficiency"]] + mapping[r["python_proficiency"]] + mapping[r["power_bi_proficiency"]]) / 9.0) * 10, 2),
        axis=1
    )
    res = compute_group_comparisons(full_df)
    assert len(res["placed_vs_unplaced"]) > 0
    assert "t-Statistic" in res["placed_vs_unplaced"].columns
    assert "Cohen's d (Effect Size)" in res["placed_vs_unplaced"].columns


def test_placement_logistic_regression():
    full_df = generate_synthetic_data(n=80, seed=42)
    mapping = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    full_df["technical_score_10"] = full_df.apply(
        lambda r: round(((mapping[r["sql_proficiency"]] + mapping[r["python_proficiency"]] + mapping[r["power_bi_proficiency"]]) / 9.0) * 10, 2),
        axis=1
    )
    res = compute_placement_logistic_regression(full_df)
    assert res is not None
    assert "accuracy" in res
    assert "roc_auc" in res
    assert "coefficients_table" in res
    assert "Odds Ratio (e^β)" in res["coefficients_table"].columns
