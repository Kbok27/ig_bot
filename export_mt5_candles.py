import MetaTrader5 as mt5
import pandas as pd

symbol = "EURUSD.a"
timeframe = mt5.TIMEFRAME_M5
bars =50000
output_file = f"{symbol}_m5.csv"

if not mt5.initialize():
    print("[❌] MT5 Initialization failed")
    quit()

rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
if rates is None:
    print(f"[❌] Failed to fetch candles for {symbol}")
    mt5.shutdown()
    quit()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df = df[['time', 'open', 'high', 'low', 'close']]
df.to_csv(output_file, index=False)

print(f"[✅] Exported {len(df)} candles to {output_file}")
mt5.shutdown()
