"""
SQLite Database Layer for EduMetrics.
Manages relational storage, 3NF normalized tables (students, academic_records, skills, placements),
automatic initialization, data ingestion, and analytical SQL queries.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from src.config import DB_PATH, DATABASE_DIR, DEFAULT_CSV_PATH


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
    Ingests student records across 4 normalized 3NF tables:
    1. students
    2. academic_records
    3. skills
    4. placements
    Replaces existing records transactionally.
    """
    if df is None or len(df) == 0:
        return 0
        
    init_db(db_path)
    conn = get_connection(db_path)
    
    # Ensure analytical helper columns exist
    df_clean = df.copy()
    if "grade_band" not in df_clean.columns or "technical_score_10" not in df_clean.columns:
        from src.data_loader import clean_and_enrich_data
        df_clean = clean_and_enrich_data(df_clean)
        
    # Table 1: Master Students
    student_cols = ["student_id", "student_name", "gender", "specialization", "semester"]
    students_df = df_clean[student_cols].drop_duplicates(subset=["student_id"])
    
    # Table 2: Academic Records
    acad_cols = ["student_id", "academic_percentage", "attendance_percentage", "grade_band", "attendance_band"]
    academic_df = df_clean[acad_cols].drop_duplicates(subset=["student_id"])
    
    # Table 3: Skills
    skill_cols = [
        "student_id", "sql_proficiency", "python_proficiency", 
        "power_bi_proficiency", "certifications_count", "internship_status", "technical_score_10"
    ]
    skills_df = df_clean[skill_cols].drop_duplicates(subset=["student_id"])
    
    # Table 4: Placements
    placement_cols = ["student_id", "placement_status", "company", "salary_lpa"]
    placements_df = df_clean[placement_cols].drop_duplicates(subset=["student_id"])
    
    with conn:
        # Atomic clear in child-to-parent order to respect foreign keys
        conn.execute("DELETE FROM placements;")
        conn.execute("DELETE FROM skills;")
        conn.execute("DELETE FROM academic_records;")
        conn.execute("DELETE FROM students;")
        
        # Insert across all 4 relational tables
        students_df.to_sql("students", conn, if_exists="append", index=False)
        academic_df.to_sql("academic_records", conn, if_exists="append", index=False)
        skills_df.to_sql("skills", conn, if_exists="append", index=False)
        placements_df.to_sql("placements", conn, if_exists="append", index=False)
        
    conn.close()
    return len(students_df)


