# export_dashboard_to_excel.py

import pandas as pd

# Load the CSV
csv_path = "optimize_results/strategy_batch_extended_results.csv"
df = pd.read_csv(csv_path)

# Export to Excel
excel_path = "optimize_results/strategy_dashboard.xlsx"
df.to_excel(excel_path, index=False)

print(f"[✅] Excel file saved to: {excel_path}")
