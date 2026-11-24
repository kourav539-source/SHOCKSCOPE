"""Deterministic company EBITDA stress test. All amounts in millions of local currency."""
import math


def calculate_company(revenue, costs, fx_pct, recovery_pct):
    """Costs: rows with category, base, shock_pct, usd_share_pct.
    Apply unit cost shock first, then currency change to unhedged USD share.
    Recover only positive net additional cost via incremental revenue.
    """
    if not all(math.isfinite(x) for x in (revenue, fx_pct, recovery_pct)):
        raise ValueError('Inputs must be finite.')
    if revenue <= 0 or fx_pct <= -100 or not 0 <= recovery_pct <= 100:
        raise ValueError('Revenue must be positive, FX above -100%, recovery 0–100%.')
    rows = []
    for item in costs:
        b, p, u = (item[k] for k in ('base', 'shock_pct', 'usd_share_pct'))
        if not all(math.isfinite(x) for x in (b, p, u)) or b < 0 or p < -100 or not 0 <= u <= 100:
            raise ValueError('Invalid cost, price shock or currency share.')
        price = b * p / 100
        fx = (b + price) * u / 100 * fx_pct / 100
        rows.append({**item, 'price_effect': price, 'fx_effect': fx,
                     'scenario': b + price + fx, 'extra': price + fx})
    base_cost = sum(x['base'] for x in rows)
    scenario_cost = sum(x['scenario'] for x in rows)
    extra = sum(x['extra'] for x in rows)
    recovered = max(extra, 0) * recovery_pct / 100
    scenario_revenue = revenue + recovered
    e0 = revenue - base_cost
    e1 = scenario_revenue - scenario_cost
    m0, m1 = 100 * e0 / revenue, 100 * e1 / scenario_revenue
    return dict(rows=rows, revenue=revenue, scenario_revenue=scenario_revenue,
                base_cost=base_cost, scenario_cost=scenario_cost, extra=extra,
                recovered=recovered, ebitda0=e0, ebitda1=e1, ebitda_change=e1-e0,
                margin0=m0, margin1=m1, margin_change_pp=m1-m0,
                price_effect=sum(x['price_effect'] for x in rows),
                fx_effect=sum(x['fx_effect'] for x in rows))
