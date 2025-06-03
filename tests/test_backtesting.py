import unittest
from backtesting import backtest

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

    def test_backtest_rsi(self):
        results, *_ = backtest(
            ticker='AAPL',
            start_date='2024-01-01',
            end_date='2025-01-01',
            strategy='RSI',
            RSI_lower=30,
            RSI_upper=70,
            plot=False
        )
        self.assertFalse(results.empty)
        self.assertIn("Buy Date", results.columns)
        self.assertIn("Sell Date", results.columns)
        self.assertIn("Profit", results.columns)

    def test_backtest_bollinger(self):
        results, *_ = backtest(
            ticker='AAPL',
            start_date='2024-01-01',
            end_date='2025-01-01',
            strategy='Bollinger',
            bb_window=20,
            bb_std=2,
            plot=False
        )
        self.assertFalse(results.empty)
        self.assertIn("Buy Date", results.columns)
        self.assertIn("Sell Date", results.columns)
        self.assertIn("Profit", results.columns)

    def test_backtest_macd(self):
        results, *_ = backtest(
            ticker='AAPL',
            start_date='2024-01-01',
            end_date='2025-01-01',
            strategy='MACD',
            macd_fast=12,
            macd_slow=26,
            macd_signal=9,
            plot=False
        )
        self.assertFalse(results.empty)
        self.assertIn("Buy Date", results.columns)
        self.assertIn("Sell Date", results.columns)
        self.assertIn("Profit", results.columns)

if __name__ == "__main__":
    unittest.main()