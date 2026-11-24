SHOCKSCOPE - Prototype 0.1

WHAT IS INCLUDED
- app.py: Streamlit application entry point
- modules/dashboard.py: Global Dashboard module
- data/event_highlights.csv: Source-backed historical event facts
- data/global_indicators.csv: Historical oil-flow time series
- data/country_exposure.csv: Clearly labelled qualitative exposure assumptions
- requirements.txt: Python packages used by this prototype

RUN ON WINDOWS
1. Open this folder in Visual Studio Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   py -m venv .venv
4. Activate it in PowerShell:
   .\.venv\Scripts\Activate.ps1
5. Install packages:
   python -m pip install -r requirements.txt
6. Start the application:
   python -m streamlit run app.py

If PowerShell blocks activation, use Command Prompt instead:
   .venv\Scripts\activate.bat

DATA NOTES
- The EIA time series are historical observed oil-flow estimates (2020 to first half of 2025).
- The UNCTAD Suez Canal transit figure is a historical June 2024 comparison against mid-December 2023.
- The World Bank wheat figure is a forecast published in April 2022, not the final realized price change.
- Country exposure labels are qualitative prototype assumptions, not official risk scores or forecasts.
