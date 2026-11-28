"""Module 4: economic scenario sandbox with editable assumptions and audit trail."""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from modules.shock_math import calculate_channel, basket_effect
from modules.case_context import shared_select
from modules.visual_intelligence import render_scenario_comparison

DATA = Path(__file__).resolve().parents[1] / 'data'
COUNTRIES = {'India': ('INR',85.0), 'China': ('CNY',7.0), 'USA': ('USD',1.0),
             'Japan': ('JPY',150.0), 'Germany': ('EUR',0.9), 'Australia': ('AUD',1.5)}
PRESETS = {'Strait of Hormuz disruption': (25,0,0), 'Red Sea shipping crisis': (0,50,0),
           'Russia–Ukraine war': (15,0,30), 'Custom / combined shock': (0,0,0)}
CHANNELS = [('Crude oil','barrels',100000,80.0),('Separate ocean freight','TEU',1000,2000.0),
            ('Wheat','metric tonnes',10000,250.0)]


def money(value, currency):
    return f'{currency} {value:,.2f}'


def compact_money(value, currency):
    if currency == "INR" and abs(value) >= 1e7:
        return f"₹{value/1e7:,.2f} Cr"
    if currency == "INR" and abs(value) >= 1e5:
        return f"₹{value/1e5:,.2f} L"
    for scale, suffix in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(value) >= scale:
            return f"{currency} {value/scale:,.2f}{suffix}"
    return money(value, currency)


def chart_style(fig):
    fig.update_layout(template='plotly_white',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#ffffff',
                      font=dict(color='#203a40'),height=370,margin=dict(l=15,r=15,t=25,b=50),
                      legend=dict(orientation='h',y=1.12),bargap=.27)
    fig.update_yaxes(gridcolor='#dce6e3',zerolinecolor='#748f89',automargin=True)
    fig.update_xaxes(automargin=True)
    return fig


def make_charts(rows, currency):
    names=rows['channel'].tolist()
    fig=go.Figure()
    for col,label,color in [('baseline_local','Baseline','#087668'),('scenario_local','Scenario','#b96517')]:
        fig.add_bar(x=names,y=rows[col],name=label,marker_color=color,hovertemplate='%{x}<br>'+currency+' %{y:,.2f}<extra>%{fullData.name}</extra>')
    fig.update_layout(barmode='group',yaxis_title=f'Cost ({currency})')
    waterfall=go.Figure(go.Waterfall(x=['Baseline','Price / freight change','FX change','Scenario'],
        measure=['absolute','relative','relative','total'],
        y=[rows.baseline_local.sum(),rows.price_effect_local.sum(),rows.fx_effect_local.sum(),0],
        increasing=dict(marker=dict(color='#e58e88')),decreasing=dict(marker=dict(color='#82c8b6')),
        totals=dict(marker=dict(color='#4275a8')),connector=dict(line=dict(color='#71849c')),
        hovertemplate=currency+' %{y:,.2f}<extra></extra>'))
    waterfall.update_layout(yaxis_title=f'Cost ({currency})',showlegend=False)
    return chart_style(fig),chart_style(waterfall)


