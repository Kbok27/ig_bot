# File: dashboard_generator.py

import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# columns to coerce to datetime if present
DATE_COLS = ['entry_time', 'exit_time', 'datetime']

def plot_dashboard(symbol: str, min_trades: int):
    results_dir = Path(__file__).parent / "results"
    trades_file = results_dir / f"{symbol}_results.csv"
    if not trades_file.exists():
        print(f"⚠️  No results CSV for {symbol}, skipping.")
        return

    # 1) load trades, skip bad lines
    trades = pd.read_csv(trades_file, on_bad_lines='skip')
    # coerce any date columns
    for col in DATE_COLS:
        if col in trades.columns:
            trades[col] = pd.to_datetime(trades[col], errors='coerce')

    total_trades = len(trades)
    if total_trades < min_trades:
        print(f"⏭️  Skipping {symbol}: only {total_trades} trades (< {min_trades}).")
        return

    fig, ax1 = plt.subplots()
    ax1.set_title(f"{symbol} — {total_trades} trades")
    ax1.set_xlabel("Time")

    # 2) price overlay (if present)
    price_file = results_dir / f"{symbol}_price.csv"
    price_plotted = False
    if price_file.exists():
        price = pd.read_csv(price_file, on_bad_lines='skip')
        if 'datetime' in price.columns:
            price['datetime'] = pd.to_datetime(price['datetime'], errors='coerce')
            ax1.plot(price['datetime'], price['close'], label='Price')
            price_plotted = True
        else:
            print(f"ℹ️  {symbol}_price.csv has no 'datetime', skipping price plot.")
    else:
        print(f"ℹ️  No price CSV for {symbol}, skipping price overlay.")

    # 3) trade markers if we have entry/exit
    markers_plotted = False
    if 'entry_time' in trades.columns and 'exit_time' in trades.columns:
        for _, r in trades.iterrows():
            ax1.axvline(r['entry_time'], color='green', linestyle='--', alpha=0.5, label='Entry')
            ax1.axvline(r['exit_time'],  color='red',   linestyle='--', alpha=0.5, label='Exit')
        markers_plotted = True
        ax1.set_ylabel("Price")
    else:
        print(f"ℹ️  No entry/exit times for {symbol}, skipping trade markers.")

    # only call legend on ax1 if there’s something to show
    handles, labels = ax1.get_legend_handles_labels()
    if labels:
        ax1.legend(loc='upper right')

    # 4) equity curves
    equity_files = sorted(results_dir.glob(f"{symbol}_equity*.csv"))
    if equity_files:
        ax2 = ax1.twinx()
        for eq in equity_files:
            df_eq = pd.read_csv(eq, on_bad_lines='skip')
            if 'datetime' in df_eq.columns and 'equity' in df_eq.columns:
                df_eq['datetime'] = pd.to_datetime(df_eq['datetime'], errors='coerce')
                ax2.plot(df_eq['datetime'], df_eq['equity'], label=eq.stem)
        # legend only if equity curves plotted
        h2, l2 = ax2.get_legend_handles_labels()
        if l2:
            ax2.legend(loc='upper left')
        ax2.set_ylabel("Equity")
    else:
        print(f"ℹ️  No equity CSVs for {symbol}.")

    plt.tight_layout()
    out_path = results_dir / f"{symbol}_dashboard.png"
    plt.savefig(out_path)
    plt.close(fig)
    print(f"✅ Saved dashboard for {symbol}: {out_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Generate dashboards from results/")
    parser.add_argument(
        "--min-trades",
        type=int,
        default=0,
        help="Minimum rows in *_results.csv to include a symbol"
    )
    args = parser.parse_args()

    results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        print("❌  results/ directory not found.")
        return

    files = list(results_dir.glob("*_results.csv"))
    if not files:
        print("⚠️  No *_results.csv files found in results/.")
        return

    symbols = sorted({f.stem.rsplit("_results", 1)[0] for f in files})
    for sym in symbols:
        plot_dashboard(sym, args.min_trades)


if __name__ == "__main__":
    main()
