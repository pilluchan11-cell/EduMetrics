"""
UI Components and Design System for EduMetrics.
Injects custom CSS, renders KPI metric cards, hero headers, and aesthetic elements
tailored for executive and MBA presentations.
"""

import streamlit as st
from typing import Optional
from src.config import (
    APP_NAME,
    APP_TAGLINE,
    SYNTHETIC_DATA_DISCLAIMER,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_ACCENT,
    COLOR_SECONDARY
)


def inject_custom_css() -> None:
    """Injects high-end, responsive custom styling for a polished SaaS dashboard."""
    css = """
    <style>
    /* Global Typography & Background */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0F172A;
    }
    
    /* Layout Containers */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 1440px;
    }
    
    /* Executive Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 55%, #1D4ED8 100%);
        border-radius: 14px;
        padding: 24px 30px;
        color: #FFFFFF;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25), 0 8px 10px -6px rgba(30, 58, 138, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .hero-container::after {
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #93C5FD;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #FFFFFF;
    }
    .hero-tagline {
        font-size: 14px;
        font-weight: 400;
        color: #E2E8F0;
        margin-top: 6px;
        margin-bottom: 0px;
        opacity: 0.95;
    }
    
    /* Modern KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.08), 0 6px 8px -4px rgba(15, 23, 42, 0.04);
        border-color: #CBD5E1;
    }
    .kpi-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .kpi-title {
        font-size: 11.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
    }
    .kpi-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        background: #F1F5F9;
    }
    .kpi-value {
        font-size: 27px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .kpi-subtext-container {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 8px;
        font-size: 12px;
        color: #64748B;
    }
    .kpi-chip {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }
    
    /* Section Headings with Description */
    .section-header-container {
        margin-top: 22px;
        margin-bottom: 14px;
    }
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .section-description {
        font-size: 13px;
        color: #64748B;
        margin-top: 3px;
        margin-bottom: 0px;
    }
    
    /* Status Badges */
    .badge-placed {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11.5px;
        font-weight: 600;
        border: 1px solid #BBF7D0;
    }
    .badge-unplaced {
        background-color: #F1F5F9;
        color: #475569;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11.5px;
        font-weight: 600;
        border: 1px solid #E2E8F0;
    }
    .badge-warning {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11.5px;
        font-weight: 600;
        border: 1px solid #FDE68A;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 11.5px;
        font-weight: 600;
        border: 1px solid #FECACA;
    }
    
    /* Notice Banners */
    .synthetic-banner {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        padding: 10px 16px;
        border-radius: 6px;
        margin-bottom: 20px;
        font-size: 12px;
        color: #475569;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Recommendation Cards */
    .rec-card-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .rec-card-container.critical {
        border-left: 4px solid #EF4444;
    }
    .rec-card-container.action {
        border-left: 4px solid #F59E0B;
    }
    .rec-card-container.strength {
        border-left: 4px solid #10B981;
    }
    
    /* Styled Footer */
    .app-footer {
        margin-top: 45px;
        padding-top: 18px;
        border-top: 1px solid #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #94A3B8;
    }
    
    /* Streamlit Native Widget Polishing */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    div[data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 13.5px !important;
        padding: 8px 16px !important;
        border-radius: 6px 6px 0 0 !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_hero(current_page_title: str) -> None:
    """Renders the executive hero banner with modern MBA BI aesthetic."""
    html = f"""
    <div class="hero-container">
        <div class="hero-badge">🎓 EXECUTIVE ANALYTICS SUITE</div>
        <div class="hero-title">
            <span>{APP_NAME}</span>
            <span style="font-size: 20px; font-weight: 400; opacity: 0.75;">/ {current_page_title}</span>
        </div>
        <div class="hero-tagline">{APP_TAGLINE}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_disclaimer() -> None:
    """Displays the synthetic data notice in a subtle corporate callout."""
    html = f"""
    <div class="synthetic-banner">
        <span>🛡️</span>
        <div><strong>Synthetic Research Benchmark:</strong> {SYNTHETIC_DATA_DISCLAIMER}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(title: str, description: Optional[str] = None, icon: str = "") -> None:
    """Renders a standard section header with an explanatory business subtitle."""
    icon_str = f"{icon} " if icon else ""
    desc_html = f'<div class="section-description">{description}</div>' if description else ""
    html = f"""
    <div class="section-header-container">
        <div class="section-title">{icon_str}{title}</div>
        {desc_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_kpi(
    title: str, 
    value: str, 
    subtext: str = "", 
    border_color: str = "#2563EB", 
    icon: str = "📊",
    chip_text: Optional[str] = None,
    chip_color: Optional[str] = None
) -> None:
    """Renders an individual KPI card with modern typography and visual anchors."""
    chip_html = ""
    if chip_text:
        bg_col = chip_color or "#EFF6FF"
        text_col = border_color
        chip_html = f'<span class="kpi-chip" style="background: {bg_col}; color: {text_col};">{chip_text}</span>'
        
    html = f"""
    <div class="kpi-card" style="border-top: 3px solid {border_color};">
        <div class="kpi-top-row">
            <span class="kpi-title">{title}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext-container">
            {chip_html}
            <span>{subtext}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_footer() -> None:
    """Renders the standard EduMetrics application footer."""
    html = f"""
    <div class="app-footer">
        <div><strong>{APP_NAME}</strong> | Student Performance & Placement Analytics</div>
        <div>MBA Decision Science & Strategic Career Intelligence Platform • v1.0.0</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
