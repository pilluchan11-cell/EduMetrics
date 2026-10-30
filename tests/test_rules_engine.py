"""
Unit tests for the explainable recommendation engine.
"""

import pytest
import pandas as pd
from src.rules_engine import evaluate_student_profile, generate_cohort_recommendations


def test_student_recommendations_low_attendance():
    student = pd.Series({
        "student_id": "EDU-099",
        "student_name": "Low Att Student",
        "academic_percentage": 75.0,
        "attendance_percentage": 68.0,
        "sql_proficiency": "Intermediate",
        "python_proficiency": "Intermediate",
        "power_bi_proficiency": "Intermediate",
        "certifications_count": 2,
        "internship_status": "Completed",
        "placement_status": "Unplaced"
    })
    recs = evaluate_student_profile(student)
    titles = [r["title"] for r in recs]
    assert "Low Attendance Alert" in titles
    
    # Check rationale is present
    att_rec = [r for r in recs if r["title"] == "Low Attendance Alert"][0]
    assert att_rec["status"] == "Critical"
    assert "75" in att_rec["message"]


def test_student_recommendations_placed():
    student = pd.Series({
        "student_id": "EDU-100",
        "student_name": "Placed Star",
        "academic_percentage": 92.0,
        "attendance_percentage": 94.0,
        "sql_proficiency": "Advanced",
        "python_proficiency": "Advanced",
        "power_bi_proficiency": "Advanced",
        "certifications_count": 4,
        "internship_status": "Completed",
        "placement_status": "Placed",
        "company": "Nexus Consulting",
        "salary_lpa": 18.0
    })
    recs = evaluate_student_profile(student)
    titles = [r["title"] for r in recs]
    assert "Placement Confirmed" in titles
    assert "Strong Academic Standing" in titles
    assert "Robust Technical Foundation" in titles


def test_cohort_recommendations():
    df = pd.DataFrame([
        {
            "student_id": "EDU-001",
            "attendance_percentage": 65.0,
            "placement_status": "Unplaced",
            "sql_proficiency": "Beginner",
            "python_proficiency": "Beginner",
            "internship_status": "Not Completed",
            "certifications_count": 0
        },
        {
            "student_id": "EDU-002",
            "attendance_percentage": 70.0,
            "placement_status": "Unplaced",
            "sql_proficiency": "Beginner",
            "python_proficiency": "Beginner",
            "internship_status": "Not Completed",
            "certifications_count": 0
        }
    ])
    cohort_recs = generate_cohort_recommendations(df)
    areas = [c["area"] for c in cohort_recs]
    assert "Attendance Compliance" in areas
    assert "Experiential Learning Gap" in areas
