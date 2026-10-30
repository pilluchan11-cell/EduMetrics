-- ====================================================================
-- EduMetrics Relational Database Schema (SQLite 3NF)
-- Normalized architecture separating demographics, academics, skills, and placements
-- ====================================================================

-- 1. Master Students Table (Demographic & Enrollment Identity)
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    student_name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female', 'Non-Binary')),
    specialization TEXT NOT NULL,
    semester TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Academic Records Table (Examination Performance & Lecture Attendance)
CREATE TABLE IF NOT EXISTS academic_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    academic_percentage REAL NOT NULL CHECK(academic_percentage >= 0.0 AND academic_percentage <= 100.0),
    attendance_percentage REAL NOT NULL CHECK(attendance_percentage >= 0.0 AND attendance_percentage <= 100.0),
    grade_band TEXT,
    attendance_band TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 3. Skills Table (Technical Competencies & Professional Credentials)
CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    sql_proficiency TEXT NOT NULL CHECK(sql_proficiency IN ('Beginner', 'Intermediate', 'Advanced')),
    python_proficiency TEXT NOT NULL CHECK(python_proficiency IN ('Beginner', 'Intermediate', 'Advanced')),
    power_bi_proficiency TEXT NOT NULL CHECK(power_bi_proficiency IN ('Beginner', 'Intermediate', 'Advanced')),
    certifications_count INTEGER NOT NULL DEFAULT 0 CHECK(certifications_count >= 0),
    internship_status TEXT NOT NULL CHECK(internship_status IN ('Completed', 'Not Completed')),
    technical_score_10 REAL CHECK(technical_score_10 >= 0.0 AND technical_score_10 <= 10.0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 4. Placements Table (Corporate Recruitment Outcomes & Compensation)
CREATE TABLE IF NOT EXISTS placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    placement_status TEXT NOT NULL CHECK(placement_status IN ('Placed', 'Unplaced')),
    company TEXT,
    salary_lpa REAL CHECK(salary_lpa IS NULL OR salary_lpa >= 0.0),
    placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ====================================================================
-- Performance Indexes for Accelerated Joins and Filtering
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_students_specialization ON students(specialization);
CREATE INDEX IF NOT EXISTS idx_students_semester ON students(semester);
CREATE INDEX IF NOT EXISTS idx_academic_student ON academic_records(student_id);
CREATE INDEX IF NOT EXISTS idx_academic_attendance ON academic_records(attendance_percentage);
CREATE INDEX IF NOT EXISTS idx_skills_student ON skills(student_id);
CREATE INDEX IF NOT EXISTS idx_placements_student ON placements(student_id);
CREATE INDEX IF NOT EXISTS idx_placements_status ON placements(placement_status);
