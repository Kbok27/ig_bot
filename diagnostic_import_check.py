# diagnostic_import_check.py

import strategies.strategy_sma_stoch_rr as mod
import inspect
import os

print(">>> Loaded module from:", inspect.getfile(mod))
print(">>> Exists on disk:", os.path.exists(inspect.getfile(mod)))
print(">>> Strategy contents preview:\n")

with open(inspect.getfile(mod), "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:20]):
        print(f"{i+1:02d}: {line.strip()}")
