"""Fixed-volume, deterministic scenario accounting. No fitted coefficients."""
import math


def calculate_channel(quantity, base_price, price_change_pct, base_fx, fx_change_pct):
    """FX is local currency per USD; positive change means local depreciation."""
    vals = (quantity, base_price, price_change_pct, base_fx, fx_change_pct)
    if not all(math.isfinite(v) for v in vals):
        raise ValueError('Inputs must be finite.')
    if quantity < 0 or base_price <= 0 or base_fx <= 0 or price_change_pct <= -100 or fx_change_pct <= -100:
        raise ValueError('Quantity must be nonnegative; prices and FX must remain positive.')
    new_price = base_price * (1 + price_change_pct / 100)
    new_fx = base_fx * (1 + fx_change_pct / 100)
    base_usd = quantity * base_price
    shock_usd = quantity * new_price
    base_local = base_usd * base_fx
    shock_local = shock_usd * new_fx
    price_effect = (shock_usd - base_usd) * base_fx
    fx_effect = shock_usd * (new_fx - base_fx)
    return dict(quantity=quantity, base_price_usd=base_price, price_change_pct=price_change_pct,
                scenario_price_usd=new_price, baseline_fx=base_fx, scenario_fx=new_fx,
                fx_change_pct=fx_change_pct, baseline_usd=base_usd, scenario_usd=shock_usd,
                extra_usd=shock_usd-base_usd, baseline_local=base_local, scenario_local=shock_local,
                price_effect_local=price_effect, fx_effect_local=fx_effect,
                extra_local=shock_local-base_local)


def basket_effect(cost_change_pct, basket_weight_pct, pass_through_pct):
    """Illustrative one-time basket price change; not an estimate of national CPI."""
    if not 0 <= basket_weight_pct <= 100 or not 0 <= pass_through_pct <= 100:
        raise ValueError('Weight and pass-through must be between zero and 100.')
    return cost_change_pct * basket_weight_pct / 100 * pass_through_pct / 100
