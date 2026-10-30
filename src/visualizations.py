"""
Reusable Plotly visualizations for EduMetrics.
Standardized design system with high-contrast, modern business intelligence aesthetics,
custom HTML tooltips, and MBA-grade presentation clarity.
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

DEFAULT_FONT = "Plus Jakarta Sans, Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"

DEFAULT_LAYOUT = dict(
    autosize=True,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family=DEFAULT_FONT, size=11.5, color="#334155"),
    margin=dict(l=28, r=20, t=55, b=28),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.04,
        xanchor="left",
        x=0,
        font=dict(size=10.5, color="#475569")
    ),
    hoverlabel=dict(
        bgcolor="#0F172A",
        font_size=11.5,
        font_family=DEFAULT_FONT,
        font_color="#F8FAFC"
    )
)


def apply_theme(fig: go.Figure) -> go.Figure:
    """Applies uniform minimalist styling, soft grid lines, and responsive configuration to Plotly charts."""
    fig.update_layout(**DEFAULT_LAYOUT)
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor="#F1F5F9", 
        zeroline=False,
        tickfont=dict(color="#64748B", size=10.5),
        title_font=dict(color="#334155", size=11.5, family=DEFAULT_FONT)
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor="#F1F5F9", 
        zeroline=False,
        tickfont=dict(color="#64748B", size=10.5),
        title_font=dict(color="#334155", size=11.5, family=DEFAULT_FONT)
    )
    return fig


def plot_placement_donut(df: pd.DataFrame) -> go.Figure:
    """Creates a sleek donut chart with central KPI callout showing Placed vs Unplaced proportion."""
    if len(df) == 0 or "placement_status" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="No Placement Data Available", **DEFAULT_LAYOUT)
        return fig
        
    status_counts = df["placement_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    
    total = status_counts["Count"].sum()
    placed_count = int(status_counts[status_counts["Status"].str.lower() == "placed"]["Count"].sum()) if len(status_counts) > 0 else 0
    rate = round((placed_count / total) * 100.0, 1) if total > 0 else 0.0
    
    colors = {
        "Placed": COLOR_SUCCESS,
        "Unplaced": "#CBD5E1"
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts["Status"],
        values=status_counts["Count"],
        hole=0.68,
        marker=dict(
            colors=[colors.get(s, COLOR_PRIMARY) for s in status_counts["Status"]],
            line=dict(color="#FFFFFF", width=2.5)
        ),
        textinfo="percent",
        textfont=dict(size=13, family=DEFAULT_FONT, color="#FFFFFF"),
        hovertemplate="<b>%{label} Cohort</b><br>Students: <b>%{value:,}</b><br>Proportion: <b>%{percent}</b><extra></extra>"
    )])
    
    fig.update_layout(
        title=dict(
            text="<b>Placement Status Conversion</b><br><span style='font-size:12px; color:#64748B;'>Proportion of cohort with accepted offers</span>",
            font=dict(size=15, color="#0F172A")
        ),
        annotations=[dict(
            text=f"<b>{rate}%</b><br><span style='font-size:11px; color:#64748B;'>Placed</span>",
            x=0.5, y=0.5,
            font_size=19,
            font_family=DEFAULT_FONT,
            font_color="#0F172A",
            showarrow=False
        )],
        showlegend=True,
        **DEFAULT_LAYOUT
    )
    return fig


def plot_academic_distribution(df: pd.DataFrame) -> go.Figure:
    """Plots histogram and density of student academic percentage with refined styling."""
    valid_scores = df["academic_percentage"].dropna() if "academic_percentage" in df.columns else pd.Series(dtype=float)
    if len(valid_scores) == 0:
        fig = go.Figure()
        fig.update_layout(title="No Academic Score Data Available", **DEFAULT_LAYOUT)
        return fig
        
    mean_val = float(valid_scores.mean())
    median_val = float(valid_scores.median())
    
    fig = px.histogram(
        df,
        x="academic_percentage",
        nbins=28,
        color_discrete_sequence=[COLOR_PRIMARY],
        opacity=0.88,
        labels={"academic_percentage": "Academic Aggregate Score (%)"},
        title="<b>Overall Academic Score Distribution</b><br><span style='font-size:12px; color:#64748B;'>Density of academic percentages across all enrolled students</span>",
        marginal="box"
    )
    
    fig.update_traces(
        hovertemplate="Score Band: <b>%{x}%</b><br>Student Count: <b>%{y}</b><extra></extra>"
    )
    
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color=COLOR_ACCENT,
        line_width=2,
        annotation_text=f"Mean: {mean_val:.1f}%",
        annotation_position="top left",
        annotation_font=dict(size=11, color=COLOR_ACCENT, family=DEFAULT_FONT)
    )
    
    fig.add_vline(
        x=median_val,
        line_dash="dot",
        line_color=COLOR_SUCCESS,
        line_width=1.5,
        annotation_text=f"Median: {median_val:.1f}%",
        annotation_position="bottom left",
        annotation_font=dict(size=11, color=COLOR_SUCCESS, family=DEFAULT_FONT)
    )
    return apply_theme(fig)


def plot_grade_distribution(band_counts: pd.DataFrame) -> go.Figure:
    """Bar chart of students by academic grade band with clean percentage labels."""
    if len(band_counts) == 0:
        fig = go.Figure()
        fig.update_layout(title="No Grade Band Data Available", **DEFAULT_LAYOUT)
        return fig
        
    colors = [COLOR_SUCCESS, COLOR_PRIMARY, COLOR_ACCENT, COLOR_DANGER]
    
    fig = px.bar(
        band_counts,
        x="Grade Band",
        y="Student Count",
        color="Grade Band",
        color_discrete_sequence=colors,
        text="Student Count",
        title="<b>Student Grade Band Distribution</b><br><span style='font-size:12px; color:#64748B;'>Classification into distinction, honors, and remediation tiers</span>"
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=12, family=DEFAULT_FONT, color="#0F172A"),
        hovertemplate="<b>%{x}</b><br>Total Students: <b>%{y}</b><extra></extra>",
        marker_line_width=0
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig)


def plot_attendance_vs_academic(df: pd.DataFrame) -> go.Figure:
    """Scatter plot correlating attendance with academic percentage, with policy threshold."""
    if len(df) == 0 or "attendance_percentage" not in df.columns or "academic_percentage" not in df.columns or "placement_status" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="No Attendance/Academic Data Available", **DEFAULT_LAYOUT)
        return fig
        
    fig = px.scatter(
        df,
        x="attendance_percentage",
        y="academic_percentage",
        color="placement_status",
        color_discrete_map={"Placed": COLOR_SUCCESS, "Unplaced": "#94A3B8"},
        custom_data=["student_id", "student_name", "specialization"],
        labels={
            "attendance_percentage": "Attendance Rate (%)",
            "academic_percentage": "Academic Aggregate (%)",
            "placement_status": "Recruitment Status"
        },
        title="<b>Attendance Compliance vs. Academic Achievement</b><br><span style='font-size:12px; color:#64748B;'>Evaluating student discipline relative to institutional benchmark and recruitment outcomes</span>",
        opacity=0.82
    )
    
    fig.update_traces(
        marker=dict(size=7, line=dict(width=0.5, color="#FFFFFF")),
        hovertemplate="<b>%{customdata[1]}</b> (%{customdata[0]})<br>"
                      "Specialization: %{customdata[2]}<br>"
                      "Attendance: <b>%{x:.1f}%</b><br>"
                      "Academic Score: <b>%{y:.1f}%</b><br>"
                      "Status: <b>%{fullData.name}</b><extra></extra>"
    )
    
    # Critical threshold reference line
    fig.add_vline(
        x=ATTENDANCE_CRITICAL_THRESHOLD,
        line_dash="dash",
        line_color=COLOR_DANGER,
        line_width=2,
        annotation_text="75% Critical Cutoff",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color=COLOR_DANGER, family=DEFAULT_FONT)
    )
    return apply_theme(fig)


def plot_placement_by_specialization(spec_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing placement rate per specialization with clean styling."""
    if len(spec_df) == 0:
        fig = go.Figure()
        fig.update_layout(title="No Specialization Data Available", **DEFAULT_LAYOUT)
        return fig
        
    fig = px.bar(
        spec_df,
        y="Specialization",
        x="Placement Rate (%)",
        orientation="h",
        color="Placement Rate (%)",
        color_continuous_scale="Blues",
        text="Placement Rate (%)",
        title="<b>Placement Conversion by Academic Specialization</b><br><span style='font-size:12px; color:#64748B;'>Comparative recruitment performance across postgraduate majors</span>"
    )
    fig.update_traces(
        texttemplate="<b>%{text:.1f}%</b>", 
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Placement Rate: <b>%{x:.1f}%</b><extra></extra>"
    )
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending")
    )
    return apply_theme(fig)
    fig.update_traces(
        texttemplate="<b>%{text:.1f}%</b>", 
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Placement Rate: <b>%{x:.1f}%</b><extra></extra>"
    )
    fig.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending")
    )
    return apply_theme(fig)


