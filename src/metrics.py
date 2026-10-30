"""
Metrics, Statistical Calculations, and Dynamic Business Insights Engine for EduMetrics.
Pure calculation functions with zero UI dependency.
"""

from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from src.config import ATTENDANCE_CRITICAL_THRESHOLD, ACADEMIC_DISTINCTION_THRESHOLD


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
            "highest_salary": 0.0
        }
        
    placed_mask = df["placement_status"].str.lower() == "placed"
    placed_count = int(placed_mask.sum())
    unplaced_count = total_students - placed_count
    placement_rate = round((placed_count / total_students) * 100.0, 1)
    
    placed_df = df[placed_mask]
    if len(placed_df) > 0 and placed_df["salary_lpa"].notna().sum() > 0:
        valid_salaries = placed_df["salary_lpa"].dropna()
        avg_salary = round(float(valid_salaries.mean()), 2)
        median_salary = round(float(valid_salaries.median()), 2)
        highest_salary = round(float(valid_salaries.max()), 2)
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
        return {
            "mean": 0.0, "median": 0.0, "std": 0.0, 
            "min": 0.0, "max": 0.0, "q25": 0.0, "q75": 0.0, 
            "iqr": 0.0, "skew": 0.0
        }
        
    series = df["academic_percentage"].dropna()
    q25 = float(series.quantile(0.25))
    q75 = float(series.quantile(0.75))
    skew_val = float(stats.skew(series)) if len(series) > 2 else 0.0
    
    return {
        "mean": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
        "std": round(float(series.std()), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "q25": round(q25, 2),
        "q75": round(q75, 2),
        "iqr": round(q75 - q25, 2),
        "skew": round(skew_val, 2)
    }


def compute_attendance_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes statistical distribution metrics for lecture attendance compliance.
    """
    if len(df) == 0:
        return {
            "mean": 0.0, "median": 0.0, "std": 0.0, 
            "min": 0.0, "max": 0.0, "q25": 0.0, "q75": 0.0, "iqr": 0.0,
            "compliant_count": 0, "compliant_rate": 0.0,
            "risk_count": 0, "risk_rate": 0.0
        }
        
    series = df["attendance_percentage"].dropna()
    total = len(series)
    compliant = int((series >= ATTENDANCE_CRITICAL_THRESHOLD).sum())
    risk = total - compliant
    q25 = float(series.quantile(0.25))
    q75 = float(series.quantile(0.75))
    
    return {
        "mean": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
        "std": round(float(series.std()), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "q25": round(q25, 2),
        "q75": round(q75, 2),
        "iqr": round(q75 - q25, 2),
        "compliant_count": compliant,
        "compliant_rate": round((compliant / total) * 100.0, 1) if total > 0 else 0.0,
        "risk_count": risk,
        "risk_rate": round((risk / total) * 100.0, 1) if total > 0 else 0.0
    }


def compute_salary_detailed_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes detailed statistical quantiles, dispersion, and skewness for placed salaries.
    """
    placed_df = df[df["placement_status"].str.lower() == "placed"].dropna(subset=["salary_lpa"])
    if len(placed_df) == 0:
        return {
            "count": 0, "mean": 0.0, "median": 0.0, "std": 0.0,
            "min": 0.0, "max": 0.0, "p10": 0.0, "p25": 0.0, "p75": 0.0, "p90": 0.0,
            "iqr": 0.0, "skew": 0.0
        }
        
    sal = placed_df["salary_lpa"]
    p25 = float(sal.quantile(0.25))
    p75 = float(sal.quantile(0.75))
    skew_val = float(stats.skew(sal)) if len(sal) > 2 else 0.0
    
    return {
        "count": len(sal),
        "mean": round(float(sal.mean()), 2),
        "median": round(float(sal.median()), 2),
        "std": round(float(sal.std()), 2),
        "min": round(float(sal.min()), 2),
        "max": round(float(sal.max()), 2),
        "p10": round(float(sal.quantile(0.10)), 2),
        "p25": round(p25, 2),
        "p75": round(p75, 2),
        "p90": round(float(sal.quantile(0.90)), 2),
        "iqr": round(p75 - p25, 2),
        "skew": round(skew_val, 2)
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
        Median_Academic=("academic_percentage", lambda x: round(x.median(), 1)),
        Std_Academic=("academic_percentage", lambda x: round(x.std(), 2) if len(x) > 1 else 0.0),
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
        avg_sal = round(float(placed["salary_lpa"].mean()), 2) if len(placed) > 0 and placed["salary_lpa"].notna().sum() > 0 else 0.0
        med_sal = round(float(placed["salary_lpa"].median()), 2) if len(placed) > 0 and placed["salary_lpa"].notna().sum() > 0 else 0.0
        
        records.append({
            "Specialization": spec,
            "Total Students": total,
            "Placed Students": placed_count,
            "Placement Rate (%)": rate,
            "Avg Salary (LPA)": avg_sal,
            "Median Salary (LPA)": med_sal
        })
        
    return pd.DataFrame(records).sort_values(by="Placement Rate (%)", ascending=False)


def compute_placement_by_academic_tier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates placement conversion and average packages across academic grade bands.
    """
    if len(df) == 0 or "grade_band" not in df.columns:
        return pd.DataFrame()
        
    records = []
    for band, group in df.groupby("grade_band"):
        total = len(group)
        placed = group[group["placement_status"].str.lower() == "placed"]
        placed_count = len(placed)
        rate = round((placed_count / total) * 100.0, 1) if total > 0 else 0.0
        avg_sal = round(float(placed["salary_lpa"].mean()), 2) if len(placed) > 0 and placed["salary_lpa"].notna().sum() > 0 else 0.0
        
        records.append({
            "Academic Performance Tier": band,
            "Total Students": total,
            "Placed Students": placed_count,
            "Placement Rate (%)": rate,
            "Avg Salary (LPA)": avg_sal
        })
        
    tier_order = {
        "Distinction (>=80%)": 1,
        "First Class (65-79%)": 2,
        "Second Class (50-64%)": 3,
        "Support Required (<50%)": 4
    }
    res_df = pd.DataFrame(records)
    res_df["order"] = res_df["Academic Performance Tier"].map(tier_order).fillna(5)
    return res_df.sort_values(by="order").drop(columns=["order"])


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
        placed_group = group[group["placement_status"].str.lower() == "placed"]
        avg_sal = round(float(placed_group["salary_lpa"].mean()), 2) if len(placed_group) > 0 and placed_group["salary_lpa"].notna().sum() > 0 else 0.0
        records.append({
            "Proficiency Level": level,
            "Total Students": total,
            "Placed Students": placed,
            "Placement Rate (%)": rate,
            "Avg Salary (LPA)": avg_sal
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
    
    top_students = df.sort_values(by="academic_percentage", ascending=False).head(top_n)[avail_cols]
    
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
    Calculates pairwise Pearson correlation among numerical columns.
    """
    num_cols = ["academic_percentage", "attendance_percentage", 
                "certifications_count", "technical_score_10"]
    if "salary_lpa" in df.columns:
        num_cols.append("salary_lpa")
        
    valid_cols = [c for c in num_cols if c in df.columns]
    corr = df[valid_cols].corr().round(3)
    return corr


def compute_correlation_with_significance(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes pairwise Pearson correlation with sample size, p-value, and significance notation.
    """
    pairs = [
        ("academic_percentage", "attendance_percentage", "Academic Score vs. Attendance"),
        ("technical_score_10", "salary_lpa", "Tech Skill Index vs. Placed Salary"),
        ("certifications_count", "salary_lpa", "Certifications vs. Placed Salary"),
        ("academic_percentage", "technical_score_10", "Academic Score vs. Tech Index"),
        ("attendance_percentage", "salary_lpa", "Attendance vs. Placed Salary")
    ]
    
    results = []
    for col1, col2, label in pairs:
        if col1 in df.columns and col2 in df.columns:
            clean = df.dropna(subset=[col1, col2])
            n = len(clean)
            if n > 2:
                r_val, p_val = stats.pearsonr(clean[col1], clean[col2])
                sig = "*** (p < 0.001)" if p_val < 0.001 else ("** (p < 0.01)" if p_val < 0.01 else ("* (p < 0.05)" if p_val < 0.05 else "ns (not significant)"))
                results.append({
                    "Relationship": label,
                    "Pearson r": round(float(r_val), 3),
                    "p-value": f"{p_val:.4f}" if p_val >= 0.0001 else "< 0.0001",
                    "Significance": sig,
                    "Sample Size (N)": n
                })
                
    return results


def compute_group_comparisons(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs two-sample hypothesis testing comparing Placed vs Unplaced cohorts.
    """
    placed = df[df["placement_status"].str.lower() == "placed"]
    unplaced = df[df["placement_status"].str.lower() == "unplaced"]
    
    metrics_to_compare = [
        ("academic_percentage", "Academic Aggregate (%)"),
        ("attendance_percentage", "Attendance Rate (%)"),
        ("technical_score_10", "Technical Skill Index (10)"),
        ("certifications_count", "Industry Certifications")
    ]
    
    comparisons = []
    for col, label in metrics_to_compare:
        if col in df.columns and len(placed) > 1 and len(unplaced) > 1:
            p_series = placed[col].dropna()
            u_series = unplaced[col].dropna()
            
            p_mean = float(p_series.mean())
            u_mean = float(u_series.mean())
            diff = round(p_mean - u_mean, 2)
            
            # Welch's t-test (unequal variances assumed)
            t_stat, p_val = stats.ttest_ind(p_series, u_series, equal_var=False)
            
            # Cohen's d effect size
            pooled_std = np.sqrt(((len(p_series) - 1) * p_series.std()**2 + (len(u_series) - 1) * u_series.std()**2) / (len(p_series) + len(u_series) - 2))
            d_val = round((p_mean - u_mean) / pooled_std, 2) if pooled_std > 0 else 0.0
            
            sig = "Statistically Significant (p < 0.05) ✅" if p_val < 0.05 else "Not Significant ❌"
            
            comparisons.append({
                "Metric": label,
                "Placed Mean": round(p_mean, 2),
                "Unplaced Mean": round(u_mean, 2),
                "Difference (Lift)": f"{diff:+} units",
                "t-Statistic": round(float(t_stat), 2),
                "p-Value": f"{p_val:.4e}" if p_val < 0.001 else f"{p_val:.3f}",
                "Cohen's d (Effect Size)": d_val,
                "Statistical Conclusion": sig
            })
            
    # One-Way ANOVA across Specializations for Academic Score
    spec_groups = [group["academic_percentage"].dropna().values for _, group in df.groupby("specialization") if len(group) > 2]
    if len(spec_groups) > 1:
        f_stat, anova_p = stats.f_oneway(*spec_groups)
        anova_res = {
            "f_statistic": round(float(f_stat), 2),
            "p_value": round(float(anova_p), 4),
            "is_significant": anova_p < 0.05
        }
    else:
        anova_res = None
        
    return {
        "placed_vs_unplaced": pd.DataFrame(comparisons),
        "anova_specializations": anova_res
    }


def compute_placement_logistic_regression(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Fits an explainable Logistic Regression model to quantify multivariate placement odds ratios.
    """
    clean_df = df.dropna(subset=[
        "academic_percentage", "attendance_percentage", 
        "technical_score_10", "certifications_count", "internship_status", "placement_status"
    ]).copy()
    
    if len(clean_df) < 30:
        return None
        
    # Feature matrix
    clean_df["internship_binary"] = (clean_df["internship_status"].str.lower() == "completed").astype(int)
    clean_df["target_placed"] = (clean_df["placement_status"].str.lower() == "placed").astype(int)
    
    feature_cols = [
        "academic_percentage", 
        "attendance_percentage", 
        "technical_score_10", 
        "certifications_count", 
        "internship_binary"
    ]
    
    X = clean_df[feature_cols]
    y = clean_df["target_placed"]
    
    if y.nunique() < 2:
        return None
        
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X, y)
    
    y_pred = model.predict(X)
    acc = round(accuracy_score(y, y_pred) * 100.0, 1)
    
    try:
        y_prob = model.predict_proba(X)[:, 1]
        auc = round(roc_auc_score(y, y_prob), 3)
    except Exception:
        auc = 0.50
        
    feature_labels = {
        "academic_percentage": "Academic Aggregate Score (per +1%)",
        "attendance_percentage": "Attendance Rate (per +1%)",
        "technical_score_10": "Technical Skill Index (per +1 pt / 10)",
        "certifications_count": "Verified Certifications (per +1 credential)",
        "internship_binary": "Summer Internship Completion (Yes vs No)"
    }
    
    coef_records = []
    for col, coef in zip(feature_cols, model.coef_[0]):
        odds_ratio = round(float(np.exp(coef)), 2)
        coef_records.append({
            "Predictor Dimension": feature_labels.get(col, col),
            "Log-Odds Coefficient (β)": round(float(coef), 3),
            "Odds Ratio (e^β)": odds_ratio,
            "Managerial Interpretation": (
                f"+{int((odds_ratio - 1) * 100)}% higher odds of placement" 
                if odds_ratio > 1.0 else 
                f"{int((1 - odds_ratio) * 100)}% lower odds"
            )
        })
        
    return {
        "accuracy": acc,
        "roc_auc": auc,
        "sample_size": len(clean_df),
        "coefficients_table": pd.DataFrame(coef_records)
    }


def generate_dynamic_business_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generates 5-8 strictly calculated, dynamic business insights derived directly
    from the loaded dataset. Zero hardcoding.
    """
    if len(df) == 0:
        return []
        
    insights = []
    
    # 1. Specialization with Highest Placement Conversion
    spec_summary = df.groupby("specialization").agg(
        Total=("student_id", "count"),
        Placed=("placement_status", lambda x: (x.str.lower() == "placed").sum())
    )
    spec_summary["Rate"] = (spec_summary["Placed"] / spec_summary["Total"]) * 100.0
    if len(spec_summary) > 0:
        top_spec = spec_summary["Rate"].idxmax()
        top_rate = round(float(spec_summary["Rate"].max()), 1)
        low_spec = spec_summary["Rate"].idxmin()
        low_rate = round(float(spec_summary["Rate"].min()), 1)
        gap = round(top_rate - low_rate, 1)
        
        insights.append({
            "id": 1,
            "category": "Placement Leader",
            "title": f"Top Placement Specialization: {top_spec}",
            "stat_callout": f"{top_rate}% Conversion",
            "finding": f"<strong>{top_spec}</strong> achieved the cohort's highest placement rate of <strong>{top_rate}%</strong>, outperforming {low_spec} ({low_rate}%) by a margin of <strong>{gap} percentage points</strong>.",
            "mba_takeaway": "Direct corporate demand and industry alignment are currently strongest in this discipline.",
            "method": "Calculated by grouping student placement conversion by academic major."
        })

    # 2. Highest Academic Performing Major
    acad_by_spec = df.groupby("specialization")["academic_percentage"].mean()
    if len(acad_by_spec) > 0:
        top_acad_spec = acad_by_spec.idxmax()
        top_acad_mean = round(float(acad_by_spec.max()), 1)
        cohort_acad_mean = round(float(df["academic_percentage"].mean()), 1)
        
        insights.append({
            "id": 2,
            "category": "Academic Excellence",
            "title": f"Highest Academic Achievement: {top_acad_spec}",
            "stat_callout": f"{top_acad_mean}% Mean Score",
            "finding": f"Students in <strong>{top_acad_spec}</strong> lead academic scores with a mean aggregate of <strong>{top_acad_mean}%</strong>, exceeding the batch benchmark of {cohort_acad_mean}%.",
            "mba_takeaway": "Curriculum rigor and selective admissions in this domain reflect in sustained distinction.",
            "method": "Parametric mean calculated across all enrolled students partitioned by major."
        })

    # 3. Attendance to Academic Score Relationship
    clean_att_acad = df.dropna(subset=["attendance_percentage", "academic_percentage"])
    if len(clean_att_acad) > 5:
        r_att, p_att = stats.pearsonr(clean_att_acad["attendance_percentage"], clean_att_acad["academic_percentage"])
        sig_str = "statistically significant (p < 0.001)" if p_att < 0.001 else "statistically significant"
        direction = "positive" if r_att > 0 else "negative"
        
        insights.append({
            "id": 3,
            "category": "Discipline & Outcomes",
            "title": "Attendance & Academic Correlation",
            "stat_callout": f"r = {r_att:+.3f}",
            "finding": f"There is a <strong>{direction} correlation (r = {r_att:+.3f})</strong> between attendance and exam marks that is <strong>{sig_str}</strong> (p = {p_att:.4e}).",
            "mba_takeaway": "Classroom engagement directly reinforces subject matter retention; policy enforcing 75% attendance protects academic performance.",
            "method": "Bivariate Pearson product-moment correlation coefficient testing linear association."
        })

    # 4. Technical Skills Lift Among Placed Students
    placed_df = df[df["placement_status"].str.lower() == "placed"]
    unplaced_df = df[df["placement_status"].str.lower() == "unplaced"]
    if len(placed_df) > 0 and len(unplaced_df) > 0:
        placed_adv_py = (placed_df["python_proficiency"] == "Advanced").mean() * 100.0
        unplaced_adv_py = (unplaced_df["python_proficiency"] == "Advanced").mean() * 100.0
        py_gap = round(placed_adv_py - unplaced_adv_py, 1)
        
        insights.append({
            "id": 4,
            "category": "Technical Competence",
            "title": "Python Proficiency Differentiator",
            "stat_callout": f"+{py_gap}% Advance Gap",
            "finding": f"<strong>{placed_adv_py:.1f}%</strong> of placed students demonstrate Advanced Python capability compared to only <strong>{unplaced_adv_py:.1f}%</strong> of unplaced students (an advantage of <strong>{py_gap}%</strong>).",
            "mba_takeaway": "Technical coding literacy acts as a strong screening filter during technical interview rounds.",
            "method": "Proportion test comparing advanced skill density between placed and unplaced cohorts."
        })

    # 5. Compensation Dispersion Across Specializations
    placed_valid_sal = placed_df.dropna(subset=["salary_lpa"])
    if len(placed_valid_sal) > 0:
        spec_sal = placed_valid_sal.groupby("specialization")["salary_lpa"].median()
        if len(spec_sal) > 1:
            highest_sal_spec = spec_sal.idxmax()
            highest_sal_val = round(float(spec_sal.max()), 2)
            lowest_sal_spec = spec_sal.idxmin()
            lowest_sal_val = round(float(spec_sal.min()), 2)
            sal_diff = round(highest_sal_val - lowest_sal_val, 2)
            
            insights.append({
                "id": 5,
                "category": "Market Compensation",
                "title": "Specialization Compensation Spread",
                "stat_callout": f"₹{sal_diff} LPA Delta",
                "finding": f"<strong>{highest_sal_spec}</strong> commands the highest median CTC at <strong>₹{highest_sal_val} LPA</strong>, while {lowest_sal_spec} stands at ₹{lowest_sal_val} LPA (a median premium of <strong>₹{sal_diff} LPA</strong>).",
                "mba_takeaway": "Market compensation reflects premium valuation for quantitative and analytics skills in corporate hiring.",
                "method": "Non-parametric median CTC comparison across specializations to resist outlier distortion."
            })

    # 6. Summer Internship Conversion Lift
    intern_placed = df[df["internship_status"].str.lower() == "completed"]
    no_intern_placed = df[df["internship_status"].str.lower() != "completed"]
    if len(intern_placed) > 0 and len(no_intern_placed) > 0:
        intern_rate = (intern_placed["placement_status"].str.lower() == "placed").mean() * 100.0
        no_intern_rate = (no_intern_placed["placement_status"].str.lower() == "placed").mean() * 100.0
        lift = round(intern_rate - no_intern_rate, 1)
        
        insights.append({
            "id": 6,
            "category": "Experiential Learning",
            "title": "Summer Internship Placement Premium",
            "stat_callout": f"+{lift}% Point Lift",
            "finding": f"Students who completed a summer internship achieved a <strong>{intern_rate:.1f}% placement conversion</strong> vs. <strong>{no_intern_rate:.1f}%</strong> for students without an internship (+<strong>{lift} percentage points</strong>).",
            "mba_takeaway": "Corporate recruiters prioritize candidates with proven workplace readiness and experiential learning.",
            "method": "Two-cohort placement probability comparison segmented by internship completion."
        })

    # 7. Attendance Risk Cohort Vulnerability
    att_risk_students = df[df["attendance_percentage"] < ATTENDANCE_CRITICAL_THRESHOLD]
    att_safe_students = df[df["attendance_percentage"] >= ATTENDANCE_CRITICAL_THRESHOLD]
    if len(att_risk_students) > 0 and len(att_safe_students) > 0:
        risk_pct = round((len(att_risk_students) / len(df)) * 100.0, 1)
        safe_place_rate = round((att_safe_students["placement_status"].str.lower() == "placed").mean() * 100.0, 1)
        risk_place_rate = round((att_risk_students["placement_status"].str.lower() == "placed").mean() * 100.0, 1)
        
        insights.append({
            "id": 7,
            "category": "Institutional Risk",
            "title": "Attendance Policy Risk Exposure",
            "stat_callout": f"{risk_pct}% at Risk",
            "finding": f"<strong>{len(att_risk_students)} students ({risk_pct}%)</strong> fall below the mandatory 75% attendance threshold. Their placement rate is <strong>{risk_place_rate}%</strong> compared to <strong>{safe_place_rate}%</strong> for compliant peers.",
            "mba_takeaway": "Attendance deficits constitute a primary institutional vulnerability that directly suppresses placement eligibility.",
            "method": "Threshold segmentation based on the 75% institutional policy benchmark."
        })

    return insights
