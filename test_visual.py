import csv,json,unittest
from pathlib import Path
from modules.visual_math import compare,sensitivity,PROFILES
from modules.visual_charts import exposure_map,transmission,scenario_chart,sensitivity_chart,ISO
DATA=Path(__file__).resolve().parent/'data'
INPUTS=[('Crude oil','barrels',100000,80,25),('Separate ocean freight','TEU',1000,2000,0),('Wheat','metric tonnes',10000,250,0)]
class VisualTests(unittest.TestCase):
    def test_scenarios(self):
        for event in PROFILES:
            for currency,fx in [('INR',85),('USD',1),('CNY',7),('JPY',150),('EUR',.9),('AUD',1.5)]:
                rows=compare(INPUTS,fx,currency,event)
                self.assertEqual(len(rows),3)
                self.assertEqual(len(set(r['Baseline'] for r in rows)),1)
                self.assertEqual(sorted(r['Scenario cost'] for r in rows),[r['Scenario cost'] for r in rows])
                for r in rows:
                    self.assertAlmostEqual(r['Additional cost'],r['Price effect']+r['FX effect'],places=4)
                    if currency=='USD': self.assertEqual(r['FX shock (%)'],0)
    def test_manual(self):
        rows=compare(INPUTS,85,'INR','Strait of Hormuz disruption')
        self.assertAlmostEqual(rows[1]['Baseline'],1062500000)
        self.assertAlmostEqual(rows[1]['Scenario cost'],1294125000)
        self.assertAlmostEqual(rows[1]['Additional cost'],231625000)
    def test_sensitivity(self):
        rows={r['Input']:r['Additional cost'] for r in sensitivity(INPUTS,85,'INR',10)}
        for key,val in [('Crude oil',68000000),('Separate ocean freight',17000000),('Wheat',21250000),('USD exchange rate',106250000)]: self.assertAlmostEqual(rows[key],val,places=4)
        self.assertEqual(len(sensitivity(INPUTS,1,'USD',10)),3)
    def test_zero_basket(self):
        inputs=[(n,u,0,p,s) for n,u,q,p,s in INPUTS]
        self.assertTrue(all(r['Change (%)'] is None and r['Additional cost']==0 for r in compare(inputs,85,'INR',next(iter(PROFILES)))))
    def test_map(self):
        shapes=json.loads((DATA/'world_outlines.json').read_text())
        self.assertTrue(set(ISO.values())<={s['iso'] for s in shapes})
        with (DATA/'country_exposure.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
        for event in PROFILES:
            if event.startswith('Custom'): continue
            fig=exposure_map(shapes,[r for r in rows if r['event']==event],'India')
            self.assertEqual(sum(t.mode=='markers+text' for t in fig.data),6)
            fig.to_json()
    def test_transmission_and_charts(self):
        events=json.loads((DATA/'events.json').read_text(encoding='utf-8'))
        with (DATA/'industry_channels.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
        for r in rows:
            e=events[r['event']]; fig=transmission(e['chain'],e['macro'],r['industry'],r['channel'],r['risk']);fig.to_json()
            self.assertEqual(len(fig.data[0].link.source),len(fig.data[0].link.target))
        scenario_chart(compare(INPUTS,85,'INR',next(iter(PROFILES))),'INR').to_json()
        sensitivity_chart(sensitivity(INPUTS,85,'INR',10),'INR').to_json()
if __name__=='__main__': unittest.main()
