"""
Unit tests for EduMetrics metrics calculations.
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics import (
    compute_executive_kpis,
    compute_academic_summary,
    compute_grade_distribution,
    compute_placement_by_specialization,
    compute_company_placement_stats,
    compute_skill_placement_matrix,
    compute_correlation_matrix
)


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
