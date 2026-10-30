-- SQLite Schema for EduMetrics
-- Master Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    student_name TEXT NOT NULL,
    gender TEXT NOT NULL,
    specialization TEXT NOT NULL,
    semester TEXT NOT NULL,
    academic_percentage REAL NOT NULL,
    attendance_percentage REAL NOT NULL,
    sql_proficiency TEXT NOT NULL,
    python_proficiency TEXT NOT NULL,
    power_bi_proficiency TEXT NOT NULL,
    certifications_count INTEGER NOT NULL DEFAULT 0,
    internship_status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Placements Table
CREATE TABLE IF NOT EXISTS placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    placement_status TEXT NOT NULL,
    company TEXT,
    salary_lpa REAL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- Indexing for Fast Querying
CREATE INDEX IF NOT EXISTS idx_students_spec ON students(specialization);
CREATE INDEX IF NOT EXISTS idx_placements_status ON placements(placement_status);
