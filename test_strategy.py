import pandas as pd
from strategies.sma_stochastic_v4 import run_strategy

def main():
    # Adjust this to your CSV file path
    file_path = "data/NAS100_5m.csv"
    df = pd.read_csv(file_path)

    # Convert Time to datetime and set as index
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.set_index('Time')

    # Run strategy with debug logs on
    result_df, trades_df, equity_curve, debug_log = run_strategy(df, debug=True)

    print(f"Total trades taken: {len(trades_df)}")
    if not trades_df.empty:
        print(trades_df.head())

    print(f"Final equity: {equity_curve[-1] if equity_curve else 'N/A'}")

    print("\nSample debug logs:")
    for log_line in debug_log[:10]:
        print(log_line)

if __name__ == "__main__":
    main()
