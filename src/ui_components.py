"""
UI Components and Design System for EduMetrics.
Injects responsive custom CSS, renders KPI metric cards, hero headers, and aesthetic elements
tailored for desktop, laptop, tablet, and mobile presentations.
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
    """Injects high-end, responsive custom styling optimized across all screen viewports."""
    css = """
    <style>
    /* ==================================================================== */
    /* Global Typography & Viewport Setup                                  */
    /* ==================================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0F172A;
        -webkit-font-smoothing: antialiased;
    }

    /* Prevent accidental horizontal scrolling across all viewports */
    .stApp {
        overflow-x: hidden;
        max-width: 100vw;
    }

    /* ==================================================================== */
    /* Responsive Block Container (Desktop, Tablet, Mobile)               */
    /* ==================================================================== */
    .block-container {
        width: 100% !important;
        max-width: 1600px !important;
        margin: 0 auto !important;
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        box-sizing: border-box !important;
    }

    /* Tablet Viewports (768px - 1024px) */
    @media screen and (max-width: 1024px) {
        .block-container {
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }
    }

    /* Mobile Viewports (320px - 640px) */
    @media screen and (max-width: 640px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 0.75rem !important;
            padding-bottom: 1.6rem !important;
        }
    }

    /* Extra-Small Mobile (<= 360px) */
    @media screen and (max-width: 360px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
        }
    }

    /* ==================================================================== */
    /* Streamlit Column Wrapping & Responsive Grid                          */
    /* ==================================================================== */
    /* Ensure all Streamlit columns can shrink below intrinsic content size */
    div[data-testid="stColumn"] {
        min-width: 0 !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stHorizontalBlock"] {
        width: 100% !important;
        box-sizing: border-box !important;
        align-items: stretch !important;
    }

    /* Tablet & Small-Screen breakpoint: Stack columns cleanly */
    @media screen and (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 12px 0 !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 8px !important;
        }
    }

    /* ==================================================================== */
    /* Executive Hero Header                                                */
    /* ==================================================================== */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 55%, #1D4ED8 100%);
        border-radius: clamp(10px, 2vw, 14px);
        padding: clamp(14px, 3vw, 24px) clamp(16px, 3.5vw, 30px);
        color: #FFFFFF;
        margin-bottom: clamp(14px, 2.5vw, 22px);
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25), 0 8px 10px -6px rgba(30, 58, 138, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: clamp(9.5px, 1.8vw, 11px);
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #93C5FD;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .hero-title {
        font-size: clamp(18px, 4vw, 26px);
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px 10px;
        color: #FFFFFF;
        line-height: 1.25;
        word-break: break-word;
    }
    .hero-tagline {
        font-size: clamp(12px, 2.2vw, 14px);
        font-weight: 400;
        color: #E2E8F0;
        margin-top: 6px;
        margin-bottom: 0px;
        opacity: 0.95;
        line-height: 1.4;
    }

    /* ==================================================================== */
    /* Modern KPI Metric Cards                                              */
    /* ==================================================================== */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 12px;
        position: relative;
        overflow: visible;
        box-sizing: border-box;
        width: 100%;
        min-height: 145px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.08);
    }
    .kpi-top-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 6px;
        width: 100%;
    }
    .kpi-title {
        font-size: 11.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        line-height: 1.35;
        flex: 1 1 auto;
        margin: 0;
        word-break: break-word;
    }
    .kpi-icon {
        width: 28px;
        height: 28px;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        background: #F1F5F9;
        flex-shrink: 0;
    }
    .kpi-value {
        font-size: clamp(20px, 2.2vw, 26px);
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.25;
        word-break: break-word;
        margin: 4px 0 8px 0;
    }
    .kpi-subtext-container {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
        font-size: 11.5px;
        color: #64748B;
        line-height: 1.4;
        margin-top: auto;
        word-break: break-word;
    }
    .kpi-chip {
        display: inline-flex;
        align-items: center;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        line-height: 1.3;
        white-space: normal;
        word-break: break-word;
    }

    /* ==================================================================== */
    /* Section Headings                                                     */
    /* ==================================================================== */
    .section-header-container {
        margin-top: 24px;
        margin-bottom: 14px;
        clear: both;
        display: block;
    }
    .section-title {
        font-size: clamp(16px, 2.5vw, 19px);
        font-weight: 700;
        color: #0F172A;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px 10px;
        margin: 0 0 4px 0;
        letter-spacing: -0.01em;
        line-height: 1.35;
        word-break: break-word;
    }
    .section-description {
        font-size: clamp(12px, 1.8vw, 13px);
        color: #64748B;
        margin: 0;
        line-height: 1.5;
        word-break: break-word;
    }

    /* ==================================================================== */
    /* Responsive Student Dossier Card                                      */
    /* ==================================================================== */
    .student-dossier-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: clamp(14px, 2.8vw, 22px) clamp(14px, 3vw, 28px);
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 14px;
        box-sizing: border-box;
    }
    .student-dossier-left {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: clamp(10px, 2vw, 18px);
    }
    .student-dossier-avatar {
        width: clamp(40px, 7vw, 54px);
        height: clamp(40px, 7vw, 54px);
        border-radius: 12px;
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(18px, 3.5vw, 24px);
        color: white;
        flex-shrink: 0;
    }
    .student-dossier-name-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }
    .student-dossier-name {
        margin: 0;
        font-size: clamp(17px, 3.5vw, 22px);
        font-weight: 800;
        color: #0F172A;
        word-break: break-word;
    }
    .student-dossier-meta {
        color: #64748B;
        font-size: clamp(11.5px, 2vw, 13.5px);
        margin-top: 4px;
        line-height: 1.45;
        word-break: break-word;
    }

    /* ==================================================================== */
    /* Insight Cards & Statistical Banners                                  */
    /* ==================================================================== */
    .insight-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: clamp(14px, 2.5vw, 18px) clamp(14px, 2.5vw, 20px);
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
        border-top: 3px solid #2563EB;
        box-sizing: border-box;
    }
    .insight-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 6px;
    }
    .stat-badge-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: clamp(8px, 2vw, 20px);
        font-size: clamp(11.5px, 2vw, 13.5px);
        color: #334155;
    }

    /* ==================================================================== */
    /* Recommendation Cards & Strategic Interventions                      */
    /* ==================================================================== */
    .recommendation-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: clamp(14px, 2.5vw, 20px) clamp(14px, 3vw, 22px);
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        box-sizing: border-box;
    }
    .recommendation-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 8px;
    }
    .recommendation-action-box {
        background: #F8FAFC;
        padding: clamp(10px, 2vw, 14px) clamp(12px, 2vw, 16px);
        border-radius: 6px;
        font-size: clamp(12.5px, 2vw, 13.5px);
        color: #1E293B;
        line-height: 1.5;
        word-break: break-word;
    }
    .info-callout {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 10px;
        padding: clamp(12px, 2vw, 16px) clamp(14px, 2.5vw, 20px);
        margin-bottom: 20px;
        box-sizing: border-box;
    }

    /* ==================================================================== */
    /* Notice Banners & Badges                                              */
    /* ==================================================================== */
    .synthetic-banner {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        padding: clamp(8px, 1.5vw, 10px) clamp(10px, 2vw, 16px);
        border-radius: 6px;
        margin-bottom: 16px;
        font-size: clamp(11px, 1.8vw, 12px);
        color: #475569;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 6px 10px;
        line-height: 1.4;
    }
    .badge-placed, .badge-unplaced, .badge-warning, .badge-danger {
        display: inline-flex;
        align-items: center;
        padding: 3px 9px;
        border-radius: 9999px;
        font-size: clamp(10.5px, 1.8vw, 11.5px);
        font-weight: 600;
        white-space: nowrap;
    }
    .badge-placed { background-color: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; }
    .badge-unplaced { background-color: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }
    .badge-warning { background-color: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
    .badge-danger { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FECACA; }

    /* Filter Badge Container */
    .filter-badge-container {
        display: flex;
        justify-content: flex-end;
        margin-top: -6px;
        margin-bottom: 10px;
    }
    @media screen and (max-width: 640px) {
        .filter-badge-container {
            justify-content: flex-start;
        }
    }

    /* ==================================================================== */
    /* Footer & App Polish                                                  */
    /* ==================================================================== */
    .app-footer {
        margin-top: clamp(24px, 4vw, 45px);
        padding-top: 16px;
        border-top: 1px solid #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px 14px;
        font-size: clamp(10.5px, 1.8vw, 12px);
        color: #94A3B8;
        line-height: 1.4;
    }

    /* Streamlit Widget Responsive Polish */
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }

    /* Tabs responsive wrap */
    div[data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        gap: 6px !important;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 16px;
    }
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: clamp(11.5px, 2vw, 13.5px) !important;
        padding: clamp(6px, 1.5vw, 8px) clamp(10px, 2vw, 16px) !important;
        border-radius: 6px 6px 0 0 !important;
    }

    /* Streamlit Buttons: Prevent text overflow and overlap across all viewports */
    button[data-testid="baseButton-secondary"], 
    button[data-testid="baseButton-primary"] {
        white-space: normal !important;
        word-wrap: break-word !important;
        word-break: break-word !important;
        height: auto !important;
        min-height: 42px !important;
        padding: 8px 14px !important;
        line-height: 1.35 !important;
        text-align: center !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
    }

    /* Streamlit Widget Labels & Inputs */
    label[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        line-height: 1.4 !important;
        margin-bottom: 5px !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
    div[data-testid="stSelectbox"],
    div[data-testid="stTextInput"],
    div[data-testid="stNumberInput"],
    div[data-testid="stMultiSelect"] {
        margin-bottom: 8px !important;
    }

    /* Streamlit Metric Boxes */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        box-sizing: border-box;
        min-width: 0 !important;
        word-break: break-word !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #64748B !important;
        line-height: 1.35 !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: clamp(18px, 2.5vw, 24px) !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        line-height: 1.25 !important;
        margin: 4px 0 !important;
    }

    /* Plotly Chart Container Responsive Behavior */
    .js-plotly-plot, .plot-container {
        width: 100% !important;
        max-width: 100% !important;
    }
    .js-plotly-plot .plotly .main-svg {
        overflow: visible !important;
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
            <span style="font-size: clamp(15px, 3vw, 20px); font-weight: 400; opacity: 0.75;">/ {current_page_title}</span>
        </div>
        <div class="hero-tagline">{APP_TAGLINE}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_disclaimer() -> None:
    """Displays the synthetic data notice in a subtle corporate callout."""
    html = f"""
    <div class="synthetic-banner">
        <span style="font-size: 15px;">🛡️</span>
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
        <div>MBA Decision Science Platform • v1.0.0</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
