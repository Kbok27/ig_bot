# scripts/generate_mock_results.py

import pandas as pd
import os
import random
import argparse

from utils.error_handling import safe_run
from utils.logger import setup_logger

def generate_mock_data(n=10, output_path="optimize_results/strategy_batch_extended_results.csv", debug=False):
    log = setup_logger("mockgen", debug=debug)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = []
    for i in range(n):
        params = {
            "atr_period": random.choice([14, 21]),
            "atr_multiplier": round(random.uniform(1.2, 2.0), 2),
            "take_profit_pips": random.choice([20, 30, 40]),
        }
        data.append({
            "Symbol": "NAS100.a",
            "Params": params,
            "Trades": random.randint(10, 100),
            "WinRate": round(random.uniform(0.3, 0.7), 2),
            "Sharpe": round(random.uniform(0.2, 1.5), 2),
            "FinalEquity": round(random.uniform(950, 1200), 2),
            "TotalPnL": round(random.uniform(-100, 200), 2),
        })

    df = pd.DataFrame(data)

    df.to_csv(output_path, index=False)
    log.info(f"✅ Mock result CSV written: {output_path}")

    json_path = output_path.replace(".csv", ".json")
    df[["Symbol", "Params"]].to_json(json_path, orient="records", indent=2)
    log.info(f"✅ Mock JSON config written: {json_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--rows", type=int, default=10, help="Number of mock strategies to generate")
    args = parser.parse_args()

    _, err = safe_run(generate_mock_data, n=args.rows, debug=args.debug)
    if err:
        print("[🚨] Mock data generation failed.")

if __name__ == "__main__":
    main()
