# EduMetrics System Architecture & Design Specification

## 1. System Overview
**EduMetrics** is engineered as a decoupled, multi-tier decision-support analytics platform. The application combines **Python 3.10+**, **Streamlit**, **Plotly**, and **SQLite 3** to provide educational leadership with an executive interface for academic monitoring, career placement intelligence, and econometric analysis.

---

## 2. Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│                 PRESENTATION LAYER (STREAMLIT)              │
│  app.py (Router & Global Slicing)                           │
│  views/ (Executive, Academic, Placement, Student, etc.)     │
│  ui_components.py (Custom CSS, Hero, KPI Cards, Footers)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  VISUALIZATION & RULES LAYER                │
│  visualizations.py (11 High-Contrast Plotly Visualizations) │
│  rules_engine.py (Deterministic Heuristic Diagnostic Engine)│
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    BUSINESS LOGIC LAYER                     │
│  metrics.py (Parametric & Non-Parametric Calculations)      │
│  data_loader.py (Validation, Cleansing, & Feature Eng.)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    PERSISTENCE & SQL LAYER                  │
│  src/database.py (ACID Ingestion & Analytical Queries)      │
│  database/schema.sql (3NF Normalized SQLite Schema)        │
│  database/edumetrics.db (Local Relational Database)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Relational Database Design (Third Normal Form - 3NF)

To enforce transactional integrity and prevent data anomalies, student records are decomposed across four relational tables:

1. **`students`**: Master entity storing enrollment identity and departmental major.
2. **`academic_records`**: Captures semester examination percentages, attendance compliance, and calculated performance tiers.
3. **`skills`**: Normalized tracking of technical tools (Python, SQL, Power BI), certifications count, and summer internship status.
4. **`placements`**: Corporate recruitment records including corporate hiring partner and annual compensation package (₹ LPA).

### Referential Integrity:
* **Foreign Key Cascade:** Child tables reference `students.student_id` with `ON DELETE CASCADE` to avoid orphaned records.
* **Domain Check Constraints:** Strict bounds ensure academic and attendance values remain within `[0.0, 100.0]`.
* **Secondary B-Tree Indexes:** Accelerate analytical queries filtering on `specialization`, `semester`, `attendance_percentage`, and `placement_status`.

---

## 4. Analytical & Econometric Methods

1. **Robust Measures of Central Tendency:**
   * Uses **Median** and **Interquartile Range (IQR = P75 - P25)** for compensation analytics to prevent skew from high package outliers.
2. **Hypothesis Testing:**
   * **Welch's Two-Sample t-Test:** Evaluates differences between Placed and Unplaced students without assuming equal cohort variances.
   * **Cohen's $d$ Effect Size:** Quantifies practical importance ($d \ge 0.8$ represents large managerial impact).
   * **One-Way ANOVA:** Tests whether academic performance varies significantly across specializations.
3. **Multivariate Econometric Demonstration:**
   * Fits a **Logistic Regression** model calculating odds ratios ($\text{OR} = e^\beta$) to measure how incremental improvements in marks, attendance, or skills shift placement odds.
