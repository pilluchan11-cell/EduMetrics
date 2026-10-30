"""
Integration tests for Streamlit app rendering using Streamlit AppTest.
Tests initialization and navigation across all 7 dashboard modules.
"""

import pytest
from streamlit.testing.v1 import AppTest


def test_app_renders_without_exception():
    """Verifies that app.py boots and executes without unhandled exceptions."""
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.run()
    assert not at.exception
    assert not at.error


def test_app_navigation_pages():
    """Verifies that each dashboard view renders without errors."""
    pages = [
        "📊 Executive Dashboard",
        "📚 Academic Performance",
        "💼 Placement Analytics",
        "👤 Student Analytics",
        "📝 Student Assessment",
        "📈 Statistical Analysis",
        "🎯 Strategic Recommendations",
        "⚙️ Data Management & Upload"
    ]
    
    for page_name in pages:
        at = AppTest.from_file("../app.py", default_timeout=30)
        at.run()
        # Find radio widget and select page
        radio = at.sidebar.radio[0]
        radio.set_value(page_name)
        at.run()
        assert not at.exception, f"Exception on page {page_name}"
        assert not at.error, f"Error on page {page_name}"


def test_app_zero_records_filter_resilience():
    """
    Verifies that when filters return 0 records (empty cohort),
    the application does NOT crash across any of the 7 dashboard modules.
    """
    pages = [
        "📊 Executive Dashboard",
        "📚 Academic Performance",
        "💼 Placement Analytics",
        "👤 Student Analytics",
        "📝 Student Assessment",
        "📈 Statistical Analysis",
        "🎯 Strategic Recommendations",
        "⚙️ Data Management & Upload"
    ]
    
    for page_name in pages:
        at = AppTest.from_file("../app.py", default_timeout=30)
        at.run()
        # Set Specialization multiselect to empty list -> produces 0 filtered records
        spec_multiselect = at.sidebar.multiselect[0]
        spec_multiselect.set_value([])
        
        # Navigate to target page
        radio = at.sidebar.radio[0]
        radio.set_value(page_name)
        at.run()
        
        assert not at.exception, f"Exception on page {page_name} with 0 records"
        assert not at.error, f"Error on page {page_name} with 0 records"
