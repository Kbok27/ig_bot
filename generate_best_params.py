import json
import os
import pandas as pd

# Path to TP/ATR sweep results
SUMMARY_CSV = os.path.join('optimize_results', 'trade_logs', 'tp_atr_sweep_summary.csv')
# Output JSON for best params
OUTPUT_JSON = 'best_params.json'

# Load sweep summary
df = pd.read_csv(SUMMARY_CSV)
# Identify best row by highest expectancy
best = df.loc[df['expectancy'].idxmax()].to_dict()

# Compose best-params dict
best_params = {
    'symbol':            best['symbol'],
    'take_profit_pips':  int(best['tp']),
    'atr_stop_multiplier': float(best['atr_stop_mult']),
    # Use pip_factors from a static mapping or infer from sweep
    'pip_factors':       {best['symbol']: 0.1},
    'bars':               10000,
    'atr_period':         10,
    'atr_multiplier':     1.0,
    'sma50_distance_pips': 30,
    'min_candle_size_pips': 0.5,
    'min_leg_move':       0.3,
    'max_leg_gap':        10,
    'initial_equity':     1000.0
}

# Write to JSON
with open(OUTPUT_JSON, 'w') as f:
    json.dump(best_params, f, indent=4)

print(f"✅ Best parameters saved to {OUTPUT_JSON}:\n{json.dumps(best_params, indent=4)}")
