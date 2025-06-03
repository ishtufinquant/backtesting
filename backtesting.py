import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def backtest(
    ticker: str,
    start_date: str,
    end_date: str,
    strategy: str = "SMA",
    sma_short: int = 20,
    sma_long: int = 50,
    RSI_lower: int = 30,
    RSI_upper: int = 70,
    bb_window: int = 20,
    bb_std: int = 2,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    plot: bool = False
) -> tuple:
    """
    Backtest trading strategies (SMA, MACD, RSI, Bollinger Bands) on historical stock data.
    Returns trades DataFrame and summary statistics.
    """

    # --- Helper function to generate buy/sell signals based on signal column changes ---
    def get_trade_signals(signal_col, prev_signal_col):
        """
    Generate boolean masks for buy and sell signals based on changes in signal columns.
    Returns:
        buy_signals (pd.Series): True where a buy signal occurs.
        sell_signals (pd.Series): True where a sell signal occurs.
    """
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

    # ===================== MACD STRATEGY =====================
    if strategy.upper() == "MACD":
        # --- Calculate fast and slow EMAs for MACD ---
        data["EMA_fast"] = data[price_col].ewm(span=macd_fast, adjust=False).mean()
        data["EMA_slow"] = data[price_col].ewm(span=macd_slow, adjust=False).mean()

        # --- Compute MACD line and Signal line ---
        data["MACD"] = data["EMA_fast"] - data["EMA_slow"]
        data["Signal"] = data["MACD"].ewm(span=macd_signal, adjust=False).mean()
        data.dropna(subset=["MACD","Signal"], inplace=True)
        
        # --- Generate trading signals: 1 for buy, -1 for sell ---
        data["MACD_Signal"] = 0
        data.loc[data["MACD"] > data["Signal"], "MACD_Signal"] = 1
        data.loc[data["MACD"] < data["Signal"], "MACD_Signal"] = -1

        # --- Shift position to avoid lookahead bias ---
        data["MACD_Prev_Signal"] = data["MACD_Signal"].shift(1).fillna(0)
        
        # --- Identify buy/sell signals based on crossovers ---
        buy_mask, sell_mask = get_trade_signals(data["MACD_Signal"], data["MACD_Prev_Signal"])

        # --- Simulate trades based on signals ---
        MACD_trades = []
        position = None
        for i in range(len(data)):
            # Enter trade on buy signal if not already in position
            if buy_mask.iloc[i] and position == None:
                entry_date = data.index[i]
                entry_price = data[price_col].iloc[i]
                position = "long"
            # Exit trade on sell signal if in position
            elif sell_mask.iloc[i] and position == "long":
                exit_date = data.index[i]
                exit_price = data[price_col].iloc[i]
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
            exit_price = data[price_col].iloc[-1]
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
            plt.plot(data[price_col].index, data[price_col], label=price_col, alpha=0.6, color="blue", linewidth=1.5)
            plt.plot(data[buy_mask].index, data.loc[buy_mask,price_col], '^', color='green', label='MACD Buy', markersize=8)
            plt.plot(data[sell_mask].index, data.loc[sell_mask,price_col], 'v', color='red', label='MACD Sell', markersize=8)
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
        data['SMA_SHORT'] = data[price_col].rolling(window=sma_short).mean()
        data['SMA_LONG'] = data[price_col].rolling(window=sma_long).mean()
        
        data.dropna(subset=["SMA_SHORT", "SMA_LONG"], inplace=True)

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
                entry_price = data[price_col].iloc[i]
                position = 'long'
            # Exit trade on sell signal if in position
            elif sell_mask.iloc[i] and position == 'long':
                exit_date = data.index[i]
                exit_price = data[price_col].iloc[i]
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
            exit_price = data[price_col].iloc[-1]
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
            plt.plot(data[price_col].index, data[price_col], label=price_col, alpha=0.6, color="blue", linewidth=1.5)
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
    # ===================== RSI STRATEGY =====================
    elif strategy.upper() == "RSI":
        delta = data[price_col].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        data["avg_gain"] = gain.rolling(window=14).mean()
        data["avg_loss"] = loss.rolling(window=14).mean()
        data.dropna(subset=["avg_gain", "avg_loss"], inplace=True) 

        rs = data["avg_gain"] / data["avg_loss"]
        data['RSI'] = 100 - (100 / (1 + rs))
        data.drop(['avg_gain', 'avg_loss'], axis=1, inplace=True)

        # --- Generate RSI signals ---
        data['RSI_Signal'] = 0
        data.loc[data['RSI'] < RSI_lower, 'RSI_Signal'] = 1
        data.loc[data['RSI'] > RSI_upper, 'RSI_Signal'] = -1
        data['RSI_Prev_Signal'] = data['RSI_Signal'].shift(1).fillna(0)

        buy_mask, sell_mask = get_trade_signals(data['RSI_Signal'], data['RSI_Prev_Signal'])      
       
        # --- Simulate trades based on RSI signals ---
        # Initialize trade list and position tracking
        RSI_trades = []
        position = None
        entry_price = 0
        entry_date = None

        for i in range(len(data)):
            if buy_mask.iloc[i] and position is None:
                entry_date = data.index[i]
                entry_price = data[price_col].iloc[i]
                position = "long"
            elif sell_mask.iloc[i] == -1 and position == "long":
                exit_date = data.index[i]
                exit_price = data[price_col].iloc[i]
                profit = exit_price - entry_price
                RSI_trades.append({
                    "Buy Date": entry_date,
                    "Buy Price": entry_price,
                    "Sell Date": exit_date,
                    "Sell Price": exit_price,
                    "Profit": profit
                })
                position = None

        if position == "long":
                exit_date = data.index[-1]
                exit_price = data[price_col].iloc[-1]
                profit = exit_price - entry_price
                RSI_trades.append({
                    "Buy Date": entry_date,
                    "Buy Price": entry_price,
                    "Sell Date": exit_date,
                    "Sell Price": exit_price,
                    "Profit": profit
                })

        RSI_trades_df = pd.DataFrame(RSI_trades)
        RSI_total_trades = len(RSI_trades_df)
        RSI_winrate = (RSI_trades_df['Profit'] > 0).mean() * 100 if RSI_total_trades > 0 else 0
        RSI_avg_profit = RSI_trades_df['Profit'].mean() if RSI_total_trades > 0 else 0
        RSI_total_profit = RSI_trades_df['Profit'].sum()
        RSI_trades_df["Cumulative_Profit"] = RSI_trades_df['Profit'].cumsum()
        print("RSI_trades_df:")
        print(RSI_trades_df)
        print("Cumulative Profit values:")
        print(RSI_trades_df["Cumulative_Profit"])
        print("Sell Dates:")
        print(RSI_trades_df["Sell Date"])
        if plot:
            plt.figure(figsize=(10, 4))
            plt.plot(data.index, data["RSI"], label="RSI", color="purple")
            plt.axhline(70, color='red', linestyle='--', label='Overbought')
            plt.axhline(30, color='green', linestyle='--', label='Oversold')
            plt.plot(data[buy_mask].index, data.loc[buy_mask,price_col], '^', linestyle= '--', color='green', label='RSI Buy')
            plt.plot(data[sell_mask].index, data.loc[sell_mask,price_col], 'v',linestyle= '--', color='orange', label='RSI Sell')
            plt.title(f"RSI Buy/Sell Signals on {ticker}")
            plt.legend()
            plt.xlabel("Date")
            plt.tight_layout()

            plt.figure(figsize=(10, 4))
            plt.plot(RSI_trades_df["Sell Date"], RSI_trades_df["Cumulative_Profit"], label="RSI Cumulative Profit")
            plt.xlabel("Sell Date")
            plt.ylabel("Cumulative Profit")
            plt.legend()
            plt.tight_layout()
            plt.show()

        return RSI_trades_df, RSI_total_trades, RSI_winrate, RSI_avg_profit, RSI_total_profit
