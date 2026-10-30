"""
UI Components and Design System for EduMetrics.
Injects custom CSS, renders KPI metric cards, and handles aesthetic styling.
"""

import streamlit as st
from src.config import (
    APP_NAME,
    APP_TAGLINE,
    SYNTHETIC_DATA_DISCLAIMER,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_ACCENT
)


def inject_custom_css() -> None:
    """Injects high-end, responsive custom styling for a polished SaaS dashboard."""
    css = f"""
    <style>
    /* Global Typography & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}
    
    /* Remove excess top padding in Streamlit */
    .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }}
    
    /* Hero Header */
    .hero-container {{
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 55%, #0D9488 100%);
        border-radius: 12px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.18);
    }}
    .hero-title {{
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .hero-tagline {{
        font-size: 15px;
        font-weight: 400;
        opacity: 0.92;
        margin-top: 6px;
        margin-bottom: 0px;
    }}
    
    /* KPI Metric Cards */
    .kpi-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        margin-bottom: 12px;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    }}
    .kpi-title {{
        font-size: 12.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748B;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
    }}
    .kpi-subtext {{
        font-size: 12px;
        color: #94A3B8;
        margin-top: 6px;
    }}
    
    /* Status Badges */
    .badge-placed {{
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }}
    .badge-unplaced {{
        background-color: #F1F5F9;
        color: #475569;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }}
    .badge-warning {{
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }}
    .badge-danger {{
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
    }}
    
    /* Section Headings */
    .section-title {{
        font-size: 19px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 20px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    /* Synthetic Banner */
    .synthetic-banner {{
        background-color: #F8FAFC;
        border-left: 4px solid #2563EB;
        padding: 10px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
        font-size: 12.5px;
        color: #475569;
    }}
    
    /* Recommendation Card */
    .rec-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }}
    .rec-card.critical {{
        border-left: 4px solid #EF4444;
    }}
    .rec-card.action {{
        border-left: 4px solid #F59E0B;
    }}
    .rec-card.strength {{
        border-left: 4px solid #10B981;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_hero(current_page_title: str) -> None:
    """Renders the executive hero banner."""
    html = f"""
    <div class="hero-container">
        <div class="hero-title">
            <span>🎓 {APP_NAME}</span>
            <span style="font-size: 18px; opacity: 0.8; font-weight: 400;">| {current_page_title}</span>
        </div>
        <div class="hero-tagline">{APP_TAGLINE}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_disclaimer() -> None:
    """Displays the synthetic data notice."""
    html = f"""
    <div class="synthetic-banner">
        <strong>ℹ️ Notice:</strong> {SYNTHETIC_DATA_DISCLAIMER}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi(title: str, value: str, subtext: str = "", border_color: str = "#2563EB") -> None:
    """Renders an individual KPI metric card."""
    html = f"""
    <div class="kpi-card" style="border-top: 3px solid {border_color};">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
