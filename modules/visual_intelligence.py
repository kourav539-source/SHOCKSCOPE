"""Streamlit visual enhancements for the existing five modules."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from modules.case_context import get_case, shared_select
from modules.visual_charts import exposure_map, transmission, scenario_chart, sensitivity_chart
from modules.visual_math import compare, sensitivity

DATA=Path(__file__).resolve().parents[1]/'data'

@st.cache_data
def load_outlines():
    return json.loads((DATA/'world_outlines.json').read_text(encoding='utf-8'))


def render_map(exposure):
    st.markdown('<div class="section-kicker">03 / Geographic intelligence</div>',unsafe_allow_html=True)
    st.subheader('Global exposure map')
    event=shared_select('Map event','event','visual_map_event')
    country=get_case('country')
    rows=exposure.loc[exposure.event==event].to_dict('records')
    st.caption('Hover over the six country markers for the exposure rationale. The active economy has a larger marker. Drag to pan; use the Plotly controls to zoom or reset.')
    st.plotly_chart(exposure_map(load_outlines(),rows,country),use_container_width=True,theme=None,key='visual_map')
    st.caption('Colors represent inherited qualitative analyst labels, not measured losses or probabilities. Gray means not assessed. Map: simplified Natural Earth low-resolution geometry; boundaries are illustrative, not a statement of territorial claims.')
    st.markdown('[Map source and terms](https://www.naturalearthdata.com/about/terms-of-use/)')


def render_transmission(event, evidence):
    industry=shared_select('Industry pathway','industry','visual_transmission_industry')
    df=pd.read_csv(DATA/'industry_channels.csv')
    row=df[(df.event==event)&(df.industry==industry)].iloc[0]
    st.plotly_chart(transmission(evidence['chain'],evidence['macro'],industry,row.channel,row.risk),use_container_width=True,theme=None,key='visual_transmission')
    st.caption('Conceptual pathway only. Every link has an arbitrary equal unit width; widths are not economic flows, probabilities or estimated effect sizes. The industry branch illustrates a conditional mechanism.')
    st.write('**Industry channel:** '+row.channel+' — '+row.risk)


def render_scenario_comparison(inputs, fx, currency, event, period):
    st.subheader('Compare three levels of stress')
    st.caption(f'{period} | {currency} | Same editable baseline prices and volumes as above. Presets below are independent of the main scenario sliders; all shock sizes are illustrative, not observed market changes or probabilities.')
    rows=compare(inputs,fx,currency,event)
    df=pd.DataFrame(rows)
    baseline_fields={'baseline_fx_local_per_usd':fx}
    for prefix,(_,unit,q,price,_) in zip(('oil','freight','wheat'),inputs):
        baseline_fields.update({prefix+'_quantity':q,prefix+'_unit':unit,prefix+'_baseline_usd_per_unit':price})
    st.dataframe(df[['Scenario','Oil shock (%)','Freight shock (%)','Wheat shock (%)','FX shock (%)']],hide_index=True,use_container_width=True)
    st.plotly_chart(scenario_chart(rows,currency),use_container_width=True,theme=None,key='visual_scenarios')
    display=df[['Scenario','Baseline','Scenario cost','Additional cost','Change (%)']].copy()
    for col in ['Baseline','Scenario cost','Additional cost']:
        display[col]=display[col].map(lambda x:f'{currency} {x:,.2f}')
    display['Change (%)']=display['Change (%)'].map(lambda x:f'{x:+.2f}%' if pd.notna(x) else 'Undefined')
    st.dataframe(display,hide_index=True,use_container_width=True)
    st.download_button('Download scenario comparison (CSV)',df.assign(event=event,currency=currency,period=period,classification='Hypothetical preset',**baseline_fields).to_csv(index=False).encode('utf-8-sig'),file_name='shockscope_scenario_comparison.csv',mime='text/csv',key='visual_compare_export')
    st.divider()
    st.subheader('Which input matters most for this basket?')
    stress=st.slider('One-at-a-time increase from baseline (%)',1,50,10,1,key='visual_stress')
    sr=sensitivity(inputs,fx,currency,stress)
    st.plotly_chart(sensitivity_chart(sr,currency),use_container_width=True,theme=None,key='visual_sensitivity')
    st.caption('Each bar changes just one input by the same percentage, holding every other price and exchange rate at baseline. FX affects the entire USD basket; a commodity price affects only its own line. These are not additive combined-shock contributions. No FX stress for USD reporting.')
    st.download_button('Download sensitivity analysis (CSV)',pd.DataFrame(sr).assign(stress_pct=stress,event=event,currency=currency,period=period,classification='Hypothetical one-at-a-time sensitivity',**baseline_fields).to_csv(index=False).encode('utf-8-sig'),file_name='shockscope_sensitivity.csv',mime='text/csv',key='visual_sensitivity_export')


def render_overview():
    st.markdown('''<div class="scope-hero"><div class="scope-eyebrow">SHOCKSCOPE / Product overview · v0.8</div><div class="scope-title">From global disruption to financial decisions.</div><div class="scope-subtitle">Understand economic exposure, stress-test costs and translate international events into business-level financial intelligence.</div></div>''',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    a.metric('Historical cases','3'); b.metric('Economies','6'); c.metric('Industries','6'); d.metric('Analytical modules','6')
    st.button('Open Global Dashboard',key='overview_launch',on_click=lambda:st.session_state.update({'scope_page':'01 · Global Dashboard'}))
    st.divider()
    a,b=st.columns(2)
    with a:
        st.subheader('The problem')
        st.write('Geopolitical news, macroeconomic data and company financials are often analyzed separately. Users need a clear way to connect a shock to the costs and decisions that matter.')
    with b:
        st.subheader('Our solution')
        st.write('A single analytical workflow: evidence → exposure → scenarios → company profitability → explainable reports. Historical facts, analyst assessments and hypothetical calculations are explicitly separated.')
    st.subheader('Explore the platform')
    for name,body in [('01 · Global Dashboard','Historical event indicators and geographic exposure.'),('02 · Event Explorer','Background, timeline and economic transmission.'),('03 · Country & Industry Impact','Compare six economies and six industries.'),('04 · Shock Simulator','Stress-test import costs, compare scenarios and isolate sensitivities.'),('05 · Company Calculator & Reports','Estimate EBITDA and export rule-based impact reports.'),('06 · Evidence & Market Reaction','Trace a case to its source and compare asset and benchmark returns.')]:
        a,b=st.columns([2,3]); a.button(name,key='overview_'+name[:2],on_click=lambda page=name:st.session_state.update({'scope_page':page})); b.write(body)
    st.divider()
    st.subheader('Who could use SHOCKSCOPE?')
    a,b,c=st.columns(3)
    a.markdown('**Corporate finance & treasury**\n\nCost stress testing and scenario planning.')
    b.markdown('**Supply chain & procurement**\n\nIdentify exposure channels and review sourcing risk.')
    c.markdown('**Research & education**\n\nExplain global events using evidence and transparent calculations.')
    st.caption('Proposed customer segments, not validated market demand. Academic prototype; historical local datasets; no live feeds, probabilistic forecasting, generative AI or investment advice.')
