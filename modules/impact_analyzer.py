"""Module 3: compare historical macro context and qualitative transmission channels."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modules.case_context import shared_select

DATA = Path(__file__).resolve().parents[1] / 'data'
COUNTRIES = ['India', 'China', 'USA', 'Japan', 'Germany', 'Australia']
INDUSTRIES = ['Energy', 'Aviation', 'Manufacturing', 'Agriculture', 'Logistics', 'Chemicals']
COLORS = {'Lower': '#82c8b6', 'Moderate': '#edc16b', 'Higher': '#e58e88'}
PALETTE = ['#79d6ca', '#f2b65f', '#92b6f5', '#b29ae8', '#f0908c', '#b6d68b']


def load_data():
    exposure = pd.read_csv(DATA / 'country_exposure.csv')
    sectors = pd.read_csv(DATA / 'industry_channels.csv')
    local = pd.read_csv(DATA / 'country_sector_context.csv')
    macro = pd.read_csv(DATA / 'macro_history.csv')
    events = json.loads((DATA / 'events.json').read_text(encoding='utf-8'))
    return exposure, sectors, local, macro, events


def theme(fig, height=390):
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='#111f30', font=dict(color='#e5eefb'), height=height,
                      margin=dict(l=25, r=25, t=30, b=45),
                      legend=dict(orientation='h', yanchor='top', y=-0.18, x=0),
                      hoverlabel=dict(bgcolor='#172b42', font_color='#ffffff'))
    fig.update_xaxes(gridcolor='#293a4c', automargin=True)
    fig.update_yaxes(gridcolor='#293a4c', automargin=True)
    return fig


def make_combinations(exposure, sectors, local):
    c = exposure.rename(columns={'level':'country_sensitivity','score':'country_score',
                                 'rationale':'country_rationale','classification':'country_classification'})
    s = sectors.rename(columns={'sensitivity':'industry_sensitivity','score':'industry_score'})
    out = c.merge(s, on='event', validate='many_to_many').merge(local, on=['country','industry'], validate='many_to_one')
    out['assessment_type'] = 'Qualitative prototype analysis; not measured or forecast loss'
    return out


def sensitivity_chart(rows, name_col, level_col, score_col):
    fig = px.bar(rows, x=score_col, y=name_col, color=level_col, text=level_col,
                 orientation='h', color_discrete_map=COLORS,
                 category_orders={level_col:['Lower','Moderate','Higher']})
    fig.update_traces(textposition='inside', textfont_color='#0b1422', hovertemplate='%{y}<br>Ordinal score: %{x}<extra></extra>')
    fig.update_layout(showlegend=False, yaxis_title=None, xaxis_title='Qualitative sensitivity (ordinal, not a %)',
                      yaxis=dict(autorange='reversed'))
    fig.update_xaxes(range=[0,3.25], tickvals=[1,2,3], ticktext=['1 · Lower','2 · Moderate','3 · Higher'])
    return theme(fig, max(290, 46*len(rows)+115))


def macro_chart(macro, column, ylabel):
    fig = px.line(macro.sort_values('year'), x='year', y=column, color='country', markers=True,
                  color_discrete_sequence=PALETTE, category_orders={'country':COUNTRIES},
                  hover_data={'period_basis':True,'year':True}, labels={column:ylabel,'country':'Economy','year':'WEO year'})
    fig.update_traces(line_width=2.6, marker_size=8)
    fig.update_xaxes(tickmode='array',tickvals=[2021,2022,2023,2024])
    fig.add_hline(y=0,line_color='#607890',line_width=1)
    return theme(fig, 440)


def matrix_chart(rows, event_order):
    z = rows.pivot(index='industry', columns='event', values='score').reindex(index=INDUSTRIES, columns=event_order)
    labels = z.replace({1:'Lower',2:'Moderate',3:'Higher'})
    fig = go.Figure(go.Heatmap(z=z.values, x=z.columns.tolist(), y=z.index.tolist(),
                 text=labels.values, texttemplate='%{text}', textfont=dict(color='#101b28', size=13),
                 zmin=1,zmax=3,colorscale=[[0,COLORS['Lower']],[.2499,COLORS['Lower']],
                 [.25,COLORS['Moderate']],[.7499,COLORS['Moderate']],[.75,COLORS['Higher']],[1,COLORS['Higher']]],
                 showscale=False, hovertemplate='%{y}<br>%{x}<br>%{text}<extra></extra>',xgap=3,ygap=3))
    fig.update_yaxes(autorange='reversed')
    fig.update_xaxes(tickangle=-12)
    return theme(fig,405)


def render_impact_analyzer():
    exposure, sectors, local, macro, events = load_data()
    combined = make_combinations(exposure, sectors, local)
    st.markdown('<div class="scope-hero"><div class="scope-eyebrow">03 / COMPARATIVE INTELLIGENCE</div><div class="scope-title">Country &amp; Industry Impact Analyzer</div><div class="scope-subtitle">Compare economic exposure, trace sector-level risks and explore historical macroeconomic trends.</div></div>', unsafe_allow_html=True)
    event = shared_select('Select international event', 'event', 'impact_event')
    st.caption('Historical case study and qualitative assessment • No live data or causal forecasts')
    erows = exposure[exposure.event == event].copy()
    srows = sectors[sectors.event == event].copy()
    st.markdown(f"**Event evidence:** [Open original reference]({events[event]['url']})")
    a,b,c = st.columns(3)
    a.metric('Economies covered', str(len(erows)))
    b.metric('Industries covered', str(len(srows)))
    c.metric('Country-sector combinations',str(len(combined[combined.event==event])))
    t1,t2,t3,t4 = st.tabs(['Country comparison','Industry analysis','Historical macro data','Detailed assessment'])
    with t1:
        st.subheader('Compare the six economies')
        chosen = st.multiselect('Economies to compare',COUNTRIES,default=COUNTRIES,key='impact_countries')
        if chosen:
            rows=erows[erows.country.isin(chosen)].sort_values(['score','country'],ascending=[False,True])
            st.plotly_chart(sensitivity_chart(rows,'country','level','score'),use_container_width=True,key='country_sensitivity_chart')
            for r in rows.itertuples():
                with st.expander(f'{r.country} — {r.level} sensitivity'):
                    st.write(r.rationale)
            st.download_button('Download country comparison (CSV)',rows.to_csv(index=False).encode('utf-8-sig'), 'shockscope_country_comparison.csv','text/csv',key='country_download')
        else:
            st.info('Select at least one economy to compare.')
        st.caption('Sensitivity is an ordinal analyst label inherited from Module 1: 1 = Lower, 2 = Moderate, 3 = Higher. It does not measure losses or the probability of disruption.')
    with t2:
        st.subheader('Industry sensitivity for the selected event')
        st.plotly_chart(sensitivity_chart(srows.sort_values(['score','industry'],ascending=[False,True]),'industry','sensitivity','score'),use_container_width=True,key='industry_sensitivity_chart')
        st.subheader('Compare industries across all three events')
        st.plotly_chart(matrix_chart(sectors,list(events)),use_container_width=True,key='industry_event_matrix')
        st.caption('Industry scores are analyst-assigned, illustrative screening labels. Higher means a more direct or important potential transmission channel, not a larger measured loss. Moderate means meaningful but more indirect or conditional exposure; Lower means relatively limited direct exposure. No calibration to economic statistics has been performed.')
        for r in srows.itertuples():
            with st.expander(f'{r.industry} — {r.sensitivity} sensitivity'):
                st.markdown(f'**Transmission channel:** {r.channel}')
                st.markdown(f'**Potential risk:** {r.risk}')
                st.markdown(f'**Potential opportunity:** {r.opportunity}')
                st.markdown(f'**Monitor:** {r.monitor}')
        st.download_button('Download industry analysis (CSV)',srows.assign(assessment_type='Qualitative prototype analysis').to_csv(index=False).encode('utf-8-sig'),'shockscope_industry_analysis.csv','text/csv',key='industry_download')
    with t3:
        st.subheader('Historical economic context | 2021–2024')
        st.caption('Source: IMF World Economic Outlook, April 2025 vintage, Tables A2, A4, A6 and A7. Values are published historical data/estimates, not the latest revisions. GDP and annual-average consumer price changes are in percent.')
        chosen_macro=st.multiselect('Choose economies for historical comparison',COUNTRIES,default=COUNTRIES,key='impact_macro_countries')
        if chosen_macro:
            m=macro[macro.country.isin(chosen_macro)].copy()
            st.markdown('**Real GDP growth (%)**')
            st.plotly_chart(macro_chart(m,'real_gdp_growth_pct','Real GDP growth (%)'),use_container_width=True,key='macro_gdp')
            st.markdown('**Consumer price inflation (%)**')
            st.plotly_chart(macro_chart(m,'consumer_price_inflation_pct','Consumer price inflation (%)'),use_container_width=True,key='macro_cpi')
            st.dataframe(m[['country','year','real_gdp_growth_pct','consumer_price_inflation_pct','period_basis']],use_container_width=True,hide_index=True)
            st.download_button('Download IMF historical data (CSV)',m.to_csv(index=False).encode('utf-8-sig'),'shockscope_macro_history.csv','text/csv',key='macro_download')
        else:
            st.info('Select at least one economy to view historical trends.')
        st.warning('Historical GDP and inflation are context only. These values are NOT the isolated impacts of the selected event. Many other forces, including domestic policy, pandemic recovery and demand, affected these indicators. Changing the selected event does not alter historical data.')
        st.caption('India uses fiscal-year reporting (the year label denotes the starting year). Reporting periods and consumer-price methodologies may differ across economies; compare with care.')
        st.markdown(f"[IMF WEO April 2025 — Statistical Appendix]({macro.source_url.iloc[0]})")
    with t4:
        st.subheader('Build a country-sector impact brief')
        l,r=st.columns(2)
        with l:
            country=shared_select('Country', 'country', 'impact_detail_country')
        with r:
            industry=shared_select('Industry', 'industry', 'impact_detail_industry')
        row=combined[(combined.event==event)&(combined.country==country)&(combined.industry==industry)].iloc[0]
        st.markdown(f'### {country} · {industry}')
        a,b=st.columns(2)
        a.metric('Country sensitivity',row.country_sensitivity)
        b.metric('Global industry sensitivity',row.industry_sensitivity)
        st.caption('Separate qualitative labels; no combined score or numerical loss estimate.')
        st.markdown('**Country context**')
        st.write(row.country_rationale)
        st.markdown('**Industry transmission channel**')
        st.write(row.channel)
        st.markdown('**Local business lens — questions to investigate**')
        st.write(row.local_lens)
        a,b=st.columns(2)
        with a:
            st.markdown('**Potential downside**')
            st.write(row.risk)
        with b:
            st.markdown('**Potential opportunity**')
            st.write(row.opportunity)
        st.markdown('**Financial indicators to monitor**')
        st.write(row.monitor)
        st.markdown('**Possible management response**')
        st.write(row.response)
        st.caption('This is a conditional screening brief combining country exposure, global sector mechanisms and a local due-diligence prompt. It is not a verified country-industry loss calculation or individualized business advice.')
        export=combined[(combined.event==event)&(combined.country==country)&(combined.industry==industry)].copy()
        export['event_reference']=events[event]['url']
        export['source_note']='Event reference supports background; ratings and business responses are analyst assumptions.'
        st.download_button('Download selected impact brief (CSV)',export.to_csv(index=False).encode('utf-8-sig'),'shockscope_impact_brief.csv','text/csv',key='detail_download')
    st.markdown('---')
    with st.expander('Methodology and evidence', expanded=False):
        st.write('Country labels use the existing Module 1 assessments. Industry labels use explicit analyst judgments about the directness of the transmission channel. The 108 combinations are produced by matching country-event and industry-event records with country-sector questions. They are not 108 empirical estimates. No scores are added or multiplied.')
        for name,info in events.items():
            st.markdown(f'- [{name}]({info["url"]}) — historical event context')
        st.markdown(f'- [IMF WEO April 2025]({macro.source_url.iloc[0]}) — historical macroeconomic data')
    st.caption('SHOCKSCOPE · Academic startup prototype · Historical data and transparent assumptions')
