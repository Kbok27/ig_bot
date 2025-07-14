# File: export_stats.py

import argparse
from pathlib import Path
import json
import pandas as pd
from typing import Optional


def compute_stats_for(symbol: str,
                      trades_csv: Path,
                      equity_csv: Optional[Path]) -> dict:
    """
    Load the trades CSV (and optional equity CSV) for a given symbol,
    then compute and return the stats dict.
    """
    df = pd.read_csv(trades_csv)

    # Win rate
    win_rate = float((df.get("profit", pd.Series()).gt(0).mean())) if "profit" in df else 0.0

    # Max drawdown from equity curve if provided
    max_dd = 0.0
    if equity_csv and equity_csv.exists():
        eq = pd.read_csv(equity_csv)
        cum_max = eq["equity"].cummax()
        drawdown = (cum_max - eq["equity"]) / cum_max
        max_dd = float(drawdown.max())

    # Sharpe ratio
    sharpe = 0.0
    if equity_csv and equity_csv.exists():
        daily_returns = eq["equity"].pct_change().dropna()
        if not daily_returns.empty and daily_returns.std() != 0:
            sharpe = float((daily_returns.mean() / daily_returns.std()) * (252 ** 0.5))

    # Profit factor: sum(wins)/sum(losses)
    pf = float("nan")
    if "profit" in df:
        wins   = df.loc[df.profit > 0, "profit"].sum()
        losses = -df.loc[df.profit < 0, "profit"].sum()
        pf = wins / losses if losses > 0 else float("inf")

    # Average holding time in minutes, if entry/exit columns exist
    avg_hold = None
    if {"entry_time", "exit_time"}.issubset(df.columns):
        # parse only those columns
        df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce")
        df["exit_time"]  = pd.to_datetime(df["exit_time"],  errors="coerce")
        delta = (df["exit_time"] - df["entry_time"]).dt.total_seconds().dropna() / 60.0
        if not delta.empty:
            avg_hold = float(delta.mean())

    return {
        "win_rate":        win_rate,
        "max_drawdown":    max_dd,
        "sharpe":          sharpe,
        "profit_factor":   pf,
        "avg_holding_min": avg_hold if avg_hold is not None else 0.0
    }


def main(stats_dir: str):
    stats_dir = Path(stats_dir)
    for trades_file in stats_dir.glob("*_trades.csv"):
        symbol      = trades_file.stem.replace("_trades", "")
        equity_file = stats_dir / f"{symbol}_equity.csv"
        stats       = compute_stats_for(symbol, trades_file, equity_file)

        out_json = stats_dir / f"{symbol}_stats.json"
        out_json.write_text(json.dumps(stats, indent=2))
        print(f"Wrote stats for {symbol}: {stats}")

    # Optionally, write a combined summary:
    all_stats = {
        f.stem.replace("_stats", ""): json.loads(f.read_text())
        for f in stats_dir.glob("*_stats.json")
    }
    (stats_dir / "all_stats_summary.json").write_text(
        json.dumps(all_stats, indent=2)
    )
    print("Wrote all_stats_summary.json")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Export strategy stats JSON")
    p.add_argument(
        "--stats-dir", "-d",
        default="results",
        help="Folder containing *_trades.csv and optional *_equity.csv"
    )
    args = p.parse_args()
    main(args.stats_dir)
