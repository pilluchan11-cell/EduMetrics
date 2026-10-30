"""
Data loading, cleaning, validation, and feature enrichment for EduMetrics.
"""

from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from src.config import (
    DEFAULT_CSV_PATH,
    EXPECTED_COLUMNS,
    ATTENDANCE_CRITICAL_THRESHOLD,
    ACADEMIC_DISTINCTION_THRESHOLD,
    ACADEMIC_PASS_THRESHOLD
)
from src.data_generator import ensure_default_dataset


def assign_grade_band(percentage: float) -> str:
    """Categorizes academic percentage into academic performance bands."""
    if pd.isna(percentage):
        return "Unknown"
    if percentage >= ACADEMIC_DISTINCTION_THRESHOLD:
        return "Distinction (>=80%)"
    elif percentage >= 65.0:
        return "First Class (65-79%)"
    elif percentage >= ACADEMIC_PASS_THRESHOLD:
        return "Second Class (50-64%)"
    else:
        return "Support Required (<50%)"


def assign_attendance_band(attendance: float) -> str:
    """Categorizes attendance percentage into compliance tiers."""
    if pd.isna(attendance):
        return "Unknown"
    if attendance >= 85.0:
        return "High (>=85%)"
    elif attendance >= ATTENDANCE_CRITICAL_THRESHOLD:
        return "Standard (75-84%)"
    else:
        return "Critical Alert (<75%)"


def calculate_technical_index(row: pd.Series) -> float:
    """Computes a normalized technical competence index out of 10."""
    mapping = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    sql = mapping.get(str(row.get("sql_proficiency", "")).strip().capitalize(), 1)
    py = mapping.get(str(row.get("python_proficiency", "")).strip().capitalize(), 1)
    bi = mapping.get(str(row.get("power_bi_proficiency", "")).strip().capitalize(), 1)
    # Total points out of 9, scaled to 10
    return round(((sql + py + bi) / 9.0) * 10.0, 2)


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Validates a student dataframe against schema and integrity rules.
    
    Returns:
        (is_valid, error_list, summary_stats)
    """
    errors = []
    summary = {
        "total_rows": len(df),
        "duplicate_ids": 0,
        "missing_values_by_col": {},
        "invalid_ranges": []
    }
    
    # 1. Column existence
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return False, errors, summary
        
    # 2. Duplicate student_id
    dups = df["student_id"].duplicated().sum()
    summary["duplicate_ids"] = int(dups)
    if dups > 0:
        errors.append(f"Found {dups} duplicate student_id records.")
        
    # 3. Missing values check
    for col in EXPECTED_COLUMNS:
        null_count = int(df[col].isna().sum())
        # company and salary_lpa are legitimately nullable for unplaced students
        if col not in ["company", "salary_lpa"] and null_count > 0:
            summary["missing_values_by_col"][col] = null_count
            errors.append(f"Column '{col}' has {null_count} missing values.")
            
    # 4. Range validation
    invalid_academic = df[
        (df["academic_percentage"] < 0) | (df["academic_percentage"] > 100)
    ]
    if len(invalid_academic) > 0:
        summary["invalid_ranges"].append(f"{len(invalid_academic)} rows have invalid academic percentages.")
        
    invalid_att = df[
        (df["attendance_percentage"] < 0) | (df["attendance_percentage"] > 100)
    ]
    if len(invalid_att) > 0:
        summary["invalid_ranges"].append(f"{len(invalid_att)} rows have invalid attendance percentages.")
        
    is_valid = len(errors) == 0
    return is_valid, errors, summary


def clean_and_enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw student data and enriches it with calculated analytical features.
    """
    clean_df = df.copy()
    
    # Clean whitespace and enforce string types
    str_cols = ["student_id", "student_name", "gender", "specialization", 
                "semester", "sql_proficiency", "python_proficiency", 
                "power_bi_proficiency", "internship_status", "placement_status"]
    
    for c in str_cols:
        if c in clean_df.columns:
            clean_df[c] = clean_df[c].astype(str).str.strip()
            
    # Standardize proficiencies
    for c in ["sql_proficiency", "python_proficiency", "power_bi_proficiency"]:
        if c in clean_df.columns:
            clean_df[c] = clean_df[c].str.capitalize()
            
    # Numeric conversions
    clean_df["academic_percentage"] = pd.to_numeric(clean_df["academic_percentage"], errors="coerce")
    clean_df["attendance_percentage"] = pd.to_numeric(clean_df["attendance_percentage"], errors="coerce")
    clean_df["certifications_count"] = pd.to_numeric(clean_df["certifications_count"], errors="coerce").fillna(0).astype(int)
    clean_df["salary_lpa"] = pd.to_numeric(clean_df["salary_lpa"], errors="coerce")
    
    # Enforce logical consistency for placement
    unplaced_mask = clean_df["placement_status"].str.lower() != "placed"
    clean_df.loc[unplaced_mask, "salary_lpa"] = np.nan
    clean_df.loc[unplaced_mask, "company"] = None
    
    # Enrich with analytic categorizations
    clean_df["grade_band"] = clean_df["academic_percentage"].apply(assign_grade_band)
    clean_df["attendance_band"] = clean_df["attendance_percentage"].apply(assign_attendance_band)
    clean_df["technical_score_10"] = clean_df.apply(calculate_technical_index, axis=1)
    
    # At-risk academic/placement flag
    clean_df["is_academic_at_risk"] = (
        (clean_df["academic_percentage"] < 55.0) | 
        (clean_df["attendance_percentage"] < ATTENDANCE_CRITICAL_THRESHOLD)
    )
    
    return clean_df


@st.cache_data(show_spinner="Loading student analytics dataset...")
def load_cached_dataset(file_path_or_buffer=None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads dataset from file or buffer, validates, enriches, and caches it.
    """
    if file_path_or_buffer is None:
        raw_df = ensure_default_dataset()
    else:
        if isinstance(file_path_or_buffer, (str, Path)):
            raw_df = pd.read_csv(file_path_or_buffer)
        else:
            raw_df = pd.read_csv(file_path_or_buffer)
            
    is_valid, errors, summary = validate_dataframe(raw_df)
    clean_df = clean_and_enrich_data(raw_df)
    
    report = {
        "is_valid": is_valid,
        "errors": errors,
        "summary": summary
    }
    return clean_df, report
