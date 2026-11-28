"""Module 5: company stress test and local, deterministic report generation."""
from pathlib import Path
from html import escape
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.company_math import calculate_company
from modules.case_context import shared_select
from modules.report_format import report_html, report_sections

DATA = Path(__file__).resolve().parents[1] / 'data'
COUNTRIES = {'India':'INR','China':'CNY','USA':'USD','Japan':'JPY','Germany':'EUR','Australia':'AUD'}
EVENTS = ['Strait of Hormuz disruption','Red Sea shipping crisis','Russia–Ukraine war']
CATEGORIES = ['Fuel / energy','Freight / logistics','Raw materials','Payroll / other cash costs']
# Fictional baseline expenses per 100 million of revenue; not sector averages.
PROFILES = {'Energy':(25,5,40,10),'Aviation':(30,5,10,40),'Manufacturing':(15,10,35,25),
            'Agriculture':(15,10,25,30),'Logistics':(30,20,5,25),'Chemicals':(20,10,40,15)}
SHOCKS = {EVENTS[0]:(25,0,0,0),EVENTS[1]:(0,50,0,0),EVENTS[2]:(15,0,30,0)}


def money(n, currency):
    if currency == 'INR':
        return f'₹{n/10:,.2f} Cr' if abs(n)>=10 else f'₹{n*10:,.2f} L'
    return f'{currency} {n:,.2f} M'


def build_report(name, country, industry, event, period, currency, result, fx, recovery, source, context, sector, lens):
    r = result
    direction = 'increases' if r['extra']>1e-9 else 'decreases' if r['extra']<-1e-9 else 'does not materially change'
    top = max(r['rows'],key=lambda x: abs(x['extra']))
    out = [f'SHOCKSCOPE | COMPANY IMPACT REPORT', 'RULE-BASED SCENARIO ANALYSIS — NOT AN ACTUAL FORECAST',
           f'Company: {name} | {country} | {industry}', f'Event: {event} | Period: {period}',
           f'All amounts: millions of {currency}.', '', 'EXECUTIVE SUMMARY',
           f'Operating cost {direction} under the chosen assumptions; signed change: {r["extra"]:,.2f} million {currency}.',
           f'EBITDA changes from {r["ebitda0"]:,.2f} to {r["ebitda1"]:,.2f} million {currency} ({r["ebitda_change"]:+,.2f}).',
           f'EBITDA margin moves from {r["margin0"]:.2f}% to {r["margin1"]:.2f}% ({r["margin_change_pp"]:+.2f} percentage points).',
           f'Largest absolute cost movement: {top["category"]}, {top["extra"]:+,.2f} million {currency}.',
           '', 'ASSUMPTIONS AND CALCULATIONS',
           f'Baseline revenue: {r["revenue"]:,.2f}; scenario revenue: {r["scenario_revenue"]:,.2f}.',
           f'Baseline cash operating costs: {r["base_cost"]:,.2f}; scenario costs: {r["scenario_cost"]:,.2f}.',
           f'Local currency per USD change: {fx:+.2f}%; assumed recovery of positive net extra cost: {recovery:.2f}%.',
           f'Price effect: {r["price_effect"]:+,.2f}; FX effect: {r["fx_effect"]:+,.2f}; extra revenue: {r["recovered"]:,.2f}.']
    for row in r['rows']:
        out.append(f'- {row["category"]}: baseline {row["base"]:,.2f}; price shock {row["shock_pct"]:+.2f}%; unhedged USD share {row["usd_share_pct"]:.2f}%; scenario {row["scenario"]:,.2f}; change {row["extra"]:+,.2f}.')
    out += ['', 'COUNTRY AND INDUSTRY CONTEXT (QUALITATIVE, NOT A MODEL INPUT)',context,sector['channel']+': '+sector['risk'],
            'Potential opportunity: '+sector['opportunity'],lens,'','MANAGEMENT ACTIONS',
            '- '+sector['response'], '- Monitor '+sector['monitor']+'.',
            '- Verify actual contract terms, cost categories and currency exposures before acting.']
    if r['ebitda1'] < 0: out.append('- Scenario EBITDA is negative; review liquidity and funding separately (not modeled here).')
    if r['extra'] > 0: out.append('- Test feasible customer price increases and demand sensitivity before assuming cost recovery.')
    if abs(r['fx_effect'])>1e-9: out.append('- Review unhedged currency exposure and the cost of potential hedging.')
    out += ['', 'HISTORICAL EVIDENCE (EVENT CONTEXT ONLY)',f'{source["source_name"]} — {source["source_title"]}',
            f'{source["period"]} | {source["classification"]} | {source["headline"]}: {source["display_value"]}',
            source['context'],source['source_url'],'', 'LIMITATIONS',
            'All financial inputs and presets are hypothetical unless independently supplied and verified by the user. The source supports event context, not these company estimates. Fixed volume; no demand response, capex, depreciation, interest, taxes, working capital, cash flow or valuation modeled. Cost categories must not overlap. No external AI or live market feed is used.']
    return '\n'.join(out)


