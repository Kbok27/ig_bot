import pandas as pd
import os

def analyze_state_distribution(symbol="AAPL", folder="logs"):
    file_path = os.path.join(folder, f"{symbol}_debug_log.csv")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return

    df = pd.read_csv(file_path)

    if "state" not in df.columns:
        print("[ERROR] 'state' column not found in debug log.")
        return

    print(f"[INFO] Market State Distribution for {symbol}:")
    print(df["state"].value_counts())
    print()

    print("[INFO] Preview of sampled states over time:")
    print(df[["time", "state"]].head(10))


if __name__ == "__main__":
    analyze_state_distribution("AAPL")
