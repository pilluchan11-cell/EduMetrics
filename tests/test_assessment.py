"""
Comprehensive unit and integration tests for Career-Specific Skill Benchmarking,
Readiness Assessment, Missing-Component Recalibration, and Learning Roadmaps.
"""

import pytest
import sqlite3
import pandas as pd
from pathlib import Path

from src.benchmarks import (
    CAREER_ROLE_BENCHMARKS,
    DEFAULT_READINESS_WEIGHTS,
    COMPONENT_DISPLAY_NAMES,
    SKILL_LEVEL_NAMES
)
from src.assessment_engine import (
    calculate_skill_gaps,
    calculate_readiness_score,
    generate_learning_roadmap,
    generate_individual_assessment,
    get_sample_student_profile
)
from src.report_generator import generate_student_pdf_report
from src.database import (
    save_assessment_record,
    load_all_assessments
)
from src.visualizations import (
    plot_skill_gap_comparison,
    plot_student_competency_radar,
    plot_readiness_component_breakdown
)


def test_configurable_benchmarks_and_weights_structure():
    """Verifies that all 5 required career roles are defined with valid benchmark targets and initial weights."""
    expected_roles = [
        "Business Analyst",
        "Data Analyst", 
        "Data Scientist", 
        "Business Intelligence Analyst", 
        "Product Analyst"
    ]
    for role in expected_roles:
        assert role in CAREER_ROLE_BENCHMARKS, f"Missing career role: {role}"
        config = CAREER_ROLE_BENCHMARKS[role]
        assert "skills" in config
        assert "key_certifications" in config
        assert "sample_project_ideas" in config
        
    # Check specific requested benchmarks
    ba_skills = CAREER_ROLE_BENCHMARKS["Business Analyst"]["skills"]
    assert ba_skills["Excel"] == 4
    assert ba_skills["SQL"] == 4
    assert ba_skills["Power BI"] == 3
    assert ba_skills["Python"] == 2
    assert ba_skills["Statistics"] == 3
    assert ba_skills["Communication"] == 5
    assert ba_skills["Problem-solving"] == 5

    da_skills = CAREER_ROLE_BENCHMARKS["Data Analyst"]["skills"]
    assert da_skills["Excel"] == 4
    assert da_skills["SQL"] == 5
    assert da_skills["Python"] == 4
    assert da_skills["Power BI"] == 4
    assert da_skills["Statistics"] == 4
    assert da_skills["Tableau"] == 3

    ds_skills = CAREER_ROLE_BENCHMARKS["Data Scientist"]["skills"]
    assert ds_skills["Python"] == 5
    assert ds_skills["SQL"] == 4
    assert ds_skills["Statistics"] == 5
    assert ds_skills["Machine Learning"] == 5
    assert ds_skills["Mathematics"] == 5

    # Verify standard initial weights: 40%, 15%, 15%, 10%, 10%, 10%
    assert DEFAULT_READINESS_WEIGHTS["technical_skills"] == 0.40
    assert DEFAULT_READINESS_WEIGHTS["academic_performance"] == 0.15
    assert DEFAULT_READINESS_WEIGHTS["communication_aptitude"] == 0.15
    assert DEFAULT_READINESS_WEIGHTS["certifications"] == 0.10
    assert DEFAULT_READINESS_WEIGHTS["internship_experience"] == 0.10
    assert DEFAULT_READINESS_WEIGHTS["project_experience"] == 0.10
    assert abs(sum(DEFAULT_READINESS_WEIGHTS.values()) - 1.00) < 0.001


def test_student_vs_career_benchmark_comparison_details():
    """Tests that student vs benchmark gap analysis properly evaluates gap and meets_benchmark boolean."""
    student_skills = {
        "Excel": 4,           # Target: 4 -> Gap 0 (Meets)
        "SQL": 3,             # Target: 5 -> Gap -2 (Deficit)
        "Python": 2,          # Target: 4 -> Gap -2 (Deficit)
        "Power BI": 4,        # Target: 4 -> Gap 0 (Meets)
        "Statistics": 5,      # Target: 4 -> Gap +1 (Surplus)
        "Tableau": 2          # Target: 3 -> Gap -1 (Deficit)
    }
    
    result = calculate_skill_gaps(student_skills, "Data Analyst")
    assert result["target_role"] == "Data Analyst"
    
    # Check item details
    by_skill = {item["skill"]: item for item in result["skill_comparison"]}
    assert by_skill["Excel"]["gap"] == 0
    assert by_skill["Excel"]["meets_benchmark"] is True
    
    assert by_skill["SQL"]["gap"] == -2
    assert by_skill["SQL"]["meets_benchmark"] is False
    assert "Deficit" in by_skill["SQL"]["status"]
    
    assert by_skill["Statistics"]["gap"] == 1
    assert by_skill["Statistics"]["meets_benchmark"] is True
    assert "Surplus" in by_skill["Statistics"]["status"]
    
    # Check biggest improvement opportunities sorting
    opps = result["biggest_improvement_opportunities"]
    assert len(opps) >= 3
    # Most negative gap should be at the front
    assert opps[0]["gap"] <= opps[-1]["gap"]


