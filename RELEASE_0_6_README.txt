SHOCKSCOPE | Release 0.6 — Integration and presentation polish

INSTALL (existing Windows project)
1. Stop the Streamlit process (Ctrl+C in VS Code terminal).
2. Back up your existing SHOCKSCOPE folder or at least its source and data files.
3. Extract the release ZIP into a temporary folder. Copy its CONTENTS into your existing SHOCKSCOPE project, including .streamlit. Merge folders and replace files. Do not remove .venv. If you customized the CSV files, keep backups and review before replacing them.
4. From the project root in the VS Code terminal, run:
   .\.venv\Scripts\python.exe -m unittest -v test_company_math test_release
   .\.venv\Scripts\python.exe -m streamlit run app.py
   If you already activated your environment, python -m streamlit run app.py also works.
5. Open http://localhost:8501. No new packages are required for an existing working installation.

CHANGES
- Shared event, economy and industry selection in the sidebar. Matching selectors in Modules 2–5 follow the active case. Module 1 remains a global overview, with its own independent event filter. Country/industry multiselects are comparison filters, not the active case.
- Module 4 custom combined scenario remains available as a checkbox. Financial assumptions are independent and may reset when changing pages. Download your results before leaving the calculator. No price-to-business-cost proxy is transferred automatically.
- Module 4 already includes compact money formatting from Module 5; this release keeps it and clarifies external-balance wording.
- Module 5 report is readable in-app and downloadable as printable HTML or TXT. Open the HTML file in your browser and press Ctrl+P, then choose Save as PDF if desired. CSV remains available.
- Updated build labels and caption contrast.

DEMO CHECK
Select Red Sea shipping crisis, Germany, Manufacturing in the sidebar. Visit Event Explorer, then Country & Industry Impact (Detailed assessment), then Shock Simulator, then Company Calculator. Confirm the shared selections. Toggle custom combined scenario on and off in Module 4. Verify the Company Calculator report and download HTML; verify source link and assumptions are included. Reset case returns Hormuz / India / Aviation, not financial inputs.

VALIDATION
13 standard-library unit tests pass, covering dataset shape and keys, financial reconciliations, sample calculations and HTML escaping. Additional checks generated 108 report texts, HTML reports and chart pairs from the actual local datasets, and exercised shared-case callback logic with a simulated state object. Python syntax compilation passed. Streamlit is not installed in the build environment, so real browser interaction remains unverified. This is a historical local-data prototype. No new external source audit, live feeds, forecasts, or AI model were added. Historical values are unchanged from build 0.5; source links and data classifications are retained.
