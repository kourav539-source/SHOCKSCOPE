import unittest
from modules.company_math import calculate_company

class CompanyTests(unittest.TestCase):
    def calc(self, shock=25, fx=0, share=0, recovery=0):
        return calculate_company(100,[dict(category='Fuel',base=30,shock_pct=shock,usd_share_pct=share),dict(category='Other',base=55,shock_pct=0,usd_share_pct=0)],fx,recovery)
    def test_default(self):
        r=self.calc(); self.assertAlmostEqual(r['extra'],7.5); self.assertAlmostEqual(r['ebitda1'],7.5); self.assertAlmostEqual(r['margin_change_pp'],-7.5)
    def test_zero(self):
        r=self.calc(0); self.assertEqual(r['ebitda_change'],0)
    def test_savings(self):
        r=self.calc(-25,recovery=100); self.assertAlmostEqual(r['extra'],-7.5); self.assertEqual(r['recovered'],0)
    def test_fx_and_recovery(self):
        r=self.calc(fx=10,share=50,recovery=40); self.assertAlmostEqual(r['fx_effect'],1.875); self.assertAlmostEqual(r['extra'],9.375); self.assertAlmostEqual(r['ebitda1'],9.375)
    def test_full_recovery(self):
        r=self.calc(recovery=100); self.assertAlmostEqual(r['ebitda1'],r['ebitda0']); self.assertLess(r['margin1'],r['margin0'])
    def test_loss(self): self.assertLess(self.calc(100)['ebitda1'],0)
    def test_invalid(self):
        with self.assertRaises(ValueError): self.calc(fx=-100)
        with self.assertRaises(ValueError): self.calc(share=101)
        with self.assertRaises(ValueError): calculate_company(0,[],0,0)
    def test_reconciliation(self):
        for shock in [-100,-20,0,25,200]:
            for fx in [-50,0,10,100]:
                for recovery in [0,40,100]:
                    r=self.calc(shock,fx,50,recovery)
                    self.assertAlmostEqual(r['extra'],r['price_effect']+r['fx_effect'])
                    self.assertAlmostEqual(r['scenario_cost']-r['base_cost'],r['extra'])
                    self.assertAlmostEqual(r['ebitda1'],r['ebitda0']-r['extra']+r['recovered'])
if __name__=='__main__': unittest.main()
