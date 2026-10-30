"""
SQLite Database Layer for EduMetrics.
Manages relational storage, ingestion, and querying for students and placements.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional
from src.config import DB_PATH, DATABASE_DIR


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Returns a SQLite connection object with foreign keys enabled."""
    target_path = db_path or DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Creates the SQLite database schema if not already initialized."""
    schema_path = DATABASE_DIR / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Database schema file not found at {schema_path}")
        
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    conn = get_connection(db_path)
    with conn:
        conn.executescript(schema_sql)
    conn.close()


def save_dataframe_to_db(df: pd.DataFrame, db_path: Optional[Path] = None) -> int:
    """
    Ingests a complete student dataframe into SQLite tables (students + placements).
    Replaces existing records transactionally.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    
    # Prepare master students table data
    student_cols = [
        "student_id", "student_name", "gender", "specialization", 
        "semester", "academic_percentage", "attendance_percentage", 
        "sql_proficiency", "python_proficiency", "power_bi_proficiency", 
        "certifications_count", "internship_status"
    ]
    students_df = df[[c for c in student_cols if c in df.columns]].drop_duplicates(subset=["student_id"])
    
    # Prepare placements table data
    placement_cols = ["student_id", "placement_status", "company", "salary_lpa"]
    placements_df = df[[c for c in placement_cols if c in df.columns]].drop_duplicates(subset=["student_id"])
    
    with conn:
        # Clear existing
        conn.execute("DELETE FROM placements;")
        conn.execute("DELETE FROM students;")
        
        # Insert master students
        students_df.to_sql("students", conn, if_exists="append", index=False)
        # Insert placements
        placements_df.to_sql("placements", conn, if_exists="append", index=False)
        
    conn.close()
    return len(students_df)


def load_data_from_db(db_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Reads joined student and placement data from SQLite.
    """
    target_path = db_path or DB_PATH
    if not target_path.exists():
        return pd.DataFrame()
        
    conn = get_connection(target_path)
    query = """
    SELECT 
        s.student_id,
        s.student_name,
        s.gender,
        s.specialization,
        s.semester,
        s.academic_percentage,
        s.attendance_percentage,
        s.sql_proficiency,
        s.python_proficiency,
        s.power_bi_proficiency,
        s.certifications_count,
        s.internship_status,
        p.placement_status,
        p.company,
        p.salary_lpa
    FROM students s
    LEFT JOIN placements p ON s.student_id = p.student_id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