def style(fig, currency):
    fig.update_layout(template='plotly_white',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#ffffff',font=dict(color='#203a40'),height=380,margin=dict(l=20,r=20,t=35,b=60),yaxis_title=f'Million {currency}',legend=dict(orientation='h',y=1.13))
    fig.update_yaxes(gridcolor='#dce6e3',zerolinecolor='#748f89',automargin=True)
    fig.update_xaxes(automargin=True)
    return fig


def make_charts(r,currency):
    fig=go.Figure()
    for label, vals, color in [('Baseline',[r['revenue'],r['base_cost'],r['ebitda0']],'#087668'),('Scenario',[r['scenario_revenue'],r['scenario_cost'],r['ebitda1']],'#b96517')]:
        fig.add_bar(name=label,x=['Revenue','Cash operating costs','EBITDA'],y=vals,marker_color=color)
    fig.update_layout(barmode='group')
    bridge=go.Figure(go.Waterfall(x=['Baseline EBITDA','Price effect','FX effect','Cost recovery','Scenario EBITDA'],measure=['absolute','relative','relative','relative','total'],y=[r['ebitda0'],-r['price_effect'],-r['fx_effect'],r['recovered'],0],increasing=dict(marker=dict(color='#82c8b6')),decreasing=dict(marker=dict(color='#e58e88')),totals=dict(marker=dict(color='#4275a8')),connector=dict(line=dict(color='#71849c'))))
    return style(fig,currency),style(bridge,currency)


def render_company_calculator():
    st.markdown('<div class="scope-hero"><div class="scope-eyebrow">05 / BUSINESS INTELLIGENCE</div><div class="scope-title">Company Impact Calculator & Reports</div><div class="scope-subtitle">Translate global shocks into operating costs, EBITDA and management actions.</div></div>',unsafe_allow_html=True)
    st.warning('Hypothetical company stress test. Default financials, price changes and USD shares are fictional. Reports use local rules and templates, not a generative AI model.')
    a,b,c=st.columns(3)
    with a:
        event=shared_select('International event', 'event', 'co_event')
    with b:
        country=shared_select('Company economy', 'country', 'co_country')
    with c:
        industry=shared_select('Industry', 'industry', 'co_industry')
    currency=COUNTRIES[country]
    a,b=st.columns(2)
    name=' '.join(a.text_input('Company name (optional)',value='Illustrative company',max_chars=100,key='co_name').split()) or 'Illustrative company'
    period=b.selectbox('Financial period',['One year','One quarter','One month'],key='co_period')
    st.caption(f'Enter all monetary inputs in millions of {currency} for the same period. For INR, 10 million = ₹1 crore. Changing period or country does not convert or annualize inputs. Review all inputs after changing economy, industry or event; defaults are fictional.')
    st.subheader('1. Baseline company financials and cost shocks')
    revenue=st.number_input(f'Baseline revenue (million {currency})',min_value=0.01,value=100.0,step=10.0,key=f'co_rev_{country}')
    st.caption('Enter non-overlapping cash operating costs including COGS, excluding depreciation, amortization, interest and tax. Shocks apply to unit costs at fixed volumes, before FX. USD share means effective unhedged USD-linked share of each category.')
    rows=[]
    for i,cat in enumerate(CATEGORIES):
        st.markdown(f'**{cat}**')
        a,b,c=st.columns(3)
        base=a.number_input(f'Baseline (million {currency})',min_value=0.0,value=float(PROFILES[industry][i]),step=1.0,key=f'co_base_{country}_{industry}_{i}')
        shock=b.number_input('Unit cost change (%)',min_value=-100.0,max_value=500.0,value=float(SHOCKS[event][i]),step=5.0,key=f'co_shock_{event}_{industry}_{i}')
        share=0 if currency=='USD' else c.slider('Unhedged USD share (%)',0,100,0,5,key=f'co_share_{country}_{industry}_{i}')
        if currency=='USD': c.caption('USD reporting: no USD FX shock.')
        rows.append(dict(category=cat,base=base,shock_pct=shock,usd_share_pct=share))
    st.subheader('2. Currency and cost recovery assumptions')
    a,b=st.columns(2)
    fx=0 if currency=='USD' else a.slider('Local currency per USD change (%)',-50,100,0,1,key=f'co_fx_{country}')
    if currency=='USD': a.info('USD reporting currency: FX shock fixed at zero.')
    recovery=b.slider('Recover positive net extra costs through revenue (%)',0,100,0,5,key='co_recovery')
    st.caption('Recovery assumes additional revenue at unchanged sales volume. No automatic revenue reduction when costs fall. Price changes should exclude currency effects already captured here.')
    r=calculate_company(revenue,rows,fx,recovery)
    st.divider(); st.subheader('3. Financial impact')
    a,b,c=st.columns(3)
    a.metric('Baseline cash operating cost',money(r['base_cost'],currency))
    b.metric('Scenario cash operating cost',money(r['scenario_cost'],currency))
    c.metric('Additional cost / (saving)',money(r['extra'],currency))
    a,b,c=st.columns(3)
    a.metric('Baseline EBITDA',money(r['ebitda0'],currency))
    b.metric('Scenario EBITDA',money(r['ebitda1'],currency))
    c.metric('EBITDA change',money(r['ebitda_change'],currency))
    a,b,c=st.columns(3)
    a.metric('Baseline EBITDA margin',f'{r["margin0"]:.2f}%')
    b.metric('Scenario EBITDA margin',f'{r["margin1"]:.2f}%')
    c.metric('Margin change',f'{r["margin_change_pp"]:+.2f} pp')
    st.write(f'**Additional revenue from assumed recovery:** {money(r["recovered"],currency)} | **Scenario revenue:** {money(r["scenario_revenue"],currency)}')
    if r['ebitda1']<0: st.warning('Scenario EBITDA is negative. This is not a liquidity or insolvency prediction.')
    if r['base_cost']>revenue: st.caption('Baseline company is already EBITDA-negative under these inputs.')
    t1,t2,t3=st.tabs(['Financial breakdown','Intelligent report','Method & evidence'])
    source=pd.read_csv(DATA/'event_highlights.csv').set_index('event').loc[event].to_dict()
    exposure=pd.read_csv(DATA/'country_exposure.csv'); e=exposure[(exposure.event==event)&(exposure.country==country)].iloc[0]
    sector_data=pd.read_csv(DATA/'industry_channels.csv'); sector=sector_data[(sector_data.event==event)&(sector_data.industry==industry)].iloc[0].to_dict()
    lens_data=pd.read_csv(DATA/'country_sector_context.csv'); lens=lens_data[(lens_data.country==country)&(lens_data.industry==industry)].iloc[0]['local_lens']
    report=build_report(name,country,industry,event,period,currency,r,fx,recovery,source,f'{country}: {e["level"]} qualitative sensitivity. {e["rationale"]}',sector,lens)
    with t1:
        f1,f2=make_charts(r,currency)
        st.plotly_chart(f1,use_container_width=True,key='co_comparison')
        st.markdown('**EBITDA bridge**')
        st.plotly_chart(f2,use_container_width=True,key='co_bridge')
        st.caption(f'All values in million {currency}; negative EBITDA is permitted. Price and FX effects reconcile to the cost change.')
        st.dataframe(pd.DataFrame(r['rows']).round(4),hide_index=True,use_container_width=True)
        summary={f'company_{k}':v for k,v in r.items() if k!='rows'}
        export=pd.DataFrame(r['rows']).assign(event=event,country=country,industry=industry,period=period,currency=currency,unit='million',fx_pct=fx,recovery_pct=recovery,**summary)
        st.download_button('Download financial analysis (CSV)',export.to_csv(index=False).encode('utf-8-sig'),file_name='shockscope_company_analysis.csv',mime='text/csv')
        st.caption('Company totals are repeated on each cost-category row for context; do not sum the repeated totals.')
    with t2:
        st.caption('Automatically refreshed local report. No external AI or API; historical evidence and hypothetical company outputs are separated.')
        for heading, lines in report_sections(report):
            st.markdown('#### ' + heading)
            for line in lines:
                st.markdown('<p style="overflow-wrap:anywhere; margin-bottom:0.5rem">' + escape(line) + '</p>', unsafe_allow_html=True)
        a,b=st.columns(2)
        a.download_button('Download printable report (HTML)',report_html(report).encode('utf-8'),file_name='shockscope_company_report.html',mime='text/html',key='co_html')
        b.download_button('Download plain text (TXT)',report.encode('utf-8'),file_name='shockscope_company_report.txt',mime='text/plain',key='co_txt')
        st.caption('Open the HTML file in your browser and press Ctrl+P to print or save as PDF.')
        st.markdown(f'Historical context: [{source["source_name"]} — {source["source_title"]}]({source["source_url"]})')
    with t3:
        st.code('Price effect = Baseline cost × unit cost change\nFX effect = (Baseline cost + price effect) × unhedged USD share × FX change\nScenario cost = Baseline cost + price effect + FX effect\nExtra revenue = max(total extra cost, 0) × recovery rate\nEBITDA = Revenue − cash operating costs\nEBITDA margin = EBITDA / revenue × 100',language=None)
        st.caption('Percentage inputs are converted to decimals in formulas. EBITDA is a simplified proxy, not audited company EBITDA. Fixed volumes and other costs; no hedging costs, debt, tax, cash flow, valuation or financial forecasts.')
        st.markdown(f'[{source["source_name"]} — {source["source_title"]}]({source["source_url"]}) · {source["period"]} · {source["classification"]}')
        st.write(source['context'])
        st.caption('Source explains historical event context only. Financial outputs are generated from the assumptions above; country and industry narratives are qualitative screening assessments from Module 3.')
    st.caption('SHOCKSCOPE · Academic startup prototype · Transparent company scenario accounting')