def render_shock_simulator():
    st.markdown('<div class="scope-hero"><div class="scope-eyebrow">04 / SCENARIO INTELLIGENCE</div><div class="scope-title">Economic Shock Simulator</div><div class="scope-subtitle">Stress-test import costs under commodity, shipping and currency shocks.</div></div>',unsafe_allow_html=True)
    st.warning('Hypothetical scenario only. Every default price, quantity, exchange rate and shock below is illustrative, not current market data, an official country statistic or a forecast.')
    a,b,c=st.columns(3)
    with a:
        event=shared_select('Scenario event', 'event', 'sim_event')
    with b:
        country=shared_select('Economy / reporting currency', 'country', 'sim_country')
    if st.checkbox('Use custom combined shock instead of event preset',key='sim_custom'):
        event='Custom / combined shock'
    period=c.selectbox('Quantity period',['One month','One quarter','One year','Custom period'],key='sim_period')
    currency,default_fx=COUNTRIES[country]
    st.caption('Country selection changes the reporting currency and historical context. Quantities are a user-defined import basket, not national totals. Changing the period changes the label only; enter quantities for that period.')
    if event != 'Custom / combined shock':
        exposure=pd.read_csv(DATA/'country_exposure.csv')
        match=exposure[(exposure.event==event)&(exposure.country==country)]
        if not match.empty:
            r=match.iloc[0]
            with st.expander(f'{country} — qualitative event context: {r["level"]}'):
                st.write(r['rationale'])
                st.caption('Inherited screening assessment; not used as a numerical multiplier.')
    st.subheader('1. Define your baseline and price shocks')
    st.caption('Enter commodity purchase prices excluding the separately entered freight charge. Set unused quantities to zero to avoid double counting. TEU = twenty-foot equivalent container unit.')
    rows=[]
    inputs=[]
    for i,(name,unit,default_q,default_price) in enumerate(CHANNELS):
        st.markdown(f'**{name}**')
        x,y,z=st.columns(3)
        q=x.number_input(f'Quantity ({unit})',min_value=0,value=default_q,step=100,key=f'sim_qty_{i}')
        price=y.number_input(f'Baseline USD / {unit}',min_value=0.01,value=default_price,step=1.0,key=f'sim_price_{i}')
        change=z.slider(f'{name} price change (%)',-75,200,PRESETS[event][i],5,key=f'sim_shock_{i}_{event}')
        st.caption(f'Scenario unit price: USD {price*(1+change/100):,.2f} per {unit}')
        inputs.append((name,unit,q,price,change))
    st.subheader('2. Exchange-rate assumptions')
    if currency=='USD':
        fx=1.0; fx_change=0
        st.info('USA: USD is the reporting and invoice currency. The exchange-rate multiplier is fixed at 1; FX shock is zero in this model.')
    else:
        x,y=st.columns(2)
        fx=x.number_input(f'Baseline {currency} per USD',min_value=0.0001,value=default_fx,step=0.01,format='%.4f',key=f'sim_fx_{country}')
        fx_change=y.slider('Change in local currency per USD (%)',-50,100,0,1,key=f'sim_fx_change_{country}')
    st.caption(f'Scenario rate: {fx*(1+fx_change/100):,.4f} {currency} per USD. A positive FX change represents local currency depreciation (more local currency per USD).')
    for name,unit,q,price,change in inputs:
        rows.append({'channel':name,'unit':unit,**calculate_channel(q,price,change,fx,fx_change)})
    df=pd.DataFrame(rows)
    base=df.baseline_local.sum(); scenario=df.scenario_local.sum(); extra=df.extra_local.sum()
    pct=100*extra/base if base>0 else None
    st.divider(); st.subheader('3. Scenario results')
    a,b,c=st.columns(3)
    a.metric('Baseline import cost',compact_money(base,currency))
    b.metric('Scenario import cost',compact_money(scenario,currency))
    c.metric('Additional cost / (saving)',compact_money(extra,currency),delta=f'{pct:+.2f}%' if pct is not None else None,delta_color='inverse')
    st.write(f'**Full amounts:** {money(base,currency)} → {money(scenario,currency)} | Change: {money(extra,currency)}')
    st.caption(f'{period} • Fixed volumes • Nominal values • Positive additional cost is adverse for an importer, not necessarily for an exporter.')
    a,b=st.columns(2)
    a.metric('Change in USD import bill',compact_money(df.extra_usd.sum(),'USD'))
    b.metric('Currency contribution',compact_money(df.fx_effect_local.sum(),currency))
    st.caption(f'Exact USD change: {money(df.extra_usd.sum(),"USD")} | Exact FX contribution: {money(df.fx_effect_local.sum(),currency)}')
    if base==0:
        st.info('All quantities are zero. Costs are zero and percentage change is undefined. Enter a positive volume to explore the scenario.')
    elif extra>0:
        st.info('For this import basket, the shock raises local-currency expenditure. Higher USD payments could put pressure on the external balance if they represent cross-border purchases and other flows are unchanged. Separately billed freight can be a services import rather than merchandise trade; currency translation alone does not change USD payments. This is not a national trade-balance estimate.')
    elif extra<0:
        st.info('For this import basket, the scenario reduces local-currency expenditure. Actual trade and business outcomes depend on quantities, contracts, demand and other factors.')
    else:
        st.info('No net local-currency cost change under these assumptions. Individual price and currency contributions may offset each other.')
    t1,t2,t3,t4=st.tabs(['Cost breakdown','Illustrative price pass-through','Method & evidence','Scenario comparison & sensitivity'])
    weight=None; pass_through=None; effect=None
    with t1:
        st.markdown('**Baseline versus scenario cost**')
        f1,f2=make_charts(df,currency)
        st.plotly_chart(f1,use_container_width=True,key='sim_comparison')
        st.markdown('**Cost bridge: what caused the change?**')
        st.plotly_chart(f2,use_container_width=True,key='sim_waterfall')
        st.caption('Price/freight effect is calculated at baseline FX; the currency effect uses scenario USD expenditure and therefore includes the interaction. The two effects add to the total change.')
        cols=['channel','quantity','unit','baseline_usd','scenario_usd','price_effect_local','fx_effect_local','extra_local']
        st.dataframe(df[cols].round(2),hide_index=True,use_container_width=True)
    with t2:
        st.markdown('**Optional, illustrative downstream price sensitivity**')
        st.caption('Assume this modeled import basket represents a share of a hypothetical final-price basket. This is not national CPI, an annual inflation rate or a calibrated forecast.')
        a,b=st.columns(2)
        weight=a.slider('Assumed import-cost weight in final basket (%)',0,100,20,5,key='sim_weight')
        pass_through=b.slider('Assumed cost pass-through (%)',0,100,50,5,key='sim_pass')
        if pct is not None:
            effect=basket_effect(pct,weight,pass_through)
            st.metric('Illustrative one-time basket price change',f'{effect:+.2f}%')
            st.write(f'{pct:+.2f}% × {weight/100:.2f} × {pass_through/100:.2f} = {effect:+.2f}%')
        else:
            st.info('Price sensitivity is undefined when the baseline import basket has zero cost.')
        st.caption('Other basket costs are assumed unchanged. No demand response, timing, taxes, subsidies, monetary policy or second-round effects are modeled.')
    with t3:
        st.markdown('**Calculation rules**')
        st.code('Scenario price = Base USD price × (1 + price shock / 100)\nScenario FX = Base FX × (1 + FX shock / 100)\nBaseline local cost = Quantity × Base USD price × Base FX\nScenario local cost = Quantity × Scenario USD price × Scenario FX\nAdditional cost = Scenario local cost − Baseline local cost',language=None)
        st.markdown('**Evidence for the event mechanisms (not for the numerical assumptions)**')
        highlights=pd.read_csv(DATA/'event_highlights.csv')
        for r in highlights.itertuples():
            st.markdown(f'- [{r.source_name} — {r.source_title}]({r.source_url}) · {r.period} · {r.classification}')
        st.caption('The event presets are manually chosen examples, not historical price changes. We do not estimate GDP, actual national CPI, exchange-rate forecasts, or a whole-economy trade balance.')
    with t4:
        render_scenario_comparison(inputs,fx,currency,event,period)
    export=df.assign(event=event,country=country,period=period,reporting_currency=currency,
        scenario_type='Hypothetical fixed-volume scenario',basket_weight_pct=weight,pass_through_pct=pass_through,
        illustrative_basket_price_change_pct=effect)
    st.download_button('Download scenario inputs and results (CSV)',export.to_csv(index=False).encode('utf-8-sig'),
                       file_name='shockscope_scenario.csv',mime='text/csv',key='sim_export')
    st.caption('SHOCKSCOPE · Academic startup prototype · Transparent scenario accounting · Not investment advice')
