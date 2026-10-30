"""
Reusable Plotly visualizations for EduMetrics.
Standardized design system with high-contrast, modern business intelligence aesthetics.
"""

from typing import List, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_ACCENT,
    COLOR_DANGER,
    COLOR_SUCCESS,
    COLOR_NEUTRAL,
    PALETTE_CATEGORICAL,
    ATTENDANCE_CRITICAL_THRESHOLD
)

DEFAULT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", size=12, color="#1E293B"),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)


def apply_theme(fig: go.Figure) -> go.Figure:
    """Applies uniform minimalist styling and grid lines to Plotly charts."""
    fig.update_layout(**DEFAULT_LAYOUT)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#E2E8F0", zeroline=False)
    return fig


def plot_placement_donut(df: pd.DataFrame) -> go.Figure:
    """Creates a sleek donut chart showing Placed vs Unplaced proportion."""
    status_counts = df["placement_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    
    colors = {
        "Placed": COLOR_SUCCESS,
        "Unplaced": "#94A3B8"
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts["Status"],
        values=status_counts["Count"],
        hole=0.65,
        marker=dict(colors=[colors.get(s, COLOR_PRIMARY) for s in status_counts["Status"]]),
        textinfo="label+percent",
        textfont=dict(size=13, family="sans-serif"),
        hoverinfo="label+value+percent"
    )])
    
    fig.update_layout(
        title="<b>Placement Status Distribution</b>",
        showlegend=False,
        **DEFAULT_LAYOUT
    )
    return fig


def plot_academic_distribution(df: pd.DataFrame) -> go.Figure:
    """Plots histogram and density of student academic percentage."""
    fig = px.histogram(
        df,
        x="academic_percentage",
        nbins=25,
        color_discrete_sequence=[COLOR_PRIMARY],
        opacity=0.85,
        labels={"academic_percentage": "Academic Percentage (%)"},
        title="<b>Overall Academic Score Distribution</b>",
        marginal="box"
    )
    fig.add_vline(
        x=float(df["academic_percentage"].mean()),
        line_dash="dash",
        line_color=COLOR_ACCENT,
        annotation_text=f"Batch Mean: {df['academic_percentage'].mean():.1f}%",
        annotation_position="top left"
    )
    return apply_theme(fig)


