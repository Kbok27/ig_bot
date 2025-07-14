# analyze_parameter_sweep.py

import pandas as pd

def analyze_results(file_path="results/parameter_sweep_results.csv"):
    df = pd.read_csv(file_path)
    
    # Show summary statistics
    print("[SUMMARY]")
    print(df.describe())
    
    # Best net profit
    best_profit = df.loc[df["Net Profit"].idxmax()]
    print("\n[Best Net Profit]")
    print(best_profit)
    
    # Highest win rate (with at least some trades)
    df_filtered = df[df["Number of Trades"] > 10]
    best_win_rate = df_filtered.loc[df_filtered["Win Rate"].idxmax()]
    print("\n[Highest Win Rate (min 10 trades)]")
    print(best_win_rate)
    
    # Top 5 by net profit
    print("\n[Top 5 Parameter Sets by Net Profit]")
    print(df.sort_values("Net Profit", ascending=False).head(5))
    
if __name__ == "__main__":
    analyze_results()
