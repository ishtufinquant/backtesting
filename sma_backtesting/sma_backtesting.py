import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def backtest(ticker, start_date, end_date, strategy="SMA", 
             sma_short=20, sma_long=50, 
             RSI_lower=30, RSI_upper=70, 
             bb_window=20, bb_std=2,
             macd_fast=12, macd_slow=26, macd_signal=9,
             plot=False):
    """
    Backtest trading strategies (SMA, MACD, RSI, Bollinger Bands) on historical stock data.
    Returns trades DataFrame and summary statistics.
    """

    # --- Helper function to generate buy/sell signals based on signal column changes ---
    def get_trade_signals(signal_col, prev_signal_col):
        buy_signals = (signal_col == 1) & (prev_signal_col != 1)
        sell_signals = (signal_col == -1) & (prev_signal_col != -1)
        return buy_signals, sell_signals

    # --- Download historical data using yfinance ---
    data = yf.download(ticker, start=start_date, end=end_date)
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

    # --- Select price column (prefer Adjusted Close if available) ---
    if "Adj Close" in data.columns:
        price_col = "Adj Close"
    elif "Close" in data.columns:
        price_col = "Close"
    else:
        raise ValueError("Price Column not Found")

    price_series = data[price_col]

    # ===================== MACD STRATEGY =====================
    if strategy.upper() == "MACD":
        # --- Calculate fast and slow EMAs for MACD ---
        data["EMA_fast"] = price_series.ewm(span=macd_fast, adjust=False).mean()
        data["EMA_slow"] = price_series.ewm(span=macd_slow, adjust=False).mean()

        # --- Compute MACD line and Signal line ---
        data["MACD"] = data["EMA_fast"] - data["EMA_slow"]
        data["Signal"] = data["MACD"].ewm(span=macd_signal, adjust=False).mean()
        data.dropna(subset=["MACD","Signal"], inplace=True)
        price_series = data[price_col]  # Update price_series to to align with data after dropna()
        # NOTE: MACD strategy modifies price_series with dropna().

        # --- Generate trading signals: 1 for buy, -1 for sell ---
        data["Position"] = 0
        data.loc[data["MACD"] > data["Signal"], "Position"] = 1
        data.loc[data["MACD"] < data["Signal"], "Position"] = -1

        # --- Shift position to avoid lookahead bias ---
        data["Prev_Position"] = data["Position"].shift()

        # --- Identify buy/sell signals based on crossovers ---
        data["buy_signals"], data["sell_signals"] = get_trade_signals(data["Position"], data["Prev_Position"])

        # --- Simulate trades based on signals ---
        MACD_trades = []
        position = None
        for i in range(len(data)):
            # Enter trade on buy signal if not already in position
            if data["buy_signals"].iloc[i] and position == None:
                entry_date = data.index[i]
                entry_price = data[price_col].iloc[i]
                position = "long"
            # Exit trade on sell signal if in position
            elif data["sell_signals"].iloc[i] and position == "long":
                exit_date = data.index[i]
                exit_price = price_series.iloc[i]
                profit = exit_price - entry_price
                MACD_trades.append({
                    "Buy Date": entry_date,
                    "Sell Date": exit_date,
                    "Buy Price": entry_price,
                    "Sell Price": exit_price,
                    "Profit": profit
                })
                position = None
        # If still in position at the end, close trade at last price
        if position == "long":
            exit_date = data.index[-1]
            exit_price = price_series.iloc[-1]
            profit = exit_price - entry_price
            MACD_trades.append({
                "Buy Date": entry_date,
                "Sell Date": exit_date,
                "Buy Price": entry_price,
                "Sell Price": exit_price,
                "Profit": profit
            })
        MACD_trades_df = pd.DataFrame(MACD_trades)

        # --- Calculate performance metrics ---
        if not MACD_trades_df.empty and "Profit" in MACD_trades_df.columns:
            MACD_total_trades = len(MACD_trades_df)
            MACD_winrate = (MACD_trades_df['Profit'] > 0).mean() * 100 if MACD_total_trades > 0 else 0
            MACD_avg_profit = MACD_trades_df['Profit'].mean() if MACD_total_trades > 0 else 0
            MACD_total_profit = MACD_trades_df['Profit'].sum()
            MACD_trades_df["Cumulative_Profit"] = MACD_trades_df["Profit"].cumsum()
        else:
            print("No trades found during the period you mentioned")
            return pd.DataFrame(), 0, 0, 0, 0

        # --- Plotting section ---
        if plot:
            # --- Price plot with buy/sell signals ---
            plt.figure(figsize=(12, 5))
            plt.plot(price_series.index, price_series, label=price_col, alpha=0.6, color="blue", linewidth=1.5)
            plt.plot(data.index[data["buy_signals"]], price_series[data["buy_signals"]], '^', color='green', label='MACD Buy', markersize=8)
            plt.plot(data.index[data["sell_signals"]], price_series[data["sell_signals"]], 'v', color='red', label='MACD Sell', markersize=8)
            plt.title(f"MACD Strategy Buy/Sell Signals on {ticker}", fontsize=14)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Price", fontsize=12)
            plt.legend(loc="upper left", fontsize=10)
            plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.tight_layout()
            plt.show()

            # --- MACD lines and Histogram plot ---
            plt.figure(figsize=(12,5))
            plt.plot(data.index, data["MACD"], label="MACD Line", color="blue", linewidth=1.5)
            plt.plot(data.index, data["Signal"], label="Signal Line", color="orange", linewidth=1.5)
            hist_colors = ['green' if val >= 0 else 'red' for val in (data["MACD"] - data["Signal"])]
            plt.bar(data.index, data["MACD"] - data["Signal"], color=hist_colors, alpha=0.5, label="Histogram")
            plt.title(f"MACD, Signal Line and Histogram for {ticker}", fontsize=14)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Value", fontsize=12)
            plt.legend(loc="upper left", fontsize=10)
            plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
            plt.tight_layout()
            plt.show()

            # --- Cumulative Profit plot ---
            if not MACD_trades_df.empty and "Cumulative_Profit" in MACD_trades_df.columns:
                plt.figure(figsize=(12, 5))
                plt.plot(MACD_trades_df["Sell Date"], MACD_trades_df["Cumulative_Profit"], label="Cumulative Profit", color='steelblue', linewidth=2)
                plt.title(f"Cumulative Profit using MACD Strategy on {ticker}", fontsize=14)
                plt.xlabel("Sell Date", fontsize=12)
                plt.ylabel("Cumulative Profit", fontsize=12)
                plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
                plt.legend(loc="upper left", fontsize=10)
                plt.tight_layout()
                plt.show()
            else:
                print("Cumulative Profit plot skipped: either no trades recorded or 'Cumulative_Profit' column is missing.")

        # --- Return trades DataFrame and summary statistics ---
        return MACD_trades_df, MACD_total_trades, MACD_winrate, MACD_avg_profit, MACD_total_profit

    # ===================== SMA STRATEGY =====================
    elif strategy.upper() == "SMA":
        # --- Calculate short and long SMAs ---
        data['SMA_SHORT'] = price_series.rolling(window=sma_short).mean()
        data['SMA_LONG'] = price_series.rolling(window=sma_long).mean()
        
        data.dropna(subset=["SMA_SHORT", "SMA_LONG"], inplace=True)
       
        price_series = data[price_col]  # Update price_series to to align with data after dropna()
        # NOTE: SMA strategy modifies price_series with dropna().

        # --- Generate SMA crossover signals ---
        data['SMA_Signal'] = 0
        data.loc[data['SMA_SHORT'] > data['SMA_LONG'], 'SMA_Signal'] = 1
        data.loc[data['SMA_SHORT'] < data['SMA_LONG'], 'SMA_Signal'] = -1
        data['SMA_Prev_Signal'] = data['SMA_Signal'].shift(1).fillna(0)

        # --- Identify buy/sell points using helper ---
        buy_mask, sell_mask = get_trade_signals(data['SMA_Signal'], data['SMA_Prev_Signal'])

        # --- Simulate trades based on signals ---
        SMA_trades = []
        position = None
        entry_price = 0
        entry_date = None

        for i in range(len(data)):
            # Enter trade on buy signal if not already in position
            if buy_mask.iloc[i] and position is None:
                entry_date = data.index[i]
                entry_price = price_series.iloc[i]
                position = 'long'
            # Exit trade on sell signal if in position
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

        # If still in position at the end, close trade at last price
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

        # --- Calculate performance metrics ---
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

        # --- Plotting section ---
        if plot:
            # --- SMA Signal Plot ---
            plt.figure(figsize=(12, 5))
            plt.plot(price_series.index, price_series, label=price_col, alpha=0.6, color="blue", linewidth=1.5)
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

        # --- Return trades DataFrame and summary statistics ---
        return SMA_trades_df, SMA_total_trades, SMA_winrate, SMA_avg_profit, SMA_total_profit

# ...existing code...

if __name__ == "__main__":
    results = backtest(
        "TSLA", "2023-01-01", "2025-04-30", strategy="MACD",
        sma_short=20, sma_long=50,
        RSI_lower=30, RSI_upper=70,
        bb_window=20, bb_std=2,
        macd_fast=12, macd_slow=26, macd_signal=9,
        plot=True
    )
    print(results)



