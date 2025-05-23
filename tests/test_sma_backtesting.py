import unittest
from sma_backtesting.sma_backtesting import backtest

class TestSMABacktest(unittest.TestCase):
    def test_backtest_returns_dataframe(self):
        results, *_ = backtest(
            ticker='AAPL',
            start_date='2024-01-01',
            end_date='2025-01-01',
            strategy='SMA',
            sma_short=20,
            sma_long=50,
            plot=False
        )
        self.assertFalse(results.empty)
        self.assertIn("Buy Date", results.columns)
        self.assertIn("Sell Date", results.columns)
        self.assertIn("Profit", results.columns)

if __name__ == "__main__":
    unittest.main()