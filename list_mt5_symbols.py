# list_mt5_symbols.py

import MetaTrader5 as mt5

def list_symbols():
    # Initialize connection to MT5 terminal
    if not mt5.initialize():
        print("MT5 initialize() failed, error code =", mt5.last_error())
        return

    # Get all available symbols
    symbols = mt5.symbols_get()
    if symbols is None:
        print("No symbols found")
    else:
        print(f"Found {len(symbols)} symbols:")
        for symbol in symbols:
            print(symbol.name)

    # Shutdown MT5 connection
    mt5.shutdown()

if __name__ == "__main__":
    list_symbols()
