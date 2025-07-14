# File: live_data.py

import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta


def get_live_trades(symbol: str) -> pd.DataFrame:
    """
    Fetch today's closed trades for the given symbol from MT5 and
    return a DataFrame indexed by execution time with a 'P/L' column.

    If no trades are found, returns an empty DataFrame with a 'P/L' column.
    """
    # Initialize MT5
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize() failed: {mt5.last_error()}")

    # Define the time window (from 00:00 UTC today to now)
    utc_end = datetime.utcnow()
    utc_start = utc_end.replace(hour=0, minute=0, second=0, microsecond=0)

    # Fetch closed deals for the symbol
    deals = mt5.history_deals_get(utc_start, utc_end, group=symbol)
    mt5.shutdown()

    # No deals → empty DataFrame
    if deals is None or len(deals) == 0:
        return pd.DataFrame(columns=['P/L'])

    # Convert to DataFrame
    df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)

    # Use the 'profit' field as P/L
    df['P/L'] = df['profit']

    # Keep only the P/L column
    return df[['P/L']]
