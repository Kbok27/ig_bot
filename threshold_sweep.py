# File: threshold_sweep.py

import pandas as pd
from pathlib import Path
from utils.data_utils import get_data
from strategies.strategy_sma_stoch_rr_v2 import run_strategy

def main():
    SYMBOL     = "BTCUSD.a"             # live symbol
    TIMEFRAME  = 5                      # 5-minute bars
    BARS       = 2000
    THRESHOLDS = [100, 80, 60, 40, 20]

    # 1) Load data
    print(f"🔎 Loading {BARS} bars for {SYMBOL} @ {TIMEFRAME}m…")
    df = get_data(SYMBOL, TIMEFRAME, BARS)
    print(f"✔️  Loaded {len(df)} rows.\n")

    # 2) Sweep thresholds
    results = []
    for t in THRESHOLDS:
        # run_strategy now returns a single float (e.g. your PF or net P/L)
        pf = run_strategy(df, t)
        results.append({
            "threshold":      t,
            "profit_factor":  pf
        })
        print(f" • Threshold {t}: PF = {pf:.4f}")

    # 3) Save sweep results
    sweep_df = pd.DataFrame(results)
    out_csv = Path(__file__).parent / "parameter_sweep_results.csv"
    sweep_df.to_csv(out_csv, index=False)
    print(f"\n✅ Saved sweep results to {out_csv}")

if __name__ == "__main__":
    main()
