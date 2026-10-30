# EduMetrics: Student Performance & Placement Analytics Dashboard

> **Tagline:** *Turning Student Data into Smarter Career Decisions.*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75.svg)](https://plotly.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg)](https://www.sqlite.org/)
[![Testing](https://img.shields.io/badge/Tests-Pytest-0A9EDC.svg)](https://docs.pytest.org/)

---

## 📌 Executive Summary & Business Objective

Higher education and business schools require actionable intelligence on how student attendance, academic performance, technical proficiencies, certifications, and experiential learning relate to recruitment outcomes. 

**EduMetrics** is an interactive, enterprise-grade business intelligence dashboard architected with **Streamlit**, **Pandas**, and **Plotly**. It processes student academic data, calculates key performance indicators, identifies at-risk cohorts, analyzes compensation spreads, and delivers transparent, rule-based recommendations for institutional leadership, faculty mentors, and career placement directors.

---

## 🏛️ System Architecture

EduMetrics adopts a modular design separating data generation, validation, business analytics, visualization, and presentation logic:

```
EduMetrics/
├── .streamlit/
│   └── config.toml                  # UI theme, responsive layout, server config
├── data/
│   └── synthetic_students.csv       # Seeded 500-student benchmark dataset
├── database/
│   ├── schema.sql                   # Normalized 3NF SQLite schema
│   └── edumetrics.db                # SQLite database (Phase 2 relational storage)
├── src/
│   ├── config.py                    # Constants, branding, color palettes, thresholds
│   ├── data_generator.py            # Reproducible synthetic student data generator
│   ├── data_loader.py               # Data cleaning, schema validation, and cached loading
│   ├── metrics.py                   # Pure calculation functions (KPIs, distributions, IQRs)
│   ├── rules_engine.py              # Explainable heuristic rules diagnostic engine
│   ├── visualizations.py            # High-contrast Plotly chart factories
│   ├── database.py                  # SQLite ingest, commit, and query layer
│   ├── ui_components.py             # Custom CSS, KPI cards, and styling components
│   └── views/                       # Modular dashboard views (Executive, Academic, etc.)
├── tests/                           # Pytest unit and integration test suite
├── app.py                           # Main application router and global filter sidebar
└── requirements.txt                 # Pinned dependencies
```

---

## 🚀 Key Modules & Capabilities

### 1. 📊 Executive Dashboard
* **Institutional KPI Ribbon:** Real-time visibility into total cohort size, placement percentage, average academic marks, and attendance.
* **Compensation Metrics:** Mean and median package offers (LPA) alongside the campus top offer.
* **Placement Funnel & Specialization Trends:** Interactive Plotly donut and comparative bar charts.

### 2. 📚 Academic Performance Analytics
* **Score & Grade Bands:** Categorization into *Distinction ($\ge 80\%$)*, *First Class*, *Second Class*, and *Intervention Needed ($<50\%$)*.
* **Attendance vs. Academic Achievement:** Scatter plots with the institutional **75% Critical Attendance Threshold** highlighted.
* **Cohort Tracking:** Automated segmentation of high-achievers and students requiring academic support.

### 3. 💼 Placement & Compensation Analytics
* **Compensation Spread:** Detailed boxplots and violin plots showing salary package dispersion across specializations.
* **Corporate Hiring Distribution:** Breakdown of recruitment volumes and average offers across hiring partners.
* **Skill & Certification Lift:** Measuring recruitment outcomes across Python, SQL, Power BI proficiency levels, and internships.

### 4. 👤 Individual Student Profiler
* **Student Search & Selector:** Interactive search by Student ID, Name, or Specialization.
* **Competency Radar Benchmark:** Multi-axis spider chart comparing the student's marks, attendance, and skills directly against the **Batch Average**.
* **Personalized Diagnostic Card:** Automated breakdown of student strengths, risk factors, and next actionable steps.

### 5. 📈 Statistical & Correlation Analysis
* **Pairwise Correlation Heatmap:** Pearson and Spearman correlations between numeric academic and career variables.
* **Bivariate Trendlines:** Ordinary Least Squares (OLS) regression curves for marks vs. attendance and technical score vs. salary.
* **Non-Parametric Summaries:** Full statistical quantiles (P10, P25, Median, P75, P90, IQR).

### 6. 🎯 Explainable Strategic Recommendations
* **Heuristic Decision Engine:** Deterministic, transparent rules that avoid unsupported causal claims or black-box bias.
* **Institutional Pillars:** Strategic roadmaps across Academic Quality, Attendance Protocol, Technical Tool Mastery, and Career Preparation.

### 7. ⚙️ Data Management & Relational Database Sync
* **Custom CSV Upload:** Drag-and-drop custom student datasets with automatic schema and boundary validation.
* **SQLite Relational Sync & 3NF Storage:** Ingest student records into 4 normalized SQLite tables with foreign key constraints.
* **Interactive SQL Explorer:** Run and inspect parameterized analytical SQL queries live with one-click CSV export.
* **Filtered Export:** One-click download of the active filtered cohort in CSV format.

---

## 🗄️ Relational Database Architecture & SQL Analytics (SQLite 3NF)

EduMetrics integrates a production-ready, normalized **SQLite 3** relational database layer (`database/edumetrics.db`) managed via `src/database.py`. The schema is normalized into **Third Normal Form (3NF)** to eliminate redundancy and enforce referential integrity.

### 1. Normalized Relational Schema (`database/schema.sql`)

The database decomposes student records across 4 interconnected tables with primary keys, foreign keys (`ON DELETE CASCADE`), and domain-level `CHECK` constraints:

| Table | Entity Purpose | Primary Key | Foreign Key Reference | Key Attributes |
|---|---|---|---|---|
| **`students`** | Master demographic & enrollment identity | `student_id` (TEXT) | *None* | `student_name`, `gender`, `specialization`, `semester`, `created_at` |
| **`academic_records`** | Examination performance & lecture attendance | `record_id` (AUTOINCREMENT) | `student_id` $\rightarrow$ `students(student_id)` | `academic_percentage`, `attendance_percentage`, `grade_band`, `attendance_band` |
| **`skills`** | Technical proficiencies & credentials | `skill_id` (AUTOINCREMENT) | `student_id` $\rightarrow$ `students(student_id)` | `sql_proficiency`, `python_proficiency`, `power_bi_proficiency`, `certifications_count`, `internship_status`, `technical_score_10` |
| **`placements`** | Corporate recruitment & compensation | `placement_id` (AUTOINCREMENT) | `student_id` $\rightarrow$ `students(student_id)` | `placement_status`, `company`, `salary_lpa`, `placed_at` |

#### Key Database Architecture Features:
* **ACID Transactions:** Atomic insertion across all four tables within single transactions.
* **Cascading Deletions:** `ON DELETE CASCADE` guarantees zero orphaned records if student identity rows are purged.
* **Performance Indexes:** 7 secondary B-tree indexes optimize high-volume queries on `specialization`, `semester`, `attendance_percentage`, and `placement_status`.
* **Automated Database Seeding:** Automatically creates tables and seeds 500 records on first run (`ensure_database_initialized()`), requiring **zero manual SQL setup**.

---

### 2. Analytical SQL Query Library

EduMetrics features 7 parameterized analytical queries executed directly from the application's **SQL Analytics & Relational Explorer** tab:

1. **Cohort Distribution by Specialization:**
   ```sql
   SELECT specialization AS "Specialization", 
          COUNT(student_id) AS "Total Students",
          ROUND(100.0 * COUNT(student_id) / (SELECT COUNT(*) FROM students), 1) AS "Cohort Share (%)"
   FROM students
   GROUP BY specialization
   ORDER BY "Total Students" DESC;
   ```

2. **Academic Performance Statistics across Specializations:**
   ```sql
   SELECT s.specialization AS "Specialization", 
          ROUND(AVG(a.academic_percentage), 2) AS "Mean Marks (%)",
          ROUND(MIN(a.academic_percentage), 2) AS "Min Marks (%)",
          ROUND(MAX(a.academic_percentage), 2) AS "Max Marks (%)",
          COUNT(s.student_id) AS "Students Evaluated"
   FROM students s
   JOIN academic_records a ON s.student_id = a.student_id
   GROUP BY s.specialization
   ORDER BY "Mean Marks (%)" DESC;
   ```

3. **Recruitment Placement Rate by Specialization:**
   ```sql
   SELECT s.specialization AS "Specialization",
          COUNT(s.student_id) AS "Enrolled Students",
          SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) AS "Placed Students",
          ROUND(100.0 * SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) / COUNT(s.student_id), 1) AS "Placement Rate (%)"
   FROM students s
   JOIN placements p ON s.student_id = p.student_id
   GROUP BY s.specialization
   ORDER BY "Placement Rate (%)" DESC;
   ```

4. **Compensation Analysis (Average & Range CTC in LPA):**
   ```sql
   SELECT s.specialization AS "Specialization",
          COUNT(p.salary_lpa) AS "Placed Students Count",
          ROUND(AVG(p.salary_lpa), 2) AS "Average Package (₹ LPA)",
          ROUND(MIN(p.salary_lpa), 2) AS "Min Offer (₹ LPA)",
          ROUND(MAX(p.salary_lpa), 2) AS "Top Offer (₹ LPA)"
   FROM students s
   JOIN placements p ON s.student_id = p.student_id
   WHERE LOWER(p.placement_status) = 'placed' AND p.salary_lpa IS NOT NULL
   GROUP BY s.specialization
   ORDER BY "Average Package (₹ LPA)" DESC;
   ```

5. **Campus-Wide Placed vs. Unplaced Cohort Counts:**
   ```sql
   SELECT p.placement_status AS "Placement Status",
          COUNT(p.student_id) AS "Student Count",
          ROUND(100.0 * COUNT(p.student_id) / (SELECT COUNT(*) FROM placements), 1) AS "Proportion (%)"
   FROM placements p
   GROUP BY p.placement_status;
   ```

6. **Parameterized Query — At-Risk Students Below Attendance Cutoff:**
   ```sql
   SELECT s.student_id AS "Student ID",
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
   ```

7. **Parameterized Query — Skill Competency vs. Placement Outcomes:**
   ```sql
   SELECT sk.python_proficiency AS "Proficiency Level",
          COUNT(sk.student_id) AS "Total Candidates",
          SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) AS "Placed Count",
          ROUND(100.0 * SUM(CASE WHEN LOWER(p.placement_status) = 'placed' THEN 1 ELSE 0 END) / COUNT(sk.student_id), 1) AS "Placement Rate (%)",
          ROUND(AVG(CASE WHEN LOWER(p.placement_status) = 'placed' THEN p.salary_lpa END), 2) AS "Mean Package (₹ LPA)"
   FROM skills sk
   JOIN placements p ON sk.student_id = p.student_id
   GROUP BY sk.python_proficiency
   ORDER BY CASE sk.python_proficiency 
       WHEN 'Beginner' THEN 1 
       WHEN 'Intermediate' THEN 2 
       WHEN 'Advanced' THEN 3 
       ELSE 4 
   END;
   ```

---

## 🔒 Synthetic Data & Responsible AI Notice

> **Notice:** All 500 student records in this portfolio dashboard are algorithmically synthesized using calibrated statistical distributions (Normal, Poisson, Beta, and Bernoulli). Student names, IDs, academic scores, and corporate offers are entirely fictional. Fictional data is never represented as empirical college records. Demographic variables are synthetic and not used for consequential individual decisions.

---

## 🛠️ Quickstart & Local Setup

### 1. Prerequisites
* Python 3.10+ (compatible with Python 3.10 through 3.14)
* Git

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/EduMetrics.git
cd EduMetrics

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```
The application will launch automatically in your browser at `http://localhost:8501`.

### 5. Run the Test Suite
```bash
pytest tests/ -v
```

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit of EduMetrics analytics platform"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account and select the `EduMetrics` repository.
4. Set Main file path to `app.py`.
5. Click **Deploy!**

---

## 📄 License
This project is licensed under the MIT License.
