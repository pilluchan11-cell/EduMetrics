# EduMetrics: Student Performance & Placement Analytics Dashboard

> **Tagline:** *Turning Student Data into Smarter Career Decisions.*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75.svg)](https://plotly.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3%203NF-003B57.svg)](https://www.sqlite.org/)
[![Testing](https://img.shields.io/badge/Tests-Pytest%20(50%20Passed)-0A9EDC.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Business Problem & Motivation

Higher education institutions and business schools capture vast volumes of student information, ranging from term examination marks and lecture attendance logs to coding tool proficiencies, certifications, and summer internship completions. However, academic deans, program chairs, and placement directors often lack unified, data-driven systems to answer critical operational questions:

* *Which academic specializations exhibit the strongest recruitment conversion and compensation premiums?*
* *How strongly does attendance compliance directly protect student marks and placement eligibility?*
* *What specific technical skill thresholds (SQL, Python, Power BI) separate placed candidates from unplaced candidates?*
* *Which students are currently at academic or career risk and require immediate targeted intervention?*

Without centralized analytics, institutions rely on fragmented spreadsheets, delayed post-semester reviews, or black-box predictive models that lack explainability. **EduMetrics** addresses this gap by combining an interactive Streamlit user interface, high-contrast Plotly business intelligence visualizations, a normalized 3NF SQLite database layer, and transparent, rule-based diagnostic guidance.

---

## 🎯 Strategic Project Objectives

1. **Executive Oversight:** Deliver real-time institutional KPIs on cohort health, placement velocity, and compensation benchmarks.
2. **Predictive & Diagnostic Guidance:** Identify at-risk students early through deterministic, explainable heuristic decision rules without algorithmic bias.
3. **Statistical & Econometric Rigor:** Provide faculty panels with empirical hypothesis testing (Welch's t-tests, Cohen's d effect sizes, ANOVA, and Logistic Regression odds ratios).
4. **Relational Data Integrity:** Transition institutional records into a Third Normal Form (3NF) relational SQLite database with foreign key cascading integrity.
5. **Presentation-Ready SaaS Interface:** Provide an MBA-grade executive aesthetic with responsive KPI cards, custom HTML tooltips, and interactive data slicing.

---

## 💻 Technology Stack

* **Core Runtime:** Python 3.10 through 3.14 compatible
* **Application Framework:** Streamlit (v1.35+)
* **Data Processing & Manipulation:** Pandas (v2.2+), NumPy (v1.26+)
* **Statistical & Econometric Computing:** SciPy (v1.11+), Scikit-learn (v1.4+)
* **Data Visualization:** Plotly Express & Plotly Graph Objects (v5.20+)
* **Relational Database:** SQLite 3 with standard library `sqlite3` (Zero external driver overhead)
* **Automated Testing Suite:** Pytest (v8.0+) with Streamlit `AppTest` harness
* **Version Control & Hosting:** Git, GitHub, and Streamlit Community Cloud

---

## 🏛️ System Architecture

```
EduMetrics/
├── .streamlit/
│   └── config.toml                  # Executive dark/navy styling, layout, server config
├── data/
│   └── synthetic_students.csv       # Seeded 500-student benchmark dataset
├── database/
│   ├── schema.sql                   # Normalized 3NF SQLite schema DDL
│   └── edumetrics.db                # SQLite database (auto-seeded on initialization)
├── docs/
│   ├── ARCHITECTURE.md              # Deep-dive system architecture & design specs
│   ├── DATA_DICTIONARY.md           # Schema definitions & distribution parameters
│   └── DEPLOYMENT.md                # Deployment walkthrough for Streamlit Cloud
├── src/
│   ├── config.py                    # Constants, branding, color palettes, benchmarks
│   ├── data_generator.py            # Calibrated synthetic data generation engine
│   ├── data_loader.py               # Data validation, cleaning, and cached loading
│   ├── database.py                  # Relational ingest, foreign key management, SQL queries
│   ├── metrics.py                   # Pure analytical calculations, KPIs, hypothesis tests
│   ├── rules_engine.py              # Explainable heuristic rules diagnostic engine
│   ├── assessment_engine.py         # Role benchmarks, skill gap analysis, readiness scoring
│   ├── report_generator.py          # Publication-ready PDF diagnostic report builder (ReportLab)
│   ├── ui_components.py             # Custom CSS, KPI cards, banners, and layout helpers
│   ├── visualizations.py            # High-contrast Plotly chart factories with tooltips
│   └── views/                       # Modular dashboard views
│       ├── executive.py             # Executive dashboard & dynamic insights
│       ├── academic.py              # Academic score distributions & attendance correlation
│       ├── placement.py             # Placement conversion, salaries, and company analytics
│       ├── student.py               # Individual student profiler & radar benchmarks
│       ├── assessment.py            # Individual student assessment & career-readiness analyzer
│       ├── statistical.py           # Hypothesis testing, p-values, OLS, and logistic regression
│       ├── recommendations.py       # Strategic 4-pillar institutional roadmaps
│       └── data_mgmt.py             # CSV upload audit, SQLite sync, and SQL query explorer
├── tests/                           # 50 Automated unit and integration tests
│   ├── test_assessment.py           # Competency gap, readiness scoring, benchmarks, PDF, DB
│   ├── test_database.py             # SQLite relational schema, joins, & 7 analytical queries
│   ├── test_edge_cases.py           # Null handling, empty dataframes, & extreme values
│   ├── test_metrics.py              # Statistical KPI calculations & hypothesis tests
│   ├── test_rules_engine.py         # Student and cohort recommendation rules
│   ├── test_streamlit_app.py        # Streamlit AppTest navigation & zero-record filter test
│   └── test_validation.py          # Schema compliance, duplicate IDs, & range checks
├── app.py                           # Main application entry point & global filter router
├── requirements.txt                 # Pinned production dependencies
└── .gitignore                       # Production ignore patterns (excluding secrets & caches)
```

---

## 🚀 Key Modules & Capabilities

### 1. 📊 Executive Dashboard
* **Institutional KPI Ribbon:** Real-time visibility into total enrolled cohort, placement percentage, average academic marks, and attendance compliance.
* **Compensation Metrics:** Mean and median package offers (₹ LPA) alongside campus peak CTC.
* **Dynamic Business Insights:** 5 to 8 automated, non-hardcoded business findings dynamically computed from the active filtered cohort.
* **Placement Funnel & Specialization Trends:** Interactive Plotly donut and comparative bar charts.

### 2. 📚 Academic Performance Analytics
* **Score & Grade Bands:** Categorization into *Distinction ($\ge 80\%$)*, *First Class ($65-79\%$)*, *Second Class ($50-64\%$)*, and *Support Required ($<50\%$)*.
* **Attendance vs. Academic Achievement:** Scatter plots with the institutional **75% Critical Attendance Threshold** highlighted.
* **Cohort Tracking:** Automated segmentation identifying high-achievers and students requiring remediation.
* **Curriculum Progression:** Semester-level boxplots evaluating score progression across semesters 1 through 4.

### 3. 💼 Placement & Compensation Analytics
* **Compensation Dispersion:** Detailed boxplots displaying median CTC, interquartile ranges (IQR), and outlier packages across specializations.
* **Corporate Hiring Distribution:** Ranked hiring volume and average compensation across corporate recruiting partners.
* **Skill Competency Lift:** Quantified placement conversion rates across Beginner, Intermediate, and Advanced tiers for Python, SQL, and Power BI.

### 4. 👤 Individual Student Profiler
* **Real-Time Student Search:** Instant search by Student ID, student name, or major, with placed/unplaced quick filters.
* **Multi-Axis Competency Radar Chart:** Spider chart indexing the student's individual marks, attendance, and technical tools directly against the **Batch Average**.
* **Personalized Diagnostic Card:** Deterministic breakdown of student strengths, risk alerts, and next actionable steps.

### 5. 📝 Individual Student Assessment & Career-Readiness Analyzer
* **Interactive Data Entry Form:** Structured evaluation form capturing basic demographics, 10th/12th/UG/CGPA scores, 5-subject marks, attendance compliance, technical tools (1-5 scale), certifications, corporate internship, project portfolio, and mock interview status.
* **Career-Role Competency Benchmarking:** Configurable industry requirement matrices across 5 core roles: *Data Analyst*, *Business Analyst*, *Data Scientist*, *Business Intelligence Analyst*, and *Product Analyst*.
* **Explainable Placement Readiness Index (0–100):** Weighted multi-pillar scoring model evaluating Academic Standing (15-20%), Attendance (10%), Technical Fit (25-40%), Certifications (10-15%), Practical Projects (10-20%), and Soft Skills (10-20%).
* **Visual Competency Gap Analysis:** Grouped bar charts identifying skill surpluses and deficits against role benchmarks, multilateral polar radar profile, and pillar score breakdowns.
* **Automated Actionable Recommendations:** Targeted, role-specific guidance (e.g. elevating SQL via window functions, publishing GitHub dashboards, or scheduling faculty advising).
* **Publication-Ready PDF Dossier Download:** Professional executive PDF generated via ReportLab with institutional branding, tables, scorecards, and faculty sign-off blocks.
* **Relational SQLite Persistence & Cohort Integration:** One-click options to save assessments to SQLite table `student_assessments` and append candidate records into the active cohort session dataset.

### 6. 📈 Statistical & Econometric Analysis
* **Pairwise Correlation Matrix:** Pearson correlation coefficients ($r$) with two-tailed p-values and significance notation.
* **Inferential Hypothesis Testing:** Two-sample Welch's t-tests and Cohen's $d$ effect sizes comparing Placed vs. Unplaced students.
* **One-Way ANOVA:** Parametric F-tests evaluating whether academic performance differs significantly across specializations.
* **Multivariate Logistic Regression:** Demonstrates the marginal contribution of academics, attendance, and skills to placement odds ratios ($\text{OR} = e^\beta$).

### 7. 🎯 Explainable Strategic Recommendations
* **Deterministic Heuristic Rules:** Transparent business logic avoiding black-box machine-learning opacity.
* **The 4 Pillars of Institutional Excellence:** Actionable roadmaps covering:
  1. *Academic Quality & Peer Mentorship*
  2. *Attendance Compliance & Early Alert Protocols*
  3. *Technical Tool Mastery & Project Portfolio Development*
  4. *Corporate Placement Conversion & Alumni Capstones*

### 8. ⚙️ Data Management & SQL Relational Explorer
* **Custom CSV Ingestion & Audit:** Drag-and-drop custom student datasets with automated schema, duplicate, and range validation.
* **SQLite Relational Synchronization:** Instant bi-directional sync between session memory and the 3NF SQLite database.
* **Interactive SQL Query Runner:** Execute and inspect 7 parameterized analytical queries with raw SQL syntax highlighting and CSV exports.

---

## 🗄️ Relational Database Architecture (SQLite 3NF)

EduMetrics implements a normalized **Third Normal Form (3NF)** relational database layer (`database/edumetrics.db`) managed via `src/database.py`. The database automatically initializes and seeds on first startup with zero manual setup required.

```
                            ┌─────────────────────────────────┐
                            │            students             │
                            ├─────────────────────────────────┤
                            │ PK  student_id (TEXT)           │
                            │     student_name (TEXT)         │
                            │     gender (TEXT)               │
                            │     specialization (TEXT)       │
                            │     semester (TEXT)             │
                            │     created_at (TIMESTAMP)      │
                            └───────────────┬─────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               │ 1:1                        │ 1:1                        │ 1:1
               ▼                            ▼                            ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────┐
│       academic_records       │ │            skills            │ │          placements          │
├──────────────────────────────┤ ├──────────────────────────────┤ ├──────────────────────────────┤
│ PK  record_id (AUTOINCREMENT)│ │ PK  skill_id (AUTOINCREMENT) │ │ PK  placement_id (AUTOINCR)  │
│ FK  student_id (TEXT) ────┐  │ │ FK  student_id (TEXT) ────┐  │ │ FK  student_id (TEXT) ────┐  │
│     academic_pct (REAL)   │  │ │     sql_proficiency (TEXT)│  │ │     placement_status (TEXT)│  │
│     attendance_pct (REAL) │  │ │     python_prof (TEXT)    │  │ │     company (TEXT)         │  │
│     grade_band (TEXT)     │  │ │     power_bi_prof (TEXT)  │  │ │     salary_lpa (REAL)      │  │
│     attendance_band (TEXT)│  │ │     certifications (INT)  │  │ │     placed_at (TIMESTAMP)  │  │
│     updated_at (TIMESTAMP)│  │ │     internship (TEXT)     │  │ └──────────────────────────────┘
└──────────────────────────────┘ │     tech_score_10 (REAL)  │  │  ON DELETE CASCADE
 ON DELETE CASCADE               │     updated_at (TIMESTAMP)│  │
                                 └──────────────────────────────┘
                                  ON DELETE CASCADE
```

### Analytical SQL Query Library (`src/database.py`)
1. **Total Students by Specialization:** `GROUP BY specialization` with dynamic cohort share percentages.
2. **Academic Statistics by Specialization:** Computes Mean, Min, and Max marks across majors.
3. **Placement Rate by Specialization:** Evaluates recruitment conversion percentage via conditional joins.
4. **Compensation Analysis by Major:** Mean, minimum, and peak CTC packages (₹ LPA) for placed candidates.
5. **Campus-Wide Placed vs. Unplaced Counts:** Population breakdown across recruitment categories.
6. **Parameterized Query — Attendance Risk:** Filters candidates below an interactive threshold (`WHERE attendance < ?`).
7. **Parameterized Query — Skill vs. Placement:** Groups placement conversion and packages across technical tool proficiencies.

---

## 📊 Dataset Description & Statistical Calibration

The benchmark dataset (`data/synthetic_students.csv`) comprises **500 fictional student records** calibrated across realistic business school distributions:

| Field | Type | Permissible Range | Distribution / Logic |
|---|---|---|---|
| `student_id` | Alphanumeric | `EDU-2026-001` to `EDU-2026-500` | Sequential primary key |
| `student_name` | String | Fictional full names | Algorithmic first/last name pairing |
| `gender` | Categorical | `Male`, `Female`, `Non-Binary` | Uniform demographic distribution |
| `specialization` | Categorical | 5 MBA Majors | Proportional enrollment weights |
| `semester` | Categorical | `Semester 1` to `Semester 4` | Curriculum cohorts |
| `academic_percentage` | Continuous | $0.0 - 100.0\%$ | Calibrated Normal distribution ($\mu=72\%, \sigma=10.5\%$) |
| `attendance_percentage` | Continuous | $0.0 - 100.0\%$ | Beta distribution ($\mu=81\%, \sigma=9.2\%$) |
| `sql_proficiency` | Ordinal | `Beginner`, `Intermediate`, `Advanced` | Skill distribution weighted by major |
| `python_proficiency` | Ordinal | `Beginner`, `Intermediate`, `Advanced` | Analytics/Finance-skewed weights |
| `power_bi_proficiency` | Ordinal | `Beginner`, `Intermediate`, `Advanced` | Visual reporting competency |
| `certifications_count` | Integer | $0$ to $5$ credentials | Poisson distribution ($\lambda=1.8$) |
| `internship_status` | Categorical | `Completed`, `Not Completed` | Bernoulli trial ($p=0.68$) |
| `placement_status` | Categorical | `Placed`, `Unplaced` | Logistic probability function of skills, marks, & intern |
| `company` | String | 10 Corporate Partners | Null for unplaced; corporate tier for placed |
| `salary_lpa` | Continuous | $5.0 - 24.0$ ₹ LPA | Right-skewed Log-Normal distribution |

---

## 📷 Screenshots & Visual Tour

*(Replace placeholders with application captures prior to submission)*

| Executive Overview & KPIs | Placement & Compensation Analytics |
|:---:|:---:|
| ![Executive Dashboard](docs/images/screenshot_executive.png)<br>*Institutional KPI ribbon, placement conversion donut, and dynamic insight cards.* | ![Placement Analytics](docs/images/screenshot_placement.png)<br>*Compensation dispersion boxplots, company hiring volumes, and skill impact.* |

| Student Competency Radar Profiler | Statistical Hypothesis & Econometrics |
|:---:|:---:|
| ![Student Profile](docs/images/screenshot_student.png)<br>*Multi-axis competency benchmark spider chart and explainable diagnostic cards.* | ![Statistical Analysis](docs/images/screenshot_statistical.png)<br>*Significance heatmap, Welch's t-tests, OLS regression lines, and logistic odds ratios.* |

---

## 🛠️ Installation & Local Setup

### 1. Prerequisites
* **Python:** Version 3.10, 3.11, 3.12, or 3.14
* **Git:** Installed on local machine

### 2. Clone the Repository
```bash
git clone https://github.com/harshthakur-45/EduMetrics.git
cd EduMetrics
```

### 3. Create & Activate Virtual Environment
```bash
# On Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\activate

# On macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the Application
```bash
streamlit run app.py
```
The application will launch automatically in your default browser at `http://localhost:8501`.

---

## 🧪 Automated Testing Strategy

EduMetrics includes a comprehensive Pytest test suite with **42 automated unit and integration tests** verifying all business calculations, database transactions, and UI workflows:

```bash
# Run the complete test suite with verbose output
pytest tests/ -v
```

### Test Coverage Highlights:
* **`tests/test_database.py` (11 tests):** 3NF table creation, foreign key cascade integrity, joined DataFrame reloading, and all 7 analytical queries.
* **`tests/test_edge_cases.py` (6 tests):** Fault tolerance against empty DataFrames (0 records), missing values (`NaN`), extreme numbers, and single-class cohorts.
* **`tests/test_metrics.py` (13 tests):** Verification of executive KPIs, academic quartiles, salary IQR, Welch's t-test, Cohen's d, ANOVA, and logistic regression.
* **`tests/test_rules_engine.py` (3 tests):** Deterministic diagnostic rules, risk alerts, and cohort recommendations.
* **`tests/test_streamlit_app.py` (3 tests):** Streamlit `AppTest` verifying clean boot, cross-module navigation, and zero-record filter resilience.
* **`tests/test_validation.py` (6 tests):** Schema auditing, duplicate student ID detection, out-of-range percentage rejection, and placement consistency.

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

1. Push your local repository to GitHub:
   ```bash
   git add .
   git commit -m "Prepare EduMetrics for production deployment"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"**.
4. Select repository: `harshthakur-45/EduMetrics`, branch: `main`, and main file path: `app.py`.
5. Click **"Deploy!"**. Streamlit Cloud will install dependencies from `requirements.txt` and launch the app with a public HTTPS URL.

---

## ⚠️ Limitations & Ethical Boundaries

1. **Synthetic Nature:** All 500 records are generated algorithmically for academic demonstration. Metrics do not reflect empirical statistics from any accredited university.
2. **Correlation vs. Causation:** Statistical associations (e.g. attendance correlation with marks) illustrate empirical patterns; they do not establish direct causality.
3. **Heuristic vs. Autonomous Decisions:** Recommendation rules provide advisory guidance for educational leaders; consequential academic decisions should always involve human mentorship.
4. **Local Database Scope:** SQLite is optimized for embedded, single-server institutional analytics. Enterprise multi-campus deployments would transition to client-server RDBMS (e.g., PostgreSQL).

---

## 📄 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👥 Author & Acknowledgements
Developed by **Harsh Thakur** as an MBA Decision Science & Business Analytics Portfolio Project.
For detailed system specifications, refer to [System Architecture](docs/ARCHITECTURE.md) and the [Data Dictionary](docs/DATA_DICTIONARY.md).
