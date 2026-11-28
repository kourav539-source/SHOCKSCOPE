SHOCKSCOPE 0.8 | Evidence & Market Reaction
Based on the saved 0.7 release. This ZIP is a full project copy. Start at app.py.
Run locally with python -m pip install -r requirements.txt and python -m streamlit run app.py.
To update an existing deployment, merge the changed files into the deployed branch after comparing local edits.
Changed: app.py and modules/visual_intelligence.py.
Added: modules/evidence_desk.py, modules/market_window.py, test_market_window.py and this note.

Open page 06 from the sidebar or Product Overview. Select an event, economy and industry. The evidence tab combines the original dated source, SHOCKSCOPE exposure assumptions, industry monitoring indicators and a World Monitor reference link appropriate to the case. Download the evidence as text.
Market Reaction opens with a synthetic example. For real data, supply a CSV with date,asset_close,benchmark_close and name the price source and both series. Use aligned closes, consistent currency, comparable dividend treatment, complete common trading dates and the date the news could first affect trading. The module uses the last supplied pre-event close and the selected number of supplied dates on or after the effective date. Missing trading days cannot be inferred from the file. The difference in cumulative returns is expressed in percentage points. Export includes the source, case and window dates.
World Monitor informed the workflow. No World Monitor source code, editorial scores or provider feeds are bundled. External reference links are opened separately. No keys or automatic price downloads are required.
Future candidates: optional dated observations from primary sources with last-success and stale states, multi-event timelines with deduplication, and saved watchlists by exposure channel. Live alerts require a provider, refresh schedule and historical observations against which to check their behavior.
Verification: 16 tests passed across test_release, test_company_math and test_market_window. Python files compiled. UI and legacy visual tests require the Streamlit/Plotly environment. Full test command: python -m unittest discover -v
