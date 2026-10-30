"""
Explainable, rule-based diagnostic and recommendation engine for EduMetrics.
Provides transparent, deterministic recommendations without black-box bias.
"""

from typing import List, Dict, Any
import pandas as pd
from src.config import ATTENDANCE_CRITICAL_THRESHOLD, ACADEMIC_DISTINCTION_THRESHOLD


def evaluate_student_profile(student: pd.Series) -> List[Dict[str, str]]:
    """
    Evaluates an individual student record against transparent business rules.
    
    Returns:
        List of recommendation dictionaries: {category, status, title, message, action, rationale}
    """
    recommendations = []
    
    # 1. Attendance Evaluation
    attendance = float(student.get("attendance_percentage", 0.0))
    if attendance < ATTENDANCE_CRITICAL_THRESHOLD:
        recommendations.append({
            "category": "Attendance",
            "status": "Critical",
            "title": "Low Attendance Alert",
            "message": (
                f"Current attendance is {attendance:.1f}%, which is below the mandatory "
                f"institutional threshold of {ATTENDANCE_CRITICAL_THRESHOLD:.1f}%."
            ),
            "action": "Meet with faculty mentor; attend all scheduled remediation and makeup sessions.",
            "rationale": "Institutions and campus placement drives typically require minimum 75% attendance for drive eligibility."
        })
    elif attendance < 85.0:
        recommendations.append({
            "category": "Attendance",
            "status": "Action Needed",
            "title": "Attendance Improvement Opportunity",
            "message": f"Attendance is {attendance:.1f}%. While above the 75% cutoff, maintaining >85% correlates with higher academic consistency.",
            "action": "Ensure consistent presence in lab and practical project lectures.",
            "rationale": "High attendance provides direct classroom engagement and continuous faculty feedback."
        })
    else:
        recommendations.append({
            "category": "Attendance",
            "status": "Strength",
            "title": "Excellent Attendance Record",
            "message": f"Outstanding attendance at {attendance:.1f}%.",
            "action": "Maintain this strong discipline through upcoming semester assessments.",
            "rationale": "High attendance demonstrates professional consistency and reliable work habits."
        })

    # 2. Academic Score Evaluation
    acad_score = float(student.get("academic_percentage", 0.0))
    if acad_score < 55.0:
        recommendations.append({
            "category": "Academics",
            "status": "Critical",
            "title": "Academic Remediation Needed",
            "message": f"Academic score is {acad_score:.1f}%, falling in the intervention band (<55%).",
            "action": "Enroll in department tutorial sessions and peer-assisted study groups.",
            "rationale": "Most corporate recruiters mandate a minimum benchmark of 60% aggregate for screening test shortlisting."
        })
    elif acad_score < 70.0:
        recommendations.append({
            "category": "Academics",
            "status": "Action Needed",
            "title": "Target 70%+ Aggregate",
            "message": f"Academic score is {acad_score:.1f}%. A push to 70%+ significantly expands company eligibility.",
            "action": "Focus on core elective exams and submission assignments to elevate overall GPA.",
            "rationale": "Tier-1 recruiters often use 70% as the threshold for early-round interview exemptions."
        })
    else:
        recommendations.append({
            "category": "Academics",
            "status": "Strength",
            "title": "Strong Academic Standing",
            "message": f"Academic score is {acad_score:.1f}%, in top performance tiers.",
            "action": "Leverage academic distinction to target competitive corporate roles and consultancies.",
            "rationale": "Consistent high grades provide a strong initial impression during campus recruitment."
        })

    # 3. Technical Skills Evaluation
    sql = str(student.get("sql_proficiency", "Beginner")).capitalize()
    py = str(student.get("python_proficiency", "Beginner")).capitalize()
    bi = str(student.get("power_bi_proficiency", "Beginner")).capitalize()
    
    tech_needs = []
    if py == "Beginner":
        tech_needs.append("Python programming")
    if sql == "Beginner":
        tech_needs.append("SQL relational queries")
    if bi == "Beginner":
        tech_needs.append("Power BI business dashboarding")
        
    if tech_needs:
        recommendations.append({
            "category": "Technical Skills",
            "status": "Action Needed",
            "title": "Skill Upskilling Recommended",
            "message": f"Currently at Beginner level in: {', '.join(tech_needs)}.",
            "action": "Complete hands-on portfolio projects and intermediate tutorials in these tools.",
            "rationale": "Modern analytics and business roles demand at least Intermediate proficiency in data querying and visualization."
        })
    else:
        recommendations.append({
            "category": "Technical Skills",
            "status": "Strength",
            "title": "Robust Technical Foundation",
            "message": f"Intermediate or Advanced across SQL ({sql}), Python ({py}), and Power BI ({bi}).",
            "action": "Build an end-to-end GitHub portfolio project demonstrating applied data modeling.",
            "rationale": "Demonstrated technical versatility is a strong positive differentiator in technical rounds."
        })

    # 4. Placement & Internship Preparation
    internship = str(student.get("internship_status", "Not Completed"))
    certs = int(student.get("certifications_count", 0))
    status = str(student.get("placement_status", "Unplaced"))
    
    if status == "Unplaced":
        if internship != "Completed":
            recommendations.append({
                "category": "Placement Prep",
                "status": "Critical",
                "title": "Prioritize Industry Internship / Live Project",
                "message": "No recorded corporate internship completion on profile.",
                "action": "Work with career services to secure a summer internship or corporate capstone.",
                "rationale": "Candidates with completed internships exhibit significantly higher campus placement conversion rates."
            })
        if certs < 2:
            recommendations.append({
                "category": "Placement Prep",
                "status": "Action Needed",
                "title": "Earn Industry Certifications",
                "message": f"Profile records {certs} certifications. Aim for at least 2 relevant credentials.",
                "action": "Pursue recognized certifications in data analytics, financial modeling, or supply chain.",
                "rationale": "Third-party verified certifications validate skills and substantiate resume credibility."
            })
    else:
        company = student.get("company", "Company")
        salary = student.get("salary_lpa", "N/A")
        recommendations.append({
            "category": "Placement Prep",
            "status": "Strength",
            "title": "Placement Confirmed",
            "message": f"Successfully placed at {company} with a package of {salary} LPA.",
            "action": "Engage in pre-onboarding technical preparation and company research.",
            "rationale": "Securing an offer enables focus on domain readiness and corporate transition."
        })
        
    return recommendations


