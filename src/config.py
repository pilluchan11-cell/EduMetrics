"""
Configuration constants and styling parameters for EduMetrics.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
DEFAULT_CSV_PATH = DATA_DIR / "synthetic_students.csv"
DB_PATH = DATABASE_DIR / "edumetrics.db"

# App Branding
APP_NAME = "EduMetrics"
APP_SUBTITLE = "Student Performance & Placement Analytics Dashboard"
APP_TAGLINE = "Turning Student Data into Smarter Career Decisions."
SYNTHETIC_DATA_DISCLAIMER = (
    "Synthetic Data Notice: All records in this dashboard are algorithmically "
    "generated for academic, demonstration, and research purposes. No actual student "
    "personal data or confidential institution records are used."
)

# Thresholds & Benchmarks
ATTENDANCE_CRITICAL_THRESHOLD = 75.0   # Percentage below which attendance is flagged
ACADEMIC_DISTINCTION_THRESHOLD = 80.0  # Percentage for top distinction
ACADEMIC_PASS_THRESHOLD = 50.0         # Passing percentage

# Palette for charts and indicators
COLOR_PRIMARY = "#2563EB"      # Royal Blue
COLOR_SECONDARY = "#0D9488"    # Teal
COLOR_ACCENT = "#F59E0B"       # Amber / Gold
COLOR_DANGER = "#EF4444"       # Red
COLOR_SUCCESS = "#10B981"      # Emerald
COLOR_NEUTRAL = "#64748B"      # Slate
COLOR_BACKGROUND = "#F8FAFC"

PALETTE_CATEGORICAL = [
    "#2563EB", "#0D9488", "#F59E0B", "#8B5CF6", "#EC4899", 
    "#10B981", "#6366F1", "#14B8A6", "#F97316", "#06B6D4"
]

# Standard Specializations
SPECIALIZATIONS = [
    "Business Analytics",
    "Finance",
    "Marketing",
    "Operations & Supply Chain",
    "Human Resources"
]

# Semesters
SEMESTERS = ["Semester 1", "Semester 2", "Semester 3", "Semester 4"]

# Proficiency Levels
PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced"]

# Fictional Hiring Companies
COMPANIES = [
    "Apex Analytics",
    "Nexus Global Consulting",
    "Titan Capital Partners",
    "Quantum Insights",
    "Vanguard Strategic Advisors",
    "Zenith Retail Technologies",
    "Horizon FinTech",
    "Starlight Media & Tech",
    "Pinnacle Logistics",
    "BlueCrest Healthcare"
]

# Expected Dataset Schema
EXPECTED_COLUMNS = [
    "student_id",
    "student_name",
    "gender",
    "specialization",
    "semester",
    "academic_percentage",
    "attendance_percentage",
    "sql_proficiency",
    "python_proficiency",
    "power_bi_proficiency",
    "certifications_count",
    "internship_status",
    "placement_status",
    "company",
    "salary_lpa"
]
