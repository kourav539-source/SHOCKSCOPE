"""Compare two price series over the same observed dates."""
import pandas as pd
import numpy as np


def read_prices(file):
    prices = pd.read_csv(file, usecols=['date', 'asset_close', 'benchmark_close'])
    if len(prices) < 2:
        raise ValueError('Include at least two common trading dates.')
    dates = prices['date'].astype(str)
    if not dates.str.fullmatch(r'\d{4}-\d{2}-\d{2}').all():
        raise ValueError('Use YYYY-MM-DD for every date.')
    prices['date'] = pd.to_datetime(dates, format='%Y-%m-%d', errors='raise')
    if prices.date.duplicated().any():
        raise ValueError('Each trading date must appear once.')
    for col in ['asset_close', 'benchmark_close']:
        values = pd.to_numeric(prices[col], errors='raise')
        if not (np.isfinite(values) & values.gt(0)).all():
            raise ValueError('Provide a positive, finite close for both series on every row.')
        prices[col] = values
    return prices.sort_values('date').set_index('date')


def compare_window(prices, event_date, sessions):
    day = pd.Timestamp(event_date)
    before = prices.loc[prices.index < day].tail(1)
    after = prices.loc[prices.index >= day].head(sessions)
    if before.empty or len(after) < sessions:
        raise ValueError('Include a close before the event and enough common trading dates on or after it.')
    window = pd.concat([before, after])
    returns = (window / window.iloc[0] - 1) * 100
    returns.columns = ['Asset return (%)', 'Benchmark return (%)']
    returns['Difference (pp)'] = returns.iloc[:, 0] - returns.iloc[:, 1]
    return returns
