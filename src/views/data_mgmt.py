"""
Data Management, Upload, and Validation View for EduMetrics.
Enables custom CSV ingestion, schema validation, SQLite persistence, and filtered data exports.
"""

import streamlit as st
import pandas as pd
from src.data_loader import validate_dataframe, clean_and_enrich_data
from src.data_generator import ensure_default_dataset
from src.database import save_dataframe_to_db, load_data_from_db
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_section_header,
    render_footer
)
from src.config import EXPECTED_COLUMNS, DEFAULT_CSV_PATH


def render(current_df: pd.DataFrame) -> None:
    """Renders the data management and upload page."""
    render_hero("Data Management & Relational Database Layer")
    render_disclaimer()
    
    tab_upload, tab_db, tab_export = st.tabs([
        "📤 Ingest Custom CSV", 
        "🗄️ Relational SQLite Database", 
        "📥 Export Filtered Cohort Data"
    ])
    
    with tab_upload:
        render_section_header(
            "Upload Custom Institutional Dataset",
            "Upload a custom CSV formatted to the EduMetrics standard schema for automated validation and immediate analysis.",
            "📂"
        )
        
        uploaded_file = st.file_uploader(
            "Select CSV file for upload", 
            type=["csv"], 
            help="File size limit: 25MB per upload."
        )
        
        if uploaded_file is not None:
            try:
                raw_custom_df = pd.read_csv(uploaded_file)
                is_valid, errors, summary = validate_dataframe(raw_custom_df)
                
                st.markdown("### 📋 Automated Schema & Integrity Audit")
                v_col1, v_col2, v_col3 = st.columns(3)
                with v_col1:
                    st.metric("Total Records Ingested", f"{summary['total_rows']:,}")
                with v_col2:
                    st.metric("Duplicate Student IDs", summary["duplicate_ids"])
                with v_col3:
                    status_text = "Verified Valid ✅" if is_valid else "Errors Detected ⚠️"
                    st.metric("Schema Compliance", status_text)
                    
                if errors:
                    st.error("Validation Warnings / Errors:")
                    for err in errors:
                        st.write(f"• {err}")
                        
                if is_valid or st.button("Proceed and Activate Ingested Dataset"):
                    cleaned_custom = clean_and_enrich_data(raw_custom_df)
                    st.session_state["active_dataset"] = cleaned_custom
                    st.success("✅ Dataset successfully validated, enriched, and activated for this application session!")
                    st.dataframe(cleaned_custom.head(5), use_container_width=True)
            except Exception as e:
                st.error(f"Failed to process CSV file: {str(e)}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("Standard Data Schema Reference", "Required column names and data types expected by EduMetrics.", "📖")
        schema_df = pd.DataFrame({
            "Column Name": EXPECTED_COLUMNS,
            "Field Description": [
                "Unique alphanumeric identifier (e.g. EDU-2026-001)",
                "Full student name (fictional)",
                "Demographic label (Male, Female, Non-Binary)",
                "Major / Specialization (e.g. Business Analytics)",
                "Academic semester (e.g. Semester 3)",
                "Aggregate score percentage (0-100)",
                "Lecture attendance percentage (0-100)",
                "SQL proficiency level (Beginner, Intermediate, Advanced)",
                "Python proficiency level (Beginner, Intermediate, Advanced)",
                "Power BI proficiency level (Beginner, Intermediate, Advanced)",
                "Count of completed industry certifications (0-5)",
                "Summer internship status (Completed, Not Completed)",
                "Campus placement outcome (Placed, Unplaced)",
                "Hiring corporate entity (Company name or blank if unplaced)",
                "Annual CTC compensation in LPA (or blank if unplaced)"
            ]
        })
        st.dataframe(schema_df, hide_index=True, use_container_width=True)
        
    with tab_db:
        render_section_header(
            "Relational SQLite Database Integration",
            "EduMetrics incorporates a normalized 3NF SQLite database layer with foreign key constraints.",
            "🗄️"
        )
        st.write("This relational architecture separates student demographic records (`students`) from recruitment outcomes (`placements`), enabling ACID-compliant transactions.")
        
        c_db1, c_db2 = st.columns(2)
        with c_db1:
            if st.button("💾 Synchronize Active Dataset into SQLite Database", use_container_width=True):
                try:
                    count = save_dataframe_to_db(current_df)
                    st.success(f"Successfully committed {count} student records into SQLite database (`edumetrics.db`)!")
                except Exception as e:
                    st.error(f"SQLite Sync error: {str(e)}")
                    
        with c_db2:
            if st.button("🔄 Reload Active Cohort from SQLite Database", use_container_width=True):
                try:
                    db_df = load_data_from_db()
                    if len(db_df) > 0:
                        cleaned_db = clean_and_enrich_data(db_df)
                        st.session_state["active_dataset"] = cleaned_db
                        st.success(f"Loaded {len(cleaned_db)} records from SQLite database!")
                        st.dataframe(cleaned_db.head(5), use_container_width=True)
                    else:
                        st.warning("SQLite database is currently empty. Click 'Synchronize Active Dataset' first.")
                except Exception as e:
                    st.error(f"SQLite Load error: {str(e)}")

    with tab_export:
        render_section_header(
            "Export Active Filtered Cohort",
            f"Export the currently filtered subset ({len(current_df)} students) or reset to benchmark records.",
            "📥"
        )
        
        csv_data = current_df.to_csv(index=False).encode('utf-8')
        
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button(
                label="⬇️ Download Filtered Dataset (CSV)",
                data=csv_data,
                file_name="edumetrics_filtered_students.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_exp2:
            if st.button("↺ Reset to Default Synthetic Benchmark", use_container_width=True):
                default_df = clean_and_enrich_data(ensure_default_dataset())
                st.session_state["active_dataset"] = default_df
                st.success("Session state successfully reset to default 500-student benchmark dataset.")
                st.rerun()
                
    render_footer()
