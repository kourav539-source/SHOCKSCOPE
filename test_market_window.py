import unittest
from io import StringIO
from modules.market_window import read_prices, compare_window


class PriceTests(unittest.TestCase):
    def load(self, rows):
        return read_prices(StringIO('date,asset_close,benchmark_close\n'+rows))

    def test_weekend_alignment_and_percentage_points(self):
        data = self.load('2024-01-09,101,202\n2024-01-05,100,200\n2024-01-08,98,201')
        self.assertAlmostEqual(compare_window(data,'2024-01-06',1).iloc[-1,-1], -2.5)
        self.assertAlmostEqual(compare_window(data,'2024-01-06',2).iloc[-1,-1], 0)

    def test_bad_data(self):
        for row in ['2024-01-05,90,201','2024-01-06,inf,205','2024-01-06,,200','2024-01-06,-1,200']:
            with self.subTest(row=row), self.assertRaises(ValueError):
                self.load('2024-01-05,100,200\n'+row)

    def test_incomplete_window(self):
        prices = self.load('2024-01-05,100,200\n2024-01-08,98,201')
        for day,n in [('2024-01-05',1),('2024-01-08',2)]:
            with self.assertRaises(ValueError):
                compare_window(prices,day,n)
