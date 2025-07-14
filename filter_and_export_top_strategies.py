# filter_and_export_top_strategies.py

import pandas as pd
import os
import argparse

from utils.validate_clean import validate_csv_columns
from utils.error_handling import safe_run
from utils.logger import setup_logger

def main(debug=False):
    log = setup_logger("exporter", debug=debug)
    input_csv = "optimize_results/strategy_batch_extended_results.csv"

    if not os.path.exists(input_csv):
        log.error(f"File does not exist: {input_csv}")
        log.info("Contents of optimize_results/:")
        log.info(os.listdir("optimize_results"))
        return

    df = pd.read_csv(input_csv)

    if df.empty:
        log.error("File is empty!")
        return

    try:
        validate_csv_columns(df, ["Symbol", "Params", "Trades", "WinRate", "Sharpe", "FinalEquity", "TotalPnL"], filename=input_csv)
    except Exception as e:
        log.error(f"Validation failed: {e}")
        return

    min_trades = 20
    min_win_rate = 0.4
    min_sharpe = 0.5
    top_n = 5

    filtered = df[
        (df["Trades"] >= min_trades) &
        (df["WinRate"] >= min_win_rate) &
        (df["Sharpe"] >= min_sharpe)
    ].copy()

    log.info(f"Filtered {len(filtered)} strategies with min {min_trades} trades, {min_win_rate} win rate, {min_sharpe} Sharpe")

    top = filtered.sort_values(by="FinalEquity", ascending=False).head(top_n)
    output_json = "optimize_results/top_strategies.json"

    top[["Symbol", "Params"]].to_json(output_json, orient="records", indent=2)
    log.info(f"✅ Exported top {top_n} strategies to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()

    _, err = safe_run(main, debug=args.debug)
    if err:
        print("[🚨] Export failed.")
