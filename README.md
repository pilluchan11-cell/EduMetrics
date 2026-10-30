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
* **SQLite Relational Sync:** Ingest student records into normalized SQLite tables with foreign key constraints.
* **Filtered Export:** One-click download of the active filtered cohort in CSV format.

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