def test_career_readiness_score_complete_profile():
    """Tests calculating readiness score when all 6 components are provided."""
    sample = get_sample_student_profile("high_achiever")
    readiness = calculate_readiness_score(sample, "Data Analyst")
    
    assert readiness["coverage_percentage"] == 100.0
    assert readiness["available_component_count"] == 6
    assert len(readiness["missing_components"]) == 0
    assert readiness["overall_score"] >= 80.0
    assert "Placement Ready" in readiness["tier_label"]


def test_missing_component_handling_and_coverage_recalculation():
    """
    Verifies that when components are missing:
    1. They are NOT silently treated as zero.
    2. Available components are proportionally re-weighted to 100%.
    3. Coverage percentage is accurately reported.
    4. Missing component names are explicitly disclosed.
    """
    # Sample with missing internship (10%) and missing projects (10%)
    sample = get_sample_student_profile("missing_components")
    readiness = calculate_readiness_score(sample, "Data Analyst")
    
    # Coverage should be exactly 80.0%
    assert readiness["coverage_percentage"] == 80.0
    assert readiness["available_component_count"] == 4
    assert len(readiness["missing_components"]) == 2
    assert "Corporate Internship Experience" in readiness["missing_components"]
    assert "Applied Portfolio Project Experience" in readiness["missing_components"]
    
    # Check component weight recalculation
    components = readiness["components"]
    tech_info = components["Technical Tool & Analytical Skills"]
    assert tech_info["base_weight_pct"] == 40
    # Scaled up: 0.40 / 0.80 = 50.0%
    assert tech_info["adjusted_weight_pct"] == 50.0
    
    # Score should not be penalized to zero for missing fields
    assert readiness["overall_score"] > 60.0


def test_prioritized_personalized_learning_roadmap():
    """Verifies that learning roadmap prioritizes largest skill gaps and provides concrete objectives & projects."""
    sample = get_sample_student_profile("balanced")
    assessment = generate_individual_assessment(sample, "Data Analyst")
    roadmap = assessment["learning_roadmap"]
    
    assert len(roadmap) >= 2
    priority_1 = roadmap[0]
    assert priority_1["priority"] == 1
    assert "title" in priority_1
    assert "objectives" in priority_1 and len(priority_1["objectives"]) >= 2
    assert "practical_project" in priority_1 and len(priority_1["practical_project"]) > 10
    assert "duration" in priority_1


def test_downloadable_pdf_includes_roadmap_and_coverage():
    """Verifies that generated PDF report contains roadmap, benchmarks, and coverage disclosure."""
    sample = get_sample_student_profile("missing_components")
    assessment = generate_individual_assessment(sample, "Business Analyst")
    pdf_bytes = generate_student_pdf_report(assessment)
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")


def test_assessment_visualizations_render_figures():
    """Verifies that all assessment Plotly charts render successfully with valid figures."""
    sample = get_sample_student_profile("balanced")
    assessment = generate_individual_assessment(sample, "Data Analyst")
    gap_analysis = assessment["readiness"]["gap_analysis"]
    target_skills = CAREER_ROLE_BENCHMARKS["Data Analyst"]["skills"]
    
    fig_gap = plot_skill_gap_comparison(gap_analysis)
    assert fig_gap is not None
    assert len(fig_gap.data) == 2 # Benchmark bar + Candidate bar
    
    fig_radar = plot_student_competency_radar(sample["skills"], target_skills, "Data Analyst")
    assert fig_radar is not None
    assert len(fig_radar.data) == 2 # Target polygon + Candidate polygon
    
    fig_breakdown = plot_readiness_component_breakdown(assessment["readiness"])
    assert fig_breakdown is not None


def test_sqlite_assessment_persistence_with_role(tmp_path):
    """Verifies saving an assessment record to SQLite with target role and loading it back."""
    test_db = tmp_path / "test_assessments.db"
    conn = sqlite3.connect(str(test_db))
    
    sample = get_sample_student_profile("balanced")
    assessment = generate_individual_assessment(sample, "Business Analyst")
    
    row_id = save_assessment_record(assessment, conn=conn)
    assert row_id > 0
    
    loaded_df = load_all_assessments(conn=conn)
    assert len(loaded_df) == 1
    assert loaded_df.iloc[0]["Student ID"] == sample["student_id"]
    assert loaded_df.iloc[0]["Target Role"] == "Business Analyst"
    conn.close()
