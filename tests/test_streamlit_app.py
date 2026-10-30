"""
Integration test for Streamlit app rendering using Streamlit AppTest.
"""

import pytest
from streamlit.testing.v1 import AppTest


def test_app_renders_without_exception():
    """Verifies that app.py boots and executes without unhandled exceptions."""
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.run()
    assert not at.exception
    assert not at.error
