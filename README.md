# Simple Moving Average (SMA) Backtesting Module

This Python script performs backtesting on a single-stock trading strategy using **Simple Moving Averages (SMA)**.

## 📈 Strategy

- Buy signal: When short-term SMA crosses above long-term SMA.
- Sell signal: When short-term SMA crosses below long-term SMA.
- Trades are executed on signal days.

## 📊 Features

- Backtests SMA crossover strategy on any stock using `yfinance`.
- Tracks buy/sell dates, prices, and profit per trade.
- Calculates:
  - Total trades
  - Win rate
  - Average profit
  - Cumulative profit
- Optional plots showing:
  - Buy/Sell points
  - SMA lines
  - Cumulative profit over time

## 🛠️ Usage

```python
from backtesting_sma import backtest

results = backtest(
    ticker='AAPL',
    start_date='2024-01-01',
    end_date='2025-01-01',
    strategy='SMA',
    sma_short=20,
    sma_long=50,
    plot=True
)
Returns a DataFrame of trades and basic statistics.

📦 Requirements
yfinance

pandas

matplotlib

Install with:

nginx
Copy
Edit
pip install yfinance pandas matplotlib
📁 Output Sample
Buy Date	Buy Price	Sell Date	Sell Price	Profit	Cumulative_Profit
2024-05-16	178.65	2024-08-19	177.48	-1.17	-1.17
2024-09-23	252.64	2025-02-07	338.59	85.95	84.78