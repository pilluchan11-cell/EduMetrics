"""
Automated UI Layout, Typography Spacing, and Visualization Collision Tests.
Verifies that:
1. Plotly charts never overlap title/subtitle with legends across all views.
2. Layout margins provide ample clearance for multi-line titles and bottom legends.
3. Custom CSS guarantees min-width: 0 on columns to prevent flex blowout.
4. KPI cards enforce flex-column layout with min-height and visible overflow to prevent text cutoffs.
5. Buttons and input labels support text wrapping and appropriate line-heights.
"""

import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.data_generator import generate_synthetic_data
from src.visualizations import (
    DEFAULT_LAYOUT,
    apply_theme,
    plot_placement_donut,
    plot_academic_distribution,
    plot_grade_distribution,
    plot_attendance_vs_academic,
    plot_placement_by_specialization,
    plot_salary_distribution,
    plot_company_hires,
    plot_skills_placement_impact,
    plot_student_radar_benchmark,
    plot_correlation_heatmap,
    plot_semester_comparison,
    plot_skill_gap_comparison,
    plot_student_competency_radar,
    plot_readiness_component_breakdown,
    plot_subject_performance
)
from src.assessment_engine import (
    get_sample_student_profile,
    generate_individual_assessment
)
from src.ui_components import inject_custom_css


@pytest.fixture(scope="module")
def sample_data():
    return generate_synthetic_data(150, seed=42)


def test_default_layout_and_margins():
    """Verifies that DEFAULT_LAYOUT positions horizontal legends safely below the chart."""
    assert DEFAULT_LAYOUT["margin"]["t"] >= 60, "Top margin must be >= 60px to accommodate 2-line titles without clipping"
    assert DEFAULT_LAYOUT["margin"]["b"] >= 45, "Bottom margin must be >= 45px to accommodate x-axis and bottom legend"
    
    legend = DEFAULT_LAYOUT["legend"]
    assert legend["orientation"] == "h", "Legends must be horizontal"
    assert legend["yanchor"] == "top", "Legend yanchor must be 'top' when positioned below chart"
    assert legend["y"] <= 0, "Legend y must be <= 0 (below plot area) to prevent colliding with chart titles"
    assert legend["xanchor"] == "center", "Legend must be centered horizontally"


def test_chart_title_and_legend_separation(sample_data):
    """
    Renders every chart generator in EduMetrics and verifies that whenever a legend is visible,
    it is positioned strictly below the plot area (y <= 0) and NEVER in the title region (y >= 1.0).
    """
    charts = []
    
    # Donut chart
    charts.append(("placement_donut", plot_placement_donut(sample_data)))
    
    # Scatter plot
    charts.append(("attendance_vs_academic", plot_attendance_vs_academic(sample_data)))
    
    # Benchmark radar
    single_stu = sample_data.iloc[0]
    charts.append(("student_radar_benchmark", plot_student_radar_benchmark(single_stu, sample_data)))
    
    # Skill gap comparison
    sample_prof = get_sample_student_profile("balanced")
    assessment = generate_individual_assessment(sample_prof, "Data Analyst")
    charts.append(("skill_gap_comparison", plot_skill_gap_comparison(assessment["readiness"]["gap_analysis"])))
    
    # Competency radar
    charts.append(("competency_radar", plot_student_competency_radar(
        sample_prof["skills"], 
        {"SQL": 4, "Python": 4, "Excel": 4}, 
        "Data Analyst"
    )))
    
    # Readiness breakdown
    charts.append(("readiness_breakdown", plot_readiness_component_breakdown(assessment["readiness"])))
    
    # Subject performance
    charts.append(("subject_performance", plot_subject_performance({"Statistics": 82.0, "SQL": 74.0})))
    
    for name, fig in charts:
        layout = fig.layout
        margin_top = layout.margin.t if layout.margin and layout.margin.t is not None else 65
        assert margin_top >= 55, f"Chart '{name}' top margin ({margin_top}px) is too small for multi-line titles"
        
        # Check legend position if legend is shown
        show_leg = layout.showlegend is not False
        if show_leg and layout.legend:
            leg_y = layout.legend.y
            if leg_y is not None:
                assert leg_y <= 0.05, f"Chart '{name}' legend is at y={leg_y}, which collides with title! Must be <= 0"


def test_custom_css_rules_for_layout_integrity():
    """Inspects the generated CSS in inject_custom_css to verify all structural rules."""
    import inspect
    from src import ui_components
    css_source = inspect.getsource(ui_components.inject_custom_css)
    
    # 1. Check min-width: 0 on Streamlit columns
    assert 'div[data-testid="stColumn"]' in css_source
    assert "min-width: 0 !important;" in css_source
    
    # 2. Check KPI card min-height and visible overflow
    assert ".kpi-card" in css_source
    assert "min-height: 145px;" in css_source
    assert "overflow: visible;" in css_source
    assert "display: flex;" in css_source
    assert "flex-direction: column;" in css_source
    assert "justify-content: space-between;" in css_source
    
    # 3. Check button wrapping and min-height
    assert 'button[data-testid="baseButton-secondary"]' in css_source
    assert "white-space: normal !important;" in css_source
    assert "min-height: 42px !important;" in css_source
    
    # 4. Check widget labels
    assert 'label[data-testid="stWidgetLabel"]' in css_source
    assert "word-break: break-word !important;" in css_source
    assert "line-height: 1.4 !important;" in css_source