# ===================BOLLINGER BANDS STRATEGY =========+====    
    elif strategy.upper() == "BOLLINGER":

        data["MA"] = data[price_col].rolling(window=bb_window).mean()
        data["STD"] = data[price_col].rolling(window=bb_window).std()
        data["Upper_Band"] = data["MA"] + (bb_std * data["STD"])
        data["Lower_Band"] = data["MA"] - (bb_std * data["STD"])
        data.dropna(subset=["Upper_Band", "Lower_Band"], inplace=True)

        data["Bollinger_Signal"] = 0
        data.loc[data[price_col] < data["Lower_Band"], "Bollinger_Signal"] = 1  # Buy
        data.loc[data[price_col] > data["Upper_Band"], "Bollinger_Signal"] = -1 # Sell
        data["Bollinger_Prev_Signal"] = data["Bollinger_Signal"].shift(1).fillna(0)
       
        # --- Identify buy/sell points using helper ---
        buy_mask,sell_mask = get_trade_signals(data["Bollinger_Signal"],data["Bollinger_Prev_Signal"] )

        Bollinger_trades = []
        position = None
        entry_price = 0
        entry_date = None

        for i in range(len(data)):
            signal = data["Bollinger_Signal"].iloc[i]
            prev = data["Bollinger_Prev_Signal"].iloc[i]
            if signal == 1 and prev != 1 and position is None:
                entry_date = data.index[i]
                entry_price = data[price_col].iloc[i]
                position = "long"
            elif signal == -1 and prev != -1 and position == "long":
                exit_date = data.index[i]
                exit_price = data[price_col].iloc[i]
                profit = exit_price - entry_price
                Bollinger_trades.append({
                    "Buy Date": entry_date,
                    "Buy Price": entry_price,
                    "Sell Date": exit_date,
                    "Sell Price": exit_price,
                    "Profit": profit
                })
                position = None

        if position == "long":
            exit_date = data.index[-1]
            exit_price = data[price_col].iloc[-1]
            profit = exit_price - entry_price
            Bollinger_trades.append({
                "Buy Date": entry_date,
                "Buy Price": entry_price,
                "Sell Date": exit_date,
                "Sell Price": exit_price,
                "Profit": profit
            })

        Bollinger_trades_df = pd.DataFrame(Bollinger_trades)
        Bollinger_total_trades = len(Bollinger_trades_df)
        Bollinger_winrate = (Bollinger_trades_df['Profit'] > 0).mean() * 100 if Bollinger_total_trades > 0 else 0
        Bollinger_avg_profit = Bollinger_trades_df['Profit'].mean() if Bollinger_total_trades > 0 else 0
        Bollinger_total_profit = Bollinger_trades_df['Profit'].sum()
        Bollinger_trades_df["Cumulative_Profit"] = Bollinger_trades_df["Profit"].cumsum()

        if plot:
            plt.figure(figsize=(10, 4))
            plt.plot(data.index, data[price_col], label=price_col, alpha=0.6)
            plt.plot(data[buy_mask].index, data.loc[buy_mask,price_col], '^', color='green', label='BB Buy')
            plt.plot(data[sell_mask].index, data.loc[sell_mask, price_col], 'v', color='red', label='BB Sell')
            plt.plot(data.index, data["Upper_Band"], '--', color='grey', label='Upper Band', alpha=0.5)
            plt.plot(data.index, data["Lower_Band"], '--', color='black', label='Lower Band', alpha=0.5)
            plt.title(f'Bollinger Bands Signals on {ticker}')
            plt.xlabel("Date")
            plt.grid()
            plt.legend()
            plt.tight_layout()

            plt.figure(figsize=(10, 4))
            plt.plot(Bollinger_trades_df["Sell Date"], Bollinger_trades_df["Cumulative_Profit"], label='Cumulative Profit')
            plt.title(f'Cumulative profit using Bollinger Bands Strategy on {ticker}')
            plt.xlabel("Date")
            plt.grid()
            plt.legend()
            plt.tight_layout()
            plt.show()

        return Bollinger_trades_df, Bollinger_total_trades, Bollinger_winrate, Bollinger_avg_profit, Bollinger_total_profit
    
    else:
        print(f"Unknown Strategy: {strategy} please use RSI,SMA, BOLLINGER or MACD as strategy ")
    
    

# Example usage (uncomment to run directly)
#backtest("AAPL", "2023-06-01", "2025-04-30", strategy="sma", sma_short=15, sma_long=45, plot=False)
                