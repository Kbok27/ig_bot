import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# ─── ARGPARSE SETUP ─────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description="Load optimization results and plot a dashboard with Profit Factor, Max Drawdown, and Avg Trade Return."
)
parser.add_argument(
    "--min-trades",
    type=int,
    default=500,
    help="Minimum number of trades to include a config"
)
parser.add_argument(
    "--min-win-rate",
    type=float,
    default=0.18,
    help="Minimum win-rate (e.g. 0.18 for 18%) to include a config"
)
parser.add_argument(
    "--save-dir",
    type=str,
    default="plots",
    help="Directory in which to save dashboard.png and dashboard.pdf"
)
args = parser.parse_args()

MIN_TRADES   = args.min_trades
MIN_WIN_RATE = args.min_win_rate
PLOTS_DIR    = os.path.abspath(args.save_dir)

# ─── PATH CONFIG ────────────────────────────────────────────────────────────────
SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR   = os.path.join(SCRIPT_DIR, "optimize", "results")
BACKTEST_FILE = os.path.join(RESULTS_DIR, "optimizer_results.csv")
PNG_PATH      = os.path.join(PLOTS_DIR, "dashboard.png")
PDF_PATH      = os.path.join(PLOTS_DIR, "dashboard.pdf")
# ────────────────────────────────────────────────────────────────────────────────

def plot_dashboard():
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # 1) load CSV
    if not os.path.exists(BACKTEST_FILE):
        print(f"[❌] File not found: {BACKTEST_FILE}")
        return
    df = pd.read_csv(BACKTEST_FILE)
    print(f"[ℹ] Loaded {len(df)} rows from {BACKTEST_FILE}")

    # 2) compute optional metrics
    if "profit_factor" not in df.columns and {"gross_profit", "gross_loss"}.issubset(df.columns):
        df["profit_factor"] = df["gross_profit"] / df["gross_loss"].abs().replace(0, pd.NA)
        print("[ℹ] Computed profit_factor from gross_profit & gross_loss")

    has_md = "max_drawdown" in df.columns
    has_avg = "avg_trade_return" in df.columns

    # 3) apply filters
    if "num_trades" not in df.columns or "win_rate" not in df.columns:
        print("[❌] Required columns 'num_trades' or 'win_rate' missing.")
        return
    df = df[(df["num_trades"] > MIN_TRADES) & (df["win_rate"] >= MIN_WIN_RATE)].reset_index(drop=True)
    if df.empty:
        print(f"[⚠️] No configs meet filters trades > {MIN_TRADES} & win_rate ≥ {MIN_WIN_RATE}")
        return
    print(f"[ℹ] {len(df)} configs pass filters")

    # prepare labels and configs
    positions = list(range(len(df)))
    labels    = [str(i+1) for i in positions]
    metrics   = {"final_equity","num_trades","sharpe","win_rate","profit_factor","max_drawdown","avg_trade_return"}
    param_cols = [c for c in df.columns if c not in metrics]
    config_dicts = df[param_cols].to_dict(orient="records")

    # determine number of panels
    panels = 3 + (1 if "profit_factor" in df.columns else 0)
    panels += 1 if has_md else 0
    panels += 1 if has_avg else 0

    fig, axes = plt.subplots(panels, 1, figsize=(10, 4*panels))
    fig.subplots_adjust(bottom=0.25, hspace=0.5)

    idx = 0
    # Final Equity
    ax = axes[idx] if panels>1 else axes
    ax.bar(positions, df["final_equity"])
    ax.set_title("Final Equity by Config")
    ax.set_ylabel("Final Equity")
    ax.set_xticks(positions); ax.set_xticklabels(labels)
    idx += 1

    # Win Rate
    ax = axes[idx]
    ax.bar(positions, df["win_rate"])
    ax.set_title("Win Rate by Config")
    ax.set_ylabel("Win Rate")
    ax.set_xticks(positions); ax.set_xticklabels(labels)
    idx += 1

    # Profit Factor
    if "profit_factor" in df.columns:
        ax = axes[idx]
        ax.bar(positions, df["profit_factor"])
        ax.set_title("Profit Factor by Config")
        ax.set_ylabel("Profit Factor")
        ax.set_xticks(positions); ax.set_xticklabels(labels)
        idx += 1

    # Max Drawdown
    if has_md:
        ax = axes[idx]
        ax.bar(positions, df["max_drawdown"])
        ax.set_title("Max Drawdown by Config")
        ax.set_ylabel("Max Drawdown")
        ax.set_xticks(positions); ax.set_xticklabels(labels)
        idx += 1

    # Avg Trade Return
    if has_avg:
        ax = axes[idx]
        ax.bar(positions, df["avg_trade_return"])
        ax.set_title("Avg Trade Return by Config")
        ax.set_ylabel("Avg Trade Return")
        ax.set_xticks(positions); ax.set_xticklabels(labels)
        idx += 1

    # Trades vs Equity
    ax = axes[idx]
    ax.scatter(df["num_trades"], df["final_equity"])
    ax.set_title("Trades vs Final Equity")
    ax.set_xlabel("Number of Trades")
    ax.set_ylabel("Final Equity")
    for i, (x, y) in enumerate(zip(df["num_trades"], df["final_equity"])):
        ax.annotate(str(i+1), (x, y), textcoords="offset points", xytext=(5,5), fontsize=9)

    fig.tight_layout()
    plt.show()

    # save outputs
    os.makedirs(PLOTS_DIR, exist_ok=True)
    fig.savefig(PNG_PATH, dpi=150, bbox_inches="tight")
    fig.savefig(PDF_PATH, bbox_inches="tight")
    print(f"[✅] Dashboard saved to {PLOTS_DIR}")

    # legend
    print("\n[ℹ] Config legend (index → parameter dict):")
    for i, cfg in enumerate(config_dicts):
        print(f"  {i+1}: {cfg}")

if __name__ == "__main__":
    plot_dashboard()
