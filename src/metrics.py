"""
Metrics and Statistical Calculations Engine for EduMetrics.
Pure calculation functions with zero UI dependency.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def compute_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes top-level executive KPIs for the dashboard.
    """
    total_students = len(df)
    if total_students == 0:
        return {
            "total_students": 0,
            "avg_academic": 0.0,
            "avg_attendance": 0.0,
            "placed_count": 0,
            "unplaced_count": 0,
            "placement_rate": 0.0,
            "avg_salary": 0.0,
            "median_salary": 0.0,
            "highest_salary": 0.0,
            "eligible_for_placement": 0
        }
        
    placed_mask = df["placement_status"].str.lower() == "placed"
    placed_count = int(placed_mask.sum())
    unplaced_count = total_students - placed_count
    placement_rate = round((placed_count / total_students) * 100.0, 1)
    
    placed_df = df[placed_mask]
    if len(placed_df) > 0 and placed_df["salary_lpa"].notna().sum() > 0:
        avg_salary = round(float(placed_df["salary_lpa"].mean()), 2)
        median_salary = round(float(placed_df["salary_lpa"].median()), 2)
        highest_salary = round(float(placed_df["salary_lpa"].max()), 2)
    else:
        avg_salary = 0.0
        median_salary = 0.0
        highest_salary = 0.0
        
    avg_academic = round(float(df["academic_percentage"].mean()), 1)
    avg_attendance = round(float(df["attendance_percentage"].mean()), 1)
    
    return {
        "total_students": total_students,
        "avg_academic": avg_academic,
        "avg_attendance": avg_attendance,
        "placed_count": placed_count,
        "unplaced_count": unplaced_count,
        "placement_rate": placement_rate,
        "avg_salary": avg_salary,
        "median_salary": median_salary,
        "highest_salary": highest_salary
    }


def compute_academic_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes statistical distribution metrics for academic performance.
    """
    if len(df) == 0:
        return {}
        
    series = df["academic_percentage"].dropna()
    return {
        "mean": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
        "std": round(float(series.std()), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "q25": round(float(series.quantile(0.25)), 2),
        "q75": round(float(series.quantile(0.75)), 2),
        "iqr": round(float(series.quantile(0.75) - series.quantile(0.25)), 2)
    }


def compute_grade_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates student distribution by academic grade band.
    """
    if len(df) == 0 or "grade_band" not in df.columns:
        return pd.DataFrame()
        
    band_counts = df["grade_band"].value_counts().reset_index()
    band_counts.columns = ["Grade Band", "Student Count"]
    band_counts["Percentage"] = (
        (band_counts["Student Count"] / len(df)) * 100.0
    ).round(1)
    return band_counts


def compute_specialization_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates academic and attendance averages per specialization.
    """
    if len(df) == 0:
        return pd.DataFrame()
        
    grouped = df.groupby("specialization").agg(
        Total_Students=("student_id", "count"),
        Avg_Academic=("academic_percentage", lambda x: round(x.mean(), 1)),
        Avg_Attendance=("attendance_percentage", lambda x: round(x.mean(), 1)),
        Avg_Tech_Index=("technical_score_10", lambda x: round(x.mean(), 1)),
        Placed_Count=("placement_status", lambda x: (x.str.lower() == "placed").sum())
    ).reset_index()
    
    grouped["Placement_Rate"] = (
        (grouped["Placed_Count"] / grouped["Total_Students"]) * 100.0
    ).round(1)
    return grouped


def compute_placement_by_specialization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Placement rates, placed counts, and average salaries across specializations.
    """
    if len(df) == 0:
        return pd.DataFrame()
        
    records = []
    for spec, group in df.groupby("specialization"):
        total = len(group)
        placed = group[group["placement_status"].str.lower() == "placed"]
        placed_count = len(placed)
        rate = round((placed_count / total) * 100.0, 1) if total > 0 else 0.0
        avg_sal = round(float(placed["salary_lpa"].mean()), 2) if len(placed) > 0 else 0.0
        med_sal = round(float(placed["salary_lpa"].median()), 2) if len(placed) > 0 else 0.0
        
        records.append({
            "Specialization": spec,
            "Total Students": total,
            "Placed Students": placed_count,
            "Placement Rate (%)": rate,
            "Avg Salary (LPA)": avg_sal,
            "Median Salary (LPA)": med_sal
        })
        
    return pd.DataFrame(records).sort_values(by="Placement Rate (%)", ascending=False)


