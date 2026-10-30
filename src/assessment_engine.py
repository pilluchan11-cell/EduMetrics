"""
Assessment and Career-Readiness Engine for EduMetrics.
Provides role-specific competency benchmarking, skill gap analysis, explainable readiness scoring,
and targeted, deterministic recommendation generation.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from src.config import ATTENDANCE_CRITICAL_THRESHOLD, ACADEMIC_DISTINCTION_THRESHOLD

# 5-point skill level definitions
SKILL_LEVEL_NAMES = {
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert"
}

SKILL_NAME_TO_LEVEL = {
    "beginner": 1,
    "basic": 2,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5
}

# Standard Career Roles and their benchmark competency matrices (1-5 scale)
CAREER_ROLE_BENCHMARKS = {
    "Data Analyst": {
        "title": "Data Analyst",
        "description": "Transforms business data into actionable dashboards, KPIs, and statistical insights for decision-makers.",
        "skills": {
            "SQL": 4,           # Advanced
            "Excel": 4,         # Advanced
            "Power BI": 4,      # Advanced
            "Python": 3,        # Intermediate
            "Tableau": 3,       # Intermediate
            "Statistics": 3,    # Intermediate
            "Machine Learning": 2, # Basic
            "Communication": 4  # Proficient
        },
        "key_certifications": [
            "Microsoft Power BI Data Analyst (PL-300)",
            "Google Data Analytics Professional Certificate",
            "SQL for Data Science"
        ],
        "recommended_projects": 2,
        "weights": {
            "academic": 0.15,
            "attendance": 0.10,
            "technical_fit": 0.35,
            "certifications": 0.10,
            "experience": 0.15,
            "soft_skills": 0.15
        }
    },
    "Business Analyst": {
        "title": "Business Analyst",
        "description": "Bridges corporate stakeholders and technical teams through business requirements, process models, and metrics.",
        "skills": {
            "Excel": 4,         # Advanced
            "SQL": 3,           # Intermediate
            "Power BI": 3,      # Intermediate
            "Tableau": 3,       # Intermediate
            "Communication": 5, # Exceptional
            "Statistics": 2,    # Basic
            "Python": 2,        # Basic
            "Machine Learning": 1 # Beginner
        },
        "key_certifications": [
            "IBM Data Analyst",
            "Microsoft Power BI Data Analyst (PL-300)",
            "Google Data Analytics Professional Certificate"
        ],
        "recommended_projects": 2,
        "weights": {
            "academic": 0.20,
            "attendance": 0.10,
            "technical_fit": 0.25,
            "certifications": 0.10,
            "experience": 0.15,
            "soft_skills": 0.20
        }
    },
    "Data Scientist": {
        "title": "Data Scientist",
        "description": "Applies statistical algorithms, machine learning models, and predictive analytics to solve complex business problems.",
        "skills": {
            "Python": 5,        # Expert
            "Statistics": 5,    # Expert
            "Machine Learning": 4, # Advanced
            "SQL": 4,           # Advanced
            "Excel": 3,         # Intermediate
            "Power BI": 2,      # Basic
            "Tableau": 2,       # Basic
            "Communication": 3  # Competent
        },
        "key_certifications": [
            "Python Data Structures & Applied Analytics",
            "Google Data Analytics Professional Certificate",
            "SQL for Data Science"
        ],
        "recommended_projects": 3,
        "weights": {
            "academic": 0.20,
            "attendance": 0.10,
            "technical_fit": 0.40,
            "certifications": 0.10,
            "experience": 0.10,
            "soft_skills": 0.10
        }
    },
    "Business Intelligence Analyst": {
        "title": "Business Intelligence Analyst",
        "description": "Architects enterprise data models, ETL semantic layers, and executive decision-support reporting suites.",
        "skills": {
            "Power BI": 5,      # Expert
            "SQL": 4,           # Advanced
            "Tableau": 4,       # Advanced
            "Excel": 4,         # Advanced
            "Statistics": 3,    # Intermediate
            "Python": 2,        # Basic
            "Communication": 4, # Proficient
            "Machine Learning": 1 # Beginner
        },
        "key_certifications": [
            "Microsoft Power BI Data Analyst (PL-300)",
            "SQL for Data Science",
            "IBM Data Analyst"
        ],
        "recommended_projects": 2,
        "weights": {
            "academic": 0.15,
            "attendance": 0.10,
            "technical_fit": 0.35,
            "certifications": 0.15,
            "experience": 0.15,
            "soft_skills": 0.10
        }
    },
    "Product Analyst": {
        "title": "Product Analyst",
        "description": "Analyzes digital product engagement, user retention funnels, A/B experiments, and feature adoption metrics.",
        "skills": {
            "SQL": 4,           # Advanced
            "Statistics": 4,    # Advanced
            "Python": 3,        # Intermediate
            "Excel": 4,         # Advanced
            "Power BI": 3,      # Intermediate
            "Communication": 4, # Proficient
            "Tableau": 3,       # Intermediate
            "Machine Learning": 2 # Basic
        },
        "key_certifications": [
            "Google Data Analytics Professional Certificate",
            "SQL for Data Science",
            "Python Data Structures & Applied Analytics"
        ],
        "recommended_projects": 2,
        "weights": {
            "academic": 0.15,
            "attendance": 0.10,
            "technical_fit": 0.30,
            "certifications": 0.10,
            "experience": 0.20,
            "soft_skills": 0.15
        }
    }
}


def calculate_skill_gaps(student_skills: Dict[str, int], target_role: str) -> Dict[str, Any]:
    """
    Computes competency gaps between student skill levels and target career role benchmarks.
    
    Returns:
        dict containing:
        - target_role: role title
        - role_desc: role description
        - skill_comparison: list of {skill, student_level, student_name, target_level, target_name, gap, status}
        - total_required_points: int
        - student_matched_points: int
        - fit_percentage: float (0.0 to 100.0)
        - surplus_skills: list of skill names where student exceeds requirements
        - deficit_skills: list of skill names where student requires development
        - aligned_skills: list of skill names meeting exact requirement
    """
    role_config = CAREER_ROLE_BENCHMARKS.get(target_role, CAREER_ROLE_BENCHMARKS["Data Analyst"])
    benchmarks = role_config["skills"]
    
    comparisons = []
    total_req = 0
    matched_points = 0
    surplus = []
    deficit = []
    aligned = []
    
    for skill_name, target_lvl in benchmarks.items():
        stu_lvl = student_skills.get(skill_name, 1)
        gap = stu_lvl - target_lvl
        total_req += target_lvl
        matched_points += min(stu_lvl, target_lvl)
        
        if gap > 0:
            status = "Surplus / Exceeds Target"
            surplus.append(skill_name)
        elif gap == 0:
            status = "Meets Target"
            aligned.append(skill_name)
        else:
            status = f"Deficit ({abs(gap)} Level{'s' if abs(gap) > 1 else ''} Gap)"
            deficit.append(skill_name)
            
        comparisons.append({
            "skill": skill_name,
            "student_level": stu_lvl,
            "student_name": SKILL_LEVEL_NAMES.get(stu_lvl, "Beginner"),
            "target_level": target_lvl,
            "target_name": SKILL_LEVEL_NAMES.get(target_lvl, "Intermediate"),
            "gap": gap,
            "status": status
        })
        
    fit_pct = round((matched_points / total_req) * 100.0, 1) if total_req > 0 else 0.0
    
    return {
        "target_role": role_config["title"],
        "role_desc": role_config["description"],
        "skill_comparison": comparisons,
        "total_required_points": total_req,
        "student_matched_points": matched_points,
        "fit_percentage": fit_pct,
        "surplus_skills": surplus,
        "deficit_skills": deficit,
        "aligned_skills": aligned
    }


def calculate_readiness_score(student_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """
    Computes an explainable, multi-dimensional Placement Readiness Index (0-100)
    using transparent, weighted component scoring.
    
    Components:
    1. Academics (0-100)
    2. Attendance Compliance (0-100)
    3. Technical Competency Fit (0-100)
    4. Certifications & Credentials (0-100)
    5. Practical Experience & Projects (0-100)
    6. Soft Skills & Placement Preparation (0-100)
    """
    role_config = CAREER_ROLE_BENCHMARKS.get(target_role, CAREER_ROLE_BENCHMARKS["Data Analyst"])
    weights = role_config["weights"]
    
    # 1. Academic Component (0-100)
    acad_pct = float(student_data.get("academic_percentage", 60.0))
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
    
    # 2. Attendance Component (0-100)
    att_pct = float(student_data.get("attendance_percentage", 75.0))
    if att_pct >= 85.0:
        att_score = 100.0
    elif att_pct >= ATTENDANCE_CRITICAL_THRESHOLD: # 75.0%
        att_score = 80.0 + ((att_pct - 75.0) / 10.0) * 20.0
    elif att_pct >= 65.0:
        att_score = 50.0 + ((att_pct - 65.0) / 10.0) * 30.0
    else:
        att_score = max(10.0, (att_pct / 65.0) * 50.0)
    att_score = round(min(100.0, max(0.0, att_score)), 1)
    
    # 3. Technical Fit Component (0-100)
    skills = student_data.get("skills", {})
    gap_analysis = calculate_skill_gaps(skills, target_role)
    tech_score = gap_analysis["fit_percentage"]
    
    # 4. Certifications Component (0-100)
    certs = student_data.get("certifications", [])
    cert_count = len(certs) if isinstance(certs, list) else int(student_data.get("certifications_count", 0))
    if cert_count >= 3:
        cert_score = 100.0
    elif cert_count == 2:
        cert_score = 85.0
    elif cert_count == 1:
        cert_score = 65.0
    else:
        cert_score = 30.0
        
    # 5. Experience & Projects Component (0-100)
    internship_done = str(student_data.get("internship_status", "Not Completed")).lower() == "completed"
    projects_count = int(student_data.get("projects_count", 0))
    
    exp_score = 0.0
    if internship_done:
        exp_score += 55.0
    else:
        exp_score += 15.0
        
    if projects_count >= 3:
        exp_score += 45.0
    elif projects_count == 2:
        exp_score += 35.0
    elif projects_count == 1:
        exp_score += 20.0
    else:
        exp_score += 0.0
    exp_score = round(min(100.0, exp_score), 1)
    
    # 6. Soft Skills & Preparation Component (0-100)
    comm_lvl = int(skills.get("Communication", student_data.get("communication_level", 3)))
    apt_lvl = int(student_data.get("aptitude_level", 3))
    resume_status = str(student_data.get("resume_status", "Draft")).lower()
    interview_status = str(student_data.get("interview_status", "Not Started")).lower()
    
    soft_score = 0.0
    # Communication (max 30 pts)
    soft_score += (comm_lvl / 5.0) * 30.0
    # Aptitude (max 30 pts)
    soft_score += (apt_lvl / 5.0) * 30.0
    # Resume (max 20 pts)
    if "verified" in resume_status or "ready" in resume_status or "final" in resume_status:
        soft_score += 20.0
    elif "reviewed" in resume_status:
        soft_score += 15.0
    elif "draft" in resume_status:
        soft_score += 8.0
        
    # Interview Readiness (max 20 pts)
    if "ready" in interview_status or "multiple" in interview_status:
        soft_score += 20.0
    elif "1 mock" in interview_status or "mock" in interview_status:
        soft_score += 12.0
    else:
        soft_score += 5.0
    soft_score = round(min(100.0, soft_score), 1)
    
    # Calculate Overall Weighted Readiness Score
    overall_score = (
        (acad_score * weights["academic"]) +
        (att_score * weights["attendance"]) +
        (tech_score * weights["technical_fit"]) +
        (cert_score * weights["certifications"]) +
        (exp_score * weights["experience"]) +
        (soft_score * weights["soft_skills"])
    )
    overall_score = round(min(100.0, max(0.0, overall_score)), 1)
    
    # Band Designation
    if overall_score >= 80.0:
        tier_label = "Placement Ready / Highly Competitive"
        tier_color = "#10B981" # Green
        tier_summary = "Candidate demonstrates strong holistic alignment across academic standing, technical competencies, and corporate readiness."
    elif overall_score >= 65.0:
        tier_label = "Near Ready / Minor Skill Gaps"
        tier_color = "#2563EB" # Blue
        tier_summary = "Candidate meets foundational recruitment criteria. Closing 1-2 targeted technical and project gaps will optimize offer competitiveness."
    elif overall_score >= 50.0:
        tier_label = "Developing / Moderate Intervention Required"
        tier_color = "#F59E0B" # Amber
        tier_summary = "Candidate requires structured development across technical tool proficiency, certifications, and mock interview practice."
    else:
        tier_label = "Early Stage / High Priority Support"
        tier_color = "#EF4444" # Red
        tier_summary = "Immediate academic and skill remediation is recommended to achieve baseline corporate eligibility thresholds."
        
    components = {
        "Academic Standing": {
            "score": acad_score,
            "weight": int(weights["academic"] * 100),
            "weighted_points": round(acad_score * weights["academic"], 1),
            "input_val": f"{acad_pct:.1f}% Aggregate"
        },
        "Attendance Discipline": {
            "score": att_score,
            "weight": int(weights["attendance"] * 100),
            "weighted_points": round(att_score * weights["attendance"], 1),
            "input_val": f"{att_pct:.1f}% Attendance"
        },
        "Technical Role Alignment": {
            "score": tech_score,
            "weight": int(weights["technical_fit"] * 100),
            "weighted_points": round(tech_score * weights["technical_fit"], 1),
            "input_val": f"{tech_score:.1f}% Benchmark Fit"
        },
        "Certifications & Credentials": {
            "score": cert_score,
            "weight": int(weights["certifications"] * 100),
            "weighted_points": round(cert_score * weights["certifications"], 1),
            "input_val": f"{cert_count} Active Certifications"
        },
        "Internship & Projects": {
            "score": exp_score,
            "weight": int(weights["experience"] * 100),
            "weighted_points": round(exp_score * weights["experience"], 1),
            "input_val": f"{'Internship Done' if internship_done else 'No Internship'} | {projects_count} Projects"
        },
        "Soft Skills & Preparation": {
            "score": soft_score,
            "weight": int(weights["soft_skills"] * 100),
            "weighted_points": round(soft_score * weights["soft_skills"], 1),
            "input_val": f"Comm: {comm_lvl}/5 | Apt: {apt_lvl}/5 | {resume_status.capitalize()}"
        }
    }
    
    return {
        "overall_score": overall_score,
        "tier_label": tier_label,
        "tier_color": tier_color,
        "tier_summary": tier_summary,
        "weights": weights,
        "components": components,
        "gap_analysis": gap_analysis
    }


def generate_individual_assessment(student_data: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """
    Comprehensive assessment pipeline producing strengths, weaknesses,
    gap breakdowns, and actionable recommendations for an individual student.
    """
    readiness = calculate_readiness_score(student_data, target_role)
    gap_analysis = readiness["gap_analysis"]
    
    strengths = []
    weaknesses = []
    recommendations = []
    
    # 1. Academic Strengths / Weaknesses
    acad_pct = float(student_data.get("academic_percentage", 65.0))
    if acad_pct >= ACADEMIC_DISTINCTION_THRESHOLD: # 75%
        strengths.append(f"Distinct academic standing with {acad_pct:.1f}% aggregate, placing candidate in premier recruitment screening tiers.")
    elif acad_pct >= 60.0:
        strengths.append(f"Consistent academic record with {acad_pct:.1f}% aggregate, meeting standard campus drive eligibility cutoffs.")
    else:
        weaknesses.append(f"Academic aggregate is {acad_pct:.1f}%, which is below the common 60.0% corporate screening cutoff.")
        recommendations.append({
            "category": "Academic Enhancement",
            "priority": "High",
            "action": f"Focus on upcoming semester examinations and internal submissions to elevate cumulative score toward 60%+.",
            "rationale": "Major corporate recruiters enforce a mandatory 60% graduation/semester cutoff to filter screening test applicants."
        })
        
    # Subject-wise inspection (if provided)
    subject_marks = student_data.get("subject_marks", {})
    if subject_marks:
        top_subs = [f"{s} ({m:.0f}%)" for s, m in subject_marks.items() if m >= 75]
        low_subs = [f"{s} ({m:.0f}%)" for s, m in subject_marks.items() if m < 55]
        if top_subs:
            strengths.append(f"Strong subject mastery demonstrated in: {', '.join(top_subs[:3])}.")
        if low_subs:
            weaknesses.append(f"Remediation required in lower-scoring subjects: {', '.join(low_subs[:3])}.")
            recommendations.append({
                "category": "Course Remediation",
                "priority": "Medium",
                "action": f"Schedule targeted doubt-clearing tutorials in {low_subs[0].split(' ')[0]} with course faculty.",
                "rationale": "Consistent subject performance avoids recruiter scrutiny during academic transcript reviews."
            })

    # 2. Attendance Compliance
    att_pct = float(student_data.get("attendance_percentage", 75.0))
    if att_pct >= 85.0:
        strengths.append(f"Exemplary classroom attendance at {att_pct:.1f}%, reflecting disciplined professional commitment.")
    elif att_pct >= ATTENDANCE_CRITICAL_THRESHOLD:
        strengths.append(f"Attendance compliant at {att_pct:.1f}% (above the {ATTENDANCE_CRITICAL_THRESHOLD:.1f}% institutional cutoff).")
    else:
        weaknesses.append(f"Attendance at {att_pct:.1f}% violates the mandatory {ATTENDANCE_CRITICAL_THRESHOLD:.1f}% institutional attendance policy.")
        recommendations.append({
            "category": "Attendance Compliance",
            "priority": "Critical",
            "action": f"Meet with your faculty academic mentor immediately and attend scheduled makeup sessions to lift attendance above 75.0%.",
            "rationale": "Students falling below 75% attendance risk formal debarment from semester exams and campus placement drives."
        })

    # 3. Technical Skills & Deficits
    for item in gap_analysis["skill_comparison"]:
        skill = item["skill"]
        gap = item["gap"]
        stu_lvl = item["student_level"]
        target_lvl = item["target_level"]
        
        if gap >= 1:
            strengths.append(f"Advanced proficiency in {skill} (Level {stu_lvl}/5), exceeding the benchmark for {target_role} (Level {target_lvl}/5).")
        elif gap == 0:
            strengths.append(f"Well-aligned capability in {skill} (Level {stu_lvl}/5), meeting benchmark expectations.")
        else: # gap < 0
            gap_size = abs(gap)
            weaknesses.append(f"Skill deficit in {skill}: candidate is Level {stu_lvl} ({item['student_name']}) vs. target Level {target_lvl} ({item['target_name']}) for {target_role}.")
            
            # Actionable advice tailored to the specific skill
            if skill == "SQL":
                action_text = f"Elevate SQL from {item['student_name']} to {item['target_name']} by completing multi-table joins, subqueries, CTEs, and window functions on LeetCode or HackerRank."
            elif skill == "Python":
                action_text = f"Advance Python capability by completing hands-on Pandas, NumPy, and data manipulation exercises on Kaggle or DataCamp."
            elif skill in ["Power BI", "Tableau"]:
                action_text = f"Build and publish 2 end-to-end interactive {skill} executive dashboards on NovyPro or Tableau Public solving commercial retail/finance problems."
            elif skill == "Excel":
                action_text = "Master advanced Excel functions (XLOOKUP, INDEX-MATCH, dynamic arrays, Pivot Tables, and scenario modeling)."
            elif skill == "Statistics":
                action_text = "Strengthen statistical concepts: hypothesis testing (t-tests, ANOVA), p-values, regression analysis, and confidence intervals."
            elif skill == "Machine Learning":
                action_text = "Develop applied scikit-learn models (logistic regression, decision trees, random forests) and explain precision/recall tradeoffs."
            else:
                action_text = f"Dedicate structured study to elevate {skill} by {gap_size} level(s) toward industry benchmark."
                
            recommendations.append({
                "category": f"Technical Mastery: {skill}",
                "priority": "High" if gap_size >= 2 else "Medium",
                "action": action_text,
                "rationale": f"{skill} is a core evaluation pillar for corporate {target_role} technical screening assessments."
            })

    # 4. Certifications
    certs = student_data.get("certifications", [])
    if certs:
        strengths.append(f"Holds {len(certs)} verified certification(s): {', '.join(certs[:2])}.")
    else:
        weaknesses.append("No active industry certifications recorded in candidate profile.")
        role_certs = CAREER_ROLE_BENCHMARKS.get(target_role, {}).get("key_certifications", ["Google Data Analytics", "Microsoft PL-300"])
        recommendations.append({
            "category": "Industry Credentialing",
            "priority": "Medium",
            "action": f"Pursue an industry-recognized credential such as {role_certs[0]} or {role_certs[1] if len(role_certs)>1 else ''}.",
            "rationale": "Standardized certifications provide external validation of candidate skills, improving resume shortlisting rates."
        })

    # 5. Internship & Project Portfolio
    internship_done = str(student_data.get("internship_status", "Not Completed")).lower() == "completed"
    projects_count = int(student_data.get("projects_count", 0))
    
    if internship_done:
        intern_co = student_data.get("internship_company", "")
        co_text = f" at {intern_co}" if intern_co else ""
        strengths.append(f"Completed verified corporate summer internship{co_text}, providing commercial workplace exposure.")
    else:
        weaknesses.append("Lacks corporate summer internship experience on candidate profile.")
        recommendations.append({
            "category": "Practical Experience",
            "priority": "High",
            "action": "Apply for live virtual internships or alumni-led consulting capstones to gain commercial project exposure.",
            "rationale": "Empirical placement data indicates that candidates with prior corporate internships experience significantly higher recruitment conversion rates."
        })
        
    if projects_count >= 2:
        strengths.append(f"Demonstrated project portfolio with {projects_count} completed applied analytics projects.")
    else:
        weaknesses.append(f"Limited project portfolio ({projects_count} completed project{'s' if projects_count!=1 else ''}).")
        recommendations.append({
            "category": "Portfolio Development",
            "priority": "High",
            "action": f"Build and host 2 public portfolio projects on GitHub tailored to {target_role} (e.g. churn prediction or sales KPI dashboard).",
            "rationale": "Recruiters favor candidates who can walk through real-world dataset problem formulations during technical interviews."
        })

    # 6. Soft Skills & Interview Preparation
    comm_lvl = int(student_data.get("skills", {}).get("Communication", student_data.get("communication_level", 3)))
    apt_lvl = int(student_data.get("aptitude_level", 3))
    interview_status = str(student_data.get("interview_status", "Not Started")).lower()
    
    if comm_lvl >= 4:
        strengths.append(f"Strong business communication capability (Level {comm_lvl}/5), facilitating persuasive stakeholder articulation.")
    elif comm_lvl <= 2:
        weaknesses.append(f"Communication capability is at Level {comm_lvl}/5, which may constrain performance in group discussions and HR interviews.")
        recommendations.append({
            "category": "Communication & Articulation",
            "priority": "High",
            "action": "Participate in departmental Toastmasters sessions, business case debriefs, and impromptu presentation drills.",
            "rationale": "Technical competency must be complemented by clear, structured business storytelling for client-facing roles."
        })
        
    if apt_lvl <= 2:
        weaknesses.append(f"Aptitude test preparation is at Level {apt_lvl}/5, posing risk during preliminary online screening exams.")
        recommendations.append({
            "category": "Aptitude Screening",
            "priority": "High",
            "action": "Complete daily timed aptitude modules (Quantitative, Logical Reasoning, and Data Interpretation) on IndiaBIX or Prepleaf.",
            "rationale": "Over 80% of Tier-1 campus recruiters employ elimination-round cognitive aptitude tests prior to technical interviews."
        })
        
    if "not started" in interview_status or "none" in interview_status:
        weaknesses.append("Candidate has not yet participated in simulated mock technical or behavioral interview panels.")
        recommendations.append({
            "category": "Mock Interview Drills",
            "priority": "High",
            "action": "Schedule at least two faculty/alumni mock interview panels focusing on technical resume defense and behavioral questions.",
            "rationale": "Mock panels acclimatize candidates to high-pressure questioning and highlight speech delivery blind spots."
        })

    return {
        "student_data": student_data,
        "target_role": target_role,
        "readiness": readiness,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations
    }


def get_sample_student_profile(sample_type: str = "balanced") -> Dict[str, Any]:
    """
    Returns realistic sample student data dictionaries for quick 1-click demonstration.
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
                "SQL": 4,
                "Python": 4,
                "Power BI": 4,
                "Tableau": 3,
                "Statistics": 4,
                "Machine Learning": 3,
                "Communication": 4
            },
            "certifications": [
                "Microsoft Power BI Data Analyst (PL-300)",
                "Google Data Analytics Professional Certificate",
                "SQL for Data Science"
            ],
            "certifications_count": 3,
            "internship_status": "Completed",
            "internship_company": "Deloitte Analytics",
            "internship_duration_months": 2,
            "project_experience": "End-to-end customer churn prediction and retail revenue dashboard in Power BI and scikit-learn.",
            "projects_count": 3,
            "resume_status": "Ready / Verified",
            "communication_level": 4,
            "aptitude_level": 4,
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
                "Communication": 3
            },
            "certifications": [],
            "certifications_count": 0,
            "internship_status": "Not Completed",
            "internship_company": "",
            "internship_duration_months": 0,
            "project_experience": "Classroom spreadsheet assignment analyzing quarterly balance sheets.",
            "projects_count": 0,
            "resume_status": "Draft",
            "communication_level": 3,
            "aptitude_level": 2,
            "interview_status": "Not Started",
            "placement_status": "Unplaced",
            "target_role": "Business Analyst"
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
                "Communication": 3
            },
            "certifications": [
                "Google Data Analytics Professional Certificate"
            ],
            "certifications_count": 1,
            "internship_status": "Not Completed",
            "internship_company": "",
            "internship_duration_months": 0,
            "project_experience": "Exploratory data analysis on hospital emergency room admissions using Excel and SQL.",
            "projects_count": 1,
            "resume_status": "Reviewed",
            "communication_level": 3,
            "aptitude_level": 3,
            "interview_status": "1 Mock Interview",
            "placement_status": "Unplaced",
            "target_role": "Data Analyst"
        }
