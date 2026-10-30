# EduMetrics Data Dictionary & Dataset Specification

## 1. Overview & Ethical Considerations
The **EduMetrics** dataset contains approximately 500 records representing fictional postgraduate/business school students. All records are algorithmically generated using Python (`numpy.random` and `scipy.stats`) to reflect realistic institutional distributions while preserving full privacy.

> **Responsible AI Notice:** Fictional demographic attributes (e.g. `gender`) are simulated purely for demographic audit balance and are **never used as decision drivers** in individual student evaluations or predictive features.

---

## 2. Comprehensive Field Schema

| Column Name | Data Type | Permissible Values / Range | Nullable? | Description & Analytical Role |
|---|---|---|:---:|---|
| `student_id` | `TEXT` | Format: `EDU-2026-###` (e.g. `EDU-2026-001`) | No | Unique alphanumeric institutional identifier (Primary Key). |
| `student_name` | `TEXT` | Fictional full names (e.g. *Aarav Sharma*) | No | Fictional student name for reporting and profile display. |
| `gender` | `TEXT` | `Male`, `Female`, `Non-Binary` | No | Demographic category for equity audits (excluded from decision rules). |
| `specialization` | `TEXT` | `Business Analytics`, `Finance`, `Marketing`, `Operations & Supply Chain`, `Human Resources` | No | Academic major / departmental specialization. |
| `semester` | `TEXT` | `Semester 1`, `Semester 2`, `Semester 3`, `Semester 4` | No | Active curriculum semester of study. |
| `academic_percentage`| `REAL` | `0.0` to `100.0` (Typically $50.0 - 95.0\%$) | No | Aggregate examination score across enrolled coursework. |
| `attendance_percentage`| `REAL` | `0.0` to `100.0` (Typically $60.0 - 98.0\%$) | No | Classroom and lecture attendance compliance rate. Flagged if $< 75.0\%$. |
| `sql_proficiency` | `TEXT` | `Beginner`, `Intermediate`, `Advanced` | No | Self-reported and evaluated SQL query proficiency. |
| `python_proficiency` | `TEXT` | `Beginner`, `Intermediate`, `Advanced` | No | Self-reported and evaluated Python coding competence. |
| `power_bi_proficiency`| `TEXT` | `Beginner`, `Intermediate`, `Advanced` | No | Self-reported and evaluated Power BI dashboarding capability. |
| `certifications_count`| `INTEGER` | `0` to `5` | No | Number of verified industry credentials earned (e.g., AWS, Microsoft, CFA). |
| `internship_status` | `TEXT` | `Completed`, `Not Completed` | No | Completion status of required corporate summer internship. |
| `placement_status` | `TEXT` | `Placed`, `Unplaced` | No | Final recruitment outcome from campus hiring drives. |
| `company` | `TEXT` | Fictional corporate names (or `None`) | Yes | Hiring corporate partner name. Must be non-null if `Placed`, null if `Unplaced`. |
| `salary_lpa` | `REAL` | Continuous (typically $5.0 - 24.0$ LPA) | Yes | Annual Cost-to-Company compensation package in ₹ Lakhs Per Annum. Must be non-null if `Placed`, null if `Unplaced`. |

---

## 3. Derived Analytical Attributes

The application's data ingestion layer (`src/data_loader.py`) enriches the raw student schema with derived attributes:

1. **`grade_band` (`TEXT`):**
   * **Distinction ($\ge 80\%$):** Outstanding academic achievement.
   * **First Class ($65 - 79.9\%$):** Strong honors standing.
   * **Second Class ($50 - 64.9\%$):** Standard pass grade.
   * **Support Required ($< 50\%$):** Academic intervention required.

2. **`attendance_band` (`TEXT`):**
   * **High ($\ge 85\%$):** Exemplary discipline.
   * **Standard ($75 - 84.9\%$):** Compliant with institutional policy.
   * **Critical Alert ($< 75\%$):** Below regulatory minimum; attendance remediation triggered.

3. **`technical_score_10` (`REAL`):**
   * Composite competency score normalized on a $0 - 10$ point scale based on SQL, Python, and Power BI proficiency levels:
     $$\text{Technical Index} = \frac{\text{SQL} + \text{Python} + \text{Power BI}}{9} \times 10$$
     *(where Beginner = 1, Intermediate = 2, Advanced = 3)*.

4. **`is_academic_at_risk` (`BOOLEAN`):**
   * Flagged `True` if `academic_percentage < 55.0` OR `attendance_percentage < 75.0`.