def plot_grade_distribution(band_counts: pd.DataFrame) -> go.Figure:
    """Bar chart of students by academic grade band."""
    colors = [COLOR_SUCCESS, COLOR_PRIMARY, COLOR_ACCENT, COLOR_DANGER]
    fig = px.bar(
        band_counts,
        x="Grade Band",
        y="Student Count",
        color="Grade Band",
        color_discrete_sequence=colors,
        text="Student Count",
        title="<b>Student Grade Band Distribution</b>"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    return apply_theme(fig)


def plot_attendance_vs_academic(df: pd.DataFrame) -> go.Figure:
    """Scatter plot correlating attendance with academic percentage."""
    fig = px.scatter(
        df,
        x="attendance_percentage",
        y="academic_percentage",
        color="placement_status",
        color_discrete_map={"Placed": COLOR_SUCCESS, "Unplaced": "#94A3B8"},
        hover_data=["student_id", "student_name", "specialization"],
        labels={
            "attendance_percentage": "Attendance Percentage (%)",
            "academic_percentage": "Academic Percentage (%)",
            "placement_status": "Placement Status"
        },
        title="<b>Attendance vs. Academic Performance</b>",
        opacity=0.75
    )
    
    fig.add_vline(
        x=ATTENDANCE_CRITICAL_THRESHOLD,
        line_dash="dot",
        line_color=COLOR_DANGER,
        line_width=2,
        annotation_text="75% Critical Threshold",
        annotation_position="bottom right"
    )
    return apply_theme(fig)


def plot_placement_by_specialization(spec_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing placement rate per specialization."""
    fig = px.bar(
        spec_df,
        y="Specialization",
        x="Placement Rate (%)",
        orientation="h",
        color="Placement Rate (%)",
        color_continuous_scale="Blues",
        text="Placement Rate (%)",
        title="<b>Placement Rate by Academic Specialization</b>"
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
    return apply_theme(fig)


def plot_salary_distribution(df: pd.DataFrame) -> go.Figure:
    """Boxplot displaying salary package distribution across specializations for placed students."""
    placed_df = df[df["placement_status"].str.lower() == "placed"].dropna(subset=["salary_lpa"])
    if len(placed_df) == 0:
        fig = go.Figure()
        fig.update_layout(title="No Placed Student Salary Data")
        return fig
        
    fig = px.box(
        placed_df,
        x="specialization",
        y="salary_lpa",
        color="specialization",
        color_discrete_sequence=PALETTE_CATEGORICAL,
        points="all",
        labels={"specialization": "Specialization", "salary_lpa": "Package (LPA)"},
        title="<b>Salary Package Spread by Specialization (LPA)</b>"
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig)


def plot_company_hires(comp_df: pd.DataFrame) -> go.Figure:
    """Bar chart of top recruiting companies."""
    if len(comp_df) == 0:
        return go.Figure()
        
    fig = px.bar(
        comp_df.head(10),
        x="Students Hired",
        y="Company",
        orientation="h",
        color="Avg Package (LPA)",
        color_continuous_scale="Viridis",
        text="Students Hired",
        title="<b>Top Hiring Companies & Average Packages</b>"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return apply_theme(fig)


def plot_skills_placement_impact(df: pd.DataFrame, skill_col: str, skill_label: str) -> go.Figure:
    """Compares placement rate across proficiency levels for a skill."""
    from src.metrics import compute_skill_placement_matrix
    matrix = compute_skill_placement_matrix(df, skill_col)
    if len(matrix) == 0:
        return go.Figure()
        
    fig = px.bar(
        matrix,
        x="Proficiency Level",
        y="Placement Rate (%)",
        color="Proficiency Level",
        color_discrete_map={"Beginner": "#94A3B8", "Intermediate": COLOR_PRIMARY, "Advanced": COLOR_SUCCESS},
        text="Placement Rate (%)",
        title=f"<b>Placement Rate by {skill_label} Proficiency</b>"
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False)
    return apply_theme(fig)


def plot_student_radar_benchmark(student: pd.Series, batch_df: pd.DataFrame) -> go.Figure:
    """
    Creates a radar (spider) benchmark chart comparing student scores against cohort averages.
    """
    # Categories to evaluate
    categories = [
        "Academic %", 
        "Attendance %", 
        "SQL (1-3)", 
        "Python (1-3)", 
        "Power BI (1-3)", 
        "Certifications"
    ]
    
    prof_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    
    # Student scores
    stu_acad = float(student.get("academic_percentage", 0))
    stu_att = float(student.get("attendance_percentage", 0))
    stu_sql = prof_map.get(str(student.get("sql_proficiency", "")).capitalize(), 1)
    stu_py = prof_map.get(str(student.get("python_proficiency", "")).capitalize(), 1)
    stu_bi = prof_map.get(str(student.get("power_bi_proficiency", "")).capitalize(), 1)
    stu_certs = float(student.get("certifications_count", 0))
    
    # Scale to 0-100 for visual uniformity
    stu_values = [
        stu_acad,
        stu_att,
        (stu_sql / 3.0) * 100.0,
        (stu_py / 3.0) * 100.0,
        (stu_bi / 3.0) * 100.0,
        min((stu_certs / 5.0) * 100.0, 100.0)
    ]
    
    # Batch averages
    avg_acad = float(batch_df["academic_percentage"].mean())
    avg_att = float(batch_df["attendance_percentage"].mean())
    avg_sql = batch_df["sql_proficiency"].map(prof_map).mean()
    avg_py = batch_df["python_proficiency"].map(prof_map).mean()
    avg_bi = batch_df["power_bi_proficiency"].map(prof_map).mean()
    avg_certs = float(batch_df["certifications_count"].mean())
    
    batch_values = [
        avg_acad,
        avg_att,
        (avg_sql / 3.0) * 100.0,
        (avg_py / 3.0) * 100.0,
        (avg_bi / 3.0) * 100.0,
        min((avg_certs / 5.0) * 100.0, 100.0)
    ]
    
    # Close the radar loop
    radar_categories = categories + [categories[0]]
    stu_values += [stu_values[0]]
    batch_values += [batch_values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=batch_values,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(148, 163, 184, 0.25)',
        line=dict(color='#94A3B8', width=2, dash='dot'),
        name='Batch Average'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=stu_values,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.35)',
        line=dict(color=COLOR_PRIMARY, width=2.5),
        name=f"Student ({student.get('student_name', 'Selected')})"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showline=False, ticksuffix="%"),
            bgcolor="rgba(0,0,0,0)"
        ),
        title="<b>Student Competency Profile vs. Batch Average</b>",
        showlegend=True,
        **DEFAULT_LAYOUT
    )
    return fig


def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Heatmap of numerical correlation matrix."""
    if len(corr_df) == 0:
        return go.Figure()
        
    labels = {
        "academic_percentage": "Academic %",
        "attendance_percentage": "Attendance %",
        "certifications_count": "Certifications",
        "technical_score_10": "Tech Index (10)",
        "salary_lpa": "Salary (LPA)"
    }
    
    clean_labels = [labels.get(c, c) for c in corr_df.columns]
    
    fig = px.imshow(
        corr_df.values,
        x=clean_labels,
        y=clean_labels,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        text_auto=".2f",
        title="<b>Correlation Matrix (Numerical Attributes)</b>"
    )
    fig.update_layout(**DEFAULT_LAYOUT)
    return fig


def plot_semester_comparison(df: pd.DataFrame) -> go.Figure:
    """Boxplot of academic performance across semesters."""
    fig = px.box(
        df,
        x="semester",
        y="academic_percentage",
        color="semester",
        color_discrete_sequence=PALETTE_CATEGORICAL,
        category_orders={"semester": ["Semester 1", "Semester 2", "Semester 3", "Semester 4"]},
        labels={"semester": "Semester", "academic_percentage": "Academic Percentage (%)"},
        title="<b>Semester-Level Academic Performance Comparison</b>"
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig)
