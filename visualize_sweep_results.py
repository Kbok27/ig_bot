# File: visualize_sweep_results.py

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(
        description="Load a parameter-sweep CSV, visualize results, and export top configs"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to your parameter_sweep CSV (e.g. results/parameter_sweep_results.csv)"
    )
    parser.add_argument(
        "--head",
        type=int,
        default=5,
        help="How many rows to preview before plotting"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="How many top configs (by Sharpe) to export to JSON"
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        print(f"❌ Error: cannot find CSV at {csv_path.resolve()}")
        return

    # ——— Load & preview ———
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows from {csv_path}\n")
    print(df.head(args.head).to_string(index=False))
    print("\n")

    # ——— Example scatter plot ———
    plt.figure()
    df.plot.scatter(x="reward_ratio", y="sharpe", ax=plt.gca())
    plt.title("Sharpe by Reward Ratio")
    plt.xlabel("Reward Ratio")
    plt.ylabel("Sharpe")
    plt.tight_layout()
    plot_path = csv_path.with_suffix(".png")
    plt.savefig(plot_path)
    print(f"📊 Scatter plot saved to {plot_path}")

    # ——— Export top N configs to JSON ———
    top_n = df.sort_values("sharpe", ascending=False).head(args.top)
    out_json = csv_path.parent / "top_configs.json"
    top_n.to_json(out_json, orient="records", indent=2)
    print(f"✅ Top {args.top} configs written to {out_json}")

if __name__ == "__main__":
    main()
