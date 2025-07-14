# visualize_optimization.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    df = pd.read_csv("results/optimization_results.csv")

    # Aggregate duplicate parameter combinations by averaging Net Profit
    df_grouped = df.groupby(["min_leg_move", "max_leg_gap"]).agg({"Net Profit": "mean"}).reset_index()

    # Pivot for heatmap
    heatmap_data = df_grouped.pivot(index="min_leg_move", columns="max_leg_gap", values="Net Profit")

    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="viridis")
    plt.title("Net Profit Heatmap by min_leg_move and max_leg_gap")
    plt.xlabel("max_leg_gap")
    plt.ylabel("min_leg_move")
    plt.tight_layout()
    plt.savefig("plots/net_profit_heatmap.png")
    plt.show()

if __name__ == "__main__":
    main()
