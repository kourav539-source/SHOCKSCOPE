from pathlib import Path
import json
import streamlit as st
import pandas as pd
from modules.case_context import shared_select
from modules.visual_intelligence import render_transmission

DATA = Path(__file__).resolve().parents[1] / 'data'

def render_event_explorer():
    events = json.loads((DATA / 'events.json').read_text(encoding='utf-8'))
    facts = pd.read_csv(DATA / 'event_highlights.csv')
    exposure = pd.read_csv(DATA / 'country_exposure.csv')
    st.markdown('<div class="scope-hero"><div class="scope-eyebrow">02 / EVENT INTELLIGENCE</div><div class="scope-title">Event Explorer</div><div class="scope-subtitle">Trace geopolitical events into economic and business consequences.</div></div>', unsafe_allow_html=True)
    name = shared_select('Select an international event', 'event', 'explorer_event')
    e = events[name]
    f = facts.loc[facts.event == name].iloc[0]
    st.caption('Historical case study • Evidence through first half of 2025 at latest • Not a live status report')
    a,b = st.columns([1,2])
    with a:
        st.metric(f.headline, f.display_value)
        st.caption(f.period + ' | ' + f.classification)
    with b:
        st.subheader('Background')
        st.write(e['background'])
        st.write(f.context)
        st.markdown(f'[{f.source_name} — {f.source_title}]({f.source_url})')
    t1,t2,t3,t4 = st.tabs(['Timeline','Economic transmission','Countries & industries','Evidence & limitations'])
    with t1:
        st.subheader('Historical milestones')
        for date, description in e['timeline']:
            st.markdown(f'**{date}** — {description}')
        st.markdown(f"[Historical reference]({e['url']})")
    with t2:
        st.subheader('How the shock travels')
        st.caption('Illustrative causal pathway; effects are conditional, not forecasts.')
        render_transmission(name,e)
        with st.expander("Read the pathway as text"):
            for i, step in enumerate(e['chain'],1):
                st.write(f'{i:02d} | {step}')
        st.subheader('Potential macroeconomic consequences')
        for item in e['macro']:
            st.markdown('- ' + item)
    with t3:
        st.subheader('Country exposure')
        st.caption('Qualitative prototype assessments, not measured losses.')
        selected = st.multiselect('Economies', sorted(exposure.country.unique()), default=sorted(exposure.country.unique()))
        rows = exposure[(exposure.event == name) & exposure.country.isin(selected)]
        for row in rows.itertuples():
            with st.expander(f'{row.country} — {row.level} sensitivity'):
                st.write(row.rationale)
        st.subheader('Industry transmission channels')
        st.table(pd.DataFrame(e['industries'], columns=['Industry','Potential effect']))
    with t4:
        st.markdown(f'[{f.source_title}]({f.source_url})')
        st.markdown(f"[Additional historical reference]({e['url']})")
        st.write('The headline is a dated historical reference. The timeline is selective. Country labels and causal pathways are analytical interpretations, not official ratings or causal estimates. No current market feed is connected.')
