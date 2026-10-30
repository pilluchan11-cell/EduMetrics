"""
Unit tests for data validation, cleaning, and schema checks.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_loader import validate_dataframe, clean_and_enrich_data


def test_validate_missing_columns():
    invalid_df = pd.DataFrame({
        "student_id": ["EDU-001"],
        "student_name": ["Jane Doe"]
    })
    is_valid, errors, summary = validate_dataframe(invalid_df)
    assert not is_valid
    assert any("Missing required columns" in err for err in errors)


def test_validate_duplicate_ids():
    dup_df = pd.DataFrame({
        "student_id": ["EDU-001", "EDU-001"],
        "student_name": ["Student A", "Student B"],
        "gender": ["Male", "Female"],
        "specialization": ["Finance", "Marketing"],
        "semester": ["Semester 1", "Semester 1"],
        "academic_percentage": [75.0, 80.0],
        "attendance_percentage": [85.0, 90.0],
        "sql_proficiency": ["Beginner", "Intermediate"],
        "python_proficiency": ["Beginner", "Intermediate"],
        "power_bi_proficiency": ["Beginner", "Intermediate"],
        "certifications_count": [1, 2],
        "internship_status": ["Completed", "Completed"],
        "placement_status": ["Unplaced", "Placed"],
        "company": [None, "Apex Analytics"],
        "salary_lpa": [np.nan, 12.0]
    })
    is_valid, errors, summary = validate_dataframe(dup_df)
    assert not is_valid
    assert summary["duplicate_ids"] == 1


def test_clean_and_enrich_consistency():
    raw_df = pd.DataFrame([{
        "student_id": "EDU-001",
        "student_name": "  Jane Doe  ",
        "gender": "Female",
        "specialization": "Finance",
        "semester": "Semester 3",
        "academic_percentage": 82.5,
        "attendance_percentage": 73.0,
        "sql_proficiency": "advanced",
        "python_proficiency": "intermediate",
        "power_bi_proficiency": "beginner",
        "certifications_count": 2,
        "internship_status": "Completed",
        "placement_status": "Unplaced",
        "company": "Fictional Corp",  # Inconsistent: unplaced with company
        "salary_lpa": 12.5           # Inconsistent: unplaced with salary
    }])
    cleaned = clean_and_enrich_data(raw_df)
    
    # Check whitespace stripped
    assert cleaned.iloc[0]["student_name"] == "Jane Doe"
    # Check capitalization
    assert cleaned.iloc[0]["sql_proficiency"] == "Advanced"
    # Check consistency enforced for unplaced
    assert pd.isna(cleaned.iloc[0]["salary_lpa"])
    assert pd.isna(cleaned.iloc[0]["company"]) or cleaned.iloc[0]["company"] is None
    # Check enriched bands
    assert cleaned.iloc[0]["grade_band"] == "Distinction (>=80%)"
    assert cleaned.iloc[0]["attendance_band"] == "Critical Alert (<75%)"
    assert cleaned.iloc[0]["is_academic_at_risk"] == True


def test_validate_empty_dataset():
    """Checks validation rejection for 0-row datasets."""
    empty_df = pd.DataFrame()
    is_valid, errors, summary = validate_dataframe(empty_df)
    assert not is_valid
    assert any("empty" in err.lower() or "missing required columns" in err.lower() for err in errors)


def test_validate_invalid_ranges():
    """Checks detection of out-of-bounds percentages."""
    invalid_range_df = pd.DataFrame([{
        "student_id": "EDU-001",
        "student_name": "Test Student",
        "gender": "Male",
        "specialization": "Finance",
        "semester": "Semester 1",
        "academic_percentage": 145.0,  # Invalid: > 100
        "attendance_percentage": -15.0,  # Invalid: < 0
        "sql_proficiency": "Beginner",
        "python_proficiency": "Beginner",
        "power_bi_proficiency": "Beginner",
        "certifications_count": 0,
        "internship_status": "Not Completed",
        "placement_status": "Unplaced",
        "company": None,
        "salary_lpa": np.nan
    }])
    is_valid, errors, summary = validate_dataframe(invalid_range_df)
    assert not is_valid
    assert len(summary["invalid_ranges"]) > 0


def test_validate_placed_inconsistency():
    """Checks detection of placed records lacking required compensation or company."""
    inconsistent_df = pd.DataFrame([{
        "student_id": "EDU-001",
        "student_name": "Placed Without Company",
        "gender": "Female",
        "specialization": "Marketing",
        "semester": "Semester 2",
        "academic_percentage": 75.0,
        "attendance_percentage": 85.0,
        "sql_proficiency": "Intermediate",
        "python_proficiency": "Intermediate",
        "power_bi_proficiency": "Intermediate",
        "certifications_count": 1,
        "internship_status": "Completed",
        "placement_status": "Placed",
        "company": None,  # Missing!
        "salary_lpa": np.nan  # Missing!
    }])
    is_valid, errors, summary = validate_dataframe(inconsistent_df)
    assert not is_valid
    assert any("placed records have missing company or salary" in err for err in errors)
