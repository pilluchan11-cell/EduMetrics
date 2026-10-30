"""
Data Management, Upload, and Validation View for EduMetrics.
Enables custom CSV ingestion, schema validation, SQLite persistence, and filtered data exports.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from src.data_loader import validate_dataframe, clean_and_enrich_data
from src.data_generator import ensure_default_dataset
from src.database import (
    save_dataframe_to_db, 
    load_data_from_db,
    get_connection,
    ensure_database_initialized,
    query_total_students_by_specialization,
    query_avg_academic_score_by_specialization,
    query_placement_rate_by_specialization,
    query_avg_salary_by_specialization,
    query_placed_vs_unplaced_counts,
    query_students_below_attendance,
    query_skill_placement_comparison
)
from src.ui_components import (
    render_hero, 
    render_disclaimer, 
    render_section_header,
    render_footer
)
from src.config import EXPECTED_COLUMNS, DEFAULT_CSV_PATH, DB_PATH, DATABASE_DIR


def render(current_df: pd.DataFrame) -> None:
    """Renders the data management, SQL analytics, and data pipeline page."""
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
            "EduMetrics incorporates a normalized 3NF SQLite database layer with primary/foreign key constraints and automated seeding.",
            "🗄️"
        )
        
        # Ensure database is present
        ensure_database_initialized()
        
        # Compute database statistics
        db_exists = DB_PATH.exists()
        db_size_kb = round(DB_PATH.stat().st_size / 1024, 1) if db_exists else 0.0
        
        total_students_count = 0
        total_academics_count = 0
        total_skills_count = 0
        total_placements_count = 0
        
        try:
            conn = get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM students;")
                total_students_count = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM academic_records;")
                total_academics_count = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM skills;")
                total_skills_count = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM placements;")
                total_placements_count = cursor.fetchone()[0]
            conn.close()
        except Exception:
            pass
            
        # Display Database Health KPIs
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Database Engine", "SQLite 3 (ACID)")
        with k2:
            st.metric("Total Stored Students", f"{total_students_count:,}")
        with k3:
            st.metric("Normalized Tables", "4 Relational Tables")
        with k4:
            st.metric("Database File Size", f"{db_size_kb} KB")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.write(
            "This relational architecture separates student demographic records (`students`), examination metrics (`academic_records`), "
            "technical competencies (`skills`), and recruitment outcomes (`placements`), enforcing referential integrity with cascading constraints."
        )
        
        # Database Sync & Reload Controls
        c_db1, c_db2 = st.columns(2)
        with c_db1:
            if st.button("💾 Synchronize Active Dataset into SQLite Database", use_container_width=True):
                try:
                    count = save_dataframe_to_db(current_df)
                    st.success(f"Successfully committed {count} student records across 4 relational tables into SQLite database (`edumetrics.db`)!")
                    st.rerun()
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
                    
        st.markdown("<hr style='margin: 24px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        # Interactive SQL Analytical Explorer
        render_section_header(
            "SQL Analytics & Relational Explorer",
            "Execute normalized analytical SQL queries with parameterization, aggregations, and live joins.",
            "⚡"
        )
        
        query_options = [
            "1. Total Students & Cohort Share by Specialization",
            "2. Average, Minimum & Maximum Academic Marks by Specialization",
            "3. Placement Rate & Student Volume by Specialization",
            "4. Average & Range Salary (CTC) by Specialization",
            "5. Placed vs Unplaced Cohort Counts & Percentages",
            "6. Parameterized Query: Students Below Attendance Cutoff",
            "7. Parameterized Query: Skill-Wise Placement & Salary Comparison"
        ]
        
        selected_query = st.selectbox(
            "Select Analytical SQL Query to Execute:",
            options=query_options,
            index=0,
            help="Choose an analytical query to inspect its SQL code and view query results directly from SQLite."
        )
        
        # Dynamic parameter controls for queries 6 and 7
        attendance_threshold = 75.0
        selected_skill = "python_proficiency"
        
        if selected_query.startswith("6."):
            attendance_threshold = st.slider(
                "Attendance Cutoff Threshold (%):",
                min_value=50.0,
                max_value=90.0,
                value=75.0,
                step=1.0,
                help="Parameterized SQL filter: WHERE attendance_percentage < ?"
            )
        elif selected_query.startswith("7."):
            skill_map = {
                "python_proficiency": "Python Programming",
                "sql_proficiency": "SQL Database Querying",
                "power_bi_proficiency": "Power BI & Data Visualization"
            }
            selected_skill = st.selectbox(
                "Select Skill Competency Dimension:",
                options=list(skill_map.keys()),
                format_func=lambda x: skill_map.get(x, x),
                help="Group placement metrics by the selected technical skill."
            )
                
        # Execute query against SQLite database
        conn = get_connection()
        try:
            if selected_query.startswith("1."):
                sql_text, query_df = query_total_students_by_specialization(conn)
                desc = "Aggregates total student headcount and cohort share percentage across each academic specialization in the `students` table."
            elif selected_query.startswith("2."):
                sql_text, query_df = query_avg_academic_score_by_specialization(conn)
                desc = "Computes summary statistics (mean, minimum, maximum) of academic percentage scores joined across `students` and `academic_records`."
            elif selected_query.startswith("3."):
                sql_text, query_df = query_placement_rate_by_specialization(conn)
                desc = "Calculates placement conversion percentage by joining `students` and `placements` tables."
            elif selected_query.startswith("4."):
                sql_text, query_df = query_avg_salary_by_specialization(conn)
                desc = "Computes mean, minimum, and highest compensation (CTC in ₹ LPA) for placed candidates across specializations."
            elif selected_query.startswith("5."):
                sql_text, query_df = query_placed_vs_unplaced_counts(conn)
                desc = "Groups recruitment outcomes across the entire student population in `placements`."
            elif selected_query.startswith("6."):
                sql_text, query_df = query_students_below_attendance(conn, threshold=attendance_threshold)
                desc = f"Executes a parameterized query (`WHERE attendance_percentage < ?`) returning students below {attendance_threshold}% attendance."
            elif selected_query.startswith("7."):
                sql_text, query_df = query_skill_placement_comparison(conn, skill_name=selected_skill)
                desc = f"Evaluates recruitment conversion and average compensation across proficiency levels for `{selected_skill}`."
            else:
                sql_text, query_df = query_total_students_by_specialization(conn)
                desc = "Aggregates total student headcount across specializations."
                
            st.info(f"💡 **Analytical Intent:** {desc}")
            
            with st.expander("📝 View Raw SQL Query", expanded=True):
                st.code(sql_text.strip(), language="sql")
                
            st.markdown(f"**Query Results** (`{len(query_df)}` records returned):")
            st.dataframe(query_df, use_container_width=True, hide_index=True)
            
            # Export Query Results
            q_csv = query_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"⬇️ Export Query Result ({len(query_df)} rows as CSV)",
                data=q_csv,
                file_name=f"sql_query_result_{selected_query[:7].strip()}.csv",
                mime="text/csv",
                key="download_sql_result"
            )
        except Exception as q_err:
            st.error(f"Error executing SQL query: {str(q_err)}")
        finally:
            conn.close()
            
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📐 Relational Architecture & 3NF Schema DDL"):
            st.markdown("""
            ### Relational Model Design
            - **Normalization Level:** Third Normal Form (3NF) - eliminates transitive and partial dependencies.
            - **Referential Integrity:** `student_id` acts as PK in `students` and is referenced as a FK in `academic_records`, `skills`, and `placements` with `ON DELETE CASCADE`.
            - **Data Constraints:** CHECK constraints enforce percentage intervals `[0.0, 100.0]`, valid categorical values, and positive compensation figures.
            - **Performance Indexes:** 7 secondary B-tree indexes optimize high-frequency filtering on specialization, semester, attendance, and placement status.
            """)
            schema_file = DATABASE_DIR / "schema.sql"
            if schema_file.exists():
                with open(schema_file, "r", encoding="utf-8") as f:
                    ddl_sql = f.read()
                st.code(ddl_sql, language="sql")

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
