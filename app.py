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
.stApp {background: #f8faf9; color: #17323a;}
[data-testid="stHeader"] {background: rgba(248,250,249,.94);}
[data-testid="stSidebar"] {background: #fff; border-right: 1px solid #d5e2df;}
.scope-hero {
    padding: clamp(20px,4vw,42px); margin: 4px 0 22px;
    background: linear-gradient(110deg,#e1f2ed,#f5faf8 82%);
    border: 1px solid #c4ded5; border-left: 5px solid #087668; border-radius: 16px;
}
.scope-title {color: #102f36; font-size: clamp(1.65rem,4vw,2.65rem); font-weight: 750; line-height: 1.14; letter-spacing: -.035em; margin-bottom: 10px;}
.scope-subtitle {max-width: 75ch; color: #3e595f; line-height: 1.58;}
.scope-eyebrow,.section-kicker {color: #075e52; font-size: .76rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 8px;}
.small-note,[data-testid="stCaptionContainer"] {color: #52676c;}
[data-testid="stMetric"],[data-testid="stPlotlyChart"],[data-testid="stDataFrame"] {
    background: #fff; border: 1px solid #d2dfdc; border-radius: 12px;
}
[data-testid="stMetric"] {padding: 14px 16px; box-shadow: 0 2px 6px rgba(22,64,52,.04);}
[data-testid="stMetricValue"] {color: #123d38; font-variant-numeric: tabular-nums;}
[data-testid="stPlotlyChart"] {padding: 4px;}
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: .42rem .55rem; border-radius: 8px; margin: .08rem 0; cursor: pointer;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: #dff1eb; color: #064c43; box-shadow: inset 3px 0 #087668;
}
.stApp [role="tab"][aria-selected="true"] {color: #065b50; font-weight: 650;}
.stApp :is(button,a,summary,[role="tab"],input):focus-visible,
[data-testid="stSidebar"] label:has(input:focus-visible) {
    outline: 3px solid #176ab1; outline-offset: 2px;
}
.stApp .stButton button,.stApp .stDownloadButton button {border-radius: 9px;}
@media (hover:hover) {
    [data-testid="stSidebar"] [role="radiogroup"] label:hover,
    .stApp [role="tab"]:hover,.stApp [data-testid="stExpander"] summary:hover {background: #eaf4f0;}
    .stApp .stButton button:hover,.stApp .stDownloadButton button:hover {
        border-color: #087668; box-shadow: 0 3px 10px rgba(9,82,66,.12);
    }
}
@media (prefers-reduced-motion:no-preference) {
    .stApp .stButton button,.stApp .stDownloadButton button,
    [data-testid="stSidebar"] [role="radiogroup"] label {transition: background-color .16s ease, border-color .16s ease, box-shadow .16s ease;}
}
</style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 8px 0 14px 0;">
            <div style="font-size: 1.55rem; font-weight: 800; letter-spacing: 0.04em; color: #17323a;">
                SHOCK<span style="color:#08675f;">SCOPE</span>
            </div>
            <div style="color:#50676c; font-size:0.72rem; letter-spacing:0.13em;">
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
