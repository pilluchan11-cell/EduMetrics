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

# Initialize active dataset in session state and ensure relational database is ready
if "active_dataset" not in st.session_state:
    initial_df, report = load_cached_dataset()
    st.session_state["active_dataset"] = initial_df
    try:
        from src.database import ensure_database_initialized
        ensure_database_initialized()
    except Exception:
        pass


def main():
    # Retrieve base dataset from state
    df_raw = st.session_state["active_dataset"]

    # Sidebar Navigation & Branding
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 38px; height: 38px; border-radius: 9px; background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); display: flex; align-items: center; justify-content: center; font-size: 20px; color: white; box-shadow: 0 4px 10px rgba(37,99,235,0.25);">
                        🎓
                    </div>
                    <div>
                        <h2 style="margin: 0; color: #0F172A; font-weight: 800; font-size: 21px; letter-spacing: -0.02em;">{APP_NAME}</h2>
                        <span style="font-size: 10.5px; font-weight: 700; color: #2563EB; letter-spacing: 0.05em; text-transform: uppercase;">Analytics Suite</span>
                    </div>
                </div>
                <div style="font-size: 12px; color: #64748B; font-weight: 500; margin-top: 8px; line-height: 1.4;">
                    {APP_TAGLINE}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="font-size: 11px; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">
                ANALYTICS MODULES
            </div>
            """,
            unsafe_allow_html=True
        )
        
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
        
        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size: 11px; font-weight: 700; color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">
                COHORT SLICING FILTERS
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 1. Specialization Multi-select
        all_specs = sorted(list(df_raw["specialization"].dropna().unique()))
        selected_specs = st.multiselect(
            "Specialization / Major:",
            options=all_specs,
            default=all_specs,
            help="Filter analytics across student majors."
        )
        
        # 2. Semester Multi-select
        all_sems = sorted(list(df_raw["semester"].dropna().unique()))
        selected_sems = st.multiselect(
            "Curriculum Semester:",
            options=all_sems,
            default=all_sems,
            help="Filter by active study semester."
        )
        
        # 3. Placement Status Radio
        placement_filter = st.radio(
            "Recruitment Status:",
            options=["All Students", "Placed Only", "Unplaced Only"],
            index=0,
            horizontal=False
        )
        
        # 4. Minimum Attendance Slider
        min_attendance = st.slider(
            "Minimum Attendance Cutoff (%):",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            help="Filter for students with attendance at or above this threshold."
        )
        
        # Filter Reset Button
        if st.button("↺ Reset All Slicing Filters", use_container_width=True):
            st.rerun()

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size: 11px; color: #64748B; line-height: 1.5;">
                <strong style="color: #0F172A;">EduMetrics</strong> | Student Performance & Placement Analytics<br>
                <em>MBA Decision Science Research Edition</em>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Apply Global Filters to Dataset
    filtered_df = df_raw.copy()
    
    if selected_specs:
        filtered_df = filtered_df[filtered_df["specialization"].isin(selected_specs)]
    else:
        filtered_df = filtered_df.iloc[0:0]
        
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

    # Quick Active Filter Badge
    total_raw = len(df_raw)
    current_count = len(filtered_df)
    pct_showing = round((current_count / total_raw) * 100.0, 1) if total_raw > 0 else 0
    
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; margin-top: -8px; margin-bottom: 10px;">
            <span style="font-size: 12px; font-weight: 600; color: #1E40AF; background: #EFF6FF; border: 1px solid #DBEAFE; padding: 4px 14px; border-radius: 9999px;">
                Active Filter: <strong>{current_count}</strong> of <strong>{total_raw}</strong> Students ({pct_showing}%)
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
