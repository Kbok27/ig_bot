# File: export_top_configs.py
import argparse
import json
from pathlib import Path
import pandas as pd

def export_top_configs(summary_csv: Path, output_json: Path, metric: str, top_n: int,
                       symbol: str, timeframe: int, bars: int):
    """
    Read a threshold sweep summary CSV and export the top-N configs to a JSON job list.
    """
    # Load the sweep results
    df = pd.read_csv(summary_csv)

    # Sort by the chosen metric and take top N
    df_top = df.sort_values(metric, ascending=False).head(top_n)

    # Build the list of job dicts
    configs = []
    for _, row in df_top.iterrows():
        cfg = {
            "symbol": symbol,
            "timeframe": timeframe,
            "bars": bars,
            "strategy_kwargs": {
                "stoch_oversold_threshold": float(row["threshold"])
            }
        }
        configs.append(cfg)

    # Write out to JSON
    output_json.write_text(json.dumps(configs, indent=2))
    print(f"✅ Exported top {top_n} configs by '{metric}' to {output_json}")


def main():
    parser = argparse.ArgumentParser(
        description="Export the top-N threshold sweep configs to JSON job list"
    )
    parser.add_argument(
        "--summary-csv", type=Path,
        default=Path("parameter_sweep_results.csv"),
        help="Path to the threshold sweep summary CSV"
    )
    parser.add_argument(
        "--output-json", type=Path,
        default=Path("top_configs.json"),
        help="Output JSON file for top configs"
    )
    parser.add_argument(
        "--metric", type=str,
        default="profit_factor",
        help="Metric to sort by (e.g. 'profit_factor')"
    )
    parser.add_argument(
        "--top-n", type=int,
        default=5,
        help="Number of top configs to export"
    )
    parser.add_argument(
        "--symbol", type=str,
        required=True,
        help="Symbol to assign to all exported configs"
    )
    parser.add_argument(
        "--timeframe", type=int,
        default=5,
        help="Timeframe (in minutes) for the configs"
    )
    parser.add_argument(
        "--bars", type=int,
        default=2000,
        help="Number of bars for each backtest"
    )
    args = parser.parse_args()

    export_top_configs(
        summary_csv=args.summary_csv,
        output_json=args.output_json,
        metric=args.metric,
        top_n=args.top_n,
        symbol=args.symbol,
        timeframe=args.timeframe,
        bars=args.bars
    )

if __name__ == "__main__":
    main()
