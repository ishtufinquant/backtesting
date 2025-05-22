import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# AAPL, TSLA, GME
def backtest(ticker, start_date, end_date, strategy="SMA", 
             sma_short=20, sma_long=50, 
             RSI_lower=30, RSI_upper=70, 
             bb_window=20, bb_std=2,
             macd_fast=12, macd_slow=26, macd_signal=9,
             plot=False):

    def get_trade_signals(signal_col, prev_signal_col):
        buy_signals = (signal_col == 1) & (prev_signal_col != 1)
        sell_signals = (signal_col == -1) & (prev_signal_col != -1)
        return buy_signals, sell_signals

    data = yf.download(ticker, start=start_date, end=end_date)
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    if "Adj Close" in data.columns:
        price_col = "Adj Close"
    elif "Close" in data.columns:
        price_col = "Close"
    else:
        raise ValueError("Price Column not Found")

    price_series = data[price_col]

    if strategy.upper() == "SMA":
        # ===================== SMA STRATEGY =====================
        data['SMA_SHORT'] = price_series.rolling(window=sma_short).mean()
        data['SMA_LONG'] = price_series.rolling(window=sma_long).mean()
        data.dropna(subset=["SMA_SHORT", "SMA_LONG"], inplace=True)

        data['SMA_Signal'] = 0
        data.loc[data['SMA_SHORT'] > data['SMA_LONG'], 'SMA_Signal'] = 1
        data.loc[data['SMA_SHORT'] < data['SMA_LONG'], 'SMA_Signal'] = -1
        data['SMA_Prev_Signal'] = data['SMA_Signal'].shift(1).fillna(0)

        buy_mask, sell_mask = get_trade_signals(data['SMA_Signal'], data['SMA_Prev_Signal'])

        SMA_trades = []
        position = None
        entry_price = 0
        entry_date = None

        for i in range(len(data)):
            if buy_mask.iloc[i] and position is None:
                entry_date = data.index[i]
                entry_price = price_series.iloc[i]
                position = 'long'
            elif sell_mask.iloc[i] and position == 'long':
                exit_date = data.index[i]
                exit_price = price_series.iloc[i]
                profit = exit_price - entry_price
                SMA_trades.append({
                    "Buy Date": entry_date,
                    "Buy Price": entry_price,
                    "Sell Date": exit_date,
                    "Sell Price": exit_price,
                    "Profit": profit
                })
                position = None

        if position == "long":
            exit_date = data.index[-1]
            exit_price = price_series.iloc[-1]
            profit = exit_price - entry_price
            SMA_trades.append({
                "Buy Date": entry_date,
                "Buy Price": entry_price,
                "Sell Date": exit_date,
                "Sell Price": exit_price,
                "Profit": profit
            })
        SMA_trades_df = pd.DataFrame(SMA_trades)

        if not SMA_trades_df.empty and "Profit" in SMA_trades_df.columns:
            SMA_trades_df["Profit"] = pd.to_numeric(SMA_trades_df["Profit"], errors="coerce")
            SMA_total_trades = len(SMA_trades_df)
            SMA_winrate = (SMA_trades_df['Profit'] > 0).mean() * 100 if SMA_total_trades > 0 else 0
            SMA_avg_profit = SMA_trades_df['Profit'].mean() if SMA_total_trades > 0 else 0
            SMA_total_profit = SMA_trades_df['Profit'].sum()
            SMA_trades_df["Cumulative_Profit"] = SMA_trades_df["Profit"].cumsum()
        else:
            print("No trades found during the period you mentioned")
            return pd.DataFrame(), 0, 0, 0, 0

        if plot:
            # --- SMA Signal Plot ---
            plt.figure(figsize=(12, 5))
            plt.plot(price_series.index, price_series, label='Close Price', alpha=0.6, color="blue", linewidth=1.5)
            plt.plot(data[buy_mask].index, data.loc[buy_mask, price_col], '^', color='green', label='SMA Buy', markersize=8)
            plt.plot(data[sell_mask].index, data.loc[sell_mask, price_col], 'v', color='red', label='SMA Sell', markersize=8)
            plt.plot(data.index, data['SMA_SHORT'], label=f"SMA {sma_short}", linestyle='--', color='orange', linewidth=1.2)
            plt.plot(data.index, data['SMA_LONG'], label=f"SMA {sma_long}", linestyle='--', color='purple', linewidth=1.2)

            plt.title(f"SMA Signals on {ticker}", fontsize=14)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Price", fontsize=12)
            plt.legend(loc="upper left", fontsize=10)
            plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.tight_layout()

            # --- Cumulative Profit Plot ---
            plt.figure(figsize=(12, 5))
            plt.plot(SMA_trades_df["Sell Date"], SMA_trades_df["Cumulative_Profit"], label='Cumulative Profit', color='steelblue', linewidth=2)
            plt.title(f'Cumulative Profit using SMA Strategy on {ticker}', fontsize=14)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Cumulative Profit", fontsize=12)
            plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.legend(loc="upper left", fontsize=10)
            plt.tight_layout()

            plt.show()

        return SMA_trades_df, SMA_total_trades, SMA_winrate, SMA_avg_profit, SMA_total_profit
    else:
        print("Please ensure to use (sma) as strategy")
        return None
results=backtest("TSLA", "2023-01-01", "2025-04-30", strategy="SMA", 
             sma_short=20, sma_long=50, 
             RSI_lower=30, RSI_upper=70, 
             bb_window=20, bb_std=2,
             macd_fast=12, macd_slow=26, macd_signal=9,
             plot=True)
print (results)