def generate_cohort_recommendations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generates institutional, data-backed strategic recommendations for the batch.
    """
    if len(df) == 0:
        return []
        
    insights = []
    
    # 1. Attendance shortfalls
    critical_att_count = (df["attendance_percentage"] < ATTENDANCE_CRITICAL_THRESHOLD).sum()
    if critical_att_count > 0:
        pct = round((critical_att_count / len(df)) * 100.0, 1)
        insights.append({
            "area": "Attendance Compliance",
            "metric": f"{critical_att_count} Students ({pct}%) below 75% attendance",
            "recommendation": "Launch automated mid-term attendance alerts and schedule mandatory faculty-student advisory sessions.",
            "impact_type": "Institutional Policy"
        })
        
    # 2. Technical skill gap in unplaced cohort
    unplaced_df = df[df["placement_status"].str.lower() == "unplaced"]
    if len(unplaced_df) > 0:
        beg_sql = (unplaced_df["sql_proficiency"] == "Beginner").sum()
        beg_py = (unplaced_df["python_proficiency"] == "Beginner").sum()
        no_intern = (unplaced_df["internship_status"] != "Completed").sum()
        
        intern_gap_pct = round((no_intern / len(unplaced_df)) * 100.0, 1)
        insights.append({
            "area": "Experiential Learning Gap",
            "metric": f"{intern_gap_pct}% of unplaced students lack completed internships",
            "recommendation": "Partner with corporate alumni to provide sponsored 8-week virtual micro-internships.",
            "impact_type": "Placement Uplift"
        })
        
        if beg_sql > (0.35 * len(unplaced_df)) or beg_py > (0.35 * len(unplaced_df)):
            insights.append({
                "area": "Technical Upskilling",
                "metric": "High concentration of Beginner-level coding skills in unplaced cohort",
                "recommendation": "Conduct intensive weekend hackathons and mock technical interview rounds for SQL and Python.",
                "impact_type": "Skill Readiness"
            })
            
    # 3. Certification correlation
    placed_df = df[df["placement_status"].str.lower() == "placed"]
    if len(placed_df) > 0 and len(unplaced_df) > 0:
        avg_cert_placed = round(float(placed_df["certifications_count"].mean()), 1)
        avg_cert_unplaced = round(float(unplaced_df["certifications_count"].mean()), 1)
        insights.append({
            "area": "Professional Credentials",
            "metric": f"Placed students hold avg {avg_cert_placed} certifications vs {avg_cert_unplaced} for unplaced",
            "recommendation": "Subsidize professional certifications (e.g., Microsoft Power BI, AWS Cloud Practitioner, Google Data Analytics).",
            "impact_type": "Curriculum Enhancement"
        })
        
    return insights