def plot_salary_distribution(df: pd.DataFrame) -> go.Figure:
    """Boxplot displaying salary package distribution across specializations for placed students."""
    if len(df) == 0 or "placement_status" not in df.columns or "salary_lpa" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="No Placed Student Salary Data", **DEFAULT_LAYOUT)
        return fig
        
    placed_df = df[df["placement_status"].str.lower() == "placed"].dropna(subset=["salary_lpa"])
    if len(placed_df) == 0:
        fig = go.Figure()
        fig.update_layout(title="No Placed Student Salary Data", **DEFAULT_LAYOUT)
        return fig
        
    fig = px.box(
        placed_df,
        x="specialization",
        y="salary_lpa",
        color="specialization",
        color_discrete_sequence=PALETTE_CATEGORICAL,
        points="all",
        labels={"specialization": "Specialization", "salary_lpa": "Package (₹ LPA)"},
        title="<b>Compensation Dispersion by Major (₹ LPA)</b><br><span style='font-size:12px; color:#64748B;'>Median, interquartile ranges, and outlier corporate offers</span>"
    )
    fig.update_traces(
        hovertemplate="Specialization: <b>%{x}</b><br>Package: <b>₹%{y:.2f} LPA</b><extra></extra>",
        marker=dict(size=4.5, opacity=0.7)
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig)


