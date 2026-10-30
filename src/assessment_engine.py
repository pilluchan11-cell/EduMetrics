"""
Assessment and Career-Readiness Engine for EduMetrics.
Implements career-specific skill benchmarking, dynamic gap analysis,
explainable 6-pillar readiness scoring with missing-component handling,
and prioritized personalized learning roadmaps.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

from src.config import ATTENDANCE_CRITICAL_THRESHOLD, ACADEMIC_DISTINCTION_THRESHOLD
from src.benchmarks import (
    CAREER_ROLE_BENCHMARKS,
    DEFAULT_READINESS_WEIGHTS,
    COMPONENT_DISPLAY_NAMES,
    SKILL_LEVEL_NAMES,
    SKILL_NAME_TO_LEVEL,
    BENCHMARK_DISCLAIMER
)


def _safe_int(val: Any, default: int = 0) -> int:
    """Safely converts input to int, handling None and strings without throwing."""
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely converts input to float, handling None and strings without throwing."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def calculate_skill_gaps(student_skills: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """
    Compares the student's actual skill proficiencies against the selected career benchmark.
    
    Returns:
        Dict with:
        - target_role: str
        - role_desc: str
        - skill_comparison: List of dicts for each benchmark skill:
            {skill, student_level, student_name, target_level, target_name, gap, meets_benchmark, status}
        - total_required_points: int
        - student_matched_points: int
        - fit_percentage: float (0.0 - 100.0)
        - surplus_skills: List[str]
        - aligned_skills: List[str]
        - deficit_skills: List[str]
        - strongest_areas: List[str]
        - biggest_improvement_opportunities: List[Dict[str, Any]] (sorted by largest deficit)
    """
    role_config = CAREER_ROLE_BENCHMARKS.get(target_role, CAREER_ROLE_BENCHMARKS["Data Analyst"])
    benchmarks = role_config["skills"]
    
    comparisons = []
    total_req = 0
    matched_points = 0
    surplus = []
    aligned = []
    deficits = []
    
    for skill_name, target_lvl in benchmarks.items():
        # Retrieve student level; handle string names or ints safely
        raw_val = student_skills.get(skill_name, 1)
        if isinstance(raw_val, str):
            stu_lvl = SKILL_NAME_TO_LEVEL.get(raw_val.lower().strip(), 1)
        elif raw_val is None:
            stu_lvl = 1
        else:
            try:
                stu_lvl = int(raw_val)
            except (ValueError, TypeError):
                stu_lvl = 1
        stu_lvl = max(1, min(5, stu_lvl))
        
        gap = stu_lvl - target_lvl
        meets_benchmark = stu_lvl >= target_lvl
        total_req += target_lvl
        matched_points += min(stu_lvl, target_lvl)
        
        if gap > 0:
            status = f"Surplus (+{gap} Level{'s' if gap > 1 else ''})"
            surplus.append(skill_name)
        elif gap == 0:
            status = "Meets Benchmark"
            aligned.append(skill_name)
        else:
            status = f"Deficit ({abs(gap)} Level{'s' if abs(gap) > 1 else ''} Gap)"
            deficits.append(skill_name)
            
        comparisons.append({
            "skill": skill_name,
            "student_level": stu_lvl,
            "student_name": SKILL_LEVEL_NAMES.get(stu_lvl, "Beginner"),
            "target_level": target_lvl,
            "target_name": SKILL_LEVEL_NAMES.get(target_lvl, "Intermediate"),
            "gap": gap,
            "meets_benchmark": meets_benchmark,
            "status": status
        })
        
    fit_pct = round((matched_points / total_req) * 100.0, 1) if total_req > 0 else 0.0
    
    # Strongest areas: skills exceeding benchmark or rated >= 4
    strongest = [c["skill"] for c in comparisons if c["gap"] > 0 or c["student_level"] >= 4]
    if not strongest:
        # Fallback to top student rated skills
        top_sorted = sorted(comparisons, key=lambda x: x["student_level"], reverse=True)
        strongest = [top_sorted[0]["skill"]] if top_sorted else []
        
    # Biggest improvement opportunities: sorted by largest deficit (most negative gap)
    gap_sorted = sorted([c for c in comparisons if c["gap"] < 0], key=lambda x: x["gap"])
    
    return {
        "target_role": role_config["title"],
        "role_desc": role_config["description"],
        "skill_comparison": comparisons,
        "total_required_points": total_req,
        "student_matched_points": matched_points,
        "fit_percentage": fit_pct,
        "surplus_skills": surplus,
        "aligned_skills": aligned,
        "deficit_skills": deficits,
        "strongest_areas": strongest,
        "biggest_improvement_opportunities": gap_sorted
    }


def calculate_readiness_score(student_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """
    Computes an explainable, multi-dimensional Career Readiness Score (0-100)
    using the official initial weighting scheme:
    
    - Technical skills: 40%
    - Academic performance: 15%
    - Communication and aptitude: 15%
    - Certifications: 10%
    - Internship experience: 10%
    - Project experience: 10%
    
    MISSING COMPONENT HANDLING:
    If a component is missing/unrecorded, it is NOT silently treated as zero.
    The readiness index is dynamically recalculated using available components,
    normalizing their weights proportionally, and disclosing the exact coverage percentage.
    """
    weights = dict(DEFAULT_READINESS_WEIGHTS)
    available_components: Dict[str, Dict[str, Any]] = {}
    missing_components: List[str] = []
    
    skills = student_data.get("skills", {})
    gap_analysis = calculate_skill_gaps(skills, target_role)
    
    # 1. Technical Skills Component (Weight: 40%)
    if skills and len(skills) > 0:
        tech_score = gap_analysis["fit_percentage"]
        available_components["technical_skills"] = {
            "score": tech_score,
            "raw_weight": weights["technical_skills"],
            "description": f"{tech_score:.1f}% Benchmark Match ({gap_analysis['student_matched_points']}/{gap_analysis['total_required_points']} pts)"
        }
    else:
        missing_components.append("technical_skills")
        
    # 2. Academic Performance Component (Weight: 15%)
    raw_acad = student_data.get("academic_percentage")
    if raw_acad is not None and str(raw_acad).strip() != "" and float(raw_acad) > 0.0:
        acad_pct = float(raw_acad)
        # Piecewise normalization to 0-100
        if acad_pct >= 80.0:
            acad_score = 100.0
        elif acad_pct >= 70.0:
            acad_score = 85.0 + ((acad_pct - 70.0) / 10.0) * 15.0
        elif acad_pct >= 60.0:
            acad_score = 65.0 + ((acad_pct - 60.0) / 10.0) * 20.0
        elif acad_pct >= 50.0:
            acad_score = 45.0 + ((acad_pct - 50.0) / 10.0) * 20.0
        else:
            acad_score = max(20.0, (acad_pct / 50.0) * 45.0)
        acad_score = round(min(100.0, max(0.0, acad_score)), 1)
        available_components["academic_performance"] = {
            "score": acad_score,
            "raw_weight": weights["academic_performance"],
            "description": f"{acad_pct:.1f}% Aggregate Marks"
        }
    else:
        missing_components.append("academic_performance")
        
    # 3. Communication and Aptitude Component (Weight: 15%)
    comm_val = student_data.get("communication_level") or skills.get("Communication")
    apt_val = student_data.get("aptitude_level") or skills.get("Problem-solving")
    
    if comm_val is not None or apt_val is not None:
        c_lvl = int(comm_val if comm_val is not None else 3)
        a_lvl = int(apt_val if apt_val is not None else 3)
        c_lvl = max(1, min(5, c_lvl))
        a_lvl = max(1, min(5, a_lvl))
        
        # 50 points from communication (1-5), 50 points from aptitude (1-5)
        soft_score = round(((c_lvl / 5.0) * 50.0) + ((a_lvl / 5.0) * 50.0), 1)
        available_components["communication_aptitude"] = {
            "score": soft_score,
            "raw_weight": weights["communication_aptitude"],
            "description": f"Comm: {c_lvl}/5 ({SKILL_LEVEL_NAMES[c_lvl]}) | Aptitude: {a_lvl}/5 ({SKILL_LEVEL_NAMES[a_lvl]})"
        }
    else:
        missing_components.append("communication_aptitude")
        
    # 4. Certifications Component (Weight: 10%)
    certs = student_data.get("certifications")
    certs_provided = student_data.get("certifications_provided", True)
    
    if certs_provided and certs is not None:
        cert_count = len(certs) if isinstance(certs, list) else int(student_data.get("certifications_count", 0))
        if cert_count >= 3:
            cert_score = 100.0
        elif cert_count == 2:
            cert_score = 85.0
        elif cert_count == 1:
            cert_score = 65.0
        else:
            cert_score = 30.0 # Base credit for formal curriculum
        available_components["certifications"] = {
            "score": cert_score,
            "raw_weight": weights["certifications"],
            "description": f"{cert_count} Completed Credential{'s' if cert_count != 1 else ''}"
        }
    else:
        missing_components.append("certifications")
        
    # 5. Internship Experience Component (Weight: 10%)
    intern_stat = student_data.get("internship_status")
    intern_provided = student_data.get("internship_provided", True)
    
    if intern_provided and intern_stat is not None and str(intern_stat).strip() != "":
        stat_lower = str(intern_stat).lower()
        if "completed" in stat_lower and "not" not in stat_lower:
            intern_score = 100.0
            desc = "Corporate Internship Completed"
        else:
            intern_score = 35.0
            desc = "No Corporate Internship Recorded"
        available_components["internship_experience"] = {
            "score": intern_score,
            "raw_weight": weights["internship_experience"],
            "description": desc
        }
    else:
        missing_components.append("internship_experience")
        
    # 6. Project Experience Component (Weight: 10%)
    proj_count = student_data.get("projects_count")
    proj_provided = student_data.get("projects_provided", True)
    
    if proj_provided and proj_count is not None:
        try:
            p_cnt = int(proj_count)
        except (ValueError, TypeError):
            p_cnt = 0
            
        if p_cnt >= 3:
            proj_score = 100.0
        elif p_cnt == 2:
            proj_score = 80.0
        elif p_cnt == 1:
            proj_score = 60.0
        else:
            proj_score = 25.0
        available_components["project_experience"] = {
            "score": proj_score,
            "raw_weight": weights["project_experience"],
            "description": f"{p_cnt} Documented Applied Project{'s' if p_cnt != 1 else ''}"
        }
    else:
        missing_components.append("project_experience")

    # -------------------------------------------------------------------------
    # Recalculate weights based on available components (Coverage Handling)
    # -------------------------------------------------------------------------
    total_raw_weight = sum(info["raw_weight"] for info in available_components.values())
    coverage_percentage = round((total_raw_weight / 1.00) * 100.0, 1)
    
    if total_raw_weight > 0:
        overall_score = 0.0
        components_breakdown = {}
        for comp_key, info in available_components.items():
            # Normalized adjusted weight
            adj_weight = info["raw_weight"] / total_raw_weight
            weighted_points = info["score"] * adj_weight
            overall_score += weighted_points
            
            components_breakdown[COMPONENT_DISPLAY_NAMES.get(comp_key, comp_key)] = {
                "score": round(info["score"], 1),
                "base_weight_pct": int(info["raw_weight"] * 100),
                "adjusted_weight_pct": round(adj_weight * 100.0, 1),
                "weighted_points": round(weighted_points, 1),
                "status": "Available",
                "description": info["description"]
            }
            
        # Add missing components with explicit notation
        for m_key in missing_components:
            components_breakdown[COMPONENT_DISPLAY_NAMES.get(m_key, m_key)] = {
                "score": None,
                "base_weight_pct": int(weights[m_key] * 100),
                "adjusted_weight_pct": 0.0,
                "weighted_points": 0.0,
                "status": "Not Provided",
                "description": "Component excluded from score; weight redistributed across available dimensions."
            }
        overall_score = round(min(100.0, max(0.0, overall_score)), 1)
    else:
        overall_score = 0.0
        components_breakdown = {}
        
    # Band Designation
    if overall_score >= 80.0:
        tier_label = "Placement Ready / Highly Competitive"
        tier_color = "#10B981" # Emerald Green
        tier_summary = "Candidate demonstrates comprehensive alignment with corporate recruiter benchmarks across evaluated dimensions."
    elif overall_score >= 65.0:
        tier_label = "Near Ready / Minor Skill Gaps"
        tier_color = "#2563EB" # Royal Blue
        tier_summary = "Candidate satisfies core corporate criteria. Closing 1-2 targeted technical and portfolio deficits will elevate candidacy."
    elif overall_score >= 50.0:
        tier_label = "Developing / Moderate Intervention Required"
        tier_color = "#F59E0B" # Amber
        tier_summary = "Candidate requires structured development across technical tool proficiency, certifications, and portfolio projects."
    else:
        tier_label = "Early Stage / High Priority Support"
        tier_color = "#EF4444" # Crimson Red
        tier_summary = "Structured foundational remediation is recommended to reach minimum corporate screening criteria."

    return {
        "overall_score": overall_score,
        "tier_label": tier_label,
        "tier_color": tier_color,
        "tier_summary": tier_summary,
        "coverage_percentage": coverage_percentage,
        "available_component_count": len(available_components),
        "total_component_count": len(DEFAULT_READINESS_WEIGHTS),
        "missing_components": [COMPONENT_DISPLAY_NAMES.get(k, k) for k in missing_components],
        "components": components_breakdown,
        "gap_analysis": gap_analysis,
        "disclaimer": BENCHMARK_DISCLAIMER
    }


def generate_learning_roadmap(gap_analysis: Dict[str, Any], student_data: Dict[str, Any], target_role: str) -> List[Dict[str, Any]]:
    """
    Generates a prioritized, structured learning roadmap based on the candidate's largest skill gaps.
    Includes specific learning objectives, practical project suggestions, and estimated timelines.
    """
    roadmap = []
    priority_num = 1
    
    # 1. Deficit Skills (Ordered by largest gap first)
    deficits = gap_analysis.get("biggest_improvement_opportunities", [])
    
    # Knowledge base of targeted objectives and project suggestions
    skill_curriculum = {
        "SQL": {
            "title": "Advanced SQL & Relational Database Engineering",
            "objectives": [
                "Master window functions (ROW_NUMBER, DENSE_RANK, NTILE, LAG/LEAD) for financial and analytical reporting.",
                "Construct multi-level Common Table Expressions (CTEs) and recursive queries for hierarchical data.",
                "Perform query execution plan analysis, index optimization, and database normalization (3NF)."
            ],
            "project": "Build an analytical retail data warehouse in PostgreSQL or SQLite analyzing 100,000+ sales transactions, computing RFM customer segmentations, and hosting query scripts on GitHub.",
            "duration": "2 to 3 Weeks"
        },
        "Python": {
            "title": "Python for Data Analysis & Statistical Modeling",
            "objectives": [
                "Master Pandas vectorization, multi-index aggregation, and categorical data wrangling.",
                "Build end-to-end data pipelines incorporating NumPy numerical operations and SciPy statistical tests.",
                "Implement reproducible Jupyter notebooks with clean functional code and docstrings."
            ],
            "project": "Develop an automated exploratory data analysis (EDA) and churn prediction script on a public telco dataset, comparing logistic regression and tree-based baselines.",
            "duration": "3 to 4 Weeks"
        },
        "Power BI": {
            "title": "Power BI Enterprise Dashboarding & DAX Modeling",
            "objectives": [
                "Architect star-schema dimensional models with clear one-to-many relationship cardinality.",
                "Write intermediate to advanced DAX formulas (CALCULATE, FILTER, ALLSELECTED, Time Intelligence).",
                "Design responsive executive layouts following corporate visual hierarchy principles."
            ],
            "project": "Design and publish a multi-page C-suite Financial Operations Cockpit on NovyPro/GitHub featuring dynamic currency toggles, drill-through pages, and executive KPI cards.",
            "duration": "2 Weeks"
        },
        "Tableau": {
            "title": "Tableau Visual Storytelling & Analytics",
            "objectives": [
                "Master Level of Detail (LOD) calculations (FIXED, INCLUDE, EXCLUDE).",
                "Create dynamic parameters, sets, and user-driven dashboard actions.",
                "Format executive presentation stories highlighting commercial takeaways."
            ],
            "project": "Publish an interactive Tableau Public dashboard analyzing global supply chain logistics delays and freight cost elasticity.",
            "duration": "2 Weeks"
        },
        "Excel": {
            "title": "Advanced Business Modeling in Microsoft Excel",
            "objectives": [
                "Master modern dynamic array formulas: XLOOKUP, FILTER, UNIQUE, and LET functions.",
                "Build dynamic sensitivity tables and scenario managers for financial planning.",
                "Implement clean data validation controls and executive summary dashboards."
            ],
            "project": "Construct a comprehensive 3-statement financial model and discounted cash flow (DCF) valuation workbook with dynamic sensitivity switches.",
            "duration": "1 to 2 Weeks"
        },
        "Statistics": {
            "title": "Applied Business Statistics & Hypothesis Testing",
            "objectives": [
                "Conduct and interpret parametric and non-parametric hypothesis tests (two-sample t-tests, ANOVA, Chi-Square).",
                "Calculate and explain effect sizes (Cohen's d), p-values, and 95% confidence intervals.",
                "Perform multivariate linear regression and diagnose multicollinearity (VIF)."
            ],
            "project": "Publish a comprehensive statistical research report evaluating customer purchase patterns across test/control groups with full Python Scipy code and executive findings.",
            "duration": "2 to 3 Weeks"
        },
        "Machine Learning": {
            "title": "Supervised Machine Learning & Model Evaluation",
            "objectives": [
                "Formulate classification and regression problems with proper train-test validation splits.",
                "Train and tune scikit-learn models (logistic regression, decision trees, random forests, gradient boosting).",
                "Evaluate models using ROC-AUC, Precision-Recall curves, confusion matrices, and SHAP explainability."
            ],
            "project": "Develop an end-to-end credit default risk prediction system, packaging the trained pipeline into an interactive Streamlit diagnostic demo app.",
            "duration": "3 to 4 Weeks"
        },
        "Mathematics": {
            "title": "Mathematical Foundations for Data Science",
            "objectives": [
                "Master multivariable calculus concepts: gradients, partial derivatives, and gradient descent optimization.",
                "Understand linear algebra fundamentals: matrix multiplication, eigenvalues, eigenvectors, and PCA dimensionality reduction.",
                "Formulate mathematical loss functions and cost function minimization."
            ],
            "project": "Implement principal component analysis (PCA) and linear regression from mathematical scratch in Python (NumPy only) without external ML libraries.",
            "duration": "3 Weeks"
        },
        "Communication": {
            "title": "Executive Business Storytelling & Technical Pitching",
            "objectives": [
                "Translate complex quantitative metrics into non-technical corporate business recommendations.",
                "Structure persuasive presentations using the Pyramid Principle (Situation-Complication-Resolution).",
                "Present live dashboard walkthroughs with concise verbal articulation."
            ],
            "project": "Record a 5-minute executive video walkthrough of an analytics dashboard, presenting specific budget reallocation recommendations to hypothetical business leaders.",
            "duration": "1 to 2 Weeks"
        },
        "Problem-solving": {
            "title": "Structured Business Problem Formulation & Case Analysis",
            "objectives": [
                "Deconstruct ambiguous business problems into mutually exclusive, collectively exhaustive (MECE) issue trees.",
                "Conduct profitability and market-entry case calculations under time pressure.",
                "Synthesize data findings into strategic actionable trade-offs."
            ],
            "project": "Author a structured 5-page business management case study analyzing a market turnaround strategy with quantitative supporting tables.",
            "duration": "2 Weeks"
        },
        "Data Modeling / ETL": {
            "title": "Data Modeling & ETL Data Pipeline Engineering",
            "objectives": [
                "Design dimensional star schemas, fact tables, and slowly changing dimensions (SCD Type 1 & 2).",
                "Write automated Python ETL scripts extract-transforming APIs and CSVs into relational databases.",
                "Implement data validation checks and schema enforcement."
            ],
            "project": "Build an automated daily data pipeline ingesting public economic indicators into a SQLite/PostgreSQL warehouse with automated logging.",
            "duration": "2 to 3 Weeks"
        },
        "Product Metrics / A/B Testing": {
            "title": "Product Telemetry & Controlled Experimentation",
            "objectives": [
                "Design two-tailed A/B experiments: sample size estimation, statistical power ($1-\\beta$), and minimum detectable effect (MDE).",
                "Analyze user engagement telemetry: DAU/MAU, user retention cohorts, and LTV/CAC ratios.",
                "Synthesize experiment results into Go / No-Go feature launch recommendations."
            ],
            "project": "Analyze a randomized A/B test dataset from an e-commerce checkout funnel, computing p-values, confidence intervals, and authoring an executive launch decision memo.",
            "duration": "2 to 3 Weeks"
        }
    }
    
    # Add deficit skills to roadmap
    for d in deficits:
        skill_name = d["skill"]
        details = skill_curriculum.get(skill_name, {
            "title": f"{skill_name} Competency Advancement",
            "objectives": [f"Deepen mastery of {skill_name} from Level {d['student_level']} to Level {d['target_level']}."],
            "project": f"Build a comprehensive portfolio project demonstrating applied {skill_name} in a business context.",
            "duration": "2 to 3 Weeks"
        })
        
        roadmap.append({
            "priority": priority_num,
            "category": "Technical Competency",
            "title": f"Priority {priority_num}: {details['title']}",
            "skill": skill_name,
            "current_status": f"{d['student_name']} (L{d['student_level']})",
            "target_status": f"{d['target_name']} (L{d['target_level']})",
            "gap_size": abs(d["gap"]),
            "objectives": details["objectives"],
            "practical_project": details["project"],
            "duration": details["duration"]
        })
        priority_num += 1

    # 2. Add Practical Project Portfolio Priority if projects < 2
    proj_count = _safe_int(student_data.get("projects_count"), 0)
    if proj_count < 2:
        role_projects = CAREER_ROLE_BENCHMARKS.get(target_role, {}).get("sample_project_ideas", [
            f"End-to-end {target_role} analytics case study with public GitHub documentation."
        ])
        roadmap.append({
            "priority": priority_num,
            "category": "Portfolio & Applied Experience",
            "title": f"Priority {priority_num}: Public Analytics Portfolio Development",
            "skill": "Project Experience",
            "current_status": f"{proj_count} Completed Projects",
            "target_status": "2+ Documented Projects",
            "gap_size": max(1, 2 - proj_count),
            "objectives": [
                f"Develop at least 2 distinct analytics case studies solving real-world challenges relevant to {target_role}.",
                "Publish all clean Python scripts, SQL queries, or dashboard pbix files to a structured public GitHub repository.",
                "Author comprehensive README summaries walking through business context, data cleaning, and actionable takeaways."
            ],
            "practical_project": f"Recommended Project: {role_projects[0]}",
            "duration": "3 to 4 Weeks"
        })
        priority_num += 1

    # 3. Add Industry Certification Priority if certs == 0
    certs = student_data.get("certifications", [])
    if not certs:
        role_certs = CAREER_ROLE_BENCHMARKS.get(target_role, {}).get("key_certifications", ["Google Data Analytics Professional Certificate"])
        roadmap.append({
            "priority": priority_num,
            "category": "Industry Credentialing",
            "title": f"Priority {priority_num}: Verified Professional Credential",
            "skill": "Certifications",
            "current_status": "0 Completed Certifications",
            "target_status": "1+ Verified Credentials",
            "gap_size": 1,
            "objectives": [
                f"Enroll in and complete {role_certs[0]} to validate technical proficiency.",
                "Showcase credential badges on LinkedIn and executive resumes to improve preliminary corporate recruiter screening rates."
            ],
            "practical_project": f"Complete all hands-on capstone assessments required for {role_certs[0]}.",
            "duration": "4 to 6 Weeks"
        })
        priority_num += 1

    return roadmap


def generate_individual_assessment(student_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """
    Main evaluation pipeline producing benchmark gap comparisons, explainable readiness index,
    strengths, weaknesses, prioritized learning roadmap, and actionable recommendations.
    """
    readiness = calculate_readiness_score(student_data, target_role)
    gap_analysis = readiness["gap_analysis"]
    roadmap = generate_learning_roadmap(gap_analysis, student_data, target_role)
    
    strengths = []
    weaknesses = []
    recommendations = []
    
    # 1. Academic Strengths / Weaknesses
    raw_acad = student_data.get("academic_percentage")
    if raw_acad is not None and float(raw_acad) > 0:
        acad_pct = float(raw_acad)
        if acad_pct >= ACADEMIC_DISTINCTION_THRESHOLD:
            strengths.append(f"Distinct academic standing with {acad_pct:.1f}% aggregate marks (Premier screening tier).")
        elif acad_pct >= 60.0:
            strengths.append(f"Solid academic track record with {acad_pct:.1f}% aggregate, meeting standard corporate eligibility cutoffs.")
        else:
            weaknesses.append(f"Academic aggregate is {acad_pct:.1f}%, below the standard 60.0% corporate screening cutoff.")
            recommendations.append({
                "category": "Academic Remediation",
                "priority": "High",
                "action": "Prioritize upcoming semester examinations and internal submissions to elevate cumulative score toward 60%+.",
                "rationale": "Major corporate recruiters enforce a mandatory 60% graduation/semester cutoff to filter screening test applicants."
            })
    else:
        weaknesses.append("Academic marks are currently unrecorded in candidate profile.")

    # 2. Attendance Compliance
    raw_att = student_data.get("attendance_percentage")
    if raw_att is not None and float(raw_att) > 0:
        att_pct = float(raw_att)
        if att_pct >= 85.0:
            strengths.append(f"Exemplary classroom attendance at {att_pct:.1f}%, reflecting disciplined professional commitment.")
        elif att_pct >= ATTENDANCE_CRITICAL_THRESHOLD:
            strengths.append(f"Classroom attendance compliant at {att_pct:.1f}% (above institutional {ATTENDANCE_CRITICAL_THRESHOLD:.1f}% cutoff).")
        else:
            weaknesses.append(f"Attendance at {att_pct:.1f}% violates the mandatory {ATTENDANCE_CRITICAL_THRESHOLD:.1f}% institutional cutoff.")
            recommendations.append({
                "category": "Attendance Compliance",
                "priority": "Critical",
                "action": "Meet with your faculty academic mentor immediately and attend scheduled makeup sessions to lift attendance above 75.0%.",
                "rationale": "Students falling below 75% attendance risk formal debarment from semester exams and campus placement drives."
            })

    # 3. Benchmark Deficit Skills
    for d in gap_analysis["biggest_improvement_opportunities"]:
        skill = d["skill"]
        gap = abs(d["gap"])
        weaknesses.append(f"Competency deficit in {skill}: candidate is {d['student_name']} (L{d['student_level']}) vs {d['target_name']} (L{d['target_level']}) required for {target_role}.")
        
    for s_name in gap_analysis["surplus_skills"]:
        strengths.append(f"Advanced proficiency in {s_name}, exceeding the benchmark requirements for {target_role}.")

    # 4. Certifications
    certs = student_data.get("certifications", [])
    if certs:
        strengths.append(f"Holds {len(certs)} verified certification(s): {', '.join(certs[:2])}.")
    else:
        weaknesses.append("No active industry certifications recorded on candidate profile.")

    # 5. Internship & Projects
    internship_done = str(student_data.get("internship_status", "")).lower() == "completed"
    if internship_done:
        co = student_data.get("internship_company", "")
        co_str = f" at {co}" if co else ""
        strengths.append(f"Completed verified corporate summer internship{co_str}, providing workplace experience.")
    else:
        weaknesses.append("Lacks corporate summer internship experience on candidate profile.")

    proj_cnt = _safe_int(student_data.get("projects_count"), 0)
    if proj_cnt >= 2:
        strengths.append(f"Documented portfolio with {proj_cnt} completed applied analytics projects.")
    else:
        weaknesses.append(f"Limited project portfolio ({proj_cnt} completed project{'s' if proj_cnt != 1 else ''}).")

    # Compile recommendations from roadmap priorities
    for item in roadmap[:4]:
        recommendations.append({
            "category": item["title"],
            "priority": "Critical" if item["priority"] == 1 and item.get("gap_size", 0) >= 2 else ("High" if item["priority"] <= 2 else "Medium"),
            "action": f"{item['practical_project']}",
            "rationale": f"Addresses {item['skill']} deficit ({item['current_status']} → {item['target_status']}) with a {item['duration']} sprint."
        })

    return {
        "student_data": student_data,
        "target_role": target_role,
        "readiness": readiness,
        "gap_analysis": gap_analysis,
        "learning_roadmap": roadmap,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "disclaimer": BENCHMARK_DISCLAIMER
    }


def get_sample_student_profile(sample_type: str = "balanced") -> Dict[str, Any]:
    """
    Returns realistic sample student dictionaries for testing and 1-click demonstration.
    """
    if sample_type == "high_achiever":
        return {
            "student_id": "EDU-2026-901",
            "student_name": "Aarav Sharma",
            "gender": "Male",
            "specialization": "Business Analytics",
            "semester": "Semester 3",
            "academic_year": "2025-2026",
            "tenth_percentage": 88.5,
            "twelfth_percentage": 86.0,
            "grad_percentage": 78.5,
            "cgpa": 8.6,
            "cgpa_scale": 10.0,
            "academic_percentage": 86.0,
            "subject_marks": {
                "Business Statistics": 88.0,
                "SQL & Relational Databases": 90.0,
                "Python for Analytics": 85.0,
                "Predictive Modeling": 84.0,
                "Financial Management": 83.0
            },
            "attendance_percentage": 92.5,
            "skills": {
                "Excel": 5,
                "SQL": 5,
                "Python": 4,
                "Power BI": 4,
                "Tableau": 4,
                "Statistics": 4,
                "Machine Learning": 3,
                "Mathematics": 4,
                "Problem-solving": 5,
                "Communication": 4,
                "Data Visualization": 4,
                "Data Modeling / ETL": 4
            },
            "certifications": [
                "Microsoft Power BI Data Analyst (PL-300)",
                "Google Data Analytics Professional Certificate",
                "SQL for Data Science"
            ],
            "certifications_count": 3,
            "certifications_provided": True,
            "internship_status": "Completed",
            "internship_provided": True,
            "internship_company": "Deloitte Analytics",
            "internship_duration_months": 2,
            "project_experience": "End-to-end customer churn prediction and retail revenue dashboard in Power BI and scikit-learn.",
            "projects_count": 3,
            "projects_provided": True,
            "resume_status": "Ready / Verified",
            "communication_level": 4,
            "aptitude_level": 5,
            "interview_status": "Multiple Mocks Completed",
            "placement_status": "In Process",
            "target_role": "Data Analyst"
        }
    elif sample_type == "needs_intervention":
        return {
            "student_id": "EDU-2026-902",
            "student_name": "Kavya Patel",
            "gender": "Female",
            "specialization": "Finance",
            "semester": "Semester 3",
            "academic_year": "2025-2026",
            "tenth_percentage": 72.0,
            "twelfth_percentage": 68.0,
            "grad_percentage": 58.0,
            "cgpa": 5.8,
            "cgpa_scale": 10.0,
            "academic_percentage": 58.0,
            "subject_marks": {
                "Corporate Finance": 64.0,
                "Financial Modeling": 54.0,
                "Business Statistics": 50.0,
                "Database Concepts": 52.0,
                "Marketing Fundamentals": 68.0
            },
            "attendance_percentage": 71.0,
            "skills": {
                "Excel": 3,
                "SQL": 2,
                "Python": 1,
                "Power BI": 2,
                "Tableau": 1,
                "Statistics": 2,
                "Machine Learning": 1,
                "Mathematics": 2,
                "Problem-solving": 2,
                "Communication": 3,
                "Data Visualization": 2,
                "Data Modeling / ETL": 1
            },
            "certifications": [],
            "certifications_count": 0,
            "certifications_provided": True,
            "internship_status": "Not Completed",
            "internship_provided": True,
            "internship_company": "",
            "internship_duration_months": 0,
            "project_experience": "Classroom spreadsheet assignment analyzing quarterly balance sheets.",
            "projects_count": 0,
            "projects_provided": True,
            "resume_status": "Draft",
            "communication_level": 3,
            "aptitude_level": 2,
            "interview_status": "Not Started",
            "placement_status": "Unplaced",
            "target_role": "Business Analyst"
        }
    elif sample_type == "missing_components":
        # Demonstrates missing components calculation (No project and no internship provided)
        return {
            "student_id": "EDU-2026-904",
            "student_name": "Meera Joshi",
            "gender": "Female",
            "specialization": "Business Analytics",
            "semester": "Semester 2",
            "academic_year": "2025-2026",
            "tenth_percentage": 84.0,
            "twelfth_percentage": 82.0,
            "grad_percentage": 74.0,
            "cgpa": 7.8,
            "cgpa_scale": 10.0,
            "academic_percentage": 78.0,
            "subject_marks": {},
            "attendance_percentage": 88.0,
            "skills": {
                "Excel": 4,
                "SQL": 4,
                "Python": 3,
                "Power BI": 3,
                "Tableau": 2,
                "Statistics": 4,
                "Machine Learning": 2,
                "Mathematics": 3,
                "Problem-solving": 4,
                "Communication": 4,
                "Data Visualization": 3
            },
            "certifications": ["Google Data Analytics Professional Certificate"],
            "certifications_count": 1,
            "certifications_provided": True,
            "internship_status": None, # Missing component!
            "internship_provided": False,
            "internship_company": "",
            "internship_duration_months": 0,
            "project_experience": "",
            "projects_count": None, # Missing component!
            "projects_provided": False,
            "resume_status": "Reviewed",
            "communication_level": 4,
            "aptitude_level": 4,
            "interview_status": "1 Mock Interview",
            "placement_status": "Unplaced",
            "target_role": "Data Analyst"
        }
    else: # balanced / average profile
        return {
            "student_id": "EDU-2026-903",
            "student_name": "Rohan Verma",
            "gender": "Male",
            "specialization": "Business Analytics",
            "semester": "Semester 3",
            "academic_year": "2025-2026",
            "tenth_percentage": 81.0,
            "twelfth_percentage": 76.5,
            "grad_percentage": 69.0,
            "cgpa": 7.2,
            "cgpa_scale": 10.0,
            "academic_percentage": 72.0,
            "subject_marks": {
                "Business Analytics": 74.0,
                "SQL Querying": 76.0,
                "Python Programming": 68.0,
                "Statistics for Managers": 70.0,
                "Operations Analytics": 72.0
            },
            "attendance_percentage": 79.0,
            "skills": {
                "Excel": 4,
                "SQL": 3,
                "Python": 2,
                "Power BI": 3,
                "Tableau": 2,
                "Statistics": 3,
                "Machine Learning": 2,
                "Mathematics": 3,
                "Problem-solving": 3,
                "Communication": 3,
                "Data Visualization": 3,
                "Data Modeling / ETL": 2
            },
            "certifications": [
                "Google Data Analytics Professional Certificate"
            ],
            "certifications_count": 1,
            "certifications_provided": True,
            "internship_status": "Not Completed",
            "internship_provided": True,
            "internship_company": "",
            "internship_duration_months": 0,
            "project_experience": "Exploratory data analysis on hospital emergency room admissions using Excel and SQL.",
            "projects_count": 1,
            "projects_provided": True,
            "resume_status": "Reviewed",
            "communication_level": 3,
            "aptitude_level": 3,
            "interview_status": "1 Mock Interview",
            "placement_status": "Unplaced",
            "target_role": "Data Analyst"
        }
