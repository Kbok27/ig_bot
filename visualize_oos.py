"""
visualize_oos.py

Load your out-of-sample validation report and create summary charts:
  1. Best Sharpe by Symbol
  2. Param combination Sharpe heatmap for each symbol
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Path to OOS validation CSV
OOS_CSV = os.path.join('results', 'oos_validation.csv')

# Load DataFrame with guard against empty data
try:
    df = pd.read_csv(OOS_CSV)
except pd.errors.EmptyDataError:
    print(f"No data to visualize in {OOS_CSV}")
    exit(0)

if df.empty or len(df.columns) == 0:
    print(f"{OOS_CSV} is empty or malformed—nothing to plot.")
    exit(0)

# Ensure numeric types for metrics
for col in ['sharpe']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 1) Best Sharpe per Symbol
best_sharpe = df.groupby('symbol')['sharpe'].max().reset_index()
plt.figure(figsize=(6, 4))
plt.bar(best_sharpe['symbol'], best_sharpe['sharpe'])
plt.title('Best OOS Sharpe Ratio by Symbol')
plt.xlabel('Symbol')
plt.ylabel('Sharpe Ratio')
plt.tight_layout()
plt.show()

# 2) Heatmap: Take Profit vs Stop Loss Sharpe for each symbol
for symbol in best_sharpe['symbol']:
    sub = df[df['symbol'] == symbol]
    pivot = sub.pivot_table(
        index='stop_loss_pips',
        columns='take_profit_pips',
        values='sharpe',
        aggfunc='max'
    )
    if pivot.empty:
        print(f"No heatmap data for {symbol}")
        continue
    plt.figure(figsize=(6, 4))
    sns.heatmap(pivot, annot=True, fmt='.2f', cbar_kws={'label': 'Sharpe'})
    plt.title(f'OOS Sharpe Heatmap: {symbol}')
    plt.xlabel('Take Profit Pips')
    plt.ylabel('Stop Loss Pips')
    plt.tight_layout()
    plt.show()
