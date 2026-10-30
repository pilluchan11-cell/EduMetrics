"""
Synthetic student dataset generator for EduMetrics.
Generates realistic, reproducible fictional student records for academic analytics.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from src.config import (
    DEFAULT_CSV_PATH,
    SPECIALIZATIONS,
    SEMESTERS,
    PROFICIENCY_LEVELS,
    COMPANIES
)

FIRST_NAMES_MALE = [
    "Aarav", "Aditya", "Arjun", "Dhruv", "Ishaan", "Kabir", "Manav", "Neil",
    "Pranav", "Rohan", "Samar", "Tanay", "Utkarsh", "Varun", "Vivaan", "Yash"
]
FIRST_NAMES_FEMALE = [
    "Ananya", "Diya", "Isha", "Kavya", "Meera", "Navya", "Pooja", "Rhea",
    "Saanvi", "Tara", "Trisha", "Vaidehi", "Zoya", "Aaliyah", "Sneha", "Kritika"
]
FIRST_NAMES_NB = [
    "Alex", "Jordan", "Morgan", "Taylor", "Sam", "Arya", "Devan", "Kiran"
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Iyer", "Mehta", "Nair", "Reddy", "Chopra",
    "Gupta", "Deshmukh", "Bose", "Kulkarni", "Malhotra", "Kapoor", "Chatterjee", "Rao"
]


def generate_synthetic_data(n: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic, synthetic dataset of fictional students.
    
    Args:
        n (int): Number of fictional student records to create (default 500).
        seed (int): Random seed for reproducibility (default 42).
        
    Returns:
        pd.DataFrame: Formatted DataFrame with clean synthetic student data.
    """
    np.random.seed(seed)
    
    records = []
    
    # Proficiency weights: Beginner: 30%, Intermediate: 50%, Advanced: 20%
    prof_weights = [0.30, 0.50, 0.20]
    prof_score_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    
    for i in range(1, n + 1):
        student_id = f"EDU-2026-{i:03d}"
        
        # Demographic assignment (purely synthetic; not used for consequential decisions)
        gender_rand = np.random.rand()
        if gender_rand < 0.48:
            gender = "Female"
            first_name = np.random.choice(FIRST_NAMES_FEMALE)
        elif gender_rand < 0.96:
            gender = "Male"
            first_name = np.random.choice(FIRST_NAMES_MALE)
        else:
            gender = "Non-Binary"
            first_name = np.random.choice(FIRST_NAMES_NB)
            
        last_name = np.random.choice(LAST_NAMES)
        student_name = f"{first_name} {last_name}"
        
        specialization = np.random.choice(SPECIALIZATIONS)
        semester = np.random.choice(SEMESTERS, p=[0.15, 0.20, 0.35, 0.30])
        
        # Academic score (percentage): Normal distribution around 73%, std 9.5%
        academic_score = float(np.clip(np.random.normal(73.0, 9.5), 46.0, 98.5))
        
        # Attendance percentage: Correlated weakly with academic score
        base_att = np.random.normal(81.0, 8.5) + (academic_score - 73.0) * 0.25
        attendance = float(np.clip(base_att, 52.0, 99.5))
        
        # Technical skill proficiencies
        # Business Analytics & Finance have higher odds for Advanced SQL / Python
        if specialization in ["Business Analytics", "Finance"]:
            sql_prof = np.random.choice(PROFICIENCY_LEVELS, p=[0.20, 0.48, 0.32])
            py_prof = np.random.choice(PROFICIENCY_LEVELS, p=[0.22, 0.48, 0.30])
            bi_prof = np.random.choice(PROFICIENCY_LEVELS, p=[0.20, 0.50, 0.30])
        else:
            sql_prof = np.random.choice(PROFICIENCY_LEVELS, p=prof_weights)
            py_prof = np.random.choice(PROFICIENCY_LEVELS, p=prof_weights)
            bi_prof = np.random.choice(PROFICIENCY_LEVELS, p=prof_weights)
            
        # Certifications count: Poisson distribution (mean 1.8), clipped [0, 5]
        certs = int(np.clip(np.random.poisson(1.8), 0, 5))
        
        # Internship completion status (approx 70% completed)
        intern_prob = 0.50 + (academic_score / 200.0)
        internship_status = "Completed" if np.random.rand() < intern_prob else "Not Completed"
        
        # Logistic placement probability calculation
        # Normalized features
        acad_norm = (academic_score - 50.0) / 50.0  # Range ~ 0 to 1
        att_norm = (attendance - 50.0) / 50.0       # Range ~ 0 to 1
        skills_score = (
            prof_score_map[sql_prof] + 
            prof_score_map[py_prof] + 
            prof_score_map[bi_prof]
        ) / 9.0  # Range ~ 0.33 to 1.0
        intern_val = 1.0 if internship_status == "Completed" else 0.0
        certs_norm = certs / 5.0
        
        # Log-odds formula
        z = (
            -2.4 
            + 2.2 * acad_norm 
            + 1.4 * att_norm 
            + 2.0 * skills_score 
            + 1.2 * intern_val 
            + 0.8 * certs_norm 
            + np.random.normal(0, 0.4)
        )
        placement_prob = 1.0 / (1.0 + np.exp(-z))
        
        # In earlier semesters (Sem 1 and Sem 2), students are mostly in pre-placement stages,
        # but for an analytics dashboard demonstrating full cohort metrics, Sem 3 & Sem 4
        # participate in campus placement drives.
        if semester in ["Semester 1", "Semester 2"]:
            # Some pre-placement offers or preparing
            is_placed = placement_prob > 0.65
        else:
            is_placed = placement_prob > 0.45
            
        placement_status = "Placed" if is_placed else "Unplaced"
        
        if is_placed:
            company = np.random.choice(COMPANIES)
            # Base salary around 6.5 LPA + increments for academic excellence and advanced skills
            base_salary = 6.2 + (academic_score - 50.0) * 0.12 + skills_score * 3.5 + certs * 0.6
            salary_noise = np.random.lognormal(mean=0.0, sigma=0.18)
            salary_lpa = float(np.round(np.clip(base_salary * salary_noise, 5.5, 26.5), 2))
        else:
            company = None
            salary_lpa = np.nan
            
        records.append({
            "student_id": student_id,
            "student_name": student_name,
            "gender": gender,
            "specialization": specialization,
            "semester": semester,
            "academic_percentage": round(academic_score, 2),
            "attendance_percentage": round(attendance, 2),
            "sql_proficiency": sql_prof,
            "python_proficiency": py_prof,
            "power_bi_proficiency": bi_prof,
            "certifications_count": certs,
            "internship_status": internship_status,
            "placement_status": placement_status,
            "company": company,
            "salary_lpa": salary_lpa
        })
        
    df = pd.DataFrame(records)
    return df


def ensure_default_dataset() -> pd.DataFrame:
    """
    Ensures that the default synthetic dataset exists on disk;
    generates and saves it if not already present.
    """
    DEFAULT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DEFAULT_CSV_PATH.exists():
        df = generate_synthetic_data(n=500, seed=42)
        df.to_csv(DEFAULT_CSV_PATH, index=False)
        return df
    return pd.read_csv(DEFAULT_CSV_PATH)


if __name__ == "__main__":
    df = ensure_default_dataset()
    print(f"Generated {len(df)} records. Sample:\n", df.head())