def compute_company_placement_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes hiring distribution and compensation by company.
    """
    placed_df = df[df["placement_status"].str.lower() == "placed"]
    if len(placed_df) == 0:
        return pd.DataFrame()
        
    company_stats = placed_df.groupby("company").agg(
        Hires=("student_id", "count"),
        Avg_Salary=("salary_lpa", lambda x: round(x.mean(), 2)),
        Min_Salary=("salary_lpa", lambda x: round(x.min(), 2)),
        Max_Salary=("salary_lpa", lambda x: round(x.max(), 2))
    ).reset_index()
    
    company_stats = company_stats.sort_values(by="Hires", ascending=False)
    company_stats.columns = ["Company", "Students Hired", "Avg Package (LPA)", "Min Package (LPA)", "Max Package (LPA)"]
    return company_stats


def compute_skill_placement_matrix(df: pd.DataFrame, skill_col: str) -> pd.DataFrame:
    """
    Calculates placement rates segmented by proficiency in a specified technical skill.
    """
    if len(df) == 0 or skill_col not in df.columns:
        return pd.DataFrame()
        
    records = []
    for level, group in df.groupby(skill_col):
        total = len(group)
        placed = (group["placement_status"].str.lower() == "placed").sum()
        rate = round((placed / total) * 100.0, 1) if total > 0 else 0.0
        avg_sal = round(float(group[group["placement_status"].str.lower() == "placed"]["salary_lpa"].mean()), 2)
        records.append({
            "Proficiency Level": level,
            "Total Students": total,
            "Placed Students": placed,
            "Placement Rate (%)": rate,
            "Avg Salary (LPA)": avg_sal if not np.isnan(avg_sal) else 0.0
        })
    
    order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    res_df = pd.DataFrame(records)
    res_df["order"] = res_df["Proficiency Level"].map(order).fillna(4)
    res_df = res_df.sort_values(by="order").drop(columns=["order"])
    return res_df


def get_top_and_support_students(df: pd.DataFrame, top_n: int = 10) -> Dict[str, pd.DataFrame]:
    """
    Retrieves cohorts of top performers and students requiring academic support.
    """
    if len(df) == 0:
        return {"top": pd.DataFrame(), "support": pd.DataFrame()}
        
    cols = [
        "student_id", "student_name", "specialization", "semester", 
        "academic_percentage", "attendance_percentage", "technical_score_10", 
        "placement_status"
    ]
    avail_cols = [c for c in cols if c in df.columns]
    
    # Top performers: Highest academic percentage
    top_students = df.sort_values(by="academic_percentage", ascending=False).head(top_n)[avail_cols]
    
    # Students requiring support: Low academic score or attendance below threshold
    support_students = df[
        (df["academic_percentage"] < 58.0) | 
        (df["attendance_percentage"] < 75.0)
    ].sort_values(by=["academic_percentage", "attendance_percentage"])[avail_cols]
    
    return {
        "top": top_students,
        "support": support_students
    }


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates pairwise correlation among numerical columns.
    """
    num_cols = ["academic_percentage", "attendance_percentage", 
                "certifications_count", "technical_score_10"]
    if "salary_lpa" in df.columns:
        num_cols.append("salary_lpa")
        
    valid_cols = [c for c in num_cols if c in df.columns]
    corr = df[valid_cols].corr().round(3)
    return corr
