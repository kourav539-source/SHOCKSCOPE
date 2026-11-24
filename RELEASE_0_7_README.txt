SHOCKSCOPE 0.7 — ADVANCED VISUAL INTELLIGENCE

Install: Stop Streamlit (Ctrl+C), back up your existing folder, extract the ZIP,
copy its CONTENTS into the existing SHOCKSCOPE folder (replace matching files).
Retain .venv and any personal dataset changes separately. This is a full release.
No extra Python packages. From your project terminal:
  python -m unittest -v test_company_math test_release test_visual
  python -m streamlit run app.py
If Python environment is not activated, on Windows you can instead run:
  .\.venv\Scripts\python.exe -m unittest -v test_company_math test_release test_visual
  .\.venv\Scripts\python.exe -m streamlit run app.py
Expected automated tests: 19 passing. Actual Streamlit browser testing is pending.

New features:
00 Product Overview: landing page and buttons for all five original modules.
01 Global Dashboard: offline world map, active case event selector, hover labels.
02 Event Explorer: Economic transmission tab, interactive conceptual Sankey,
   industry-specific branch, original text steps retained in expander.
04 Shock Simulator: Scenario comparison & sensitivity tab, with CSV exports.
   Presets use your edited baseline quantity, unit price, reporting currency and
   FX, but ignore current main scenario shock sliders intentionally.
   Mild/moderate/severe FX shocks are 0/5/10% except USD (all zero).
   Other shock assumptions are displayed in the table; not calibrated forecasts.
   Sensitivity changes one input at a time from baseline by the same chosen %.
   Zero quantities produce zero costs and undefined % change.
   No national GDP, CPI or trade-balance estimates are produced.

Manual test: select India, Hormuz, and default quantities/prices (100000 oil at
80 USD, 1000 TEU at 2000 USD, 10000 tonnes wheat at 250 USD), baseline FX 85.
Moderate scenario (+25% oil, +5% FX): baseline INR 1,062,500,000; scenario
INR 1,294,125,000; additional INR 231,625,000 (+21.8%).
One-at-a-time 10% sensitivity: oil INR 68,000,000; freight INR 17,000,000;
wheat INR 21,250,000; FX INR 106,250,000.

Map: bundled Natural Earth low-resolution geometry derived from the pyogrio
naturalearth_lowres fixture, simplified to exterior outlines, omits Antarctica.
No map tiles or API. Source https://www.naturalearthdata.com/about/terms-of-use/
Natural Earth is public domain. Boundaries are illustrative, not a statement
of territorial claims. Only geometries are included, no economic attributes.

Existing historical datasets are unchanged. All quantitative scenario presets
and qualitative exposure labels are explicitly assumptions, not official data.
