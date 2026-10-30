"""
Unit and integration tests for Individual Student Assessment & Career-Readiness Analyzer.
Tests competency gap analysis, readiness scoring, recommendations, PDF generation, and SQLite persistence.
"""

import pytest
import sqlite3
import pandas as pd
from pathlib import Path

from src.assessment_engine import (
    CAREER_ROLE_BENCHMARKS,
    SKILL_LEVEL_NAMES,
    calculate_skill_gaps,
    calculate_readiness_score,
    generate_individual_assessment,
    get_sample_student_profile
)
from src.report_generator import generate_student_pdf_report
from src.database import (
    save_assessment_record,
    load_all_assessments,
    save_single_student_to_db,
    get_connection,
    init_db
)
from src.visualizations import (
    plot_skill_gap_comparison,
    plot_student_competency_radar,
    plot_readiness_component_breakdown,
    plot_subject_performance
)


def test_career_role_benchmarks_integrity():
    """Verifies that all 5 standard career roles are defined with valid weights and skill targets."""
    expected_roles = [
        "Data Analyst", 
        "Business Analyst", 
        "Data Scientist", 
        "Business Intelligence Analyst", 
        "Product Analyst"
    ]
    for role in expected_roles:
        assert role in CAREER_ROLE_BENCHMARKS, f"Missing role: {role}"
        config = CAREER_ROLE_BENCHMARKS[role]
        assert "skills" in config
        assert "weights" in config
        assert "key_certifications" in config
        
        # Verify weights sum to 1.0 (with floating-point tolerance)
        weights_sum = sum(config["weights"].values())
        assert abs(weights_sum - 1.0) < 0.01, f"Weights for {role} do not sum to 1.0: {weights_sum}"
        
        # Verify skills are on 1-5 scale
        for skill_name, lvl in config["skills"].items():
            assert 1 <= lvl <= 5, f"Invalid skill level {lvl} for {skill_name} in {role}"


def test_calculate_skill_gaps_aligned_and_deficits():
    """Tests that skill gap calculation accurately computes surplus, aligned, and deficit skills."""
    student_skills = {
        "SQL": 4,           # Target: 4 -> Aligned (0)
        "Excel": 5,         # Target: 4 -> Surplus (+1)
        "Power BI": 2,      # Target: 4 -> Deficit (-2)
        "Python": 1,        # Target: 3 -> Deficit (-2)
        "Tableau": 3,       # Target: 3 -> Aligned (0)
        "Statistics": 3,    # Target: 3 -> Aligned (0)
        "Machine Learning": 1, # Target: 2 -> Deficit (-1)
        "Communication": 4  # Target: 4 -> Aligned (0)
    }
    
    result = calculate_skill_gaps(student_skills, "Data Analyst")
    assert result["target_role"] == "Data Analyst"
    assert "Excel" in result["surplus_skills"]
    assert "SQL" in result["aligned_skills"]
    assert "Power BI" in result["deficit_skills"]
    assert "Python" in result["deficit_skills"]
    assert 0.0 <= result["fit_percentage"] <= 100.0


def test_calculate_readiness_score_high_achiever():
    """Tests that a high achiever candidate achieves a high readiness score in the top tier."""
    sample = get_sample_student_profile("high_achiever")
    readiness = calculate_readiness_score(sample, "Data Analyst")
    
    assert readiness["overall_score"] >= 80.0
    assert "Placement Ready" in readiness["tier_label"]
    assert readiness["tier_color"] == "#10B981"
    assert len(readiness["components"]) == 6


def test_calculate_readiness_score_needs_intervention():
    """Tests that an at-risk profile receives an appropriate lower score and risk tier."""
    sample = get_sample_student_profile("needs_intervention")
    readiness = calculate_readiness_score(sample, "Business Analyst")
    
    assert readiness["overall_score"] < 65.0
    assert readiness["tier_label"] in ["Developing / Moderate Intervention Required", "Early Stage / High Priority Support"]


def test_generate_individual_assessment_recommendations():
    """Verifies that diagnostic assessment generates actionable strengths, weaknesses, and recommendations."""
    sample = get_sample_student_profile("needs_intervention")
    assessment = generate_individual_assessment(sample, "Business Analyst")
    
    assert len(assessment["weaknesses"]) > 0
    assert len(assessment["recommendations"]) > 0
    
    # Needs intervention sample has 71% attendance -> should trigger attendance alert
    rec_categories = [r["category"] for r in assessment["recommendations"]]
    assert any("Attendance" in cat for cat in rec_categories)


def test_generate_student_pdf_report_valid_bytes():
    """Verifies that ReportLab compiles a valid, non-empty PDF document starting with '%PDF'."""
    sample = get_sample_student_profile("balanced")
    assessment = generate_individual_assessment(sample, "Data Analyst")
    pdf_bytes = generate_student_pdf_report(assessment)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")


def test_assessment_visualizations_render_figures():
    """Verifies that all 4 assessment Plotly charts render successfully with valid figures."""
    sample = get_sample_student_profile("balanced")
    assessment = generate_individual_assessment(sample, "Data Analyst")
    gap_analysis = assessment["readiness"]["gap_analysis"]
    target_skills = CAREER_ROLE_BENCHMARKS["Data Analyst"]["skills"]
    
    fig_gap = plot_skill_gap_comparison(gap_analysis)
    assert fig_gap is not None
    assert len(fig_gap.data) >= 2
    
    fig_radar = plot_student_competency_radar(sample["skills"], target_skills, "Data Analyst")
    assert fig_radar is not None
    assert len(fig_radar.data) == 2
    
    fig_breakdown = plot_readiness_component_breakdown(assessment["readiness"])
    assert fig_breakdown is not None
    
    fig_subs = plot_subject_performance(sample["subject_marks"])
    assert fig_subs is not None


def test_save_and_load_assessment_database(tmp_path):
    """Verifies saving an assessment to SQLite and loading it back."""
    test_db = tmp_path / "test_assessments.db"
    conn = sqlite3.connect(str(test_db))
    
    sample = get_sample_student_profile("balanced")
    assessment = generate_individual_assessment(sample, "Data Analyst")
    
    row_id = save_assessment_record(assessment, conn=conn)
    assert row_id > 0
    
    loaded_df = load_all_assessments(conn=conn)
    assert len(loaded_df) == 1
    assert loaded_df.iloc[0]["Student ID"] == sample["student_id"]
    assert loaded_df.iloc[0]["Target Role"] == "Data Analyst"
    conn.close()