def load_data_from_db(db_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Reads complete joined student records across all 4 relational tables from SQLite.
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
        a.academic_percentage,
        a.attendance_percentage,
        a.grade_band,
        a.attendance_band,
        sk.sql_proficiency,
        sk.python_proficiency,
        sk.power_bi_proficiency,
        sk.certifications_count,
        sk.internship_status,
        sk.technical_score_10,
        p.placement_status,
        p.company,
        p.salary_lpa
    FROM students s
    JOIN academic_records a ON s.student_id = a.student_id
    JOIN skills sk ON s.student_id = sk.student_id
    JOIN placements p ON s.student_id = p.student_id
    ORDER BY s.student_id ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def ensure_database_initialized(db_path: Optional[Path] = None) -> None:
    """
    Checks if SQLite database exists and is populated.
    If not, automatically initializes schema and seeds data from the synthetic CSV.
    """
    target_path = db_path or DB_PATH
    needs_seeding = False
    
    if not target_path.exists():
        needs_seeding = True
    else:
        conn = get_connection(target_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM students;")
            count = cursor.fetchone()[0]
            if count == 0:
                needs_seeding = True
        except Exception:
            needs_seeding = True
        finally:
            conn.close()
            
    if needs_seeding:
        from src.data_generator import ensure_default_dataset
        df = ensure_default_dataset()
        save_dataframe_to_db(df, db_path=target_path)


# ====================================================================
# Parameterized Analytical SQL Queries
# ====================================================================

def query_total_students_by_specialization(conn: sqlite3.Connection) -> Tuple[str, pd.DataFrame]:
    """1. Total students by specialization."""
    sql = """
    SELECT 
        specialization AS "Specialization", 
        COUNT(student_id) AS "Total Students",
        ROUND(100.0 * COUNT(student_id) / (SELECT COUNT(*) FROM students), 1) AS "Cohort Share (%)"
    FROM students
    GROUP BY specialization
    ORDER BY "Total Students" DESC;
    """
    return sql, pd.read_sql_query(sql, conn)


def query_avg_academic_score_by_specialization(conn: sqlite3.Connection) -> Tuple[str, pd.DataFrame]:
    """2. Average academic score by specialization."""
    sql = """
    SELECT 
        s.specialization AS "Specialization", 
        ROUND(AVG(a.academic_percentage), 2) AS "Mean Marks (%)",
        ROUND(MIN(a.academic_percentage), 2) AS "Min Marks (%)",
        ROUND(MAX(a.academic_percentage), 2) AS "Max Marks (%)",
        COUNT(s.student_id) AS "Students Evaluated"
    FROM students s
    JOIN academic_records a ON s.student_id = a.student_id
    GROUP BY s.specialization
    ORDER BY "Mean Marks (%)" DESC;
    """
    return sql, pd.read_sql_query(sql, conn)


def query_placement_rate_by_specialization(conn: sqlite3.Connection) -> Tuple[str, pd.DataFrame]:
    """3. Placement rate by specialization."""
    sql = """
    SELECT 
        s.specialization AS "Specialization",
        COUNT(s.student_id) AS "Enrolled Students",
        SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) AS "Placed Students",
        ROUND(100.0 * SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) / COUNT(s.student_id), 1) AS "Placement Rate (%)"
    FROM students s
    JOIN placements p ON s.student_id = p.student_id
    GROUP BY s.specialization
    ORDER BY "Placement Rate (%)" DESC;
    """
    return sql, pd.read_sql_query(sql, conn)


def query_avg_salary_by_specialization(conn: sqlite3.Connection) -> Tuple[str, pd.DataFrame]:
    """4. Average salary by specialization."""
    sql = """
    SELECT 
        s.specialization AS "Specialization",
        COUNT(p.salary_lpa) AS "Placed Students Count",
        ROUND(AVG(p.salary_lpa), 2) AS "Average Package (₹ LPA)",
        ROUND(MIN(p.salary_lpa), 2) AS "Min Offer (₹ LPA)",
        ROUND(MAX(p.salary_lpa), 2) AS "Top Offer (₹ LPA)"
    FROM students s
    JOIN placements p ON s.student_id = p.student_id
    WHERE LOWER(p.placement_status) = 'placed' AND p.salary_lpa IS NOT NULL
    GROUP BY s.specialization
    ORDER BY "Average Package (₹ LPA)" DESC;
    """
    return sql, pd.read_sql_query(sql, conn)


def query_placed_vs_unplaced_counts(conn: sqlite3.Connection) -> Tuple[str, pd.DataFrame]:
    """5. Number of placed and unplaced students."""
    sql = """
    SELECT 
        p.placement_status AS "Placement Status",
        COUNT(p.student_id) AS "Student Count",
        ROUND(100.0 * COUNT(p.student_id) / (SELECT COUNT(*) FROM placements), 1) AS "Proportion (%)"
    FROM placements p
    GROUP BY p.placement_status;
    """
    return sql, pd.read_sql_query(sql, conn)


def query_students_below_attendance(conn: sqlite3.Connection, threshold: float = 75.0) -> Tuple[str, pd.DataFrame]:
    """6. Parameterized query: Students with attendance below a selected threshold."""
    sql = """
    SELECT 
        s.student_id AS "Student ID",
        s.student_name AS "Student Name",
        s.specialization AS "Specialization",
        ROUND(a.attendance_percentage, 1) AS "Attendance (%)",
        ROUND(a.academic_percentage, 1) AS "Marks (%)",
        p.placement_status AS "Placement Status"
    FROM students s
    JOIN academic_records a ON s.student_id = a.student_id
    JOIN placements p ON s.student_id = p.student_id
    WHERE a.attendance_percentage < ?
    ORDER BY a.attendance_percentage ASC;
    """
    return sql, pd.read_sql_query(sql, conn, params=(threshold,))


def query_skill_placement_comparison(conn: sqlite3.Connection, skill_name: str = "python_proficiency") -> Tuple[str, pd.DataFrame]:
    """7. Parameterized query: Skill-wise placement comparisons."""
    valid_skills = {"python_proficiency", "sql_proficiency", "power_bi_proficiency"}
    if skill_name not in valid_skills:
        skill_name = "python_proficiency"
        
    sql = f"""
    SELECT 
        sk.{skill_name} AS "Proficiency Level",
        COUNT(sk.student_id) AS "Total Candidates",
        SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) AS "Placed Count",
        ROUND(100.0 * SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) / COUNT(sk.student_id), 1) AS "Placement Rate (%)",
        ROUND(AVG(CASE WHEN LOWER(p.placement_status) = 'placed' THEN p.salary_lpa END), 2) AS "Mean Package (₹ LPA)"
    FROM skills sk
    JOIN placements p ON sk.student_id = p.student_id
    GROUP BY sk.{skill_name}
    ORDER BY CASE sk.{skill_name} 
        WHEN 'Beginner' THEN 1 
        WHEN 'Intermediate' THEN 2 
        WHEN 'Advanced' THEN 3 
        ELSE 4 
    END;
    """
    return sql, pd.read_sql_query(sql, conn)
