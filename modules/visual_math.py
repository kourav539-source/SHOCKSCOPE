"""Independent what-if comparisons using the existing fixed-volume engine."""
from modules.shock_math import calculate_channel

PROFILES = {
    'Strait of Hormuz disruption': [(10,0,0),(25,0,0),(50,0,0)],
    'Red Sea shipping crisis': [(0,20,0),(0,50,0),(0,100,0)],
    'Russia–Ukraine war': [(5,0,10),(15,0,30),(30,0,60)],
    'Custom / combined shock': [(10,15,10),(25,50,30),(50,100,60)],
}
LABELS = ('Mild','Moderate','Severe')


def compare(inputs, base_fx, currency, event):
    """inputs: three (name, unit, quantity, base price, current shock) tuples.
    Current shocks deliberately ignored: preset comparisons use baseline only.
    """
    rows=[]
    for label, changes, fx in zip(LABELS, PROFILES[event], (0,5,10)):
        if currency=='USD': fx=0
        parts=[calculate_channel(q,p,s,base_fx,fx) for (_,_,q,p,_),s in zip(inputs,changes)]
        base=sum(r['baseline_local'] for r in parts)
        end=sum(r['scenario_local'] for r in parts)
        delta=end-base
        rows.append({'Scenario':label,'Oil shock (%)':changes[0],'Freight shock (%)':changes[1],
                     'Wheat shock (%)':changes[2],'FX shock (%)':fx,'Baseline':base,
                     'Scenario cost':end,'Additional cost':delta,
                     'Change (%)':100*delta/base if base else None,
                     'Price effect':sum(r['price_effect_local'] for r in parts),
                     'FX effect':sum(r['fx_effect_local'] for r in parts)})
    return rows


def sensitivity(inputs, base_fx, currency, stress):
    """One-at-a-time positive change from the same baseline; no interactions."""
    if stress < 0: raise ValueError('Stress must be nonnegative')
    names=[r[0] for r in inputs]
    rows=[]
    for i,name in enumerate(names + (['USD exchange rate'] if currency!='USD' else [])):
        parts=[calculate_channel(q,p,stress if j==i else 0,base_fx,stress if i==len(names) else 0)
               for j,(_,_,q,p,_) in enumerate(inputs)]
        rows.append({'Input':name,'Additional cost':sum(r['extra_local'] for r in parts)})
    return sorted(rows,key=lambda r:r['Additional cost'])
