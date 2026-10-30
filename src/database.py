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


def ensure_assessments_table(conn: sqlite3.Connection) -> None:
    """Creates the student_assessments table if not already present."""
    create_sql = """
    CREATE TABLE IF NOT EXISTS student_assessments (
        assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        student_name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        semester TEXT NOT NULL,
        target_role TEXT NOT NULL,
        academic_percentage REAL NOT NULL,
        attendance_percentage REAL NOT NULL,
        overall_readiness_score REAL NOT NULL,
        tier_label TEXT NOT NULL,
        technical_fit_percentage REAL NOT NULL,
        certifications_count INTEGER NOT NULL DEFAULT 0,
        internship_status TEXT NOT NULL,
        projects_count INTEGER NOT NULL DEFAULT 0,
        assessment_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_assessment_student ON student_assessments(student_id);
    """
    with conn:
        conn.executescript(create_sql)


def save_assessment_record(assessment_result: Dict[str, Any], conn: Optional[sqlite3.Connection] = None) -> int:
    """
    Persists a completed student assessment into SQLite using parameterized queries.
    Returns the newly inserted assessment_id.
    """
    import json
    close_at_end = False
    if conn is None:
        conn = get_connection()
        close_at_end = True
        
    ensure_assessments_table(conn)
    
    student = assessment_result.get("student_data", {})
    target_role = assessment_result.get("target_role", "Data Analyst")
    readiness = assessment_result.get("readiness", {})
    gap_analysis = readiness.get("gap_analysis", {})
    
    # Extract scalar fields
    student_id = str(student.get("student_id", "")).strip()
    student_name = str(student.get("student_name", "")).strip()
    specialization = str(student.get("specialization", "")).strip()
    semester = str(student.get("semester", "")).strip()
    acad_pct = float(student.get("academic_percentage", 0.0))
    att_pct = float(student.get("attendance_percentage", 0.0))
    overall_score = float(readiness.get("overall_score", 0.0))
    tier_label = str(readiness.get("tier_label", "Developing"))
    tech_fit = float(gap_analysis.get("fit_percentage", 0.0))
    certs_count = len(student.get("certifications", []))
    internship = str(student.get("internship_status", "Not Completed"))
    projects_count = int(student.get("projects_count", 0))
    
    # Store complete serializable payload as JSON for retrieval
    clean_payload = {
        "student_data": student,
        "target_role": target_role,
        "overall_score": overall_score,
        "tier_label": tier_label,
        "strengths": assessment_result.get("strengths", []),
        "weaknesses": assessment_result.get("weaknesses", []),
        "recommendations": assessment_result.get("recommendations", [])
    }
    json_str = json.dumps(clean_payload, default=str)
    
    insert_sql = """
    INSERT INTO student_assessments (
        student_id, student_name, specialization, semester, target_role,
        academic_percentage, attendance_percentage, overall_readiness_score,
        tier_label, technical_fit_percentage, certifications_count,
        internship_status, projects_count, assessment_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    with conn:
        cursor = conn.cursor()
        cursor.execute(insert_sql, (
            student_id, student_name, specialization, semester, target_role,
            acad_pct, att_pct, overall_score, tier_label, tech_fit,
            certs_count, internship, projects_count, json_str
        ))
        row_id = cursor.lastrowid
        
    if close_at_end:
        conn.close()
    return int(row_id or 0)


def load_all_assessments(conn: Optional[sqlite3.Connection] = None) -> pd.DataFrame:
    """Reads all historical student assessments from SQLite."""
    close_at_end = False
    if conn is None:
        conn = get_connection()
        close_at_end = True
        
    ensure_assessments_table(conn)
    sql = """
    SELECT 
        assessment_id AS "ID",
        student_id AS "Student ID",
        student_name AS "Student Name",
        specialization AS "Specialization",
        semester AS "Semester",
        target_role AS "Target Role",
        ROUND(academic_percentage, 1) AS "Marks (%)",
        ROUND(attendance_percentage, 1) AS "Attendance (%)",
        ROUND(overall_readiness_score, 1) AS "Readiness Score",
        tier_label AS "Readiness Tier",
        ROUND(technical_fit_percentage, 1) AS "Tech Fit (%)",
        certifications_count AS "Certs",
        internship_status AS "Internship",
        projects_count AS "Projects",
        created_at AS "Assessed At"
    FROM student_assessments
    ORDER BY assessment_id DESC;
    """
    df = pd.read_sql_query(sql, conn)
    if close_at_end:
        conn.close()
    return df


def save_single_student_to_db(student_row: Dict[str, Any], conn: Optional[sqlite3.Connection] = None) -> bool:
    """
    Saves or updates a single student record across all 4 normalized SQLite tables:
    students, academic_records, skills, and placements.
    Uses parameterized SQL and respects referential integrity.
    """
    close_at_end = False
    if conn is None:
        conn = get_connection()
        close_at_end = True
        
    init_db()
    
    stu_id = str(student_row.get("student_id", "")).strip()
    name = str(student_row.get("student_name", "")).strip()
    gender = str(student_row.get("gender", "Non-Binary")).strip()
    if gender not in ["Male", "Female", "Non-Binary"]:
        gender = "Non-Binary"
    spec = str(student_row.get("specialization", "Business Analytics")).strip()
    sem = str(student_row.get("semester", "Semester 3")).strip()
    
    acad_pct = float(student_row.get("academic_percentage", 65.0))
    att_pct = float(student_row.get("attendance_percentage", 75.0))
    grade_band = "Distinction" if acad_pct >= 75 else ("First Class" if acad_pct >= 60 else ("Second Class" if acad_pct >= 50 else "Remedial"))
    att_band = "Compliant" if att_pct >= 75 else "At-Risk"
    
    sql_prof = str(student_row.get("sql_proficiency", "Intermediate")).capitalize()
    py_prof = str(student_row.get("python_proficiency", "Beginner")).capitalize()
    bi_prof = str(student_row.get("power_bi_proficiency", "Intermediate")).capitalize()
    certs_cnt = int(student_row.get("certifications_count", 0))
    intern_stat = "Completed" if str(student_row.get("internship_status", "")).lower() == "completed" else "Not Completed"
    
    # Calculate tech score out of 10
    mapping = {"Beginner": 1, "Basic": 1, "Intermediate": 2, "Advanced": 3, "Expert": 3}
    total_pts = mapping.get(sql_prof, 1) + mapping.get(py_prof, 1) + mapping.get(bi_prof, 1)
    tech_score_10 = round((total_pts / 9.0) * 10.0, 2)
    
    placement_stat = str(student_row.get("placement_status", "Unplaced")).capitalize()
    if placement_stat not in ["Placed", "Unplaced"]:
        placement_stat = "Unplaced"
    company = student_row.get("company", None)
    salary_lpa = student_row.get("salary_lpa", None)
    if placement_stat == "Unplaced":
        company = None
        salary_lpa = None
    elif salary_lpa is not None:
        salary_lpa = float(salary_lpa)
        
    with conn:
        cursor = conn.cursor()
        # 1. Students
        cursor.execute("""
            INSERT INTO students (student_id, student_name, gender, specialization, semester)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                student_name=excluded.student_name,
                gender=excluded.gender,
                specialization=excluded.specialization,
                semester=excluded.semester;
        """, (stu_id, name, gender, spec, sem))
        
        # 2. Academic Records
        cursor.execute("""
            INSERT INTO academic_records (student_id, academic_percentage, attendance_percentage, grade_band, attendance_band)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                academic_percentage=excluded.academic_percentage,
                attendance_percentage=excluded.attendance_percentage,
                grade_band=excluded.grade_band,
                attendance_band=excluded.attendance_band;
        """, (stu_id, acad_pct, att_pct, grade_band, att_band))
        
        # 3. Skills
        cursor.execute("""
            INSERT INTO skills (student_id, sql_proficiency, python_proficiency, power_bi_proficiency, certifications_count, internship_status, technical_score_10)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                sql_proficiency=excluded.sql_proficiency,
                python_proficiency=excluded.python_proficiency,
                power_bi_proficiency=excluded.power_bi_proficiency,
                certifications_count=excluded.certifications_count,
                internship_status=excluded.internship_status,
                technical_score_10=excluded.technical_score_10;
        """, (stu_id, sql_prof, py_prof, bi_prof, certs_cnt, intern_stat, tech_score_10))
        
        # 4. Placements
        cursor.execute("""
            INSERT INTO placements (student_id, placement_status, company, salary_lpa)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                placement_status=excluded.placement_status,
                company=excluded.company,
                salary_lpa=excluded.salary_lpa;
        """, (stu_id, placement_stat, company, salary_lpa))
        
    if close_at_end:
        conn.close()
    return True
