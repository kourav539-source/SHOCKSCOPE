from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.case_context import get_case
from modules.market_window import compare_window, read_prices

DATA = Path(__file__).resolve().parents[1] / 'data'
EXAMPLE = ('date,asset_close,benchmark_close\n2024-01-05,100,200\n'
           '2024-01-08,98,201\n2024-01-09,99,202\n2024-01-10,101,202\n')
WM = 'https://www.worldmonitor.app/'


def render_evidence_desk():
    event, country, industry = [get_case(key) for key in ('event','country','industry')]
    st.title('Evidence & Market Reaction')
    st.caption(f'{event} · {country} · {industry}')
    evidence, market = st.tabs(['Case evidence', 'Market reaction'])
    with evidence:
        facts = pd.read_csv(DATA / 'event_highlights.csv')
        fact = facts.loc[facts.event == event].iloc[0]
        channels = pd.read_csv(DATA / 'industry_channels.csv')
        channel = channels.loc[(channels.event == event) & (channels.industry == industry)].iloc[0]
        exposures = pd.read_csv(DATA / 'country_exposure.csv')
        exposure = exposures.loc[(exposures.event == event) & (exposures.country == country)].iloc[0]
        st.subheader(fact.headline)
        st.metric(fact.period, fact.display_value)
        st.write(fact.context)
        st.caption(fact.classification)
        st.markdown(f'[{fact.source_name} · {fact.source_title}]({fact.source_url})')
        st.subheader('Exposure and evidence to monitor')
        st.write(f'**{country}** · {exposure.rationale}')
        st.write(f'**{industry}** · {channel.channel}')
        st.write(f'**Watch for** · {channel.monitor}')
        st.caption('Country and industry assessments come from the SHOCKSCOPE case model.')
        reference = WM + ('crises/' if event == 'Russia–Ukraine war' else 'chokepoints/')
        st.markdown(f'[Explore current context on World Monitor]({reference})')
        st.caption('External reference. Check the publication time and original source before comparing it with this historical case.')
        brief = '\n'.join([event, f'{country} | {industry}', str(fact.headline), str(fact.display_value),
                           str(fact.period), str(fact.classification), str(fact.context), str(fact.source_name),
                           str(fact.source_title), str(fact.source_url), 'SHOCKSCOPE case assumptions',
                           str(exposure.rationale), str(channel.channel), 'Monitor: '+str(channel.monitor),
                           'External context: '+reference])
        st.download_button('Download case evidence',brief,file_name='shockscope_case_evidence.txt')
    with market:
        st.write('Compare a company or sector with a benchmark over the same trading dates. The baseline is the last supplied close before the event.')
        mode = st.radio('Price data', ['Worked example (synthetic)', 'Upload historical closes'], horizontal=True)
        demo = mode.startswith('Worked')
        if demo:
            st.caption('Synthetic prices demonstrate the calculation independently of the selected case.')
            prices = read_prices(StringIO(EXAMPLE))
            day, sessions = date(2024,1,8), 3
            source = 'Synthetic worked example'
        else:
            st.download_button('Download example CSV layout',EXAMPLE,file_name='synthetic_price_template.csv')
            st.caption('Use one row per common trading date, comparable adjusted prices and a consistent currency. For after-close announcements, choose the next trading date.')
            file = st.file_uploader('Historical closes CSV', type='csv')
            source = st.text_input('Price source and series names', placeholder='Provider, asset, benchmark, currency')
            if file is None or not source.strip():
                return
            try:
                prices = read_prices(file)
            except (ValueError, UnicodeError, pd.errors.ParserError) as err:
                st.error(str(err))
                return
            day = st.date_input('Effective event date',value=prices.index[1].date(),
                                min_value=prices.index.min().date(),max_value=prices.index.max().date())
            sessions = st.selectbox('Common trading observations after baseline',[1,3,5,10,20])
        try:
            result = compare_window(prices,day,sessions)
        except ValueError as err:
            st.info(str(err))
            return
        a,b,c = st.columns(3)
        for box, label, val, unit in zip([a,b,c],result.columns,result.iloc[-1],['%','%',' pp']):
            box.metric(label,f'{val:+.2f}{unit}')
        st.caption(f'Baseline {result.index[0].date()} · Through {result.index[-1].date()} · {source}')
        st.line_chart(result.iloc[:,:2])
        st.dataframe(result)
        st.write('The difference measures performance relative to the benchmark. Earnings, currency moves and other announcements can affect the same window.')
        export = result.assign(source=source,effective_date=str(day),case='Synthetic example' if demo else event,
                               economy='' if demo else country,industry='' if demo else industry)
        st.download_button('Download comparison CSV',export.to_csv(),file_name='shockscope_market_reaction.csv')
