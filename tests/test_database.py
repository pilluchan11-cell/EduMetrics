"""
Comprehensive unit and integration tests for EduMetrics SQLite relational database layer.
Tests schema creation, 4-table 3NF ingestion, foreign keys, and analytical queries.
"""

import pytest
import sqlite3
import pandas as pd
from pathlib import Path
from src.database import (
    get_connection,
    init_db,
    save_dataframe_to_db,
    load_data_from_db,
    ensure_database_initialized,
    query_total_students_by_specialization,
    query_avg_academic_score_by_specialization,
    query_placement_rate_by_specialization,
    query_avg_salary_by_specialization,
    query_placed_vs_unplaced_counts,
    query_students_below_attendance,
    query_skill_placement_comparison
)
from src.data_generator import generate_synthetic_data


@pytest.fixture
def test_db_path(tmp_path):
    return tmp_path / "test_edumetrics_relational.db"


@pytest.fixture
def populated_db(test_db_path):
    df = generate_synthetic_data(n=50, seed=42)
    save_dataframe_to_db(df, db_path=test_db_path)
    return test_db_path


def test_schema_creation_and_tables(test_db_path):
    init_db(test_db_path)
    conn = get_connection(test_db_path)
    cursor = conn.cursor()
    
    # Check that all 4 normalized tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    assert "students" in tables
    assert "academic_records" in tables
    assert "skills" in tables
    assert "placements" in tables


def test_ingest_and_foreign_keys(test_db_path):
    df = generate_synthetic_data(n=25, seed=101)
    count = save_dataframe_to_db(df, db_path=test_db_path)
    assert count == 25
    
    conn = get_connection(test_db_path)
    cursor = conn.cursor()
    
    # Verify counts in all 4 tables
    cursor.execute("SELECT COUNT(*) FROM students;")
    assert cursor.fetchone()[0] == 25
    
    cursor.execute("SELECT COUNT(*) FROM academic_records;")
    assert cursor.fetchone()[0] == 25
    
    cursor.execute("SELECT COUNT(*) FROM skills;")
    assert cursor.fetchone()[0] == 25
    
    cursor.execute("SELECT COUNT(*) FROM placements;")
    assert cursor.fetchone()[0] == 25
    
    conn.close()


def test_load_joined_data(populated_db):
    df = load_data_from_db(db_path=populated_db)
    assert len(df) == 50
    expected_cols = [
        "student_id", "student_name", "gender", "specialization", "semester",
        "academic_percentage", "attendance_percentage", "grade_band", "attendance_band",
        "sql_proficiency", "python_proficiency", "power_bi_proficiency",
        "certifications_count", "internship_status", "technical_score_10",
        "placement_status", "company", "salary_lpa"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Column {col} missing from joined SQLite view"


def test_analytical_query_1_students_by_specialization(populated_db):
    conn = get_connection(populated_db)
    sql, res = query_total_students_by_specialization(conn)
    conn.close()
    assert len(res) > 0
    assert "Total Students" in res.columns
    assert res["Total Students"].sum() == 50


def test_analytical_query_2_avg_academic_by_specialization(populated_db):
    conn = get_connection(populated_db)
    sql, res = query_avg_academic_score_by_specialization(conn)
    conn.close()
    assert len(res) > 0
    assert "Mean Marks (%)" in res.columns


def test_analytical_query_3_placement_rate_by_specialization(populated_db):
    conn = get_connection(populated_db)
    sql, res = query_placement_rate_by_specialization(conn)
    conn.close()
    assert len(res) > 0
    assert "Placement Rate (%)" in res.columns


def test_analytical_query_4_avg_salary_by_specialization(populated_db):
    conn = get_connection(populated_db)
    sql, res = query_avg_salary_by_specialization(conn)
    conn.close()
    assert len(res) > 0
    assert "Average Package (₹ LPA)" in res.columns


def test_analytical_query_5_placed_vs_unplaced(populated_db):
    conn = get_connection(populated_db)
    sql, res = query_placed_vs_unplaced_counts(conn)
    conn.close()
    assert len(res) == 2
    assert "Student Count" in res.columns
    assert res["Student Count"].sum() == 50


def test_analytical_query_6_parameterized_attendance_threshold(populated_db):
    conn = get_connection(populated_db)
    sql, res = query_students_below_attendance(conn, threshold=75.0)
    conn.close()
    # All returned rows must have attendance < 75.0
    if len(res) > 0:
        assert (res["Attendance (%)"] < 75.0).all()


def test_analytical_query_7_skill_placement_comparison(populated_db):
    conn = get_connection(populated_db)
    sql, res_py = query_skill_placement_comparison(conn, "python_proficiency")
    sql, res_sql = query_skill_placement_comparison(conn, "sql_proficiency")
    conn.close()
    assert len(res_py) > 0
    assert "Proficiency Level" in res_py.columns
    assert len(res_sql) > 0


def test_ensure_database_initialized(tmp_path):
    auto_db_path = tmp_path / "auto_init.db"
    assert not auto_db_path.exists()
    
    ensure_database_initialized(db_path=auto_db_path)
    assert auto_db_path.exists()
    
    conn = get_connection(auto_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students;")
    count = cursor.fetchone()[0]
    conn.close()
    assert count >= 500
