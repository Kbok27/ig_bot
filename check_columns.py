# check_columns.py
import pandas as pd

df = pd.read_csv("optimize_results/strategy_batch_extended_results.csv")
print("[INFO] Column names in the CSV:")
print(df.columns.tolist())