def plot_company_hires(comp_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of top recruiting companies and average packages."""
    if len(comp_df) == 0:
        return go.Figure()
        
    top_comps = comp_df.head(10).copy()
    
    fig = px.bar(
        top_comps,
        x="Students Hired",
        y="Company",
        orientation="h",
        color="Avg Package (LPA)",
        color_continuous_scale="Viridis",
        text="Students Hired",
        title="<b>Top Corporate Hiring Partners & Average Offers</b><br><span style='font-size:12px; color:#64748B;'>Ranked by hiring volume with color coding by average package (LPA)</span>"
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(family=DEFAULT_FONT, size=11),
        hovertemplate="Company: <b>%{y}</b><br>Hires: <b>%{x}</b><br>Avg Package: <b>₹%{marker.color:.2f} LPA</b><extra></extra>"
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_colorbar=dict(title="Avg LPA", len=0.8)
    )
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
        title=f"<b>{skill_label} Competence vs. Placement Rate</b><br><span style='font-size:12px; color:#64748B;'>Progression from Beginner to Advanced</span>"
    )
    fig.update_traces(
        texttemplate="<b>%{text:.1f}%</b>", 
        textposition="outside",
        hovertemplate="Proficiency: <b>%{x}</b><br>Placement Conversion: <b>%{y:.1f}%</b><extra></extra>"
    )
    fig.update_layout(
        showlegend=False,
        yaxis=dict(range=[0, 105])
    )
    return apply_theme(fig)


def plot_student_radar_benchmark(student: pd.Series, batch_df: pd.DataFrame) -> go.Figure:
    """
    Creates an executive radar benchmark chart comparing student scores against cohort averages.
    """
    categories = [
        "Academic %", 
        "Attendance %", 
        "SQL Skills", 
        "Python Skills", 
        "Power BI", 
        "Certifications"
    ]
    
    prof_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    
    raw_acad = student.get("academic_percentage", 0)
    stu_acad = float(raw_acad) if pd.notna(raw_acad) else 0.0
    raw_att = student.get("attendance_percentage", 0)
    stu_att = float(raw_att) if pd.notna(raw_att) else 0.0
    stu_sql = prof_map.get(str(student.get("sql_proficiency", "")).capitalize(), 1)
    stu_py = prof_map.get(str(student.get("python_proficiency", "")).capitalize(), 1)
    stu_bi = prof_map.get(str(student.get("power_bi_proficiency", "")).capitalize(), 1)
    raw_certs = student.get("certifications_count", 0)
    stu_certs = float(raw_certs) if pd.notna(raw_certs) else 0.0
    
    # Scale to 0-100 for visual uniformity
    stu_values = [
        stu_acad,
        stu_att,
        (stu_sql / 3.0) * 100.0,
        (stu_py / 3.0) * 100.0,
        (stu_bi / 3.0) * 100.0,
        min((stu_certs / 5.0) * 100.0, 100.0)
    ]
    
    if len(batch_df) > 0:
        b_acad = batch_df["academic_percentage"].dropna()
        avg_acad = float(b_acad.mean()) if len(b_acad) > 0 else 0.0
        b_att = batch_df["attendance_percentage"].dropna()
        avg_att = float(b_att.mean()) if len(b_att) > 0 else 0.0
        b_sql = batch_df["sql_proficiency"].dropna().map(prof_map)
        avg_sql = float(b_sql.mean()) if len(b_sql) > 0 else 1.0
        b_py = batch_df["python_proficiency"].dropna().map(prof_map)
        avg_py = float(b_py.mean()) if len(b_py) > 0 else 1.0
        b_bi = batch_df["power_bi_proficiency"].dropna().map(prof_map)
        avg_bi = float(b_bi.mean()) if len(b_bi) > 0 else 1.0
        b_certs = batch_df["certifications_count"].dropna()
        avg_certs = float(b_certs.mean()) if len(b_certs) > 0 else 0.0
    else:
        avg_acad, avg_att, avg_sql, avg_py, avg_bi, avg_certs = 0.0, 0.0, 1.0, 1.0, 1.0, 0.0
    
    batch_values = [
        avg_acad,
        avg_att,
        (avg_sql / 3.0) * 100.0,
        (avg_py / 3.0) * 100.0,
        (avg_bi / 3.0) * 100.0,
        min((avg_certs / 5.0) * 100.0, 100.0)
    ]
    
    radar_categories = categories + [categories[0]]
    stu_values += [stu_values[0]]
    batch_values += [batch_values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=batch_values,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(148, 163, 184, 0.22)',
        line=dict(color='#94A3B8', width=2, dash='dot'),
        name='Cohort Benchmark Average',
        hovertemplate="Dimension: <b>%{theta}</b><br>Cohort Avg: <b>%{r:.1f}%</b><extra></extra>"
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=stu_values,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.32)',
        line=dict(color=COLOR_PRIMARY, width=2.8),
        name=f"Student Profile ({student.get('student_name', 'Selected')})",
        hovertemplate="Dimension: <b>%{theta}</b><br>Student Score: <b>%{r:.1f}%</b><extra></extra>"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100], 
                showline=False, 
                ticksuffix="%",
                tickfont=dict(size=9.5, color="#94A3B8")
            ),
            angularaxis=dict(
                tickfont=dict(size=10, family=DEFAULT_FONT, color="#1E293B")
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        title=dict(
            text="<b>Multi-Axis Competency Benchmark</b><br><span style='font-size:11.5px; color:#64748B;'>Individual student scores indexed against batch average</span>",
            font=dict(size=14, color="#0F172A")
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#475569")
        ),
        margin=dict(l=20, r=20, t=50, b=45),
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=DEFAULT_FONT, size=11, color="#334155")
    )
    return fig


def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Heatmap of numerical correlation matrix with clear formatting."""
    if len(corr_df) == 0:
        return go.Figure()
        
    labels = {
        "academic_percentage": "Academic %",
        "attendance_percentage": "Attendance %",
        "certifications_count": "Certifications",
        "technical_score_10": "Tech Index (10)",
        "salary_lpa": "Package (LPA)"
    }
    
    clean_labels = [labels.get(c, c) for c in corr_df.columns]
    
    fig = px.imshow(
        corr_df.values,
        x=clean_labels,
        y=clean_labels,
        color_continuous_scale="Blues",
        zmin=-1,
        zmax=1,
        text_auto=".2f",
        title="<b>Pairwise Correlation Matrix</b><br><span style='font-size:11.5px; color:#64748B;'>Pearson correlation coefficients among numerical attributes</span>"
    )
    fig.update_traces(
        hovertemplate="Factor 1: <b>%{y}</b><br>Factor 2: <b>%{x}</b><br>Correlation r: <b>%{z:.3f}</b><extra></extra>"
    )
    fig.update_layout(**DEFAULT_LAYOUT)
    fig.update_layout(margin=dict(l=20, r=15, t=50, b=25))
    fig.update_xaxes(tickangle=-25, tickfont=dict(size=10, color="#64748B"))
    fig.update_yaxes(tickfont=dict(size=10, color="#64748B"))
    return fig


def plot_semester_comparison(df: pd.DataFrame) -> go.Figure:
    """Boxplot of academic performance across semesters with jittered dots."""
    if len(df) == 0:
        fig = go.Figure()
        fig.update_layout(title="No Semester Data Available", **DEFAULT_LAYOUT)
        return fig
        
    fig = px.box(
        df,
        x="semester",
        y="academic_percentage",
        color="semester",
        color_discrete_sequence=PALETTE_CATEGORICAL,
        category_orders={"semester": ["Semester 1", "Semester 2", "Semester 3", "Semester 4"]},
        labels={"semester": "Semester", "academic_percentage": "Academic Aggregate (%)"},
        title="<b>Semester-Level Academic Progression</b><br><span style='font-size:12px; color:#64748B;'>Distribution of marks across curriculum semesters</span>"
    )
    fig.update_traces(
        hovertemplate="Semester: <b>%{x}</b><br>Score: <b>%{y:.1f}%</b><extra></extra>",
        marker=dict(size=3.5, opacity=0.6)
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig)
    fig.update_traces(
        hovertemplate="Semester: <b>%{x}</b><br>Score: <b>%{y:.1f}%</b><extra></extra>",
        marker=dict(size=3.5, opacity=0.6)
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig)
