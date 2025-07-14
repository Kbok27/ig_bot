import MetaTrader5 as mt5
from datetime import datetime

if not mt5.initialize():
    print("[❌] MT5 initialization failed")
    mt5.shutdown()
    exit()

symbol = "EURUSD.a"  # Replace with your actual symbol if needed
timeframe = mt5.TIMEFRAME_M5
bars = 10

# Use current time
now = datetime.now()
rates = mt5.copy_rates_from(symbol, timeframe, now, bars)

mt5.shutdown()

if rates is None or len(rates) == 0:
    print(f"[❌] No data returned for {symbol}")
else:
    print(f"[✅] Retrieved {len(rates)} bars of data for {symbol}")
