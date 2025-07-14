import pandas as pd

csv_path = "optimize_results/optimization_results.csv"

try:
    df = pd.read_csv(csv_path)
    print("CSV loaded successfully!")
    print("Columns found:")
    print(df.columns.tolist())
except FileNotFoundError:
    print(f"File not found: {csv_path}")
except Exception as e:
    print(f"Error reading CSV: {e}")
