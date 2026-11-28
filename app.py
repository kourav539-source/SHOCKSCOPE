import streamlit as st

from modules.evidence_desk import render_evidence_desk
from modules.dashboard import render_dashboard
from modules.event_explorer import render_event_explorer
from modules.impact_analyzer import render_impact_analyzer
from modules.shock_simulator import render_shock_simulator
from modules.company_calculator import render_company_calculator
from modules.case_context import shared_select, reset_case
from modules.visual_intelligence import render_overview


st.set_page_config(
    page_title="SHOCKSCOPE | Economic Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A small amount of CSS gives the prototype a consistent financial-intelligence look.
st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at 12% 0%, #132943 0%, #0b1422 42%, #08101b 100%);
            color: #e9f1fb;
        }
        [data-testid="stSidebar"] {
            background: #0c1726;
            border-right: 1px solid #21334a;
        }
        [data-testid="stHeader"] {
            background: rgba(8, 16, 27, 0.82);
        }
        h1, h2, h3, h4 {
            color: #f1f6ff !important;
        }
        p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
            color: #c3d0e0;
        }
        [data-testid="stCaptionContainer"] p { color: #a8bbd0 !important; }
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #142943, #102137);
            border: 1px solid #29415d;
            border-radius: 14px;
            padding: 15px 17px;
        }
        [data-testid="stMetricLabel"] p {
            color: #a9bdd3 !important;
            font-size: 0.88rem !important;
        }
        [data-testid="stMetricValue"] {
            color: #f4f8ff !important;
        }
        [data-testid="stMetricDelta"] {
            color: #9eb4cd !important;
        }
        div[data-testid="stPlotlyChart"] {
            background: rgba(17, 34, 54, 0.68);
            border: 1px solid #263d57;
            border-radius: 14px;
            padding: 8px;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #263d57;
            border-radius: 12px;
            overflow: hidden;
        }
        .scope-hero {
            background: linear-gradient(110deg, rgba(26, 56, 84, 0.96), rgba(15, 32, 51, 0.92));
            border: 1px solid #34516f;
            border-radius: 18px;
            padding: 26px 28px;
            margin: 4px 0 22px 0;
        }
        .scope-eyebrow {
            color: #79d6ca;
            font-size: 0.76rem;
            letter-spacing: 0.16em;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 9px;
        }
        .scope-title {
            color: #f5f8ff;
            font-size: 2.1rem;
            font-weight: 750;
            line-height: 1.15;
            margin: 0 0 9px 0;
        }
        .scope-subtitle {
            color: #bac9da;
            font-size: 1rem;
            line-height: 1.55;
            max-width: 900px;
            margin: 0;
        }
        .section-kicker {
            color: #79d6ca;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .small-note {
            color: #98adc4;
            font-size: 0.82rem;
        }
        a {
            color: #79d6ca !important;
        }
        hr {
            border-color: #243a52 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 8px 0 14px 0;">
            <div style="font-size: 1.55rem; font-weight: 800; letter-spacing: 0.04em; color: #f4f8ff;">
                SHOCK<span style="color:#79d6ca;">SCOPE</span>
            </div>
            <div style="color:#8fa8c3; font-size:0.72rem; letter-spacing:0.13em;">
                EVENT-TO-ECONOMY INTELLIGENCE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**WORKSPACE**")
    page = st.radio("Navigate", ["00 · Product Overview", "01 · Global Dashboard", "02 · Event Explorer", "03 · Country & Industry Impact", "04 · Shock Simulator", "05 · Company Calculator & Reports", "06 · Evidence & Market Reaction"], label_visibility="collapsed", key="scope_page")
    st.markdown("---")
    st.markdown("**ACTIVE ANALYSIS CASE**")
    shared_select("International event", "event", "scope_sidebar_event")
    shared_select("Economy", "country", "scope_sidebar_country")
    shared_select("Industry", "industry", "scope_sidebar_industry")
    st.button("Reset case", on_click=reset_case, key="scope_reset_case")
    st.caption("Selections follow you between modules. Financial inputs are separate and may reset when navigating; export results before leaving a calculator.")
    st.markdown("---")
    st.caption("BUILD 0.8 · LOCAL DATA MODE")
    st.caption("Historical reference data only. No live market feed is connected.")

if page.startswith("00"):
    render_overview()
elif page.startswith("01"):
    render_dashboard()
elif page.startswith("02"):
    render_event_explorer()
elif page.startswith("03"):
    render_impact_analyzer()
elif page.startswith("04"):
    render_shock_simulator()
elif page.startswith("05"):
    render_company_calculator()
else:
    render_evidence_desk()
