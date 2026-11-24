"""Local smoke tests: data integrity, scenario math, report safety; no network."""
import csv, json, unittest, math
from pathlib import Path
from itertools import product
from modules.shock_math import calculate_channel, basket_effect
from modules.company_math import calculate_company
from modules.report_format import report_html, report_sections
DATA=Path(__file__).resolve().parent/'data'

def read(name):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    assert rows and all(None not in row and all(v is not None and v.strip() for v in row.values()) for row in rows), name
    return rows

class ReleaseTests(unittest.TestCase):
    def test_data_keys_and_coverage(self):
        events=json.loads((DATA/'events.json').read_text(encoding='utf-8'))
        e=set(events); self.assertEqual(len(e),3)
        c={'India','China','USA','Japan','Germany','Australia'}
        i={'Energy','Aviation','Manufacturing','Agriculture','Logistics','Chemicals'}
        facts=read('event_highlights.csv'); self.assertEqual(len(facts),3); self.assertEqual({r['event'] for r in facts},e)
        self.assertTrue(all(r['source_url'].startswith('https://') for r in facts))
        exp=read('country_exposure.csv'); sec=read('industry_channels.csv'); loc=read('country_sector_context.csv'); macro=read('macro_history.csv'); flows=read('global_indicators.csv')
        self.assertEqual(len(exp),18); self.assertEqual({(r['event'],r['country']) for r in exp},set(product(e,c)))
        self.assertEqual(len(sec),18); self.assertEqual({(r['event'],r['industry']) for r in sec},set(product(e,i)))
        self.assertEqual(len(loc),36); self.assertEqual({(r['country'],r['industry']) for r in loc},set(product(c,i)))
        self.assertEqual(len(macro),24); self.assertEqual({(r['country'],int(r['year'])) for r in macro},set(product(c,range(2021,2025))))
        self.assertEqual(len(flows),18)
        self.assertEqual(len({(r['series'],r['period']) for r in flows}),18)
        self.assertTrue(all(math.isfinite(float(r['value'])) for r in flows))
        self.assertEqual(len(list(product(e,c,i))),108)
    def test_manual_simulator(self):
        r=calculate_channel(100000,80,25,85,10)
        self.assertAlmostEqual(r['baseline_local'],680000000)
        self.assertAlmostEqual(r['scenario_local'],935000000,places=4)
        self.assertAlmostEqual(r['extra_local'],255000000,places=4)
    def test_simulator_reconciliation(self):
        for q,p,fx in product([0,100000],[-75,0,25,200],[-50,0,10,100]):
            r=calculate_channel(q,80,p,85,fx)
            self.assertAlmostEqual(r['extra_local'],r['price_effect_local']+r['fx_effect_local'],places=5)
    def test_basket(self):
        self.assertAlmostEqual(basket_effect(16,20,50),1.6)
    def test_report_escape_and_structure(self):
        raw='SHOCKSCOPE\nCompany: <script>alert(1)</script>\n\nEXECUTIVE SUMMARY\nCost +10\nHISTORICAL EVIDENCE (EVENT CONTEXT ONLY)\nhttps://example.org/report\nLIMITATIONS\nNot a forecast'
        sections=report_sections(raw); self.assertEqual(len(sections),4)
        html=report_html(raw); self.assertIn('&lt;script&gt;',html); self.assertNotIn('<script>',html)
        self.assertIn('href="https://example.org/report"',html); self.assertIn('Not a forecast',html)

if __name__=='__main__': unittest.main()
