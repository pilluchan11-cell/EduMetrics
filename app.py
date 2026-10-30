"""
EduMetrics - Student Performance & Placement Analytics Dashboard
Main application entry point and global navigation router.

Tagline: Turning Student Data into Smarter Career Decisions.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    APP_NAME,
    APP_TAGLINE,
    APP_SUBTITLE,
    SYNTHETIC_DATA_DISCLAIMER
)
from src.data_loader import load_cached_dataset
from src.ui_components import inject_custom_css
from src.views import (
    executive,
    academic,
    placement,
    student,
    statistical,
    recommendations,
    data_mgmt
)

# Configure Streamlit page settings
st.set_page_config(
    page_title=f"{APP_NAME} | Student & Placement Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom UI styling
inject_custom_css()

# Initialize active dataset in session state
if "active_dataset" not in st.session_state:
    initial_df, report = load_cached_dataset()
    st.session_state["active_dataset"] = initial_df


def main():
    # Retrieve base dataset from state
    df_raw = st.session_state["active_dataset"]

    # Sidebar Navigation & Branding
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 12px 0 16px 0;">
                <h2 style="margin: 0; color: #1E3A8A; font-weight: 800; font-size: 24px;">🎓 {APP_NAME}</h2>
                <div style="font-size: 11.5px; color: #475569; font-weight: 500; margin-top: 4px;">{APP_TAGLINE}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        st.markdown("**MODULE NAVIGATION**")
        
        page = st.radio(
            "Select Dashboard View:",
            options=[
                "📊 Executive Dashboard",
                "📚 Academic Performance",
                "💼 Placement Analytics",
                "👤 Student Analytics",
                "📈 Statistical Analysis",
                "🎯 Strategic Recommendations",
                "⚙️ Data Management & Upload"
            ],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("**GLOBAL COHORT FILTERS**")
        
        # 1. Specialization Multi-select
        all_specs = sorted(list(df_raw["specialization"].dropna().unique()))
        selected_specs = st.multiselect(
            "Specialization / Major:",
            options=all_specs,
            default=all_specs,
            help="Filter analytics by student major."
        )
        
        # 2. Semester Multi-select
        all_sems = sorted(list(df_raw["semester"].dropna().unique()))
        selected_sems = st.multiselect(
            "Semester:",
            options=all_sems,
            default=all_sems,
            help="Filter by active study semester."
        )
        
        # 3. Placement Status Radio
        placement_filter = st.radio(
            "Placement Status:",
            options=["All Students", "Placed Only", "Unplaced Only"],
            index=0,
            horizontal=False
        )
        
        # 4. Minimum Attendance Slider
        min_attendance = st.slider(
            "Minimum Attendance (%):",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            help="Filter for students with attendance above this threshold."
        )
        
        # Filter Reset Button
        if st.button("↺ Reset All Filters", use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 11px; color: #94A3B8; line-height: 1.4;">
                <strong>EduMetrics v1.0.0</strong><br>
                Built with Python & Streamlit.<br>
                <em>Data is 100% synthetic for academic demonstration.</em>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Apply Global Filters to Dataset
    filtered_df = df_raw.copy()
    
    if selected_specs:
        filtered_df = filtered_df[filtered_df["specialization"].isin(selected_specs)]
    else:
        filtered_df = filtered_df.iloc[0:0]  # Empty if none selected
        
    if selected_sems:
        filtered_df = filtered_df[filtered_df["semester"].isin(selected_sems)]
    else:
        filtered_df = filtered_df.iloc[0:0]
        
    if placement_filter == "Placed Only":
        filtered_df = filtered_df[filtered_df["placement_status"].str.lower() == "placed"]
    elif placement_filter == "Unplaced Only":
        filtered_df = filtered_df[filtered_df["placement_status"].str.lower() == "unplaced"]
        
    if min_attendance > 0:
        filtered_df = filtered_df[filtered_df["attendance_percentage"] >= min_attendance]

    # Quick Cohort Indicator
    total_raw = len(df_raw)
    current_count = len(filtered_df)
    pct_showing = round((current_count / total_raw) * 100.0, 1) if total_raw > 0 else 0
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: -15px;">
            <span style="font-size: 12px; color: #64748B; background: #F1F5F9; padding: 4px 12px; border-radius: 9999px;">
                Active Filter: <strong>{current_count}</strong> of <strong>{total_raw}</strong> students ({pct_showing}%)
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Route to Selected Module
    if page == "📊 Executive Dashboard":
        executive.render(filtered_df)
    elif page == "📚 Academic Performance":
        academic.render(filtered_df)
    elif page == "💼 Placement Analytics":
        placement.render(filtered_df)
    elif page == "👤 Student Analytics":
        student.render(filtered_df)
    elif page == "📈 Statistical Analysis":
        statistical.render(filtered_df)
    elif page == "🎯 Strategic Recommendations":
        recommendations.render(filtered_df)
    elif page == "⚙️ Data Management & Upload":
        data_mgmt.render(filtered_df)


if __name__ == "__main__":
    main()
