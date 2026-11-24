SHOCKSCOPE | Module 4 | Build 0.4

Stop Streamlit (Ctrl+C), extract ZIP, and copy app.py, modules/ and this README into the existing SHOCKSCOPE folder. Merge folders, replace app.py only. Retain previous data and modules. Run python -m streamlit run app.py from the project folder. No new packages.

Select 04 · Shock Simulator. Choose a country and event, adjust price shocks and exchange rate, inspect results and download CSV. All defaults are illustrative, not national import volumes or market quotes. Prices exclude separate freight, quantities are for the chosen period. Switching event initializes the associated example shock sliders; currency and quantity controls are independent.

Manual check: select India, Hormuz; oil 100000 barrels at USD 80, +25%; freight and wheat quantities zero; FX INR 85/USD, change 0%. Baseline INR 680,000,000; scenario INR 850,000,000; extra INR 170,000,000. Change FX to +10%: scenario INR 935,000,000; extra INR 255,000,000; price effect INR 170,000,000; FX effect INR 85,000,000. Set all shocks to zero: extra cost zero. USA locks FX to 1. Zero quantities: no percentage. No browser testing in build environment; test locally.
