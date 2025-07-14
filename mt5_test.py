import MetaTrader5 as mt5

print("[🔍] Initializing MetaTrader 5...")
if not mt5.initialize():
    print(f"[❌] Initialization failed: {mt5.last_error()}")
    exit()

symbol = "NAS100.a"
info = mt5.symbol_info(symbol)
if info is None:
    print(f"[⚠️] Symbol {symbol} not found. Check if it's visible in MT5 Market Watch.")
else:
    print(f"[✅] Symbol found: {info.name}, Bid: {mt5.symbol_info_tick(symbol).bid}")

mt5.shutdown()
