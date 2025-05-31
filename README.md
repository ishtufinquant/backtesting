# SMA & MACD Strategy Backtesting with Python | Quantitative Trading Module

This project provides a clean and modular backtesting engine for Simple Moving Average (SMA) crossover and MACD strategies using Python, Pandas, and yFinance. It simulates trades, tracks performance, and visualizes buy/sell points — ideal for traders, analysts, and quant developers.

---

## 📢 What's New

- **2025-06-01:** Added MACD strategy support.
- **2025-06-01:** Improved SMA strategy to ensure price series is always aligned after dropping NA values.

---

## 📈 Strategies Supported

### SMA Crossover
- **Buy signal:** When short-term SMA crosses **above** long-term SMA.
- **Sell signal:** When short-term SMA crosses **below** long-term SMA.
- Trades are executed on signal days.

### MACD
- **Buy signal:** When MACD line crosses **above** the Signal line.
- **Sell signal:** When MACD line crosses **below** the Signal line.
- Trades are executed on signal days.

---

## 📊 Features

- Backtests both SMA crossover and MACD strategies using `yfinance`.
- Tracks:
  - Buy/sell dates and prices
  - Profit per trade
- Calculates:
  - Total trades
  - Win rate
  - Average profit
  - Cumulative profit
- Optional plots showing:
  - Buy/Sell points
  - Indicator lines (SMA or MACD/Signal/Histogram)
  - Cumulative profit over time

---

## 🛠️ Usage

```python
from sma_backtesting.sma_backtesting import backtest

# SMA Example
results = backtest(
    ticker='AAPL',
    start_date='2024-01-01',
    end_date='2025-01-01',
    strategy='SMA',
    sma_short=20,
    sma_long=50,
    plot=True
)

# MACD Example
results = backtest(
    ticker='AAPL',
    start_date='2024-01-01',
    end_date='2025-01-01',
    strategy='MACD',
    macd_fast=12,
    macd_slow=26,
    macd_signal=9,
    plot=True
)
```

---

## 📁 Output Sample

| Buy Date   | Buy Price | Sell Date  | Sell Price | Profit | Cumulative_Profit |
|------------|-----------|------------|------------|--------|-------------------|
| 2024-05-16 | 178.65    | 2024-08-19 | 177.48     | -1.17  | -1.17             |
| 2024-09-23 | 252.64    | 2025-02-07 | 338.59     | 85.95  | 84.78             |

---

## 📝 Notes

- The SMA strategy was updated on 2025-06-01 to fix a potential index misalignment bug.
- You can easily extend this framework to add more strategies or custom indicators.

---

## 📦 Requirements

- Python 3.x
- pandas
- yfinance
- matplotlib

Install requirements with:
```sh
pip install pandas yfinance matplotlib
```

---

## 📌 License

MIT License

---

Feel free to add screenshots of your plots below for a more visual showcase!