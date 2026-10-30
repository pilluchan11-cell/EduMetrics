"""
Unit tests for SQLite database operations.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.database import save_dataframe_to_db, load_data_from_db
from src.data_generator import generate_synthetic_data


def test_sqlite_ingest_and_load(tmp_path):
    test_db_path = tmp_path / "test_edumetrics.db"
    
    # Generate small dataset
    df = generate_synthetic_data(n=20, seed=123)
    
    # Save to SQLite
    rows_saved = save_dataframe_to_db(df, db_path=test_db_path)
    assert rows_saved == 20
    assert test_db_path.exists()
    
    # Load back from SQLite
    loaded_df = load_data_from_db(db_path=test_db_path)
    assert len(loaded_df) == 20
    assert "student_id" in loaded_df.columns
    assert "placement_status" in loaded_df.columns
    assert "salary_lpa" in loaded_df.columns
