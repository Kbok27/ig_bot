import MetaTrader5 as mt5

def main():
    # Initialize MT5 connection
    if not mt5.initialize():
        print("MT5 initialize() failed, error code =", mt5.last_error())
        return

    # List tradable symbols
    print("Listing tradable symbols:")
    symbols = mt5.symbols_get()
    tradable_symbols = []
    for sym in symbols:
        allowed = getattr(sym, 'trade_allowed', None)
        if allowed:
            tradable_symbols.append(sym.name)
            print(f"Symbol: {sym.name}, Trading allowed: {allowed}")

    # Use AUDUSD.a for test order
    symbol = "AUDUSD.a"
    if symbol not in tradable_symbols:
        print(f"Symbol {symbol} is not tradable or not found in symbols list.")
        mt5.shutdown()
        return

    # Select symbol explicitly
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}")
        mt5.shutdown()
        return

    # Get symbol tick info
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"Failed to get tick for symbol {symbol}")
        mt5.shutdown()
        return

    # Prepare market buy order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "deviation": 10,
        "magic": 234000,
        "comment": "Test Market Buy Order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    print(f"Placing market buy order for {symbol} at price {tick.ask}")

    # Send order
    result = mt5.order_send(request)

    # Check result
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Order placed successfully! Order ticket: {result.order}")
    else:
        print(f"Order failed, retcode={result.retcode}, result={result}")

    mt5.shutdown()

if __name__ == "__main__":
    main()
