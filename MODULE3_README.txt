SHOCKSCOPE | Module 3 update (build 0.3)
======================================
1. Stop Streamlit in the VS Code terminal (Ctrl+C).
2. Extract SHOCKSCOPE_Module3.zip. Copy the extracted app.py, data and modules folders into your existing SHOCKSCOPE project. Replace app.py and merge folders. Keep all existing files, especially .streamlit, .venv, dashboard.py and event_explorer.py.
3. In the existing project terminal, run:
   python -m streamlit run app.py
   If the virtual environment is not active, use this PowerShell command instead:
   .\.venv\Scripts\python.exe -m streamlit run app.py
4. Click 03 - Country & Industry Impact on the sidebar.
5. Test all three event choices, country and industry filters, and CSV downloads. Check Modules 1 and 2 still open.

No extra packages, APIs, databases or network calls are needed to render Module 3. Source hyperlinks require internet access if opened.

DATA NOTES
macro_history.csv: IMF World Economic Outlook April 2025, statistical appendix Tables A2, A4, A6 and A7, annual data 2021–2024 only. The vintage is intentionally frozen and can differ from later revisions. The figures are historical context, not event-attributable outcomes.
industry_channels.csv: analyst-defined conditional sector assessments (18 event/industry combinations). Scores are ordinal labels, not measured statistics.
country_sector_context.csv: 36 country-sector investigation prompts, not measured facts.
The 108 possible combinations are generated from these records and the existing country_exposure.csv; no combined numerical risk or loss is computed.

Validation: Python syntax, input datasets, full 108 unique combinations, missing values, and Plotly chart creation/serialization were tested. Streamlit browser runtime must be checked on the user's computer.
