import pandas as pd

def show_top_strategies(csv_path="optimization_results.csv", top_n=10):
    df = pd.read_csv(csv_path)
    
    # Sort by final equity descending
    df_sorted = df.sort_values(by="final_equity", ascending=False).reset_index(drop=True)
    
    # Select columns to display
    display_cols = ["min_candle_size_pips", "sma50_distance_pips", "atr_period", "atr_multiplier",
                    "total_trades", "wins", "losses", "win_rate_pct", "final_equity"]
    
    print(f"\nTop {top_n} Strategies by Final Equity:\n")
    print(df_sorted[display_cols].head(top_n).to_string(index=False))

if __name__ == "__main__":
    show_top_strategies()
