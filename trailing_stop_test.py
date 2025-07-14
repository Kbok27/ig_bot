import pandas as pd
import numpy as np
import os

def calculate_atr(df, period=14):
    df = df.copy()
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period, min_periods=1).mean()
    return df

def simulate_trades_with_trailing_stop(df, atr_multiplier=3, initial_equity=10000, debug=True):
    equity = initial_equity
    position = None
    entry_price = 0
    trailing_stop = 0
    trades = []
    debug_log = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]

        if pd.isna(row['ATR']):
            continue

        price = row['Close']
        atr = row['ATR']
        ts_distance = atr * atr_multiplier

        if position is None:
            # Simple entry logic: Buy if close is above previous close
            if price > prev_row['Close']:
                position = 'long'
                entry_price = price
                trailing_stop = price - ts_distance
                trades.append({'entry_time': row.name, 'direction': position, 'entry_price': entry_price})
                if debug:
                    debug_log.append(f"{row.name} ENTER LONG at {entry_price:.2f}, initial trailing stop {trailing_stop:.2f}")

        elif position == 'long':
            # Update trailing stop if price moves up
            new_trailing_stop = price - ts_distance
            if new_trailing_stop > trailing_stop:
                trailing_stop = new_trailing_stop
                if debug:
                    debug_log.append(f"{row.name} UPDATED trailing stop to {trailing_stop:.2f}")

            # Check if price hits trailing stop
            if price <= trailing_stop:
                exit_price = price
                profit = exit_price - entry_price
                equity += profit
                trades[-1].update({'exit_time': row.name, 'exit_price': exit_price, 'profit': profit, 'equity': equity})
                if debug:
                    debug_log.append(f"{row.name} EXIT LONG at {exit_price:.2f} | Profit: {profit:.2f} | Equity: {equity:.2f}")
                position = None
                trailing_stop = 0

    # Close open position at last bar
    if position == 'long':
        exit_price = df.iloc[-1]['Close']
        profit = exit_price - entry_price
        equity += profit
        trades[-1].update({'exit_time': df.index[-1], 'exit_price': exit_price, 'profit': profit, 'equity': equity})
        if debug:
            debug_log.append(f"{df.index[-1]} FINAL EXIT LONG at {exit_price:.2f} | Profit: {profit:.2f} | Equity: {equity:.2f}")

    trades_df = pd.DataFrame(trades)

    if debug:
        print(f"Total trades: {len(trades_df)}")
        print(f"Final equity: {equity:.2f}")
        print("Sample trades:")
        print(trades_df.head())
        print("\nDebug log sample:")
        print("\n".join(debug_log[:10]))

    return trades_df, equity, debug_log

def main():
    file_path = os.path.join("data", "NAS100_5m.csv")
    df = pd.read_csv(file_path, parse_dates=['Time'])
    df.set_index('Time', inplace=True)

    df = calculate_atr(df, period=14)

    trades_df, final_equity, debug_log = simulate_trades_with_trailing_stop(df)

if __name__ == "__main__":
    main()
