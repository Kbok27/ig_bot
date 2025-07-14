# generate_dashboard_table.py

import pandas as pd

# === CONFIGURATION ===
csv_path = "optimize_results/strategy_batch_extended_results.csv"
html_path = "optimize_results/dashboard_table.html"
min_trades = 20

# === FILTERING RULES ===
filters = {
    "Win_rate_percent": lambda x: x > 40,
    "Sharpe_ratio": lambda x: x > 0.15,
    "Max_drawdown": lambda x: x < 30,
    "Trades": lambda x: x >= min_trades,
}

# === LOAD CSV ===
df = pd.read_csv(csv_path)

# === COLUMN SANITIZATION (handle leading/trailing spaces) ===
df.columns = df.columns.str.strip()

# === APPLY FILTERS ===
initial_count = len(df)
for column, condition in filters.items():
    if column not in df.columns:
        print(f"[WARN] Column not found: {column}")
        continue
    df = df[condition(df[column])]

filtered_count = len(df)
print(f"[INFO] Strategies before filtering: {initial_count}")
print(f"[INFO] Strategies after filtering: {filtered_count}")

# === SORT & CLEAN ===
df = df.sort_values(by="Final_equity", ascending=False)

# === HTML GENERATION ===
html = "<h2>Top Strategies (Filtered)</h2>\n"
html += "<table border='1' cellpadding='5' cellspacing='0'>\n"
html += "<tr>" + "".join([f"<th>{col}</th>" for col in df.columns]) + "</tr>\n"

for _, row in df.iterrows():
    html += "<tr>" + "".join([f"<td>{row[col]}</td>" for col in df.columns]) + "</tr>\n"

html += "</table>\n"

# === SAVE TO FILE ===
with open(html_path, "w") as f:
    f.write(html)

print(f"[✅] HTML dashboard table updated: {html_path}")
